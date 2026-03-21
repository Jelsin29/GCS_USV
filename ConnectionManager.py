"""
ConnectionManager — Orchestrates dual MAVLink connections (USV + Drone).

IMPORTANT: The USV connection (ArdupilotConnectionThread) is NOT managed
by this class — it is owned by MainWindow and wired directly to the UI.
This class adds drone connection management alongside the existing USV flow
without modifying it.

ConnectionManager responsibilities:
1. Own and manage the DroneConnectionThread lifecycle
2. Forward drone signals (position, battery, target detection) to the UI
3. Relay target detection data from drone to USV when requested
"""

from PySide6.QtCore import QObject, Signal

from DroneConnection import DroneConnectionThread


class ConnectionManager(QObject):
    """Manages the drone connection alongside the existing USV connection."""

    # Drone signals (forwarded from DroneConnectionThread)
    drone_connected = Signal()
    drone_disconnected = Signal()
    drone_position_updated = Signal(float, float, float)  # lat, lon, alt
    drone_battery_updated = Signal(float, float)  # voltage, percentage
    drone_target_detected = Signal(str, float, float)  # color, lat, lon
    drone_error = Signal(str)

    def __init__(self, usv_connection_thread=None, parent=None):
        """Initialize with optional reference to existing USV connection thread.

        The usv_connection_thread is NOT owned by this class — it's just
        a reference so we can relay target data to the USV.
        """
        super().__init__(parent)
        self._usv_thread = usv_connection_thread
        self._drone_thread: DroneConnectionThread | None = None

    def set_usv_thread(self, usv_thread) -> None:
        """Set reference to the USV connection thread (for target relay)."""
        self._usv_thread = usv_thread

    # --- Drone Connection ---

    def connect_drone(self, port: str, baudrate: int = 57600) -> None:
        """Start drone connection on the given serial port."""
        if self._drone_thread is not None and self._drone_thread.isRunning():
            print("[CONN_MGR] Drone already connected, disconnecting first...")
            self.disconnect_drone()

        self._drone_thread = DroneConnectionThread(self)
        self._drone_thread.set_connection_params(port, baudrate)

        # Wire drone signals to our forwarding signals
        self._drone_thread.connected.connect(self.drone_connected)
        self._drone_thread.disconnected.connect(self.drone_disconnected)
        self._drone_thread.position_updated.connect(self.drone_position_updated)
        self._drone_thread.battery_updated.connect(self.drone_battery_updated)
        self._drone_thread.target_detected.connect(self._on_target_detected)
        self._drone_thread.connection_error.connect(self.drone_error)

        self._drone_thread.start()
        print(f"[CONN_MGR] Drone connection started on {port}")

    def disconnect_drone(self) -> None:
        """Stop the drone connection."""
        if self._drone_thread is not None:
            self._drone_thread.stop()
            self._drone_thread = None
            print("[CONN_MGR] Drone disconnected")

    @property
    def drone_connected_status(self) -> bool:
        """Return True if drone is currently connected."""
        return self._drone_thread is not None and self._drone_thread.is_connected

    # --- Target Relay ---

    def _on_target_detected(self, color: str, lat: float, lon: float) -> None:
        """Handle target detection from drone and forward to UI."""
        print(f"[CONN_MGR] Target detected: {color} at ({lat}, {lon})")
        self.drone_target_detected.emit(color, lat, lon)

    def relay_target_to_usv(self, color: str, lat: float, lon: float) -> None:
        """Forward target data to USV via MAVLink STATUSTEXT.

        The USV's onboard Jetson Orin can parse this to adjust
        its engagement target for Parkour-3.
        """
        if self._usv_thread is None or self._usv_thread.connection is None:
            print("[CONN_MGR] Cannot relay target — USV not connected")
            return

        try:
            msg = f"TARGET:{color}:{lat:.6f}:{lon:.6f}"
            self._usv_thread.connection.mav.statustext_send(
                severity=6,  # MAV_SEVERITY_INFO
                text=msg.encode("utf-8"),
            )
            print(f"[CONN_MGR] Relayed target to USV: {msg}")
        except Exception as e:
            print(f"[CONN_MGR] Failed to relay target: {e}")

    # --- Lifecycle ---

    def shutdown(self) -> None:
        """Gracefully stop the drone connection.

        Note: USV connection shutdown is handled by MainWindow.closeEvent().
        """
        self.disconnect_drone()
