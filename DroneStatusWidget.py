"""Minimal drone status widget — connection status and position only.

UI source of truth: uifolder/DroneStatusWidget.ui
"""

from PySide6.QtCore import QFile, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy


class DroneStatusWidget(QWidget):
    """Light-theme drone status card showing connection + position.

    Loads its layout from ``uifolder/DroneStatusWidget.ui`` at runtime.
    The public contract is intentionally minimal:
      - ``set_connected(bool)`` — toggle connection indicator
      - ``update_position(lat, lon, alt)`` — display coordinates
      - ``is_connected`` — read-only property
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Load .ui file at runtime (setupUi + multiple inheritance causes segfault)
        loader = QUiLoader()
        ui_file = QFile("uifolder/DroneStatusWidget.ui")
        ui_file.open(QFile.ReadOnly)
        self._ui_widget = loader.load(ui_file, self)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui_widget)

        # Expose .ui labels as direct attributes for compatibility
        for attr in [
            "headerLabel",
            "connectionStatusLabel",
            "positionLabel",
        ]:
            widget = self._ui_widget.findChild(QWidget, attr)
            if widget:
                setattr(self, attr, widget)

        # Ensure widget expands properly
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connection state tracking
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @Slot(bool)
    def set_connected(self, connected: bool) -> None:
        self._is_connected = connected
        if hasattr(self, "connectionStatusLabel"):
            if connected:
                self.connectionStatusLabel.setText("Connected")
                self.connectionStatusLabel.setStyleSheet(
                    "font-weight: bold; font-size: 12px; color: #28a745;"
                )
            else:
                self.connectionStatusLabel.setText("Disconnected")
                self.connectionStatusLabel.setStyleSheet(
                    "font-weight: bold; font-size: 12px; color: #dc3545;"
                )
        if not connected and hasattr(self, "positionLabel"):
            self.positionLabel.setText("--")

    @Slot(float, float, float)
    def update_position(self, lat: float, lon: float, alt: float) -> None:
        if hasattr(self, "positionLabel"):
            self.positionLabel.setText(f"{lat:.6f}, {lon:.6f} | {alt:.1f}m")
