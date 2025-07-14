from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, \
    QPushButton, QSpacerItem, QSizePolicy, QInputDialog
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

        # **SAFE: Mission Control Button Connections with error handling**
        try:
            if hasattr(self, 'btn_chooseMode'):
                self.btn_chooseMode.clicked.connect(self.buttonFunctions)
            else:
                print("Warning: btn_chooseMode not found in UI")
                
            if hasattr(self, 'btn_undo'):
                self.btn_undo.clicked.connect(self.buttonFunctions)
            else:
                print("Warning: btn_undo not found in UI")
                
            if hasattr(self, 'btn_clearAll'):
                self.btn_clearAll.clicked.connect(self.buttonFunctions)
            else:
                print("Warning: btn_clearAll not found in UI")
                
            if hasattr(self, 'btn_setMission'):
                self.btn_setMission.clicked.connect(self.set_mission)
            else:
                print("Warning: btn_setMission not found in UI")
                
            if hasattr(self, 'btn_antenna'):
                self.btn_antenna.clicked.connect(self.run_antenna_tracker)
            else:
                print("Warning: btn_antenna not found in UI")
                
            if hasattr(self, 'btn_startMission'):
                self.btn_startMission.clicked.connect(self.start_mission)
            else:
                print("Warning: btn_startMission not found in UI")
                
            if hasattr(self, 'btn_abort'):
                self.btn_abort.clicked.connect(self.abort)
            else:
                print("Warning: btn_abort not found in UI")
                
            if hasattr(self, 'btn_rtl'):
                self.btn_rtl.clicked.connect(self.rtl)
            else:
                print("Warning: btn_rtl not found in UI")
            
            print("TargetsPage: Mission control buttons connection completed")
            
        except Exception as e:
            print(f"TargetsPage: Error connecting buttons: {e}")
            print("Note: UI file may need to be regenerated from TargetsPage.ui")

        # Firebase Thread (if needed for mobile connections - optional now)
        self.firebase = self.parent.firebase if self.parent else None
        
        # **REMOVED: Target and User functionality**
        # This page is now Mission Control only
        # If you want to keep some target functionality, uncomment these:
        # if self.firebase != None:
        #     QTimer.singleShot(20000, self.addUsers)

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
    def addTarget(self, image, position, time, no):
        """
        Optional method for adding targets (currently disabled)
        Can be implemented later if target functionality is needed
        """
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
        # Uncomment for debugging:
        # self.debug_ui_elements()

    def hideEvent(self, event):
        """Called when the page is hidden"""
        super().hideEvent(event)
        print("TargetsPage (Mission Control) is now hidden")


# **REMOVED: UserMenu class - can be added back if needed**
# class UserMenu(QWidget):
#     def __init__(self, parent, image, position, time, no):
#         # Implementation would go here
#         pass