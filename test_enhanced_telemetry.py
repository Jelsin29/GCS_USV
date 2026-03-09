#!/usr/bin/env python3
"""
Test script for enhanced telemetry data flow
This script helps debug the telemetry data flow from ArdupilotConnection to widgets
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from MainWindow import MainWindow
from PySide6.QtWidgets import QApplication

def test_telemetry_flow():
    """Test the telemetry data flow with debug information"""
    app = QApplication(sys.argv)
    
    print("=== Enhanced Telemetry Test ===")
    print("1. Creating MainWindow...")
    
    # Create a mock firebase object for testing
    class MockFirebase:
        def __init__(self):
            self.connected = False
    
    mock_firebase = MockFirebase()
    
    # Create main window with firebase parameter
    main_window = MainWindow(mock_firebase)
    main_window.show()
    
    print("2. Checking widget availability...")
    
    # Check if telemetry widgets are available
    homepage_widget = None
    usv_widget = None
    
    if hasattr(main_window, 'homepage') and hasattr(main_window.homepage, 'telemetryWidget'):
        homepage_widget = main_window.homepage.telemetryWidget
        print(f"   ✓ HomePage TelemetryWidget found: {type(homepage_widget).__name__}")
        print(f"   - Has updateFromArduPilotData: {hasattr(homepage_widget, 'updateFromArduPilotData')}")
        print(f"   - Has setConnectionStatus: {hasattr(homepage_widget, 'setConnectionStatus')}")
        print(f"   - Has connected attribute: {hasattr(homepage_widget, 'connected')}")
    else:
        print("   ✗ HomePage TelemetryWidget not found")
    
    if hasattr(main_window, 'indicatorspage') and hasattr(main_window.indicatorspage, 'usv_telemetry'):
        usv_widget = main_window.indicatorspage.usv_telemetry
        print(f"   ✓ USVTelemetryWidget found: {type(usv_widget).__name__}")
        print(f"   - Has updateFromArduPilotData: {hasattr(usv_widget, 'updateFromArduPilotData')}")
        print(f"   - Has setConnectionStatus: {hasattr(usv_widget, 'setConnectionStatus')}")
        print(f"   - Has connected attribute: {hasattr(usv_widget, 'connected')}")
    else:
        print("   ✗ USVTelemetryWidget not found")
    
    print("3. Testing connection status updates...")
    
    # Test connection status updates
    if homepage_widget and hasattr(homepage_widget, 'setConnectionStatus'):
        homepage_widget.setConnectionStatus(True)
        print("   ✓ Set HomePage widget to connected")
    
    if usv_widget and hasattr(usv_widget, 'setConnectionStatus'):
        usv_widget.setConnectionStatus(True)
        print("   ✓ Set USV widget to connected")
    
    print("4. Testing telemetry data update...")
    
    # Create test telemetry data
    test_data = {
        'latitude': 40.7128,
        'longitude': -74.0060,
        'altitude': 5.0,
        'relative_alt': 5.0,
        'roll': 0.1,
        'pitch': 0.05,
        'yaw': 1.57,
        'groundspeed': 2.5,
        'heading': 90,
        'battery_voltage': 12.6,
        'battery_current': 1.2,
        'armed': True,
        'mode': 'AUTO'
    }
    
    # Test direct widget updates
    if homepage_widget and hasattr(homepage_widget, 'updateFromArduPilotData'):
        try:
            homepage_widget.updateFromArduPilotData(test_data)
            print("   ✓ HomePage widget updated successfully")
        except Exception as e:
            print(f"   ✗ HomePage widget update failed: {e}")
    
    if usv_widget and hasattr(usv_widget, 'updateFromArduPilotData'):
        try:
            usv_widget.updateFromArduPilotData(test_data)
            print("   ✓ USV widget updated successfully")
        except Exception as e:
            print(f"   ✗ USV widget update failed: {e}")
    
    print("5. Testing MainWindow telemetry conversion...")
    
    # Test MainWindow telemetry conversion
    try:
        vrx_data = main_window.convert_telemetry_to_vrx_format(test_data)
        print(f"   ✓ VRX conversion successful, keys: {list(vrx_data.keys())}")
    except Exception as e:
        print(f"   ✗ VRX conversion failed: {e}")
    
    print("6. Testing full telemetry update chain...")
    
    # Test the full update chain through MainWindow
    try:
        main_window.on_telemetry_update(test_data)
        print("   ✓ Full telemetry update chain completed")
    except Exception as e:
        print(f"   ✗ Full telemetry update failed: {e}")
    
    print("\n=== Test Summary ===")
    print("If you see checkmarks (✓) above, the telemetry system is working.")
    print("If you see X marks (✗), there are issues that need to be fixed.")
    print("\nTo test with real ArduPilot data:")
    print("1. Connect to your ArduPilot vehicle")
    print("2. The enhanced logging will show data flow in real-time")
    print("3. Check the terminal for DEBUG messages during connection")
    
    # Keep the window open for manual testing
    print("\nWindow is now open for manual testing. Close the window to exit.")
    app.exec()

if __name__ == "__main__":
    test_telemetry_flow()
