#!/usr/bin/env python3
import sys
import time
from PySide6.QtCore import QCoreApplication
from Vehicle.ArdupilotConnection import ArdupilotConnectionThread

class TestConnectionSignals:
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        
    def test_enhanced_connection(self):
        """Test the enhanced connection with signals"""
        print("Testing Enhanced ArdupilotConnection...")
        
        # Create a mock parent object
        class MockParent:
            def __init__(self):
                self.btn_connect = None
                self.homepage = MockHomePage()
                self.indicatorspage = None
                self.firebase = None
                
        class MockHomePage:
            def __init__(self):
                self.mapwidget = None
                self.cameraWidget = None
        
        # Create connection thread
        mock_parent = MockParent()
        connection_thread = ArdupilotConnectionThread(mock_parent)
        
        # Connect signals to test handlers
        connection_thread.connection_status.connect(self.on_connection_status)
        connection_thread.telemetry_update.connect(self.on_telemetry_update)
        connection_thread.mission_status.connect(self.on_mission_status)
        
        # Test connection string setting
        print("Testing connection string settings...")
        connection_thread.setConnectionString('SITL (UDP)')
        print(f"Connection string set to: {connection_thread.connection_string}")
        
        # Test baud rate setting
        connection_thread.setBaudRate(57600)
        print(f"Baud rate set to: {connection_thread.baudrate}")
        
        # Test mode string function
        print("Testing mode string conversion...")
        mode_string = connection_thread.get_mode_string(0, None)
        print(f"Mode 0 = {mode_string}")
        
        print("Enhanced connection test completed successfully!")
        
    def on_connection_status(self, connected, message):
        print(f"Connection Status: {'Connected' if connected else 'Disconnected'} - {message}")
        
    def on_telemetry_update(self, data):
        print(f"Telemetry Update: {data}")
        
    def on_mission_status(self, message, success):
        print(f"Mission Status: {message} ({'Success' if success else 'Failed'})")

if __name__ == "__main__":
    try:
        test = TestConnectionSignals()
        test.test_enhanced_connection()
        print("\n✅ All tests passed! Enhanced ArdupilotConnection is ready.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
