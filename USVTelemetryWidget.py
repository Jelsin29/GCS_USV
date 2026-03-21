from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy


class USVTelemetryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load .ui file at runtime (setupUi + multiple inheritance causes segfault)
        loader = QUiLoader()
        ui_file = QFile("uifolder/USVTelemetryWidget.ui")
        ui_file.open(QFile.ReadOnly)
        self._ui_widget = loader.load(ui_file, self)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui_widget)

        # Expose .ui labels as direct attributes for compatibility
        for attr in [
            "statusValueLabel",
            "gpsValueLabel",
            "speedValueLabel",
            "headingValueLabel",
            "depthValueLabel",
            "rollValueLabel",
            "pitchValueLabel",
            "batteryProgressBar",
            "rudderProgressBar",
            "connectionStatusLabel",
            "headerLabel",
        ]:
            widget = self._ui_widget.findChild(QWidget, attr)
            if widget:
                setattr(self, attr, widget)

        # Ensure widget expands properly
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connection state tracking
        self.is_connected = False
        self.simulation_mode = False  # Start with real mode, no simulation
        self.last_update_time = 0

        # **UPDATED: Initialize with zero values instead of mock data**
        self.initializeZeroValues()

        print(
            "USVTelemetryWidget: Initialized with zero values, ready for real telemetry"
        )

    def initializeZeroValues(self):
        """Initialize all telemetry displays with zero/disconnected values"""
        try:
            # Set all values to zero/disconnected state
            self.updateStatus("DISCONNECTED")
            self.updateGPS(0.0, 0.0)  # Zero coordinates
            self.updateSpeed(0.0)  # Zero speed
            self.updateHeading(0)  # Zero heading
            self.updateDepth(0.0)  # Zero depth
            self.updateRoll(0.0)  # Zero roll
            self.updatePitch(0.0)  # Zero pitch
            self.updateBatteryLevel(0)  # Zero battery
            self.updateRudderAngle(0.0)  # Zero rudder angle
            self.updateConnectionStatus(False)  # Disconnected

            print("USVTelemetryWidget: All values initialized to zero/disconnected")

        except Exception as e:
            print(f"USVTelemetryWidget: Error initializing zero values: {e}")

    def setSimulationMode(self, is_simulation=False):
        """Set whether we're running in simulation mode - DEFAULT TO FALSE"""
        self.simulation_mode = is_simulation
        if not is_simulation and not self.is_connected:
            # If not in simulation and not connected, show zero values
            self.initializeZeroValues()
        print(
            f"USVTelemetryWidget: Simulation mode: {'ON' if is_simulation else 'OFF'}"
        )

    def setConnectionStatus(self, connected=False, connection_type="USV"):
        """Set connection status and update display accordingly"""
        self.is_connected = connected
        self.updateConnectionStatus(connected, connection_type)

        if not connected:
            # When disconnected, reset to zero values
            self.initializeZeroValues()
            print("USVTelemetryWidget: Connection lost, reset to zero values")
        else:
            # When connected, stop showing zero values and wait for real data
            print("USVTelemetryWidget: Connected, ready for live telemetry data")

    def updateFromVRXData(self, vrx_telemetry):
        """Update telemetry from real ArduPilot data structure"""
        if not self.is_connected:
            print("USVTelemetryWidget: Ignoring data - not connected")
            return

        try:
            # Expected ArduPilot telemetry structure
            if "global_position_int" in vrx_telemetry:
                gps_data = vrx_telemetry["global_position_int"]
                self.updateGPS(
                    gps_data.get("lat", 0) / 1e7, gps_data.get("lon", 0) / 1e7
                )

            if "attitude" in vrx_telemetry:
                attitude = vrx_telemetry["attitude"]
                self.updateRoll(attitude.get("roll", 0) * 57.2958)  # Convert rad to deg
                self.updatePitch(attitude.get("pitch", 0) * 57.2958)
                self.updateHeading(attitude.get("yaw", 0) * 57.2958)

            if "vfr_hud" in vrx_telemetry:
                hud = vrx_telemetry["vfr_hud"]
                self.updateSpeed(hud.get("groundspeed", 0))
                self.updateHeading(hud.get("heading", 0))

            if "battery_status" in vrx_telemetry:
                battery = vrx_telemetry["battery_status"]
                self.updateBatteryLevel(battery.get("battery_remaining", 0))

            if "servo_output_raw" in vrx_telemetry:
                servo = vrx_telemetry["servo_output_raw"]
                # Assuming rudder is on servo channel 4 (typical for USV)
                rudder_pwm = servo.get("servo4_raw", 1500)
                rudder_angle = (rudder_pwm - 1500) * 30 / 500  # Convert PWM to angle
                self.updateRudderAngle(rudder_angle)

            if "rangefinder" in vrx_telemetry:
                rangefinder = vrx_telemetry["rangefinder"]
                self.updateDepth(rangefinder.get("distance", 0))

            # Update mode based on flight mode
            if "heartbeat" in vrx_telemetry:
                mode = vrx_telemetry["heartbeat"].get("custom_mode", 0)
                mode_names = {
                    0: "MANUAL",
                    1: "ACRO",
                    2: "STEERING",
                    3: "HOLD",
                    4: "LOITER",
                    5: "FOLLOW",
                    6: "SIMPLE",
                    10: "AUTO",
                    11: "RTL",
                    12: "SMARTRTL",
                    15: "GUIDED",
                }
                mode_name = mode_names.get(mode, f"MODE_{mode}")
                # Add LIVE prefix for real data
                self.updateStatus(f"LIVE_{mode_name}")

            self.last_update_time = QTimer().remainingTime()
            print("USVTelemetryWidget: Updated from live ArduPilot data")

        except Exception as e:
            print(f"USVTelemetryWidget: Error updating from ArduPilot data: {e}")

    # **NAVIGATION & POSITIONING UPDATES**

    def updateStatus(self, status):
        """Update operational status"""
        try:
            if hasattr(self, "statusValueLabel"):
                display_status = status.upper()
                self.statusValueLabel.setText(display_status)

                # Color coding for different statuses
                colors = {
                    "DISCONNECTED": "#6c757d",  # Gray for disconnected
                    "MANUAL": "#ff6b35",
                    "AUTO": "#2e7d32",
                    "AUTONOMOUS": "#2e7d32",
                    "LIVE_AUTO": "#4caf50",  # Brighter green for live data
                    "LIVE_MANUAL": "#ff8a65",  # Lighter orange for live data
                    "STATION_KEEPING": "#1976d2",
                    "LOITER": "#1976d2",
                    "HOLD": "#1976d2",
                    "RTL": "#f57c00",
                    "SMARTRTL": "#f57c00",
                    "GUIDED": "#9c27b0",
                    "EMERGENCY": "#d32f2f",
                }

                color = colors.get(display_status, "#6c757d")
                self.statusValueLabel.setStyleSheet(
                    f"color: {color}; font-weight: bold;"
                )

            print(f"Status updated: {status}")
        except Exception as e:
            print(f"Error updating status: {e}")

    def updateGPS(self, lat, lon):
        """Update GPS coordinates"""
        try:
            if hasattr(self, "gpsValueLabel"):
                if lat == 0.0 and lon == 0.0 and not self.is_connected:
                    # Show disconnected state
                    self.gpsValueLabel.setText("0.000000, 0.000000 (NO GPS)")
                    self.gpsValueLabel.setStyleSheet(
                        "color: #6c757d; font-weight: normal;"
                    )
                else:
                    # Show real data
                    location_note = " (LIVE)" if self.is_connected else ""
                    self.gpsValueLabel.setText(f"{lat:.6f}, {lon:.6f}{location_note}")
                    self.gpsValueLabel.setStyleSheet(
                        "color: #0277bd; font-weight: bold;"
                    )

            print(f"GPS updated: {lat:.6f}, {lon:.6f}")
        except Exception as e:
            print(f"Error updating GPS: {e}")

    def updateSpeed(self, speed_ms):
        """Update speed in m/s"""
        try:
            if hasattr(self, "speedValueLabel"):
                speed_knots = speed_ms * 1.943844  # Convert m/s to knots

                if speed_ms == 0.0 and not self.is_connected:
                    # Show disconnected state
                    self.speedValueLabel.setText("0.0 m/s (0.0 kt) - NO DATA")
                    self.speedValueLabel.setStyleSheet(
                        "color: #6c757d; font-weight: normal;"
                    )
                else:
                    # Show real data
                    data_note = " (LIVE)" if self.is_connected else ""
                    self.speedValueLabel.setText(
                        f"{speed_ms:.1f} m/s ({speed_knots:.1f} kt{data_note})"
                    )
                    self.speedValueLabel.setStyleSheet(
                        "color: #0277bd; font-weight: bold;"
                    )

            print(f"Speed updated: {speed_ms:.1f} m/s")
        except Exception as e:
            print(f"Error updating speed: {e}")

    def updateHeading(self, heading_degrees):
        """Update heading with cardinal direction"""
        try:
            if hasattr(self, "headingValueLabel"):
                # Normalize heading to 0-360
                heading_degrees = heading_degrees % 360

                # Convert to cardinal direction
                directions = [
                    "N",
                    "NNE",
                    "NE",
                    "ENE",
                    "E",
                    "ESE",
                    "SE",
                    "SSE",
                    "S",
                    "SSW",
                    "SW",
                    "WSW",
                    "W",
                    "WNW",
                    "NW",
                    "NNW",
                ]
                direction_index = int((heading_degrees + 11.25) / 22.5) % 16
                direction = directions[direction_index]

                if heading_degrees == 0 and not self.is_connected:
                    # Show disconnected state
                    self.headingValueLabel.setText("000° (N) - NO DATA")
                    self.headingValueLabel.setStyleSheet(
                        "color: #6c757d; font-weight: normal;"
                    )
                else:
                    # Show real data
                    data_note = " (LIVE)" if self.is_connected else ""
                    self.headingValueLabel.setText(
                        f"{heading_degrees:03.0f}° ({direction}){data_note}"
                    )
                    self.headingValueLabel.setStyleSheet(
                        "color: #0277bd; font-weight: bold;"
                    )

            print(f"Heading updated: {heading_degrees:.0f}°")
        except Exception as e:
            print(f"Error updating heading: {e}")

    def updateDepth(self, depth_meters):
        """Update water depth"""
        try:
            if hasattr(self, "depthValueLabel"):
                if depth_meters == 0.0 and not self.is_connected:
                    # Show disconnected state
                    self.depthValueLabel.setText("0.0 m - NO DATA")
                    self.depthValueLabel.setStyleSheet(
                        "color: #6c757d; font-weight: normal;"
                    )
                else:
                    # Show real data
                    data_note = " (LIVE)" if self.is_connected else ""
                    depth_note = (
                        " (shallow)"
                        if depth_meters < 1.0
                        else " (deep)"
                        if depth_meters > 50.0
                        else ""
                    )
                    self.depthValueLabel.setText(
                        f"{depth_meters:.1f} m{depth_note}{data_note}"
                    )
                    self.depthValueLabel.setStyleSheet(
                        "color: #0277bd; font-weight: bold;"
                    )

            print(f"Depth updated: {depth_meters:.1f} m")
        except Exception as e:
            print(f"Error updating depth: {e}")

    # **ATTITUDE UPDATES**

    def updateRoll(self, roll_degrees):
        """Update roll angle"""
        try:
            if hasattr(self, "rollValueLabel"):
                if roll_degrees == 0.0 and not self.is_connected:
                    # Show disconnected state
                    self.rollValueLabel.setText("+0.00° - NO DATA")
                    self.rollValueLabel.setStyleSheet(
                        "color: #6c757d; font-weight: normal;"
                    )
                else:
                    # Show real data
                    self.rollValueLabel.setText(f"{roll_degrees:+.2f}°")
                    self.rollValueLabel.setStyleSheet(
                        "color: #2e7d32; font-weight: bold;"
                    )

            print(f"Roll updated: {roll_degrees:+.2f}°")
        except Exception as e:
            print(f"Error updating roll: {e}")

    def updatePitch(self, pitch_degrees):
        """Update pitch angle"""
        try:
            if hasattr(self, "pitchValueLabel"):
                if pitch_degrees == 0.0 and not self.is_connected:
                    # Show disconnected state
                    self.pitchValueLabel.setText("+0.00° - NO DATA")
                    self.pitchValueLabel.setStyleSheet(
                        "color: #6c757d; font-weight: normal;"
                    )
                else:
                    # Show real data
                    self.pitchValueLabel.setText(f"{pitch_degrees:+.2f}°")
                    self.pitchValueLabel.setStyleSheet(
                        "color: #2e7d32; font-weight: bold;"
                    )

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
        """Update battery level"""
        try:
            if hasattr(self, "batteryProgressBar"):
                self.batteryProgressBar.setValue(int(percentage))

                if percentage == 0 and not self.is_connected:
                    # Show disconnected state
                    display_text = "0% - NO DATA"
                    color_start, color_end = "#6c757d", "#6c757d"  # Gray
                else:
                    # Show real data
                    display_text = f"{percentage:.0f}%" + (
                        " (LIVE)" if self.is_connected else ""
                    )

                    # Update color based on battery level
                    if percentage > 60:
                        color_start, color_end = "#4caf50", "#8bc34a"  # Green
                    elif percentage > 30:
                        color_start, color_end = "#ff9800", "#ffb74d"  # Orange
                    else:
                        color_start, color_end = "#f44336", "#ef5350"  # Red

                self.batteryProgressBar.setFormat(display_text)
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
        """Update rudder angle"""
        try:
            if hasattr(self, "rudderProgressBar"):
                # Clamp angle to valid range
                clamped_angle = max(-30, min(30, angle_degrees))
                self.rudderProgressBar.setValue(int(clamped_angle))

                if clamped_angle == 0.0 and not self.is_connected:
                    # Show disconnected state
                    display_text = "0° - NO DATA"
                else:
                    # Format display text for real data
                    if abs(clamped_angle) < 0.5:
                        display_text = "0° (Center)"
                    elif clamped_angle > 0:
                        display_text = f"{clamped_angle:.1f}° R"
                    else:
                        display_text = f"{abs(clamped_angle):.1f}° L"

                    # Add live data context
                    if self.is_connected:
                        display_text += " (LIVE)"

                self.rudderProgressBar.setFormat(display_text)

            print(f"Rudder updated: {angle_degrees:.1f}°")
        except Exception as e:
            print(f"Error updating rudder: {e}")

    # **CONNECTION STATUS METHODS**

    def updateConnectionStatus(self, connected=False, connection_type="USV"):
        """Update connection status display"""
        try:
            if hasattr(self, "connectionStatusLabel"):
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

    # **UTILITY METHODS**

    def resetDisplay(self):
        """Reset all displays to zero values"""
        self.initializeZeroValues()
        print("USV Telemetry display reset to zero values")

    def setEmergencyMode(self, emergency=True):
        """Set emergency visual state"""
        try:
            if emergency:
                self.updateStatus("EMERGENCY")
            else:
                status = "DISCONNECTED" if not self.is_connected else "MANUAL"
                self.updateStatus(status)
            print(f"Emergency mode: {'ON' if emergency else 'OFF'}")
        except Exception as e:
            print(f"Error setting emergency mode: {e}")

    # **CONVENIENCE METHODS**

    def updateAllNavigation(self, lat, lon, speed_ms, heading):
        """Update all navigation parameters at once"""
        self.updateGPS(lat, lon)
        self.updateSpeed(speed_ms)
        self.updateHeading(heading)

    def updateAllTelemetry(
        self, lat, lon, speed_ms, heading, depth, roll, pitch, battery, rudder
    ):
        """Update all telemetry parameters at once"""
        if self.is_connected:  # Only update if connected
            self.updateGPS(lat, lon)
            self.updateSpeed(speed_ms)
            self.updateHeading(heading)
            self.updateDepth(depth)
            self.updateRoll(roll)
            self.updatePitch(pitch)
            self.updateBatteryLevel(battery)
            self.updateRudderAngle(rudder)

    # **LEGACY COMPATIBILITY**

    def updateLatitude(self, lat):
        """Legacy compatibility - updates GPS lat"""
        if hasattr(self, "_last_lon"):
            self.updateGPS(lat, self._last_lon)
        self._last_lat = lat

    def updateLongitude(self, lon):
        """Legacy compatibility - updates GPS lon"""
        if hasattr(self, "_last_lat"):
            self.updateGPS(self._last_lat, lon)
        self._last_lon = lon

    def updatePosition(self, lat, lon):
        """Legacy compatibility - updates GPS position"""
        self.updateGPS(lat, lon)

    def updateFromArduPilotData(self, telemetry_data):
        """New method to handle ArduPilot telemetry data directly"""
        try:
            print(
                f"[USV_TELEMETRY] USVTelemetryWidget received ArduPilot data: {list(telemetry_data.keys())}"
            )

            # Extract and update GPS position
            if "latitude" in telemetry_data and "longitude" in telemetry_data:
                self.updateGPS(telemetry_data["latitude"], telemetry_data["longitude"])
                print(
                    f"[USV_TELEMETRY] Updated GPS: {telemetry_data['latitude']:.6f}, {telemetry_data['longitude']:.6f}"
                )

            # Extract and update speed
            if "groundspeed" in telemetry_data:
                # USVTelemetryWidget expects speed in m/s
                self.updateSpeed(telemetry_data["groundspeed"])
                print(
                    f"[USV_TELEMETRY] Updated speed: {telemetry_data['groundspeed']:.1f} m/s"
                )

            # Extract and update heading
            if "heading" in telemetry_data:
                self.updateHeading(telemetry_data["heading"])
                print(
                    f"[USV_TELEMETRY] Updated heading: {telemetry_data['heading']:.1f}°"
                )

            # Extract and update depth (for USV, use altitude if available)
            if "altitude" in telemetry_data:
                # For surface vessels, depth is usually 0, but we can show relative altitude
                depth = max(0, -telemetry_data["altitude"])  # Convert altitude to depth
                self.updateDepth(depth)
                print(f"[USV_TELEMETRY] Updated depth: {depth:.1f} m (from altitude)")

            # Extract and update attitude
            if "roll" in telemetry_data and "pitch" in telemetry_data:
                yaw = telemetry_data.get("yaw", telemetry_data.get("heading", 0))
                self.updateAttitude(
                    telemetry_data["roll"], telemetry_data["pitch"], yaw
                )
                print(
                    f"[USV_TELEMETRY] Updated attitude: Roll={telemetry_data['roll']:.1f}°, Pitch={telemetry_data['pitch']:.1f}°"
                )
            elif "roll" in telemetry_data:
                self.updateRoll(telemetry_data["roll"])
                print(f"[USV_TELEMETRY] Updated roll: {telemetry_data['roll']:.1f}°")
            elif "pitch" in telemetry_data:
                self.updatePitch(telemetry_data["pitch"])
                print(f"[USV_TELEMETRY] Updated pitch: {telemetry_data['pitch']:.1f}°")

            # Extract and update battery
            if (
                "battery_voltage" in telemetry_data
                or "battery_remaining" in telemetry_data
            ):
                if "battery_remaining" in telemetry_data:
                    percentage = telemetry_data["battery_remaining"]
                else:
                    # Estimate percentage from voltage (rough approximation for 12V system)
                    voltage = telemetry_data["battery_voltage"]
                    percentage = max(0, min(100, ((voltage - 11.0) / 1.6) * 100))

                self.updateBatteryLevel(percentage)
                print(f"[USV_TELEMETRY] Updated battery: {percentage:.0f}%")

            # Extract and update rudder angle (if available in servo outputs)
            # This would come from servo_output_raw or similar messages
            # For now, we'll skip this as it requires more complex parsing

            print("[USV_TELEMETRY] USVTelemetryWidget update complete")

        except Exception as e:
            print(
                f"[USV_TELEMETRY] Error in USVTelemetryWidget updateFromArduPilotData: {e}"
            )
            import traceback

            traceback.print_exc()
