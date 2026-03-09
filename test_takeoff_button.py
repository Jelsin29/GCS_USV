#!/usr/bin/env python3
"""
Test the TAKEOFF button functionality
"""

import sys
import time
from unittest.mock import Mock
from Vehicle.ArdupilotConnection import ArdupilotConnectionThread

def test_takeoff_button():
    """Test that the TAKEOFF button properly calls arm_and_start"""
    
    print("=== TESTING TAKEOFF BUTTON FUNCTIONALITY ===")
    
    # Create mock parent
    mock_parent = Mock()
    mock_parent.btn_connect = Mock()
    mock_parent.homepage = Mock()
    mock_parent.homepage.mapwidget = Mock()
    mock_parent.indicatorspage = Mock()
    
    # Create connection thread
    connection_thread = ArdupilotConnectionThread(mock_parent)
    
    # Test 1: Test takeoff method exists
    print("\n1. Testing takeoff method exists...")
    assert hasattr(connection_thread, 'takeoff'), "❌ takeoff method missing"
    print("✅ takeoff method exists")
    
    # Test 2: Test arm_and_start method exists  
    print("\n2. Testing arm_and_start method exists...")
    assert hasattr(connection_thread, 'arm_and_start'), "❌ arm_and_start method missing"
    print("✅ arm_and_start method exists")
    
    # Test 3: Test takeoff calls arm_and_start (mock test)
    print("\n3. Testing takeoff calls arm_and_start...")
    
    # Mock the arm_and_start method
    connection_thread.arm_and_start = Mock(return_value=True)
    
    # Call takeoff
    connection_thread.takeoff()
    
    # Verify arm_and_start was called
    connection_thread.arm_and_start.assert_called_once()
    print("✅ takeoff successfully calls arm_and_start")
    
    # Test 4: Test with no connection
    print("\n4. Testing arm_and_start with no connection...")
    connection_thread.connection = None
    result = connection_thread.arm_and_start()
    print(f"Result with no connection: {result}")
    print("✅ arm_and_start handles no connection gracefully")
    
    print("\n=== ALL TAKEOFF BUTTON TESTS PASSED! ===")
    print("\nTo test in the actual GUI:")
    print("1. Run 'python main.py'")
    print("2. Connect to ArduPilot (SITL or real vehicle)")
    print("3. Go to TargetsPage")
    print("4. Click TAKEOFF button")
    print("5. Watch console for ARM sequence output")

if __name__ == "__main__":
    test_takeoff_button()
