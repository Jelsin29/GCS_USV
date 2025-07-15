import os
import sys
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QInputDialog

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
        istanbulhavalimani = [41.27442, 28.727317]
        self.mapwidget = MapWidget(istanbulhavalimani)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())