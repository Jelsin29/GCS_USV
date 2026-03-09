import time
from PySide6.QtGui import QColor
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from pymavlink import mavutil

from uifolder import Ui_TargetsPage


class MissionUploadWorker(QThread):
    """Runs upload_mission() on a background thread so the Qt main thread
    remains responsive during the entire MAVLink handshake."""

    upload_finished = Signal(bool, int)  # (success, waypoint_count)

    def __init__(self, connection_thread, waypoints):
        super().__init__()
        self._connection_thread = connection_thread
        self._waypoints = waypoints

    def run(self):
        success = self._connection_thread.upload_mission(self._waypoints)
        count = len(self._waypoints) if success else 0
        self.upload_finished.emit(success, count)


class MissionStartWorker(QThread):
    """Runs start_mission() on a background thread so the Qt main thread
    remains responsive during arming + MAV_CMD_MISSION_START handshake."""

    start_finished = Signal(bool)  # success

    def __init__(self, connection_thread):
        super().__init__()
        self._connection_thread = connection_thread

    def run(self):
        success = self._connection_thread.start_mission()
        self.start_finished.emit(success)


class TargetsPage(QWidget, Ui_TargetsPage):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent

        self.antenna_tracking_active = False
        self._upload_in_progress = False
        self._upload_worker = None
        self._start_worker = None

        QTimer.singleShot(50, self.addShadowEffects)

        try:
            # Mission buttons
            self.btn_chooseMode.clicked.connect(self.buttonFunctions)
            self.btn_undo.clicked.connect(self.buttonFunctions)
            self.btn_clearAll.clicked.connect(self.buttonFunctions)
            self.btn_setMission.clicked.connect(self.set_mission)
            self.btn_antenna.clicked.connect(self.toggle_antenna_tracking)
            self.update_antenna_button_state()
            self.btn_startMission.clicked.connect(self.start_mission)
            self.btn_abort.clicked.connect(self.abort)
            self.btn_rtl.clicked.connect(self.rtl)

            # Guided Control Buttons
            self.btn_takeoff.clicked.connect(self.takeoff)
            self.btn_move.clicked.connect(self.move_to_point)
            self.btn_track_all.clicked.connect(self.track_all)
            self.btn_land.clicked.connect(self.hold_position)
            self.btn_rtl_2.clicked.connect(self.rtl_2)
            self.btn_set_roi.clicked.connect(self.set_roi)
            self.btn_cancel_roi.clicked.connect(self.cancel_roi)

            print("TargetsPage: All mission and guided control buttons connected")

        except Exception as e:
            print(f"TargetsPage: Error connecting buttons: {e}")

    def addTarget(self, image, position, time_interval, no):
        """
        Placeholder for handling detected targets from the video stream.
        This method is required by VideoStreamThread to prevent a startup crash.
        """
        target_info = f"Target {no} detected at {position}."
        print(target_info)
        self.show_mission_status(target_info, success=True)

    def buttonFunctions(self):
        if not hasattr(self, 'modes_comboBox'):
            print("Error: modes_comboBox not found.")
            return

        button = self.sender()

        if not self.parent or not hasattr(self.parent, 'homepage'):
            print("Error: Parent or homepage not available")
            return

        try:
            if button.objectName() == "btn_chooseMode":
                current_mode = self.modes_comboBox.currentText()
                print(f"Selected mode: {current_mode}")

                if current_mode == "Waypoint Mode":
                    self.parent.homepage.mapwidget.page().runJavaScript("map.off('click', moveMarkerByClick); map.off('click', drawRectangle); map.on('click', putWaypointEvent);")
                elif current_mode == "Area Selection Mode":
                    self.parent.homepage.mapwidget.page().runJavaScript("map.off('click', putWaypointEvent); map.off('click', moveMarkerByClick); map.on('click', drawRectangle);")
                else:  # Default to Marker Mode
                    self.parent.homepage.mapwidget.page().runJavaScript("map.on('click', moveMarkerByClick); map.off('click', drawRectangle); map.off('click', putWaypointEvent);")

            elif button.objectName() == "btn_clearAll":
                self.parent.homepage.mapwidget.page().runJavaScript("clearAll();")
                print("Cleared all map elements")

            elif button.objectName() == "btn_undo":
                self.parent.homepage.mapwidget.page().runJavaScript("undoWaypoint();")
                print("Undid last waypoint")

        except Exception as e:
            print(f"Error in buttonFunctions: {e}")

    def set_mission(self):
        if not self.parent or not hasattr(self.parent, 'homepage'):
            print("[MISSION ERROR] Parent or homepage not available")
            self.show_mission_status("Connection not available", success=False)
            return

        if not hasattr(self.parent, 'connectionThread'):
            print("[MISSION ERROR] MAVLink connectionThread not available")
            self.show_mission_status("MAVLink connection not available", success=False)
            return

        # Prevent multiple simultaneous uploads
        if hasattr(self, '_upload_in_progress') and self._upload_in_progress:
            print("[MISSION WARNING] Upload already in progress, ignoring duplicate request")
            self.show_mission_status("Upload already in progress...", success=False)
            return

        try:
            self._upload_in_progress = True
            current_mode = self.modes_comboBox.currentText()
            mission_type = 1 if current_mode == 'Waypoint Mode' else 0

            def upload_mission_to_vehicle(js_data_string):
                """JS callback — runs on the Qt main thread.  Parses waypoints
                and hands off to MissionUploadWorker so the main thread is
                never blocked by the MAVLink handshake."""
                if not js_data_string:
                    self.show_mission_status("No waypoints found on map. Place waypoints first!", success=False)
                    self._upload_in_progress = False
                    return

                mission_points = []
                try:
                    pairs = js_data_string.split('&')
                    for pair in pairs:
                        if ',' in pair:
                            lat, lon = map(float, pair.split(','))
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                mission_points.append([lat, lon, 0])
                            else:
                                print(f"[MISSION WARNING] Invalid coordinates: {lat}, {lon}")
                except Exception as e:
                    self.show_mission_status(f"Error parsing waypoints: {e}", success=False)
                    print(f"[MISSION ERROR] Error parsing: {e}")
                    self._upload_in_progress = False
                    return

                if not mission_points:
                    self.show_mission_status("No valid waypoints found", success=False)
                    self._upload_in_progress = False
                    return

                print(f"[MISSION] Parsed {len(mission_points)} waypoints from map")
                for i, wp in enumerate(mission_points):
                    print(f"  Waypoint {i+1}: {wp[0]:.6f}, {wp[1]:.6f}")

                connection_thread = self.parent.connectionThread
                if not hasattr(connection_thread, 'upload_mission'):
                    self.show_mission_status("Mission upload method not available", success=False)
                    self._upload_in_progress = False
                    return

                self.show_mission_status("Starting MAVLink mission upload...", success=True)
                print("[MISSION] Starting upload on background thread...")
                self._set_upload_buttons_enabled(False)

                self._upload_worker = MissionUploadWorker(connection_thread, mission_points)
                self._upload_worker.upload_finished.connect(self._on_upload_finished)
                self._upload_worker.finished.connect(self._cleanup_upload_worker)
                self._upload_worker.start()

            print("[MISSION] Getting waypoints from map...")
            self.parent.homepage.mapwidget.page().runJavaScript(f"setMission({mission_type});", 0, upload_mission_to_vehicle)

        except Exception as e:
            error_msg = f"Error in set_mission: {e}"
            print(f"[MISSION ERROR] {error_msg}")
            self.show_mission_status(error_msg, success=False)
            self._upload_in_progress = False

    def _set_upload_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable action buttons that must not run during an upload."""
        for btn_name in ('btn_takeoff', 'btn_startMission', 'btn_rtl', 'btn_rtl_2'):
            btn = getattr(self, btn_name, None)
            if btn is not None:
                btn.setEnabled(enabled)

    def _cleanup_upload_worker(self) -> None:
        """Called via finished signal after run() fully returns — safe to delete."""
        if self._upload_worker is not None:
            self._upload_worker.deleteLater()
            self._upload_worker = None

    def _cleanup_start_worker(self) -> None:
        """Called via finished signal after run() fully returns — safe to delete."""
        if self._start_worker is not None:
            self._start_worker.deleteLater()
            self._start_worker = None

    def _on_upload_finished(self, success: bool, count: int) -> None:
        """Slot called on the Qt main thread when MissionUploadWorker finishes."""
        if success:
            self.show_mission_status(f"✓ MAVLink mission uploaded: {count} waypoints", success=True)
            print(f"[MISSION SUCCESS] Uploaded {count} waypoints via MAVLink")
        else:
            self.show_mission_status("✗ MAVLink mission upload failed. Check connection and try again.", success=False)
            print("[MISSION FAILED] MAVLink upload failed")
        self._upload_in_progress = False
        self._set_upload_buttons_enabled(True)

    def start_mission(self):
        """Start the uploaded mission on a background thread.

        Runs ArdupilotConnection.start_mission() (which sends
        MAV_CMD_MISSION_START) off the Qt main thread so the UI stays
        responsive during arming and mode confirmation.
        """
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            self.show_mission_status("Connection to vehicle not active.", success=False)
            return

        if not self.parent.connectionThread.connection:
            self.show_mission_status("Vehicle not connected.", success=False)
            return

        if hasattr(self, '_start_worker') and self._start_worker and self._start_worker.isRunning():
            self.show_mission_status("Mission start already in progress...", success=False)
            return

        self.show_mission_status("Starting mission...", success=True)
        self._set_upload_buttons_enabled(False)

        self._start_worker = MissionStartWorker(self.parent.connectionThread)
        self._start_worker.start_finished.connect(self._on_start_finished)
        self._start_worker.finished.connect(self._cleanup_start_worker)
        self._start_worker.start()

    def _on_start_finished(self, success: bool) -> None:
        """Slot called on the Qt main thread when MissionStartWorker finishes."""
        if success:
            self.show_mission_status("✓ Mission started — USV in AUTO mode", success=True)
        else:
            self.show_mission_status("✗ Failed to start mission. Check connection and mission upload.", success=False)
        self._set_upload_buttons_enabled(True)

    def abort(self):
        """
        Aborts the current mission by switching the vehicle to HOLD mode.
        """
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            self.show_mission_status("Connection to vehicle not active.", success=False)
            return

        try:
            print("Aborting mission, switching to HOLD mode...")
            if self.parent.connectionThread.connection:
                success = self.parent.connectionThread.set_mode('HOLD')
                if success:
                    msg = "HOLD mode command sent. Mission aborted."
                    self.show_mission_status(msg, success=True)
                else:
                    msg = "Failed to set HOLD mode — vehicle may still be executing mission."
                    self.show_mission_status(msg, success=False)
                print(msg)
            else:
                msg = "Error: Vehicle not connected."
                print(msg)
                self.show_mission_status(msg, success=False)
        except Exception as e:
            error_msg = f"Failed to abort mission: {e}"
            print(error_msg)
            self.show_mission_status(error_msg, success=False)

    def rtl(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
        try:
            if self.parent.connectionThread.connection:
                self.parent.connectionThread.set_mode('RTL')
                print("Return to Launch (RTL) mode activated")
            else:
                print("Warning: Connection not available")
        except Exception as e:
            print(f"Error activating RTL mode: {e}")

    def takeoff(self):
        """
        Arms the vehicle and prepares it for a mission by setting it to GUIDED mode.
        This is the USV equivalent of aircraft takeoff.
        """
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            self.show_mission_status("Connection not available", success=False)
            return

        try:
            print("[TAKEOFF] Starting USV takeoff sequence (Arm + GUIDED)...")

            connection_thread = self.parent.connectionThread

            if hasattr(connection_thread, 'arm_and_start'):
                print("[TAKEOFF] Using arm_and_start method...")
                success = connection_thread.arm_and_start()
                if success:
                    self.show_mission_status("✓ USV Armed and Ready for Mission", success=True)
                    print("[TAKEOFF SUCCESS] USV is armed and in GUIDED mode")
                else:
                    self.show_mission_status("✗ Failed to arm USV", success=False)
                    print("[TAKEOFF FAILED] Could not arm USV")

            elif hasattr(connection_thread, 'arm_vehicle'):
                print("[TAKEOFF] Using fallback arm_vehicle method...")
                success = connection_thread.arm_vehicle()
                if success:
                    if connection_thread.set_mode('GUIDED'):
                        self.show_mission_status("✓ USV Armed and in GUIDED mode", success=True)
                    else:
                        self.show_mission_status("✓ USV Armed (manual mode set required)", success=True)
                else:
                    self.show_mission_status("✗ Failed to arm USV", success=False)

            elif hasattr(connection_thread, 'connection') and connection_thread.connection:
                print("[TAKEOFF] Using direct MAVLink arm command...")
                connection = connection_thread.connection

                connection.mav.command_long_send(
                    connection.target_system,
                    connection.target_component,
                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                    0,
                    1,
                    0,
                    0, 0, 0, 0, 0
                )

                connection_thread.set_mode('GUIDED')
                self.show_mission_status("✓ Arm and GUIDED commands sent", success=True)
                print("[TAKEOFF] Direct commands sent - check vehicle status")

            else:
                self.show_mission_status("✗ No arm method available", success=False)
                print("[TAKEOFF ERROR] No arming method available")

        except Exception as e:
            error_msg = f"Takeoff error: {e}"
            self.show_mission_status(error_msg, success=False)
            print(f"[TAKEOFF ERROR] {error_msg}")
            import traceback
            traceback.print_exc()

    def show_mission_status(self, message, success=True):
        """Display mission status in console"""
        try:
            if hasattr(self, 'textBrowser'):
                color = "green" if success else "red"
                status = "SUCCESS" if success else "ERROR"
                timestamp = time.strftime("%H:%M:%S")
                self.textBrowser.append(f'<span style="color: {color};">[{timestamp}] {status}: {message}</span>')
                print(f"[MISSION STATUS] {message}")
            else:
                print(f"[MISSION STATUS] {message}")
        except Exception as e:
            print(f"Error showing mission status: {e}")
            print(f"[MISSION STATUS] {message}")

    # --- Other Methods (Antenna Tracking, Guided Control, UI Effects) ---

    def toggle_antenna_tracking(self):
        if not self.antenna_tracking_active:
            self.start_antenna_tracking()
        else:
            self.stop_antenna_tracking()

    def start_antenna_tracking(self):
        try:
            import threading
            from AntennaTracker import AntennaTracker, antenna_tracker
            antenna = AntennaTracker(-35.3635, 149.1652)
            lat, lon = antenna.get_location()
            if self.parent and hasattr(self.parent, 'homepage'):
                self.parent.homepage.mapwidget.page().runJavaScript(f"var homeMarker = L.marker([{lat}, {lon}], {{icon: homeIcon,}}).addTo(map);")
            threading.Thread(target=antenna_tracker, args=(antenna, self.parent.connectionThread)).start()
            self.antenna_tracking_active = True
            self.update_antenna_button_state()
            print("Antenna tracking started.")
        except Exception as e:
            print(f"Error starting antenna tracker: {e}")

    def stop_antenna_tracking(self):
        try:
            self.antenna_tracking_active = False
            self.update_antenna_button_state()
            print("Antenna tracking stopped.")
        except Exception as e:
            print(f"Error stopping antenna tracker: {e}")

    def update_antenna_button_state(self):
        if hasattr(self, 'btn_antenna'):
            if self.antenna_tracking_active:
                self.btn_antenna.setProperty("tracking", "true")
                self.btn_antenna.setText("STOP TRACKING")
            else:
                self.btn_antenna.setProperty("tracking", "false")
                self.btn_antenna.setText("ANTENNA TRACKING")
            self.btn_antenna.style().unpolish(self.btn_antenna)
            self.btn_antenna.style().polish(self.btn_antenna)

    def move_to_point(self):
        if not (self.parent and hasattr(self.parent, 'connectionThread')):
            print("Error: connectionThread not available")
            return
        try:
            mapwidget = self.parent.homepage.mapwidget
            mapwidget.page().runJavaScript("getMarkerPosition()", self._on_marker_position)
        except Exception as e:
            print(f"Error getting marker position: {e}")

    def _on_marker_position(self, result):
        if result is None:
            self.show_mission_status("No marker placed. Click the map in Marker Mode first.", success=False)
            return
        try:
            lat, lon = map(float, str(result).split(','))
            print(f"Move to marker: Lat {lat}, Lon {lon}")
            self.parent.connectionThread.goto_markers_pos(lat, lon)
        except Exception as e:
            print(f"Error parsing marker position '{result}': {e}")

    def track_all(self):
        if self.parent and hasattr(self.parent, 'homepage') and hasattr(self.parent.homepage, 'cameraWidget'):
            self.parent.homepage.cameraWidget.videothread.sendMessage("track -1")
            print("Track all command sent")
        else:
            print("Warning: Camera widget not available")

    def hold_position(self):
        """
        Commands the USV to hold its current position using HOLD mode.
        """
        if self.parent and hasattr(self.parent, 'connectionThread'):
            print("[HOLD] Commanding USV to hold position...")
            self.parent.connectionThread.set_mode('HOLD')
            self.show_mission_status("✓ USV is now holding its position.", success=True)
        else:
            self.show_mission_status("✗ Connection not available.", success=False)

    def rtl_2(self):
        self.rtl()

    def set_roi(self):
        if self.parent and hasattr(self.parent, 'connectionThread'):
            self.parent.connectionThread.set_roi()
            print("Set ROI command sent")
        else:
            print("Error: connectionThread not available")

    def cancel_roi(self):
        if self.parent and hasattr(self.parent, 'connectionThread'):
            self.parent.connectionThread.cancel_roi_mode()
            print("Cancel ROI command sent")
        else:
            print("Error: connectionThread not available")

    def addShadowEffects(self):
        try:
            self.addFrameShadow(self.missionFrame)
            self.addFrameShadow(self.guidedFrame)
            self.addFrameShadow(self.consoleFrame, blur=25, offset_y=6)
            important_buttons = ['btn_startMission', 'btn_abort', 'btn_antenna', 'btn_takeoff', 'btn_land', 'btn_rtl', 'btn_rtl_2']
            for button_name in important_buttons:
                if hasattr(self, button_name):
                    self.addButtonShadow(getattr(self, button_name))
            print("TargetsPage: Shadow effects applied.")
        except Exception as e:
            print(f"TargetsPage: Error applying shadow effects: {e}")

    def addFrameShadow(self, frame, blur=20, offset_y=4):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(0)
        shadow.setYOffset(offset_y)
        shadow.setColor(QColor(0, 0, 0, 40))
        frame.setGraphicsEffect(shadow)

    def addButtonShadow(self, button):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        button.setGraphicsEffect(shadow)
