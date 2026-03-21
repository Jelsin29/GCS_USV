"""
ConnectionManager — Orchestrates dual MAVLink connections (USV + Drone).

Manages simultaneous GCS↔USV (RFD900x) and GCS↔Drone (SiK) connections,
each running in its own QThread. Provides unified API for MainWindow.
"""

from PySide6.QtCore import QObject, Signal

from Vehicle.ArdupilotConnection import ArdupilotConnectionThread
from DroneConnection import DroneConnectionThread


class ConnectionManager(QObject):
    """Manages dual MAVLink connections for USV and Drone."""

    # USV signals
    usv_connected = Signal()
    usv_disconnected = Signal()
    usv_telemetry_updated = Signal(dict)

    # Drone signals
    drone_connected = Signal()
    drone_disconnected = Signal()
    drone_telemetry_updated = Signal(dict)
    drone_target_detected = Signal(str, float, float)  # color, lat, lon

    def __init__(self, parent=None):
        super().__init__(parent)
        self._usv_thread: ArdupilotConnectionThread | None = None
        self._drone_thread: DroneConnectionThread | None = None

    # --- USV Connection ---

    def connect_usv(self, port: str, baudrate: int = 115200) -> None:
        """Establish MAVLink connection to USV via serial port."""
        raise NotImplementedError

    def disconnect_usv(self) -> None:
        """Disconnect from USV."""
        raise NotImplementedError

    @property
    def usv_connected_status(self) -> bool:
        """Return True if USV is connected."""
        raise NotImplementedError

    # --- Drone Connection ---

    def connect_drone(self, port: str, baudrate: int = 57600) -> None:
        """Establish MAVLink connection to Drone via serial port."""
        raise NotImplementedError

    def disconnect_drone(self) -> None:
        """Disconnect from Drone."""
        raise NotImplementedError

    @property
    def drone_connected_status(self) -> bool:
        """Return True if Drone is connected."""
        raise NotImplementedError

    # --- Target Relay ---

    def relay_target_to_usv(self, color: str, lat: float, lon: float) -> None:
        """Forward drone target detection data to USV via MAVLink."""
        raise NotImplementedError

    # --- Lifecycle ---

    def shutdown(self) -> None:
        """Gracefully stop all connections."""
        raise NotImplementedError
