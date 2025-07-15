from PySide6.QtWidgets import QWidget, QSizePolicy
from uifolder.ui_TelemetryWidget import Ui_TelemetryWidget

class TelemetryWidget(QWidget, Ui_TelemetryWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        
        # **UPDATED: Ensure widget expands to fill all available space**
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        print("TelemetryWidget: Optimized for maximum space utilization")
    
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