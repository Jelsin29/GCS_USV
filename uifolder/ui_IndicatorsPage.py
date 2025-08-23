# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'IndicatorsPage.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)
import indicators_rc

class Ui_IndicatorsPage(object):
    def setupUi(self, IndicatorsPage):
        if not IndicatorsPage.objectName():
            IndicatorsPage.setObjectName(u"IndicatorsPage")
        IndicatorsPage.resize(1200, 700)
        IndicatorsPage.setMinimumSize(QSize(900, 600))
        IndicatorsPage.setStyleSheet(u"\n"
"/* MODERN USV INDICATORS - TESLA DASHBOARD STYLE */\n"
"QWidget {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    color: #2c3e50;\n"
"    font-family: 'Segoe UI', 'San Francisco', Arial, sans-serif;\n"
"}\n"
"\n"
"QFrame {\n"
"    background: qradial-gradient(cx:0.5, cy:0.5, radius:1.0, \n"
"                                fx:0.5, fy:0.3,\n"
"                                stop:0 #ffffff, \n"
"                                stop:0.8 #f8f9fa, \n"
"                                stop:1.0 #e9ecef);\n"
"    border: none;\n"
"    border-radius: 20px;\n"
"    margin: 12px;\n"
"    padding: 16px;\n"
"}\n"
"\n"
"QLabel {\n"
"    background: transparent;\n"
"    color: #2c3e50;\n"
"    font-weight: 500;\n"
"    border: none;\n"
"}\n"
"\n"
"/* REMOVE ALL HARSH BORDERS AND LINES */\n"
"* {\n"
"    border: none;\n"
"    outline: none;\n"
"}\n"
"   ")
        self.verticalLayout = QVBoxLayout(IndicatorsPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mainWidget = QWidget(IndicatorsPage)
        self.mainWidget.setObjectName(u"mainWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainWidget.sizePolicy().hasHeightForWidth())
        self.mainWidget.setSizePolicy(sizePolicy)
        self.mainWidget.setMinimumSize(QSize(800, 500))
        self.mainHorizontalLayout = QHBoxLayout(self.mainWidget)
        self.mainHorizontalLayout.setSpacing(20)
        self.mainHorizontalLayout.setObjectName(u"mainHorizontalLayout")
        self.instrumentsContainer = QWidget(self.mainWidget)
        self.instrumentsContainer.setObjectName(u"instrumentsContainer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.instrumentsContainer.sizePolicy().hasHeightForWidth())
        self.instrumentsContainer.setSizePolicy(sizePolicy1)
        self.instrumentsContainer.setMinimumSize(QSize(320, 600))
        self.instrumentsContainer.setMaximumSize(QSize(350, 16777215))
        self.instrumentsContainer.setStyleSheet(u"QWidget { background: transparent; border: none; }")
        self.instrumentsLayout = QVBoxLayout(self.instrumentsContainer)
        self.instrumentsLayout.setSpacing(10)
        self.instrumentsLayout.setObjectName(u"instrumentsLayout")
        self.instrumentsLayout.setContentsMargins(0, 0, 0, 0)
        self.Speedometer = QFrame(self.instrumentsContainer)
        self.Speedometer.setObjectName(u"Speedometer")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.Speedometer.sizePolicy().hasHeightForWidth())
        self.Speedometer.setSizePolicy(sizePolicy2)
        self.Speedometer.setMinimumSize(QSize(300, 280))
        self.Speedometer.setMaximumSize(QSize(320, 300))
        self.Speedometer.setFrameShape(QFrame.StyledPanel)
        self.Speedometer.setFrameShadow(QFrame.Raised)
        self.speed_label = QLabel(self.Speedometer)
        self.speed_label.setObjectName(u"speed_label")
        self.speed_label.setGeometry(QRect(22, 12, 256, 256))
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.speed_label.sizePolicy().hasHeightForWidth())
        self.speed_label.setSizePolicy(sizePolicy3)
        self.speed_label.setMinimumSize(QSize(256, 256))
        self.speed_label.setPixmap(QPixmap(u":/meters/assets/Speedometer.png"))
        self.speed_label.setScaledContents(True)
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_needle = QLabel(self.Speedometer)
        self.speed_needle.setObjectName(u"speed_needle")
        self.speed_needle.setGeometry(QRect(22, 12, 256, 256))
        self.speed_needle.setStyleSheet(u"background-color: transparent")
        self.speed_needle.setPixmap(QPixmap(u":/needles/assets/needle.png"))
        self.speed_needle.setScaledContents(False)
        self.speed_needle.setAlignment(Qt.AlignCenter)
        self.speed_text = QLabel(self.Speedometer)
        self.speed_text.setObjectName(u"speed_text")
        self.speed_text.setGeometry(QRect(140, 220, 60, 30))
        self.speed_text.setStyleSheet(u"color: #ffffff; font-family: 'Lato',sans-serif; font-size: 18px; font-weight: bold; text-align: center;")
        self.speed_text.setAlignment(Qt.AlignCenter)

        self.instrumentsLayout.addWidget(self.Speedometer)

        self.Direction = QFrame(self.instrumentsContainer)
        self.Direction.setObjectName(u"Direction")
        sizePolicy2.setHeightForWidth(self.Direction.sizePolicy().hasHeightForWidth())
        self.Direction.setSizePolicy(sizePolicy2)
        self.Direction.setMinimumSize(QSize(300, 280))
        self.Direction.setMaximumSize(QSize(320, 300))
        self.Direction.setFrameShape(QFrame.StyledPanel)
        self.Direction.setFrameShadow(QFrame.Raised)
        self.direction_label = QLabel(self.Direction)
        self.direction_label.setObjectName(u"direction_label")
        self.direction_label.setGeometry(QRect(22, 12, 256, 256))
        sizePolicy3.setHeightForWidth(self.direction_label.sizePolicy().hasHeightForWidth())
        self.direction_label.setSizePolicy(sizePolicy3)
        self.direction_label.setMinimumSize(QSize(256, 256))
        self.direction_label.setPixmap(QPixmap(u":/meters/assets/Gyrometre.png"))
        self.direction_label.setScaledContents(True)
        self.direction_label.setAlignment(Qt.AlignCenter)
        self.direction_needle = QLabel(self.Direction)
        self.direction_needle.setObjectName(u"direction_needle")
        self.direction_needle.setGeometry(QRect(22, 12, 252, 252))
        self.direction_needle.setStyleSheet(u"background-color: transparent")
        self.direction_needle.setPixmap(QPixmap(u":/needles/assets/plane.png"))
        self.direction_needle.setScaledContents(False)
        self.direction_needle.setAlignment(Qt.AlignCenter)

        self.instrumentsLayout.addWidget(self.Direction)


        self.mainHorizontalLayout.addWidget(self.instrumentsContainer)

        self.telemetryContainer = QWidget(self.mainWidget)
        self.telemetryContainer.setObjectName(u"telemetryContainer")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.telemetryContainer.sizePolicy().hasHeightForWidth())
        self.telemetryContainer.setSizePolicy(sizePolicy4)
        self.telemetryContainer.setMinimumSize(QSize(450, 580))
        self.telemetryContainer.setStyleSheet(u"QWidget { background: transparent; border: none; }")
        self.telemetryLayout = QVBoxLayout(self.telemetryContainer)
        self.telemetryLayout.setSpacing(0)
        self.telemetryLayout.setObjectName(u"telemetryLayout")
        self.telemetryLayout.setContentsMargins(0, 0, 0, 0)

        self.mainHorizontalLayout.addWidget(self.telemetryContainer)


        self.verticalLayout.addWidget(self.mainWidget)

        self.statusWidget = QWidget(IndicatorsPage)
        self.statusWidget.setObjectName(u"statusWidget")
        self.statusWidget.setMinimumSize(QSize(0, 80))
        self.statusWidget.setMaximumSize(QSize(16777215, 100))
        self.statusLayout = QHBoxLayout(self.statusWidget)
        self.statusLayout.setObjectName(u"statusLayout")
        self.connectionStatus = QFrame(self.statusWidget)
        self.connectionStatus.setObjectName(u"connectionStatus")
        self.connectionStatus.setStyleSheet(u"color: #ffffff; font-family: 'Lato',sans-serif; font-size: 14px; font-weight: bold; text-align: center;")
        self.connectionStatus.setFrameShape(QFrame.StyledPanel)
        self.connectionStatus.setFrameShadow(QFrame.Raised)
        self.connection_status_label = QLabel(self.connectionStatus)
        self.connection_status_label.setObjectName(u"connection_status_label")
        self.connection_status_label.setGeometry(QRect(10, 15, 200, 31))
        self.connection_status_label.setAlignment(Qt.AlignCenter)

        self.statusLayout.addWidget(self.connectionStatus)

        self.modeStatus = QFrame(self.statusWidget)
        self.modeStatus.setObjectName(u"modeStatus")
        self.modeStatus.setStyleSheet(u"color: #ffffff; font-family: 'Lato',sans-serif; font-size: 14px; font-weight: bold; text-align: center;")
        self.modeStatus.setFrameShape(QFrame.StyledPanel)
        self.modeStatus.setFrameShadow(QFrame.Raised)
        self.mode_status_label = QLabel(self.modeStatus)
        self.mode_status_label.setObjectName(u"mode_status_label")
        self.mode_status_label.setGeometry(QRect(10, 15, 200, 31))
        self.mode_status_label.setAlignment(Qt.AlignCenter)

        self.statusLayout.addWidget(self.modeStatus)

        self.systemStatus = QFrame(self.statusWidget)
        self.systemStatus.setObjectName(u"systemStatus")
        self.systemStatus.setStyleSheet(u"color: #ffffff; font-family: 'Lato',sans-serif; font-size: 14px; font-weight: bold; text-align: center;")
        self.systemStatus.setFrameShape(QFrame.StyledPanel)
        self.systemStatus.setFrameShadow(QFrame.Raised)
        self.system_status_label = QLabel(self.systemStatus)
        self.system_status_label.setObjectName(u"system_status_label")
        self.system_status_label.setGeometry(QRect(10, 15, 200, 31))
        self.system_status_label.setAlignment(Qt.AlignCenter)

        self.statusLayout.addWidget(self.systemStatus)


        self.verticalLayout.addWidget(self.statusWidget)


        self.retranslateUi(IndicatorsPage)

        QMetaObject.connectSlotsByName(IndicatorsPage)
    # setupUi

    def retranslateUi(self, IndicatorsPage):
        IndicatorsPage.setWindowTitle(QCoreApplication.translate("IndicatorsPage", u"USV Indicators", None))
        self.speed_label.setText("")
        self.speed_needle.setText("")
        self.speed_text.setText(QCoreApplication.translate("IndicatorsPage", u"0.0", None))
        self.direction_label.setText("")
        self.direction_needle.setText("")
        self.connection_status_label.setText(QCoreApplication.translate("IndicatorsPage", u"Connection: CONNECTED", None))
        self.mode_status_label.setText(QCoreApplication.translate("IndicatorsPage", u"Mode: AUTONOMOUS", None))
        self.system_status_label.setText(QCoreApplication.translate("IndicatorsPage", u"Systems: NOMINAL", None))
    # retranslateUi

