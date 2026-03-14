#!/bin/bash
# Launch VRX Gazebo + ArduPilot SITL for WAM-V USV simulation
#
# Architecture:
#   1. Gazebo Harmonic with VRX WAM-V (buoyancy + wave physics)
#   2. ArduPilot Rover SITL (communicates with Gazebo via JSON/UDP port 9002)
#   3. MAVProxy bridges SITL to GCS on UDP 14550
#
# Requirements:
#   - VRX built:         ~/vrx_ws
#   - ardupilot_gazebo:  ~/ardupilot_gazebo/build
#   - ArduPilot SITL:    ~/ardupilot
#   - venv-ardupilot:    ~/venv-ardupilot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GCS_DIR="$(dirname "$SCRIPT_DIR")"

# ============================================================
# Configuration
# ============================================================
ARDUPILOT_DIR=~/ardupilot
VENV=~/venv-ardupilot
VRX_WS=~/vrx_ws
ARDUPILOT_GZ_DIR=~/ardupilot_gazebo
PARAM_FILE="$SCRIPT_DIR/params/wamv_sitl.parm"

# GCS MAVLink port (matches SITL default output)
GCS_UDP_PORT=14550

# MAVProxy auto-restart: how many times to retry if it fails to get heartbeat
MAVPROXY_MAX_RETRIES=5

# ============================================================
# Cleanup on exit
# ============================================================
cleanup() {
    echo ""
    echo "[LAUNCH] Stopping all processes..."
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    echo "[LAUNCH] Done."
}
trap cleanup EXIT INT TERM

# ============================================================
# Check dependencies
# ============================================================
echo "[LAUNCH] Checking dependencies..."

if [ ! -d "$VRX_WS/install" ]; then
    echo "[ERROR] VRX not found at $VRX_WS. Build it first:"
    echo "        cd ~/vrx_ws && colcon build"
    exit 1
fi

if [ ! -f "$ARDUPILOT_GZ_DIR/build/libArduPilotPlugin.so" ]; then
    echo "[ERROR] ardupilot_gazebo plugin not found. Build it first:"
    echo "        cd ~/ardupilot_gazebo && cmake -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo && cmake --build build -j4"
    exit 1
fi

if [ ! -f "$ARDUPILOT_DIR/build/sitl/bin/ardurover" ]; then
    echo "[ERROR] ArduPilot SITL not found. Build it first:"
    echo "        cd ~/ardupilot && ./waf configure --board sitl && ./waf rover"
    exit 1
fi

echo "[LAUNCH] All dependencies found."

# ============================================================
# Set Gazebo plugin paths
# ============================================================

# Source VRX workspace FIRST so ament env hooks populate GZ_SIM_RESOURCE_PATH
source $VRX_WS/install/setup.bash 2>/dev/null || true

# Plugin paths: prepend ArduPilot plugin (VRX plugins already added by setup.bash)
export GZ_SIM_SYSTEM_PLUGIN_PATH=$ARDUPILOT_GZ_DIR/build:$GZ_SIM_SYSTEM_PLUGIN_PATH

# Model/world resource paths:
#   1. ArduPilot models (our custom wamv_ardupilot model)
#   2. wamv_description/share parent — needed so model://wamv_description/models/... URIs resolve
#   3. wamv_gazebo/share parent     — needed so model://wamv_gazebo/models/gps/... resolves
#   4. VRX paths already set by setup.bash
export GZ_SIM_RESOURCE_PATH=$ARDUPILOT_GZ_DIR/models:$ARDUPILOT_GZ_DIR/worlds:$VRX_WS/install/wamv_description/share:$VRX_WS/install/wamv_gazebo/share:$GZ_SIM_RESOURCE_PATH

# SDF_PATH mirrors resource path for gz sdf URI resolution
export SDF_PATH=$GZ_SIM_RESOURCE_PATH

echo "[LAUNCH] GZ_SIM_SYSTEM_PLUGIN_PATH=$GZ_SIM_SYSTEM_PLUGIN_PATH"
echo "[LAUNCH] Starting Gazebo with WAM-V world..."

# ============================================================
# Step 1: Launch Gazebo
# ============================================================
gz sim -r "$ARDUPILOT_GZ_DIR/worlds/wamv_ardupilot.sdf" &
GZ_PID=$!
echo "[LAUNCH] Gazebo PID: $GZ_PID"

# Wait for Gazebo to fully load world + plugins
echo "[LAUNCH] Waiting for Gazebo to start (10 seconds)..."
sleep 10

# ============================================================
# Step 2: Launch ardurover directly (no sim_vehicle.py wrapper)
#
# Why not sim_vehicle.py?
#   --delay-start applies TWICE (before ardurover AND before MAVProxy),
#   making it impossible to control timing independently.
#
# ardurover startup sequence:
#   1. Opens TCP 5760 for MAVLink
#   2. Connects to Gazebo plugin via JSON/UDP on port 9002
#   3. Receives initial sensor data, loads params → triggers internal reboot
#   4. After reboot: reconnects to Gazebo, EKF initialises, heartbeats start
#   Total time to stable heartbeats: ~20-35 seconds
# ============================================================
echo "[LAUNCH] Starting ardurover SITL..."

source $VENV/bin/activate 2>/dev/null || true

ARDUROVER_DEFAULTS="$ARDUPILOT_DIR/Tools/autotest/default_params/rover.parm"
ARDUROVER_DEFAULTS="$ARDUROVER_DEFAULTS,$ARDUPILOT_DIR/Tools/autotest/default_params/rover-skid.parm"
ARDUROVER_DEFAULTS="$ARDUROVER_DEFAULTS,$PARAM_FILE"

cd $ARDUPILOT_DIR

$ARDUPILOT_DIR/build/sitl/bin/ardurover \
    --model JSON \
    --speedup 1 \
    --defaults "$ARDUROVER_DEFAULTS" \
    --sim-address=127.0.0.1 \
    -I0 \
    > /tmp/ardurover_sitl.log 2>&1 &

ARDUROVER_PID=$!
echo "[LAUNCH] ardurover PID: $ARDUROVER_PID (log: /tmp/ardurover_sitl.log)"

# ============================================================
# Step 3: Wait for ardurover TCP port 5760 to open,
#         then wait for the internal reboot + EKF to settle.
#
# ardurover does an internal reboot ~5-10s after startup when
# FRAME_CLASS/EKF params load. The reboot resets the Gazebo
# JSON frame counter. We must wait for re-sync + EKF init
# before MAVProxy tries to receive a heartbeat.
# ============================================================
echo "[LAUNCH] Waiting for ardurover TCP port 5760..."
TCP_WAIT=0
TCP_MAX=60
while ! nc -z 127.0.0.1 5760 2>/dev/null; do
    sleep 1
    TCP_WAIT=$((TCP_WAIT + 1))
    if [ $TCP_WAIT -ge $TCP_MAX ]; then
        echo "[ERROR] ardurover TCP port 5760 did not open after ${TCP_MAX}s"
        echo "[ERROR] Last 20 lines of ardurover log:"
        tail -20 /tmp/ardurover_sitl.log
        exit 1
    fi
done
echo "[LAUNCH] ardurover TCP port open after ${TCP_WAIT}s"

# Additional wait for internal reboot + EKF initialisation
# (the TCP port opens ~2s after startup, but reboot happens 5-10s later
# and EKF needs another 10-15s to converge)
echo "[LAUNCH] Waiting 30 more seconds for ardurover reboot + EKF init..."
sleep 30

# ============================================================
# Step 4: Launch MAVProxy with auto-restart
#
# MAVProxy may fail to receive the first heartbeat if ardurover
# is still mid-reboot. Auto-restart guarantees a successful
# connection once ardurover is fully ready.
# ============================================================
echo ""
echo "========================================================"
echo " VRX Gazebo + ArduPilot SITL running"
echo "========================================================"
echo " Gazebo:      PID $GZ_PID"
echo " ardurover:   PID $ARDUROVER_PID"
echo ""
echo " Connect your GCS to: udp:127.0.0.1:$GCS_UDP_PORT"
echo " In the GCS app, select: UDP and port $GCS_UDP_PORT"
echo ""
echo " ardurover log: /tmp/ardurover_sitl.log"
echo " Press Ctrl+C to stop all processes."
echo "========================================================"
echo ""

for attempt in $(seq 1 $MAVPROXY_MAX_RETRIES); do
    # Bail out if core processes died
    if ! kill -0 $GZ_PID 2>/dev/null; then
        echo "[LAUNCH] Gazebo (PID $GZ_PID) has exited. Stopping."
        exit 1
    fi
    if ! kill -0 $ARDUROVER_PID 2>/dev/null; then
        echo "[LAUNCH] ardurover (PID $ARDUROVER_PID) has exited. Check /tmp/ardurover_sitl.log"
        exit 1
    fi

    echo "[LAUNCH] Starting MAVProxy (attempt $attempt/$MAVPROXY_MAX_RETRIES)..."

    # Run MAVProxy in the foreground so we can detect exit and restart
    mavproxy.py \
        --master tcp:127.0.0.1:5760 \
        --sitl 127.0.0.1:5501 \
        --out udp:127.0.0.1:$GCS_UDP_PORT \
        --retries 60 \
        --map \
        --console
    MAVPROXY_EXIT=$?

    # Exit code 0 = user closed MAVProxy intentionally
    if [ $MAVPROXY_EXIT -eq 0 ]; then
        echo "[LAUNCH] MAVProxy exited cleanly."
        exit 0
    fi

    echo "[LAUNCH] MAVProxy exited with code $MAVPROXY_EXIT (heartbeat timeout or connection error)"

    if [ $attempt -lt $MAVPROXY_MAX_RETRIES ]; then
        echo "[LAUNCH] Retrying in 5 seconds..."
        sleep 5
    fi
done

echo "[LAUNCH] MAVProxy failed after $MAVPROXY_MAX_RETRIES attempts."
echo "[LAUNCH] ardurover log tail:"
tail -30 /tmp/ardurover_sitl.log
exit 1
