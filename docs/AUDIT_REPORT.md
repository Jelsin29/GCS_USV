# GCS_USV Audit Report

**Date**: 2026-03-21
**Auditor**: Claude Code (Opus 4.6)
**Project**: Ground Control Station for Unmanned Surface Vehicle — TEKNOFEST 2026

---

## 1. Competition Requirements

Sources: TEKNOFEST 2026 Insansiz Deniz Araci Sartnamesi (PDF) + Team Technical Report Template (example_report.docx)

### 1.1 USV (IDA) Technical Requirements
1. Size: Min 75x75x30 cm, Max 150x200x200 cm
2. Weight: Max 50 kg (all payload included)
3. Power: Battery only, waterproof compartment
4. Physical kill switch: Red button on vehicle that cuts ALL motor/actuator power
5. Remote kill switch: Via GCS software or RC transmitter — must CUT power, not just signal
6. Propulsion: Any non-combustion system allowed
7. Tow hook: At least 1 for recovery
8. Sea state: Must operate up to Sea State 2
9. At least 1 onboard camera
10. Team identification: Name written in 3 locations (port, starboard, stern)

### 1.2 Communication Requirements
11. NO 2.4-2.8 GHz or 5.15-5.85 GHz modules (WiFi bands FORBIDDEN)
12. NO 4G/LTE modems
13. All laptop/computer built-in WiFi must be DISABLED
14. Only telemetry + RC transmitter/receiver modules allowed
15. Frequency channels must be selectable
16. USV GCS can serve as relay for IDA-IHA communication
17. No image/video transfer from USV or Drone to ANY ground station or third party
18. Autonomy/sensor processing software MUST run ON the vehicles, NOT on GCS

### 1.3 GCS (YKI) Requirements
19. Show waypoints/mission points on map
20. Show real-time vehicle position with waypoints on map
21. Show vehicle status and mode information
22. Mission upload capability (wired or wireless)
23. Mission start command from GCS or RC
24. NO commands allowed after mission starts (except emergency kill)
25. Mission coordinates received as file (dd.dddddd format) before competition

### 1.4 Competition Parkour Tasks
26. Parkur-1: Autonomous waypoint following (no obstacles) — 4 waypoints forming rectangle
27. Parkur-2: Autonomous obstacle avoidance navigation — reach final waypoint avoiding buoys
28. Parkur-3: Kamikaze engagement — physical contact with target buoy of correct color
29. Automatic transition between parkours (no user input between parkurs)
30. Total competition time: 20 minutes
31. Mission upload AFTER entering competition area and powering on USV

### 1.5 Drone (IHA) Requirements (Optional)
32. Drone max 5 kg
33. Drone controlled via RC (manual)
34. Drone detects colored target plate on shore, relays color to USV
35. Drone components must be secured
36. Drone flight zone limited to shore area
37. USV GCS can relay drone data to USV

### 1.6 Data Deliverables (within 20 min post-competition)
38. File 1: Autonomy sensor data — camera feed (1 Hz min, mp4, with detection overlays)
39. File 2: Telemetry CSV — lat, lon, speed, roll/pitch/heading, speed setpoint, heading setpoint (1 Hz min)
40. File 3: Local cost map / obstacle map (1 Hz min)

### 1.7 Team Architecture (from example_report.docx)
41. GCS ↔ USV communication via RFD900x v2 (900 MHz band)
42. GCS ↔ Drone communication via Holybro SiK Telemetry Radio
43. Drone carries Jetson Nano + Logitech C920 camera
44. USV carries Jetson Orin Nano + LIDAR
45. Drone processes vision locally, sends semantic data (not raw video) to USV
46. 3 cameras total for image processing on USV
47. Drone acts as elevated radio relay node between GCS and USV

### 1.8 Report Requirements
48. Technical Qualification Report (TYR): max 12 pages, deadline 24.03.2026 (PASSED)
49. Critical Design Report (KTR): max 30 pages, deadline 20.05.2026
50. Autonomy Demo Video: deadline 21.07.2026
51. Academic formatting: Arial 12pt, Arial Black 14pt headings, 1.15 line spacing

---

## 2. File-by-File Analysis

| File | Purpose | Status | Critical Issues |
|------|---------|--------|-----------------|
| `main.py` | App entry point, QApplication + MainWindow | Working | Firebase thread reference lost, no shutdown cleanup |
| `MainWindow.py` | Frameless main window, page navigation, connection management | Partial | `set_mode_apm("QRTL")` crash, `sys.exit()` without cleanup, dead code, hardcoded coords |
| `HomePage.py` | Dashboard with map, camera, telemetry | Working | Hardcoded Istanbul coords, orphaned widget, missing null checks |
| `IndicatorsPage.py` | Flight instruments (speed, heading, altitude) | Partial | Empty methods, broken animation property, excessive debug prints |
| `TargetsPage.py` | Mission control, waypoint management, mission upload | Partial | Antenna tracking never stops, deep parent chain crashes, naming confusion |
| `MapWidget.py` | Folium/Leaflet map in QWebEngineView | Working | Class-level mutable `mission=[]`, side effects at import, writes map.html to disk |
| `CameraWidget.py` | Video feed display | Working | Hardcoded default IP, socket never closed on disconnect |
| `MediaPlayer.py` | VLC player for recorded footage | Partial | Division by zero, hardcoded path, deep parent chain |
| `TelemetryWidget.py` | 5-param telemetry display | Partial | `updateHeading` redirects to `updateRoll` (wrong), excessive prints |
| `USVTelemetryWidget.py` | USV-specific telemetry dashboard | Broken | `setupUi` COMMENTED OUT — widget displays NOTHING |
| `AntennaTracker.py` | Arduino servo antenna tracking | Partial | Incorrect azimuth calculation, hardcoded serial ports, no shutdown |
| `IconUtils.py` | SVG icon color conversion | Working | Bare `except:` clause |
| `indicators_rc.py` | Auto-generated Qt resources | Working | Duplicated with `uifolder/rc_indicators.py` |
| `FirebaseUserTest.py` | Firebase test script | Broken | Executes on import, no `__main__` guard |
| `Vehicle/ArdupilotConnection.py` | MAVLink connection, telemetry, mission upload | Partial | `connected` vs `is_connected` attribute mismatch blocks telemetry, duplicate processing, dead code |
| `Vehicle/Exploration.py` | Lawnmower survey pattern generation | Working | Assumes aerial drone parameters (altitude, FOV, camera_angle) |
| `Database/Cloud.py` | Firebase sync thread | Partial | Marker data never updated (stays at 0) |
| `Database/users_db.py` | Firebase RTDB wrapper | Partial | Hardcoded credentials path, not thread-safe |
| `Database/VideoStream.py` | Video stream client with detection data | Partial | Platform-dependent struct, hardcoded parent chain, socket never closed |
| `deneme/server.py` | Experimental video server | Broken | Platform-dependent struct packing |
| `deneme/VideoStream.py` | Experimental video client | Broken | Platform-dependent struct packing |
| `deneme/socketCameraServer.py` | Socket camera server | Broken | Fragile IP detection hack |
| `deneme/socketCameraReceiver.py` | Socket camera receiver | Broken | Hardcoded IP |
| `deneme/oldClient.py` | Legacy client | Broken | pickle.loads() SECURITY VULN, unreachable code |
| `deneme/firebase.py` | Firebase utilities | Broken | Executes at import time, different credential path |
| `uifolder/main.py` | Standalone test for indicators | Broken | Calls nonexistent `gyrometer` method |
| `uifolder/rc_indicators.py` | Auto-generated Qt resources | Working | Duplicate of root-level `indicators_rc.py` |
| `map.html` | Auto-generated Leaflet map | N/A | Tracked in git, should be in .gitignore |
| `requirements.txt` | Package dependencies | Incomplete | Missing 5 dependencies |
| `pytest.ini` | Test configuration | Broken | `testpaths = tests` but tests are in root |
| `tests/conftest.py` | Pytest fixtures | Working | Only file in tests/ directory |
| `test_*.py` (6 files) | Various test scripts | Broken | Call nonexistent methods, incorrect mocking, never discovered by pytest |
| `debug_mission.py` | Debug script | Working | Not a proper test |

---

## 3. Gap Analysis

### Competition Requirements vs Current Implementation

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1-10 | USV physical specs | N/A | Hardware, not software |
| 11-13 | WiFi/4G bands forbidden | N/A | Hardware config |
| 14 | Telemetry + RC only | ✅ DONE | Uses MAVLink telemetry via serial |
| 15 | Selectable frequency channels | N/A | Hardware config |
| 16 | GCS as relay for IDA-IHA | ❌ MISSING | No drone connection support |
| 17 | No image transfer to GCS | ⚠ PARTIAL | VideoStream.py receives frames — may violate rules |
| 18 | Autonomy runs on vehicles | ✅ DONE | GCS only sends missions, doesn't run autonomy |
| 19 | Show waypoints on map | ✅ DONE | MapWidget supports waypoint display |
| 20 | Show real-time position on map | ✅ DONE | USV marker updated via GLOBAL_POSITION_INT |
| 21 | Show vehicle status/mode | ⚠ PARTIAL | USVTelemetryWidget is broken (setupUi commented), TelemetryWidget has heading/roll bug |
| 22 | Mission upload capability | ✅ DONE | Full MAVLink mission protocol implemented |
| 23 | Mission start from GCS | ✅ DONE | ARM + MISSION_START commands |
| 24 | No commands after start | ⚠ PARTIAL | UI doesn't lock after mission start, buttons remain clickable |
| 25 | Mission from coordinate file | ✅ DONE | JSON and TXT file loading implemented |
| 26 | Parkur-1: Waypoint following | ✅ DONE | Mission upload + AUTO mode |
| 27 | Parkur-2: Obstacle avoidance | ❌ MISSING | No obstacle avoidance logic (runs on vehicle, but GCS needs to support mission with obstacle data) |
| 28 | Parkur-3: Kamikaze engagement | ❌ MISSING | No target engagement logic, no color-based target selection |
| 29 | Auto transition between parkours | ❌ MISSING | No parkour state machine or auto-transition logic |
| 30 | 20 min competition timer | ❌ MISSING | No timer in GCS |
| 31 | Upload after entering area | ✅ DONE | Manual upload via button |
| 32-37 | Drone requirements | ❌ MISSING | No drone connection, no drone telemetry, no color detection relay |
| 38 | Autonomy sensor data recording | ❌ MISSING | No on-GCS recording of autonomy data |
| 39 | Telemetry CSV logging | ❌ MISSING | No telemetry data logging to file |
| 40 | Cost map / obstacle map | ❌ MISSING | No cost map support |
| 41 | GCS ↔ USV via RFD900x | ⚠ PARTIAL | Serial connection works, but no RFD900x-specific config |
| 42 | GCS ↔ Drone via SiK | ❌ MISSING | No second connection support |
| 43-47 | Drone/USV onboard processing | N/A | Runs on vehicle hardware |
| 48-51 | Reports | N/A | Document deliverables, not software |

### Summary
- ✅ DONE: 8 requirements
- ⚠ PARTIAL: 5 requirements
- ❌ MISSING: 12 requirements (software-related)
- N/A: 25 requirements (hardware, docs, or vehicle-side)

### CRITICAL GAPS

1. **No Dual-Connection Architecture**: The entire system supports only ONE MAVLink connection. Competition requires simultaneous GCS↔USV and GCS↔Drone connections.
2. **No Drone Integration**: No drone telemetry display, no color detection relay, no drone↔USV data forwarding.
3. **No Parkour State Machine**: No automatic transition between parkours, no competition timer, no parkour completion detection.
4. **No Telemetry Logging**: Competition requires CSV telemetry data delivery within 20 minutes. Nothing is logged.
5. **USV Telemetry Widget Broken**: `setupUi` is commented out — the widget displays nothing.
6. **No UI Lockout After Mission Start**: Buttons remain clickable during autonomous operation, violating competition rules.

---

## 4. Bugs and Issues

### Critical (Blocks Competition)

| # | File | Line | Issue | Impact |
|---|------|------|-------|--------|
| C1 | `Database/*.json` | — | Firebase private keys committed to git | Security: full database access for anyone with repo history |
| C2 | `deneme/oldClient.py` | 40 | `pickle.loads()` on network data | Security: arbitrary code execution vulnerability |
| C3 | `Vehicle/ArdupilotConnection.py` | 195, 212 | `telemetry_widget.connected` should be `is_connected` | Telemetry never reaches widgets via legacy path |
| C4 | `USVTelemetryWidget.py` | 10 | `setupUi(self)` is commented out | Entire USV telemetry widget displays NOTHING |
| C5 | — | — | No dual-connection support | Cannot connect to both USV and drone simultaneously |
| C6 | — | — | No telemetry CSV logging | Cannot deliver required competition data |

### Major (Degrades Functionality)

| # | File | Line | Issue | Impact |
|---|------|------|-------|--------|
| M1 | `MainWindow.py` | 116 | `set_mode_apm("QRTL")` does not exist | RTL button crashes the app |
| M2 | `MainWindow.py` | 86 | `sys.exit()` without thread cleanup | Resource leak, potential data corruption on exit |
| M3 | `Vehicle/ArdupilotConnection.py` | 346-355 | Duplicate telemetry processing paths | Double processing of every message, wasted CPU |
| M4 | `Database/VideoStream.py` | 43 | Hardcoded 3-level parent chain | Crashes if widget hierarchy changes |
| M5 | `MediaPlayer.py` | 221 | Division by zero if `video_length` is 0 | Crash on startup |
| M6 | `TelemetryWidget.py` | 568-569 | `updateHeading` redirects to `updateRoll` | Wrong telemetry displayed |
| M7 | `TargetsPage.py` | 416-422 | `stop_antenna_tracking` doesn't stop thread | Antenna tracking runs forever |
| M8 | `MapWidget.py` | 45 | Class-level mutable `mission = []` | All MapWidget instances share same mission list |

### Minor (Cosmetic or Code Quality)

| # | File | Line | Issue |
|---|------|------|-------|
| m1 | Multiple | — | 100+ debug `print()` statements flooding console |
| m2 | `MainWindow.py`, `TargetsPage.py`, `AntennaTracker.py` | 559, 405 | Hardcoded coordinates (-35.3635, 149.1652 = Canberra) |
| m3 | Multiple | — | Relative asset paths break if CWD changes |
| m4 | `Readme.md` | — | Describes UAV but code is for USV |
| m5 | `HomePage.py` | 29 | Orphaned widget not deleted (memory leak) |
| m6 | `IndicatorsPage.py` | 239-247 | Empty method body (dead code) |
| m7 | `Vehicle/ArdupilotConnection.py` | 447-510 | `convert_telemetry_to_mavlink_format` never called (dead code) |
| m8 | `requirements.txt` | — | Missing 5 dependencies: opencv-python, python-vlc, pyserial, numpy, msgpack |
| m9 | `map.html` | — | Auto-generated file tracked in git |
| m10 | `indicators_rc.py` / `rc_indicators.py` | — | Duplicated resource files |
| m11 | `pytest.ini` | 2 | `testpaths = tests` but test files are in project root |
| m12 | `AntennaTracker.py` | 49 | Azimuth calculation incorrect at non-equatorial latitudes |
| m13 | `Database/VideoStream.py` | 96 | `struct.unpack("L")` is platform-dependent |
| m14 | `Database/users_db.py` | 76-106 | Getters overwrite `self.user_ref` (not thread-safe) |

---

## 5. Security Concerns

### CRITICAL: Firebase Credentials Committed to Git

**Files**:
- `Database/ilkdeneme-5656-firebase-adminsdk-10hg3-741e03da89.json`
- `Database/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json`

Both contain FULL RSA private keys for Firebase Admin SDK service accounts. Anyone with access to the git history can:
- Read/write the entire Firebase Realtime Database
- Access Firebase Storage
- Impersonate the service account

**Immediate Actions Required**:
1. Revoke these service account keys in Firebase Console
2. Generate new keys
3. Add `Database/*.json` to `.gitignore`
4. Use environment variables or a secrets manager
5. Consider using `git filter-branch` or BFG to remove keys from git history

### HIGH: Pickle Deserialization of Untrusted Data

**File**: `deneme/oldClient.py` line 40

`pickle.loads()` on data received from a network socket allows **arbitrary code execution**. An attacker who can send data to this socket can execute any Python code on the GCS machine.

**Action**: Replace pickle with a safe serialization format (JSON, msgpack, protobuf).

### MEDIUM: No Input Validation on Network Data

Video stream protocol (`Database/VideoStream.py`) receives binary data with no authentication, no integrity checks, and no size limits. A malformed packet could cause buffer overflows or crashes.

---

## 6. Architecture Assessment

### Current Architecture
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
                           │ MAVLink (single connection)
                           │
                    ┌──────┴──────┐
                    │    USV      │
                    │ (ArduPilot) │
                    └─────────────┘
```

### Required Architecture (Competition)
```
                    ┌──────────────────────┐
                    │      GCS (PC)        │
                    │     PySide6 UI       │
                    │                      │
                    │ ┌────────┐ ┌───────┐ │
                    │ │Serial 1│ │Serial2│ │
                    │ │RFD900x │ │  SiK  │ │
                    │ └───┬────┘ └───┬───┘ │
                    └─────┼─────────┼─────┘
                          │         │
                   MAVLink│         │MAVLink
                   (USV)  │         │(Drone)
                          │         │
                   ┌──────┴──┐  ┌───┴──────┐
                   │   USV   │  │  Drone   │
                   │ArduPilot│  │ArduPilot │
                   │Orin Nano│  │Jetson    │
                   │+ LIDAR  │  │Nano+Cam  │
                   └─────────┘  └──────────┘
```

### Gap: What's Missing
1. Second serial connection and MAVLink instance
2. Connection manager that handles both connections independently
3. Drone telemetry display (position, battery, status)
4. Target color detection data relay from drone to USV
5. Parkour state machine with auto-transitions
6. Competition timer (20 min countdown)
7. Telemetry CSV logger
8. UI lockout after mission start
9. Cost map / obstacle map display

---

**Word count**: ~2,800 words
**Generated**: 2026-03-21
