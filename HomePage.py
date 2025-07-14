import os
import sys
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QInputDialog

from MapWidget import MapWidget
from uifolder import Ui_HomePage
from CameraWidget import CameraWidget

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

        # **NEW: Setup Vehicle Status Dashboard**
        self.setupVehicleStatus()

        # Show in another window buttons
        self.mapwidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.mapFrame, self.mapwidget))
        self.cameraWidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.cameraFrame, self.cameraWidget))

        # **NEW: Start telemetry update timer**
        self.telemetryTimer = QTimer()
        self.telemetryTimer.timeout.connect(self.updateTelemetry)
        self.telemetryTimer.start(1000)  # Update every second

    def setupVehicleStatus(self):
        """Setup the vehicle status dashboard with ship image and battery icon"""
        try:
            # **SHIP IMAGE: Load and set the ship image**
            ship_image_path = "uifolder/assets/icons/ship.png"  # You'll need to save your ship image here
            if os.path.exists(ship_image_path):
                ship_pixmap = QPixmap(ship_image_path)
                # Scale image to fit while maintaining aspect ratio
                scaled_pixmap = ship_pixmap.scaled(200, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.shipImageLabel.setPixmap(scaled_pixmap)
            else:
                # Use placeholder if image not found
                self.shipImageLabel.setText("🚢")
                self.shipImageLabel.setStyleSheet("""
                    QLabel { 
                        color: #6c5ce7; 
                        font-size: 48px;
                        border: none;
                        background: transparent;
                    }
                """)

            # **BATTERY ICON: Load and set the battery image**
            battery_image_path = "uifolder/assets/icons/battery.png"  # You'll need to save your battery image here
            if os.path.exists(battery_image_path):
                battery_pixmap = QPixmap(battery_image_path)
                scaled_battery = battery_pixmap.scaled(40, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.batteryIconLabel.setPixmap(scaled_battery)
            else:
                # Use emoji placeholder if image not found
                self.batteryIconLabel.setText("🔋")
                self.batteryIconLabel.setStyleSheet("""
                    QLabel { 
                        color: #00ff88;
                        font-size: 20px;
                        border: none;
                        background: transparent;
                    }
                """)

            print("Vehicle status dashboard setup completed")
            
        except Exception as e:
            print(f"Error setting up vehicle status: {e}")

    def updateTelemetry(self):
        """Update telemetry data from vehicle connection"""
        try:
            if self.parent and hasattr(self.parent, 'connectionThread') and self.parent.connectionThread:
                # Get data from connection thread if available
                # This is a placeholder - you'll need to implement actual data retrieval
                
                # **BATTERY PERCENTAGE**
                battery_percent = self.getBatteryPercentage()
                self.updateBatteryDisplay(battery_percent)
                
                # **RANGE CALCULATION**
                estimated_range = self.calculateRange()
                self.rangeValueLabel.setText(f"{estimated_range} km")
                
                # **CONSUMPTION**
                consumption = self.getConsumption()
                self.consumptionValueLabel.setText(f"{consumption} Wh/km")
                
                # **SPEED**
                speed = self.getSpeed()
                self.speedValueLabel.setText(f"{speed} km/h")
                
                # **CONNECTION STATUS**
                connection_status = self.getConnectionStatus()
                self.updateConnectionStatus(connection_status)
                
        except Exception as e:
            print(f"Error updating telemetry: {e}")

    def getBatteryPercentage(self):
        """Get battery percentage from vehicle"""
        # Placeholder - implement actual battery reading
        if self.parent and hasattr(self.parent, 'connectionThread'):
            # Return actual battery data when available
            return 50  # Placeholder
        return 50

    def updateBatteryDisplay(self, percentage):
        """Update battery display with color coding"""
        self.batteryPercentLabel.setText(f"{percentage}%")
        
        # Color coding based on battery level
        if percentage > 60:
            color = "#00ff88"  # Green
        elif percentage > 30:
            color = "#ffa500"  # Orange
        else:
            color = "#ff4757"  # Red
            
        self.batteryPercentLabel.setStyleSheet(f"""
            QLabel {{ 
                color: {color}; 
                font-size: 24px; 
                font-weight: bold;
                border: none;
            }}
        """)

    def calculateRange(self):
        """Calculate estimated range based on current battery and consumption"""
        # Placeholder calculation
        battery_percent = self.getBatteryPercentage()
        consumption = self.getConsumption()
        
        if consumption > 0:
            # Assuming 100kWh battery capacity (adjust as needed)
            remaining_energy = (battery_percent / 100) * 100  # kWh
            estimated_range = int((remaining_energy * 1000) / consumption)  # km
            return min(max(estimated_range, 0), 999)  # Clamp between 0-999
        return 164  # Default value

    def getConsumption(self):
        """Get average consumption"""
        # Placeholder - implement actual consumption calculation
        return 304

    def getSpeed(self):
        """Get current/average speed"""
        # Placeholder - implement actual speed reading
        if self.parent and hasattr(self.parent, 'connectionThread'):
            # Return actual speed data when available
            return 43  # Placeholder
        return 43

    def getConnectionStatus(self):
        """Get vehicle connection status"""
        if self.parent and hasattr(self.parent, 'connectionThread'):
            # Check if connection thread is active and connected
            if hasattr(self.parent.connectionThread, 'connection') and self.parent.connectionThread.connection:
                return True
        return False

    def updateConnectionStatus(self, is_connected):
        """Update connection status indicator"""
        if is_connected:
            self.connectionStatusLabel.setText("● CONNECTED")
            self.connectionStatusLabel.setStyleSheet("""
                QLabel { 
                    color: #00ff88; 
                    font-size: 12px; 
                    font-weight: bold;
                    border: none;
                    text-align: center;
                }
            """)
        else:
            self.connectionStatusLabel.setText("● DISCONNECTED")
            self.connectionStatusLabel.setStyleSheet("""
                QLabel { 
                    color: #ff4757; 
                    font-size: 12px; 
                    font-weight: bold;
                    border: none;
                    text-align: center;
                }
            """)

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