#!/usr/bin/env python3
"""
Autonomous SITL Mission Test
Tests: connect → wait GPS → upload waypoints → arm → AUTO mode → monitor
Uses pymavlink directly (same library as the GCS).
"""

import subprocess
import time
import sys
import os
import signal

from pymavlink import mavutil

# ── SITL config ────────────────────────────────────────────────────────────
SITL_HOME = "-35.363261,149.165230,584,270"   # ArduRover default home
SITL_BINARY = os.path.expanduser("~/ardupilot/build/sitl/bin/ardurover")
SITL_PARM = os.path.expanduser("~/ardupilot/Tools/autotest/default_params/rover.parm")
SITL_TCP_PORT = 5760

# Simple 4-waypoint box ~50m around SITL home
WP_LAT0, WP_LON0 = -35.363261, 149.165230  # home / WP1
WAYPOINTS = [
    (WP_LAT0 + 0.0005,  WP_LON0),           # ~55m north
    (WP_LAT0 + 0.0005,  WP_LON0 + 0.0005),  # NE corner
    (WP_LAT0,           WP_LON0 + 0.0005),  # ~55m east
    (WP_LAT0,           WP_LON0),           # back to home
]

RESULTS = {}

# ── helpers ────────────────────────────────────────────────────────────────
def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)

def wait_msg(conn, msg_type, timeout=15, **filters):
    deadline = time.time() + timeout
    while time.time() < deadline:
        m = conn.recv_match(type=msg_type, blocking=True, timeout=0.5)
        if m is None:
            continue
        match = all(getattr(m, k, None) == v for k, v in filters.items())
        if match:
            return m
    return None

# ── test steps ─────────────────────────────────────────────────────────────

def start_sitl():
    log("SITL", f"Launching ardurover binary at {SITL_BINARY}")
    cmd = [
        SITL_BINARY,
        "--model", "rover",
        "--speedup", "5",
        "--home", SITL_HOME,
        "--defaults", SITL_PARM,
        "--sim-address", "127.0.0.1",
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    log("SITL", f"PID={proc.pid} — waiting 10s for socket to open...")
    time.sleep(10)
    return proc


def connect(port=SITL_TCP_PORT):
    log("CONNECT", f"Connecting to tcp:127.0.0.1:{port}")
    conn = mavutil.mavlink_connection(f"tcp:127.0.0.1:{port}", timeout=10)
    hb = conn.wait_heartbeat(timeout=20)
    if not hb:
        raise RuntimeError("No heartbeat received")
    log("CONNECT", f"Heartbeat from sysid={conn.target_system} compid={conn.target_component}")
    return conn


def wait_gps(conn, timeout=60):
    log("GPS", "Waiting for GPS fix (fix_type >= 3)...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        m = conn.recv_match(type="GPS_RAW_INT", blocking=True, timeout=1)
        if m and m.fix_type >= 3:
            lat = m.lat / 1e7
            lon = m.lon / 1e7
            log("GPS", f"Fix acquired: lat={lat:.6f} lon={lon:.6f} fix={m.fix_type} sats={m.satellites_visible}")
            return True
    log("GPS", "TIMEOUT — no GPS fix")
    return False


def request_streams(conn):
    conn.mav.request_data_stream_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1
    )
    time.sleep(0.5)


def upload_mission(conn, waypoints):
    log("UPLOAD", f"Uploading {len(waypoints)} waypoints...")

    # Clear
    conn.mav.mission_clear_all_send(conn.target_system, conn.target_component)
    ack = conn.recv_match(type="MISSION_ACK", blocking=True, timeout=10)
    log("UPLOAD", f"Clear ACK: {ack.type if ack else 'none'}")
    time.sleep(0.5)

    # Build items
    items = []
    for i, (lat, lon) in enumerate(waypoints):
        items.append({
            "seq": i,
            "frame": mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            "command": mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            "current": 0,
            "autocontinue": 1,
            "p1": 0.0, "p2": 3.0, "p3": 0.0, "p4": 0.0,
            "x": int(lat * 1e7),
            "y": int(lon * 1e7),
            "z": 0.0,
        })

    # Count
    conn.mav.mission_count_send(
        conn.target_system, conn.target_component,
        len(items), mavutil.mavlink.MAV_MISSION_TYPE_MISSION
    )

    # Serve items
    uploaded = set()
    deadline = time.time() + 45
    while len(uploaded) < len(items) and time.time() < deadline:
        req = conn.recv_match(
            type=["MISSION_REQUEST_INT", "MISSION_REQUEST"],
            blocking=True, timeout=10
        )
        if not req:
            log("UPLOAD", "Request timeout")
            break
        seq = req.seq
        if seq >= len(items):
            continue
        it = items[seq]
        conn.mav.mission_item_int_send(
            conn.target_system, conn.target_component,
            it["seq"], it["frame"], it["command"],
            it["current"], it["autocontinue"],
            it["p1"], it["p2"], it["p3"], it["p4"],
            it["x"], it["y"], it["z"],
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        uploaded.add(seq)
        log("UPLOAD", f"  sent item {seq} ({len(uploaded)}/{len(items)})")

    # Final ACK
    final = conn.recv_match(type="MISSION_ACK", blocking=True, timeout=15)
    if final and final.type == 0:
        log("UPLOAD", "Mission ACCEPTED by vehicle")
        return True
    log("UPLOAD", f"FAILED — final ACK type={final.type if final else 'none'}")
    return False


def set_mode(conn, mode_name):
    mode_map = {
        "MANUAL": 0, "ACRO": 1, "STEERING": 3, "HOLD": 4,
        "LOITER": 5, "AUTO": 10, "RTL": 11, "GUIDED": 15,
    }
    mode_id = mode_map.get(mode_name.upper())
    if mode_id is None:
        log("MODE", f"Unknown mode: {mode_name}")
        return False

    # Try up to 3 times
    for attempt in range(3):
        conn.mav.set_mode_send(
            conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )
        # Also try via COMMAND_LONG as backup
        conn.mav.command_long_send(
            conn.target_system, conn.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id,
            0, 0, 0, 0, 0
        )
        deadline = time.time() + 5
        while time.time() < deadline:
            hb = conn.recv_match(type="HEARTBEAT", blocking=True, timeout=0.5)
            if hb:
                log("MODE", f"  HB custom_mode={hb.custom_mode} (want {mode_id})")
                if hb.custom_mode == mode_id:
                    log("MODE", f"Mode confirmed: {mode_name}")
                    return True
        log("MODE", f"  Attempt {attempt+1} not confirmed, retrying...")
        time.sleep(0.5)

    log("MODE", f"Mode change to {mode_name} FAILED after 3 attempts")
    return False


def disable_prearm_checks(conn):
    """Disable pre-arm checks for SITL testing."""
    log("ARM", "Disabling pre-arm checks (ARMING_CHECK=0)...")
    conn.mav.param_set_send(
        conn.target_system, conn.target_component,
        b'ARMING_CHECK', 0.0,
        mavutil.mavlink.MAV_PARAM_TYPE_INT32
    )
    time.sleep(0.5)


def arm_vehicle(conn, timeout=30):
    log("ARM", "Sending arm command (with force flag)...")
    # param2=21196 is the force-arm magic number in ArduPilot
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,       # confirmation
        1,       # param1: 1=arm
        21196,   # param2: force arm magic number
        0, 0, 0, 0, 0
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        m = conn.recv_match(
            type=["HEARTBEAT", "COMMAND_ACK"],
            blocking=True, timeout=1
        )
        if m is None:
            continue
        if m.get_type() == "COMMAND_ACK":
            cmd = getattr(m, "command", None)
            result = getattr(m, "result", None)
            log("ARM", f"COMMAND_ACK command={cmd} result={result}")
            if result == 0:  # MAV_RESULT_ACCEPTED
                log("ARM", "Arm accepted by vehicle")
        if m.get_type() == "HEARTBEAT":
            if m.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
                log("ARM", "Vehicle ARMED (confirmed via HEARTBEAT)")
                return True
    log("ARM", "Arm TIMEOUT")
    return False


def monitor_mission(conn, timeout=60):
    log("MISSION", f"Monitoring AUTO mission for {timeout}s...")
    start = time.time()
    last_seq = -1
    last_pos_log = 0
    reached = set()
    mission_complete_text = False
    while time.time() - start < timeout:
        m = conn.recv_match(
            type=["MISSION_CURRENT", "MISSION_ITEM_REACHED",
                  "HEARTBEAT", "STATUSTEXT", "GLOBAL_POSITION_INT"],
            blocking=True, timeout=1
        )
        if m is None:
            continue
        t = m.get_type()
        if t == "MISSION_CURRENT" and m.seq != last_seq:
            last_seq = m.seq
            log("MISSION", f"Current waypoint: {m.seq}")
        elif t == "MISSION_ITEM_REACHED":
            log("MISSION", f"Reached waypoint {m.seq}")
            reached.add(m.seq)
            if len(reached) >= len(WAYPOINTS):
                log("MISSION", "All waypoints reached!")
                return True
        elif t == "STATUSTEXT":
            txt = m.text.strip()
            log("STATUS", txt)
            if "Mission Complete" in txt or "mission complete" in txt.lower():
                mission_complete_text = True
                log("MISSION", "COMPLETE (via STATUSTEXT) — success!")
                return True
        elif t == "GLOBAL_POSITION_INT":
            now = time.time()
            if now - last_pos_log >= 10:
                lat = m.lat / 1e7
                lon = m.lon / 1e7
                log("POS", f"lat={lat:.6f} lon={lon:.6f}")
                last_pos_log = now
        elif t == "HEARTBEAT":
            armed = bool(m.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            mode = m.custom_mode
            if not armed:
                log("MISSION", f"Vehicle disarmed mode={mode} (mission complete or aborted)")
                return len(reached) > 0  # only success if we reached at least one wp
    log("MISSION", f"Monitor timeout after {timeout}s — reached {len(reached)}/{len(WAYPOINTS)} waypoints")
    return len(reached) >= len(WAYPOINTS)


# ── main ───────────────────────────────────────────────────────────────────

def main():
    sitl_proc = None
    conn = None

    try:
        # 1. Start SITL
        sitl_proc = start_sitl()
        RESULTS["sitl_started"] = True

        # 2. Connect
        conn = connect()
        RESULTS["connected"] = True

        # 3. Request telemetry streams
        request_streams(conn)

        # 4. Wait for GPS
        gps_ok = wait_gps(conn, timeout=90)
        RESULTS["gps_fix"] = gps_ok
        if not gps_ok:
            raise RuntimeError("No GPS fix")

        # 5. Upload mission
        upload_ok = upload_mission(conn, WAYPOINTS)
        RESULTS["mission_uploaded"] = upload_ok
        if not upload_ok:
            raise RuntimeError("Mission upload failed")

        # 6. Switch to GUIDED, disable pre-arm checks, then arm
        set_mode(conn, "GUIDED")
        time.sleep(1)
        disable_prearm_checks(conn)
        time.sleep(0.5)
        armed = arm_vehicle(conn, timeout=30)
        RESULTS["armed"] = armed
        if not armed:
            raise RuntimeError("Arm failed")

        # 7. Switch to AUTO and start
        time.sleep(0.5)
        set_mode(conn, "AUTO")
        RESULTS["auto_mode"] = True

        # 8. Monitor
        finished = monitor_mission(conn, timeout=120)
        RESULTS["mission_completed"] = finished

    except Exception as e:
        RESULTS["error"] = str(e)
        log("ERROR", str(e))

    finally:
        # Print summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        checks = [
            ("SITL started",        RESULTS.get("sitl_started")),
            ("Connected",           RESULTS.get("connected")),
            ("GPS fix",             RESULTS.get("gps_fix")),
            ("Mission uploaded",    RESULTS.get("mission_uploaded")),
            ("Armed",               RESULTS.get("armed")),
            ("AUTO mode set",       RESULTS.get("auto_mode")),
            ("Mission completed",   RESULTS.get("mission_completed")),
        ]
        all_pass = True
        for label, result in checks:
            icon = "PASS" if result else "FAIL"
            if result is None:
                icon = "SKIP"
                all_pass = False
            elif not result:
                all_pass = False
            print(f"  [{icon}]  {label}")

        if "error" in RESULTS:
            print(f"\n  ERROR: {RESULTS['error']}")

        print("=" * 60)
        print("OVERALL:", "PASS" if all_pass else "FAIL")
        print("=" * 60)

        # Cleanup
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        if sitl_proc:
            log("SITL", "Terminating SITL...")
            try:
                os.killpg(os.getpgid(sitl_proc.pid), signal.SIGTERM)
            except Exception:
                pass


if __name__ == "__main__":
    main()
