from PySide6.QtGui import QPixmap, QImage, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, \
    QPushButton, QSpacerItem, QSizePolicy, QInputDialog, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QEvent, QTimer, QByteArray, QBuffer, QIODevice

from uifolder import Ui_TargetsPage
from MapWidget import image_to_base64
from MediaPlayer import MediaPlayerWindow
from Database.Cloud import UpdateUserMenuThread
from Vehicle.ArdupilotConnection import MissionModes


def qimage_to_base64(qimage, image_format="PNG"):
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    image = qimage.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    image.save(buffer, image_format)
    base64_data = byte_array.toBase64().data().decode("utf-8")
    return base64_data


class TargetsPage(QWidget, Ui_TargetsPage):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent

        # **NEW: Add shadow effects after UI setup**
        self.addShadowEffects()

        # **SAFE: Mission Control Button Connections with error handling**
        try:
            # Mission buttons
            if hasattr(self, 'btn_chooseMode'):
                self.btn_chooseMode.clicked.connect(self.buttonFunctions)
            if hasattr(self, 'btn_undo'):
                self.btn_undo.clicked.connect(self.buttonFunctions)
            if hasattr(self, 'btn_clearAll'):
                self.btn_clearAll.clicked.connect(self.buttonFunctions)
            if hasattr(self, 'btn_setMission'):
                self.btn_setMission.clicked.connect(self.set_mission)
            if hasattr(self, 'btn_antenna'):
                self.btn_antenna.clicked.connect(self.run_antenna_tracker)
            if hasattr(self, 'btn_startMission'):
                self.btn_startMission.clicked.connect(self.start_mission)
            if hasattr(self, 'btn_abort'):
                self.btn_abort.clicked.connect(self.abort)
            if hasattr(self, 'btn_rtl'):
                self.btn_rtl.clicked.connect(self.rtl)
            
            # **NEW: Guided Control Button Connections**
            if hasattr(self, 'btn_takeoff'):
                self.btn_takeoff.clicked.connect(self.takeoff)
            if hasattr(self, 'btn_move'):
                self.btn_move.clicked.connect(self.move_to_point)
            if hasattr(self, 'btn_track_all'):
                self.btn_track_all.clicked.connect(self.track_all)
            if hasattr(self, 'btn_land'):
                self.btn_land.clicked.connect(self.land)
            if hasattr(self, 'btn_rtl_2'):
                self.btn_rtl_2.clicked.connect(self.rtl_2)
            if hasattr(self, 'btn_set_roi'):
                self.btn_set_roi.clicked.connect(self.set_roi)
            if hasattr(self, 'btn_cancel_roi'):
                self.btn_cancel_roi.clicked.connect(self.cancel_roi)
            
            print("TargetsPage: All mission and guided control buttons connected")
            
        except Exception as e:
            print(f"TargetsPage: Error connecting buttons: {e}")

        # Firebase Thread (if needed for mobile connections - optional now)
        self.firebase = self.parent.firebase if self.parent else None

    # **NEW: Mission Control Methods (moved from HomePage)**
    def buttonFunctions(self):
        if not hasattr(self, 'modes_comboBox'):
            print("Error: modes_comboBox not found in UI - cannot process mode selection")
            return
            
        button = self.sender()
        
        if not self.parent or not hasattr(self.parent, 'homepage'):
            print("Error: Parent or homepage not available")
            return

        try:
            if button.objectName() == "btn_chooseMode":
                current_mode = self.modes_comboBox.currentText()
                print(f"Selected mode: {current_mode}")
                
                if current_mode == "Marker Mode":
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.on('click', moveMarkerByClick);")
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.off('click', drawRectangle);")
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.off('click', putWaypointEvent);")
                    
                elif current_mode == "Area Selection Mode":
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.off('click', putWaypointEvent);")
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.off('click', moveMarkerByClick);")
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.on('click', drawRectangle);")
                    
                elif current_mode == "Waypoint Mode":
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.off('click', moveMarkerByClick);")
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.off('click', drawRectangle);")
                    self.parent.homepage.mapwidget.page().runJavaScript(f"map.on('click', putWaypointEvent);")
                    
            elif button.objectName() == "btn_clearAll":
                self.parent.homepage.mapwidget.page().runJavaScript(f"clearAll();")
                print("Cleared all map elements")
                
            elif button.objectName() == "btn_undo":
                self.parent.homepage.mapwidget.page().runJavaScript("undoWaypoint();")
                print("Undid last waypoint")
                
        except Exception as e:
            print(f"Error in buttonFunctions: {e}")

    def set_mission(self):
        if not hasattr(self, 'modes_comboBox'):
            print("Error: modes_comboBox not found in UI - cannot set mission")
            return
            
        if not self.parent or not hasattr(self.parent, 'homepage') or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent, homepage, or connectionThread not available")
            return

        try:
            altitude, okPressed = QInputDialog.getText(self, "Enter Altitude", "Altitude:", text="10")
            
            if okPressed and altitude:
                altitude = int(altitude)
                current_mode = self.modes_comboBox.currentText()
                print(f"Setting mission with altitude: {altitude}m, mode: {current_mode}")
                
                if current_mode == 'Waypoint Mode':
                    self.parent.homepage.mapwidget.page().runJavaScript("setMission(1);")
                    QTimer().singleShot(1000, lambda: self.parent.connectionThread.set_mission(
                        MissionModes.WAYPOINTS, 
                        self.parent.homepage.mapwidget.mission, 
                        altitude
                    ))
                else:
                    self.parent.homepage.mapwidget.page().runJavaScript("setMission(0);")
                    QTimer().singleShot(1000, lambda: self.parent.connectionThread.set_mission(
                        MissionModes.EXPLORATION, 
                        self.parent.homepage.mapwidget.mission, 
                        altitude
                    ))
                    
        except ValueError:
            print("Error: Invalid altitude value")
        except Exception as e:
            print(f"Error setting mission: {e}")

    def run_antenna_tracker(self):
        if not self.parent or not hasattr(self.parent, 'homepage') or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent, homepage, or connectionThread not available")
            return
            
        try:
            import threading
            # Import here to avoid circular imports
            from AntennaTracker import AntennaTracker, antenna_tracker
            
            # Create antenna tracker instance with default coordinates
            antenna = AntennaTracker(-35.3635, 149.1652)
            lat, lon = antenna.get_location()
            
            print(f"Starting antenna tracker at coordinates: {lat}, {lon}")
            
            # Add home marker to map
            self.parent.homepage.mapwidget.page().runJavaScript("""
                            var homeMarker = L.marker(
                                        %s,
                                        {icon: homeIcon,},).addTo(map);
                            """ % [lat, lon]
                                           )

            # Start antenna tracker in separate thread
            threading.Thread(target=antenna_tracker, args=(antenna, self.parent.connectionThread)).start()
            
            # Disable antenna button to prevent multiple instances
            if hasattr(self, 'btn_antenna'):
                self.btn_antenna.setDisabled(True)
                print("Antenna tracking started - button disabled")
                
        except ImportError as e:
            print(f"Error importing antenna tracker: {e}")
        except Exception as e:
            print(f"Error starting antenna tracker: {e}")

    def start_mission(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            self.parent.connectionThread.start_mission()
            print("Mission started")
        except Exception as e:
            print(f"Error starting mission: {e}")

    def abort(self):
        if not self.parent or not hasattr(self.parent, 'homepage'):
            print("Error: Parent or homepage not available")
            return
            
        try:
            if hasattr(self.parent.homepage, 'cameraWidget') and hasattr(self.parent.homepage.cameraWidget, 'videothread'):
                self.parent.homepage.cameraWidget.videothread.sendMessage("abort")
                print("Abort signal sent to camera widget")
            else:
                print("Warning: Camera widget or video thread not available")
        except Exception as e:
            print(f"Error sending abort signal: {e}")

    def rtl(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            if hasattr(self.parent.connectionThread, 'connection'):
                self.parent.connectionThread.connection.set_mode_apm("QRTL")
                print("Return to Launch (RTL) mode activated")
            else:
                print("Warning: Connection not available")
        except Exception as e:
            print(f"Error activating RTL mode: {e}")

    # **NEW: Guided Control Methods**
    def takeoff(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            altitude, okPressed = QInputDialog.getText(self, "Enter Altitude", "Altitude:", text="10")
            if okPressed and altitude:
                self.parent.connectionThread.takeoff(int(altitude))
                print(f"Takeoff command sent with altitude: {altitude}m")
        except ValueError:
            print("Error: Invalid altitude value")
        except Exception as e:
            print(f"Error with takeoff: {e}")

    def move_to_point(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            self.parent.connectionThread.goto_markers_pos()
            print("Move to marker position command sent")
        except Exception as e:
            print(f"Error moving to point: {e}")

    def track_all(self):
        if not self.parent or not hasattr(self.parent, 'homepage'):
            print("Error: Parent or homepage not available")
            return
            
        try:
            if hasattr(self.parent.homepage, 'cameraWidget') and hasattr(self.parent.homepage.cameraWidget, 'videothread'):
                self.parent.homepage.cameraWidget.videothread.sendMessage("track -1")
                print("Track all command sent to camera widget")
            else:
                print("Warning: Camera widget or video thread not available")
        except Exception as e:
            print(f"Error with track all: {e}")

    def land(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            self.parent.connectionThread.land()
            print("Land command sent")
        except Exception as e:
            print(f"Error with land command: {e}")

    def rtl_2(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            self.parent.connectionThread.rtl()
            print("RTL command sent (alternative)")
        except Exception as e:
            print(f"Error with RTL command: {e}")

    def set_roi(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            self.parent.connectionThread.set_roi()
            print("Set ROI command sent")
        except Exception as e:
            print(f"Error setting ROI: {e}")

    def cancel_roi(self):
        if not self.parent or not hasattr(self.parent, 'connectionThread'):
            print("Error: Parent or connectionThread not available")
            return
            
        try:
            self.parent.connectionThread.cancel_roi_mode()
            print("Cancel ROI command sent")
        except Exception as e:
            print(f"Error canceling ROI: {e}")

    def addShadowEffects(self):
        """Add modern shadow effects to frames for clean card appearance"""
        try:
            # Mission Frame Shadow
            if hasattr(self, 'missionFrame'):
                mission_shadow = QGraphicsDropShadowEffect()
                mission_shadow.setBlurRadius(20)
                mission_shadow.setXOffset(0)
                mission_shadow.setYOffset(4)
                mission_shadow.setColor(QColor(0, 0, 0, 40))  # Light shadow
                self.missionFrame.setGraphicsEffect(mission_shadow)

            # Guided Frame Shadow
            if hasattr(self, 'guidedFrame'):
                guided_shadow = QGraphicsDropShadowEffect()
                guided_shadow.setBlurRadius(20)
                guided_shadow.setXOffset(0)
                guided_shadow.setYOffset(4)
                guided_shadow.setColor(QColor(0, 0, 0, 40))  # Light shadow
                self.guidedFrame.setGraphicsEffect(guided_shadow)

            # Console Frame Shadow - Darker for dark background
            if hasattr(self, 'consoleFrame'):
                console_shadow = QGraphicsDropShadowEffect()
                console_shadow.setBlurRadius(25)
                console_shadow.setXOffset(0)
                console_shadow.setYOffset(6)
                console_shadow.setColor(QColor(0, 0, 0, 60))  # Slightly darker shadow
                self.consoleFrame.setGraphicsEffect(console_shadow)

            print("TargetsPage: Shadow effects applied successfully to frames only")
            
        except Exception as e:
            print(f"TargetsPage: Error applying shadow effects: {e}")

    def addButtonHoverEffects(self):
        """Remove button shadow effects - buttons should only have borders"""
        try:
            # No shadow effects for buttons - they keep their borders from CSS
            print("TargetsPage: Button styling handled by CSS borders only")
                    
        except Exception as e:
            print(f"TargetsPage: Error in button effects: {e}")

    # **DEBUGGING: Method to check what UI elements are available**
    def debug_ui_elements(self):
        print("=== TargetsPage UI Elements Debug ===")
        ui_elements = [
            'btn_chooseMode', 'btn_undo', 'btn_clearAll', 'btn_setMission',
            'btn_antenna', 'btn_startMission', 'btn_abort', 'btn_rtl',
            'modes_comboBox'
        ]
        
        for element in ui_elements:
            has_element = hasattr(self, element)
            print(f"{element}: {'✓' if has_element else '✗'}")
        
        print("=====================================")

    # **OPTIONAL: Keep these if you want some target functionality in the future**
    def addTarget(self, image, position, time_interval, no):
        """Add target method for compatibility with VideoStreamThread"""
        print(f"Target detected: ID {no} at position {position} at time {time_interval}")
        # Since this is now mission control, you can either:
        # 1. Log the target detection
        # 2. Add it to a mission log
        # 3. Or simply ignore it
        pass

    def addUsers(self):
        """
        Optional method for adding users (currently disabled)
        Can be implemented later if user management is needed
        """
        pass

    # **EVENT HANDLING: Override for debugging**
    def showEvent(self, event):
        """Called when the page is shown"""
        super().showEvent(event)
        print("TargetsPage (Mission Control) is now visible")
        
        # **NEW: Apply additional effects when page is shown**
        QTimer.singleShot(100, self.addButtonHoverEffects)  # Delay to ensure UI is ready

    def hideEvent(self, event):
        """Called when the page is hidden"""
        super().hideEvent(event)
        print("TargetsPage (Mission Control) is now hidden")


# **REMOVED: UserMenu class - can be added back if needed**
# class UserMenu(QWidget):
#     def __init__(self, parent, image, position, time, no):
#         # Implementation would go here
#         pass