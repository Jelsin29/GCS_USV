"""
DroneStatusWidget — UI panel for drone telemetry and target detection display.

Shows: connection status, battery, GPS position, last detected target.
"""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFrame


class DroneStatusWidget(QFrame):
    """Compact drone status display panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._is_connected = False

    def _setup_ui(self) -> None:
        """Create the widget layout and labels."""
        raise NotImplementedError

    @property
    def is_connected(self) -> bool:
        """Return True if drone is connected."""
        return self._is_connected

    @Slot(bool)
    def set_connected(self, connected: bool) -> None:
        """Update connection status display."""
        raise NotImplementedError

    @Slot(float, float, float)
    def update_position(self, lat: float, lon: float, alt: float) -> None:
        """Update drone GPS position display."""
        raise NotImplementedError

    @Slot(float, float)
    def update_battery(self, voltage: float, percentage: float) -> None:
        """Update drone battery display."""
        raise NotImplementedError

    @Slot(str, float, float)
    def on_target_detected(self, color: str, lat: float, lon: float) -> None:
        """Display target detection alert."""
        raise NotImplementedError
