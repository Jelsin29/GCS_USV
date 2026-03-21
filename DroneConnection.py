"""
DroneConnectionThread — MAVLink connection thread for the drone (IHA).

Lighter than ArdupilotConnectionThread: only receives telemetry and
target detection data. Does not upload missions (drone is RC-controlled).
"""

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection: mavutil.mavlink_connection | None = None
        self._running = False
        self._port: str = ""
        self._baudrate: int = 57600

    def set_connection_params(self, port: str, baudrate: int = 57600) -> None:
        """Set serial port and baud rate before starting thread."""
        self._port = port
        self._baudrate = baudrate

    def run(self) -> None:
        """Main thread loop: connect and receive telemetry."""
        raise NotImplementedError

    def _process_message(self, msg) -> None:
        """Process incoming MAVLink message from drone."""
        raise NotImplementedError

    def _parse_target_detection(self, text: str) -> tuple[str, float, float] | None:
        """Parse target detection from STATUSTEXT message.

        Expected format: 'TARGET:COLOR:LAT:LON'
        Returns (color, lat, lon) or None if not a target message.
        """
        raise NotImplementedError

    def stop(self) -> None:
        """Stop the connection thread gracefully."""
        self._running = False
        self.wait(5000)
