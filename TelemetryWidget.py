from PySide6.QtGui import QColor
from PySide6.QtCore import QTimer
from uifolder.ui_TelemetryWidget import Ui_TelemetryWidget
from PySide6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect

class TelemetryWidget(QWidget, Ui_TelemetryWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        
        # Ensure widget expands to fill all available space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add shadow effects and sample data after UI setup
        QTimer.singleShot(50, self.addShadowEffects)
        QTimer.singleShot(100, self.populateWithSampleData)
        
        print("TelemetryWidget: Initialized with 5-parameter USV layout")
    
    def addShadowEffects(self):
        """Add modern shadow effects to telemetry sections"""
        try:
            # Add shadows to main telemetry frame
            if hasattr(self, 'telemetryFrame'):
                self.addFrameShadow(self.telemetryFrame)
                
            # Add shadows to individual parameter frames
            parameter_frames = ['rangeFrame', 'consumptionFrame', 'speedFrame', 'headingFrame', 'pitchFrame']
            for frame_name in parameter_frames:
                if hasattr(self, frame_name):
                    frame = getattr(self, frame_name)
                    self.addFrameShadow(frame, blur=10)
                    
            print("TelemetryWidget: Shadow effects applied to 5 parameters")
            
        except Exception as e:
            print(f"TelemetryWidget: Error applying shadow effects: {e}")

    def addFrameShadow(self, frame, blur=15):
        """Add shadow effect to a frame"""
        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(blur)
            shadow.setXOffset(0)
            shadow.setYOffset(3)
            shadow.setColor(QColor(0, 0, 0, 30))
            frame.setGraphicsEffect(shadow)
        except Exception as e:
            print(f"Error adding shadow to frame: {e}")

    def populateWithSampleData(self):
        """Populate telemetry widget with sample USV data matching the screenshot"""
        try:
            # Sample USV telemetry data matching your screenshot
            self.updateLatitude(14.4155610)
            self.updateLongitude(13.8964845)
            self.updateSpeed(2.5)  # knots
            self.updateRoll(-0.05)  # degrees
            self.updatePitch(-0.09)  # degrees
                
            print("TelemetryWidget: Sample 5-parameter USV data populated")
            
        except Exception as e:
            print(f"TelemetryWidget: Error populating sample data: {e}")

    # **USV-SPECIFIC DATA UPDATE METHODS**
    
    def updateLatitude(self, lat):
        """Update latitude display"""
        try:
            if hasattr(self, 'rangeValueLabel'):
                self.rangeValueLabel.setText(f"{lat:.7f}")
            print(f"Latitude updated: {lat:.7f}")
        except Exception as e:
            print(f"Error updating latitude: {e}")
    
    def updateLongitude(self, lon):
        """Update longitude display"""
        try:
            if hasattr(self, 'consumptionValueLabel'):
                self.consumptionValueLabel.setText(f"{lon:.7f}")
            print(f"Longitude updated: {lon:.7f}")
        except Exception as e:
            print(f"Error updating longitude: {e}")
    
    def updateSpeed(self, speed_knots):
        """Update speed display in knots"""
        try:
            if hasattr(self, 'speedValueLabel'):
                self.speedValueLabel.setText(f"{speed_knots:.1f} kts")
            print(f"Speed updated: {speed_knots:.1f} knots")
        except Exception as e:
            print(f"Error updating speed: {e}")
    
    def updateRoll(self, roll_degrees):
        """Update roll display in degrees"""
        try:
            if hasattr(self, 'headingValueLabel'):
                self.headingValueLabel.setText(f"{roll_degrees:+.2f}°")
            print(f"Roll updated: {roll_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating roll: {e}")
    
    def updatePitch(self, pitch_degrees):
        """Update pitch display in degrees"""
        try:
            if hasattr(self, 'pitchValueLabel'):
                self.pitchValueLabel.setText(f"{pitch_degrees:+.2f}°")
            print(f"Pitch updated: {pitch_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating pitch: {e}")
    
    # **CONVENIENCE METHODS**
    
    def updatePosition(self, lat, lon):
        """Update both latitude and longitude at once"""
        self.updateLatitude(lat)
        self.updateLongitude(lon)
    
    def updateAttitude(self, roll, pitch, yaw=None):
        """Update vessel attitude (roll and pitch)"""
        self.updateRoll(roll)
        self.updatePitch(pitch)
        # Note: yaw is not displayed in the 5-parameter layout
        if yaw is not None:
            print(f"Yaw received but not displayed: {yaw:+.2f}°")
    
    def updateAllTelemetry(self, lat, lon, speed_kts, roll, pitch):
        """Update all 5 telemetry parameters at once"""
        self.updateLatitude(lat)
        self.updateLongitude(lon)
        self.updateSpeed(speed_kts)
        self.updateRoll(roll)
        self.updatePitch(pitch)
    
    # **LEGACY COMPATIBILITY METHODS**
    
    def updateBatteryLevel(self, battery_percent, voltage=None):
        """Legacy method - battery not displayed in 5-parameter layout"""
        print(f"Battery level received but not displayed: {battery_percent}%")
    
    def updateHeading(self, heading):
        """Legacy method - redirects to roll for compatibility"""
        self.updateRoll(heading)
    
    def updateYaw(self, yaw_degrees):
        """Legacy method - yaw not displayed in 5-parameter layout"""
        print(f"Yaw received but not displayed: {yaw_degrees:+.2f}°")
    
    def updateDirection(self, heading_degrees):
        """Legacy method - direction not displayed in 5-parameter layout"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        direction_index = int((heading_degrees + 11.25) / 22.5) % 16
        direction = directions[direction_index]
        print(f"Direction received but not displayed: {heading_degrees:.0f}° ({direction})")
    
    # **STATUS METHODS**
    
    def updateConnectionStatus(self, connected=True):
        """Update connection status display"""
        try:
            if hasattr(self, 'connectionStatusLabel'):
                if connected:
                    self.connectionStatusLabel.setText("● CONNECTED")
                    self.connectionStatusLabel.setStyleSheet("""
                        QLabel {
                            color: #28a745;
                            font-size: 14px;
                            font-weight: bold;
                            background-color: #d4edda;
                            border: 1px solid #c3e6cb;
                            border-radius: 8px;
                            padding: 12px;
                        }
                    """)
                else:
                    self.connectionStatusLabel.setText("● DISCONNECTED")
                    self.connectionStatusLabel.setStyleSheet("""
                        QLabel {
                            color: #dc3545;
                            font-size: 14px;
                            font-weight: bold;
                            background-color: #f8d7da;
                            border: 1px solid #f5c6cb;
                            border-radius: 8px;
                            padding: 12px;
                        }
                    """)
        except Exception as e:
            print(f"Error updating connection status: {e}")
    
    def reset_display(self):
        """Reset all displays to default values"""
        try:
            self.updateLatitude(0.0)
            self.updateLongitude(0.0)
            self.updateSpeed(0.0)
            self.updateRoll(0.0)
            self.updatePitch(0.0)
            self.updateConnectionStatus(False)
            print("Telemetry display reset to default values")
        except Exception as e:
            print(f"Error resetting display: {e}")