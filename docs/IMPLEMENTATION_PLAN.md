# Implementation Plan — Competition Ready

**Project**: GCS_USV — TEKNOFEST 2026 Insansiz Deniz Araci
**Date**: 2026-03-21
**Critical Deadline**: Autonomy Demo Video due 2026-07-21
**Competition**: Aug-Sep 2026

---

## Architecture Overview

### Current State (Single Connection)
```
              ┌─────────────┐
              │   GCS (PC)  │
              │  PySide6 UI │
              │             │
              │ ┌─────────┐ │
              │ │ Serial  │ │
              │ │  Port   │ │
              │ └────┬────┘ │
              └──────┼──────┘
                     │ MAVLink (1 connection)
              ┌──────┴──────┐
              │    USV      │
              └─────────────┘
```

### Target State (Dual Connection)
```
              ┌──────────────────────────────┐
              │          GCS (PC)            │
              │         PySide6 UI           │
              │                              │
              │  ┌───────────────────────┐   │
              │  │  ConnectionManager    │   │
              │  │                       │   │
              │  │ ┌─────────┐ ┌──────┐  │   │
              │  │ │USV Conn │ │Drone │  │   │
              │  │ │ Thread  │ │Conn  │  │   │
              │  │ │(RFD900x)│ │Thread│  │   │
              │  │ │Serial 1 │ │(SiK) │  │   │
              │  │ │         │ │Ser.2 │  │   │
              │  │ └────┬────┘ └──┬───┘  │   │
              │  └──────┼────────┼──────┘   │
              │         │        │           │
              │  ┌──────┴────────┴────────┐  │
              │  │    Telemetry Logger     │  │
              │  │  (CSV + sensor data)   │  │
              │  └────────────────────────┘  │
              │                              │
              │  ┌─────────────────────────┐  │
              │  │   Parkour State Machine │  │
              │  │ P1→P2→P3 auto-transition│  │
              │  └─────────────────────────┘  │
              └──────────┬────────┬──────────┘
                         │        │
                  MAVLink│        │MAVLink
                  (USV)  │        │(Drone)
                         │        │
              ┌──────────┴──┐ ┌───┴──────────┐
              │     USV     │ │    Drone      │
              │  ArduPilot  │ │  ArduPilot    │
              │  Rover/Boat │ │  Copter       │
              │  Orin Nano  │ │  Jetson Nano  │
              │  + LIDAR    │ │  + Camera     │
              └─────────────┘ └──────────────┘
```

### Data Flow

```
[Drone Camera] → Jetson Nano (detection) → MAVLink custom msg → SiK Radio
                                                                    │
                                                              ┌─────┴─────┐
                                                              │    GCS    │
                                                              │           │
                                                              │ Display   │
                                                              │ target    │
                                                              │ color +   │
                                                              │ position  │
                                                              │           │
                                                              │ Relay to  │
                                                              │ USV via   │
                                                              │ RFD900x   │
                                                              └─────┬─────┘
                                                                    │
[USV Autopilot] ← mission + target data ← RFD900x ← ─────────────┘
```

---

## Priority 1 — Dual Connection System

### 1.1 Connection Manager (NEW)

**What**: A manager class that handles multiple simultaneous MAVLink connections, each in its own QThread.

**Why**: Competition requires GCS↔USV and GCS↔Drone simultaneously. Current codebase only supports one.

**Files to create**:
- `ConnectionManager.py` — orchestrates multiple connections
- `DroneConnection.py` — drone-specific MAVLink thread (lighter than ArdupilotConnection)

**Files to modify**:
- `Vehicle/ArdupilotConnection.py` — refactor to be USV-specific, clean up dual telemetry paths
- `MainWindow.py` — use ConnectionManager instead of direct ArdupilotConnectionThread
- `TargetsPage.py` — route mission commands through ConnectionManager

**Implementation Steps**:
1. Create `ConnectionManager` class with:
   - `usv_connection: ArdupilotConnectionThread` (existing, refactored)
   - `drone_connection: DroneConnectionThread` (new)
   - `connect_usv(port, baudrate)` / `disconnect_usv()`
   - `connect_drone(port, baudrate)` / `disconnect_drone()`
   - Signals: `usv_telemetry_updated`, `drone_telemetry_updated`, `usv_connected`, `drone_connected`
   - `relay_target_to_usv(color, lat, lon)` — forwards drone detection to USV
2. Create `DroneConnectionThread(QThread)`:
   - Connects via MAVLink to drone autopilot
   - Processes: HEARTBEAT, GLOBAL_POSITION_INT, GPS_RAW_INT, SYS_STATUS, BATTERY_STATUS
   - Receives custom MAVLink messages or STATUSTEXT with detection data
   - Signals: `position_updated(lat, lon, alt)`, `battery_updated(voltage, pct)`, `target_detected(color, lat, lon)`
3. Refactor `ArdupilotConnectionThread`:
   - Remove duplicate telemetry processing (keep only `process_telemetry`, remove `updateData`)
   - Fix `connected` vs `is_connected` attribute mismatch (line 195, 212)
   - Remove dead `convert_telemetry_to_mavlink_format` method
   - Add `receive_target_data(color, lat, lon)` to forward detection to USV via MAVLink
4. Update `MainWindow.py`:
   - Add second serial port selector for drone
   - Add drone connection button
   - Route connection lifecycle through ConnectionManager
   - Add drone status indicator (connected/disconnected)
5. Update UI to show dual connection status

### 1.2 Connection 1: GCS ↔ USV

**Protocol**: MAVLink over serial (RFD900x v2, 900 MHz)
**Baud rate**: 57600 (RFD900x default) or 115200
**Data flow**:
- GCS → USV: Mission waypoints (MISSION_ITEM_INT), ARM, MISSION_START, mode changes
- USV → GCS: Telemetry (GLOBAL_POSITION_INT, ATTITUDE, VFR_HUD, SYS_STATUS, BATTERY_STATUS, SERVO_OUTPUT_RAW, RANGEFINDER)

**Current state**: Mostly implemented. Needs cleanup:
1. Fix telemetry_widget attribute mismatch (`connected` → `is_connected`)
2. Remove duplicate processing in `updateData`
3. Fix RTL button (`QRTL` → `RTL`)
4. Add telemetry data logging (see Priority 2)

### 1.3 Connection 2: GCS ↔ Drone

**Protocol**: MAVLink over serial (SiK Telemetry Radio)
**Baud rate**: 57600 (SiK default)
**Data flow**:
- Drone → GCS: Position, battery, target detection results (color + GPS coords)
- GCS → Drone: None (drone is RC-controlled only per competition rules)

**Implementation Steps**:
1. Create `DroneConnectionThread` class (lighter than USV connection):
   - Only needs to RECEIVE telemetry, no mission upload
   - Process HEARTBEAT (verify it's a copter), GLOBAL_POSITION_INT, SYS_STATUS
   - Listen for target detection data via:
     - Option A: STATUSTEXT messages with encoded data (e.g., `TARGET:RED:41.037:29.029`)
     - Option B: Custom MAVLink message (requires pymavlink dialect extension)
     - Option C: Named value messages (DEBUG_VECT or NAMED_VALUE_FLOAT)
   - Recommendation: Use STATUSTEXT for simplicity — the drone's Jetson Nano sends formatted text
2. Add drone marker to MapWidget (different icon from USV)
3. Add drone telemetry panel to IndicatorsPage or new DroneStatusWidget
4. Implement target relay: when drone detects target → GCS displays → GCS sends to USV

### 1.4 Connection Manager Integration

**How both connections coexist**:
- Each connection runs in its own QThread (already the pattern for USV)
- ConnectionManager holds references to both threads
- Qt signal/slot mechanism connects threads to UI (thread-safe by design)
- No shared state between connections — each has its own mavutil instance

**Failover and reconnection**:
- Auto-reconnect with exponential backoff (5s, 10s, 20s, max 60s)
- Connection health monitored via HEARTBEAT timeout (5 seconds)
- If USV disconnects: show warning, keep drone connected
- If drone disconnects: show warning, keep USV connected (drone is optional)

**Status indicators**:
- Two connection status indicators in the status bar
- USV: green (connected) / red (disconnected) / yellow (connecting)
- Drone: green / red / gray (not configured)

---

## Priority 2 — Missing Competition Features

### 2.1 Telemetry CSV Logger

**What**: Log all telemetry data to CSV file during competition.

**Why**: Competition requires delivery of telemetry CSV within 20 minutes (requirement #39).

**Files to create**:
- `TelemetryLogger.py`

**Files to modify**:
- `Vehicle/ArdupilotConnection.py` — emit telemetry data signal
- `MainWindow.py` — start/stop logger with connection

**Implementation Steps**:
1. Create `TelemetryLogger` class:
   - Opens CSV file with timestamp in filename: `telemetry_YYYYMMDD_HHMMSS.csv`
   - Header: `timestamp,lat,lon,speed,roll,pitch,heading,speed_setpoint,heading_setpoint`
   - Receives telemetry via Qt signal connection
   - Writes at minimum 1 Hz (guaranteed by ArduPilot stream rate)
   - Flush buffer every 5 seconds to prevent data loss
   - Auto-stop after 20 minutes (competition time limit)
2. Add start/stop logging buttons to UI
3. Add recording indicator (red dot when logging)

### 2.2 Parkour State Machine

**What**: Manage the 3-parkour competition flow with automatic transitions.

**Why**: Competition requires automatic parkour transitions with no user input (requirement #29).

**Files to create**:
- `ParkourStateMachine.py`

**Files to modify**:
- `TargetsPage.py` — integrate state machine with mission control
- `MainWindow.py` — display current parkour state

**Implementation Steps**:
1. Create `ParkourStateMachine` with states:
   - `IDLE` → `PARKOUR_1` → `PARKOUR_2` → `PARKOUR_3` → `COMPLETED`
   - Plus: `RETURNING` (after P3, return to start)
2. Parkour completion detection:
   - P1: All waypoints reached (MISSION_ITEM_REACHED message)
   - P2: Final waypoint reached
   - P3: Target contact confirmed (manual or sensor-based)
3. Auto-transition logic:
   - On P1 complete → clear mission → upload P2 waypoints → set AUTO → start
   - On P2 complete → transition to P3 engagement mode
   - On P3 complete → switch to MANUAL for return
4. Display current parkour in UI with progress indicator
5. Lock UI controls during autonomous phases (requirement #24)

### 2.3 Competition Timer

**What**: 20-minute countdown timer that starts when team enters competition area.

**Why**: Competition time is 20 minutes (requirement #30). Must track remaining time.

**Files to modify**:
- `MainWindow.py` — add timer display and controls

**Implementation Steps**:
1. Add `QTimer`-based countdown (20:00 → 0:00)
2. Start button (triggered on competition entry)
3. Display in toolbar/status bar with color coding:
   - Green: > 10 min remaining
   - Yellow: 5-10 min remaining
   - Red: < 5 min remaining
4. Audio/visual alert at 5 min, 2 min, 30 sec marks
5. Timer does NOT stop between parkours

### 2.4 UI Lockout After Mission Start

**What**: Disable command buttons after mission starts.

**Why**: Competition rules prohibit any commands after mission start except emergency kill (requirement #24).

**Files to modify**:
- `TargetsPage.py` — disable buttons after ARM + MISSION_START
- `MainWindow.py` — lock mode buttons

**Implementation Steps**:
1. After successful MISSION_START:
   - Disable: upload, arm, start, mode change buttons
   - Keep enabled: EMERGENCY KILL button only
2. Re-enable on: mission complete, emergency kill activated, or manual override
3. Visual indication: grayed out buttons, "AUTONOMOUS MODE" banner

### 2.5 Coordinate File Loading (Competition Format)

**What**: Load mission coordinates from USB-provided file in dd.dddddd format.

**Why**: Competition provides waypoints on USB drive in specific format (requirement #25).

**Files to modify**:
- `TargetsPage.py` — enhance file loader for competition format

**Implementation Steps**:
1. Support coordinate file formats:
   - Plain text: one coordinate pair per line (`lat,lon` in decimal degrees)
   - Detect and handle both comma and tab separators
2. Auto-detect parkour assignment (P1 = first 4 waypoints, P2 = remaining, etc.)
3. Validate coordinates are in competition area (reasonable lat/lon range)
4. Preview waypoints on map before upload

### 2.6 Fix USV Telemetry Widget

**What**: Uncomment `setupUi` and fix the USV telemetry dashboard.

**Why**: Widget currently displays NOTHING (requirement #21).

**Files to modify**:
- `USVTelemetryWidget.py` — uncomment line 10, verify all label references

**Implementation Steps**:
1. Uncomment `self.setupUi(self)` on line 10
2. Verify all `hasattr` label checks match the .ui file widget names
3. Test with simulated telemetry data
4. Add missing fields if needed: mode, armed status, GPS fix quality

### 2.7 Drone Telemetry Display

**What**: New UI panel showing drone status (position, battery, detection results).

**Why**: Need to monitor drone during competition and see target detections (requirements #32-37).

**Files to create**:
- `DroneStatusWidget.py`

**Files to modify**:
- `IndicatorsPage.py` or `HomePage.py` — add drone status panel
- `MapWidget.py` — add drone marker with different icon

**Implementation Steps**:
1. Create compact drone status widget:
   - Connection status indicator
   - Battery percentage + voltage
   - GPS position (lat, lon, alt)
   - Last detected target: color + position + timestamp
2. Add drone marker to map (different color/icon from USV)
3. Show drone flight zone boundary on map (shore area limitation)
4. When target detected: flash notification, display color, show on map

### 2.8 Target Detection Relay

**What**: Receive target color + position from drone, display on GCS, relay to USV.

**Why**: Parkur-3 requires drone to detect colored target, relay info to USV (requirements #34, #37).

**Files to create**:
- Part of `DroneConnection.py` and `ConnectionManager.py`

**Implementation Steps**:
1. Parse incoming target data from drone (color: RED/GREEN/BLUE, position: lat/lon)
2. Display detected target on map with color marker
3. Show prominent alert: "TARGET DETECTED: [COLOR] at [POSITION]"
4. Relay to USV via MAVLink:
   - Use SET_POSITION_TARGET_GLOBAL_INT to send target position
   - Or use STATUSTEXT to send color information
   - Or use custom MAVLink message
5. Confirm USV received the data (ACK)

---

## Priority 3 — Bug Fixes

Ordered by severity. Reference: AUDIT_REPORT.md

### 3.1 Critical Fixes

| # | Bug | File | Fix |
|---|-----|------|-----|
| 1 | Firebase keys in git | `Database/*.json` | Add to `.gitignore`, revoke keys, use env vars |
| 2 | pickle.loads() RCE | `deneme/oldClient.py` | Replace with JSON/msgpack (or delete — it's experimental) |
| 3 | `connected` vs `is_connected` | `Vehicle/ArdupilotConnection.py:195,212` | Change to `is_connected` |
| 4 | `setupUi` commented out | `USVTelemetryWidget.py:10` | Uncomment |

### 3.2 Major Fixes

| # | Bug | File | Fix |
|---|-----|------|-----|
| 5 | `set_mode_apm("QRTL")` | `MainWindow.py:116` | Change to `"RTL"` |
| 6 | `sys.exit()` no cleanup | `MainWindow.py:86` | Add `closeEvent` with thread stop |
| 7 | Duplicate telemetry processing | `Vehicle/ArdupilotConnection.py:346-355` | Remove `updateData` path, keep `process_telemetry` only |
| 8 | Hardcoded 3-level parent chain | `Database/VideoStream.py:43` | Pass target callback via constructor |
| 9 | Division by zero | `MediaPlayer.py:221` | Guard with `max(video_length, 1)` |
| 10 | `updateHeading` → `updateRoll` | `TelemetryWidget.py:568` | Fix redirect to correct method |
| 11 | Antenna tracking never stops | `TargetsPage.py:416-422` | Add thread termination flag |
| 12 | Class-level mutable mission | `MapWidget.py:45` | Move to `__init__` |

### 3.3 Minor Fixes

| # | Bug | File | Fix |
|---|-----|------|-----|
| 13 | Excessive print() | Multiple | Replace with `logging` module |
| 14 | Hardcoded Canberra coords | Multiple:559,405 | Make configurable or remove |
| 15 | Missing requirements.txt deps | `requirements.txt` | Add: opencv-python, python-vlc, pyserial, numpy, msgpack |
| 16 | map.html in git | `.gitignore` | Add `map.html` |
| 17 | pytest.ini wrong testpaths | `pytest.ini` | Change to `.` or move test files to `tests/` |
| 18 | Azimuth calculation incorrect | `AntennaTracker.py:49` | Apply longitude compression factor |
| 19 | Platform-dependent struct | `Database/VideoStream.py:96` | Use `!I` instead of `L` |
| 20 | Dead code | `Vehicle/ArdupilotConnection.py:447-510` | Remove `convert_telemetry_to_mavlink_format` |

---

## Priority 4 — Polish and Testing

### 4.1 Test Infrastructure

1. Fix `pytest.ini` to discover tests correctly
2. Move test files to `tests/` directory
3. Fix mock objects in existing tests to match actual class interfaces
4. Add conftest fixtures for:
   - Mock MAVLink connection
   - Mock QApplication
   - Simulated telemetry data generator

### 4.2 Integration Tests

1. **Dual connection test**: Connect to two SITL instances simultaneously
2. **Mission upload test**: Upload 4-waypoint mission, verify ACK
3. **Telemetry logging test**: Run for 10 seconds, verify CSV output
4. **Parkour transition test**: Simulate P1→P2→P3 state transitions
5. **Target relay test**: Simulate drone detection, verify USV receives data

### 4.3 Competition Rehearsal

1. Full 20-minute simulated run with:
   - SITL USV (ArduPilot Rover)
   - SITL Drone (ArduPilot Copter) — optional
   - Gazebo/VRX for realistic water simulation
2. Test coordinate file loading from USB
3. Test telemetry CSV export
4. Test emergency kill at various stages
5. Verify UI lockout behavior

### 4.4 UI Polish

1. Add connection status icons to toolbar
2. Add competition mode toggle (locks non-essential features)
3. Clean up debug prints (replace with logging)
4. Update README to describe USV (not UAV)
5. Add About dialog with version info

---

## Estimated Task Breakdown

| Task | Priority | Complexity | Dependencies | Files |
|------|----------|------------|--------------|-------|
| ConnectionManager class | P1 | L | None | NEW: ConnectionManager.py |
| DroneConnectionThread | P1 | M | ConnectionManager | NEW: DroneConnection.py |
| Refactor ArdupilotConnection | P1 | M | ConnectionManager | Vehicle/ArdupilotConnection.py |
| Dual connection UI | P1 | M | ConnectionManager | MainWindow.py |
| Fix `is_connected` mismatch | P1 | S | None | Vehicle/ArdupilotConnection.py |
| Fix `setupUi` commented out | P1 | S | None | USVTelemetryWidget.py |
| TelemetryLogger | P2 | M | ArdupilotConnection | NEW: TelemetryLogger.py |
| ParkourStateMachine | P2 | L | Mission upload | NEW: ParkourStateMachine.py |
| Competition timer | P2 | S | None | MainWindow.py |
| UI lockout after start | P2 | S | ParkourStateMachine | TargetsPage.py, MainWindow.py |
| Coordinate file loader | P2 | S | None | TargetsPage.py |
| DroneStatusWidget | P2 | M | DroneConnection | NEW: DroneStatusWidget.py |
| Target detection relay | P2 | M | DroneConnection, ConnectionManager | ConnectionManager.py |
| Drone marker on map | P2 | S | DroneConnection | MapWidget.py |
| Fix RTL button crash | P3 | S | None | MainWindow.py |
| Fix sys.exit cleanup | P3 | S | None | MainWindow.py |
| Remove duplicate telemetry | P3 | M | None | Vehicle/ArdupilotConnection.py |
| Fix heading/roll mismatch | P3 | S | None | TelemetryWidget.py |
| Fix division by zero | P3 | S | None | MediaPlayer.py |
| Security: Firebase keys | P3 | S | None | .gitignore, Database/ |
| Update requirements.txt | P3 | S | None | requirements.txt |
| Replace print with logging | P4 | M | None | Multiple files |
| Fix pytest infrastructure | P4 | M | None | pytest.ini, tests/ |
| Integration tests | P4 | L | All P1+P2 features | tests/ |
| Competition rehearsal | P4 | L | All above | — |
| UI polish | P4 | M | None | Multiple files |

### Complexity Legend
- **S** (Small): < 1 hour, single file change
- **M** (Medium): 1-4 hours, 2-3 files affected
- **L** (Large): 4+ hours, multiple files, new architecture

### Recommended Implementation Order
1. Fix critical bugs first (S tasks in P1/P3): `is_connected`, `setupUi`, RTL button, `sys.exit`
2. Build ConnectionManager + DroneConnection (P1 core)
3. Integrate dual connection into UI (P1)
4. Add TelemetryLogger (P2 — needed for demo video)
5. Add ParkourStateMachine (P2 — needed for demo video)
6. Add competition timer + UI lockout (P2)
7. Add DroneStatusWidget + target relay (P2)
8. Remaining bug fixes (P3)
9. Tests and polish (P4)

---

## New Files Summary

| File | Purpose |
|------|---------|
| `ConnectionManager.py` | Orchestrates dual MAVLink connections |
| `DroneConnection.py` | Drone-specific MAVLink thread |
| `TelemetryLogger.py` | CSV telemetry data recording |
| `ParkourStateMachine.py` | 3-parkour competition flow management |
| `DroneStatusWidget.py` | Drone telemetry + detection display |

---

**Total sections**: 15 major sections
**Word count**: ~3,200 words
**Generated**: 2026-03-21
