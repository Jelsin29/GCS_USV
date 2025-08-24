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
        
        # VRX simulation state tracking
        self.simulation_mode = True
        self.vrx_task_active = False
        self.current_waypoint = 0
        self.total_waypoints = 0
        
        # Add shadow effects and VRX data after UI setup
        QTimer.singleShot(50, self.addShadowEffects)
        QTimer.singleShot(100, self.populateWithVRXData)
        
        print("TelemetryWidget: VRX-compatible USV layout initialized")
    
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
                    
            print("TelemetryWidget: Shadow effects applied to VRX telemetry")
            
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

    def populateWithVRXData(self):
        """Populate telemetry widget with VRX simulation appropriate data"""
        try:
            # VRX simulation data - Sandisland Marina starting position
            self.updateLatitude(21.31924)    # VRX starting latitude
            self.updateLongitude(-157.88916) # VRX starting longitude  
            self.updateSpeed(2.5)            # knots - typical USV speed
            self.updateRoll(0.05)            # degrees - very stable in simulation
            self.updatePitch(-0.02)          # degrees - slight bow down
            
            # Update title for VRX mode
            if hasattr(self, 'titleLabel'):
                self.titleLabel.setText("VRX USV SIMULATION")
                
            print("TelemetryWidget: VRX simulation data populated")
            
        except Exception as e:
            print(f"TelemetryWidget: Error populating VRX data: {e}")

    def setSimulationMode(self, is_simulation=True):
        """Set VRX simulation mode"""
        self.simulation_mode = is_simulation
        if hasattr(self, 'titleLabel'):
            if is_simulation:
                self.titleLabel.setText("VRX USV SIMULATION")
            else:
                self.titleLabel.setText("AUTONOMOUS USV")
        print(f"TelemetryWidget: Simulation mode: {'VRX' if is_simulation else 'LIVE'}")

    def updateFromVRXData(self, vrx_telemetry):
        """Update telemetry from VRX ArduPilot data"""
        try:
            # Handle VRX telemetry data structure from ArduPilot connection
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
                
            print("TelemetryWidget: Updated from VRX telemetry")
            
        except Exception as e:
            print(f"TelemetryWidget: Error updating from VRX data: {e}")

    # **VRX-SPECIFIC DATA UPDATE METHODS**
    
    def updateLatitude(self, lat):
        """Update latitude display with VRX context"""
        try:
            if hasattr(self, 'rangeValueLabel'):
                # Check if we're in VRX area (Hawaii coordinates)
                if 21.0 <= lat <= 22.0:
                    self.rangeValueLabel.setText(f"{lat:.6f}")
                    # Update frame color for VRX area
                    if hasattr(self, 'rangeFrame'):
                        self.rangeFrame.setStyleSheet("""
                            QFrame {
                                background-color: #e8f5e8;
                                border: 2px solid #4caf50;
                                border-radius: 8px;
                                padding: 12px;
                            }
                        """)
                else:
                    self.rangeValueLabel.setText(f"{lat:.6f}")
                    
            print(f"Latitude updated: {lat:.6f}")
        except Exception as e:
            print(f"Error updating latitude: {e}")
    
    def updateLongitude(self, lon):
        """Update longitude display with VRX context"""
        try:
            if hasattr(self, 'consumptionValueLabel'):
                # Check if we're in VRX area (Hawaii coordinates)  
                if -158.0 <= lon <= -157.0:
                    self.consumptionValueLabel.setText(f"{lon:.6f}")
                    # Update frame color for VRX area
                    if hasattr(self, 'consumptionFrame'):
                        self.consumptionFrame.setStyleSheet("""
                            QFrame {
                                background-color: #e8f5e8;
                                border: 2px solid #4caf50;
                                border-radius: 8px;
                                padding: 12px;
                            }
                        """)
                else:
                    self.consumptionValueLabel.setText(f"{lon:.6f}")
                    
            print(f"Longitude updated: {lon:.6f}")
        except Exception as e:
            print(f"Error updating longitude: {e}")
    
    def updateSpeed(self, speed_knots):
        """Update speed display in knots with VRX simulation context"""
        try:
            if hasattr(self, 'speedValueLabel'):
                if self.simulation_mode:
                    # VRX simulation speeds are typically lower and more stable
                    display_text = f"{speed_knots:.1f} kt (SIM)"
                    if speed_knots > 15:  # High speed for USV
                        display_text += " ⚡"
                else:
                    display_text = f"{speed_knots:.1f} kt"
                    
                self.speedValueLabel.setText(display_text)
            print(f"Speed updated: {speed_knots:.1f} knots")
        except Exception as e:
            print(f"Error updating speed: {e}")
    
    def updateRoll(self, roll_degrees):
        """Update roll display with VRX simulation stability"""
        try:
            if hasattr(self, 'headingValueLabel'):
                # VRX simulation typically has very stable roll
                if self.simulation_mode and abs(roll_degrees) < 0.1:
                    display_text = f"{roll_degrees:+.3f}° (STABLE)"
                    color_style = "color: #4caf50; font-weight: bold;"
                else:
                    display_text = f"{roll_degrees:+.2f}°"
                    color_style = "color: #f57c00; font-weight: bold;"
                    
                self.headingValueLabel.setText(display_text)
                self.headingValueLabel.setStyleSheet(color_style)
            print(f"Roll updated: {roll_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating roll: {e}")
    
    def updatePitch(self, pitch_degrees):
        """Update pitch display with VRX simulation stability"""
        try:
            if hasattr(self, 'pitchValueLabel'):
                # VRX simulation typically has very stable pitch
                if self.simulation_mode and abs(pitch_degrees) < 0.1:
                    display_text = f"{pitch_degrees:+.3f}° (STABLE)"
                    color_style = "color: #4caf50; font-weight: bold;"
                else:
                    display_text = f"{pitch_degrees:+.2f}°"
                    color_style = "color: #ad1457; font-weight: bold;"
                    
                self.pitchValueLabel.setText(display_text)
                self.pitchValueLabel.setStyleSheet(color_style)
            print(f"Pitch updated: {pitch_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating pitch: {e}")
    
    # **VRX MISSION-SPECIFIC METHODS**
    
    def updateVRXTaskStatus(self, task_name, progress=None, status="ACTIVE"):
        """Update current VRX task information"""
        try:
            if hasattr(self, 'titleLabel'):
                if task_name and task_name != "":
                    if progress is not None:
                        title_text = f"VRX {task_name.upper()} - {progress}%"
                    else:
                        title_text = f"VRX {task_name.upper()}"
                else:
                    title_text = "VRX USV SIMULATION"
                    
                self.titleLabel.setText(title_text)
                
                # Update title color based on task status
                if status == "COMPLETED":
                    title_color = "#4caf50"  # Green for completed
                elif status == "ACTIVE":
                    title_color = "#2196f3"  # Blue for active
                elif status == "FAILED":
                    title_color = "#f44336"  # Red for failed
                else:
                    title_color = "#ffffff"  # Default white
                    
                self.titleLabel.setStyleSheet(f"""
                    QLabel {{
                        color: {title_color};
                        background-color: #0d47a1;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                    }}
                """)
                
            print(f"VRX Task Status: {task_name} ({status})")
        except Exception as e:
            print(f"Error updating VRX task status: {e}")
    
    def updateWaypointProgress(self, current_wp, total_wp, distance_to_wp=None):
        """Update waypoint navigation progress for VRX tasks"""
        try:
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
        """Update perception information for VRX tasks"""
        try:
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
        self.updateLatitude(lat)
        self.updateLongitude(lon)
        self.updateSpeed(speed_kts)
        self.updateRoll(roll)
        self.updatePitch(pitch)
    
    def updateFromFullVRXState(self, vrx_state):
        """Update all telemetry from complete VRX state"""
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
                
            print("TelemetryWidget: Updated from full VRX state")
        except Exception as e:
            print(f"Error updating from full VRX state: {e}")
    
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
    
    def updateConnectionStatus(self, connected=True, connection_type="VRX"):
        """Update connection status display for VRX"""
        try:
            if hasattr(self, 'connectionStatusLabel'):
                if connected:
                    if self.simulation_mode:
                        status_text = f"● CONNECTED ({connection_type} SIMULATION)"
                        color = "#4caf50"  # Bright green for VRX simulation
                        bg_color = "#e8f5e9"
                        border_color = "#4caf50"
                    else:
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
        """Reset all displays to VRX simulation defaults"""
        try:
            if self.simulation_mode:
                self.populateWithVRXData()
            else:
                self.updateLatitude(0.0)
                self.updateLongitude(0.0)
                self.updateSpeed(0.0)
                self.updateRoll(0.0)
                self.updatePitch(0.0)
                
            self.updateConnectionStatus(False)
            print("Telemetry display reset to VRX defaults" if self.simulation_mode else "Telemetry display reset to default values")
        except Exception as e:
            print(f"Error resetting display: {e}")
    
    def setVRXEnvironmentInfo(self, weather_condition="CALM", sea_state=1, visibility_km=10):
        """Set VRX environment information display"""
        try:
            # Could use pitch field to show environment info
            if hasattr(self, 'pitchValueLabel') and hasattr(self, 'pitchLabel'):
                self.pitchLabel.setText("Env")
                env_text = f"{weather_condition} SS{sea_state}"
                self.pitchValueLabel.setText(env_text)
                
                # Color based on conditions
                if sea_state <= 2 and weather_condition in ["CALM", "CLEAR"]:
                    color_style = "color: #4caf50; font-weight: bold;"  # Good conditions - green
                elif sea_state <= 4:
                    color_style = "color: #ff9800; font-weight: bold;"  # Moderate - orange
                else:
                    color_style = "color: #f44336; font-weight: bold;"  # Poor conditions - red
                    
                self.pitchValueLabel.setStyleSheet(color_style)
                
            print(f"VRX Environment: {weather_condition}, Sea State {sea_state}, Visibility {visibility_km}km")
        except Exception as e:
            print(f"Error updating VRX environment info: {e}")