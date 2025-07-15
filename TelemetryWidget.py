from PySide6.QtGui import QColor
from PySide6.QtCore import QTimer
from uifolder.ui_TelemetryWidget import Ui_TelemetryWidget
from PySide6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect

class TelemetryWidget(QWidget, Ui_TelemetryWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        
        # **UPDATED: Ensure widget expands to fill all available space**
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # **NEW: Add shadow effects after UI setup**
        QTimer.singleShot(50, self.addShadowEffects)
        
        print("TelemetryWidget: Optimized for maximum space utilization")
    
    def addShadowEffects(self):
        """Add modern shadow effects to telemetry sections"""
        try:
            # List of frames to add shadows to
            shadow_frames = [
                'batteryFrame', 'rangeFrame', 'consumptionFrame', 
                'speedFrame', 'headingFrame'
            ]
            
            for frame_name in shadow_frames:
                if hasattr(self, frame_name):
                    frame = getattr(self, frame_name)
                    
                    # Create shadow effect
                    shadow = QGraphicsDropShadowEffect()
                    shadow.setBlurRadius(15)
                    shadow.setXOffset(0)
                    shadow.setYOffset(3)
                    shadow.setColor(QColor(0, 0, 0, 30))  # Light shadow
                    
                    frame.setGraphicsEffect(shadow)
                    
            print("TelemetryWidget: Shadow effects applied")
            
        except Exception as e:
            print(f"TelemetryWidget: Error applying shadow effects: {e}")
    
    # **ADD THESE METHODS (same pattern as IndicatorsPage):**
    def updateBatteryLevel(self, battery_percent, voltage):
        """Called directly from connection thread"""
        try:
            self.batteryPercentLabel.setText(f"{battery_percent}%")
            # Update battery bar if it exists
            if hasattr(self, 'batteryBarFill'):
                bar_width = int((battery_percent / 100) * 96)
                self.batteryBarFill.setGeometry(2, 2, bar_width, 16)
        except Exception as e:
            print(f"Error updating battery: {e}")
    
    def updateSpeed(self, speed):
        """Called directly from connection thread"""
        try:
            self.speedValueLabel.setText(f"{speed:.1f} km/h")
        except Exception as e:
            print(f"Error updating speed: {e}")
    
    def updateHeading(self, heading):
        """Called directly from connection thread"""
        try:
            self.headingValueLabel.setText(f"{heading:03.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")
    
    def updatePosition(self, lat, lon):
        """Called directly from connection thread"""
        try:
            # Update range calculation or other position-based data
            estimated_range = self.calculateRange()
            self.rangeValueLabel.setText(f"{estimated_range} km")
        except Exception as e:
            print(f"Error updating position: {e}")
    
    def calculateRange(self):
        """Simple range calculation"""
        return 164  # Default for now