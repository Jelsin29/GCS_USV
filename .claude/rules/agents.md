# Agent Usage Rules — USV Ground Control Station

## Core Principle

Never implement directly when a specialized agent exists for the task.
Delegate first, implement second.

---

## Custom USV Agents (this project)

### mavlink-specialist

ALWAYS use when:

- Modifying any file that imports pymavlink
- Changing connection logic (serial, UDP, TCP)
- Adding or modifying MAVLink message send/receive
- Handling COMMAND*LONG, PARAM_SET, or MISSION*\* messages
- Debugging heartbeat loss or connection drops
- Reviewing baud rate, port, or protocol config changes

NEVER skip for:

- Any function that arms/disarms the USV
- Any change to message retry or timeout logic

---

### telemetry-reviewer

ALWAYS use when:

- Parsing incoming MAVLink messages (any MSG type)
- Adding new telemetry fields to the GCS state
- Modifying GPS, attitude, battery, or EKF data handling
- Building UI widgets that display live vehicle data
- Writing tests for telemetry parsing logic

NEVER skip for:

- Any field used in a safety decision (GPS fix, battery, EKF flags)
- Unit conversion code (int32 lat/lon, radians/degrees, cm/m)

---

### mission-planner-agent

ALWAYS use when:

- Implementing or modifying waypoint upload/download
- Changing AUTO, GUIDED, RTL, LOITER mode transitions
- Adding geofence logic
- Building mission editor UI
- Writing path planning algorithms
- Modifying DO*\* or NAV*\* mission commands

NEVER skip for:

- Any coordinate transformation code
- Mission handshake protocol (COUNT → REQUEST → ITEM → ACK)

---

## everything-claude-code Agents

### planner

Use BEFORE starting any feature that touches 2+ files.
Trigger: "I need to add [feature]" → run /plan first, always.
Do not write code until planner produces an implementation plan.
For GCS features: include which MAVLink messages are affected in the plan prompt.

---

### architect

Use when:

- Redesigning the communication stack
- Deciding between asyncio patterns (queue vs callback vs stream)
- Planning new major modules (e.g. adding a video feed, adding a new sensor)
- Any change that affects how modules import each other
  Do NOT use for single-file changes.

---

### tdd-guide

Use for ALL new modules and functions.
Workflow for this project:

1. Define the interface (function signature + docstring)
2. Write test covering: happy path, timeout, connection loss, malformed data
3. Implement
4. Verify with /verify
   Safety-critical functions (anything touching MAVLink send) require tests
   for failure modes, not just happy path.

---

### code-reviewer

Run before every git commit that touches:

- mavlink_handler.py or equivalent
- mission logic
- telemetry parsing
- Any async code
  Trigger: /code-review
  Do not push to main without a passing code-reviewer run.

---

### security-reviewer

MANDATORY before any commit that touches:

- Serial port or UDP socket code
- Config file loading (env vars, .yaml, .json)
- Any subprocess or shell command execution
- External data ingestion (anything received from the vehicle)
  Trigger: use security-reviewer agent

---

### build-error-resolver

Use immediately when:

- Import errors on pymavlink or asyncio dependencies
- SITL connection refused errors during testing
- pip install conflicts in venv-ardupilot
  Do not manually debug dependency errors for more than 5 minutes.

---

### refactor-cleaner

Run after completing a full feature (not mid-feature).
Trigger: /refactor-clean
Especially important after long SITL debugging sessions
that leave print() and debug flags scattered.

---

## Delegation Decision Tree

```
Task involves MAVLink send/receive?
  └─ YES → mavlink-specialist first

Task involves reading telemetry data?
  └─ YES → telemetry-reviewer first

Task involves waypoints or modes?
  └─ YES → mission-planner-agent first

New feature (2+ files)?
  └─ YES → /plan (planner agent) before any code

Architectural decision?
  └─ YES → architect agent

Writing new module?
  └─ YES → tdd-guide → implement → /verify

Before commit?
  └─ ALWAYS → /code-review
  └─ IF network/serial/config touched → security-reviewer
```

---

## Model Selection for this Project

Use Sonnet (default) for:

- Single file edits
- Adding parameters
- Writing tests for known behavior
- UI changes

Escalate to Opus for:

- Full communication stack changes
- Debugging intermittent SITL issues
- Mission upload/download protocol implementation
- Any change flagged [SAFETY CRITICAL] or [AUTONOMOUS CRITICAL] by agents

```

```
