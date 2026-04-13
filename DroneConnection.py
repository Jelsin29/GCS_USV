"""
DroneConnectionThread — MAVLink connection thread for the drone (IHA).

Lighter than ArdupilotConnectionThread: only receives telemetry and
semantic sensing data. Does not upload missions (drone is RC-controlled).

Communication: SiK Telemetry Radio (57600 baud default)
"""

import time
from uuid import uuid4

from pymavlink import mavutil

from PySide6.QtCore import QThread, Signal


class DroneConnectionThread(QThread):
    """QThread for receiving drone telemetry via MAVLink."""

    # Telemetry signals
    position_updated = Signal(float, float, float)  # lat, lon, alt
    battery_updated = Signal(float, float)  # voltage, percentage
    heartbeat_received = Signal(dict)  # mode, armed, system_status

    # Target detection signals
    target_detected = Signal(str, float, float)  # color, lat, lon
    semantic_target_detected = Signal(dict)
    semantic_event_detected = Signal(dict)

    # Connection signals
    connected = Signal()
    disconnected = Signal()
    connection_error = Signal(str)

    HEARTBEAT_TIMEOUT_S = 5
    RECONNECT_DELAY_S = 5
    RECONNECT_MAX_DELAY_S = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection = None
        self._running = False
        self._port: str = ""
        self._baudrate: int = 57600
        self._is_connected = False
        self._last_heartbeat_time: float = 0

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def set_connection_params(self, port: str, baudrate: int = 57600) -> None:
        """Set serial port and baud rate before starting thread."""
        self._port = port
        self._baudrate = baudrate

    def run(self) -> None:
        """Main thread loop: connect and receive telemetry."""
        self._running = True
        reconnect_delay = self.RECONNECT_DELAY_S

        while self._running:
            try:
                self._connect()
                reconnect_delay = self.RECONNECT_DELAY_S  # Reset on success
                self._recv_loop()
            except Exception as e:
                print(f"[DRONE] Connection error: {e}")
                self.connection_error.emit(str(e))
            finally:
                self._cleanup()

            if not self._running:
                break

            # Wait before reconnecting
            print(f"[DRONE] Reconnecting in {reconnect_delay}s...")
            for _ in range(reconnect_delay * 10):
                if not self._running:
                    return
                self.msleep(100)
            reconnect_delay = min(reconnect_delay * 2, self.RECONNECT_MAX_DELAY_S)

    def _connect(self) -> None:
        """Establish MAVLink connection to drone."""
        print(f"[DRONE] Connecting to {self._port} at {self._baudrate} baud...")
        self.connection = mavutil.mavlink_connection(
            self._port,
            baud=self._baudrate,
            timeout=5,
        )
        heartbeat = self.connection.wait_heartbeat(timeout=10)
        if heartbeat is None:
            raise ConnectionError("No heartbeat received from drone")

        print(
            f"[DRONE] Connected — system {self.connection.target_system}, "
            f"component {self.connection.target_component}"
        )
        self._is_connected = True
        self._last_heartbeat_time = time.time()
        self.connected.emit()

    def _recv_loop(self) -> None:
        """Receive and process messages until stopped or connection lost."""
        while self._running and self.connection:
            msg = self.connection.recv_match(
                type=[
                    "HEARTBEAT",
                    "GLOBAL_POSITION_INT",
                    "SYS_STATUS",
                    "BATTERY_STATUS",
                    "STATUSTEXT",
                ],
                blocking=True,
                timeout=1.0,
            )
            if msg is not None:
                self._process_message(msg)
            else:
                # Check heartbeat timeout
                if time.time() - self._last_heartbeat_time > self.HEARTBEAT_TIMEOUT_S:
                    print("[DRONE] Heartbeat timeout — connection lost")
                    return

    def _process_message(self, msg) -> None:
        """Process incoming MAVLink message from drone."""
        msg_type = msg.get_type()

        if msg_type == "HEARTBEAT":
            self._last_heartbeat_time = time.time()
            self.heartbeat_received.emit(
                {
                    "custom_mode": msg.custom_mode,
                    "base_mode": msg.base_mode,
                    "system_status": msg.system_status,
                    "armed": bool(msg.base_mode & 128),
                }
            )

        elif msg_type == "GLOBAL_POSITION_INT":
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.relative_alt / 1000.0
            self.position_updated.emit(lat, lon, alt)

        elif msg_type == "SYS_STATUS":
            voltage = msg.voltage_battery / 1000.0 if msg.voltage_battery != -1 else 0.0
            remaining = (
                float(msg.battery_remaining) if msg.battery_remaining != -1 else 0.0
            )
            self.battery_updated.emit(voltage, remaining)

        elif msg_type == "BATTERY_STATUS":
            if hasattr(msg, "voltages") and msg.voltages[0] != 65535:
                voltage = msg.voltages[0] / 1000.0
                remaining = (
                    float(msg.battery_remaining) if msg.battery_remaining != -1 else 0.0
                )
                self.battery_updated.emit(voltage, remaining)

        elif msg_type == "STATUSTEXT":
            text = msg.text.strip()
            event = self._parse_semantic_event(text)
            if event is not None:
                print(
                    f"[DRONE] Semantic event: {event['event_type']} "
                    f"at ({event['lat']}, {event['lon']})"
                )
                self.semantic_event_detected.emit(event)

                if event["event_type"] == "MISSION_TARGET":
                    color = event["color"]
                    lat = event["lat"]
                    lon = event["lon"]
                    self.semantic_target_detected.emit(event)
                    self.target_detected.emit(color, lat, lon)

    def _parse_target_detection(self, text: str) -> tuple[str, float, float] | None:
        """Parse target detection from STATUSTEXT message.

        Expected format: 'TARGET:COLOR:LAT:LON'
        Example: 'TARGET:RED:41.037083:29.029528'
        Returns (color, lat, lon) or None if not a target message.
        """
        event = self._parse_semantic_event(text)
        if event is None or event["event_type"] != "MISSION_TARGET":
            return None
        return (event["color"], event["lat"], event["lon"])

    def _parse_semantic_event(self, text: str) -> dict | None:
        """Parse normalized semantic events from drone STATUSTEXT.

        Supported formats:
        - TARGET:COLOR:LAT:LON
        - MISSION_TARGET:COLOR:LAT:LON[:CONFIDENCE]
        - OBSTACLE:TYPE:LAT:LON[:CONFIDENCE]
        - OBSTACLE_REPORT:TYPE:LAT:LON[:CONFIDENCE]
        """
        if not text:
            return None

        parts = [part.strip() for part in text.split(":")]
        if len(parts) < 4:
            return None

        prefix = parts[0].upper()
        if prefix in {"TARGET", "MISSION_TARGET"}:
            return self._build_target_event(parts, text)
        if prefix in {"OBSTACLE", "OBSTACLE_REPORT"}:
            return self._build_obstacle_event(parts, text)
        return None

    def _build_target_event(self, parts: list[str], raw_text: str) -> dict | None:
        try:
            color = self._normalize_target_color(parts[1])
            lat = float(parts[2])
            lon = float(parts[3])
            confidence = self._parse_confidence(parts[4] if len(parts) > 4 else None)
        except (ValueError, IndexError):
            return None

        if not self._valid_coordinates(lat, lon):
            return None

        return {
            "id": f"mission-target-{uuid4().hex[:8]}",
            "event_type": "MISSION_TARGET",
            "color": color,
            "lat": lat,
            "lon": lon,
            "source": "drone",
            "confidence": confidence,
            "timestamp": time.time(),
            "raw_text": raw_text,
            "raw_color": parts[1].upper(),
        }

    def _build_obstacle_event(self, parts: list[str], raw_text: str) -> dict | None:
        try:
            obstacle_type = parts[1].upper()
            lat = float(parts[2])
            lon = float(parts[3])
            confidence = self._parse_confidence(parts[4] if len(parts) > 4 else None)
        except (ValueError, IndexError):
            return None

        if not self._valid_coordinates(lat, lon):
            return None

        return {
            "id": f"obstacle-{uuid4().hex[:8]}",
            "event_type": "OBSTACLE_REPORT",
            "obstacle_type": obstacle_type,
            "lat": lat,
            "lon": lon,
            "source": "drone",
            "confidence": confidence,
            "timestamp": time.time(),
            "raw_text": raw_text,
        }

    def _normalize_target_color(self, color: str) -> str:
        normalized = color.strip().upper()
        aliases = {
            "BLUE": "BLACK",
            "SIYAH": "BLACK",
            "BLACK": "BLACK",
            "RED": "RED",
            "GREEN": "GREEN",
        }
        return aliases.get(normalized, normalized)

    def _parse_confidence(self, value: str | None) -> float:
        if value is None or value == "":
            return 1.0
        confidence = float(value)
        return max(0.0, min(confidence, 1.0))

    def _valid_coordinates(self, lat: float, lon: float) -> bool:
        return -90 <= lat <= 90 and -180 <= lon <= 180

    def _cleanup(self) -> None:
        """Close connection and reset state."""
        was_connected = self._is_connected
        self._is_connected = False
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
        if was_connected:
            self.disconnected.emit()

    def stop(self) -> None:
        """Stop the connection thread gracefully."""
        self._running = False
        self.wait(5000)
