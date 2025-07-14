# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QMainWindow, QPushButton, QSizePolicy,
    QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1400, 900)
        MainWindow.setMinimumSize(QSize(1200, 800))
        MainWindow.setStyleSheet(u"\n"
"/* MODERN WINDOWS 10 LIGHT STYLE */\n"
"QMainWindow {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    color: #212529;\n"
"}\n"
"\n"
"/* MODERN TITLE BAR */\n"
"QFrame#frame_top {\n"
"    background: #ffffff;\n"
"    border-bottom: 1px solid #dee2e6;\n"
"}\n"
"\n"
"QFrame#frame_top_btns {\n"
"    background: #ffffff;\n"
"}\n"
"\n"
"/* MODERN BUTTONS - TITLE BAR */\n"
"QPushButton#btn_minimize, QPushButton#btn_maximize_restore, QPushButton#btn_close {\n"
"    border: none;\n"
"    background: transparent;\n"
"    padding: 8px;\n"
"    color: #495057;\n"
"}\n"
"QPushButton#btn_minimize:hover, QPushButton#btn_maximize_restore:hover {\n"
"    background: #e9ecef;\n"
"}\n"
"QPushButton#btn_close:hover {\n"
"    background: #dc3545;\n"
"    color: white;\n"
"}\n"
"\n"
"/* MODERN SIDEBAR */\n"
"QFrame#frame_left_menu {\n"
"    background: #f8f9fa;\n"
"    border-right: 1px solid #dee2e6;\n"
"}\n"
"\n"
"QPushButton#btn_toggle"
                        "_menu {\n"
"    background: transparent;\n"
"    border: none;\n"
"    padding: 15px;\n"
"    color: #495057;\n"
"}\n"
"QPushButton#btn_toggle_menu:hover {\n"
"    background: #e9ecef;\n"
"}\n"
"\n"
"/* MODERN NAVIGATION BUTTONS */\n"
"QPushButton#btn_home_page, QPushButton#btn_indicators_page, QPushButton#btn_targets_page {\n"
"    background: transparent;\n"
"    border: none;\n"
"    text-align: left;\n"
"    padding: 15px 20px;\n"
"    color: #495057;\n"
"    font-size: 14px;\n"
"    border-left: 3px solid transparent;\n"
"}\n"
"\n"
"QPushButton#btn_home_page:hover, QPushButton#btn_indicators_page:hover, QPushButton#btn_targets_page:hover {\n"
"    background: #e9ecef;\n"
"    color: #212529;\n"
"}\n"
"\n"
"QPushButton#btn_home_page:disabled, QPushButton#btn_indicators_page:disabled, QPushButton#btn_targets_page:disabled {\n"
"    background: #0d6efd;\n"
"    border-left: 3px solid #0d6efd;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"/* MODERN CONTENT AREA */\n"
"QFrame#frame_content_right {\n"
"    background:"
                        " #ffffff;\n"
"}\n"
"\n"
"QFrame#frame_content {\n"
"    background: #ffffff;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"/* MODERN CONNECTION CONTROLS */\n"
"QComboBox {\n"
"    background: #ffffff;\n"
"    border: 1px solid #ced4da;\n"
"    border-radius: 4px;\n"
"    padding: 8px 12px;\n"
"    color: #495057;\n"
"    selection-background-color: #0d6efd;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border: 1px solid #0d6efd;\n"
"}\n"
"\n"
"QComboBox:focus {\n"
"    border: 2px solid #0d6efd;\n"
"    outline: none;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    border: none;\n"
"    width: 20px;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(uifolder/assets/icons/16x16/cil-arrow-bottom.png);\n"
"    width: 12px;\n"
"    height: 12px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background: #ffffff;\n"
"    border: 1px solid #ced4da;\n"
"    selection-background-color: #0d6efd;\n"
"    color: #495057;\n"
"}\n"
"\n"
"/* MODERN CONNECT BUTTON */\n"
"QPushButton#btn_connect {\n"
"    background: qline"
                        "argradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                stop:0 #0d6efd, stop:1 #0b5ed7);\n"
"    border: 1px solid #0a58ca;\n"
"    border-radius: 4px;\n"
"    color: #ffffff;\n"
"    font-weight: 600;\n"
"    padding: 8px 16px;\n"
"}\n"
"\n"
"QPushButton#btn_connect:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                stop:0 #0b5ed7, stop:1 #0a58ca);\n"
"}\n"
"\n"
"QPushButton#btn_connect:pressed {\n"
"    background: #0a58ca;\n"
"}\n"
"\n"
"/* MODERN SCROLLBARS */\n"
"QScrollBar:vertical {\n"
"    background: #f8f9fa;\n"
"    width: 12px;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: #ced4da;\n"
"    border-radius: 6px;\n"
"    min-height: 20px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"    background: #adb5bd;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"    border: none;\n"
"    background: none;\n"
"}\n"
"\n"
"/* MODERN STATUS BAR */\n"
"QFram"
                        "e#frame_top_info {\n"
"    background: #0d6efd;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"/* MODERN GRIP */\n"
"QFrame#frame_grip {\n"
"    background: #f8f9fa;\n"
"}\n"
"\n"
"/* LABELS */\n"
"QLabel {\n"
"    color: #495057;\n"
"}\n"
"\n"
"/* GENERAL BUTTONS */\n"
"QPushButton {\n"
"    background: #f8f9fa;\n"
"    border: 1px solid #ced4da;\n"
"    border-radius: 4px;\n"
"    padding: 6px 12px;\n"
"    color: #495057;\n"
"    font-weight: 500;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: #e9ecef;\n"
"    border-color: #adb5bd;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"    background: #e9ecef;\n"
"    color: #6c757d;\n"
"    border-color: #dee2e6;\n"
"}\n"
"   ")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_main = QFrame(self.centralwidget)
        self.frame_main.setObjectName(u"frame_main")
        self.frame_main.setFrameShape(QFrame.NoFrame)
        self.verticalLayout = QVBoxLayout(self.frame_main)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_top = QFrame(self.frame_main)
        self.frame_top.setObjectName(u"frame_top")
        self.frame_top.setMinimumSize(QSize(0, 48))
        self.frame_top.setMaximumSize(QSize(16777215, 48))
        self.frame_top.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_top)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_toggle = QFrame(self.frame_top)
        self.frame_toggle.setObjectName(u"frame_toggle")
        self.frame_toggle.setMaximumSize(QSize(60, 16777215))
        self.frame_toggle.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_3 = QVBoxLayout(self.frame_toggle)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.btn_toggle_menu = QPushButton(self.frame_toggle)
        self.btn_toggle_menu.setObjectName(u"btn_toggle_menu")
        self.btn_toggle_menu.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.btn_toggle_menu)


        self.horizontalLayout_3.addWidget(self.frame_toggle)

        self.frame_top_right = QFrame(self.frame_top)
        self.frame_top_right.setObjectName(u"frame_top_right")
        self.frame_top_right.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_2 = QVBoxLayout(self.frame_top_right)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_top_btns = QFrame(self.frame_top_right)
        self.frame_top_btns.setObjectName(u"frame_top_btns")
        self.frame_top_btns.setMaximumSize(QSize(16777215, 48))
        self.frame_top_btns.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_top_btns)
        self.horizontalLayout_4.setSpacing(12)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(20, 0, 0, 0)
        self.label_title_bar_top = QLabel(self.frame_top_btns)
        self.label_title_bar_top.setObjectName(u"label_title_bar_top")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(14)
        font.setBold(True)
        self.label_title_bar_top.setFont(font)

        self.horizontalLayout_4.addWidget(self.label_title_bar_top)

        self.combobox_connectionstring = QComboBox(self.frame_top_btns)
        self.combobox_connectionstring.addItem("")
        self.combobox_connectionstring.addItem("")
        self.combobox_connectionstring.addItem("")
        self.combobox_connectionstring.addItem("")
        self.combobox_connectionstring.addItem("")
        self.combobox_connectionstring.addItem("")
        self.combobox_connectionstring.setObjectName(u"combobox_connectionstring")
        self.combobox_connectionstring.setMinimumSize(QSize(150, 32))

        self.horizontalLayout_4.addWidget(self.combobox_connectionstring)

        self.combobox_baudrate = QComboBox(self.frame_top_btns)
        self.combobox_baudrate.addItem("")
        self.combobox_baudrate.addItem("")
        self.combobox_baudrate.addItem("")
        self.combobox_baudrate.addItem("")
        self.combobox_baudrate.addItem("")
        self.combobox_baudrate.addItem("")
        self.combobox_baudrate.addItem("")
        self.combobox_baudrate.setObjectName(u"combobox_baudrate")
        self.combobox_baudrate.setMinimumSize(QSize(100, 32))

        self.horizontalLayout_4.addWidget(self.combobox_baudrate)

        self.btn_connect = QPushButton(self.frame_top_btns)
        self.btn_connect.setObjectName(u"btn_connect")
        self.btn_connect.setMinimumSize(QSize(80, 32))

        self.horizontalLayout_4.addWidget(self.btn_connect)

        self.frame_btns_right = QFrame(self.frame_top_btns)
        self.frame_btns_right.setObjectName(u"frame_btns_right")
        self.frame_btns_right.setMaximumSize(QSize(138, 16777215))
        self.frame_btns_right.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_btns_right)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.btn_minimize = QPushButton(self.frame_btns_right)
        self.btn_minimize.setObjectName(u"btn_minimize")
        self.btn_minimize.setMinimumSize(QSize(46, 32))
        self.btn_minimize.setMaximumSize(QSize(46, 32))

        self.horizontalLayout_5.addWidget(self.btn_minimize)

        self.btn_maximize_restore = QPushButton(self.frame_btns_right)
        self.btn_maximize_restore.setObjectName(u"btn_maximize_restore")
        self.btn_maximize_restore.setMinimumSize(QSize(46, 32))
        self.btn_maximize_restore.setMaximumSize(QSize(46, 32))

        self.horizontalLayout_5.addWidget(self.btn_maximize_restore)

        self.btn_close = QPushButton(self.frame_btns_right)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setMinimumSize(QSize(46, 32))
        self.btn_close.setMaximumSize(QSize(46, 32))

        self.horizontalLayout_5.addWidget(self.btn_close)


        self.horizontalLayout_4.addWidget(self.frame_btns_right)


        self.verticalLayout_2.addWidget(self.frame_top_btns)


        self.horizontalLayout_3.addWidget(self.frame_top_right)


        self.verticalLayout.addWidget(self.frame_top)

        self.frame_top_info = QFrame(self.frame_main)
        self.frame_top_info.setObjectName(u"frame_top_info")
        self.frame_top_info.setMaximumSize(QSize(16777215, 32))
        self.frame_top_info.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_top_info)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(20, 0, 20, 0)

        self.verticalLayout.addWidget(self.frame_top_info)

        self.frame_center = QFrame(self.frame_main)
        self.frame_center.setObjectName(u"frame_center")
        self.frame_center.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_center)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_left_menu = QFrame(self.frame_center)
        self.frame_left_menu.setObjectName(u"frame_left_menu")
        self.frame_left_menu.setMinimumSize(QSize(60, 0))
        self.frame_left_menu.setMaximumSize(QSize(240, 16777215))
        self.frame_left_menu.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_5 = QVBoxLayout(self.frame_left_menu)
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 20, 0, 20)
        self.frame_menus = QFrame(self.frame_left_menu)
        self.frame_menus.setObjectName(u"frame_menus")
        self.frame_menus.setFrameShape(QFrame.NoFrame)
        self.layout_menus = QVBoxLayout(self.frame_menus)
        self.layout_menus.setSpacing(2)
        self.layout_menus.setObjectName(u"layout_menus")
        self.layout_menus.setContentsMargins(0, 0, 0, 0)
        self.btn_home_page = QPushButton(self.frame_menus)
        self.btn_home_page.setObjectName(u"btn_home_page")
        self.btn_home_page.setMinimumSize(QSize(0, 48))
        self.btn_home_page.setIconSize(QSize(24, 24))

        self.layout_menus.addWidget(self.btn_home_page)

        self.btn_indicators_page = QPushButton(self.frame_menus)
        self.btn_indicators_page.setObjectName(u"btn_indicators_page")
        self.btn_indicators_page.setMinimumSize(QSize(0, 48))
        self.btn_indicators_page.setIconSize(QSize(24, 24))

        self.layout_menus.addWidget(self.btn_indicators_page)

        self.btn_targets_page = QPushButton(self.frame_menus)
        self.btn_targets_page.setObjectName(u"btn_targets_page")
        self.btn_targets_page.setMinimumSize(QSize(0, 48))
        self.btn_targets_page.setIconSize(QSize(24, 24))

        self.layout_menus.addWidget(self.btn_targets_page)


        self.verticalLayout_5.addWidget(self.frame_menus, 0, Qt.AlignTop)


        self.horizontalLayout_2.addWidget(self.frame_left_menu)

        self.frame_content_right = QFrame(self.frame_center)
        self.frame_content_right.setObjectName(u"frame_content_right")
        self.frame_content_right.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_4 = QVBoxLayout(self.frame_content_right)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_content = QFrame(self.frame_content_right)
        self.frame_content.setObjectName(u"frame_content")
        self.frame_content.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_9 = QVBoxLayout(self.frame_content)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(12, 12, 12, 12)
        self.stackedWidget = QStackedWidget(self.frame_content)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"QStackedWidget { background: transparent; }")

        self.verticalLayout_9.addWidget(self.stackedWidget)


        self.verticalLayout_4.addWidget(self.frame_content)

        self.frame_grip = QFrame(self.frame_content_right)
        self.frame_grip.setObjectName(u"frame_grip")
        self.frame_grip.setMinimumSize(QSize(0, 20))
        self.frame_grip.setMaximumSize(QSize(16777215, 20))
        self.frame_grip.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_grip)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 2, 0)
        self.frame_label_bottom = QFrame(self.frame_grip)
        self.frame_label_bottom.setObjectName(u"frame_label_bottom")
        self.frame_label_bottom.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_6.addWidget(self.frame_label_bottom)

        self.frame_size_grip = QFrame(self.frame_grip)
        self.frame_size_grip.setObjectName(u"frame_size_grip")
        self.frame_size_grip.setMinimumSize(QSize(20, 20))
        self.frame_size_grip.setMaximumSize(QSize(20, 20))
        self.frame_size_grip.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_6.addWidget(self.frame_size_grip)


        self.verticalLayout_4.addWidget(self.frame_grip)


        self.horizontalLayout_2.addWidget(self.frame_content_right)


        self.verticalLayout.addWidget(self.frame_center)


        self.horizontalLayout.addWidget(self.frame_main)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Ground Control Station - USV", None))
        self.btn_toggle_menu.setText("")
        self.label_title_bar_top.setStyleSheet(QCoreApplication.translate("MainWindow", u"color: #495057;", None))
        self.label_title_bar_top.setText(QCoreApplication.translate("MainWindow", u"Ground Control Station - USV", None))
        self.combobox_connectionstring.setItemText(0, QCoreApplication.translate("MainWindow", u"USB", None))
        self.combobox_connectionstring.setItemText(1, QCoreApplication.translate("MainWindow", u"Telemetry", None))
        self.combobox_connectionstring.setItemText(2, QCoreApplication.translate("MainWindow", u"SITL (UDP)", None))
        self.combobox_connectionstring.setItemText(3, QCoreApplication.translate("MainWindow", u"SITL (TCP)", None))
        self.combobox_connectionstring.setItemText(4, QCoreApplication.translate("MainWindow", u"TCP", None))
        self.combobox_connectionstring.setItemText(5, QCoreApplication.translate("MainWindow", u"UDP", None))

        self.combobox_baudrate.setItemText(0, QCoreApplication.translate("MainWindow", u"128000", None))
        self.combobox_baudrate.setItemText(1, QCoreApplication.translate("MainWindow", u"115200", None))
        self.combobox_baudrate.setItemText(2, QCoreApplication.translate("MainWindow", u"57600", None))
        self.combobox_baudrate.setItemText(3, QCoreApplication.translate("MainWindow", u"38400", None))
        self.combobox_baudrate.setItemText(4, QCoreApplication.translate("MainWindow", u"19200", None))
        self.combobox_baudrate.setItemText(5, QCoreApplication.translate("MainWindow", u"14400", None))
        self.combobox_baudrate.setItemText(6, QCoreApplication.translate("MainWindow", u"9600", None))

        self.btn_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.btn_minimize.setText("")
        self.btn_maximize_restore.setText("")
        self.btn_close.setText("")
        self.btn_home_page.setText("")
        self.btn_indicators_page.setText("")
        self.btn_targets_page.setText("")
    # retranslateUi

