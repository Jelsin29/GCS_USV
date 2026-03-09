# MAVLink Specialist Memory

See topic files for details. Lines here are kept short for system-prompt inclusion.

## Key Architectural Facts
- Main connection thread: `Vehicle/ArdupilotConnection.py` → `ArdupilotConnectionThread(QThread)`
- pymavlink connection object is NOT thread-safe; only one caller may call `recv_match` at a time
- run() loop and command methods (upload_mission, arm_vehicle, set_mode, start_mission, disarm_vehicle)
  share the same connection object — must use `_pause_recv_loop()` / `_resume_recv_loop()` protocol
- See `patterns.md` for the reference-counted pause mechanism details

## Confirmed Patterns
- `_stop_recv` (threading.Event) + `_stop_recv_count` (int) + `_stop_recv_lock` (Lock) in `__init__`
- `_pause_recv_loop()` increments count, sets event, sleeps 0.3 s; `_resume_recv_loop()` decrements,
  clears event only when count reaches 0 (re-entrant safe: arm_vehicle → set_mode chain works)
- run() loop: check `_stop_recv.is_set()` first, then `recv_match(blocking=True, timeout=0.2)`
- All five command methods wrap body in `self._pause_recv_loop()` / `try: ... finally: self._resume_recv_loop()`

## Known Firmware / Config Notes
- `SER1_PROTOCOL` param_set must NOT be sent over SITL/UDP — produces NACK noise, not applicable
- `configure_ardupilot_timeouts()` sleep reduced from 2.0 s to 0.1 s (no blocking purpose)
- `MIS_TIMEOUT=60`, `MIS_OPTIONS=1` are the only params set in configure_ardupilot_timeouts()

## Qt Threading
- All telemetry UI updates go through Qt signals, never direct calls from QThread methods
- `mission_status`, `telemetry_update`, `connection_status` signals defined on the thread class
