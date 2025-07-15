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
        
        # **NEW: Add shadow effects and sample data after UI setup**
        QTimer.singleShot(50, self.addShadowEffects)
        QTimer.singleShot(100, self.populateWithSampleData)
        
        print("TelemetryWidget: Initialized with modern styling")
    
    def addShadowEffects(self):
        """Add modern shadow effects to telemetry sections"""
        try:
            # Add shadows to main frames
            if hasattr(self, 'batteryFrame'):
                self.addFrameShadow(self.batteryFrame)
                
            if hasattr(self, 'telemetryFrame'):
                self.addFrameShadow(self.telemetryFrame)
                
            # Add shadows to individual telemetry frames if they exist
            telemetry_frames = ['rangeFrame', 'consumptionFrame', 'speedFrame', 'headingFrame']
            for frame_name in telemetry_frames:
                if hasattr(self, frame_name):
                    frame = getattr(self, frame_name)
                    self.addFrameShadow(frame, blur=10)
                    
            print("TelemetryWidget: Shadow effects applied")
            
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
        """Populate telemetry widget with sample data for appearance testing"""
        try:
            # Battery data
            if hasattr(self, 'batteryPercentLabel'):
                self.batteryPercentLabel.setText("87%")
                
            # Create battery bar effect (if batteryBarFrame exists)
            if hasattr(self, 'batteryBarFrame'):
                # Add visual battery level indicator
                self.updateBatteryBar(87)
                
            print("TelemetryWidget: Sample data populated")
            
        except Exception as e:
            print(f"TelemetryWidget: Error populating sample data: {e}")

    def updateBatteryBar(self, percentage):
        """Update battery bar visual indicator"""
        try:
            if hasattr(self, 'batteryBarFrame'):
                # Change background color based on battery level
                if percentage > 60:
                    color = "#28a745"  # Green
                elif percentage > 30:
                    color = "#ffc107"  # Yellow
                else:
                    color = "#dc3545"  # Red
                    
                self.batteryBarFrame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color};
                        border-radius: 6px;
                        margin: 2px;
                    }}
                """)
        except Exception as e:
            print(f"Error updating battery bar: {e}")
    
    # **SAMPLE DATA METHODS (for appearance only)**
    def updateBatteryLevel(self, battery_percent, voltage):
        """Demo method - updates battery display"""
        try:
            if hasattr(self, 'batteryPercentLabel'):
                self.batteryPercentLabel.setText(f"{battery_percent}%")
            self.updateBatteryBar(battery_percent)
        except Exception as e:
            print(f"Error updating battery: {e}")
    
    def updateSpeed(self, speed):
        """Demo method - updates speed display"""
        try:
            # If you have speed labels in your UI, update them here
            print(f"Speed updated: {speed:.1f} km/h")
        except Exception as e:
            print(f"Error updating speed: {e}")
    
    def updateHeading(self, heading):
        """Demo method - updates heading display"""
        try:
            # If you have heading labels in your UI, update them here
            print(f"Heading updated: {heading:03.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")
    
    def updatePosition(self, lat, lon):
        """Demo method - updates position display"""
        try:
            print(f"Position updated: {lat}, {lon}")
        except Exception as e:
            print(f"Error updating position: {e}")