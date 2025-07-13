import threading

import math
import serial

import time
from pymavlink import mavutil


class AntennaTracker:
    def __init__(self, latitude, longitude):
        self.arduino = None

        self.heading = 0
        self.flag = 0
        self.memory_x = 0
        self.last_time = time.time()
        self.delay_interval = 0.3

        self.vehicle_lat, self.vehicle_lon, self.vehicle_alt = 0, 0, 0
        self.antenna_lat, self.antenna_lon, self.antenna_alt = latitude, longitude, 0.0  # AntennaTracker's fixed coordinates
        self.angle_x, self.angle_y = 0, 0

        self.default_heading = self.heading

        # test cases for calculate_servo_angles 41.2563 28.7424
        # 41.2693 28.7419 90 degrees front
        # 41.2622 28.7526 45 degrees right
        # 41.2619 28.7339 45 degrees left
        # 41.2441 28.7423 90 degrees back
        # 41.2470 28.7562 45 degrees right back

    def calculate_servo_angles(self):
        # Latitude and longitude differences
        delta_lat = math.radians(self.vehicle_lat - self.antenna_lat)
        delta_lon = math.radians(self.vehicle_lon - self.antenna_lon)

        # Convert antenna and vehicle's latitude and longitude to radians
        lat1 = math.radians(self.antenna_lat)
        lat2 = math.radians(self.vehicle_lat)

        # Find horizontal distance (Haversine Formula)
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        earth_radius = 6371000  # Earth's radius (meters)
        horizontal_distance = earth_radius * c

        # Azimuth angle
        angle_x = math.degrees(math.atan2(delta_lon, delta_lat))

        # Altitude difference
        delta_alt = self.vehicle_alt - self.antenna_alt

        # Elevation angle
        angle_y = math.degrees(math.atan2(delta_alt, horizontal_distance))

        self.angle_x, self.angle_y = angle_x, angle_y
        return angle_x, angle_y

    def set_heading(self, heading):
        self.heading = heading

    def set_default_heading(self, heading):
        self.default_heading = heading

    def set_arduino(self, arduino):
        self.arduino = arduino

    def send_servo_angles(self):
        offset = 3
        target = (self.default_heading + self.angle_x + 360) % 360
        delta = target - self.heading
        print("default heading: ", self.default_heading)
        print("target: ", target)
        print("delta: ", delta)

        changed_y = int(140 - (self.angle_y / 180) * 140)
        # changed_y = 90

        ## still the 360 degree thing doesn't work properly
        # calculation for the arduino 360 degree servo (180 anticlockwise - 0 clockwise - 90 stop) (reversed because it's a geared system)
        if delta > -offset and delta < offset:
            changed_x = 90
            print("stop")
        else:

            if abs(delta) > 180:
                if delta > 0:
                    changed_x = 60
                    print("anticlockwise")
                else:
                    changed_x = 120
                    print("clockwise")
            else:
                if delta < 0:
                    changed_x = 60
                    print("anticlockwise")
                else:
                    changed_x = 120
                    print("clockwise")

        # if  self.memory_x != changed_x :
        #   self.memory_x = changed_x
        # if time.time() - self.last_time > self.delay_interval:

        self.arduino.write(changed_x.to_bytes(1, 'little') + changed_y.to_bytes(1, 'little') + b'\n')

        response = self.arduino.readline().decode('utf-8').strip()
        print(f"[ARDUINO] {response}")

        print(f"Servos: x = {self.angle_x}, y = {self.angle_y}")

        # test cases for calculate_servo_angles 41.2563 28.7424
        # 41.2693 28.7419 90 degrees front
        # 41.2622 28.7526 45 degrees right
        # 41.2619 28.7339 45 degrees left
        # 41.2441 28.7423 90 degrees back
        # 41.2470 28.7562 45 degrees right back

    def set_vehicle_gps(self, vehicle_lat, vehicle_lon, vehicle_alt):
        self.vehicle_lat, self.vehicle_lon, self.vehicle_alt = vehicle_lat, vehicle_lon, vehicle_alt

    def set_antenna_gps(self, antenna_lat, antenna_lon, antenna_alt):
        self.antenna_lat, self.antenna_lon, self.antenna_alt = antenna_lat, antenna_lon, antenna_alt

    def input_vehicle_gps(self):
        vehicle_lat, vehicle_lon = input("Enter vehicle's latitude and longitude: ").split()
        self.vehicle_lat, self.vehicle_lon = float(vehicle_lat), float(vehicle_lon)
        return self.vehicle_lat, self.vehicle_lon, 0

    def get_location(self):
        return self.antenna_lat, self.antenna_lon

    def track(self, heading, vehicle_lat, vehicle_lon, vehicle_alt):
        self.set_heading(heading)
        self.set_vehicle_gps(vehicle_lat, vehicle_lon, vehicle_alt)
        self.calculate_servo_angles()
        self.send_servo_angles()


# This method is called when the thread is started
def update_heading(pixhawk):
    # Only get 'VFR_HUD' messages with a filter
    msg = pixhawk.recv_match(type='VFR_HUD', blocking=True)
    if msg:
        heading = msg.heading  # Compass direction
        print(f"Current Compass Direction (heading): {heading} degrees")
        return heading
    else:
        print("VFR_HUD message could not be received. If default position was not received, program should be restarted!")
        return None


def get_gps_data(pixhawk, antenna):
    # Only get 'GLOBAL_POSITION_INT' messages with a filter
    msg = pixhawk.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg:
        lat = msg.lat  # Compass direction
        lon = msg.lon
        # antenna.set_antenna_gps(lat, lon, 0)
        return lat, lon
    else:
        print("GPS could not be received")
        return None


def antenna_tracker(antenna, vehicle):
    timeout = 10  # seconds
    connected = False  # Flag to monitor connection status

    try:
        # Creating MAVLink connection (enter the serial port where Pixhawk is connected)
        pixhawk = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200, autoreconnect=True)
        try:
            arduino = serial.Serial('/dev/ttyUSB0', 115200)
        except Exception as e:
            arduino = serial.Serial('/dev/ttyUSB1', 115200)

        # Wait for the first message to initiate communication
        if pixhawk.wait_heartbeat():
            print("Connection established with Pixhawk!")
            connected = True
        else:
            print("Connection failed")
            connected = False
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    heading = update_heading(pixhawk)
    get_gps_data(pixhawk, antenna)
    antenna.set_default_heading(heading)
    antenna.set_arduino(arduino)
    print("lat:", antenna.antenna_lat, "lng:", antenna.antenna_lon)

    time.sleep(2)

    last_time = time.time()
    delay_interval = 0.01

    if connected:
        while connected:
            try:
                if time.time() - last_time > delay_interval:
                    heading = update_heading(pixhawk)
                    antenna.track(heading, vehicle.latitude, vehicle.longitude, vehicle.altitude)
                    last_time = time.time()
                    time.sleep(.05)

            except Exception as e:
                print(f"Error: {e}")
                connected = False


# Test
if __name__ == "__main__":
    class Vehicle:
        latitude = 37.5841412
        longitude = 36.8361289
        altitude = 0


    vehicle = Vehicle()
    antenna = AntennaTracker()
    threading.Thread(target=antenna_tracker, args=(antenna, vehicle)).start()

    while True:
        time.sleep(0.01)
