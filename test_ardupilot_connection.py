#!/usr/bin/env python3
"""
ArduPilot Connection Test Script
Use this to verify your ArduPilot SITL is sending telemetry data
"""

import time
from pymavlink import mavutil

def test_ardupilot_connection():
    """Test connection to ArduPilot and display incoming data"""
    
    # Connection string - adjust as needed
    connection_string = 'udp:127.0.0.1:14550'  # Default SITL UDP
    
    print(f"Attempting to connect to ArduPilot at {connection_string}")
    print("Make sure you have started ArduPilot SITL with:")
    print("sim_vehicle.py -v Rover --model rover --add-param-file=usv_params.param --console --map")
    print("-" * 60)
    
    try:
        # Create connection
        connection = mavutil.mavlink_connection(connection_string, baud=115200)
        
        # Wait for heartbeat
        print("Waiting for heartbeat...")
        if connection.wait_heartbeat(timeout=10):
            print("✓ Heartbeat received - ArduPilot is connected!")
            print(f"System ID: {connection.target_system}")
            print(f"Component ID: {connection.target_component}")
        else:
            print("✗ No heartbeat received - check ArduPilot connection")
            return False
            
        print("\nReceiving telemetry data (press Ctrl+C to stop):")
        print("-" * 60)
        
        # Message types we want to monitor
        message_types = ['GLOBAL_POSITION_INT', 'VFR_HUD', 'ATTITUDE', 'SYS_STATUS', 'HEARTBEAT']
        
        message_count = {}
        start_time = time.time()
        
        while True:
            # Read message
            msg = connection.recv_match(type=message_types, blocking=False)
            
            if msg is not None:
                msg_type = msg.get_type()
                
                # Count messages
                if msg_type not in message_count:
                    message_count[msg_type] = 0
                message_count[msg_type] += 1
                
                # Print specific data based on message type
                if msg_type == 'GLOBAL_POSITION_INT':
                    lat = msg.lat / 1e7
                    lon = msg.lon / 1e7
                    alt = msg.relative_alt / 1000.0
                    print(f"GPS: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.1f}m")
                    
                elif msg_type == 'VFR_HUD':
                    speed = msg.groundspeed
                    heading = msg.heading
                    print(f"MOTION: Speed={speed:.1f}m/s, Heading={heading:.0f}°")
                    
                elif msg_type == 'ATTITUDE':
                    roll = msg.roll * 57.2958  # rad to deg
                    pitch = msg.pitch * 57.2958
                    yaw = msg.yaw * 57.2958
                    print(f"ATTITUDE: Roll={roll:.1f}°, Pitch={pitch:.1f}°, Yaw={yaw:.1f}°")
                    
                elif msg_type == 'SYS_STATUS':
                    battery_pct = msg.battery_remaining
                    voltage = msg.voltage_battery / 1000.0
                    current = msg.current_battery / 100.0
                    print(f"POWER: Battery={battery_pct}%, Voltage={voltage:.1f}V, Current={current:.1f}A")
                    
                elif msg_type == 'HEARTBEAT':
                    mode = mavutil.mode_string_v10(msg)
                    print(f"STATUS: Mode={mode}, Armed={bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)}")
            
            # Print summary every 5 seconds
            if time.time() - start_time > 5:
                print(f"\nMessage counts in last 5 seconds: {message_count}")
                message_count = {}
                start_time = time.time()
                print("-" * 60)
            
            time.sleep(0.1)  # Small delay
            
    except KeyboardInterrupt:
        print("\nConnection test stopped by user")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("ArduPilot Connection Test")
    print("=" * 30)
    
    success = test_ardupilot_connection()
    
    if success:
        print("\n✓ Connection test completed successfully")
        print("Your ArduPilot SITL is working correctly")
        print("The GCS should be able to connect and receive real data")
    else:
        print("\n✗ Connection test failed")
        print("Check that ArduPilot SITL is running and accessible")