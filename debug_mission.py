#!/usr/bin/env python3
"""
Debug Mission System
This script helps diagnose mission upload and start issues
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from MainWindow import MainWindow
from PySide6.QtWidgets import QApplication

def debug_mission_system():
    """Debug the mission upload and start system"""
    app = QApplication(sys.argv)
    
    print("=== Mission System Debug ===")
    
    # Create a mock firebase object
    class MockFirebase:
        def __init__(self):
            self.connected = False
    
    mock_firebase = MockFirebase()
    
    # Create main window
    main_window = MainWindow(mock_firebase)
    main_window.show()
    
    print("1. Checking connection thread status...")
    connection_thread = main_window.connectionThread
    
    if hasattr(connection_thread, 'connection') and connection_thread.connection:
        print("   ✓ Connection thread has active connection")
        print(f"   - Target system: {connection_thread.connection.target_system}")
        print(f"   - Target component: {connection_thread.connection.target_component}")
        
        # Check current GPS position
        if hasattr(connection_thread, 'latitude') and hasattr(connection_thread, 'longitude'):
            print(f"   - Current GPS: {connection_thread.latitude:.6f}, {connection_thread.longitude:.6f}")
            
            if connection_thread.latitude == 0.0 and connection_thread.longitude == 0.0:
                print("   ⚠️  WARNING: No GPS position available (0,0)")
            else:
                print("   ✓ GPS position available")
        
        # Test mission upload with simple waypoints
        print("\n2. Testing mission upload...")
        test_waypoints = [
            [connection_thread.latitude + 0.001, connection_thread.longitude + 0.001],
            [connection_thread.latitude + 0.002, connection_thread.longitude + 0.001],
            [connection_thread.latitude + 0.002, connection_thread.longitude + 0.002]
        ]
        
        print(f"   - Test waypoints: {len(test_waypoints)} points")
        for i, wp in enumerate(test_waypoints):
            print(f"     {i+1}: {wp[0]:.6f}, {wp[1]:.6f}")
        
        # Test the mission upload
        success = connection_thread.upload_mission(test_waypoints, auto_start=False)
        
        if success:
            print("   ✓ Mission upload test successful")
            
            print("\n3. Testing mission verification...")
            # Check if mission was actually uploaded
            connection_thread.connection.mav.mission_request_list_send(
                connection_thread.connection.target_system,
                connection_thread.connection.target_component,
                0  # MAV_MISSION_TYPE_MISSION
            )
            
            # Wait for mission count response
            msg = connection_thread.connection.recv_match(type='MISSION_COUNT', blocking=True, timeout=5)
            if msg:
                print(f"   ✓ Mission count on vehicle: {msg.count}")
                if msg.count >= len(test_waypoints) + 1:  # +1 for home
                    print("   ✓ Mission count looks correct")
                else:
                    print(f"   ⚠️  Expected {len(test_waypoints) + 1}, got {msg.count}")
            else:
                print("   ✗ No mission count response from vehicle")
            
            print("\n4. Testing mission start...")
            start_success = connection_thread.start_mission()
            
            if start_success:
                print("   ✓ Mission start successful")
            else:
                print("   ✗ Mission start failed")
                
        else:
            print("   ✗ Mission upload test failed")
    else:
        print("   ✗ No active connection found")
        print("   → Connect to ArduPilot first, then run this debug script")
    
    print("\n=== Debug Summary ===")
    print("Check the output above for any issues:")
    print("- GPS position should not be (0, 0)")
    print("- Mission upload should succeed")
    print("- Mission count on vehicle should match uploaded waypoints")
    print("- Mission start should succeed after upload")
    
    print("\nClose the window to exit debug mode.")
    app.exec()

if __name__ == "__main__":
    debug_mission_system()
