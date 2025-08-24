import sys

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QTimer
from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout

from uifolder import Ui_IndicatorsPage
# Note: Import USVTelemetryWidget when UI is generated
# from USVTelemetryWidget import USVTelemetryWidget


class IndicatorsPage(QWidget, Ui_IndicatorsPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Indicators' values
        self.maxSpeed = 15  # Reduced for USV (knots)
        self.maxVerticalSpeed = 0  # Not applicable for USV

        # Animation Duration
        self.duration = 200

        # VRX simulation state
        self.simulation_mode = True
        self.vrx_task_active = False
        self.current_task = ""
        
        # Connection to parent for ArduPilot data
        self.connection_thread = None

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

        print("IndicatorsPage: VRX-compatible indicators initialized")

    def setConnectionThread(self, connection_thread):
        """Set reference to the ArduPilot connection thread for VRX data"""
        self.connection_thread = connection_thread
        print("IndicatorsPage: Connection thread reference set")

    def setSimulationMode(self, is_simulation=True):
        """Enable/disable VRX simulation mode"""
        self.simulation_mode = is_simulation
        if hasattr(self, 'usv_telemetry'):
            self.usv_telemetry.setSimulationMode(is_simulation)
        print(f"IndicatorsPage: Simulation mode: {'VRX' if is_simulation else 'LIVE'}")

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
            # Create USV Telemetry Widget
            # Once you have the USVTelemetryWidget class ready, uncomment this line:
            # from USVTelemetryWidget import USVTelemetryWidget
            # self.usv_telemetry = USVTelemetryWidget(self)
            
            # For now, create VRX-specific placeholder
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
            
            # Create VRX-specific content layout
            placeholder_layout = QVBoxLayout(self.usv_telemetry)
            
            from PySide6.QtWidgets import QLabel, QFrame, QProgressBar
            
            # VRX Header
            header_label = QLabel("🚢 VRX USV TELEMETRY")
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
            
            # VRX Mission Status
            self.mission_status_label = QLabel("Task: STATION_KEEPING")
            self.mission_status_label.setStyleSheet("""
                QLabel {
                    color: #0d47a1;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    background-color: #e3f2fd;
                    border-radius: 4px;
                    margin-bottom: 8px;
                }
            """)
            placeholder_layout.addWidget(self.mission_status_label)
            
            # VRX sample data with realistic coordinates
            vrx_data = [
                "GPS Position:",
                "  Lat: 21.31924° (VRX Area)",
                "  Lon: -157.88916° (Sandisland)",
                "",
                "Navigation:",
                "  Speed:   2.5 kts (SIM)",
                "  Heading: 045° (NE)",
                "  Depth:   5.2 m",
                "",
                "Attitude:",
                "  Roll:  +0.05° (STABLE)",
                "  Pitch: -0.02° (STABLE)", 
                "",
                "Systems:",
                "  Battery: ████████-- 95% (SIM)",
                "  Rudder:  --███----- 5° R",
                "",
                "VRX Status: ✓ SIMULATION READY"
            ]
            
            for data_line in vrx_data:
                data_label = QLabel(data_line)
                if data_line.startswith("  ") or data_line.startswith("GPS") or data_line.startswith("Navigation"):
                    # Indent and style data lines
                    data_label.setStyleSheet("""
                        QLabel {
                            color: #1976d2;
                            font-family: 'Consolas', monospace;
                            font-size: 12px;
                            padding: 2px 0px;
                            border: none;
                            background: transparent;
                        }
                    """)
                elif "VRX Status" in data_line:
                    # Special styling for VRX status
                    data_label.setStyleSheet("""
                        QLabel {
                            color: #4caf50;
                            font-family: 'Consolas', monospace;
                            font-size: 12px;
                            font-weight: bold;
                            padding: 4px;
                            border: none;
                            background: transparent;
                        }
                    """)
                else:
                    # Section headers
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
            
            # Add to the telemetry container
            if hasattr(self, 'telemetryContainer') and hasattr(self.telemetryContainer, 'layout'):
                # Clear any existing widgets in the container
                container_layout = self.telemetryContainer.layout()
                if container_layout is None:
                    container_layout = QVBoxLayout(self.telemetryContainer)
                
                container_layout.addWidget(self.usv_telemetry)
            else:
                print("Warning: telemetryContainer not found in UI")
            
            print("IndicatorsPage: VRX USV Telemetry Widget created")
            
        except Exception as e:
            print(f"Error setting up VRX USV telemetry: {e}")

    def updateVRXTaskStatus(self, task_name, progress=None, status="ACTIVE"):
        """Update the current VRX task status"""
        try:
            self.current_task = task_name
            self.vrx_task_active = (status == "ACTIVE")
            
            if hasattr(self, 'mission_status_label'):
                if progress is not None:
                    status_text = f"Task: {task_name.upper()} ({progress}%)"
                else:
                    status_text = f"Task: {task_name.upper()}"
                    
                self.mission_status_label.setText(status_text)
                
                # Color based on status
                if status == "COMPLETED":
                    bg_color = "#e8f5e8"
                    text_color = "#2e7d32"
                elif status == "ACTIVE":
                    bg_color = "#e3f2fd"
                    text_color = "#0d47a1"
                elif status == "FAILED":
                    bg_color = "#ffebee"
                    text_color = "#d32f2f"
                else:
                    bg_color = "#f5f5f5"
                    text_color = "#757575"
                    
                self.mission_status_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-weight: bold;
                        font-size: 14px;
                        padding: 8px;
                        background-color: {bg_color};
                        border-radius: 4px;
                        margin-bottom: 8px;
                    }}
                """)
                
            print(f"VRX Task Status: {task_name} ({status})")
        except Exception as e:
            print(f"Error updating VRX task status: {e}")

    def rotate_needle(self, angle, needle):
        """Rotate instrument needle with animation"""
        # Calculate the shortest path for the rotation
        current_angle = needle.getAngle() if hasattr(needle, 'getAngle') else 0
        if abs(angle - current_angle) > 180:
            # Adjust angles for minimal rotation distance
            if angle < current_angle:
                angle += 360
            else:
                current_angle += 360

        # Set up the animation
        try:
            rotation_animation = QPropertyAnimation(needle, b"angle", parent=self)
            rotation_animation.setStartValue(current_angle)
            rotation_animation.setEndValue(angle)
            rotation_animation.setDuration(self.duration)
            rotation_animation.start()
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
                # Add VRX simulation context
                if self.simulation_mode:
                    self.speed_text.setText(f"{speed:.1f} (SIM)")
                else:
                    self.speed_text.setText(f"{speed:.1f}")
                
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
                
            # Update heading display with VRX context
            if hasattr(self, 'heading_text'):
                if self.simulation_mode:
                    self.heading_text.setText(f"{degree:.0f}° (VRX)")
                else:
                    self.heading_text.setText(f"{degree:.0f}°")
                    
            print(f"Heading updated: {degree:.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")

    def updateVRXTelemetry(self, vrx_data):
        """Update the USV telemetry widget with VRX simulation data"""
        try:
            if hasattr(self, 'usv_telemetry'):
                # If using full USVTelemetryWidget
                if hasattr(self.usv_telemetry, 'updateFromVRXData'):
                    self.usv_telemetry.updateFromVRXData(vrx_data)
                    
                # Also update main instruments
                if 'vfr_hud' in vrx_data:
                    hud = vrx_data['vfr_hud']
                    speed_ms = hud.get('groundspeed', 0)
                    speed_knots = speed_ms * 1.943844  # Convert to knots
                    heading = hud.get('heading', 0)
                    
                    self.setSpeed(speed_knots)
                    self.setHeading(heading)
                    
            print("VRX telemetry updated")
        except Exception as e:
            print(f"Error updating VRX telemetry: {e}")

    def updateFromArduPilotData(self, mavlink_data):
        """Update indicators from ArduPilot/VRX MAVLink data"""
        try:
            # Process different MAVLink message types
            for msg_type, msg_data in mavlink_data.items():
                if msg_type == 'VFR_HUD':
                    # Update main instruments
                    speed_ms = msg_data.get('groundspeed', 0)
                    speed_knots = speed_ms * 1.943844
                    heading = msg_data.get('heading', 0)
                    
                    self.setSpeed(speed_knots)
                    self.setHeading(heading)
                    
                elif msg_type == 'GLOBAL_POSITION_INT':
                    # Update telemetry widget position
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateGPS'):
                        lat = msg_data.get('lat', 0) / 1e7
                        lon = msg_data.get('lon', 0) / 1e7
                        self.usv_telemetry.updateGPS(lat, lon)
                        
                elif msg_type == 'ATTITUDE':
                    # Update attitude information
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateAttitude'):
                        roll = msg_data.get('roll', 0) * 57.2958  # Convert rad to deg
                        pitch = msg_data.get('pitch', 0) * 57.2958
                        yaw = msg_data.get('yaw', 0) * 57.2958
                        self.usv_telemetry.updateAttitude(roll, pitch, yaw)
                        
                elif msg_type == 'MISSION_CURRENT':
                    # Update waypoint progress
                    if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateWaypointProgress'):
                        current_wp = msg_data.get('seq', 0)
                        # Get total waypoints from mission count if available
                        total_wp = getattr(self, '_total_waypoints', 0)
                        self.usv_telemetry.updateWaypointProgress(current_wp, total_wp)
                        
                elif msg_type == 'MISSION_COUNT':
                    # Store total waypoints
                    self._total_waypoints = msg_data.get('count', 0)
                    
            print(f"Updated from ArduPilot data: {list(mavlink_data.keys())}")
        except Exception as e:
            print(f"Error updating from ArduPilot data: {e}")

    # **VRX-SPECIFIC UPDATE METHODS**
    
    def updateVRXEnvironment(self, weather="CALM", sea_state=1, wind_speed=5):
        """Update VRX environment conditions display"""
        try:
            # Update telemetry widget if it has environment methods
            if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'setVRXEnvironmentInfo'):
                self.usv_telemetry.setVRXEnvironmentInfo(weather, sea_state, wind_speed)
                
            print(f"VRX Environment: {weather}, Sea State {sea_state}, Wind {wind_speed} kts")
        except Exception as e:
            print(f"Error updating VRX environment: {e}")

    def updateVRXPerception(self, objects_detected, avg_confidence=None, object_types=None):
        """Update VRX perception system status"""
        try:
            # Update telemetry widget if it has perception methods
            if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateVRXPerceptionInfo'):
                self.usv_telemetry.updateVRXPerceptionInfo(objects_detected, avg_confidence)
                
            # Could also update a dedicated perception display
            print(f"VRX Perception: {objects_detected} objects detected")
            if avg_confidence:
                print(f"  Average confidence: {avg_confidence:.1f}%")
            if object_types:
                print(f"  Object types: {', '.join(object_types)}")
                
        except Exception as e:
            print(f"Error updating VRX perception: {e}")

    # **SIMPLIFIED UPDATE METHODS - USV FOCUSED**
    
    def setAttitude(self, pitch, roll):
        """Update attitude - send to USV telemetry instead of attitude indicator"""
        if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateAttitude'):
            self.usv_telemetry.updateAttitude(roll, pitch)

    def setVerticalSpeed(self, speed):
        """Not applicable for USV - ignore or log"""
        print(f"Vertical speed received but not applicable for USV: {speed}")
        pass

    def setAltitude(self, altitude):
        """Convert altitude to depth for USV"""
        if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateDepth'):
            # For USV, negative altitude could represent depth below sea level
            depth = max(0, -altitude) if altitude < 0 else 0
            self.usv_telemetry.updateDepth(depth)

    # **CONVENIENCE METHODS FOR VRX INTEGRATION**
    
    def updateSpeedAndHeading(self, speed_ms, heading_deg):
        """Update both main instruments at once with VRX data"""
        # Convert m/s to knots for USV display
        speed_knots = speed_ms * 1.943844
        self.setSpeed(speed_knots)
        self.setHeading(heading_deg)

    def updateNavigationData(self, lat, lon, speed_ms, heading, depth=0):
        """Update all navigation-related data from VRX"""
        # Update main instruments
        self.updateSpeedAndHeading(speed_ms, heading)
        
        # Update comprehensive telemetry widget
        nav_data = {
            'latitude': lat,
            'longitude': lon,
            'speed_ms': speed_ms,
            'heading': heading,
            'depth': depth,
            'roll': 0.0,  # Default values for stable simulation
            'pitch': 0.0,
            'battery': 95,  # High battery for simulation
            'rudder': 0,
            'status': 'VRX_AUTO'
        }
        if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'updateAllTelemetry'):
            self.usv_telemetry.updateAllTelemetry(lat, lon, speed_ms, heading, depth, 0.0, 0.0, 95, 0)

    def updateFromVRXState(self, vrx_state):
        """Update all indicators from complete VRX state"""
        try:
            # Update main instruments
            if 'speed_knots' in vrx_state:
                self.setSpeed(vrx_state['speed_knots'])
            if 'heading' in vrx_state:
                self.setHeading(vrx_state['heading'])
                
            # Update telemetry widget
            if hasattr(self, 'usv_telemetry'):
                if hasattr(self.usv_telemetry, 'updateFromFullVRXState'):
                    self.usv_telemetry.updateFromFullVRXState(vrx_state)
                    
            # Update task status
            if 'current_task' in vrx_state:
                task_progress = vrx_state.get('task_progress', None)
                task_status = vrx_state.get('task_status', 'ACTIVE')
                self.updateVRXTaskStatus(vrx_state['current_task'], task_progress, task_status)
                
            # Update environment
            if 'environment' in vrx_state:
                env = vrx_state['environment']
                self.updateVRXEnvironment(
                    env.get('weather', 'CALM'),
                    env.get('sea_state', 1),
                    env.get('wind_speed', 5)
                )
                
            # Update perception
            if 'perception' in vrx_state:
                perc = vrx_state['perception']
                self.updateVRXPerception(
                    perc.get('objects_detected', 0),
                    perc.get('avg_confidence', None),
                    perc.get('object_types', None)
                )
                
            print("IndicatorsPage: Updated from complete VRX state")
        except Exception as e:
            print(f"Error updating from VRX state: {e}")

    def resetForVRX(self):
        """Reset all indicators to VRX simulation defaults"""
        try:
            # Reset main instruments to VRX starting values
            self.setSpeed(0.0)  # Start stationary
            self.setHeading(45.0)  # Typical starting heading for VRX tasks
            
            # Reset telemetry widget
            if hasattr(self, 'usv_telemetry') and hasattr(self.usv_telemetry, 'resetDisplay'):
                self.usv_telemetry.resetDisplay()
                
            # Set initial VRX task
            self.updateVRXTaskStatus("STATION_KEEPING", 0, "ACTIVE")
            
            # Set VRX environment
            self.updateVRXEnvironment("CALM", 1, 5)
            
            print("IndicatorsPage: Reset for VRX simulation")
        except Exception as e:
            print(f"Error resetting for VRX: {e}")

    def connectToArduPilot(self, connection_thread):
        """Connect to ArduPilot connection thread for live VRX data"""
        try:
            self.connection_thread = connection_thread
            
            # Set up data callbacks if the connection thread supports them
            if hasattr(connection_thread, 'add_telemetry_callback'):
                connection_thread.add_telemetry_callback(self.updateFromArduPilotData)
                
            print("IndicatorsPage: Connected to ArduPilot for VRX data")
        except Exception as e:
            print(f"Error connecting to ArduPilot: {e}")

    def resizeEvent(self, event):
        """Handle resize events"""
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)

    # **DEBUG AND TESTING METHODS**
    
    def simulateVRXTask(self, task_name="WAYFINDING"):
        """Simulate a VRX task for testing"""
        import random
        
        try:
            # Simulate task progression
            for progress in range(0, 101, 10):
                QTimer.singleShot(progress * 50, lambda p=progress: self.updateVRXTaskStatus(task_name, p, "ACTIVE"))
                
                # Simulate changing speed and heading
                if progress < 100:
                    speed = 2.0 + random.uniform(-0.5, 1.0)
                    heading = 45 + random.uniform(-15, 15)
                    QTimer.singleShot(progress * 50, lambda s=speed, h=heading: self.updateSpeedAndHeading(s, h))
                    
            # Mark complete
            QTimer.singleShot(5500, lambda: self.updateVRXTaskStatus(task_name, 100, "COMPLETED"))
            
            print(f"Started VRX task simulation: {task_name}")
        except Exception as e:
            print(f"Error simulating VRX task: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IndicatorsPage()
    window.show()
    
    # Test VRX simulation mode
    window.setSimulationMode(True)
    
    # Test with VRX sample data
    vrx_test_data = {
        'speed_knots': 3.2,
        'heading': 45,
        'current_task': 'WAYFINDING',
        'task_progress': 65,
        'task_status': 'ACTIVE',
        'environment': {
            'weather': 'CALM',
            'sea_state': 1,
            'wind_speed': 5
        },
        'perception': {
            'objects_detected': 3,
            'avg_confidence': 87.5,
            'object_types': ['buoy', 'dock', 'other_vessel']
        }
    }
    
    # Test update
    QTimer.singleShot(1000, lambda: window.updateFromVRXState(vrx_test_data))
    
    # Test task simulation
    QTimer.singleShot(2000, lambda: window.simulateVRXTask("PERCEPTION"))
    
    sys.exit(app.exec())