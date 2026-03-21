import sys
import threading
import serial.tools.list_ports

from PySide6 import QtGui
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QEvent, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSizePolicy,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)

from HomePage import HomePage
from uifolder import Ui_MainWindow
from TargetsPage import TargetsPage
from IndicatorsPage import IndicatorsPage
from ConnectionManager import ConnectionManager
from TelemetryLogger import TelemetryLogger
from AntennaTracker import AntennaTracker, antenna_tracker
from Vehicle.ArdupilotConnection import ArdupilotConnectionThread


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, firebase=None):
        super().__init__()
        self.setupUi(self)

        self.firebase = firebase

        # Frameless Window
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set initial windows size
        self.state = 0  # maximized or not
        self.screenSize = QApplication.primaryScreen().size()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        width = self.screenSize.width() * 0.8
        height = self.screenSize.height() * 0.8
        self.resize(width, height)

        # Move Window to Center
        self.move(
            self.screenSize.width() / 2 - self.width() / 2,
            self.screenSize.height() / 2 - self.height() / 2,
        )

        # Set Font
        QtGui.QFontDatabase.addApplicationFont("uifolder/assets/fonts/segoeui.ttf")
        QtGui.QFontDatabase.addApplicationFont("uifolder/assets/fonts/segoeuib.ttf")

        # Sizegrip (To Resize Window)
        self.sizegrip = QSizeGrip(self.frame_size_grip)
        self.sizegrip.setStyleSheet(
            "background-image: url(uifolder/assets/icons/16x16/cil-size-grip.png);"
            "width: 20px; height: 20px; margin 0px; padding 0px;"
        )

        # Set Initial Baud Rate to Combobox
        self.combobox_baudrate.setCurrentText("115200")

        # Enhanced serial port detection
        self.update_serial_ports()

        # Set up connection status indicator
        self.connection_status_label = None  # Will be set if exists in UI

        # Setting Pages
        self.targetspage = TargetsPage(self)
        self.homepage = HomePage(self)
        self.indicatorspage = IndicatorsPage()

        # **NEW: Initialize telemetry widgets with proper disconnected state**
        # Make sure HomePage TelemetryWidget starts disconnected
        if hasattr(self.homepage, "telemetryWidget"):
            self.homepage.telemetryWidget.setConnectionStatus(False)
            print("MainWindow: HomePage TelemetryWidget initialized - disconnected")

        # Make sure IndicatorsPage starts with zero values
        if hasattr(self.indicatorspage, "resetForArduPilot"):
            self.indicatorspage.resetForArduPilot()
            print("MainWindow: IndicatorsPage initialized - zero values")
        self.indicatorswidget = QWidget(layout=QVBoxLayout())
        self.indicatorswidget.layout().addWidget(self.indicatorspage)
        self.stackedWidget.addWidget(self.homepage)
        self.stackedWidget.addWidget(self.targetspage)
        self.stackedWidget.addWidget(self.indicatorswidget)
        self.stackedWidget.setCurrentWidget(self.homepage)

        # Connection Thread (USV — existing, untouched)
        self.connectionThread = ArdupilotConnectionThread(self)

        # Dual Connection Manager (adds drone connection alongside USV)
        self.connection_manager = ConnectionManager(
            usv_connection_thread=self.connectionThread, parent=self
        )
        self._setup_drone_ui()

        # Telemetry Logger (CSV recording for competition deliverables)
        self.telemetry_logger = TelemetryLogger(output_dir="logs", parent=self)

        #  SET BUTTONS
        #  Main Window buttons
        self.btn_close.setIcon(QtGui.QIcon("uifolder/assets/icons/16x16/cil-x.png"))
        self.btn_close.clicked.connect(self.close)
        self.btn_maximize_restore.setIcon(
            QtGui.QIcon("uifolder/assets/icons/16x16/cil-window-maximize.png")
        )
        self.btn_maximize_restore.clicked.connect(self.maximize_restore)
        self.btn_minimize.setIcon(
            QtGui.QIcon("uifolder/assets/icons/16x16/cil-window-minimize.png")
        )
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())

        self.btn_home_page.setDisabled(True)
        self.disabledbutton = self.btn_home_page
        self.setButton(self.btn_toggle_menu, "uifolder/assets/icons/24x24/cil-menu.png")
        self.setButton(self.btn_home_page, "uifolder/assets/icons/24x24/cil-home.png")
        self.setButton(
            self.btn_indicators_page, "uifolder/assets/icons/24x24/cil-speedometer.png"
        )
        self.setButton(
            self.btn_targets_page, "uifolder/assets/icons/24x24/cil-user.png"
        )
        self.btn_connect.setIcon(
            QtGui.QIcon("uifolder/assets/icons/24x24/cil-link-broken.png")
        )

        # **UPDATED: Main Connection Button**
        self.btn_connect.clicked.connect(self.connectToVehicle)

        # **UPDATED: HomePage Guidance Buttons (only if they exist)**
        # These are the buttons that might still be on HomePage for guided control
        if hasattr(self.homepage, "btn_set_roi"):
            self.homepage.btn_set_roi.clicked.connect(self.connectionThread.set_roi)
        if hasattr(self.homepage, "btn_cancel_roi"):
            self.homepage.btn_cancel_roi.clicked.connect(
                self.connectionThread.cancel_roi_mode
            )
        if hasattr(self.homepage, "btn_move"):
            self.homepage.btn_move.clicked.connect(
                self.connectionThread.goto_markers_pos
            )
        if hasattr(self.homepage, "btn_takeoff"):
            self.homepage.btn_takeoff.clicked.connect(self.takeoff)
        if hasattr(self.homepage, "btn_land"):
            self.homepage.btn_land.clicked.connect(self.connectionThread.land)
        if hasattr(self.homepage, "btn_rtl"):
            self.homepage.btn_rtl.clicked.connect(lambda: self.connectionThread.rtl())
        if hasattr(self.homepage, "btn_rtl_2"):
            self.homepage.btn_rtl_2.clicked.connect(self.connectionThread.rtl)
        if hasattr(self.homepage, "btn_track_all"):
            self.homepage.btn_track_all.clicked.connect(self.track_all)

        # **REMOVED: Mission control buttons - now handled in TargetsPage**
        # These buttons have been moved to TargetsPage (Mission Control)
        # if hasattr(self.homepage, 'btn_abort'):
        #     self.homepage.btn_abort.clicked.connect(self.abort)
        # if hasattr(self.homepage, 'btn_startMission'):
        #     self.homepage.btn_startMission.clicked.connect(self.connectionThread.start_mission)
        # if hasattr(self.homepage, 'btn_antenna'):
        #     self.homepage.btn_antenna.clicked.connect(self.run_antenna_tracker)

        # Button to Allocate Windows
        self.indicatorspage.btn_AllocateWidget.clicked.connect(
            lambda: self.AllocateWidget(self.indicatorswidget, self.indicatorspage)
        )

        # To move the window only from top frame
        self.label_title_bar_top.installEventFilter(self)

    #########################################################################################################################

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    # To take events from child widgets
    def eventFilter(self, obj, event):
        if obj == self.label_title_bar_top:
            # Maximize and restore when double click
            if event.type() == QEvent.MouseButtonDblClick:
                self.maximize_restore()
            # Drag move window
            if event.type() == QEvent.MouseMove:
                if event.buttons() == Qt.LeftButton:
                    self.setCursor(Qt.SizeAllCursor)
                    self.move(
                        self.pos() + event.globalPosition().toPoint() - self.dragPos
                    )
                    self.dragPos = event.globalPosition().toPoint()
                    return True
            if event.type() == QEvent.MouseButtonRelease:
                self.setCursor(Qt.ArrowCursor)
        return super().eventFilter(obj, event)

    def setButton(self, button, icon):
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QSize(0, 70))
        button.setLayoutDirection(Qt.LeftToRight)
        button.setIcon(QtGui.QIcon(icon))
        button.clicked.connect(self.buttonFunctions)

    def _setup_drone_ui(self):
        """Set up drone connection UI elements if they exist in the .ui file.

        If the UI doesn't have drone-specific widgets yet, this creates
        programmatic fallbacks so drone connection still works via code.
        """
        # Wire drone signals from ConnectionManager
        self.connection_manager.drone_connected.connect(self._on_drone_connected)
        self.connection_manager.drone_disconnected.connect(self._on_drone_disconnected)
        self.connection_manager.drone_position_updated.connect(
            self._on_drone_position_updated
        )
        self.connection_manager.drone_target_detected.connect(
            self._on_drone_target_detected
        )
        self.connection_manager.drone_error.connect(
            lambda msg: print(f"[DRONE UI] Error: {msg}")
        )

        # Check if drone UI widgets exist (from .ui file)
        # If not, drone can still be connected programmatically
        self._drone_ui_available = hasattr(self, "btn_connect_drone")
        if self._drone_ui_available:
            self.btn_connect_drone.clicked.connect(self.connectToDrone)
            if hasattr(self, "combobox_drone_port"):
                # Populate drone serial port dropdown
                ports = serial.tools.list_ports.comports()
                for port in ports:
                    if port.device:
                        self.combobox_drone_port.addItem(port.device)

    def connectToDrone(self):
        """Connect or disconnect from the drone."""
        if self.connection_manager.drone_connected_status:
            self.connection_manager.disconnect_drone()
            if self._drone_ui_available:
                self.btn_connect_drone.setText("Connect Drone")
        else:
            port = ""
            if hasattr(self, "combobox_drone_port"):
                port = self.combobox_drone_port.currentText()
            if not port:
                from PySide6.QtWidgets import QInputDialog

                port, ok = QInputDialog.getText(
                    self,
                    "Drone Connection",
                    "Enter drone serial port (e.g. /dev/ttyUSB1):",
                )
                if not ok or not port:
                    return
            self.connection_manager.connect_drone(port)

    def _on_drone_connected(self):
        """Handle drone connection established."""
        print("[DRONE UI] Drone connected")
        if self._drone_ui_available:
            self.btn_connect_drone.setText("Disconnect Drone")

    def _on_drone_disconnected(self):
        """Handle drone disconnection."""
        print("[DRONE UI] Drone disconnected")
        if self._drone_ui_available:
            self.btn_connect_drone.setText("Connect Drone")

    def _on_drone_position_updated(self, lat: float, lon: float, alt: float):
        """Update drone marker on map."""
        if hasattr(self, "homepage") and hasattr(self.homepage, "mapwidget"):
            mapwidget = self.homepage.mapwidget
            # Add or update drone marker on map
            js = (
                f"if (typeof droneMarker === 'undefined') {{"
                f"  droneMarker = L.circleMarker([{lat}, {lon}], "
                f"    {{radius: 8, color: '#FF4444', fillColor: '#FF4444', "
                f"     fillOpacity: 0.8}}).addTo({mapwidget.map_variable_name});"
                f"  droneMarker.bindTooltip('Drone', {{permanent: true, direction: 'top'}});"
                f"}} else {{"
                f"  droneMarker.setLatLng([{lat}, {lon}]);"
                f"}}"
            )
            mapwidget.page().runJavaScript(js)

    def _on_drone_target_detected(self, color: str, lat: float, lon: float):
        """Handle target detection from drone — display on map and relay to USV."""
        print(f"[DRONE UI] TARGET DETECTED: {color} at ({lat}, {lon})")
        # Show target marker on map
        if hasattr(self, "homepage") and hasattr(self.homepage, "mapwidget"):
            color_hex = {"RED": "#FF0000", "GREEN": "#00FF00", "BLUE": "#0000FF"}.get(
                color, "#FFFF00"
            )
            mapwidget = self.homepage.mapwidget
            js = (
                f"L.circleMarker([{lat}, {lon}], "
                f"  {{radius: 12, color: '{color_hex}', fillColor: '{color_hex}', "
                f"   fillOpacity: 0.9}}).addTo({mapwidget.map_variable_name})"
                f"  .bindTooltip('Target: {color}', {{permanent: true}});"
            )
            mapwidget.page().runJavaScript(js)

        # Relay to USV
        self.connection_manager.relay_target_to_usv(color, lat, lon)

    def closeEvent(self, event):
        if hasattr(self, "telemetry_logger"):
            self.telemetry_logger.stop()
        if hasattr(self, "connection_manager"):
            self.connection_manager.shutdown()
        if hasattr(self, "connectionThread") and self.connectionThread.isRunning():
            self.connectionThread.stop()
            self.connectionThread.wait(3000)
        event.accept()

    def maximize_restore(self):
        if self.state == 1:
            self.btn_maximize_restore.setToolTip("Maximize")
            self.btn_maximize_restore.setIcon(
                QtGui.QIcon("uifolder/assets/icons/16x16/cil-window-maximize.png")
            )
            self.showNormal()
            self.state = 0
        else:
            self.btn_maximize_restore.setToolTip("Restore")
            self.btn_maximize_restore.setIcon(
                QtGui.QIcon("uifolder/assets/icons/16x16/cil-window-restore.png")
            )
            self.showMaximized()
            self.state = 1

    def buttonFunctions(self):
        button = self.sender()
        # Toggle Button
        if button.objectName() == "btn_toggle_menu":
            width = self.frame_left_menu.width()
            maxWidth = 240
            standard = 70

            # SET MAX WIDTH
            if width == standard:
                widthExtended = maxWidth
                # Show text labels when expanded
                self.btn_home_page.setText("    Home")
                self.btn_indicators_page.setText("   Indicators")
                self.btn_targets_page.setText("   Mission Control")
                # Change icon to indicate menu can be collapsed
                self.btn_toggle_menu.setIcon(
                    QtGui.QIcon("uifolder/assets/icons/24x24/cil-x.png")
                )
            else:
                widthExtended = standard
                # Hide text labels when collapsed
                self.btn_home_page.setText("")
                self.btn_indicators_page.setText("")
                self.btn_targets_page.setText("")
                # Change icon back to menu
                self.btn_toggle_menu.setIcon(
                    QtGui.QIcon("uifolder/assets/icons/24x24/cil-menu.png")
                )

            # ANIMATION for smooth width transition
            self.animation = QPropertyAnimation(self.frame_left_menu, b"minimumWidth")
            self.animation.setDuration(300)  # Slightly longer for smoother feel
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

            # Also animate maximum width for better control
            self.animation2 = QPropertyAnimation(self.frame_left_menu, b"maximumWidth")
            self.animation2.setDuration(300)
            self.animation2.setStartValue(width)
            self.animation2.setEndValue(widthExtended)
            self.animation2.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation2.start()

        else:
            # Handle page navigation buttons
            self.disabledbutton.setDisabled(False)
            self.disabledbutton = button
            self.disabledbutton.setDisabled(True)

        # PAGE HOME
        if button.objectName() == "btn_home_page":
            self.stackedWidget.setCurrentWidget(self.homepage)

        # PAGE INDICATORS
        if button.objectName() == "btn_indicators_page":
            self.stackedWidget.setCurrentWidget(self.indicatorswidget)

        # PAGE MISSION CONTROL (formerly Targets)
        if button.objectName() == "btn_targets_page":
            self.stackedWidget.setCurrentWidget(self.targetspage)

    def update_serial_ports(self):
        """Update the connection string combobox with available serial ports"""
        # Clear current items except for network options
        network_options = ["SITL (UDP)", "SITL (TCP)", "MAVROS Direct", "UDP", "TCP"]

        # Clear and add network options
        self.combobox_connectionstring.clear()
        for option in network_options:
            self.combobox_connectionstring.addItem(option)

        # Add detected serial ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.device:
                self.combobox_connectionstring.addItem(port.device)

        # Set default to first serial port if available, otherwise SITL
        if ports:
            self.combobox_connectionstring.setCurrentText(ports[0].device)
        else:
            # Default to SITL if no serial ports found
            self.combobox_connectionstring.setCurrentText("SITL (UDP)")

    def setup_connection_signals(self):
        """Connect signals from the connection thread to UI handlers."""
        try:
            if hasattr(self.connectionThread, "connection_status"):
                self.connectionThread.connection_status.connect(
                    self.on_connection_status_changed
                )
            if hasattr(self.connectionThread, "telemetry_update"):
                self.connectionThread.telemetry_update.connect(self.on_telemetry_update)
                self.connectionThread.telemetry_update.connect(
                    self.telemetry_logger.log
                )
            if hasattr(self.connectionThread, "mission_status"):
                self.connectionThread.mission_status.connect(
                    self.on_mission_status_changed
                )
        except Exception as e:
            print(f"ERROR setting up connection signals: {e}")

    def on_connection_status_changed(self, connected, message):
        """Handle connection status changes from the connection thread signal."""
        if connected:
            self.btn_connect.setText("Disconnect")
            self.btn_connect.setIcon(
                QtGui.QIcon("uifolder/assets/icons/24x24/cil-wifi.png")
            )
            self._set_all_widgets_connection_status(True)
            if hasattr(self, "indicatorspage") and hasattr(
                self.indicatorspage, "switchToRealDataMode"
            ):
                self.indicatorspage.switchToRealDataMode()
            # Auto-start telemetry recording on connection
            if (
                hasattr(self, "telemetry_logger")
                and not self.telemetry_logger.is_recording
            ):
                self.telemetry_logger.start()
        else:
            self.btn_connect.setText("Connect")
            self.btn_connect.setIcon(
                QtGui.QIcon("uifolder/assets/icons/24x24/cil-link-broken.png")
            )
            self._set_all_widgets_connection_status(False)
            if hasattr(self, "indicatorspage") and hasattr(
                self.indicatorspage, "onConnectionLost"
            ):
                self.indicatorspage.onConnectionLost()
            # Auto-stop telemetry recording on disconnection
            if hasattr(self, "telemetry_logger") and self.telemetry_logger.is_recording:
                self.telemetry_logger.stop()

        if hasattr(self, "connection_status_label") and self.connection_status_label:
            self.connection_status_label.setText(message)

    def on_mission_status_changed(self, message, success):
        """Handle mission status updates"""
        status_text = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"[MISSION STATUS] {status_text}: {message}")

        # Update UI status if available
        if hasattr(self, "mission_status_label") and self.mission_status_label:
            self.mission_status_label.setText(f"{status_text}: {message}")

        # You can add more UI updates here, like:
        # - Updating mission progress bar
        # - Showing success/failure dialogs
        # - Enabling/disabling mission buttons
        # - Updating mission list display

    def on_telemetry_update(self, telemetry_data):
        """Route incoming telemetry data to all registered UI widgets."""
        connection_running = (
            hasattr(self.connectionThread, "is_running")
            and self.connectionThread.is_running
        )
        if not connection_running:
            return

        try:
            # Update map marker when GPS data arrives
            if "latitude" in telemetry_data and "longitude" in telemetry_data:
                self._update_map_position(
                    telemetry_data["latitude"],
                    telemetry_data["longitude"],
                    telemetry_data.get("heading", 0),
                )

            # Convert to VRX format for widgets that expect that structure
            vrx_data = self.convert_telemetry_to_vrx_format(telemetry_data)

            # Forward to HomePage TelemetryWidget
            if hasattr(self, "homepage") and hasattr(self.homepage, "telemetryWidget"):
                telemetry_widget = self.homepage.telemetryWidget
                if hasattr(telemetry_widget, "updateFromArduPilotData"):
                    telemetry_widget.updateFromArduPilotData(telemetry_data)
                elif hasattr(telemetry_widget, "updateFromVRXData"):
                    telemetry_widget.updateFromVRXData(vrx_data)
                elif hasattr(telemetry_widget, "process_telemetry"):
                    telemetry_widget.process_telemetry(vrx_data)

            # Forward to IndicatorsPage USV Telemetry Widget
            if hasattr(self, "indicatorspage") and hasattr(
                self.indicatorspage, "usv_telemetry"
            ):
                usv_widget = self.indicatorspage.usv_telemetry
                if hasattr(usv_widget, "updateFromArduPilotData"):
                    usv_widget.updateFromArduPilotData(telemetry_data)
                elif hasattr(usv_widget, "updateFromVRXData"):
                    usv_widget.updateFromVRXData(vrx_data)
                elif hasattr(usv_widget, "process_telemetry"):
                    usv_widget.process_telemetry(vrx_data)

            # Also update IndicatorsPage main instruments
            if hasattr(self, "indicatorspage") and hasattr(
                self.indicatorspage, "updateFromArduPilotData"
            ):
                self.indicatorspage.updateFromArduPilotData(telemetry_data)

        except Exception as e:
            print(f"ERROR in telemetry update: {e}")

    def _update_map_position(self, lat: float, lon: float, heading: float) -> None:
        """Update the USV marker on the map. Runs on the Qt main thread."""
        try:
            if not (hasattr(self, "homepage") and hasattr(self.homepage, "mapwidget")):
                return
            if lat == 0.0 and lon == 0.0:
                return

            mapwidget = self.homepage.mapwidget
            position = [lat, lon]
            ct = self.connectionThread

            if not ct.usv_marker_created:
                mapwidget.page().runJavaScript(
                    f"{mapwidget.map_variable_name}.flyTo({position}, 16)"
                )
                mapwidget.page().runJavaScript(f"""
                    if (typeof usvMarker !== 'undefined') {{ map.removeLayer(usvMarker); }}
                    usvMarker = L.marker({position}, {{icon: usvIcon, rotationAngle: {heading - 45}}}).addTo(map);
                """)
                ct.usv_marker_created = True
                print(f"[MAP] USV marker created at {lat:.6f}, {lon:.6f}")
            else:
                mapwidget.page().runJavaScript(f"usvMarker.setLatLng({position});")
                mapwidget.page().runJavaScript(
                    f"usvMarker.setRotationAngle({heading - 45});"
                )
        except Exception as e:
            print(f"[MAP] Error updating marker: {e}")

    def convert_telemetry_to_vrx_format(self, telemetry_data):
        """Convert flat ArduPilot telemetry dict to nested VRX/MAVLink-style format."""
        if not telemetry_data:
            return {}

        vrx_format = {}

        try:
            # GPS Position — convert decimal degrees to int32 (1e7 scale)
            if "latitude" in telemetry_data and "longitude" in telemetry_data:
                vrx_format["global_position_int"] = {
                    "lat": int(telemetry_data["latitude"] * 1e7),
                    "lon": int(telemetry_data["longitude"] * 1e7),
                    "alt": int(telemetry_data.get("altitude", 0) * 1000),
                    "relative_alt": int(telemetry_data.get("relative_alt", 0) * 1000),
                }

            # Attitude (values in degrees from ArdupilotConnection)
            if (
                "roll" in telemetry_data
                or "pitch" in telemetry_data
                or "yaw" in telemetry_data
            ):
                vrx_format["attitude"] = {
                    "roll": telemetry_data.get("roll", 0),
                    "pitch": telemetry_data.get("pitch", 0),
                    "yaw": telemetry_data.get("yaw", 0),
                    "rollspeed": telemetry_data.get("rollspeed", 0),
                    "pitchspeed": telemetry_data.get("pitchspeed", 0),
                    "yawspeed": telemetry_data.get("yawspeed", 0),
                }

            # VFR HUD
            if "groundspeed" in telemetry_data or "heading" in telemetry_data:
                vrx_format["vfr_hud"] = {
                    "airspeed": telemetry_data.get("airspeed", 0),
                    "groundspeed": telemetry_data.get("groundspeed", 0),
                    "heading": telemetry_data.get("heading", 0),
                    "throttle": telemetry_data.get("throttle", 0),
                    "alt": telemetry_data.get("altitude", 0),
                    "climb": telemetry_data.get("climb_rate", 0),
                }

            # Heartbeat / mode
            if "armed" in telemetry_data or "mode" in telemetry_data:
                vrx_format["heartbeat"] = {
                    "base_mode": 1 if telemetry_data.get("armed", False) else 0,
                    "custom_mode": telemetry_data.get("mode", "MANUAL"),
                    "system_status": telemetry_data.get("system_status", 3),
                }

            # Battery
            if (
                "battery_voltage" in telemetry_data
                or "battery_current" in telemetry_data
            ):
                vrx_format["battery_status"] = {
                    "voltages": [int(telemetry_data.get("battery_voltage", 0) * 1000)]
                    + [0] * 9,
                    "current_battery": int(
                        telemetry_data.get("battery_current", 0) * 100
                    ),
                    "current_consumed": telemetry_data.get("battery_consumed", -1),
                    "energy_consumed": -1,
                    "battery_remaining": telemetry_data.get("battery_remaining", -1),
                }

            return vrx_format

        except Exception as e:
            print(f"Error converting telemetry to VRX format: {e}")
            return {}

    def convert_telemetry_to_mavlink_format(self, telemetry_data):
        """Convert telemetry data to MAVLink format expected by IndicatorsPage"""
        mavlink_format = {}

        try:
            # GPS Position
            if "latitude" in telemetry_data and "longitude" in telemetry_data:
                mavlink_format["global_position_int"] = {
                    "lat": int(telemetry_data["latitude"] * 1e7),
                    "lon": int(telemetry_data["longitude"] * 1e7),
                    "alt": int(telemetry_data.get("altitude", 0) * 1000),
                    "hdg": int(telemetry_data.get("heading", 0) * 100),
                }

            # VFR HUD data
            if "groundspeed" in telemetry_data:
                mavlink_format["vfr_hud"] = {
                    "groundspeed": telemetry_data["groundspeed"],
                    "heading": telemetry_data.get("heading", 0),
                    "throttle": telemetry_data.get("throttle", 0),
                    "alt": telemetry_data.get("altitude", 0),
                    "climb": telemetry_data.get("climb_rate", 0),
                }

            # Attitude
            if "roll" in telemetry_data:
                mavlink_format["attitude"] = {
                    "roll": telemetry_data["roll"] * 0.0174533,  # Convert deg to rad
                    "pitch": telemetry_data.get("pitch", 0) * 0.0174533,
                    "yaw": telemetry_data.get("yaw", 0) * 0.0174533,
                    "rollspeed": 0,
                    "pitchspeed": 0,
                    "yawspeed": 0,
                }

            # System status
            if "voltage_battery" in telemetry_data:
                mavlink_format["sys_status"] = {
                    "voltage_battery": int(
                        telemetry_data["voltage_battery"] * 1000
                    ),  # Convert to mV
                    "current_battery": int(
                        telemetry_data.get("current_battery", 0) * 100
                    ),  # Convert to cA
                    "battery_remaining": telemetry_data.get("battery_remaining", 0),
                }

            # Heartbeat
            if "mode" in telemetry_data:
                mode_mapping = {
                    "MANUAL": 0,
                    "ACRO": 1,
                    "STEERING": 3,
                    "HOLD": 4,
                    "LOITER": 5,
                    "FOLLOW": 6,
                    "SIMPLE": 7,
                    "AUTO": 10,
                    "RTL": 11,
                    "SMART_RTL": 12,
                    "GUIDED": 15,
                }
                mode_name = (
                    telemetry_data["mode"].replace("UNKNOWN(", "").replace(")", "")
                )
                custom_mode = mode_mapping.get(mode_name, 0)

                mavlink_format["heartbeat"] = {
                    "type": 10,  # MAV_TYPE_GROUND_ROVER
                    "autopilot": 3,  # MAV_AUTOPILOT_ARDUPILOTMEGA
                    "base_mode": 1 if telemetry_data.get("armed", False) else 0,
                    "custom_mode": custom_mode,
                    "system_status": telemetry_data.get("system_status", 4),
                }

        except Exception as e:
            print(f"Error converting telemetry to MAVLink format: {e}")

        return mavlink_format

    def connectToVehicle(self):
        """Connect or disconnect from the vehicle."""
        if (
            hasattr(self.connectionThread, "connection")
            and self.connectionThread.connection
        ):
            # Disconnect
            self._set_all_widgets_connection_status(False)
            self.connectionThread.stop()
            self.connectionThread.wait(5000)
            self.btn_connect.setText("Connect")
            self.btn_connect.setIcon(
                QtGui.QIcon("uifolder/assets/icons/24x24/cil-link-broken.png")
            )
        else:
            # Connect
            self.connectionThread.setBaudRate(int(self.combobox_baudrate.currentText()))
            self.connectionThread.setConnectionString(
                self.combobox_connectionstring.currentText()
            )
            if not hasattr(self, "_signals_connected"):
                self.setup_connection_signals()
                self._signals_connected = True
            # Widgets are set to connected via the connection_status signal on success
            self.connectionThread.start()

    def _set_all_widgets_connection_status(self, connected: bool) -> None:
        """Update connection status on all telemetry widgets."""
        if hasattr(self, "homepage") and hasattr(self.homepage, "telemetryWidget"):
            widget = self.homepage.telemetryWidget
            if hasattr(widget, "setConnectionStatus"):
                widget.setConnectionStatus(connected)
        if hasattr(self, "indicatorspage") and hasattr(
            self.indicatorspage, "usv_telemetry"
        ):
            usv = self.indicatorspage.usv_telemetry
            if hasattr(usv, "setConnectionStatus"):
                usv.setConnectionStatus(connected)

    def takeoff(self):
        """Arm the USV and prepare for mission (takeoff equivalent for USV)"""
        try:
            if self.connectionThread and self.connectionThread.connection:
                print("🚤 ARM button pressed - Arming USV...")
                result = self.connectionThread.arm_and_start()
                if result:
                    print("✅ USV armed successfully!")
                else:
                    print("❌ Failed to arm USV")
            else:
                print("❌ No connection to vehicle")
        except Exception as e:
            print(f"❌ Error during arm operation: {e}")

    # **MOVED: These methods are now available but might be called from TargetsPage**
    def run_antenna_tracker(self):
        antenna = AntennaTracker(-35.3635, 149.1652)
        lat, lon = antenna.get_location()
        # Add home marker
        self.homepage.mapwidget.page().runJavaScript(
            """
                        var homeMarker = L.marker(
                                    %s,
                                    {icon: homeIcon,},).addTo(map);
                        """
            % [lat, lon]
        )

        threading.Thread(
            target=antenna_tracker, args=(antenna, self.connectionThread)
        ).start()
        # **UPDATED: Now disable the button on TargetsPage instead of HomePage**
        if hasattr(self.targetspage, "btn_antenna"):
            self.targetspage.btn_antenna.setDisabled(True)

    def abort(self):
        if hasattr(self.homepage, "cameraWidget") and hasattr(
            self.homepage.cameraWidget, "videothread"
        ):
            self.homepage.cameraWidget.videothread.sendMessage("abort")

    def track_all(self):
        if hasattr(self.homepage, "cameraWidget") and hasattr(
            self.homepage.cameraWidget, "videothread"
        ):
            self.homepage.cameraWidget.videothread.sendMessage("track -1")

    def AllocateWidget(self, parent, child):
        if child.isAttached:
            self.stackedWidget.setCurrentWidget(self.homepage)
            parent.layout().removeWidget(child)
            self.new_window = QMainWindow(
                styleSheet="background-color: rgb(44, 49, 60);"
            )
            self.new_window.setWindowFlags(
                Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint
            )
            child.btn_AllocateWidget.setIcon(
                QIcon("uifolder/assets/icons/16x16/cil-arrow-bottom.png")
            )
            self.new_window.setCentralWidget(child)
            self.new_window.show()
            child.isAttached = False
        else:
            parent.layout().addWidget(child)
            self.new_window.setCentralWidget(None)
            self.new_window.close()
            child.btn_AllocateWidget.setIcon(
                QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png")
            )
            child.isAttached = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
