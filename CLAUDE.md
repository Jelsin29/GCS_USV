# USV Ground Control Station — Project Context

## What This Project Is

Ground Control Station (GCS) for an Unmanned Surface Vehicle (USV) built in Python.
Controls and monitors a boat running ArduPilot Rover firmware (FRAME_CLASS=2) via MAVLink.
Connects to real hardware over serial/UDP and to simulation via ArduPilot SITL.

## Stack

- Language: Python 3.12
- Virtual environment: ~/venv-ardupilot
- MAVLink library: pymavlink
- Async: asyncio (all I/O must be non-blocking)
- Simulation: ArduPilot SITL via sim_vehicle.py -v Rover
- SITL default ports: TCP 5760 (primary), UDP 14550 (out), 5762/5763 (serial1/2)
- Type checking: mypy
- Linting: flake8 (max-line-length 100)
- Testing: pytest

## ArduPilot / MAVLink Reference

- Vehicle type: Boat (FRAME_CLASS=2)
- Firmware: ArduPilot Rover
- SITL binary: ~/ardupilot/build/sitl/bin/ardurover
- Default params: ~/ardupilot/Tools/autotest/default_params/rover.parm
- Key modes: MANUAL=0, HOLD=4, LOITER=5, AUTO=10, RTL=11, SMART_RTL=12, GUIDED=15
- Position hold active after waypoint reached in AUTO/GUIDED/RTL/SMART_RTL

## Architecture Principles

- Modular: one responsibility per file, max 300 lines per file
- Async-first: use asyncio for all serial/UDP/network I/O
- Config-driven: no hardcoded IPs, ports, baud rates, or device paths
- Safety-critical: any function sending commands to the USV must document failure modes

## Agent Delegation

Read .claude/rules/agents.md before starting any task.
Always consult the appropriate agent before implementing:

- MAVLink/comms changes → mavlink-specialist
- Telemetry parsing → telemetry-reviewer
- Mission/waypoints/modes → mission-planner-agent
- New features → /plan first
- Before commits → /code-review

## Safety Rules — Non-Negotiable

- Never modify MAVLink send logic without mavlink-specialist review
- Never push to main without /code-review passing
- Never hardcode secrets, ports, or device paths
- Always handle connection loss in every send operation
- Always validate GPS fix_type >= 3 before autonomous navigation
- Always check EKF flags before trusting position estimates
- Battery, GPS, and EKF fields are SAFETY CRITICAL — never skip validation

## Running SITL

```bash
cd ~/ardupilot
source ~/venv-ardupilot/bin/activate
sim_vehicle.py -v Rover --console --map
# With speedup:
sim_vehicle.py -v Rover --console --map --speedup 5
# MAVProxy connects to TCP 5760, forwards UDP to 14550
```

## Key MAVLink Ports (SITL)

| Port      | Purpose                       |
| --------- | ----------------------------- |
| TCP 5760  | Primary MAVLink (SERIAL0)     |
| TCP 5762  | SERIAL1                       |
| TCP 5763  | SERIAL2                       |
| UDP 14550 | GCS output (MAVProxy forward) |
| UDP 5501  | SITL input                    |

## ArduPilot Docs

- Boat config: https://ardupilot.org/rover/docs/boat-configuration.html
- Rover params: https://ardupilot.org/rover/docs/parameters.html
- MAVLink messages: https://mavlink.io/en/messages/common.html
- pymavlink: https://github.com/ArduPilot/pymavlink

## Development Workflow

1. /plan → review plan → confirm
2. /tdd → implement → /verify
3. /code-review → fix issues
4. If network/serial touched → security-reviewer
5. /refactor-clean after feature complete
6. /checkpoint for long sessions

## MCP Tools — When to Use

### Serena

Use Serena for:

- Understanding how modules connect before making changes
- Finding all usages of a function or class across the codebase
- Refactoring that affects multiple files
- Before /plan on any feature touching 3+ files

### Pyright LSP

Use Pyright for:

- Validating type correctness after writing new functions
- Checking imports resolve correctly
- Before /code-review on any Python file

## TargetsPage — Key Buttons Reference

| Button | Object name | Action |
|--------|-------------|--------|
| LOAD FILE | `btn_set_roi` | Opens QFileDialog → parses .json/.txt → shows on map → uploads to vehicle |
| CLEAR MAP | `btn_cancel_roi` | Calls `clearAll()` JS to remove all map waypoints/shapes |
| SET MISSION | `btn_setMission` | Reads waypoints drawn on map → uploads to vehicle |
| START MISSION | `btn_startMission` | Arms vehicle and sends MAV_CMD_MISSION_START |
| ABORT | `btn_abort` | Switches vehicle to HOLD mode |
| RTL | `btn_rtl` / `btn_rtl_2` | Switches vehicle to RTL mode |

### LOAD FILE — accepted file formats

**.json** — three layouts recognised:
- `[{"lat": 1.0, "lon": 2.0}, ...]`
- `[[lat, lon], ...]` or `[[lat, lon, alt], ...]`
- `{"waypoints": [...]}` (wrapper key may be waypoints/mission/points/coords)

**.txt** — one waypoint per line, delimiter comma, tab, or space:
- `lat,lon` or `lat,lon,alt`
- Lines starting with `#` are comments and ignored

## What NOT to Do

- Do not use time.sleep() — use asyncio.sleep()
- Do not use blocking recv_match without timeout
- Do not mix coordinate systems in one function (always explicit: degrees vs int32 1e7)
- Do not enable more than 10 MCPs at once (context window protection)
- Do not skip agent delegation for safety-critical code
- Do not commit without running mypy and flake8
