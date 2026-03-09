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
        
        # Add USV Telemetry Widget
        self.setupUSVTelemetry()

        # Add allocate widget button
        self.btn_AllocateWidget = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self)
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
        if hasattr(self, 'usv_telemetry'):
            self.usv_telemetry.setSimulationMode(is_simulation)
        
        mode_text = "SIMULATION" if is_simulation else "LIVE DATA"
        print(f"IndicatorsPage: Mode set to {mode_text}")

    def hideUnnecessaryInstruments(self):
        """Hide instruments we don't need for USV - keep only Speedometer and Direction"""
        try:
            # Hide Attitude Indicator (not critical for USV)
            if hasattr(self, 'AttitudeIndicator'):
                self.AttitudeIndicator.hide()
            
            # Hide Vertical Speed (not applicable for USV)
            if hasattr(self, 'Vspeedometer'):
                self.Vspeedometer.hide()
                
            # Hide Altitude (use depth instead in telemetry widget)
            if hasattr(self, 'Altitude'):
                self.Altitude.hide()
                
            # Keep Speedometer and Direction visible - critical for USV navigation
            if hasattr(self, 'Speedometer'):
                self.Speedometer.show()
            if hasattr(self, 'Direction'):
                self.Direction.show()
                
            print("IndicatorsPage: Configured for USV operation (Speedometer + Direction + Telemetry)")
                
        except Exception as e:
            print(f"Error configuring USV instruments: {e}")

    def setupUSVTelemetry(self):
        """Add the comprehensive USV Telemetry Widget"""
        try:
            # Try to import and create real USV Telemetry Widget
            try:
                from USVTelemetryWidget import USVTelemetryWidget
                self.usv_telemetry = USVTelemetryWidget(self)
                
                # Set initial mode to simulation (will switch when connected)
                self.usv_telemetry.setSimulationMode(True)
                print("IndicatorsPage: Real USV Telemetry Widget created")
                
            except ImportError:
                print("USVTelemetryWidget not found, creating placeholder")
                self.setupPlaceholderTelemetry()
                return
            
            # Add to the telemetry container
            if hasattr(self, 'telemetryContainer') and hasattr(self.telemetryContainer, 'layout'):
                container_layout = self.telemetryContainer.layout()
                if container_layout is None:
                    container_layout = QVBoxLayout(self.telemetryContainer)
                
                container_layout.addWidget(self.usv_telemetry)
                print("IndicatorsPage: Real USV Telemetry Widget integrated")
            else:
                print("Warning: telemetryContainer not found in UI, creating manual layout")
                self.createManualTelemetryLayout()
                
        except Exception as e:
            print(f"Error setting up USV telemetry: {e}")
            self.setupPlaceholderTelemetry()

    def setupPlaceholderTelemetry(self):
        """Create placeholder telemetry when USVTelemetryWidget is not available"""
        try:
            self.usv_telemetry = QWidget()
            self.usv_telemetry.setMinimumSize(380, 500)
            self.usv_telemetry.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    border: 2px solid #0d47a1;
                    border-radius: 12px;
                    margin: 4px;
                    padding: 16px;
                    font-family: 'Segoe UI', 'Consolas', monospace;
                }
            """)
            
            # Create placeholder content layout
            placeholder_layout = QVBoxLayout(self.usv_telemetry)
            
            # Header
            header_label = QLabel("🚢 USV TELEMETRY")
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #0d47a1;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 12px;
                    border-radius: 6px;
                    margin-bottom: 12px;
                }
            """)
            placeholder_layout.addWidget(header_label)
            
            # Status
            self.mission_status_label = QLabel("Status: WAITING FOR CONNECTION")
            self.mission_status_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    background-color: #f8d7da;
                    border-radius: 4px;
                    margin-bottom: 8px;
                }
            """)
            placeholder_layout.addWidget(self.mission_status_label)
            
            # Add placeholder telemetry data
            telemetry_data = [
                "GPS Position:",
                "  Lat: 0.000000° (NO DATA)",
                "  Lon: 0.000000° (NO DATA)",
                "",
                "Navigation:",
                "  Speed: 0.0 kts (NO DATA)", 
                "  Heading: 000° (NO DATA)",
                "  Depth: 0.0 m (NO DATA)",
                "",
                "Attitude:",
                "  Roll: +0.00° (NO DATA)",
                "  Pitch: +0.00° (NO DATA)",
                "",
                "Systems:",
                "  Battery: ------ 0% (NO DATA)",
                "  Rudder: ------ 0° (NO DATA)",
                "",
                "Status: WAITING FOR ARDUPILOT CONNECTION"
            ]
            
            for data_line in telemetry_data:
                data_label = QLabel(data_line)
                if "NO DATA" in data_line or "WAITING" in data_line:
                    data_label.setStyleSheet("""
                        QLabel {
                            color: #dc3545;
                            font-family: 'Consolas', monospace;
                            font-size: 12px;
                            padding: 2px 0px;
                            border: none;
                            background: transparent;
                        }
                    """)
                elif data_line.startswith("  "):
                    data_label.setStyleSheet("""
                        QLabel {
                            color: #6c757d;
                            font-family: 'Consolas', monospace;
                            font-size: 12px;
                            padding: 2px 0px;
                            border: none;
                            background: transparent;
                        }
                    """)
                else:
                    data_label.setStyleSheet("""
                        QLabel {
                            color: #2c3e50;
                            font-weight: bold;
                            font-size: 12px;
                            padding: 4px 0px;
                            border: none;
                            background: transparent;
                        }
                    """)
                placeholder_layout.addWidget(data_label)
            
            # Add to container
            if hasattr(self, 'telemetryContainer'):
                container_layout = self.telemetryContainer.layout()
                if container_layout is None:
                    container_layout = QVBoxLayout(self.telemetryContainer)
                container_layout.addWidget(self.usv_telemetry)
            
            print("IndicatorsPage: Placeholder telemetry widget created")
            
        except Exception as e:
            print(f"Error creating placeholder telemetry: {e}")

    def createManualTelemetryLayout(self):
        """Create telemetry layout manually if container not found"""
        try:
            # This is a fallback method if the UI doesn't have the expected container
            print("IndicatorsPage: Creating manual telemetry layout")
            # You might need to adjust this based on your actual UI structure
            
        except Exception as e:
            print(f"Error creating manual telemetry layout: {e}")

    def switchToRealDataMode(self):
        """Switch from simulation to real data mode."""
        try:
            self.simulation_mode = False

            if hasattr(self, 'usv_telemetry'):
                if hasattr(self.usv_telemetry, 'setConnectionStatus'):
                    self.usv_telemetry.setConnectionStatus(True, 'ARDUPILOT')
                if hasattr(self.usv_telemetry, 'setSimulationMode'):
                    self.usv_telemetry.setSimulationMode(False)

            if hasattr(self, 'mission_status_label'):
                self.mission_status_label.setText('Status: LIVE DATA CONNECTED')
                self.mission_status_label.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 8px;
                        background-color: #28a745;
                        border-radius: 4px;
                        margin-bottom: 8px;
                    }
                """)

        except Exception as e:
            print(f'[ERROR] Error switching to real data mode: {e}')

    def updateFromArduPilotData(self, mavlink_data):
        """Update indicators from ArduPilot MAVLink data"""
        try:
            print(f"[INDICATORS] Received ArduPilot data: {list(mavlink_data.keys())}")
            
            # Process different MAVLink message types
            for msg_type, msg_data in mavlink_data.items():
                if msg_type == 'vfr_hud':
                    # Update main instruments
                    speed_ms = msg_data.get('groundspeed', 0)
                    speed_knots = speed_ms * 1.943844
                    heading = msg_data.get('heading', 0)
                    
                    print(f"[INDICATORS] Updating speed: {speed_knots:.1f} kts, heading: {heading:.0f}°")
                    self.setSpeed(speed_knots)
                    self.setHeading(heading)
                    
                elif msg_type == 'global_position_int':
                    # Update telemetry widget position
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateGPS'):
                        lat = msg_data.get('lat', 0) / 1e7
                        lon = msg_data.get('lon', 0) / 1e7
                        print(f"[INDICATORS] Updating GPS: {lat:.6f}, {lon:.6f}")
                        self.usv_telemetry.updateGPS(lat, lon)
                        
                elif msg_type == 'attitude':
                    # Update attitude information
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateAttitude'):
                        roll = msg_data.get('roll', 0) * 57.2958  # Convert rad to deg
                        pitch = msg_data.get('pitch', 0) * 57.2958
                        yaw = msg_data.get('yaw', 0) * 57.2958
                        print(f"[INDICATORS] Updating attitude: Roll={roll:.1f}°, Pitch={pitch:.1f}°")
                        self.usv_telemetry.updateAttitude(roll, pitch, yaw)
                        
                elif msg_type == 'sys_status' or msg_type == 'battery_status':
                    # Update battery information
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateBatteryLevel'):
                        battery_pct = msg_data.get('battery_remaining', 0)
                        voltage = msg_data.get('voltage_battery', 0)
                        if voltage > 1000:  # Convert from millivolts if needed
                            voltage = voltage / 1000.0
                        print(f"[INDICATORS] Updating battery: {battery_pct}%, {voltage:.1f}V")
                        self.usv_telemetry.updateBatteryLevel(battery_pct)
                        
                elif msg_type == 'servo_output_raw':
                    # Update servo data for rudder angle, etc.
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateRudderAngle'):
                        servo4_raw = msg_data.get('servo4_raw', 1500)  # Typical rudder channel
                        rudder_angle = (servo4_raw - 1500) * 30 / 500  # Convert PWM to angle
                        print(f"[INDICATORS] Updating rudder: {rudder_angle:.1f}°")
                        self.usv_telemetry.updateRudderAngle(rudder_angle)
                        
                elif msg_type == 'rangefinder':
                    # Update water depth data
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateDepth'):
                        distance = msg_data.get('distance', 0)
                        print(f"[INDICATORS] Updating depth: {distance:.1f}m")
                        self.usv_telemetry.updateDepth(distance)
                        
                elif msg_type == 'heartbeat':
                    # Update status/mode information
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateStatus'):
                        custom_mode = msg_data.get('custom_mode', 0)
                        
                        # ArduRover mode mapping
                        mode_names = {
                            0: 'MANUAL', 1: 'ACRO', 2: 'STEERING', 3: 'HOLD', 4: 'LOITER',
                            5: 'FOLLOW', 6: 'SIMPLE', 10: 'AUTO', 11: 'RTL', 12: 'SMARTRTL',
                            15: 'GUIDED'
                        }
                        mode_name = mode_names.get(custom_mode, f'MODE_{custom_mode}')
                        
                        # Add LIVE prefix to distinguish from simulation
                        status = f"LIVE_{mode_name}"
                        print(f"[INDICATORS] Updating status: {status}")
                        self.usv_telemetry.updateStatus(status)
                        
            print(f"[INDICATORS] Successfully processed {len(mavlink_data)} message types")
            
        except Exception as e:
            print(f"[ERROR] Error updating from ArduPilot data: {e}")
            import traceback
            traceback.print_exc()

    def rotate_needle(self, angle, needle):
        """Rotate instrument needle with animation"""
        try:
            # Calculate the shortest path for the rotation
            current_angle = getattr(needle, '_current_angle', 0)
            if abs(angle - current_angle) > 180:
                # Adjust angles for minimal rotation distance
                if angle < current_angle:
                    angle += 360
                else:
                    current_angle += 360

            # Set up the animation
            rotation_animation = QPropertyAnimation(needle, b"rotation", parent=self)
            rotation_animation.setStartValue(current_angle)
            rotation_animation.setEndValue(angle)
            rotation_animation.setDuration(self.duration)
            rotation_animation.start()
            
            # Store current angle
            needle._current_angle = angle % 360
            
        except Exception as e:
            print(f"Error animating needle: {e}")

    def setSpeed(self, speed):
        """Update speedometer - main instrument for USV navigation"""
        try:
            # Clamp speed to realistic USV range
            if speed < self.maxSpeed:
                degree = speed * 360 / self.maxSpeed
            else:
                degree = 360

            degree = 280 / 360 * degree + 140
            
            if hasattr(self, 'speed_needle'):
                self.rotate_needle(degree, self.speed_needle)
            if hasattr(self, 'speed_text'):
                # Show real vs simulation data
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
            # Normalize heading
            degree = degree % 360
            
            if hasattr(self, 'direction_needle'):
                self.rotate_needle(degree, self.direction_needle)
                
            # Update heading display context
            if hasattr(self, 'heading_text'):
                if self.simulation_mode:
                    self.heading_text.setText(f"{degree:.0f}° (SIM)")
                else:
                    self.heading_text.setText(f"{degree:.0f}° (LIVE)")
                    
            print(f"Heading updated: {degree:.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")

    # USV-focused methods - simplified from aircraft
    def setAttitude(self, pitch, roll):
        """Update attitude - send to USV telemetry instead of attitude indicator"""
        if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateAttitude'):
            self.usv_telemetry.updateAttitude(roll, pitch)

    def setVerticalSpeed(self, speed):
        """Not applicable for USV - ignore or log"""
        if not self.simulation_mode:  # Only log for real data
            print(f"Vertical speed received but not applicable for USV: {speed}")

    def setAltitude(self, altitude):
        """Convert altitude to depth for USV"""
        if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateDepth'):
            # For USV, negative altitude could represent depth below sea level
            depth = max(0, -altitude) if altitude < 0 else 0
            self.usv_telemetry.updateDepth(depth)

    # Convenience methods
    def updateSpeedAndHeading(self, speed_ms, heading_deg):
        """Update both main instruments at once with ArduPilot data"""
        # Convert m/s to knots for USV display
        speed_knots = speed_ms * 1.943844
        self.setSpeed(speed_knots)
        self.setHeading(heading_deg)

    def updateNavigationData(self, lat, lon, speed_ms, heading, depth=0):
        """Update all navigation-related data from ArduPilot"""
        # Update main instruments
        self.updateSpeedAndHeading(speed_ms, heading)
        
        # Update comprehensive telemetry widget
        if hasattr(self, 'usv_telemetry'):
            if hasattr(self.usv_telemetry, 'updateAllTelemetry'):
                self.usv_telemetry.updateAllTelemetry(lat, lon, speed_ms, heading, depth, 0.0, 0.0, 85, 0)
            elif hasattr(self.usv_telemetry, 'updateGPS'):
                self.usv_telemetry.updateGPS(lat, lon)

    def resetForArduPilot(self):
        """Reset all indicators for new ArduPilot connection."""
        try:
            self.setSpeed(0.0)
            self.setHeading(0.0)

            if hasattr(self, 'usv_telemetry'):
                if hasattr(self.usv_telemetry, 'setConnectionStatus'):
                    self.usv_telemetry.setConnectionStatus(False)
                if hasattr(self.usv_telemetry, 'resetDisplay'):
                    self.usv_telemetry.resetDisplay()

            if hasattr(self, 'mission_status_label'):
                self.mission_status_label.setText('Status: READY FOR CONNECTION')
                self.mission_status_label.setStyleSheet("""
                    QLabel {
                        color: #495057;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 8px;
                        background-color: #e9ecef;
                        border-radius: 4px;
                        margin-bottom: 8px;
                    }
                """)

        except Exception as e:
            print(f'Error resetting for ArduPilot: {e}')
    
    def connectToArduPilot(self, connection_thread):
        """Connect to ArduPilot connection thread for live data"""
        try:
            self.connection_thread = connection_thread
            
            # Set up data callbacks if the connection thread supports them
            if hasattr(connection_thread, 'add_telemetry_callback'):
                connection_thread.add_telemetry_callback(self.updateFromArduPilotData)
                
            print("IndicatorsPage: Connected to ArduPilot for live data")
        except Exception as e:
            print(f"Error connecting to ArduPilot: {e}")

    def onConnectionLost(self):
        """Handle connection loss."""
        try:
            self.simulation_mode = False

            if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'setConnectionStatus'):
                self.usv_telemetry.setConnectionStatus(False)

            self.setSpeed(0.0)
            self.setHeading(0.0)

            if hasattr(self, 'mission_status_label'):
                self.mission_status_label.setText('Status: DISCONNECTED')
                self.mission_status_label.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 8px;
                        background-color: #dc3545;
                        border-radius: 4px;
                        margin-bottom: 8px;
                    }
                """)

        except Exception as e:
            print(f'Error handling connection loss: {e}')

    def resizeEvent(self, event):
        """Handle resize events"""
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)

    # Debug methods
    def testWithMockArduPilotData(self):
        """Test the indicators with mock ArduPilot data"""
        mock_data = {
            'vfr_hud': {
                'groundspeed': 2.5,  # m/s
                'heading': 45,       # degrees
                'throttle': 50,      # percent
                'alt': 0.5,         # altitude
                'climb': 0.0        # climb rate
            },
            'global_position_int': {
                'lat': 413717139,   # lat * 1e7
                'lon': 290295276,   # lon * 1e7
                'alt': 500          # altitude in mm
            },
            'attitude': {
                'roll': 0.05,       # radians
                'pitch': -0.02,     # radians
                'yaw': 0.785        # radians (45 degrees)
            },
            'sys_status': {
                'voltage_battery': 12500,  # millivolts
                'current_battery': 500,    # centiamps
                'battery_remaining': 85    # percent
            },
            'heartbeat': {
                'custom_mode': 10,  # AUTO mode
                'base_mode': 1,
                'system_status': 4
            }
        }
        
        print("[DEBUG] Testing with mock ArduPilot data")
        self.updateFromArduPilotData(mock_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IndicatorsPage()
    window.show()
    
    # Test with mock ArduPilot data
    QTimer.singleShot(2000, window.testWithMockArduPilotData)
    
    # Simulate connection after 3 seconds
    QTimer.singleShot(3000, lambda: window.switchToRealDataMode())
    
    sys.exit(app.exec())