# MAVLink / Qt Threading Patterns

## Re-entrant Recv-Loop Pause Protocol

### Problem
`ArdupilotConnectionThread.run()` calls `recv_match` in a loop.  Command methods
(upload_mission, arm_vehicle, set_mode, start_mission, disarm_vehicle) are called
from the Qt main thread.  Both paths call `recv_match` on the same pymavlink
connection object — which is not thread-safe.  The run() loop steals
MISSION_REQUEST_INT / MISSION_ACK / COMMAND_ACK messages before the command
methods can see them.

### Solution (implemented 2026-03)
Three instance variables added in `__init__`:
```python
self._stop_recv = threading.Event()
self._stop_recv_count = 0
self._stop_recv_lock = threading.Lock()
```

Two helper methods:
```python
def _pause_recv_loop(self):
    with self._stop_recv_lock:
        self._stop_recv_count += 1
        self._stop_recv.set()
    time.sleep(0.3)  # outlast the 0.2 s recv_match timeout in run()

def _resume_recv_loop(self):
    with self._stop_recv_lock:
        self._stop_recv_count = max(0, self._stop_recv_count - 1)
        if self._stop_recv_count == 0:
            self._stop_recv.clear()
```

run() loop change:
```python
if self._stop_recv.is_set():
    self.msleep(50)
    continue
message = self.connection.recv_match(blocking=True, timeout=0.2)  # was timeout=5
```

Command method wrapper template:
```python
def some_command(self):
    if not self.connection:
        return False
    self._pause_recv_loop()
    try:
        # ... recv_match calls here are safe ...
    except Exception as e:
        ...
        return False
    finally:
        self._resume_recv_loop()
```

### Re-entrancy
`arm_vehicle` calls `set_mode`, which also calls `_pause_recv_loop`.  The counter
ensures the loop stays paused until both `finally` blocks have executed.

### Timing
- run() recv_match timeout: 0.2 s (guarantees loop exits current call within 0.2 s)
- _pause_recv_loop sleep: 0.3 s (0.2 s + 0.1 s buffer)
- Total pause latency: ~0.3 s per call level (nested calls don't add latency because
  the event is already set when the inner _pause_recv_loop runs)
