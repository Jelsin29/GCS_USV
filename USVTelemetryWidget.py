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
        
        # Initialize with sample data
        QTimer.singleShot(100, self.populateWithSampleData)
        
        print("USVTelemetryWidget: Comprehensive dashboard initialized")
    
    def populateWithSampleData(self):
        """Populate with sample USV data"""
        try:
            # Sample data matching the UI design
            self.updateStatus("MANUAL")
            self.updateGPS(41.0370, 29.0295)
            self.updateSpeed(5.2)  # m/s
            self.updateHeading(175)  # degrees
            self.updateDepth(15.4)  # meters
            self.updateRoll(2.1)  # degrees
            self.updatePitch(1.5)  # degrees
            self.updateBatteryLevel(85)  # percent
            self.updateRudderAngle(10)  # degrees right
            
            print("USVTelemetryWidget: Sample data populated")
            
        except Exception as e:
            print(f"USVTelemetryWidget: Error populating sample data: {e}")
    
    # **NAVIGATION & POSITIONING UPDATES**
    
    def updateStatus(self, status):
        """Update operational status (MANUAL, AUTO, STATION_KEEPING, etc.)"""
        try:
            if hasattr(self, 'statusValueLabel'):
                self.statusValueLabel.setText(status.upper())
                
                # Color coding for different statuses
                colors = {
                    'MANUAL': '#ff6b35',
                    'AUTO': '#2e7d32', 
                    'AUTONOMOUS': '#2e7d32',
                    'STATION_KEEPING': '#1976d2',
                    'RTH': '#f57c00',
                    'EMERGENCY': '#d32f2f'
                }
                
                color = colors.get(status.upper(), '#ff6b35')
                self.statusValueLabel.setStyleSheet(f"color: {color}; font-weight: bold;")
                
            print(f"Status updated: {status}")
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def updateGPS(self, lat, lon):
        """Update GPS coordinates"""
        try:
            if hasattr(self, 'gpsValueLabel'):
                self.gpsValueLabel.setText(f"{lat:.4f}, {lon:.4f}")
            print(f"GPS updated: {lat:.4f}, {lon:.4f}")
        except Exception as e:
            print(f"Error updating GPS: {e}")
    
    def updateSpeed(self, speed_ms):
        """Update speed in m/s and convert to knots"""
        try:
            if hasattr(self, 'speedValueLabel'):
                speed_knots = speed_ms * 1.943844  # Convert m/s to knots
                self.speedValueLabel.setText(f"{speed_ms:.1f} m/s ({speed_knots:.1f} knots)")
            print(f"Speed updated: {speed_ms:.1f} m/s")
        except Exception as e:
            print(f"Error updating speed: {e}")
    
    def updateHeading(self, heading_degrees):
        """Update heading with cardinal direction"""
        try:
            if hasattr(self, 'headingValueLabel'):
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
        """Update water depth"""
        try:
            if hasattr(self, 'depthValueLabel'):
                self.depthValueLabel.setText(f"{depth_meters:.1f} m")
            print(f"Depth updated: {depth_meters:.1f} m")
        except Exception as e:
            print(f"Error updating depth: {e}")
    
    # **ATTITUDE UPDATES**
    
    def updateRoll(self, roll_degrees):
        """Update roll angle"""
        try:
            if hasattr(self, 'rollValueLabel'):
                self.rollValueLabel.setText(f"{roll_degrees:+.1f}°")
            print(f"Roll updated: {roll_degrees:+.1f}°")
        except Exception as e:
            print(f"Error updating roll: {e}")
    
    def updatePitch(self, pitch_degrees):
        """Update pitch angle"""
        try:
            if hasattr(self, 'pitchValueLabel'):
                self.pitchValueLabel.setText(f"{pitch_degrees:+.1f}°")
            print(f"Pitch updated: {pitch_degrees:+.1f}°")
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
        """Update battery level with progress bar"""
        try:
            if hasattr(self, 'batteryProgressBar'):
                self.batteryProgressBar.setValue(percentage)
                self.batteryProgressBar.setFormat(f"{percentage}%")
                
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
        """Update rudder angle (-30 to +30 degrees)"""
        try:
            if hasattr(self, 'rudderProgressBar'):
                # Clamp angle to valid range
                clamped_angle = max(-30, min(30, angle_degrees))
                self.rudderProgressBar.setValue(clamped_angle)
                
                # Format display text
                if clamped_angle == 0:
                    display_text = "0° (Center)"
                elif clamped_angle > 0:
                    display_text = f"{clamped_angle}° R"
                else:
                    display_text = f"{abs(clamped_angle)}° L"
                    
                self.rudderProgressBar.setFormat(display_text)
                
            print(f"Rudder updated: {angle_degrees:.1f}°")
        except Exception as e:
            print(f"Error updating rudder: {e}")
    
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
        """Reset all displays to default values"""
        try:
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
                self.updateStatus("MANUAL")
                # Reset to normal appearance
            print(f"Emergency mode: {'ON' if emergency else 'OFF'}")
        except Exception as e:
            print(f"Error setting emergency mode: {e}")
    
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