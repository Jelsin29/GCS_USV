"""
DroneStatusWidget — UI panel for drone telemetry and target detection display.

Shows: connection status, battery, GPS position, last detected target.
"""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout


class DroneStatusWidget(QFrame):
    """Compact drone status display panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_connected = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the widget layout and labels."""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            "DroneStatusWidget { background: #1e1e2e; border-radius: 8px; padding: 8px; }"
            "QLabel { color: #cdd6f4; font-size: 12px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Title
        title = QLabel("DRONE (IHA)")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #89b4fa;")
        layout.addWidget(title)

        # Connection status
        self._status_label = QLabel("Disconnected")
        self._status_label.setStyleSheet("color: #f38ba8;")
        layout.addWidget(self._status_label)

        # Battery
        battery_row = QHBoxLayout()
        battery_row.addWidget(QLabel("Battery:"))
        self._battery_label = QLabel("--")
        battery_row.addWidget(self._battery_label)
        layout.addLayout(battery_row)

        # Position
        pos_row = QHBoxLayout()
        pos_row.addWidget(QLabel("Position:"))
        self._position_label = QLabel("--")
        pos_row.addWidget(self._position_label)
        layout.addLayout(pos_row)

        # Target detection
        self._target_label = QLabel("")
        self._target_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self._target_label.setWordWrap(True)
        layout.addWidget(self._target_label)

    @property
    def is_connected(self) -> bool:
        """Return True if drone is connected."""
        return self._is_connected

    @Slot(bool)
    def set_connected(self, connected: bool) -> None:
        """Update connection status display."""
        self._is_connected = connected
        if connected:
            self._status_label.setText("Connected")
            self._status_label.setStyleSheet("color: #a6e3a1;")
        else:
            self._status_label.setText("Disconnected")
            self._status_label.setStyleSheet("color: #f38ba8;")
            self._battery_label.setText("--")
            self._position_label.setText("--")

    @Slot(float, float, float)
    def update_position(self, lat: float, lon: float, alt: float) -> None:
        """Update drone GPS position display."""
        self._position_label.setText(f"{lat:.6f}, {lon:.6f} | {alt:.1f}m")

    @Slot(float, float)
    def update_battery(self, voltage: float, percentage: float) -> None:
        """Update drone battery display."""
        self._battery_label.setText(f"{percentage:.0f}% ({voltage:.1f}V)")

    @Slot(str, float, float)
    def on_target_detected(self, color: str, lat: float, lon: float) -> None:
        """Display target detection alert."""
        color_styles = {
            "RED": "color: #f38ba8; background: #302030;",
            "GREEN": "color: #a6e3a1; background: #203020;",
            "BLUE": "color: #89b4fa; background: #202040;",
        }
        style = color_styles.get(color.upper(), "color: #f9e2af;")
        self._target_label.setStyleSheet(
            f"font-weight: bold; font-size: 13px; padding: 4px; border-radius: 4px; {style}"
        )
        self._target_label.setText(f"TARGET: {color} @ ({lat:.6f}, {lon:.6f})")
