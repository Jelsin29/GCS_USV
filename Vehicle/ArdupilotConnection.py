import math
import time
import threading
from enum import Enum
from pymavlink import mavutil

from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QPushButton, QInputDialog

from MapWidget import MapWidget
from CameraWidget import CameraWidget
from IndicatorsPage import IndicatorsPage

# Some Definitions for testing purpose
ALTITUDE = 15
FOV = 110
DEBUG_TELEMETRY = False  # Set True to enable verbose telemetry prints


class MissionModes(Enum):
    WAYPOINTS = 1
    EXPLORATION = 2


def handleConnectedVehicle(connection, mapwidget, connectbutton):
    # This function is now simplified. It only handles the UI change for the button.
    # Marker creation is moved to the updateData function to wait for the first GPS fix.
    connectbutton.setText("Connected")
    connectbutton.setIcon(QIcon("../uifolder/assets/icons/24x24/cil-link.png"))
    connectbutton.setDisabled(True)
    print("✅ Connection established. Waiting for GPS fix to place vehicle on map.")


def updateData(thread, vehicle, mapwidget, indicators, camerawidget):
    type_list = [
        "ATTITUDE",
        "GLOBAL_POSITION_INT",
        "VFR_HUD",
        "SYS_STATUS",
        "HEARTBEAT",
        "BATTERY_STATUS",
        "SERVO_OUTPUT_RAW",
        "RANGEFINDER",
    ]

    # Read messages from the vehicle
    msg = vehicle.recv_match(type=type_list)
    if msg is not None:
        # Collect telemetry data for widgets
        telemetry_data = {}

        # Update indicators
        if msg.get_type() == "GLOBAL_POSITION_INT":
            position = [msg.lat / 1e7, msg.lon / 1e7]
            heading = msg.hdg / 100
            altitude = msg.relative_alt / 1000.0

            # Update USV Data
            thread.latitude = position[0]
            thread.longitude = position[1]
            thread.altitude = altitude

            # --- ROBUST MARKER HANDLING ---
            if not thread.usv_marker_created and position[0] != 0:
                # Create marker on first valid GPS fix
                mapwidget.page().runJavaScript(
                    f'console.log("First GPS fix received. Placing USV on map at: {position}")'
                )
                mapwidget.page().runJavaScript(
                    f"{mapwidget.map_variable_name}.flyTo({position}, 16)"
                )  # Fly and zoom
                mapwidget.page().runJavaScript(f"""
                    if (typeof usvMarker !== 'undefined') {{ map.removeLayer(usvMarker); }}
                    usvMarker = L.marker({position}, {{icon: usvIcon, rotationAngle: {heading - 45}}}).addTo(map);
                """)
                thread.usv_marker_created = True
                print("✅ GPS fix acquired. USV marker created on map.")

            if thread.usv_marker_created:
                # Update USV marker position and rotation
                mapwidget.page().runJavaScript(f"usvMarker.setLatLng({str(position)});")
                mapwidget.page().runJavaScript(
                    f"usvMarker.setRotationAngle({heading - 45});"
                )

            # Prepare telemetry data
            telemetry_data["global_position_int"] = {
                "lat": msg.lat,
                "lon": msg.lon,
                "hdg": msg.hdg,
                "alt": msg.relative_alt,
            }

            # Update indicators
            indicators.setAltitude(altitude)
            indicators.setHeading(heading)

            if DEBUG_TELEMETRY:
                print(
                    f"[TELEMETRY] GPS: Lat={position[0]:.6f}, Lon={position[1]:.6f}, Alt={altitude:.1f}m"
                )
        if msg.get_type() == "VFR_HUD":
            speed = msg.groundspeed
            indicators.setSpeed(speed * 1.943844)  # Convert m/s to knots

            # Prepare telemetry data
            telemetry_data["vfr_hud"] = {
                "groundspeed": msg.groundspeed,
                "heading": msg.heading,
                "throttle": msg.throttle,
                "alt": msg.alt,
                "climb": msg.climb,
            }

            if DEBUG_TELEMETRY:
                print(f"[TELEMETRY] Speed: {speed:.1f}m/s ({speed * 1.943844:.1f} kts)")

        if msg.get_type() == "ATTITUDE":
            pitch = msg.pitch
            roll = msg.roll
            indicators.setAttitude(pitch, roll)

            # Prepare telemetry data
            telemetry_data["attitude"] = {
                "roll": msg.roll,
                "pitch": msg.pitch,
                "yaw": msg.yaw,
                "rollspeed": msg.rollspeed,
                "pitchspeed": msg.pitchspeed,
                "yawspeed": msg.yawspeed,
            }

            if DEBUG_TELEMETRY:
                print(
                    f"[TELEMETRY] Attitude: Roll={roll * 57.3:.1f}°, Pitch={pitch * 57.3:.1f}°"
                )

        if msg.get_type() == "SYS_STATUS":
            # Remove missing battery_label reference
            voltage = msg.voltage_battery / 1e3
            battery_pct = msg.battery_remaining
            current = msg.current_battery / 100.0

            if hasattr(thread.parent, "label_top_info_1"):
                thread.parent.label_top_info_1.setText(
                    f"Battery: {battery_pct}% | {voltage:.1f}V | {current:.1f}A"
                )

            # Prepare telemetry data
            telemetry_data["sys_status"] = {
                "voltage_battery": msg.voltage_battery,
                "current_battery": msg.current_battery,
                "battery_remaining": msg.battery_remaining,
            }

            if DEBUG_TELEMETRY:
                print(
                    f"[TELEMETRY] Power: {battery_pct}%, {voltage:.1f}V, {current:.1f}A"
                )

        if msg.get_type() == "BATTERY_STATUS":
            # Additional battery information
            telemetry_data["battery_status"] = {
                "battery_remaining": msg.battery_remaining,
                "voltages": msg.voltages,
                "current_battery": msg.current_battery,
                "current_consumed": msg.current_consumed,
                "energy_consumed": msg.energy_consumed,
                "battery_function": msg.battery_function,
                "type": msg.type,
            }

        if msg.get_type() == "SERVO_OUTPUT_RAW":
            # Servo data for rudder angle, etc.
            telemetry_data["servo_output_raw"] = {
                "servo1_raw": msg.servo1_raw,
                "servo2_raw": msg.servo2_raw,
                "servo3_raw": msg.servo3_raw,
                "servo4_raw": msg.servo4_raw,  # Typical rudder channel
                "servo5_raw": msg.servo5_raw,
                "servo6_raw": msg.servo6_raw,
                "servo7_raw": msg.servo7_raw,
                "servo8_raw": msg.servo8_raw,
            }

        if msg.get_type() == "RANGEFINDER":
            # Water depth data
            telemetry_data["rangefinder"] = {
                "distance": msg.distance,
                "voltage": msg.voltage,
            }

        if msg.get_type() == "HEARTBEAT":
            thread.last_heartbeat = time.time()
            flight_mode = mavutil.mode_string_v10(msg)

            if DEBUG_TELEMETRY:
                print(f"[TELEMETRY] Mode: {flight_mode}")

            # Prepare telemetry data
            telemetry_data["heartbeat"] = {
                "type": msg.type,
                "autopilot": msg.autopilot,
                "base_mode": msg.base_mode,
                "custom_mode": msg.custom_mode,
                "system_status": msg.system_status,
            }

        # Update telemetry widgets with real data
        if telemetry_data:
            updateTelemetryWidgets(thread, telemetry_data)


def updateTelemetryWidgets(thread, telemetry_data):
    """Update telemetry widgets with real ArduPilot data"""
    try:
        # Update TelemetryWidget on HomePage
        if hasattr(thread.parent, "homepage") and hasattr(
            thread.parent.homepage, "telemetryWidget"
        ):
            telemetry_widget = thread.parent.homepage.telemetryWidget
            if (
                hasattr(telemetry_widget, "is_connected")
                and telemetry_widget.is_connected
            ):
                if hasattr(telemetry_widget, "updateFromArduPilotData"):
                    telemetry_widget.updateFromArduPilotData(telemetry_data)
                elif hasattr(telemetry_widget, "updateFromVRXData"):
                    telemetry_widget.updateFromVRXData(telemetry_data)
        # Update USVTelemetryWidget on IndicatorsPage
        if hasattr(thread.parent, "indicatorspage") and hasattr(
            thread.parent.indicatorspage, "usv_telemetry"
        ):
            usv_telemetry = thread.parent.indicatorspage.usv_telemetry
            if hasattr(usv_telemetry, "is_connected") and usv_telemetry.is_connected:
                if hasattr(usv_telemetry, "updateFromArduPilotData"):
                    usv_telemetry.updateFromArduPilotData(telemetry_data)
                elif hasattr(usv_telemetry, "updateFromVRXData"):
                    usv_telemetry.updateFromVRXData(telemetry_data)
        # Update IndicatorsPage main instruments
        if hasattr(thread.parent, "indicatorspage"):
            indicators = thread.parent.indicatorspage
            if hasattr(indicators, "updateFromArduPilotData"):
                indicators.updateFromArduPilotData(telemetry_data)

    except Exception as e:
        print(f"[ERROR] Error updating telemetry widgets with real data: {e}")
        import traceback

        traceback.print_exc()


def connectionLost(connectbutton, mapwidget):
    connectbutton.setText("Connect")
    connectbutton.setIcon(QIcon("../uifolder/assets/icons/24x24/cil-link-broken.png"))
    connectbutton.setDisabled(False)

    # Remove USV marker (guard against undefined if no GPS fix was received)
    mapwidget.page().runJavaScript(
        "if (typeof usvMarker !== 'undefined') { map.removeLayer(usvMarker); }"
    )

    print("❌ Connection lost - Telemetry widgets reverted to simulation mode")
    print("🔄 Restart connection to resume live data")


class ArdupilotConnectionThread(QThread):
    # Enhanced signals for better communication
    vehicleConnected_signal = Signal(object, MapWidget, QPushButton)
    updateData_signal = Signal(QThread, object, MapWidget, IndicatorsPage, CameraWidget)
    connectionLost_signal = Signal(QPushButton, MapWidget)

    # New enhanced signals
    telemetry_update = Signal(dict)
    connection_status = Signal(bool, str)
    mission_status = Signal(str, bool)
    mission_item_reached = Signal(int)  # waypoint sequence number
    relay_target_result = Signal(dict)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.connection = None
        self.connection_string = None
        self.baudrate = None
        self.connectButton = parent.btn_connect
        self.mapwidget = parent.homepage.mapwidget
        self.indicators = parent.indicatorspage

        # Telemetry Data
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0  # For surface vessels, this is typically 0

        # Variables
        self.home_position = [0, 0]
        self.camera_angle = 45
        self.is_running = True
        self.last_mission_count = 0  # Cached count after upload (real waypoints only)
        self.usv_marker_created = False

        # PRODUCTION TIMEOUT SETTINGS
        self.MISSION_UPLOAD_TIMEOUT = 45  # Total mission upload timeout (seconds)
        self.MISSION_ITEM_TIMEOUT = 8  # Individual item request timeout (seconds)
        self.MISSION_CLEAR_TIMEOUT = 10  # Mission clear timeout (seconds)
        self.MISSION_ACK_TIMEOUT = 15  # Final ACK timeout (seconds)
        self.HEARTBEAT_TIMEOUT = 10  # Heartbeat timeout (seconds)
        self.ARM_TIMEOUT = 20  # Arm operation timeout (seconds)

        # Counter-based pause mechanism for the run() recv loop.
        # Using a counter (protected by a Lock) rather than a plain Event allows
        # re-entrant callers (e.g. arm_vehicle calling set_mode) to each
        # pause/resume independently without the inner callee prematurely
        # re-enabling the loop while the outer caller still needs it paused.
        self._stop_recv = threading.Event()
        self._stop_recv_count = 0
        self._stop_recv_lock = threading.Lock()

        # RLock that serialises all blocking MAVLink operations (upload,
        # arm, set_mode, start_mission).  Prevents two operations from
        # calling recv_match() on the same connection simultaneously.
        # RLock (re-entrant) is required because arm_vehicle calls set_mode
        # and start_mission calls arm_vehicle — the same thread acquires
        # the lock multiple times in the call stack.
        self._operation_lock = threading.RLock()

        self.vehicleConnected_signal.connect(handleConnectedVehicle)
        self.updateData_signal.connect(updateData)
        self.connectionLost_signal.connect(connectionLost)

    # This method is called when the thread is started
    def run(self):
        try:
            self.connection_status.emit(True, "Connecting...")
            self.is_running = True

            # Connect to the vehicle
            if self.connect_to_vehicle():
                # Request data streams
                self.request_data_streams()

                # Connection successful
                self.vehicleConnected_signal.emit(
                    self.connection, self.mapwidget, self.connectButton
                )
                self.connection_status.emit(True, "Connected")

                # Main loop
                while self.is_running and self.connection:
                    try:
                        # Yield the socket to command methods (arm, upload, set_mode, …)
                        # while they hold _stop_recv.  Max pause granularity = 0.2 s.
                        if self._stop_recv.is_set():
                            self.msleep(50)
                            continue
                        message = self.connection.recv_match(blocking=True, timeout=0.2)
                        if message is None:
                            self.msleep(100)
                            continue

                        # Process telemetry
                        self.process_telemetry(message)

                        # Update UI with data
                        self.updateData_signal.emit(
                            self,
                            self.connection,
                            self.mapwidget,
                            self.indicators,
                            self.parent.homepage.cameraWidget,
                        )

                        self.msleep(100)  # 10Hz update rate

                    except Exception as e:
                        print(f"Error in communication loop: {e}")
                        self.msleep(1000)

            else:
                self.connection_status.emit(False, "Connection failed")

        except Exception as e:
            print(f"Fatal error in connection thread: {e}")
            self.connection_status.emit(False, f"Fatal error: {str(e)}")
        finally:
            self.cleanup()

    def connect_to_vehicle(self):
        """Enhanced connection method with better error handling"""
        try:
            print(f"Attempting connection to: {self.connection_string}")

            # Create the connection
            if "COM" in self.connection_string or "/dev/" in self.connection_string:
                # Serial connection
                self.connection = mavutil.mavlink_connection(
                    self.connection_string,
                    baud=self.baudrate if self.baudrate else 57600,
                    timeout=5,
                )
            else:
                # UDP/TCP connection
                self.connection = mavutil.mavlink_connection(
                    self.connection_string, timeout=5
                )

            # Wait for heartbeat
            print("Waiting for heartbeat...")
            heartbeat = self.connection.wait_heartbeat(timeout=10)

            if heartbeat:
                print(f"Heartbeat from system {heartbeat.get_srcSystem()}")

                # Verify this is appropriate vehicle type for USV
                if heartbeat.type in [
                    mavutil.mavlink.MAV_TYPE_GROUND_ROVER,
                    mavutil.mavlink.MAV_TYPE_SURFACE_BOAT,
                ]:
                    return True
                else:
                    print(
                        f"Warning: Vehicle type {heartbeat.type} may not be suitable for USV"
                    )
                    return True  # Continue anyway

            return False

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def is_ardupilot(self):
        """Check if connected to ArduPilot"""
        if not self.connection:
            return False

        # Get heartbeat to check autopilot type
        heartbeat = self.connection.recv_match(type="HEARTBEAT", timeout=2)
        if heartbeat:
            return heartbeat.autopilot == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA
        return False

    def configure_ardupilot_timeouts(self):
        """Configure ArduPilot parameters for reliable mission operations"""
        if not self.connection:
            return False

        try:
            print("[CONFIG] Setting ArduPilot timeout parameters...")

            # Mission timeout (critical for preventing OPERATION_CANCELLED)
            self.connection.mav.param_set_send(
                self.connection.target_system,
                self.connection.target_component,
                b"MIS_TIMEOUT",
                60.0,  # 60 seconds mission timeout
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
            )

            # Mission options (use MISSION_REQUEST_INT)
            self.connection.mav.param_set_send(
                self.connection.target_system,
                self.connection.target_component,
                b"MIS_OPTIONS",
                1.0,  # Use MISSION_REQUEST_INT
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
            )

            # Note: SER1_PROTOCOL is a serial-port hardware parameter — setting
            # it over a SITL/UDP link produces a PARAM_VALUE NACK and is harmless
            # but noisy.  It is intentionally omitted here.

            # Brief pause to allow ArduPilot to process the param_set messages
            # without flooding the link.
            self.msleep(100)

            print("[CONFIG] Timeout parameters configured for production use")
            return True

        except Exception as e:
            print(f"[CONFIG ERROR] Failed to set timeout parameters: {e}")
            return False

    def request_data_streams(self):
        """Request telemetry data streams"""
        if not self.connection:
            return

        try:
            # Request data streams
            self.connection.mav.request_data_stream_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                1,  # Rate in Hz
                1,  # Start/stop
            )

            # Request specific message types for USV
            try:
                # Use command_long_send for SET_MESSAGE_INTERVAL instead
                message_rates = [
                    (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 2),
                    (mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, 2),
                    (mavutil.mavlink.MAVLINK_MSG_ID_EKF_STATUS_REPORT, 2),
                    (mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 2),
                    (mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 1),
                    (mavutil.mavlink.MAVLINK_MSG_ID_HEARTBEAT, 1),
                    (mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 1),
                    (mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS, 1),
                ]

                for msg_id, rate in message_rates:
                    # Use MAV_CMD_SET_MESSAGE_INTERVAL command
                    self.connection.mav.command_long_send(
                        self.connection.target_system,
                        self.connection.target_component,
                        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                        0,  # confirmation
                        msg_id,  # param1: message ID
                        int(1000000 / rate),  # param2: interval in microseconds
                        0,
                        0,
                        0,
                        0,
                        0,  # params 3-7
                    )
            except Exception as inner_e:
                print(f"Error with command_long_send: {inner_e}")
                # Fallback: just use the basic data stream request

        except Exception as e:
            print(f"Error requesting data streams: {e}")

    def process_telemetry(self, message):
        """Process incoming telemetry messages"""
        if not message:
            return

        telemetry_data = {}

        try:
            if message.get_type() == "GLOBAL_POSITION_INT":
                self.latitude = message.lat / 1e7
                self.longitude = message.lon / 1e7
                self.altitude = message.alt / 1000.0  # Convert mm to m

                telemetry_data.update(
                    {
                        "latitude": self.latitude,
                        "longitude": self.longitude,
                        "altitude": self.altitude,
                        "heading": message.hdg / 100.0
                        if hasattr(message, "hdg")
                        else 0,
                    }
                )

            elif message.get_type() == "GPS_RAW_INT":
                telemetry_data.update(
                    {
                        "gps_fix_type": message.fix_type,
                        "satellites_visible": message.satellites_visible,
                        "gps_hdop": message.eph / 100.0
                        if message.eph != 65535
                        else 999.99,
                    }
                )

            elif message.get_type() == "ATTITUDE":
                telemetry_data.update(
                    {
                        "roll": math.degrees(message.roll),
                        "pitch": math.degrees(message.pitch),
                        "yaw": math.degrees(message.yaw),
                    }
                )

            elif message.get_type() == "VFR_HUD":
                telemetry_data.update(
                    {
                        "groundspeed": message.groundspeed,
                        "airspeed": message.airspeed,
                        "climb_rate": message.climb,
                        "throttle": message.throttle,
                    }
                )

            elif message.get_type() == "SYS_STATUS":
                telemetry_data.update(
                    {
                        "voltage_battery": message.voltage_battery / 1000.0,
                        "current_battery": message.current_battery / 100.0
                        if message.current_battery != -1
                        else 0,
                        "battery_remaining": message.battery_remaining,
                    }
                )

            elif message.get_type() == "HEARTBEAT":
                telemetry_data.update(
                    {
                        "mode": self.get_mode_string(message.custom_mode, message.type),
                        "armed": bool(
                            message.base_mode
                            & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                        ),
                        "system_status": message.system_status,
                    }
                )

            elif message.get_type() == "MISSION_ITEM_REACHED":
                seq = message.seq
                print(f"[MISSION] Waypoint {seq} reached")
                self.mission_item_reached.emit(seq)

            # Emit telemetry update if we have data
            if telemetry_data:
                self.telemetry_update.emit(telemetry_data)

        except Exception as e:
            print(f"Error processing telemetry: {e}")

    def get_mode_string(self, custom_mode, vehicle_type):
        """Get human-readable mode string"""
        try:
            # Rover/Boat mode mappings
            rover_modes = {
                0: "MANUAL",
                1: "ACRO",
                3: "STEERING",
                4: "HOLD",
                5: "LOITER",
                6: "FOLLOW",
                7: "SIMPLE",
                10: "AUTO",
                11: "RTL",
                12: "SMART_RTL",
                15: "GUIDED",
            }

            return rover_modes.get(custom_mode, f"UNKNOWN({custom_mode})")

        except Exception:
            return "UNKNOWN"

    def upload_mission(self, waypoints, auto_start=False):
        """
        PRODUCTION VERSION: Mission upload with extended timeouts.

        Pauses the background recv loop for the duration of the upload so that
        MISSION_REQUEST_INT and MISSION_ACK messages are not consumed by run()
        before this method sees them.  The loop is always resumed in the
        finally block even if an exception occurs.
        """
        if not self.connection or not waypoints:
            print("[UPLOAD ERROR] No connection or empty waypoints")
            return False

        if not self._operation_lock.acquire(blocking=True, timeout=5):
            print(
                "[UPLOAD ERROR] Another MAVLink operation is in progress — try again shortly"
            )
            return False

        self._pause_recv_loop()
        try:
            print(
                f"[UPLOAD] Starting PRODUCTION mission upload with {len(waypoints)} waypoints"
            )

            # If a previous mission is still active, replace it from a stable mode.
            # Uploading a brand-new mission while the rover is still armed/in AUTO can
            # leave mission execution state ambiguous across runs, especially when the
            # user chains single-waypoint and multi-waypoint tests without disarming.
            heartbeat = self.connection.recv_match(
                type="HEARTBEAT", blocking=True, timeout=1
            )
            if heartbeat:
                current_mode = self.get_mode_string(
                    heartbeat.custom_mode, heartbeat.type
                )
                is_armed = bool(
                    heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                )
                print(
                    f"[UPLOAD] Pre-upload vehicle state: mode={current_mode} armed={is_armed}"
                )
                if is_armed and current_mode == "AUTO":
                    print(
                        "[UPLOAD] Vehicle is in AUTO during upload — switching to HOLD first..."
                    )
                    if not self.set_mode("HOLD"):
                        print(
                            "[UPLOAD ERROR] Failed to switch to HOLD before mission replacement"
                        )
                        return False
                    self.msleep(500)

            # Step 1: Configure ArduPilot timeouts first
            self.configure_ardupilot_timeouts()

            # Step 2: Clear message buffer thoroughly
            print("[UPLOAD] Clearing message buffer...")
            cleared_count = 0
            for _ in range(20):  # Clear more messages
                msg = self.connection.recv_match(timeout=0.05)
                if not msg:
                    break
                cleared_count += 1
            print(f"[UPLOAD] Cleared {cleared_count} pending messages")

            # Step 3: Clear existing mission with extended timeout
            print("[UPLOAD] Clearing existing mission...")
            self.connection.mav.mission_clear_all_send(
                self.connection.target_system, self.connection.target_component
            )

            # Wait for clear confirmation — blocking so we actually wait for the ACK
            ack = self.connection.recv_match(
                type="MISSION_ACK", blocking=True, timeout=self.MISSION_CLEAR_TIMEOUT
            )
            if ack:
                if ack.type == 0:  # MAV_MISSION_ACCEPTED
                    print("[UPLOAD] Mission cleared successfully")
                    pass
                else:
                    print(
                        f"[UPLOAD] Clear returned type={ack.type}, continuing anyway..."
                    )

            self.msleep(300)  # Brief settle after clear

            # Step 4: Prepare mission items.
            # ArduPilot AP_Mission reserves seq=0 for HOME. Upload a placeholder
            # item 0 so the first real waypoint starts at seq=1, then explicitly
            # set the current mission item to 1 after upload.
            mission_items = [
                {
                    "seq": 0,
                    "frame": mavutil.mavlink.MAV_FRAME_GLOBAL_INT,
                    "command": mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                    "current": 0,
                    "autocontinue": 1,
                    "param1": 0.0,
                    "param2": 0.0,
                    "param3": 0.0,
                    "param4": 0.0,
                    "x": 0,
                    "y": 0,
                    "z": 0.0,
                }
            ]
            real_waypoint_count = len(waypoints)

            for i, wp in enumerate(waypoints):
                if isinstance(wp, dict):
                    lat, lon = wp["lat"], wp["lon"]
                    alt = wp.get("alt", 0)
                else:
                    lat, lon = float(wp[0]), float(wp[1])
                    alt = float(wp[2]) if len(wp) > 2 else 0

                mission_items.append(
                    {
                        "seq": i
                        + 1,  # seq 0 reserved for HOME; real waypoints start at 1
                        "frame": mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                        "command": mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                        "current": 0,
                        "autocontinue": 1,
                        "param1": 0.0,
                        "param2": 3.0,
                        "param3": 0.0,
                        "param4": 0.0,
                        "x": int(lat * 1e7),
                        "y": int(lon * 1e7),
                        "z": float(alt),
                    }
                )

            total_items = len(mission_items)

            # Step 5: Send mission count — send ONCE only.
            # Retrying MISSION_COUNT while ArduPilot is waiting for MISSION_ITEM_INT
            # causes it to cancel the in-progress upload (OPERATION_CANCELLED).
            print(f"[UPLOAD] Sending mission count: {total_items}")
            self.connection.mav.mission_count_send(
                self.connection.target_system,
                self.connection.target_component,
                total_items,
                mavutil.mavlink.MAV_MISSION_TYPE_MISSION,
            )

            # ArduPilot responds with MISSION_REQUEST_INT within ~1 s under normal
            # conditions.  We wait up to 20 s to handle slow links.
            # blocking=True is REQUIRED — without it recv_match returns None immediately.
            first_request = self.connection.recv_match(
                type=["MISSION_REQUEST_INT", "MISSION_REQUEST"],
                blocking=True,
                timeout=20,
            )

            if not first_request:
                print("[UPLOAD ERROR] No response to mission count")
                return False

            print("[UPLOAD] Mission count acknowledged")
            # Handle the first request immediately
            if first_request.seq < len(mission_items):
                item = mission_items[first_request.seq]
                self.connection.mav.mission_item_int_send(
                    self.connection.target_system,
                    self.connection.target_component,
                    item["seq"],
                    item["frame"],
                    item["command"],
                    item["current"],
                    item["autocontinue"],
                    item["param1"],
                    item["param2"],
                    item["param3"],
                    item["param4"],
                    item["x"],
                    item["y"],
                    item["z"],
                    mavutil.mavlink.MAV_MISSION_TYPE_MISSION,
                )
                print(f"[UPLOAD] Sent item {first_request.seq}")

            # Step 6: Handle remaining requests with extended timeout
            uploaded_items = {first_request.seq}
            start_time = time.time()

            while len(uploaded_items) < total_items:
                if time.time() - start_time > self.MISSION_UPLOAD_TIMEOUT:
                    print(
                        f"[UPLOAD ERROR] Total timeout - uploaded {len(uploaded_items)}/{total_items}"
                    )
                    return False

                # Wait for next request with production timeout.
                # blocking=True is REQUIRED — without it recv_match returns immediately.
                request = self.connection.recv_match(
                    type=["MISSION_REQUEST_INT", "MISSION_REQUEST"],
                    blocking=True,
                    timeout=self.MISSION_ITEM_TIMEOUT,
                )

                if request:
                    seq = request.seq

                    if seq < len(mission_items):
                        item = mission_items[seq]
                        # Per spec: always resend on re-request — vehicle may not have
                        # received the item (lost packet), so resend even if already sent.
                        self.connection.mav.mission_item_int_send(
                            self.connection.target_system,
                            self.connection.target_component,
                            item["seq"],
                            item["frame"],
                            item["command"],
                            item["current"],
                            item["autocontinue"],
                            item["param1"],
                            item["param2"],
                            item["param3"],
                            item["param4"],
                            item["x"],
                            item["y"],
                            item["z"],
                            mavutil.mavlink.MAV_MISSION_TYPE_MISSION,
                        )
                        if seq not in uploaded_items:
                            uploaded_items.add(seq)
                            print(
                                f"[UPLOAD] Sent item {seq} ({len(uploaded_items)}/{total_items})"
                            )
                        else:
                            print(f"[UPLOAD] Re-sent item {seq} (vehicle re-requested)")
                else:
                    print("[UPLOAD] Request timeout - checking if upload complete...")
                    break

            # Step 7: Wait for final ACK with extended timeout
            print("[UPLOAD] Waiting for final mission ACK...")

            final_ack = None
            ack_start = time.time()

            while time.time() - ack_start < self.MISSION_ACK_TIMEOUT:
                ack = self.connection.recv_match(
                    type="MISSION_ACK", blocking=True, timeout=0.5
                )
                if ack:
                    print(f"[UPLOAD] Received ACK type: {ack.type}")

                    if ack.type == 0:  # ACCEPTED
                        final_ack = ack
                        break
                    elif ack.type == 15:  # OPERATION_CANCELLED
                        print(
                            "[UPLOAD ERROR] Mission cancelled by ArduPilot - timeout issue"
                        )
                        return False
                    elif ack.type == 14:  # DENIED
                        print("[UPLOAD ERROR] Mission denied by ArduPilot")
                        return False
                    else:
                        print(f"[UPLOAD ERROR] Unexpected ACK: {ack.type}")

            if final_ack and final_ack.type == 0:
                print(
                    "[UPLOAD SUCCESS] Mission uploaded successfully for PRODUCTION use!"
                )

                # Set current waypoint to seq=1 (first real waypoint; seq=0 is HOME)
                self.connection.mav.mission_set_current_send(
                    self.connection.target_system, self.connection.target_component, 1
                )
                print("[UPLOAD] Set mission current to seq=1 (first real waypoint)")
                self.last_mission_count = real_waypoint_count

                # Extra cleanup for production
                self.msleep(500)
                for _ in range(5):
                    msg = self.connection.recv_match(timeout=0.1)
                    if not msg:
                        break

                return True
            else:
                print("[UPLOAD ERROR] No final ACK or upload failed")
                return False

        except Exception as e:
            print(f"[UPLOAD ERROR] Production upload exception: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            self._resume_recv_loop()
            self._operation_lock.release()

    def set_mode(self, mode_name):
        """Set vehicle mode with detailed debugging.

        Pauses the background recv loop while waiting for a HEARTBEAT
        confirmation so the run() loop does not consume the reply first.
        The loop is always resumed in the finally block.
        """
        if not self.connection:
            print(f"[MODE DEBUG] Cannot set mode {mode_name} - no connection")
            return False

        self._operation_lock.acquire()
        self._pause_recv_loop()
        try:
            print(f"[MODE DEBUG] Setting mode to: {mode_name}")

            def _drain_mode_debug_messages(window_s=0.75):
                """Drain immediate COMMAND_ACK/STATUSTEXT messages for mode diagnostics."""
                end_time = time.time() + window_s
                while time.time() < end_time:
                    msg = self.connection.recv_match(
                        type=["COMMAND_ACK", "STATUSTEXT", "HEARTBEAT"],
                        blocking=True,
                        timeout=0.25,
                    )
                    if not msg:
                        continue

                    msg_type = msg.get_type()
                    if msg_type == "COMMAND_ACK":
                        print(
                            "[MODE DEBUG] COMMAND_ACK "
                            f"command={msg.command} result={msg.result}"
                        )
                    elif msg_type == "STATUSTEXT":
                        text = getattr(msg, "text", "")
                        severity = getattr(msg, "severity", "?")
                        print(f"[MODE DEBUG] STATUSTEXT severity={severity}: {text}")
                    elif msg_type == "HEARTBEAT":
                        current_mode_id = msg.custom_mode
                        current_mode_name = self.get_mode_string(
                            current_mode_id, msg.type
                        )
                        armed = bool(
                            msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                        )
                        print(
                            "[MODE DEBUG] HEARTBEAT "
                            f"mode={current_mode_name} (ID:{current_mode_id}) armed={armed}"
                        )

            # Mode mappings for Rover/Boat
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

            if mode_name not in mode_mapping:
                print(f"[MODE DEBUG] Unknown mode: {mode_name}")
                print(f"[MODE DEBUG] Available modes: {list(mode_mapping.keys())}")
                return False

            mode_id = mode_mapping[mode_name]
            print(f"[MODE DEBUG] Mode {mode_name} maps to ID: {mode_id}")

            print("[MODE DEBUG] Sending mode change command...")
            print(f"[MODE DEBUG] Target system: {self.connection.target_system}")
            print(f"[MODE DEBUG] Target component: {self.connection.target_component}")

            initial_hb = self.connection.recv_match(
                type="HEARTBEAT", blocking=True, timeout=1
            )
            if initial_hb:
                initial_mode_id = initial_hb.custom_mode
                initial_mode_name = self.get_mode_string(
                    initial_mode_id, initial_hb.type
                )
                initial_armed = bool(
                    initial_hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                )
                print(
                    "[MODE DEBUG] Initial vehicle state: "
                    f"mode={initial_mode_name} (ID:{initial_mode_id}) armed={initial_armed}"
                )

            for attempt in range(3):
                self.connection.mav.set_mode_send(
                    self.connection.target_system,
                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                    mode_id,
                )
                # COMMAND_LONG backup improves compatibility with ArduPilot Rover/SITL
                self.connection.mav.command_long_send(
                    self.connection.target_system,
                    self.connection.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                    0,
                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                    mode_id,
                    0,
                    0,
                    0,
                    0,
                    0,
                )

                print(
                    f"[MODE DEBUG] Mode change to {mode_name} (ID:{mode_id}) requested "
                    f"(attempt {attempt + 1}/3)"
                )

                _drain_mode_debug_messages(window_s=1.0)

                deadline = time.time() + 5
                while time.time() < deadline:
                    heartbeat = self.connection.recv_match(
                        type="HEARTBEAT", blocking=True, timeout=0.5
                    )
                    if not heartbeat:
                        continue

                    current_mode_id = heartbeat.custom_mode
                    current_mode_name = self.get_mode_string(
                        current_mode_id, heartbeat.type
                    )
                    print(
                        f"[MODE DEBUG] Current mode after request: {current_mode_name} "
                        f"(ID:{current_mode_id})"
                    )

                    if current_mode_id == mode_id:
                        print(f"[MODE DEBUG] ✓ Mode change to {mode_name} confirmed")
                        return True

                print(
                    f"[MODE DEBUG] ⚠️ Attempt {attempt + 1} did not confirm {mode_name}; retrying..."
                )

            print(f"[MODE DEBUG] ✗ Mode change to {mode_name} failed after 3 attempts")
            _drain_mode_debug_messages(window_s=1.5)
            return False

        except Exception as e:
            print(f"[MODE DEBUG] Error setting mode {mode_name}: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            self._resume_recv_loop()
            self._operation_lock.release()

    # ------------------------------------------------------------------
    # Recv-loop pause helpers
    # ------------------------------------------------------------------
    def _pause_recv_loop(self):
        """Pause the run() recv loop so a command method can own recv_match.

        Uses a reference-count so that re-entrant callers (e.g. arm_vehicle
        calling set_mode, which also pauses) each hold an independent pause.
        The loop stays paused until every paired _resume_recv_loop() has been
        called.  The run() loop polls _stop_recv with a 0.2 s recv_match
        timeout, so after setting the event we wait 0.3 s to guarantee the
        loop has exited its current blocking call before we start our own
        recv_match calls.
        """
        with self._stop_recv_lock:
            self._stop_recv_count += 1
            self._stop_recv.set()
        self.msleep(300)  # Allow the in-flight 0.2 s recv_match to complete

    def _resume_recv_loop(self):
        """Resume the run() recv loop after a command method finishes.

        Only clears the pause event when the last nested caller resumes,
        matching the re-entrant semantics of _pause_recv_loop().
        """
        with self._stop_recv_lock:
            self._stop_recv_count = max(0, self._stop_recv_count - 1)
            if self._stop_recv_count == 0:
                self._stop_recv.clear()

    def stop(self):
        """Stop the connection thread gracefully"""
        self.is_running = False
        self.wait(5000)  # Wait up to 5 seconds for thread to finish

    def cleanup(self):
        """Clean up connection resources and notify widgets of disconnection"""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connection = None
        self.usv_marker_created = False

        # Notify widgets of disconnection
        if hasattr(self.parent, "homepage") and hasattr(
            self.parent.homepage, "telemetryWidget"
        ):
            telemetry_widget = self.parent.homepage.telemetryWidget
            if hasattr(telemetry_widget, "setConnectionStatus"):
                telemetry_widget.setConnectionStatus(False)

        if hasattr(self.parent, "indicatorspage") and hasattr(
            self.parent.indicatorspage, "usv_telemetry"
        ):
            usv_telemetry = self.parent.indicatorspage.usv_telemetry
            if hasattr(usv_telemetry, "setConnectionStatus"):
                usv_telemetry.setConnectionStatus(False)

    def setBaudRate(self, baud):
        self.baudrate = baud  # 115200 on USB or 57600 on Radio/Telemetry

    def setConnectionString(self, connectionstring):
        if connectionstring == "Telemetri":
            self.connection_string = "/dev/ttyUSB0"
        elif connectionstring == "USB":
            self.connection_string = "/dev/ttyACM0"
        elif connectionstring == "SITL (UDP)":
            self.connection_string = "udp:127.0.0.1:14550"
        elif connectionstring == "SITL (TCP)":
            self.connection_string = "tcp:127.0.0.1:5760"
        elif connectionstring == "MAVROS Direct":
            self.connection_string = "udp:127.0.0.1:14556"
        elif connectionstring == "UDP":
            text, ok = QInputDialog.getText(self.parent, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = f"udp:{text}:14550"
        elif connectionstring == "TCP":
            text, ok = QInputDialog.getText(self.parent, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = f"tcp:{text}:5760"
        else:
            self.connection_string = connectionstring

    def send_semantic_event(self, event: dict) -> bool:
        """Relay semantic target/obstacle data to the USV companion via DEBUG_VECT."""
        event_type = event.get("event_type", "MISSION_TARGET")
        message_name = b"TARGET" if event_type == "MISSION_TARGET" else b"OBSTACLE"
        semantic_code = self._semantic_code_for_event(event)
        return self._send_semantic_debug_vect(message_name, event, semantic_code)

    def send_semantic_target(self, target_event: dict) -> bool:
        """Backward-compatible target relay helper used by the coordinator."""
        event = dict(target_event)
        event["event_type"] = "MISSION_TARGET"
        return self.send_semantic_event(event)

    def _send_semantic_debug_vect(
        self, message_name: bytes, event: dict, semantic_code: float
    ) -> bool:
        if not self.connection:
            self.relay_target_result.emit(
                {
                    "target_id": event.get("id", "unknown"),
                    "status": "failed",
                    "error": "usv-not-connected",
                    "event_type": event.get("event_type", "UNKNOWN"),
                }
            )
            return False

        try:
            self.connection.mav.debug_vect_send(
                name=message_name,
                time_usec=int(time.time() * 1e6),
                x=float(event["lat"]),
                y=float(event["lon"]),
                z=semantic_code,
            )
            self.relay_target_result.emit(
                {
                    "target_id": event.get("id", "unknown"),
                    "status": "relayed",
                    "error": None,
                    "event_type": event.get("event_type", "UNKNOWN"),
                }
            )
            return True
        except Exception as e:
            self.relay_target_result.emit(
                {
                    "target_id": event.get("id", "unknown"),
                    "status": "failed",
                    "error": str(e),
                    "event_type": event.get("event_type", "UNKNOWN"),
                }
            )
            print(f"[SEMANTIC RELAY] Failed to send {event.get('event_type')}: {e}")
            return False

    def _semantic_code_for_event(self, event: dict) -> float:
        event_type = event.get("event_type", "MISSION_TARGET")
        if event_type == "MISSION_TARGET":
            color_ids = {"RED": 1.0, "GREEN": 2.0, "BLACK": 3.0, "BLUE": 3.0}
            return color_ids.get(str(event.get("color", "UNKNOWN")).upper(), 0.0)

        obstacle_ids = {
            "UNKNOWN": 100.0,
            "BUOY": 101.0,
            "ROCK": 102.0,
            "VESSEL": 103.0,
            "DEBRIS": 104.0,
        }
        return obstacle_ids.get(
            str(event.get("obstacle_type", "UNKNOWN")).upper(), 100.0
        )

    def goto_markers_pos(self, lat, lon):
        """
        Commands the USV to move to the given lat/lon in GUIDED mode.
        Uses SET_POSITION_TARGET_GLOBAL_INT (modern ArduPilot Rover API).
        """
        if not self.connection:
            print("[GOTO ERROR] No connection.")
            return

        try:
            if lat == 0 and lon == 0:
                print(
                    "[GOTO WARN] Target position is (0,0). Please set a valid target."
                )
                return

            # Ensure the vehicle is in GUIDED mode
            if not self.set_mode("GUIDED"):
                print("[GOTO ERROR] Failed to set GUIDED mode.")
                return

            print(f"[GOTO] Commanding USV to move to: Lat {lat}, Lon {lon}")

            # type_mask: ignore velocity, acceleration, yaw, yaw_rate; use lat/lon/alt
            # bits 3-8, 10-11 set to 1 (ignore); bits 0-2 clear (use position)
            type_mask = (
                mavutil.mavlink.POSITION_TARGET_TYPEMASK_VX_IGNORE
                | mavutil.mavlink.POSITION_TARGET_TYPEMASK_VY_IGNORE
                | mavutil.mavlink.POSITION_TARGET_TYPEMASK_VZ_IGNORE
                | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AX_IGNORE
                | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AY_IGNORE
                | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AZ_IGNORE
                | mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_IGNORE
                | mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE
            )

            self.connection.mav.set_position_target_global_int_send(
                0,  # time_boot_ms
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                type_mask,
                int(lat * 1e7),  # lat_int
                int(lon * 1e7),  # lon_int
                0,  # alt (surface vehicle)
                0,
                0,
                0,  # vx, vy, vz (ignored)
                0,
                0,
                0,  # afx, afy, afz (ignored)
                0,
                0,  # yaw, yaw_rate (ignored)
            )
            print("[GOTO] Go-to command sent.")

        except Exception as e:
            print(f"[GOTO EXCEPTION] An error occurred: {e}")

    def arm_vehicle(self):
        """Arm the vehicle for USV operation.

        Pauses the background recv loop for the duration of arming so that
        COMMAND_ACK and HEARTBEAT messages are not consumed by run() before
        this method sees them.  When arm_vehicle calls set_mode internally,
        the reference-counted pause ensures the loop remains paused for the
        full arm sequence.  The loop is always resumed in the finally block.
        """
        if not self.connection:
            print("[ARM ERROR] No connection to vehicle")
            return False

        self._operation_lock.acquire()
        self._pause_recv_loop()
        try:
            print("[ARM] Arming USV...")

            # Safety check: verify GPS fix before arming
            gps_msg = self.connection.recv_match(
                type="GPS_RAW_INT", blocking=True, timeout=3
            )
            if gps_msg:
                if gps_msg.fix_type < 3:
                    print(
                        f"[ARM ERROR] GPS fix insufficient: fix_type={gps_msg.fix_type} "
                        f"(need >= 3). Satellites: {gps_msg.satellites_visible}"
                    )
                    return False
                if gps_msg.satellites_visible < 6:
                    print(
                        f"[ARM WARNING] Low satellite count: {gps_msg.satellites_visible}"
                    )
            else:
                print("[ARM ERROR] Could not verify GPS fix — refusing to arm")
                return False

            # First ensure we're in a mode that allows arming (MANUAL or GUIDED)
            current_mode = self.get_current_mode()
            if current_mode not in ["MANUAL", "GUIDED"]:
                print(
                    f"[ARM] Switching from {current_mode} to GUIDED mode for arming..."
                )
                if not self.set_mode("GUIDED"):
                    print("[ARM ERROR] Failed to set GUIDED mode")
                    return False
                self.msleep(1000)  # Give time for mode change

            # Check if already armed
            heartbeat = self.connection.recv_match(
                type="HEARTBEAT", blocking=True, timeout=3
            )
            if heartbeat:
                if heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
                    print("[ARM] Vehicle is already armed")
                    return True

            # Send arm command
            print("[ARM] Sending ARM command...")
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,  # confirmation
                1,  # param1: 1 to arm, 0 to disarm
                0,  # param2: force (0=normal, 21196=force)
                0,
                0,
                0,
                0,
                0,  # unused parameters
            )

            # Wait for arm acknowledgment with timeout
            print("[ARM] Waiting for arm confirmation...")
            start_time = time.time()

            while time.time() - start_time < self.ARM_TIMEOUT:
                # Check command acknowledgment
                ack = self.connection.recv_match(type="COMMAND_ACK", timeout=1)
                if ack and ack.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                    if ack.result == 0:  # Success
                        print("[ARM] Arm command acknowledged")
                    else:
                        print(
                            f"[ARM ERROR] Arm command rejected with result: {ack.result}"
                        )
                        return False

                # Check if actually armed via heartbeat
                heartbeat = self.connection.recv_match(type="HEARTBEAT", timeout=0.5)
                if heartbeat:
                    if heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
                        print("[ARM SUCCESS] Vehicle is now armed!")
                        return True

            print("[ARM ERROR] Arm operation timed out")
            return False

        except Exception as e:
            print(f"[ARM ERROR] Exception during arm operation: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            self._resume_recv_loop()
            self._operation_lock.release()

    def arm_and_start(self):
        """Arm the vehicle and set to GUIDED mode (USV equivalent of takeoff)"""
        if not self.connection:
            print("[ARM_START ERROR] No connection to vehicle")
            return False

        try:
            print("[ARM_START] Starting USV arm and preparation sequence...")

            # Step 1: Arm the vehicle
            if not self.arm_vehicle():
                print("[ARM_START ERROR] Failed to arm vehicle")
                return False

            # Step 2: Ensure we're in GUIDED mode
            if not self.set_mode("GUIDED"):
                print("[ARM_START ERROR] Failed to set GUIDED mode after arming")
                return False

            # Step 3: Wait a moment for everything to settle
            self.msleep(1000)

            print("[ARM_START SUCCESS] USV is armed and ready for guided operations!")
            return True

        except Exception as e:
            print(f"[ARM_START ERROR] Exception: {e}")
            return False

    def disarm_vehicle(self):
        """Disarm the vehicle.

        Pauses the background recv loop so that HEARTBEAT messages confirming
        the disarm are not consumed by run() before this method sees them.
        The loop is always resumed in the finally block.
        """
        if not self.connection:
            print("[DISARM ERROR] No connection to vehicle")
            return False

        self._operation_lock.acquire()
        self._pause_recv_loop()
        try:
            print("[DISARM] Disarming USV...")

            # Send disarm command
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,  # confirmation
                0,  # param1: 0 to disarm
                0,  # param2: force (0=normal, 21196=force)
                0,
                0,
                0,
                0,
                0,  # unused parameters
            )

            # Wait for disarm confirmation
            start_time = time.time()
            while time.time() - start_time < 10:  # 10 second timeout
                heartbeat = self.connection.recv_match(type="HEARTBEAT", timeout=1)
                if heartbeat:
                    if not (
                        heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                    ):
                        print("[DISARM SUCCESS] Vehicle disarmed")
                        return True

            print("[DISARM ERROR] Disarm operation timed out")
            return False

        except Exception as e:
            print(f"[DISARM ERROR] Exception: {e}")
            return False
        finally:
            self._resume_recv_loop()
            self._operation_lock.release()

    def rtl(self):
        """Return to Launch"""
        self.set_mode("RTL")

    def land(self):
        """Hold position (USV equivalent of land)"""
        self.set_mode("HOLD")

    def set_roi(self):
        """Set Region of Interest - not implemented for USV"""
        print("[ROI] ROI not supported for USV")

    def cancel_roi_mode(self):
        """Cancel ROI - not implemented for USV"""
        print("[ROI] Cancel ROI not supported for USV")

    def get_current_mode(self):
        """Get the current flight mode string"""
        try:
            heartbeat = self.connection.recv_match(
                type="HEARTBEAT", blocking=True, timeout=3
            )
            if heartbeat:
                return self.get_mode_string(heartbeat.custom_mode, heartbeat.type)
            return "UNKNOWN"
        except Exception:
            return "UNKNOWN"

    def start_mission(self):
        """Start the uploaded mission using the proper MAVLink protocol.

        Per the ArduPilot docs, the correct sequence is:
          1. Arm (if not already armed)
          2. Send MAV_CMD_MISSION_START via COMMAND_LONG
          3. Confirm via COMMAND_ACK + HEARTBEAT in AUTO mode

        Pauses the background recv loop for the duration so that
        HEARTBEAT and COMMAND_ACK messages are not consumed by run().
        The loop is always resumed in the finally block.
        """
        if not self.connection:
            print("[START_MISSION ERROR] No connection to vehicle")
            self.mission_status.emit("No connection to vehicle", False)
            return False

        self._operation_lock.acquire()
        self._pause_recv_loop()
        try:
            print("[START_MISSION] Starting mission sequence...")
            self.mission_status.emit("Starting mission...", True)

            EKF_REQUIRED_FLAGS = (
                mavutil.mavlink.EKF_ATTITUDE
                | mavutil.mavlink.EKF_VELOCITY_HORIZ
                | mavutil.mavlink.EKF_POS_HORIZ_ABS
            )

            def _drain_start_debug_messages(window_s=1.0):
                """Drain COMMAND_ACK/STATUSTEXT/HEARTBEAT for mission-start diagnostics."""
                end_time = time.time() + window_s
                while time.time() < end_time:
                    msg = self.connection.recv_match(
                        type=["COMMAND_ACK", "STATUSTEXT", "HEARTBEAT"],
                        blocking=True,
                        timeout=0.25,
                    )
                    if not msg:
                        continue

                    msg_type = msg.get_type()
                    if msg_type == "COMMAND_ACK":
                        print(
                            "[START_MISSION] COMMAND_ACK "
                            f"command={msg.command} result={msg.result}"
                        )
                    elif msg_type == "STATUSTEXT":
                        text = getattr(msg, "text", "")
                        severity = getattr(msg, "severity", "?")
                        print(f"[START_MISSION] STATUSTEXT severity={severity}: {text}")
                    elif msg_type == "HEARTBEAT":
                        mode = self.get_mode_string(msg.custom_mode, msg.type)
                        armed = bool(
                            msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                        )
                        print(
                            "[START_MISSION] HEARTBEAT "
                            f"mode={mode} (ID:{msg.custom_mode}) armed={armed}"
                        )

            def _wait_autonomous_ready(timeout_s=15.0):
                """Wait until GPS + EKF are ready for Rover AUTO mode."""
                deadline = time.time() + timeout_s
                last_fix = None
                last_sats = None
                last_flags = None

                while time.time() < deadline:
                    msg = self.connection.recv_match(
                        type=[
                            "GPS_RAW_INT",
                            "EKF_STATUS_REPORT",
                            "HEARTBEAT",
                            "STATUSTEXT",
                        ],
                        blocking=True,
                        timeout=0.5,
                    )
                    if not msg:
                        continue

                    msg_type = msg.get_type()
                    if msg_type == "GPS_RAW_INT":
                        last_fix = msg.fix_type
                        last_sats = msg.satellites_visible
                        print(
                            f"[START_MISSION] GPS fix_type={last_fix} sats={last_sats}"
                        )
                    elif msg_type == "EKF_STATUS_REPORT":
                        last_flags = msg.flags
                        print(
                            "[START_MISSION] EKF_STATUS_REPORT "
                            f"flags={last_flags} "
                            f"att={bool(last_flags & mavutil.mavlink.EKF_ATTITUDE)} "
                            f"vel_h={bool(last_flags & mavutil.mavlink.EKF_VELOCITY_HORIZ)} "
                            f"pos_h_abs={bool(last_flags & mavutil.mavlink.EKF_POS_HORIZ_ABS)}"
                        )
                    elif msg_type == "STATUSTEXT":
                        print(
                            f"[START_MISSION] STATUSTEXT severity={getattr(msg, 'severity', '?')}: {getattr(msg, 'text', '')}"
                        )

                    gps_ready = last_fix is not None and last_fix >= 3
                    ekf_ready = (
                        last_flags is not None
                        and (last_flags & EKF_REQUIRED_FLAGS) == EKF_REQUIRED_FLAGS
                    )

                    if gps_ready and ekf_ready:
                        print("[START_MISSION] GPS/EKF ready for AUTO mode")
                        return True

                print(
                    "[START_MISSION] GPS/EKF not ready for AUTO mode within timeout "
                    f"(last_fix={last_fix}, last_sats={last_sats}, last_flags={last_flags})"
                )
                return False

            # Step 1: Capture initial armed state
            heartbeat = self.connection.recv_match(
                type="HEARTBEAT", blocking=True, timeout=3
            )
            if not heartbeat:
                self.mission_status.emit("No heartbeat from vehicle", False)
                return False

            initially_armed = bool(
                heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
            )
            print(f"[START_MISSION] Initial armed state: {initially_armed}")

            # IMPORTANT WORKAROUND FOR ARDUPILOT ROVER / BOAT:
            # Rover becomes stricter about EKF position validity once the vehicle is
            # armed. In our VRX/SITL path this can leave EKF in const_pos_mode after
            # arming, which makes AUTO entry fail with "Flight mode change failed"
            # even though the mission upload succeeded.
            #
            # To preserve the previously working behavior, when the vehicle starts
            # disarmed we try to enter mission/AUTO BEFORE arming. If the vehicle is
            # already armed, we keep the stricter GPS/EKF gate before attempting AUTO.
            # Leave this comment in place until the underlying EKF/SITL cause is fixed.
            if initially_armed:
                print(
                    "[START_MISSION] Vehicle already armed — waiting for GPS/EKF readiness..."
                )
                self.mission_status.emit("Waiting for GPS/EKF readiness...", True)
                if not _wait_autonomous_ready(timeout_s=15.0):
                    self.mission_status.emit("GPS/EKF not ready for AUTO mode", False)
                    return False
            else:
                print(
                    "[START_MISSION] Vehicle disarmed — trying mission/AUTO before arming "
                    "(Rover EKF workaround)..."
                )

            # Step 2: Send MAV_CMD_MISSION_START (proper protocol per ArduPilot docs)
            # param1 = first_item (0 = start from beginning)
            # param2 = last_item  (0 = run to end)
            # Re-assert the first real mission item before starting. This protects
            # against stale mission state when replacing one mission with another
            # while the vehicle remains armed between tests.
            print("[START_MISSION] Re-applying mission current seq=1 before start...")
            self.connection.mav.mission_set_current_send(
                self.connection.target_system,
                self.connection.target_component,
                1,
            )
            self.msleep(200)

            print("[START_MISSION] Sending MAV_CMD_MISSION_START...")
            self.mission_status.emit("Sending mission start command...", True)
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_MISSION_START,
                0,  # confirmation
                0,  # param1: first_item (0 = from beginning)
                0,  # param2: last_item  (0 = to end)
                0,
                0,
                0,
                0,
                0,
            )

            _drain_start_debug_messages(window_s=1.0)

            # Step 3: Wait for COMMAND_ACK
            ack = self.connection.recv_match(
                type="COMMAND_ACK", blocking=True, timeout=5
            )
            auto_entered = False

            if ack and ack.command == mavutil.mavlink.MAV_CMD_MISSION_START:
                print(f"[START_MISSION] MISSION_START ACK result={ack.result}")
                if ack.result != 0:
                    print(
                        f"[START_MISSION] MAV_CMD_MISSION_START rejected (result={ack.result}), "
                        "falling back to AUTO mode switch..."
                    )
                    _drain_start_debug_messages(window_s=1.5)
                    # Fallback: set AUTO mode directly
                    if not self.set_mode("AUTO"):
                        self.mission_status.emit("Failed to set AUTO mode", False)
                        return False
                    auto_entered = True
            elif ack:
                print(
                    "[START_MISSION] Received unrelated COMMAND_ACK "
                    f"command={ack.command} result={ack.result}"
                )
            else:
                print("[START_MISSION] No COMMAND_ACK received for MISSION_START")
                _drain_start_debug_messages(window_s=1.5)

            # Step 4: Confirm vehicle is in AUTO mode via HEARTBEAT
            deadline = time.time() + 10
            while time.time() < deadline:
                hb = self.connection.recv_match(
                    type="HEARTBEAT", blocking=True, timeout=1
                )
                if hb:
                    mode = self.get_mode_string(hb.custom_mode, hb.type)
                    if mode == "AUTO":
                        auto_entered = True
                        print(
                            "[START_MISSION SUCCESS] Vehicle is in AUTO mode — mission running!"
                        )
                        break

            # If we couldn't confirm AUTO mode, try forcing it
            if not auto_entered:
                print(
                    "[START_MISSION] AUTO mode not confirmed — trying direct mode switch..."
                )
                if self.set_mode("AUTO"):
                    auto_entered = True
                else:
                    self.mission_status.emit(
                        "Mission start: could not confirm AUTO mode", False
                    )
                    return False

            # Step 5: If AUTO/mission entry succeeded while disarmed, arm afterward.
            if not initially_armed:
                print("[START_MISSION] AUTO entered while disarmed — arming now...")
                self.mission_status.emit("Arming vehicle after AUTO entry...", True)
                if not self.arm_vehicle():
                    self.mission_status.emit(
                        "Failed to arm vehicle after AUTO entry", False
                    )
                    return False

            self.mission_status.emit("Mission started — USV in AUTO mode", True)
            return True

        except Exception as e:
            error_msg = f"Exception during mission start: {e}"
            print(f"[START_MISSION ERROR] {error_msg}")
            self.mission_status.emit(error_msg, False)
            return False
        finally:
            self._resume_recv_loop()
            self._operation_lock.release()
