import sys
import threading

from PySide6 import QtGui
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, QEvent, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QSizeGrip, QVBoxLayout, QWidget, QInputDialog, QGraphicsDropShadowEffect

from HomePage import HomePage
from uifolder import Ui_MainWindow
from TargetsPage import TargetsPage
from IndicatorsPage import IndicatorsPage
from AntennaTracker import AntennaTracker, antenna_tracker
from Vehicle.ArdupilotConnection import ArdupilotConnectionThread

from IconUtils import createWhiteIcon


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, firebase):
        super().__init__()
        self.setupUi(self)

        self.firebase = firebase

        # Frameless Window
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set initial windows size
        self.state = 0  # maximized or not
        self.screenSize = QApplication.primaryScreen().size()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        width = self.screenSize.width() * 0.8
        height = self.screenSize.height() * 0.8
        self.resize(width, height)

        # Move Window to Center
        self.move(self.screenSize.width() / 2 - self.width() / 2, self.screenSize.height() / 2 - self.height() / 2)

        # Set Font
        QtGui.QFontDatabase.addApplicationFont('uifolder/assets/fonts/segoeui.ttf')
        QtGui.QFontDatabase.addApplicationFont('uifolder/assets/fonts/segoeuib.ttf')

        # **NEW: Initialize menu in collapsed state**
        self.initializeMenuCollapsed()

        # Sizegrip (To Resize Window)
        self.sizegrip = QSizeGrip(self.frame_size_grip)
        self.sizegrip.setStyleSheet("background-image: url(uifolder/assets/icons/16x16/cil-size-grip.png);"
                                    "width: 20px; height: 20px; margin 0px; padding 0px;")

        # Set Initial Baud Rate to Combobox
        self.combobox_baudrate.setCurrentText('115200')

        # Setting Pages
        self.targetspage = TargetsPage(self)
        self.homepage = HomePage(self)
        self.indicatorspage = IndicatorsPage()
        self.indicatorswidget = QWidget(layout=QVBoxLayout())
        self.indicatorswidget.layout().addWidget(self.indicatorspage)
        self.stackedWidget.addWidget(self.homepage)
        self.stackedWidget.addWidget(self.targetspage)
        self.stackedWidget.addWidget(self.indicatorswidget)
        self.stackedWidget.setCurrentWidget(self.homepage)

        # Connection Thread
        self.connectionThread = ArdupilotConnectionThread(self)

        #  SET BUTTONS
        #  Main Window buttons
        self.btn_close.setIcon(QtGui.QIcon('uifolder/assets/icons/16x16/cil-x.png'))
        self.btn_close.clicked.connect(lambda: sys.exit())
        self.btn_maximize_restore.setIcon(QtGui.QIcon('uifolder/assets/icons/16x16/cil-window-maximize.png'))
        self.btn_maximize_restore.clicked.connect(self.maximize_restore)
        self.btn_minimize.setIcon(QtGui.QIcon('uifolder/assets/icons/16x16/cil-window-minimize.png'))
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())

        # **UPDATED: Setup navigation buttons with black and white icons**
        self.btn_home_page.setDisabled(True)
        self.disabledbutton = self.btn_home_page
        
        # Toggle menu button
        self.btn_toggle_menu.setIcon(QtGui.QIcon('uifolder/assets/icons/svg/menu.svg'))
        self.setButton(self.btn_toggle_menu, 'uifolder/assets/icons/svg/menu.svg')
        
        # Home button - start white (active)
        self.btn_home_page.black_icon = QtGui.QIcon('uifolder/assets/icons/svg/home.svg')
        self.btn_home_page.white_icon = createWhiteIcon('uifolder/assets/icons/svg/home.svg')
        self.btn_home_page.setIcon(self.btn_home_page.white_icon)  # Start white (active)
        self.setButton(self.btn_home_page, 'uifolder/assets/icons/svg/home.svg')
        
        # Indicators button - start black
        self.btn_indicators_page.black_icon = QtGui.QIcon('uifolder/assets/icons/svg/speed.svg')
        self.btn_indicators_page.white_icon = createWhiteIcon('uifolder/assets/icons/svg/speed.svg')
        self.btn_indicators_page.setIcon(self.btn_indicators_page.black_icon)  # Start black
        self.setButton(self.btn_indicators_page, 'uifolder/assets/icons/svg/speed.svg')
        
        # Targets button - start black
        self.btn_targets_page.black_icon = QtGui.QIcon('uifolder/assets/icons/svg/task-manager.svg')
        self.btn_targets_page.white_icon = createWhiteIcon('uifolder/assets/icons/svg/task-manager.svg')
        self.btn_targets_page.setIcon(self.btn_targets_page.black_icon)  # Start black
        self.setButton(self.btn_targets_page, 'uifolder/assets/icons/svg/user.svg')
        
        # Connect button
        self.btn_connect.setIcon(QtGui.QIcon('uifolder/assets/icons/svg/connection.svg'))

        # **UPDATED: Main Connection Button**
        self.btn_connect.clicked.connect(self.connectToVehicle)

        # **UPDATED: HomePage Guidance Buttons (only if they exist)**
        # These are the buttons that might still be on HomePage for guided control
        if hasattr(self.homepage, 'btn_set_roi'):
            self.homepage.btn_set_roi.clicked.connect(self.connectionThread.set_roi)
        if hasattr(self.homepage, 'btn_cancel_roi'):
            self.homepage.btn_cancel_roi.clicked.connect(self.connectionThread.cancel_roi_mode)
        if hasattr(self.homepage, 'btn_move'):
            self.homepage.btn_move.clicked.connect(self.connectionThread.goto_markers_pos)
        if hasattr(self.homepage, 'btn_takeoff'):
            self.homepage.btn_takeoff.clicked.connect(self.takeoff)
        if hasattr(self.homepage, 'btn_land'):
            self.homepage.btn_land.clicked.connect(self.connectionThread.land)
        if hasattr(self.homepage, 'btn_rtl'):
            self.homepage.btn_rtl.clicked.connect(lambda: self.connectionThread.connection.set_mode_apm("QRTL"))
        if hasattr(self.homepage, 'btn_rtl_2'):
            self.homepage.btn_rtl_2.clicked.connect(self.connectionThread.rtl)
        if hasattr(self.homepage, 'btn_track_all'):
            self.homepage.btn_track_all.clicked.connect(self.track_all)

        # **REMOVED: Mission control buttons - now handled in TargetsPage**
        # These buttons have been moved to TargetsPage (Mission Control)
        # if hasattr(self.homepage, 'btn_abort'):
        #     self.homepage.btn_abort.clicked.connect(self.abort)
        # if hasattr(self.homepage, 'btn_startMission'):
        #     self.homepage.btn_startMission.clicked.connect(self.connectionThread.start_mission)
        # if hasattr(self.homepage, 'btn_antenna'):
        #     self.homepage.btn_antenna.clicked.connect(self.run_antenna_tracker)

        # Button to Allocate Windows
        self.indicatorspage.btn_AllocateWidget.clicked.connect(
            lambda: self.AllocateWidget(self.indicatorswidget, self.indicatorspage))

        # **NEW: Add shadow effects after UI setup**
        QTimer.singleShot(100, self.addShadowEffects)

        # To move the window only from top frame
        self.label_title_bar_top.installEventFilter(self)

    def addShadowEffects(self):
        """Add modern shadow effects to main UI elements"""
        try:
            # Main frame shadow
            main_shadow = QGraphicsDropShadowEffect()
            main_shadow.setBlurRadius(20)
            main_shadow.setXOffset(0)
            main_shadow.setYOffset(5)
            main_shadow.setColor(QColor(0, 0, 0, 50))
            self.frame_content.setGraphicsEffect(main_shadow)

            # Left menu shadow
            menu_shadow = QGraphicsDropShadowEffect()
            menu_shadow.setBlurRadius(15)
            menu_shadow.setXOffset(2)
            menu_shadow.setYOffset(0)
            menu_shadow.setColor(QColor(0, 0, 0, 30))
            self.frame_left_menu.setGraphicsEffect(menu_shadow)

            # Connect button shadow
            connect_shadow = QGraphicsDropShadowEffect()
            connect_shadow.setBlurRadius(12)
            connect_shadow.setXOffset(0)
            connect_shadow.setYOffset(3)
            connect_shadow.setColor(QColor(13, 110, 253, 80))  # Blue shadow for connect button
            self.btn_connect.setGraphicsEffect(connect_shadow)

            # Navigation buttons shadows
            self.addButtonShadow(self.btn_home_page)
            self.addButtonShadow(self.btn_indicators_page) 
            self.addButtonShadow(self.btn_targets_page)
            self.addButtonShadow(self.btn_toggle_menu)

            print("MainWindow: Shadow effects applied successfully")
            
        except Exception as e:
            print(f"MainWindow: Error applying shadow effects: {e}")

    def addButtonShadow(self, button):
        """Add subtle shadow to a button"""
        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 25))
            button.setGraphicsEffect(shadow)
        except Exception as e:
            print(f"Error adding shadow to button {button.objectName()}: {e}")

    #########################################################################################################################

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    # To take events from child widgets
    def eventFilter(self, obj, event):
        if obj == self.label_title_bar_top:
            # Maximize and restore when double click
            if event.type() == QEvent.MouseButtonDblClick:
                self.maximize_restore()
            # Drag move window
            if event.type() == QEvent.MouseMove:
                if event.buttons() == Qt.LeftButton:
                    self.setCursor(Qt.SizeAllCursor)
                    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                    self.dragPos = event.globalPosition().toPoint()
                    return True
            if event.type() == QEvent.MouseButtonRelease:
                self.setCursor(Qt.ArrowCursor)
        return super().eventFilter(obj, event)

    def setButton(self, button, icon):
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QSize(0, 70))
        button.setLayoutDirection(Qt.LeftToRight)
        button.clicked.connect(self.buttonFunctions)

    def maximize_restore(self):
        if self.state == 1:
            self.btn_maximize_restore.setToolTip("Maximize")
            self.btn_maximize_restore.setIcon(QtGui.QIcon(u"uifolder/assets/icons/16x16/cil-window-maximize.png"))
            self.showNormal()
            self.state = 0
        else:
            self.btn_maximize_restore.setToolTip("Restore")
            self.btn_maximize_restore.setIcon(QtGui.QIcon(u"uifolder/assets/icons/16x16/cil-window-restore.png"))
            self.showMaximized()
            self.state = 1

    def buttonFunctions(self):
        button = self.sender()
        
        # Toggle Button
        if button.objectName() == "btn_toggle_menu":
            width = self.frame_left_menu.width()
            maxWidth = 240
            standard = 70
            
            # SET MAX WIDTH
            if width == standard:
                widthExtended = maxWidth
                # Show text labels when expanded
                self.btn_home_page.setText("    Home")
                self.btn_indicators_page.setText("   Indicators") 
                self.btn_targets_page.setText("   Mission Control")
                # Change icon to indicate menu can be collapsed
                self.btn_toggle_menu.setIcon(QtGui.QIcon('uifolder/assets/icons/svg/close.svg'))
            else:
                widthExtended = standard
                # Hide text labels when collapsed
                self.btn_home_page.setText("")
                self.btn_indicators_page.setText("")
                self.btn_targets_page.setText("")
                # Change icon back to menu
                self.btn_toggle_menu.setIcon(QtGui.QIcon('uifolder/assets/icons/svg/menu.svg'))

            # ANIMATION for smooth width transition
            self.animation = QPropertyAnimation(self.frame_left_menu, b"minimumWidth")
            self.animation.setDuration(300)  # Slightly longer for smoother feel
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

            # Also animate maximum width for better control
            self.animation2 = QPropertyAnimation(self.frame_left_menu, b"maximumWidth")
            self.animation2.setDuration(300)
            self.animation2.setStartValue(width)
            self.animation2.setEndValue(widthExtended)
            self.animation2.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation2.start()

        else:
            # Handle page navigation buttons
            self.disabledbutton.setDisabled(False)
            # **NEW: Set old button to black icon**
            if hasattr(self.disabledbutton, 'black_icon'):
                self.disabledbutton.setIcon(self.disabledbutton.black_icon)
                
            self.disabledbutton = button
            self.disabledbutton.setDisabled(True)
            # **NEW: Set new active button to white icon**
            if hasattr(self.disabledbutton, 'white_icon'):
                self.disabledbutton.setIcon(self.disabledbutton.white_icon)

        # PAGE HOME
        if button.objectName() == "btn_home_page":
            self.stackedWidget.setCurrentWidget(self.homepage)

        # PAGE INDICATORS  
        if button.objectName() == "btn_indicators_page":
            self.stackedWidget.setCurrentWidget(self.indicatorswidget)

        # PAGE MISSION CONTROL (formerly Targets)
        if button.objectName() == "btn_targets_page":
            self.stackedWidget.setCurrentWidget(self.targetspage)

    def connectToVehicle(self):
        self.connectionThread.setBaudRate(int(self.combobox_baudrate.currentText()))
        self.connectionThread.setConnectionString(self.combobox_connectionstring.currentText())
        self.connectionThread.start()

    def takeoff(self):
        altitude, okPressed = QInputDialog.getText(self, "Enter Altitude", "Altitude:", text="10")
        if okPressed:
            self.connectionThread.takeoff(int(altitude))

    # **MOVED: These methods are now available but might be called from TargetsPage**
    def run_antenna_tracker(self):
        antenna = AntennaTracker(-35.3635, 149.1652)
        lat, lon = antenna.get_location()
        # Add home marker
        self.homepage.mapwidget.page().runJavaScript("""
                        var homeMarker = L.marker(
                                    %s,
                                    {icon: homeIcon,},).addTo(map);
                        """ % [lat, lon]
                                       )

        threading.Thread(target=antenna_tracker, args=(antenna, self.connectionThread)).start()
        # **UPDATED: Now disable the button on TargetsPage instead of HomePage**
        if hasattr(self.targetspage, 'btn_antenna'):
            self.targetspage.btn_antenna.setDisabled(True)

    def abort(self):
        if hasattr(self.homepage, 'cameraWidget') and hasattr(self.homepage.cameraWidget, 'videothread'):
            self.homepage.cameraWidget.videothread.sendMessage("abort")

    def track_all(self):
        if hasattr(self.homepage, 'cameraWidget') and hasattr(self.homepage.cameraWidget, 'videothread'):
            self.homepage.cameraWidget.videothread.sendMessage("track -1")

    def AllocateWidget(self, parent, child):
        if child.isAttached:
            self.stackedWidget.setCurrentWidget(self.homepage)
            parent.layout().removeWidget(child)
            self.new_window = QMainWindow(styleSheet="background-color: rgb(44, 49, 60);")
            self.new_window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
            child.btn_AllocateWidget.setIcon(QIcon("uifolder/assets/icons/16x16/cil-arrow-bottom.png"))
            self.new_window.setCentralWidget(child)
            self.new_window.show()
            child.isAttached = False
        else:
            parent.layout().addWidget(child)
            self.new_window.setCentralWidget(None)
            self.new_window.close()
            child.btn_AllocateWidget.setIcon(QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"))
            child.isAttached = True

    def initializeMenuCollapsed(self):
        """Initialize the left menu in collapsed state"""
        try:
            # Set menu to collapsed width
            standard_width = 70
            self.frame_left_menu.setMinimumWidth(standard_width)
            self.frame_left_menu.setMaximumWidth(standard_width)
            
            # Remove text from navigation buttons (start collapsed)
            self.btn_home_page.setText("")
            self.btn_indicators_page.setText("")
            self.btn_targets_page.setText("")
            
            # Set toggle button icon to menu (not X)
            self.btn_toggle_menu.setIcon(QtGui.QIcon('uifolder/assets/icons/svg/menu.svg'))
            
            print("MainWindow: Menu initialized in collapsed state")
            
        except Exception as e:
            print(f"MainWindow: Error initializing collapsed menu: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())