import os
import sys
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QInputDialog, QGraphicsDropShadowEffect

from MapWidget import MapWidget
from uifolder import Ui_HomePage
from CameraWidget import CameraWidget
from TelemetryWidget import TelemetryWidget  # **NEW: Import TelemetryWidget**

class HomePage(QWidget, Ui_HomePage):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        
        # Set Map Widget
        uskudar = [41.037083, 29.029528]
        self.mapwidget = MapWidget(uskudar)
        self.mapFrame.layout().addWidget(self.mapwidget)

        # Set Camera Widget
        self.cameraWidget = CameraWidget(self)
        self.cameraFrame.layout().addWidget(self.cameraWidget)

        # **NEW: Add TelemetryWidget to the reserved space**
        self.telemetryWidget = TelemetryWidget(self)
        self.futureContentFrame.layout().removeWidget(self.futureContentLabel)  # Remove placeholder
        
        # **UPDATED: Remove all margins and spacing for efficient space usage**
        self.futureContentFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.futureContentFrame.layout().setSpacing(0)
        
        self.futureContentFrame.layout().addWidget(self.telemetryWidget)
        
        # **UPDATED: Remove dashed border and ensure clean container**
        self.futureContentFrame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)

        # Show in another window buttons
        self.mapwidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.mapFrame, self.mapwidget))
        self.cameraWidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.cameraFrame, self.cameraWidget))

        # **NEW: Add shadow effects after all widgets are set up**
        QTimer.singleShot(100, self.addShadowEffects)

    def AllocateWidget(self, parent, child):
        if child.isAttached:
            parent.layout().removeWidget(child)
            self.new_window = QMainWindow()
            self.new_window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
            child.btn_AllocateWidget.setIcon(QIcon("uifolder/assets/icons/16x16/cil-arrow-bottom.png"))
            self.new_window.setCentralWidget(child)
            self.new_window.show()
            child.isAttached = False
        else:
            parent.layout().addWidget(child)
            self.new_window.setCentralWidget(None)
            self.new_window.close()
            child.btn_AllocateWidget.setIcon(QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"))
            child.isAttached = True

    def addShadowEffects(self):
        """Add shadow effects to main components"""
        try:
            # Camera frame shadow
            if hasattr(self, 'cameraFrame'):
                camera_shadow = QGraphicsDropShadowEffect()
                camera_shadow.setBlurRadius(15)
                camera_shadow.setXOffset(0)
                camera_shadow.setYOffset(4)
                camera_shadow.setColor(QColor(0, 0, 0, 35))
                self.cameraFrame.setGraphicsEffect(camera_shadow)

            # Map frame shadow
            if hasattr(self, 'mapFrame'):
                map_shadow = QGraphicsDropShadowEffect()
                map_shadow.setBlurRadius(15)
                map_shadow.setXOffset(0)
                map_shadow.setYOffset(4)
                map_shadow.setColor(QColor(0, 0, 0, 35))
                self.mapFrame.setGraphicsEffect(map_shadow)

            # Telemetry frame shadow
            if hasattr(self, 'futureContentFrame'):
                telemetry_shadow = QGraphicsDropShadowEffect()
                telemetry_shadow.setBlurRadius(15)
                telemetry_shadow.setXOffset(0)
                telemetry_shadow.setYOffset(4)
                telemetry_shadow.setColor(QColor(0, 0, 0, 35))
                self.futureContentFrame.setGraphicsEffect(telemetry_shadow)

            print("HomePage: Shadow effects applied successfully")
            
        except Exception as e:
            print(f"HomePage: Error applying shadow effects: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())