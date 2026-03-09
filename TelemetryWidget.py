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
        
        # Connection state tracking
        self.is_connected = False
        self.simulation_mode = False  # Start with real mode, no simulation
        self.vrx_task_active = False
        self.current_waypoint = 0
        self.total_waypoints = 0
        
        # Add shadow effects and initialize with zero data
        QTimer.singleShot(50, self.addShadowEffects)
        QTimer.singleShot(100, self.initializeZeroValues)  # **CHANGED: Initialize with zero values**
        
        print("TelemetryWidget: Initialized with zero values, ready for real telemetry")
    
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

    def initializeZeroValues(self):
        """**NEW: Initialize telemetry widget with zero values instead of mock data**"""
        try:
            # Initialize with zero coordinates and parameters
            self.updateLatitude(0.0)      # Zero latitude
            self.updateLongitude(0.0)     # Zero longitude
            self.updateSpeed(0.0)         # Zero speed
            self.updateRoll(0.0)          # Zero roll
            self.updatePitch(0.0)         # Zero pitch
            
            # Update title for disconnected state
            if hasattr(self, 'titleLabel'):
                self.titleLabel.setText("USV TELEMETRY - DISCONNECTED")
                self.titleLabel.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        background-color: #6c757d;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                    }
                """)
                
            # Set connection flag but avoid recursion
            self.is_connected = False
                
            print("TelemetryWidget: Zero values initialized, ready for live data")
            
        except Exception as e:
            print(f"TelemetryWidget: Error initializing zero values: {e}")

    def setSimulationMode(self, is_simulation=False):
        """Set simulation mode - DEFAULT TO FALSE"""
        self.simulation_mode = is_simulation
        if hasattr(self, 'titleLabel'):
            if is_simulation:
                self.titleLabel.setText("USV SIMULATION")
            else:
                title = "USV TELEMETRY - LIVE" if self.is_connected else "USV TELEMETRY - DISCONNECTED"
                self.titleLabel.setText(title)
        print(f"TelemetryWidget: Simulation mode: {'ON' if is_simulation else 'OFF'}")
        
        # If switching to live mode and not connected, show zero values
        if not is_simulation and not self.is_connected:
            self.initializeZeroValues()

    def setConnectionStatus(self, connected=False, connection_type="USV"):
        """Set connection status and update display accordingly"""
        self.is_connected = connected
        self.updateConnectionStatus(connected, connection_type)
        
        # Update title based on connection status
        if hasattr(self, 'titleLabel'):
            if connected:
                self.titleLabel.setText("USV TELEMETRY - LIVE")
                self.titleLabel.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        background-color: #28a745;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                    }
                """)
            else:
                # When disconnected, just update title (avoid recursion)
                self.titleLabel.setText("USV TELEMETRY - DISCONNECTED")
                self.titleLabel.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        background-color: #dc3545;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                    }
                """)
                print("TelemetryWidget: Connection lost, reset to zero values")
            
    def clearMockData(self):
        """Clear mock data when switching to live mode"""
        try:
            # Reset to zero values instead of just clearing styling
            self.initializeZeroValues()
            print("TelemetryWidget: Reset to zero values, ready for live data")
        except Exception as e:
            print(f"Error clearing mock data: {e}")

    def updateFromVRXData(self, vrx_telemetry):
        """Update telemetry from real ArduPilot data"""
        if not self.is_connected:
            print("TelemetryWidget: Ignoring data - not connected")
            return
            
        try:
            # Handle ArduPilot telemetry data structure
            if 'global_position_int' in vrx_telemetry:
                gps_data = vrx_telemetry['global_position_int']
                lat = gps_data.get('lat', 0) / 1e7  # Convert from int to decimal degrees
                lon = gps_data.get('lon', 0) / 1e7
                self.updateLatitude(lat)
                self.updateLongitude(lon)
                
            if 'vfr_hud' in vrx_telemetry:
                hud = vrx_telemetry['vfr_hud']
                # Convert m/s to knots for display
                speed_ms = hud.get('groundspeed', 0)
                speed_knots = speed_ms * 1.943844
                self.updateSpeed(speed_knots)
                
            if 'attitude' in vrx_telemetry:
                attitude = vrx_telemetry['attitude']
                # Convert radians to degrees
                roll_deg = attitude.get('roll', 0) * 57.2958
                pitch_deg = attitude.get('pitch', 0) * 57.2958
                self.updateRoll(roll_deg)
                self.updatePitch(pitch_deg)
                
            if 'mission_current' in vrx_telemetry:
                mission = vrx_telemetry['mission_current']
                self.current_waypoint = mission.get('seq', 0)
                
            if 'mission_count' in vrx_telemetry:
                count = vrx_telemetry['mission_count']
                self.total_waypoints = count.get('count', 0)
                
            print("TelemetryWidget: Updated from live ArduPilot data")
            
        except Exception as e:
            print(f"TelemetryWidget: Error updating from ArduPilot data: {e}")

    # **DATA UPDATE METHODS**
    
    def updateLatitude(self, lat):
        """Update latitude display"""
        try:
            if hasattr(self, 'rangeValueLabel'):
                # Format latitude with appropriate precision
                if lat == 0.0 and not self.is_connected:
                    lat_text = "0.000000 (NO DATA)"
                    frame_style = """
                        QFrame {
                            background-color: #f8f9fa;
                            border: 2px solid #6c757d;
                            border-radius: 8px;
                            padding: 12px;
                        }
                    """
                else:
                    lat_text = f"{lat:.6f} (LIVE)"
                    frame_style = """
                        QFrame {
                            background-color: #e3f2fd;
                            border: 2px solid #2196f3;
                            border-radius: 8px;
                            padding: 12px;
                        }
                    """
                    
                self.rangeValueLabel.setText(lat_text)
                
                # Update frame styling based on connection status
                if hasattr(self, 'rangeFrame'):
                    self.rangeFrame.setStyleSheet(frame_style)
                    
            print(f"Latitude updated: {lat:.6f}")
        except Exception as e:
            print(f"Error updating latitude: {e}")
    
    def updateLongitude(self, lon):
        """Update longitude display"""
        try:
            if hasattr(self, 'consumptionValueLabel'):
                # Format longitude with appropriate precision
                if lon == 0.0 and not self.is_connected:
                    lon_text = "0.000000 (NO DATA)"
                    frame_style = """
                        QFrame {
                            background-color: #f8f9fa;
                            border: 2px solid #6c757d;
                            border-radius: 8px;
                            padding: 12px;
                        }
                    """
                else:
                    lon_text = f"{lon:.6f} (LIVE)"
                    frame_style = """
                        QFrame {
                            background-color: #e8f5e8;
                            border: 2px solid #4caf50;
                            border-radius: 8px;
                            padding: 12px;
                        }
                    """
                        
                self.consumptionValueLabel.setText(lon_text)
                
                # Update frame styling based on connection status
                if hasattr(self, 'consumptionFrame'):
                    self.consumptionFrame.setStyleSheet(frame_style)
                    
            print(f"Longitude updated: {lon:.6f}")
        except Exception as e:
            print(f"Error updating longitude: {e}")
    
    def updateSpeed(self, speed_knots):
        """Update speed display in knots"""
        try:
            if hasattr(self, 'speedValueLabel'):
                if speed_knots == 0.0 and not self.is_connected:
                    display_text = "0.0 kts (NO DATA)"
                    color_style = "color: #6c757d; font-weight: normal;"
                else:
                    display_text = f"{speed_knots:.1f} kts (LIVE)"
                    color_style = "color: #7b1fa2; font-weight: bold;"
                    
                self.speedValueLabel.setText(display_text)
                self.speedValueLabel.setStyleSheet(color_style)
                
            print(f"Speed updated: {speed_knots:.1f} knots")
        except Exception as e:
            print(f"Error updating speed: {e}")
    
    def updateRoll(self, roll_degrees):
        """Update roll display"""
        try:
            if hasattr(self, 'headingValueLabel'):
                if roll_degrees == 0.0 and not self.is_connected:
                    display_text = "+0.000° (NO DATA)"
                    color_style = "color: #6c757d; font-weight: normal;"
                else:
                    display_text = f"{roll_degrees:+.3f}° (LIVE)"
                    if abs(roll_degrees) > 10.0:  # Significant roll
                        color_style = "color: #f44336; font-weight: bold;"  # Red
                    elif abs(roll_degrees) > 5.0:  # Moderate roll
                        color_style = "color: #ff9800; font-weight: bold;"  # Orange
                    else:  # Normal roll
                        color_style = "color: #4caf50; font-weight: bold;"  # Green
                    
                self.headingValueLabel.setText(display_text)
                self.headingValueLabel.setStyleSheet(color_style)
                
            print(f"Roll updated: {roll_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating roll: {e}")
    
    def updatePitch(self, pitch_degrees):
        """Update pitch display"""
        try:
            if hasattr(self, 'pitchValueLabel'):
                if pitch_degrees == 0.0 and not self.is_connected:
                    display_text = "+0.000° (NO DATA)"
                    color_style = "color: #6c757d; font-weight: normal;"
                else:
                    display_text = f"{pitch_degrees:+.3f}° (LIVE)"
                    if abs(pitch_degrees) > 15.0:  # Significant pitch
                        color_style = "color: #f44336; font-weight: bold;"  # Red
                    elif abs(pitch_degrees) > 8.0:  # Moderate pitch
                        color_style = "color: #ff9800; font-weight: bold;"  # Orange
                    else:  # Normal pitch
                        color_style = "color: #4caf50; font-weight: bold;"  # Green
                    
                self.pitchValueLabel.setText(display_text)
                self.pitchValueLabel.setStyleSheet(color_style)
                
            print(f"Pitch updated: {pitch_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating pitch: {e}")
    
    # **MISSION-SPECIFIC METHODS**
    
    def updateVRXTaskStatus(self, task_name, progress=None, status="ACTIVE"):
        """Update current task information"""
        try:
            if hasattr(self, 'titleLabel'):
                if self.is_connected:
                    if task_name and task_name != "":
                        if progress is not None:
                            title_text = f"USV {task_name.upper()} - {progress}%"
                        else:
                            title_text = f"USV {task_name.upper()}"
                    else:
                        title_text = "USV TELEMETRY - LIVE"
                else:
                    title_text = "USV TELEMETRY - DISCONNECTED"
                    
                self.titleLabel.setText(title_text)
                
                # Update title color based on status
                if not self.is_connected:
                    title_color = "#6c757d"  # Gray for disconnected
                elif status == "COMPLETED":
                    title_color = "#4caf50"  # Green for completed
                elif status == "ACTIVE":
                    title_color = "#2196f3"  # Blue for active
                elif status == "FAILED":
                    title_color = "#f44336"  # Red for failed
                else:
                    title_color = "#28a745"  # Default green for connected
                    
                self.titleLabel.setStyleSheet(f"""
                    QLabel {{
                        color: #ffffff;
                        background-color: {title_color};
                        font-size: 16px;
                        font-weight: bold;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                    }}
                """)
                
            print(f"Task Status: {task_name} ({status})")
        except Exception as e:
            print(f"Error updating task status: {e}")
    
    def updateWaypointProgress(self, current_wp, total_wp, distance_to_wp=None):
        """Update waypoint navigation progress"""
        try:
            if not self.is_connected:
                return  # Don't show waypoint progress when disconnected
                
            self.current_waypoint = current_wp
            self.total_waypoints = total_wp
            
            # Use speed field to show waypoint progress
            if hasattr(self, 'speedValueLabel') and hasattr(self, 'speedLabel'):
                self.speedLabel.setText("Waypoint")
                if distance_to_wp is not None:
                    wp_text = f"{current_wp}/{total_wp} ({distance_to_wp:.0f}m)"
                else:
                    wp_text = f"{current_wp}/{total_wp}"
                    
                self.speedValueLabel.setText(wp_text)
                
                # Update frame color based on progress
                if hasattr(self, 'speedFrame'):
                    progress_pct = (current_wp / max(total_wp, 1)) * 100
                    if progress_pct >= 100:
                        border_color = "#4caf50"  # Green when complete
                    elif progress_pct >= 75:
                        border_color = "#8bc34a"  # Light green
                    elif progress_pct >= 50:
                        border_color = "#ff9800"  # Orange
                    else:
                        border_color = "#ce93d8"  # Default purple
                        
                    self.speedFrame.setStyleSheet(f"""
                        QFrame {{
                            background-color: #f3e5f5;
                            border: 2px solid {border_color};
                            border-radius: 8px;
                            padding: 12px;
                        }}
                    """)
                    
            print(f"Waypoint progress: {current_wp}/{total_wp}")
        except Exception as e:
            print(f"Error updating waypoint progress: {e}")
    
    def updateVRXPerceptionInfo(self, objects_detected, classification_confidence=None):
        """Update perception information"""
        try:
            if not self.is_connected:
                return  # Don't show perception info when disconnected
                
            # Use roll field to show perception info
            if hasattr(self, 'headingValueLabel') and hasattr(self, 'headingLabel'):
                self.headingLabel.setText("Objects")
                if classification_confidence is not None:
                    perception_text = f"{objects_detected} ({classification_confidence:.1f}%)"
                else:
                    perception_text = f"{objects_detected} detected"
                    
                self.headingValueLabel.setText(perception_text)
                
                # Color based on detection confidence
                if classification_confidence is not None:
                    if classification_confidence > 80:
                        color_style = "color: #4caf50; font-weight: bold;"  # High confidence - green
                    elif classification_confidence > 60:
                        color_style = "color: #ff9800; font-weight: bold;"  # Medium confidence - orange
                    else:
                        color_style = "color: #f44336; font-weight: bold;"  # Low confidence - red
                else:
                    color_style = "color: #f57c00; font-weight: bold;"  # Default orange
                    
                self.headingValueLabel.setStyleSheet(color_style)
                
            print(f"Perception: {objects_detected} objects, {classification_confidence}% confidence")
        except Exception as e:
            print(f"Error updating perception info: {e}")
    
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
        if self.is_connected:  # Only update if connected
            self.updateLatitude(lat)
            self.updateLongitude(lon)
            self.updateSpeed(speed_kts)
            self.updateRoll(roll)
            self.updatePitch(pitch)
    
    def updateFromFullVRXState(self, vrx_state):
        """Update all telemetry from complete state"""
        if not self.is_connected:
            return  # Don't process data when not connected
            
        try:
            # Position
            if 'position' in vrx_state:
                pos = vrx_state['position']
                self.updatePosition(pos.get('lat', 0), pos.get('lon', 0))
                
            # Motion
            if 'motion' in vrx_state:
                motion = vrx_state['motion']
                self.updateSpeed(motion.get('speed_knots', 0))
                self.updateRoll(motion.get('roll_deg', 0))
                self.updatePitch(motion.get('pitch_deg', 0))
                
            # Mission status
            if 'mission' in vrx_state:
                mission = vrx_state['mission']
                task_name = mission.get('current_task', '')
                progress = mission.get('progress_pct', None)
                task_status = mission.get('status', 'ACTIVE')
                self.updateVRXTaskStatus(task_name, progress, task_status)
                
                # Waypoint info
                current_wp = mission.get('current_waypoint', 0)
                total_wp = mission.get('total_waypoints', 0)
                wp_distance = mission.get('distance_to_waypoint', None)
                if total_wp > 0:
                    self.updateWaypointProgress(current_wp, total_wp, wp_distance)
                    
            # Perception data
            if 'perception' in vrx_state:
                perception = vrx_state['perception']
                objects = perception.get('objects_detected', 0)
                confidence = perception.get('avg_confidence', None)
                self.updateVRXPerceptionInfo(objects, confidence)
                
            print("TelemetryWidget: Updated from full state")
        except Exception as e:
            print(f"Error updating from full state: {e}")
    
    # **CONNECTION STATUS METHODS**
    
    def updateConnectionStatus(self, connected=False, connection_type="USV"):
        """Update connection status display"""
        try:
            if hasattr(self, 'connectionStatusLabel'):
                if connected:
                    status_text = f"● CONNECTED ({connection_type})"
                    color = "#28a745"
                    bg_color = "#d4edda"
                    border_color = "#c3e6cb"
                else:
                    status_text = "● DISCONNECTED"
                    color = "#dc3545"
                    bg_color = "#f8d7da"
                    border_color = "#f5c6cb"
                    
                self.connectionStatusLabel.setText(status_text)
                self.connectionStatusLabel.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-size: 14px;
                        font-weight: bold;
                        background-color: {bg_color};
                        border: 1px solid {border_color};
                        border-radius: 8px;
                        padding: 12px;
                    }}
                """)
        except Exception as e:
            print(f"Error updating connection status: {e}")
    
    def reset_display(self):
        """Reset all displays to zero values"""
        self.initializeZeroValues()
        print("Telemetry display reset to zero values")
    
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
    
    def updateFromArduPilotData(self, telemetry_data):
        """New method to handle ArduPilot telemetry data directly"""
        try:
            print(f"[TELEMETRY] TelemetryWidget received ArduPilot data: {list(telemetry_data.keys())}")
            
            # Extract and update GPS position
            if 'latitude' in telemetry_data and 'longitude' in telemetry_data:
                self.updatePosition(telemetry_data['latitude'], telemetry_data['longitude'])
                print(f"[TELEMETRY] Updated position: {telemetry_data['latitude']:.6f}, {telemetry_data['longitude']:.6f}")
            
            # Extract and update speed
            if 'groundspeed' in telemetry_data:
                # Convert m/s to knots for display
                speed_knots = telemetry_data['groundspeed'] * 1.944
                self.updateSpeed(speed_knots)
                print(f"[TELEMETRY] Updated speed: {telemetry_data['groundspeed']:.1f}m/s ({speed_knots:.1f} kts)")
            
            # Extract and update attitude
            if 'roll' in telemetry_data:
                self.updateRoll(telemetry_data['roll'])
                print(f"[TELEMETRY] Updated roll: {telemetry_data['roll']:.1f}°")
                
            if 'pitch' in telemetry_data:
                self.updatePitch(telemetry_data['pitch'])
                print(f"[TELEMETRY] Updated pitch: {telemetry_data['pitch']:.1f}°")
            
            # Extract and update heading
            if 'heading' in telemetry_data:
                self.updateHeading(telemetry_data['heading'])
                print(f"[TELEMETRY] Updated heading: {telemetry_data['heading']:.1f}°")
            
            # Extract and update battery
            if 'battery_voltage' in telemetry_data:
                # Estimate percentage from voltage (rough approximation for 12V system)
                voltage = telemetry_data['battery_voltage']
                percentage = max(0, min(100, ((voltage - 11.0) / 1.6) * 100))
                self.updateBatteryLevel(percentage, voltage)
                print(f"[TELEMETRY] Updated battery: {percentage:.0f}% ({voltage:.1f}V)")
            
            print(f"[TELEMETRY] TelemetryWidget update complete")
            
        except Exception as e:
            print(f"[TELEMETRY] Error in TelemetryWidget updateFromArduPilotData: {e}")
            import traceback
            traceback.print_exc()