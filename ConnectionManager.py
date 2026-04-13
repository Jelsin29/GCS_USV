"""
ConnectionManager — Orchestrates dual MAVLink connections (USV + Drone).

IMPORTANT: The USV connection (ArdupilotConnectionThread) remains owned by
MainWindow and stays authoritative for mission/control flow. This module adds
coordination, drone semantic intake, and semantic relay policy around that
existing path.
"""

import math
import time
from enum import Enum

from PySide6.QtCore import QObject, Signal

from DroneConnection import DroneConnectionThread


class StartupState(str, Enum):
    IDLE = "idle"
    CONNECTING_USV = "connecting-usv"
    CONNECTING_DRONE = "connecting-drone"
    READY = "ready"
    DEGRADED = "degraded"


class StartupCoordinator(QObject):
    state_changed = Signal(str)
    protocol_state_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = StartupState.IDLE
        self._usv_connected = False
        self._drone_connected = False
        self._usv_protocol_state = "idle"
        self._drone_protocol_state = "idle"

    @property
    def state(self) -> StartupState:
        return self._state

    def mark_usv_connecting(self) -> None:
        self._usv_protocol_state = "connecting"
        self._set_state(StartupState.CONNECTING_USV)

    def mark_drone_connecting(self) -> None:
        self._drone_protocol_state = "connecting"
        self._set_state(StartupState.CONNECTING_DRONE)

    def coordinated_stop(self) -> None:
        self._usv_connected = False
        self._drone_connected = False
        self._usv_protocol_state = "stopped"
        self._drone_protocol_state = "stopped"
        self._set_state(StartupState.IDLE)

    def set_usv_link(self, connected: bool) -> None:
        self._usv_connected = connected
        self._usv_protocol_state = "ready" if connected else "waiting-link"
        self._refresh_state()

    def set_drone_link(self, connected: bool) -> None:
        self._drone_connected = connected
        self._drone_protocol_state = "ready" if connected else "waiting-link"
        self._refresh_state()

    def snapshot(self) -> dict:
        return {
            "startup_state": self._state.value,
            "DRONE_PROTOCOL_STATE": self._drone_protocol_state,
            "USV_PROTOCOL_STATE": self._usv_protocol_state,
            "drone_connected": self._drone_connected,
            "usv_connected": self._usv_connected,
        }

    def _refresh_state(self) -> None:
        if self._usv_connected and self._drone_connected:
            self._set_state(StartupState.READY)
        elif self._usv_connected or self._drone_connected:
            if self._state == StartupState.CONNECTING_USV and self._usv_connected:
                self._set_state(StartupState.CONNECTING_USV)
            elif self._state == StartupState.CONNECTING_DRONE and self._drone_connected:
                self._set_state(StartupState.CONNECTING_DRONE)
            else:
                self._set_state(StartupState.DEGRADED)
        else:
            self._set_state(StartupState.IDLE)

    def _set_state(self, state: StartupState) -> None:
        self._state = state
        snapshot = self.snapshot()
        self.state_changed.emit(state.value)
        self.protocol_state_changed.emit(snapshot)


class ConnectionManager(QObject):
    """Manages drone connectivity and semantic relay alongside the USV thread."""

    # Drone signals (forwarded from DroneConnectionThread)
    drone_connected = Signal()
    drone_disconnected = Signal()
    drone_position_updated = Signal(float, float, float)  # lat, lon, alt
    drone_battery_updated = Signal(float, float)  # voltage, percentage
    drone_target_detected = Signal(str, float, float)  # color, lat, lon
    drone_error = Signal(str)

    # Coordinator / relay signals
    startup_state_changed = Signal(str)
    protocol_state_changed = Signal(dict)
    relay_decision = Signal(dict)
    semantic_target_ready = Signal(dict)
    semantic_event_received = Signal(dict)
    relay_status = Signal(dict)

    RELAY_DUPLICATE_WINDOW_S = 10.0
    RELAY_DUPLICATE_DISTANCE_M = 3.0

    def __init__(self, usv_connection_thread=None, parent=None):
        super().__init__(parent)
        self._usv_thread = usv_connection_thread
        self._drone_thread: DroneConnectionThread | None = None
        self._coordinator = StartupCoordinator(self)
        self._recent_semantic_events: list[dict] = []

        self._coordinator.state_changed.connect(self.startup_state_changed)
        self._coordinator.protocol_state_changed.connect(self.protocol_state_changed)

        self._bind_usv_thread_signals()

    def set_usv_thread(self, usv_thread) -> None:
        self._usv_thread = usv_thread
        self._bind_usv_thread_signals()

    def _bind_usv_thread_signals(self) -> None:
        if self._usv_thread is None:
            return
        connection_status = getattr(self._usv_thread, "connection_status", None)
        if connection_status is not None:
            try:
                connection_status.disconnect(self._on_usv_connection_status)
            except (RuntimeError, TypeError):
                pass
            connection_status.connect(self._on_usv_connection_status)

    # --- Startup coordination ---

    def connect_all(
        self,
        usv_port: str,
        usv_baud: int,
        drone_port: str,
        drone_baud: int = 57600,
    ) -> None:
        """Coordinate USV-first, then drone connection setup."""
        if self._usv_thread is not None:
            self._coordinator.mark_usv_connecting()
            if hasattr(self._usv_thread, "setBaudRate"):
                self._usv_thread.setBaudRate(usv_baud)
            if hasattr(self._usv_thread, "setConnectionString"):
                self._usv_thread.setConnectionString(usv_port)
            if not getattr(self._usv_thread, "connection", None):
                self._usv_thread.start()

        self._coordinator.mark_drone_connecting()
        self.connect_drone(drone_port, drone_baud)

    def _on_usv_connection_status(self, connected: bool, _message: str) -> None:
        self._coordinator.set_usv_link(connected)

    # --- Drone Connection ---

    def connect_drone(self, port: str, baudrate: int = 57600) -> None:
        if self._drone_thread is not None and self._drone_thread.isRunning():
            print("[CONN_MGR] Drone already connected, disconnecting first...")
            self.disconnect_drone()

        self._coordinator.mark_drone_connecting()

        self._drone_thread = DroneConnectionThread(self)
        self._drone_thread.set_connection_params(port, baudrate)

        self._drone_thread.connected.connect(self._on_drone_connected)
        self._drone_thread.disconnected.connect(self._on_drone_disconnected)
        self._drone_thread.position_updated.connect(self.drone_position_updated)
        self._drone_thread.battery_updated.connect(self.drone_battery_updated)
        self._drone_thread.target_detected.connect(self._on_target_detected)
        self._drone_thread.semantic_event_detected.connect(self.handle_semantic_event)
        self._drone_thread.connection_error.connect(self.drone_error)

        self._drone_thread.start()
        print(f"[CONN_MGR] Drone connection started on {port}")

    def disconnect_drone(self) -> None:
        if self._drone_thread is not None:
            thread = self._drone_thread
            thread.stop()
            self._drone_thread = None
            self._coordinator.set_drone_link(False)
            print("[CONN_MGR] Drone disconnected")

    @property
    def drone_connected_status(self) -> bool:
        return self._drone_thread is not None and self._drone_thread.is_connected

    def _on_drone_connected(self) -> None:
        self._coordinator.set_drone_link(True)
        self.drone_connected.emit()

    def _on_drone_disconnected(self) -> None:
        self._coordinator.set_drone_link(False)
        self.drone_disconnected.emit()

    # --- Semantic relay ---

    def _on_target_detected(self, color: str, lat: float, lon: float) -> None:
        print(f"[CONN_MGR] Target detected: {color} at ({lat}, {lon})")
        self.drone_target_detected.emit(color, lat, lon)

    def handle_semantic_target(self, event: dict) -> None:
        semantic_event = dict(event)
        semantic_event["event_type"] = "MISSION_TARGET"
        if "color" in semantic_event:
            semantic_event["color"] = self._normalize_target_color(
                semantic_event["color"]
            )
        self.handle_semantic_event(semantic_event)

    def handle_semantic_event(self, event: dict) -> None:
        normalized_event = self._normalize_semantic_event(event)
        if normalized_event is None:
            self.relay_decision.emit({"reason": "invalid", "event": event})
            return

        if self._is_duplicate(normalized_event):
            decision = {"reason": "duplicate", "event": normalized_event}
            self.relay_decision.emit(decision)
            self.relay_status.emit(
                {
                    "target_id": normalized_event["id"],
                    "status": "suppressed",
                    "error": "duplicate",
                    "event_type": normalized_event["event_type"],
                }
            )
            return

        self._remember_event(normalized_event)
        self.semantic_event_received.emit(normalized_event)

        if normalized_event["event_type"] == "MISSION_TARGET":
            self.semantic_target_ready.emit(normalized_event)

        self.relay_decision.emit({"reason": "relay", "event": normalized_event})
        self.relay_semantic_event_to_usv(normalized_event)

    def relay_semantic_event_to_usv(self, event: dict) -> bool:
        if self._usv_thread is None:
            self._emit_relay_status(event, "failed", "usv-thread-missing")
            return False

        send_method = getattr(self._usv_thread, "send_semantic_event", None)
        if callable(send_method):
            result = bool(send_method(event))
        elif event.get("event_type") == "MISSION_TARGET" and callable(
            getattr(self._usv_thread, "send_semantic_target", None)
        ):
            result = bool(self._usv_thread.send_semantic_target(event))
        else:
            result = self.relay_target_to_usv(
                event.get("color", "UNKNOWN"), event["lat"], event["lon"]
            )

        self._emit_relay_status(
            event,
            "relayed" if result else "failed",
            None if result else "relay-rejected",
        )
        return result

    def relay_target_to_usv(self, color: str, lat: float, lon: float) -> bool:
        event = {
            "id": f"legacy-target-{int(time.time() * 1000)}",
            "event_type": "MISSION_TARGET",
            "color": self._normalize_target_color(color),
            "lat": lat,
            "lon": lon,
            "source": "gcs",
            "confidence": 1.0,
            "timestamp": time.time(),
            "raw_text": "legacy-relay",
        }

        if (
            self._usv_thread is None
            or getattr(self._usv_thread, "connection", None) is None
        ):
            print("[CONN_MGR] Cannot relay target — USV not connected")
            return False

        send_target = getattr(self._usv_thread, "send_semantic_target", None)
        if callable(send_target):
            return bool(send_target(event))

        print("[CONN_MGR] Cannot relay target — USV helper missing")
        return False

    def _normalize_semantic_event(self, event: dict) -> dict | None:
        try:
            lat = float(event["lat"])
            lon = float(event["lon"])
        except (KeyError, TypeError, ValueError):
            return None

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None

        normalized = dict(event)
        normalized["lat"] = lat
        normalized["lon"] = lon
        normalized["timestamp"] = float(normalized.get("timestamp", time.time()))
        normalized["confidence"] = float(normalized.get("confidence", 1.0))
        normalized["source"] = normalized.get("source", "drone")
        normalized["event_type"] = normalized.get(
            "event_type", "MISSION_TARGET"
        ).upper()
        normalized["id"] = normalized.get(
            "id",
            f"{normalized['event_type'].lower()}-{int(normalized['timestamp'] * 1000)}",
        )

        if normalized["event_type"] == "MISSION_TARGET":
            normalized["color"] = self._normalize_target_color(
                normalized.get("color", "UNKNOWN")
            )
        elif normalized["event_type"] == "OBSTACLE_REPORT":
            normalized["obstacle_type"] = normalized.get(
                "obstacle_type", normalized.get("color", "UNKNOWN")
            ).upper()
        else:
            return None

        return normalized

    def _normalize_target_color(self, color: str) -> str:
        aliases = {
            "BLUE": "BLACK",
            "BLACK": "BLACK",
            "SIYAH": "BLACK",
            "RED": "RED",
            "GREEN": "GREEN",
        }
        return aliases.get(str(color).upper(), str(color).upper())

    def _is_duplicate(self, event: dict) -> bool:
        now = event["timestamp"]
        semantic_key = (
            event.get("color") or event.get("obstacle_type") or event["event_type"]
        )
        for previous in self._recent_semantic_events:
            if previous["event_type"] != event["event_type"]:
                continue
            previous_key = (
                previous.get("color")
                or previous.get("obstacle_type")
                or previous["event_type"]
            )
            if previous_key != semantic_key:
                continue
            age = abs(now - previous["timestamp"])
            if age > self.RELAY_DUPLICATE_WINDOW_S:
                continue
            distance = self._distance_meters(
                previous["lat"], previous["lon"], event["lat"], event["lon"]
            )
            if distance <= self.RELAY_DUPLICATE_DISTANCE_M:
                return True
        return False

    def _remember_event(self, event: dict) -> None:
        self._recent_semantic_events.append(event)
        cutoff = event["timestamp"] - self.RELAY_DUPLICATE_WINDOW_S
        self._recent_semantic_events = [
            item for item in self._recent_semantic_events if item["timestamp"] >= cutoff
        ]

    def _distance_meters(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        radius_m = 6_371_000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(d_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        )
        return 2 * radius_m * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _emit_relay_status(self, event: dict, status: str, error: str | None) -> None:
        self.relay_status.emit(
            {
                "target_id": event.get("id", "unknown"),
                "status": status,
                "error": error,
                "event_type": event.get("event_type", "UNKNOWN"),
            }
        )

    # --- Lifecycle ---

    def shutdown(self) -> None:
        self.disconnect_drone()
        self._coordinator.coordinated_stop()
