"""
DroneConnectionThread — MAVLink connection thread for the drone (IHA).

Lighter than ArdupilotConnectionThread: only receives telemetry and
target detection data. Does not upload missions (drone is RC-controlled).

Communication: SiK Telemetry Radio (57600 baud default)
"""

import time

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
            detection = self._parse_target_detection(text)
            if detection is not None:
                color, lat, lon = detection
                print(f"[DRONE] Target detected: {color} at ({lat}, {lon})")
                self.target_detected.emit(color, lat, lon)

    def _parse_target_detection(self, text: str) -> tuple[str, float, float] | None:
        """Parse target detection from STATUSTEXT message.

        Expected format: 'TARGET:COLOR:LAT:LON'
        Example: 'TARGET:RED:41.037083:29.029528'
        Returns (color, lat, lon) or None if not a target message.
        """
        if not text.startswith("TARGET:"):
            return None
        parts = text.split(":")
        if len(parts) != 4:
            return None
        try:
            color = parts[1].upper()
            lat = float(parts[2])
            lon = float(parts[3])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (color, lat, lon)
        except (ValueError, IndexError):
            pass
        return None

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
