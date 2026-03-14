# Gazebo VRX + ArduPilot SITL Integration

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Your Machine                        │
│                                                       │
│  ┌──────────────┐  UDP:9002  ┌──────────────────┐   │
│  │  Gazebo Sim   │◄──────────►│  ArduPilot SITL  │   │
│  │  (VRX WAM-V)  │  JSON FDM  │  (Rover/Boat)    │   │
│  └──────────────┘            └────────┬─────────┘   │
│       │ Physics:                      │ MAVLink      │
│       │ - Buoyancy                    │ UDP:14550    │
│       │ - Waves                       ▼             │
│       │ - Hydrodynamics       ┌──────────────────┐  │
│       └──────────────────────►│   GCS App (USV)  │  │
│                                └──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Data Flow

1. **Gazebo → ArduPilot SITL** (via ArduPilotPlugin, UDP port 9002):
   - IMU data (angular velocity, linear acceleration)
   - GPS position (NavSat sensor)
   - Simulation time

2. **ArduPilot SITL → Gazebo** (servo PWM outputs, UDP port 9002):
   - SERVO1 (channel 0) → left thruster angular velocity (rad/s)
   - SERVO3 (channel 2) → right thruster angular velocity (rad/s)
   - Published to `/wamv/thrusters/left/thrust` and `/wamv/thrusters/right/thrust`

3. **ArduPilot SITL → GCS** (MAVLink, UDP port 14550):
   - Standard MAVLink telemetry (position, attitude, battery, etc.)
   - Mission commands and acknowledgements

## Prerequisites

All of these should already be installed/built:
- **Gazebo Harmonic (gz-harmonic)**: `gz sim --version`
- **VRX**: `~/vrx_ws/install/vrx_gz/lib/libSurface.so`
- **ardupilot_gazebo**: `~/ardupilot_gazebo/build/libArduPilotPlugin.so`
- **ArduPilot SITL**: `~/ardupilot/build/sitl/bin/ardurover`

## Launch Instructions

### Method 1: Full stack (recommended)

```bash
cd ~/projecto/GCS_USV
./gazebo/launch_vrx.sh
```

Then connect the GCS app:
- Open the GCS application
- Connection type: **UDP**
- Port: **14550**
- Click Connect

### Method 2: Manual (for debugging)

**Terminal 1 — Gazebo:**
```bash
source ~/vrx_ws/install/setup.bash
export GZ_SIM_SYSTEM_PLUGIN_PATH=~/ardupilot_gazebo/build:~/vrx_ws/install/vrx_gz/lib:$GZ_SIM_SYSTEM_PLUGIN_PATH
export GZ_SIM_RESOURCE_PATH=~/ardupilot_gazebo/models:~/ardupilot_gazebo/worlds:$GZ_SIM_RESOURCE_PATH
export SDF_PATH=$GZ_SIM_RESOURCE_PATH
gz sim -r ~/ardupilot_gazebo/worlds/wamv_ardupilot.sdf
```

**Terminal 2 — ArduPilot SITL:**
```bash
source ~/venv-ardupilot/bin/activate
cd ~/ardupilot
sim_vehicle.py \
  -v Rover \
  -f gazebo-rover \
  --add-param-file=~/projecto/GCS_USV/gazebo/params/wamv_sitl.parm \
  --no-rebuild \
  --out=udp:127.0.0.1:14550 \
  --console
```

**Terminal 3 — GCS:**
```bash
cd ~/projecto/GCS_USV
source ~/venv-ardupilot/bin/activate
python3 main.py
```
Then connect to UDP port 14550.

## Files

| File | Purpose |
|------|---------|
| `launch_vrx.sh` | Launch Gazebo + SITL in one command |
| `params/wamv_sitl.parm` | ArduPilot params for WAM-V boat |
| `~/ardupilot_gazebo/worlds/wamv_ardupilot.sdf` | Gazebo world |
| `~/ardupilot_gazebo/models/wamv_ardupilot/model.sdf` | WAM-V + ArduPilot plugin |

## Troubleshooting

### Gazebo opens but boat doesn't move
- Verify ArduPilot SITL connected: look for "SIM: Gazebo" in SITL console
- Check Gazebo console for "ArduPilotPlugin: connected" message
- Ensure the GCS has armed the vehicle before sending missions

### SITL says "waiting for Gazebo"
- ArduPilot is listening on UDP 9002 for Gazebo's JSON state
- Gazebo must launch FIRST, then SITL
- Wait ~8 seconds after Gazebo starts before launching SITL

### Boat spawns but sinks
- VRX buoyancy plugins need `coast_waves` model to be loaded
- Verify `libSurface.so` is in `GZ_SIM_SYSTEM_PLUGIN_PATH`

### GCS map not showing boat movement
- Connect to UDP 14550 (standard MAVLink output from SITL)
- GPS fix_type must be ≥ 3 (SITL starts with GPS lock by default)
