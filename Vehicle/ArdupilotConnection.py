import math
import time

from pymavlink import mavutil
import pymavlink.dialects.v20.all as dialect

from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QPushButton, QInputDialog

from MapWidget import MapWidget
from CameraWidget import CameraWidget
from IndicatorsPage import IndicatorsPage
from Database.users_db import FirebaseUser
from Vehicle.Exploration import exploration

# Some Definitions for testing purpose
ALTITUDE = 15
FOV = 110


class MissionModes:
    EXPLORATION = 0
    WAYPOINTS = 1


def handleConnectedVehicle(connection, mapwidget, connectbutton):
    msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    position = [msg.lat / 1e7, msg.lon / 1e7]
    # Set connect button disable
    connectbutton.setText('Connected')
    connectbutton.setIcon(QIcon('../uifolder/assets/icons/24x24/cil-link.png'))
    connectbutton.setDisabled(True)

    # Fly to UAV's position
    mapwidget.page().runJavaScript(f'console.log("usv position: {position}")')
    mapwidget.page().runJavaScript(f"{mapwidget.map_variable_name}.flyTo({position})")

    # Add USV marker
    mapwidget.page().runJavaScript("""
                    var usvMarker = L.marker(
                                %s,
                                {icon: usvIcon,},).addTo(map);
                    """ % position
                                   )


def updateData(thread, vehicle, mapwidget, indicators, camerawidget, firebase):
    type_list = ['ATTITUDE', 'GLOBAL_POSITION_INT', 'VFR_HUD', 'SYS_STATUS', 'HEARTBEAT']

    # Read messages from the vehicle
    msg = vehicle.recv_match(type=type_list)
    if msg is not None:
        # Update indicators
        if msg.get_type() == 'GLOBAL_POSITION_INT':
            position = [msg.lat / 1e7, msg.lon / 1e7]
            heading = msg.hdg / 100
            altitude = msg.relative_alt / 1000.0

            # Update USV Data
            thread.latitude = position[0]
            thread.longitude = position[1]
            thread.altitude = altitude

            # Update indicators
            indicators.setAltitude(altitude)
            indicators.xpos_label.setText(f"Lat: {position[0]:.6f}")
            indicators.ypos_label.setText(f"Lon: {position[1]:.6f}")
            indicators.setHeading(heading)
            # Update USV marker
            mapwidget.page().runJavaScript(f"uavMarker.setLatLng({str(position)});")  # to set position of USV marker
            mapwidget.page().runJavaScript(
                f"uavMarker.setRotationAngle({heading - 45});")  # to set rotation of USV

            # Update Firebase USV Data
            firebase.marker_latitude = position[0]
            firebase.marker_longitude = position[1]

        if msg.get_type() == 'VFR_HUD':
            speed = msg.groundspeed
            indicators.setSpeed(speed)
            
        if msg.get_type() == 'ATTITUDE':
            pitch = msg.pitch
            roll = msg.roll
            indicators.setAttitude(pitch, roll)

        if msg.get_type() == 'SYS_STATUS':
            indicators.battery_label.setText(f"Battery: {msg.voltage_battery / 1e3}V")
            thread.parent.label_top_info_1.setText(f"Battery: {msg.battery_remaining}%      {msg.voltage_battery/1e3}V      {msg.current_battery}A")
        if msg.get_type() == 'HEARTBEAT':
            thread.last_heartbeat = time.time()
            flight_mode = mavutil.mode_string_v10(msg)
            indicators.flight_mode_label.setText(f"Mode: {flight_mode}")


def connectionLost(connectbutton, mapwidget):
    connectbutton.setText('Connect')
    connectbutton.setIcon(QIcon('../uifolder/assets/icons/24x24/cil-link-broken.png'))
    connectbutton.setDisabled(False)

    # Remove USV marker
    mapwidget.page().runJavaScript("""
                    map.removeLayer(uavMarker);
                    """
                                   )


class ArdupilotConnectionThread(QThread):
    vehicleConnected_signal = Signal(mavutil.mavudp, MapWidget, QPushButton)
    updateData_signal = Signal(QThread, mavutil.mavudp, MapWidget, IndicatorsPage, CameraWidget, FirebaseUser)
    connectionLost_signal = Signal(QPushButton, MapWidget)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.connection = None
        self.connection_string = None
        self.baudrate = None
        self.connectButton = parent.btn_connect
        self.mapwidget = parent.homepage.mapwidget
        self.indicators = parent.indicatorspage
        self.firebase = parent.targetspage.firebase

        # Telemetry Data
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0  # For surface vessels, this is typically 0

        # Variables
        self.home_position = [0,0]
        self.camera_angle = 45

        self.vehicleConnected_signal.connect(handleConnectedVehicle)
        self.updateData_signal.connect(updateData)
        self.connectionLost_signal.connect(connectionLost)

    # This method is called when the thread is started
    def run(self):
        timeout = 10  # seconds
        connected = False  # Flag to monitor connection status

        # For VRX/SITL testing, you can uncomment the following line
        # self.connection_string = "udp:127.0.0.1:14550"

        try:
            print(f"Connecting to vehicle on: {self.connection_string}")
            self.connection = mavutil.mavlink_connection(self.connection_string, baud=self.baudrate, autoreconnect=True,
                                                         timeout=timeout)
            print("Waiting for heartbeat...")
            if self.connection.wait_heartbeat(timeout=timeout):
                print("Connected to USV")
                connected = True
                self.vehicleConnected_signal.emit(self.connection, self.mapwidget, self.connectButton)
            else:
                print("Connection failed")
                connected = False
        except Exception as e:
            print(f"Failed to connect: {e}")
            connected = False

        if connected:
            while connected:
                try:
                    self.updateData_signal.emit(self, self.connection, self.mapwidget, self.indicators,
                                                self.parent.homepage.cameraWidget, self.firebase)
                    self.msleep(20)
                except Exception as e:
                    print(f"Error: {e}")
                    connected = False
            self.connectionLost_signal.emit(self.connectButton, self.mapwidget)

    def setBaudRate(self, baud):
        self.baudrate = baud  # 115200 on USB or 57600 on Radio/Telemetry

    def setConnectionString(self, connectionstring):
        if connectionstring == 'Telemetri':
            self.connection_string = '/dev/ttyUSB0'
        elif connectionstring == 'USB':
            self.connection_string = '/dev/ttyACM0'
        elif connectionstring == 'SITL (UDP)':
            self.connection_string = 'udp:127.0.0.1:14550'
        elif connectionstring == 'SITL (TCP)':
            self.connection_string = 'tcp:127.0.0.1:5760'
        elif connectionstring == 'VRX Simulation':  # New option for VRX
            self.connection_string = 'udp:127.0.0.1:14550'
        elif connectionstring == 'MAVROS Direct':
            self.connection_string = 'udp:127.0.0.1:14556' 
        elif connectionstring == 'UDP':
            text, ok = QInputDialog.getText(self.parent, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = f'udp:{text}:14550'
        elif connectionstring == 'TCP':
            text, ok = QInputDialog.getText(self.parent, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = f'tcp:{text}:5760'
        else:
            self.connection_string = connectionstring

    def goto_markers_pos(self, speed=-1):
        lat = float(self.mapwidget.map_page.markers_pos[0])
        lng = float(self.mapwidget.map_page.markers_pos[1])

        self.connection.set_mode_apm('GUIDED')
        self.move_to(lat, lng)

    def move_to(self, lat, lng, speed=5):
        lat = int(lat * 1e7)
        lng = int(lng * 1e7)
        # For USV, altitude is always 0
        alt = 0
        
        # Send command to move to the specified latitude, longitude
        self.connection.mav.command_int_send(
            self.connection.target_system,
            self.connection.target_component,
            dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            dialect.MAV_CMD_DO_REPOSITION,
            0,  # Current
            0,  # Autocontinue
            speed,
            0, 0, 0,  # Params 2-4 (unused)
            lat,
            lng,
            alt
        )

    def set_roi(self, alt=0):
        lat = int(float(self.mapwidget.map_page.markers_pos[0])*1e7)
        lng = int(float(self.mapwidget.map_page.markers_pos[1])*1e7)
        self.connection.mav.command_int_send(
            self.connection.target_system,
            self.connection.target_component,
            dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            dialect.MAV_CMD_DO_SET_ROI_LOCATION,
            0,  # Current
            0,  # Autocontinue
            0, 0, 0, 0,  # Params 2-4 (unused)
            lat,
            lng,
            alt  # Altitude
        )

    def cancel_roi_mode(self):
        # Cancel the ROI mode.
        self.connection.mav.command_int_send(
            self.connection.target_system,
            self.connection.target_component,
            0,
            dialect.MAV_CMD_DO_SET_ROI_NONE,
            0, 0,
            0, 0, 0, 0,
            0, 0, 0
        )

    def hold_position(self):
        """USV equivalent of land - hold current position"""
        print("Holding position (switching to HOLD mode)")
        self.connection.set_mode('HOLD')

    def rtl(self):
        print("Returning to Launch")
        self.connection.set_mode('RTL')

    def arm_and_start(self): 
        """USV equivalent of takeoff - just arm and switch to GUIDED mode"""
        print("Arming USV...")
        self.connection.set_mode('GUIDED')
        
        # Send arm command
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0) # 1 to arm

        # Wait for the vehicle to be armed
        print("Waiting for USV to arm...")
        self.connection.motors_armed_wait()
        print("USV Armed and Ready.")

        self.set_home_position(self.latitude, self.longitude)

    def set_home_position(self, lat, lng):
        self.home_position[0] = lat
        self.home_position[1] = lng

    def start_mission(self):
        self.connection.set_mode('GUIDED')
        # Arm the USV
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0) # 1 to arm
        
        print("Waiting for USV to arm...")
        self.connection.motors_armed_wait()
        print("USV armed, starting mission.")
        self.connection.set_mode('AUTO')

        time.sleep(0.2)
        speed = 5
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            0,
            0, speed, -1, 0,
            0, 0, 0)

    def set_mission(self, mission_mode, waypoints, altitude=0):
        print("Setting mission for USV")
        if mission_mode == MissionModes.EXPLORATION:
            waypoints = exploration(self, waypoints[0], waypoints[1], altitude, FOV)
            self.upload_mission(waypoints)
            # Put waypoints on map
            for wp in waypoints:
                self.mapwidget.page().runJavaScript(f"putWaypoint({wp[0]}, {wp[1]});")

        elif mission_mode == MissionModes.WAYPOINTS:
            self.upload_mission(waypoints)

    def clear_mission(self):
        self.connection.mav.mission_clear_all_send(
            self.connection.target_system,
            self.connection.target_component,
            mission_type=dialect.MAV_MISSION_TYPE_MISSION
        )

    def upload_mission(self, waypoints, speed=5):
        self.clear_mission()

        # USV mission is simpler - just waypoints on the water surface
        mission_items = []

        # Upload waypoints
        for i, item in enumerate(waypoints):
            self.connection.mav.mission_item_int_send(
                self.connection.target_system,
                self.connection.target_component,
                i, # Sequence number
                dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                dialect.MAV_CMD_NAV_WAYPOINT,
                1 if i == 0 else 0,  # current = true for first waypoint, false for others
                1,  # auto continue
                0, 0, 0, 0,  # params 1-4 (hold, acceptance radius, pass radius, yaw)
                int(item[0] * 1e7),
                int(item[1] * 1e7),
                0) # Altitude for USV is always 0

        self.set_home_position(self.latitude, self.longitude)
        print("USV mission uploaded successfully.")

    # Compatibility methods - keep the old names for existing UI code
    def takeoff(self, target_altitude=0):
        """Compatibility wrapper - calls arm_and_start for USV"""
        self.arm_and_start()
        
    def land(self):
        """Compatibility wrapper - calls hold_position for USV"""
        self.hold_position()