from PySide6.QtGui import QColor
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect
# Note: You'll need to generate the UI file using: pyside6-uic USVTelemetryWidget.ui -o ui_USVTelemetryWidget.py
# from uifolder.ui_USVTelemetryWidget import Ui_USVTelemetryWidget

class USVTelemetryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # self.setupUi(self)  # Uncomment after generating UI file
        self.parent = parent
        
        # Ensure widget expands properly
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # VRX simulation state tracking
        self.simulation_mode = True  # Assume VRX simulation by default
        self.last_update_time = 0
        
        # Initialize with VRX-appropriate sample data
        QTimer.singleShot(100, self.populateWithVRXData)
        
        print("USVTelemetryWidget: VRX-compatible telemetry dashboard initialized")
    
    def populateWithVRXData(self):
        """Populate with VRX simulation appropriate data"""
        try:
            # VRX simulation typically starts at Sandisland Marina
            self.updateStatus("AUTO" if self.simulation_mode else "MANUAL")
            self.updateGPS(21.31924, -157.88916)  # VRX Sandisland coordinates
            self.updateSpeed(2.5)  # m/s - typical USV speed
            self.updateHeading(45)  # degrees - heading toward first waypoint
            self.updateDepth(5.2)  # meters - shallow water depth
            self.updateRoll(0.1)  # degrees - minimal roll in simulation
            self.updatePitch(-0.2)  # degrees - slight bow down
            self.updateBatteryLevel(95)  # percent - start with full battery
            self.updateRudderAngle(5)  # degrees - slight starboard turn
            
            print("USVTelemetryWidget: VRX simulation data populated")
            
        except Exception as e:
            print(f"USVTelemetryWidget: Error populating VRX data: {e}")
    
    def setSimulationMode(self, is_simulation=True):
        """Set whether we're running in VRX simulation mode"""
        self.simulation_mode = is_simulation
        if is_simulation:
            self.updateStatus("SIM_AUTO")
        print(f"USVTelemetryWidget: Simulation mode: {'ON' if is_simulation else 'OFF'}")
    
    def updateFromVRXData(self, vrx_telemetry):
        """Update telemetry from VRX simulation data structure"""
        try:
            # Expected VRX telemetry structure from ArduPilot connection
            if 'global_position_int' in vrx_telemetry:
                gps_data = vrx_telemetry['global_position_int']
                self.updateGPS(gps_data.get('lat', 0) / 1e7, gps_data.get('lon', 0) / 1e7)
                
            if 'attitude' in vrx_telemetry:
                attitude = vrx_telemetry['attitude']
                self.updateRoll(attitude.get('roll', 0) * 57.2958)  # Convert rad to deg
                self.updatePitch(attitude.get('pitch', 0) * 57.2958)
                self.updateHeading(attitude.get('yaw', 0) * 57.2958)
                
            if 'vfr_hud' in vrx_telemetry:
                hud = vrx_telemetry['vfr_hud']
                self.updateSpeed(hud.get('groundspeed', 0))
                self.updateHeading(hud.get('heading', 0))
                
            if 'battery_status' in vrx_telemetry:
                battery = vrx_telemetry['battery_status']
                self.updateBatteryLevel(battery.get('battery_remaining', 0))
                
            if 'servo_output_raw' in vrx_telemetry:
                servo = vrx_telemetry['servo_output_raw']
                # Assuming rudder is on servo channel 4 (typical for USV)
                rudder_pwm = servo.get('servo4_raw', 1500)
                rudder_angle = (rudder_pwm - 1500) * 30 / 500  # Convert PWM to angle
                self.updateRudderAngle(rudder_angle)
                
            if 'rangefinder' in vrx_telemetry:
                rangefinder = vrx_telemetry['rangefinder']
                self.updateDepth(rangefinder.get('distance', 0))
                
            # Update mode based on flight mode
            if 'heartbeat' in vrx_telemetry:
                mode = vrx_telemetry['heartbeat'].get('custom_mode', 0)
                mode_names = {0: 'MANUAL', 1: 'ACRO', 2: 'STEERING', 3: 'HOLD', 4: 'LOITER', 
                             5: 'FOLLOW', 6: 'SIMPLE', 10: 'AUTO', 11: 'RTL', 12: 'SMARTRTL', 
                             15: 'GUIDED'}
                mode_name = mode_names.get(mode, f'MODE_{mode}')
                if self.simulation_mode:
                    mode_name = f"SIM_{mode_name}"
                self.updateStatus(mode_name)
                
            self.last_update_time = QTimer().remainingTime()
            print("USVTelemetryWidget: Updated from VRX telemetry data")
            
        except Exception as e:
            print(f"USVTelemetryWidget: Error updating from VRX data: {e}")
    
    # **NAVIGATION & POSITIONING UPDATES**
    
    def updateStatus(self, status):
        """Update operational status with VRX simulation awareness"""
        try:
            if hasattr(self, 'statusValueLabel'):
                display_status = status.upper()
                self.statusValueLabel.setText(display_status)
                
                # Color coding for different statuses including simulation modes
                colors = {
                    'MANUAL': '#ff6b35',
                    'AUTO': '#2e7d32', 
                    'AUTONOMOUS': '#2e7d32',
                    'SIM_AUTO': '#4caf50',  # Brighter green for simulation
                    'SIM_MANUAL': '#ff8a65',  # Lighter orange for simulation
                    'STATION_KEEPING': '#1976d2',
                    'LOITER': '#1976d2',
                    'HOLD': '#1976d2',
                    'RTL': '#f57c00',
                    'SMARTRTL': '#f57c00',
                    'GUIDED': '#9c27b0',
                    'EMERGENCY': '#d32f2f'
                }
                
                color = colors.get(display_status, '#ff6b35')
                self.statusValueLabel.setStyleSheet(f"color: {color}; font-weight: bold;")
                
            print(f"Status updated: {status}")
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def updateGPS(self, lat, lon):
        """Update GPS coordinates with VRX location awareness"""
        try:
            if hasattr(self, 'gpsValueLabel'):
                # Check if we're in VRX simulation area (Hawaii)
                if 21.0 <= lat <= 22.0 and -158.0 <= lon <= -157.0:
                    location_note = " (VRX)"
                else:
                    location_note = ""
                    
                self.gpsValueLabel.setText(f"{lat:.6f}, {lon:.6f}{location_note}")
            print(f"GPS updated: {lat:.6f}, {lon:.6f}")
        except Exception as e:
            print(f"Error updating GPS: {e}")
    
    def updateSpeed(self, speed_ms):
        """Update speed in m/s with VRX simulation context"""
        try:
            if hasattr(self, 'speedValueLabel'):
                speed_knots = speed_ms * 1.943844  # Convert m/s to knots
                
                # Add context for simulation vs real-world speeds
                if self.simulation_mode and speed_ms > 10:  # Very high speed for USV
                    speed_note = " (SIM)"
                else:
                    speed_note = ""
                    
                self.speedValueLabel.setText(f"{speed_ms:.1f} m/s ({speed_knots:.1f} kt{speed_note})")
            print(f"Speed updated: {speed_ms:.1f} m/s")
        except Exception as e:
            print(f"Error updating speed: {e}")
    
    def updateHeading(self, heading_degrees):
        """Update heading with cardinal direction"""
        try:
            if hasattr(self, 'headingValueLabel'):
                # Normalize heading to 0-360
                heading_degrees = heading_degrees % 360
                
                # Convert to cardinal direction
                directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                             'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
                direction_index = int((heading_degrees + 11.25) / 22.5) % 16
                direction = directions[direction_index]
                
                self.headingValueLabel.setText(f"{heading_degrees:03.0f}° ({direction})")
            print(f"Heading updated: {heading_degrees:.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")
    
    def updateDepth(self, depth_meters):
        """Update water depth with VRX simulation context"""
        try:
            if hasattr(self, 'depthValueLabel'):
                # VRX simulation typically has shallow water areas
                if self.simulation_mode and depth_meters < 1.0:
                    depth_note = " (shallow)"
                elif depth_meters > 50.0:
                    depth_note = " (deep)"
                else:
                    depth_note = ""
                    
                self.depthValueLabel.setText(f"{depth_meters:.1f} m{depth_note}")
            print(f"Depth updated: {depth_meters:.1f} m")
        except Exception as e:
            print(f"Error updating depth: {e}")
    
    # **ATTITUDE UPDATES**
    
    def updateRoll(self, roll_degrees):
        """Update roll angle with simulation stability context"""
        try:
            if hasattr(self, 'rollValueLabel'):
                # VRX simulation typically has very stable roll
                if self.simulation_mode and abs(roll_degrees) < 0.1:
                    self.rollValueLabel.setStyleSheet("color: #4caf50; font-weight: bold;")
                else:
                    self.rollValueLabel.setStyleSheet("color: #2e7d32; font-weight: bold;")
                    
                self.rollValueLabel.setText(f"{roll_degrees:+.2f}°")
            print(f"Roll updated: {roll_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating roll: {e}")
    
    def updatePitch(self, pitch_degrees):
        """Update pitch angle with simulation stability context"""
        try:
            if hasattr(self, 'pitchValueLabel'):
                # VRX simulation typically has very stable pitch
                if self.simulation_mode and abs(pitch_degrees) < 0.1:
                    self.pitchValueLabel.setStyleSheet("color: #4caf50; font-weight: bold;")
                else:
                    self.pitchValueLabel.setStyleSheet("color: #2e7d32; font-weight: bold;")
                    
                self.pitchValueLabel.setText(f"{pitch_degrees:+.2f}°")
            print(f"Pitch updated: {pitch_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating pitch: {e}")
    
    def updateAttitude(self, roll, pitch, yaw=None):
        """Update both roll and pitch at once"""
        self.updateRoll(roll)
        self.updatePitch(pitch)
        if yaw is not None:
            self.updateHeading(yaw)
    
    # **SYSTEMS UPDATES**
    
    def updateBatteryLevel(self, percentage):
        """Update battery level with VRX simulation context"""
        try:
            if hasattr(self, 'batteryProgressBar'):
                self.batteryProgressBar.setValue(int(percentage))
                
                # In VRX simulation, battery doesn't typically drain
                if self.simulation_mode:
                    display_text = f"{percentage:.0f}% (SIM)"
                else:
                    display_text = f"{percentage:.0f}%"
                    
                self.batteryProgressBar.setFormat(display_text)
                
                # Update color based on battery level
                if percentage > 60:
                    color_start, color_end = "#4caf50", "#8bc34a"  # Green
                elif percentage > 30:
                    color_start, color_end = "#ff9800", "#ffb74d"  # Orange  
                else:
                    color_start, color_end = "#f44336", "#ef5350"  # Red
                    
                self.batteryProgressBar.setStyleSheet(f"""
                    QProgressBar::chunk {{
                        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                         stop:0 {color_start}, 
                                                         stop:1 {color_end});
                        border-radius: 2px;
                    }}
                """)
                
            print(f"Battery updated: {percentage}%")
        except Exception as e:
            print(f"Error updating battery: {e}")
    
    def updateRudderAngle(self, angle_degrees):
        """Update rudder angle with VRX simulation context"""
        try:
            if hasattr(self, 'rudderProgressBar'):
                # Clamp angle to valid range
                clamped_angle = max(-30, min(30, angle_degrees))
                self.rudderProgressBar.setValue(int(clamped_angle))
                
                # Format display text
                if abs(clamped_angle) < 0.5:
                    display_text = "0° (Center)"
                elif clamped_angle > 0:
                    display_text = f"{clamped_angle:.1f}° R"
                else:
                    display_text = f"{abs(clamped_angle):.1f}° L"
                    
                # Add simulation context
                if self.simulation_mode:
                    display_text += " (SIM)"
                    
                self.rudderProgressBar.setFormat(display_text)
                
            print(f"Rudder updated: {angle_degrees:.1f}°")
        except Exception as e:
            print(f"Error updating rudder: {e}")
    
    # **VRX-SPECIFIC METHODS**
    
    def updateVRXMissionStatus(self, task_name, progress=None):
        """Update current VRX task status"""
        try:
            current_status = getattr(self, '_current_status', 'AUTO')
            if task_name:
                new_status = f"VRX_{task_name.upper()}"
                if progress is not None:
                    new_status += f"_{progress}%"
                self.updateStatus(new_status)
            print(f"VRX Mission Status: {task_name} ({progress}%)" if progress else f"VRX Mission Status: {task_name}")
        except Exception as e:
            print(f"Error updating VRX mission status: {e}")
    
    def updateWaypointProgress(self, current_wp, total_wp, distance_to_wp=None):
        """Update waypoint navigation progress for VRX"""
        try:
            if hasattr(self, 'statusValueLabel'):
                if distance_to_wp is not None:
                    status_text = f"WP {current_wp}/{total_wp} ({distance_to_wp:.1f}m)"
                else:
                    status_text = f"WAYPOINT {current_wp}/{total_wp}"
                    
                if self.simulation_mode:
                    status_text = f"SIM_{status_text}"
                    
                self.updateStatus(status_text)
            print(f"Waypoint progress: {current_wp}/{total_wp}")
        except Exception as e:
            print(f"Error updating waypoint progress: {e}")
    
    # **CONVENIENCE METHODS**
    
    def updateAllNavigation(self, lat, lon, speed_ms, heading):
        """Update all navigation parameters at once"""
        self.updateGPS(lat, lon)
        self.updateSpeed(speed_ms)
        self.updateHeading(heading)
    
    def updateAllTelemetry(self, lat, lon, speed_ms, heading, depth, roll, pitch, battery, rudder):
        """Update all telemetry parameters at once"""
        self.updateGPS(lat, lon)
        self.updateSpeed(speed_ms)
        self.updateHeading(heading)
        self.updateDepth(depth)
        self.updateRoll(roll)
        self.updatePitch(pitch)
        self.updateBatteryLevel(battery)
        self.updateRudderAngle(rudder)
    
    # **UTILITY METHODS**
    
    def resetDisplay(self):
        """Reset all displays to VRX simulation defaults"""
        try:
            if self.simulation_mode:
                self.populateWithVRXData()
            else:
                self.updateStatus("DISCONNECTED")
                self.updateGPS(0.0, 0.0)
                self.updateSpeed(0.0)
                self.updateHeading(0)
                self.updateDepth(0.0)
                self.updateRoll(0.0)
                self.updatePitch(0.0)
                self.updateBatteryLevel(0)
                self.updateRudderAngle(0)
            print("USV Telemetry display reset")
        except Exception as e:
            print(f"Error resetting display: {e}")
    
    def setEmergencyMode(self, emergency=True):
        """Set emergency visual state"""
        try:
            if emergency:
                self.updateStatus("EMERGENCY")
                # Could add red background or flashing effects here
            else:
                status = "SIM_AUTO" if self.simulation_mode else "MANUAL"
                self.updateStatus(status)
                # Reset to normal appearance
            print(f"Emergency mode: {'ON' if emergency else 'OFF'}")
        except Exception as e:
            print(f"Error setting emergency mode: {e}")
    
    # **CONNECTION STATUS METHODS**
    
    def updateConnectionStatus(self, connected=True, connection_type="VRX"):
        """Update connection status with simulation context"""
        try:
            if hasattr(self, 'connectionStatusLabel'):
                if connected:
                    if self.simulation_mode:
                        status_text = f"● CONNECTED ({connection_type} SIM)"
                        color = "#4caf50"  # Bright green for simulation
                        bg_color = "#e8f5e9"
                    else:
                        status_text = f"● CONNECTED ({connection_type})"
                        color = "#28a745"
                        bg_color = "#d4edda"
                else:
                    status_text = "● DISCONNECTED"
                    color = "#dc3545"
                    bg_color = "#f8d7da"
                    
                self.connectionStatusLabel.setText(status_text)
                self.connectionStatusLabel.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-size: 12px;
                        font-weight: bold;
                        background-color: {bg_color};
                        border: 1px solid {color};
                        border-radius: 6px;
                        padding: 8px;
                    }}
                """)
        except Exception as e:
            print(f"Error updating connection status: {e}")
    
    # **LEGACY COMPATIBILITY**
    
    def updateLatitude(self, lat):
        """Legacy compatibility - updates GPS lat"""
        if hasattr(self, '_last_lon'):
            self.updateGPS(lat, self._last_lon)
        self._last_lat = lat
    
    def updateLongitude(self, lon):
        """Legacy compatibility - updates GPS lon"""
        if hasattr(self, '_last_lat'):
            self.updateGPS(self._last_lat, lon)
        self._last_lon = lon
    
    def updatePosition(self, lat, lon):
        """Legacy compatibility - updates GPS position"""
        self.updateGPS(lat, lon)