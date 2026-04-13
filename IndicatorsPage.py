import sys

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QLabel

from uifolder import Ui_IndicatorsPage


class IndicatorsPage(QWidget, Ui_IndicatorsPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Indicators' values
        self.maxSpeed = 15  # Reduced for USV (knots)
        self.maxVerticalSpeed = 0  # Not applicable for USV

        # Animation Duration
        self.duration = 200

        # Connection to parent for ArduPilot data
        self.connection_thread = None

        # State flags
        self.simulation_mode = False

        # Hide unnecessary instruments - keep only Speedometer and Direction for USV
        self.hideUnnecessaryInstruments()

        # Add allocate widget button
        self.btn_AllocateWidget = QPushButton(
            icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self
        )
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

        print("IndicatorsPage: Initialized for real ArduPilot telemetry")

    def setConnectionThread(self, connection_thread):
        """Set reference to the ArduPilot connection thread for real data"""
        self.connection_thread = connection_thread
        print("IndicatorsPage: Connection thread reference set")

    def setSimulationMode(self, is_simulation=True):
        """Enable/disable simulation mode - switches between mock and real data"""
        self.simulation_mode = is_simulation
        mode_text = "SIMULATION" if is_simulation else "LIVE DATA"
        print(f"IndicatorsPage: Mode set to {mode_text}")

    def hideUnnecessaryInstruments(self):
        """Hide instruments we don't need for USV - keep only Speedometer and Direction"""
        try:
            # Hide Attitude Indicator (not critical for USV)
            if hasattr(self, "AttitudeIndicator"):
                self.AttitudeIndicator.hide()

            # Hide Vertical Speed (not applicable for USV)
            if hasattr(self, "Vspeedometer"):
                self.Vspeedometer.hide()

            # Hide Altitude (use depth instead in telemetry widget)
            if hasattr(self, "Altitude"):
                self.Altitude.hide()

            # Keep Speedometer and Direction visible - critical for USV navigation
            if hasattr(self, "Speedometer"):
                self.Speedometer.show()
            if hasattr(self, "Direction"):
                self.Direction.show()

            print(
                "IndicatorsPage: Configured for USV operation (Speedometer + Direction)"
            )

        except Exception as e:
            print(f"Error configuring USV instruments: {e}")

    def updateFromArduPilotData(self, mavlink_data):
        """Update instruments from ArduPilot MAVLink data"""
        try:
            for msg_type, msg_data in mavlink_data.items():
                if msg_type == "vfr_hud":
                    speed_ms = msg_data.get("groundspeed", 0)
                    speed_knots = speed_ms * 1.943844
                    heading = msg_data.get("heading", 0)
                    self.setSpeed(speed_knots)
                    self.setHeading(heading)

        except Exception as e:
            print(f"[ERROR] Error updating from ArduPilot data: {e}")

    def rotate_needle(self, angle, needle):
        """Rotate instrument needle with animation"""
        try:
            current_angle = getattr(needle, "_current_angle", 0)
            if abs(angle - current_angle) > 180:
                if angle < current_angle:
                    angle += 360
                else:
                    current_angle += 360

            rotation_animation = QPropertyAnimation(needle, b"rotation", parent=self)
            rotation_animation.setStartValue(current_angle)
            rotation_animation.setEndValue(angle)
            rotation_animation.setDuration(self.duration)
            rotation_animation.start()

            needle._current_angle = angle % 360

        except Exception as e:
            print(f"Error animating needle: {e}")

    def setSpeed(self, speed):
        """Update speedometer - main instrument for USV navigation"""
        try:
            if speed < self.maxSpeed:
                degree = speed * 360 / self.maxSpeed
            else:
                degree = 360

            degree = 280 / 360 * degree + 140

            if hasattr(self, "speed_needle"):
                self.rotate_needle(degree, self.speed_needle)
            if hasattr(self, "speed_text"):
                if self.simulation_mode:
                    self.speed_text.setText(f"{speed:.1f} (SIM)")
                else:
                    self.speed_text.setText(f"{speed:.1f} (LIVE)")

            print(f"Speed updated: {speed:.1f} knots")
        except Exception as e:
            print(f"Error updating speed: {e}")

    def setHeading(self, degree):
        """Update heading/direction - critical for USV navigation"""
        try:
            degree = degree % 360

            if hasattr(self, "direction_needle"):
                self.rotate_needle(degree, self.direction_needle)

            print(f"Heading updated: {degree:.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")

    def setAttitude(self, pitch, roll):
        """Attitude is not displayed on indicators — no-op."""
        pass

    def setVerticalSpeed(self, speed):
        """Not applicable for USV - ignore."""
        if not self.simulation_mode:
            print(f"Vertical speed received but not applicable for USV: {speed}")

    def setAltitude(self, altitude):
        """Not applicable for USV surface vessel — no-op."""
        pass

    def updateSpeedAndHeading(self, speed_ms, heading_deg):
        """Update both main instruments at once with ArduPilot data"""
        speed_knots = speed_ms * 1.943844
        self.setSpeed(speed_knots)
        self.setHeading(heading_deg)

    def updateNavigationData(self, lat, lon, speed_ms, heading, depth=0):
        """Update all navigation-related data from ArduPilot"""
        self.updateSpeedAndHeading(speed_ms, heading)

    def resetForArduPilot(self):
        """Reset all indicators for new ArduPilot connection."""
        try:
            self.setSpeed(0.0)
            self.setHeading(0.0)
        except Exception as e:
            print(f"Error resetting for ArduPilot: {e}")

    def connectToArduPilot(self, connection_thread):
        """Connect to ArduPilot connection thread for live data"""
        try:
            self.connection_thread = connection_thread

            if hasattr(connection_thread, "add_telemetry_callback"):
                connection_thread.add_telemetry_callback(self.updateFromArduPilotData)

            print("IndicatorsPage: Connected to ArduPilot for live data")
        except Exception as e:
            print(f"Error connecting to ArduPilot: {e}")

    def onConnectionLost(self):
        """Handle connection loss."""
        try:
            self.simulation_mode = False
            self.setSpeed(0.0)
            self.setHeading(0.0)
        except Exception as e:
            print(f"Error handling connection loss: {e}")

    def switchToRealDataMode(self):
        """Switch from simulation to real data mode."""
        try:
            self.simulation_mode = False
            print("IndicatorsPage: Switched to real data mode")
        except Exception as e:
            print(f"[ERROR] Error switching to real data mode: {e}")

    def resizeEvent(self, event):
        """Handle resize events"""
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)

    # Debug methods
    def testWithMockArduPilotData(self):
        """Test the indicators with mock ArduPilot data"""
        mock_data = {
            "vfr_hud": {
                "groundspeed": 2.5,
                "heading": 45,
                "throttle": 50,
                "alt": 0.5,
                "climb": 0.0,
            },
            "global_position_int": {"lat": 413717139, "lon": 290295276, "alt": 500},
            "attitude": {"roll": 0.05, "pitch": -0.02, "yaw": 0.785},
            "sys_status": {
                "voltage_battery": 12500,
                "current_battery": 500,
                "battery_remaining": 85,
            },
            "heartbeat": {"custom_mode": 10, "base_mode": 1, "system_status": 4},
        }

        print("[DEBUG] Testing with mock ArduPilot data")
        self.updateFromArduPilotData(mock_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IndicatorsPage()
    window.show()

    QTimer.singleShot(2000, window.testWithMockArduPilotData)
    QTimer.singleShot(3000, lambda: window.switchToRealDataMode())

    sys.exit(app.exec())
