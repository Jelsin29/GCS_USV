import sys
import time
import types


_FAKE_PYMAVLINK = "pymavlink" not in sys.modules
if _FAKE_PYMAVLINK:
    fake_mavlink = types.SimpleNamespace(
        MAV_MODE_FLAG_SAFETY_ARMED=128,
        MAV_CMD_COMPONENT_ARM_DISARM=400,
        MAV_CMD_MISSION_START=300,
        MAV_FRAME_GLOBAL_RELATIVE_ALT_INT=6,
        POSITION_TARGET_TYPEMASK_VX_IGNORE=1,
        POSITION_TARGET_TYPEMASK_VY_IGNORE=2,
        POSITION_TARGET_TYPEMASK_VZ_IGNORE=4,
        POSITION_TARGET_TYPEMASK_AX_IGNORE=8,
        POSITION_TARGET_TYPEMASK_AY_IGNORE=16,
        POSITION_TARGET_TYPEMASK_AZ_IGNORE=32,
        POSITION_TARGET_TYPEMASK_YAW_IGNORE=64,
        POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE=128,
    )
    fake_mavutil = types.SimpleNamespace(
        mavlink=fake_mavlink,
        mavlink_connection=lambda *args, **kwargs: None,
        mode_string_v10=lambda msg: "MANUAL",
    )
    pymavlink_module = types.ModuleType("pymavlink")
    pymavlink_module.mavutil = fake_mavutil
    sys.modules["pymavlink"] = pymavlink_module


_FAKE_PYSIDE6 = "PySide6" not in sys.modules
if _FAKE_PYSIDE6:

    class BoundSignal:
        def __init__(self):
            self._callbacks = []

        def connect(self, callback):
            self._callbacks.append(callback)

        def disconnect(self, callback):
            self._callbacks = [cb for cb in self._callbacks if cb != callback]

        def emit(self, *args, **kwargs):
            for callback in list(self._callbacks):
                callback(*args, **kwargs)

    class SignalDescriptor:
        def __init__(self, *args, **kwargs):
            self._name = None

        def __set_name__(self, owner, name):
            self._name = f"__signal_{name}"

        def __get__(self, instance, owner):
            if instance is None:
                return self
            signal = instance.__dict__.get(self._name)
            if signal is None:
                signal = BoundSignal()
                instance.__dict__[self._name] = signal
            return signal

    class QObject:
        def __init__(self, parent=None):
            self._parent = parent

    class QThread(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._running = False

        def start(self):
            self._running = True

        def isRunning(self):
            return self._running

        def wait(self, timeout=None):
            self._running = False
            return True

        @staticmethod
        def msleep(_ms):
            return None

    qtcore_module = types.ModuleType("PySide6.QtCore")
    qtcore_module.QObject = QObject
    qtcore_module.QThread = QThread
    qtcore_module.Signal = SignalDescriptor

    pyside6_module = types.ModuleType("PySide6")
    pyside6_module.QtCore = qtcore_module

    sys.modules["PySide6"] = pyside6_module
    sys.modules["PySide6.QtCore"] = qtcore_module

from DroneConnection import DroneConnectionThread
from ConnectionManager import ConnectionManager, StartupCoordinator, StartupState

if _FAKE_PYSIDE6:
    sys.modules.pop("PySide6.QtCore", None)
    sys.modules.pop("PySide6", None)

if _FAKE_PYMAVLINK:
    sys.modules.pop("pymavlink", None)


class FakeStatusText:
    def __init__(self, text: str):
        self.text = text

    def get_type(self):
        return "STATUSTEXT"


class FakeUSVThread:
    def __init__(self):
        self.connection = object()
        self.events = []

    def send_semantic_event(self, event):
        self.events.append(event)
        return True


def make_target_event(**overrides):
    event = {
        "id": "target-black-1",
        "event_type": "MISSION_TARGET",
        "color": "BLACK",
        "lat": 41.037083,
        "lon": 29.029528,
        "source": "drone",
        "confidence": 1.0,
        "timestamp": time.time(),
        "raw_text": "TARGET:BLUE:41.037083:29.029528",
    }
    event.update(overrides)
    return event


def test_drone_connection_parses_legacy_target_and_obstacle_messages():
    drone = DroneConnectionThread()

    legacy_target = drone._parse_semantic_event("TARGET:BLUE:41.037083:29.029528")
    assert legacy_target is not None
    assert legacy_target["event_type"] == "MISSION_TARGET"
    assert legacy_target["color"] == "BLACK"
    assert legacy_target["lat"] == 41.037083
    assert legacy_target["lon"] == 29.029528

    obstacle = drone._parse_semantic_event("OBSTACLE:BUOY:41.037100:29.029600:0.75")
    assert obstacle is not None
    assert obstacle["event_type"] == "OBSTACLE_REPORT"
    assert obstacle["obstacle_type"] == "BUOY"
    assert obstacle["confidence"] == 0.75


def test_drone_connection_emits_richer_semantic_signals():
    drone = DroneConnectionThread()
    target_events = []
    semantic_events = []
    legacy_events = []

    drone.semantic_target_detected.connect(target_events.append)
    drone.semantic_event_detected.connect(semantic_events.append)
    drone.target_detected.connect(
        lambda color, lat, lon: legacy_events.append((color, lat, lon))
    )

    drone._process_message(FakeStatusText("MISSION_TARGET:BLUE:41.037083:29.029528"))
    drone._process_message(FakeStatusText("OBSTACLE:BUOY:41.037100:29.029600:0.75"))

    assert len(target_events) == 1
    assert target_events[0]["color"] == "BLACK"
    assert len(semantic_events) == 2
    assert semantic_events[1]["event_type"] == "OBSTACLE_REPORT"
    assert legacy_events == [("BLACK", 41.037083, 29.029528)]


def test_connection_manager_deduplicates_semantic_targets_before_relay():
    usv_thread = FakeUSVThread()
    manager = ConnectionManager(usv_connection_thread=usv_thread)

    ready_events = []
    relay_statuses = []
    relay_decisions = []

    manager.semantic_target_ready.connect(ready_events.append)
    manager.relay_status.connect(relay_statuses.append)
    manager.relay_decision.connect(relay_decisions.append)

    event = make_target_event()
    manager.handle_semantic_target(event)
    manager.handle_semantic_target(make_target_event(timestamp=event["timestamp"] + 1))

    assert len(ready_events) == 1
    assert len(usv_thread.events) == 1
    assert relay_statuses[0]["status"] == "relayed"
    assert relay_statuses[1]["status"] == "suppressed"
    assert relay_decisions[1]["reason"] == "duplicate"


def test_startup_coordinator_tracks_ready_and_degraded_states():
    coordinator = StartupCoordinator()
    states = []

    coordinator.state_changed.connect(states.append)

    coordinator.mark_usv_connecting()
    coordinator.set_usv_link(True)
    coordinator.mark_drone_connecting()
    coordinator.set_drone_link(True)
    coordinator.set_drone_link(False)

    assert states[:4] == [
        StartupState.CONNECTING_USV.value,
        StartupState.CONNECTING_USV.value,
        StartupState.CONNECTING_DRONE.value,
        StartupState.READY.value,
    ]
    assert states[-1] == StartupState.DEGRADED.value


def test_integration_drone_signal_flows_through_manager_to_usv():
    usv_thread = FakeUSVThread()
    manager = ConnectionManager(usv_connection_thread=usv_thread)
    drone = DroneConnectionThread()

    semantic_events = []
    relay_statuses = []

    manager.semantic_event_received.connect(semantic_events.append)
    manager.relay_status.connect(relay_statuses.append)
    drone.semantic_event_detected.connect(manager.handle_semantic_event)

    drone._process_message(FakeStatusText("OBSTACLE:ROCK:41.037200:29.029700:0.55"))

    assert len(semantic_events) == 1
    assert semantic_events[0]["event_type"] == "OBSTACLE_REPORT"
    assert len(usv_thread.events) == 1
    assert relay_statuses[-1]["status"] == "relayed"
