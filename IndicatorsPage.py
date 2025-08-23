import sys

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QTimer
from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout

from uifolder import Ui_IndicatorsPage
# Note: You'll need to add this import after generating the UI file
# from USVTelemetryWidget import USVTelemetryWidget


class IndicatorsPage(QWidget, Ui_IndicatorsPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Indicators' values
        self.maxSpeed = 33
        self.maxVerticalSpeed = 12

        # Animation Duration
        self.duration = 200

        # Hide unnecessary instruments - keep only Speedometer and Direction
        self.hideUnnecessaryInstruments()
        
        # Add USV Telemetry Widget
        self.setupUSVTelemetry()

        # Add allocate widget button
        self.btn_AllocateWidget = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self)
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

    def hideUnnecessaryInstruments(self):
        """Hide instruments we don't need - keep only Speedometer and Direction"""
        try:
            # Hide Attitude Indicator
            if hasattr(self, 'AttitudeIndicator'):
                self.AttitudeIndicator.hide()
            
            # Hide Vertical Speed
            if hasattr(self, 'Vspeedometer'):
                self.Vspeedometer.hide()
                
            # Hide Altitude
            if hasattr(self, 'Altitude'):
                self.Altitude.hide()
                
            # Keep Speedometer and Direction visible
            if hasattr(self, 'Speedometer'):
                self.Speedometer.show()
            if hasattr(self, 'Direction'):
                self.Direction.show()
                
            print("IndicatorsPage: Hidden unnecessary instruments, keeping Speedometer and Direction")
                
        except Exception as e:
            print(f"Error hiding instruments: {e}")

    def setupUSVTelemetry(self):
        """Add the USV Telemetry Widget to the telemetryContainer"""
        try:
            # Create USV Telemetry Widget
            # Once you have the USVTelemetryWidget class ready, uncomment this line:
            # from USVTelemetryWidget import USVTelemetryWidget
            # self.usv_telemetry = USVTelemetryWidget(self)
            
            # For now, create a placeholder that matches the telemetry design
            self.usv_telemetry = QWidget()
            self.usv_telemetry.setMinimumSize(380, 450)
            self.usv_telemetry.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    border: 2px solid #0d47a1;
                    border-radius: 8px;
                    margin: 4px;
                    padding: 12px;
                    font-family: 'Segoe UI', 'Consolas', monospace;
                }
            """)
            
            # Create placeholder content that looks like the telemetry widget
            placeholder_layout = QVBoxLayout(self.usv_telemetry)
            
            from PySide6.QtWidgets import QLabel, QFrame
            
            # Header
            header_label = QLabel("📊 USV TELEMETRY")
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #0d47a1;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 4px;
                    margin-bottom: 8px;
                }
            """)
            placeholder_layout.addWidget(header_label)
            
            # Sample data labels
            sample_data = [
                "Status:      MANUAL",
                "GPS:         41.0370, 29.0295",
                "Speed:       5.2 m/s (10.1 knots)",
                "Heading:     175° (S)",
                "Depth:       15.4 m",
                "",
                "Attitude:",
                "  Roll: 2.1°   Pitch: 1.5°",
                "",
                "Systems:",
                "  Battery: ████████-- 85%",
                "  Rudder:  ---███---- 10° R"
            ]
            
            for data_line in sample_data:
                data_label = QLabel(data_line)
                data_label.setStyleSheet("""
                    QLabel {
                        color: #2c3e50;
                        font-family: 'Consolas', monospace;
                        font-size: 12px;
                        padding: 2px;
                        border: none;
                        background: transparent;
                    }
                """)
                placeholder_layout.addWidget(data_label)
            
            # Add to the telemetry container
            if hasattr(self, 'telemetryContainer') and hasattr(self.telemetryContainer, 'layout'):
                # Clear any existing widgets in the container
                container_layout = self.telemetryContainer.layout()
                if container_layout is None:
                    container_layout = QVBoxLayout(self.telemetryContainer)
                
                container_layout.addWidget(self.usv_telemetry)
            else:
                print("Warning: telemetryContainer not found in UI")
            
            print("IndicatorsPage: USV Telemetry Widget added to telemetryContainer")
            
        except Exception as e:
            print(f"Error setting up USV telemetry: {e}")

    def rotate_needle(self, angle, needle):
        # Calculate the shortest path for the rotation
        current_angle = needle.getAngle()
        if abs(angle - current_angle) > 180:
            # Adjust angles for minimal rotation distance
            if angle < current_angle:
                angle += 360
            else:
                current_angle += 360

        # Set up the animation
        rotation_animation = QPropertyAnimation(needle, b"angle", parent=self)
        rotation_animation.setStartValue(current_angle)
        rotation_animation.setEndValue(angle)
        rotation_animation.setDuration(self.duration)
        rotation_animation.start()

    def setSpeed(self, speed):
        """Update speedometer - main instrument for USV"""
        try:
            if speed < self.maxSpeed:
                degree = speed * 360 / self.maxSpeed
            else:
                degree = 360

            degree = 280 / 360 * degree + 140
            
            if hasattr(self, 'speed_needle'):
                self.rotate_needle(degree, self.speed_needle)
            if hasattr(self, 'speed_text'):
                self.speed_text.setText("%.1f" % speed)
                
            print(f"Speed updated: {speed:.1f}")
        except Exception as e:
            print(f"Error updating speed: {e}")

    def setHeading(self, degree):
        """Update heading/direction - important for USV navigation"""
        try:
            if hasattr(self, 'direction_needle'):
                self.rotate_needle(degree, self.direction_needle)
            print(f"Heading updated: {degree:.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")

    def updateUSVTelemetry(self, telemetry_data):
        """Update the USV telemetry widget with comprehensive data"""
        try:
            if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateAllTelemetry'):
                # Extract data from telemetry_data dict
                lat = telemetry_data.get('latitude', 0.0)
                lon = telemetry_data.get('longitude', 0.0)
                speed_ms = telemetry_data.get('speed_ms', 0.0)
                heading = telemetry_data.get('heading', 0.0)
                depth = telemetry_data.get('depth', 0.0)
                roll = telemetry_data.get('roll', 0.0)
                pitch = telemetry_data.get('pitch', 0.0)
                battery = telemetry_data.get('battery', 0)
                rudder = telemetry_data.get('rudder', 0)
                status = telemetry_data.get('status', 'MANUAL')
                
                # Update the comprehensive telemetry display
                self.usv_telemetry.updateAllTelemetry(lat, lon, speed_ms, heading, depth, roll, pitch, battery, rudder)
                self.usv_telemetry.updateStatus(status)
                
            print("USV telemetry updated")
        except Exception as e:
            print(f"Error updating USV telemetry: {e}")

    # **SIMPLIFIED UPDATE METHODS - Only for Speed and Heading**
    
    def setAttitude(self, pitch, roll):
        """Simplified - send to USV telemetry instead of attitude indicator"""
        if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateAttitude'):
            self.usv_telemetry.updateAttitude(roll, pitch)

    def setVerticalSpeed(self, speed):
        """Simplified - convert to regular speed or ignore"""
        # Since we don't have vertical speed for USV, we could ignore this
        # or use it for speed calculation
        pass

    def setAltitude(self, altitude):
        """Simplified - convert to depth for USV"""
        if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateDepth'):
            # For USV, altitude becomes water depth (inverted)
            depth = max(0, -altitude) if altitude < 0 else 0
            self.usv_telemetry.updateDepth(depth)

    # **CONVENIENCE METHODS FOR USV DATA**
    
    def updateSpeedAndHeading(self, speed_ms, heading_deg):
        """Update both main instruments at once"""
        # Convert m/s to appropriate scale for speedometer
        speed_display = speed_ms * 1.943844  # Convert to knots for display
        self.setSpeed(speed_display)
        self.setHeading(heading_deg)

    def updateNavigationData(self, lat, lon, speed_ms, heading, depth=0):
        """Update all navigation-related data"""
        # Update main instruments
        self.updateSpeedAndHeading(speed_ms, heading)
        
        # Update telemetry widget
        nav_data = {
            'latitude': lat,
            'longitude': lon,
            'speed_ms': speed_ms,
            'heading': heading,
            'depth': depth,
            'roll': 0.0,  # Default values
            'pitch': 0.0,
            'battery': 85,
            'rudder': 0,
            'status': 'AUTO'
        }
        self.updateUSVTelemetry(nav_data)

    def resizeEvent(self, event):
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IndicatorsPage()
    window.show()
    
    # Test with sample data
    test_data = {
        'latitude': 41.0370,
        'longitude': 29.0295,
        'speed_ms': 5.2,
        'heading': 175,
        'depth': 15.4,
        'roll': 2.1,
        'pitch': 1.5,
        'battery': 85,
        'rudder': 10,
        'status': 'AUTO'
    }
    window.updateUSVTelemetry(test_data)
    window.updateSpeedAndHeading(5.2, 175)
    
    sys.exit(app.exec())