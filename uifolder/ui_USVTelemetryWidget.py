# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'USVTelemetryWidget.ui'
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
    QProgressBar, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_USVTelemetryWidget(object):
    def setupUi(self, USVTelemetryWidget):
        if not USVTelemetryWidget.objectName():
            USVTelemetryWidget.setObjectName(u"USVTelemetryWidget")
        USVTelemetryWidget.resize(400, 480)
        USVTelemetryWidget.setMinimumSize(QSize(380, 450))
        USVTelemetryWidget.setStyleSheet(u"\n"
"/* USV TELEMETRY DASHBOARD - MARITIME THEME */\n"
"QWidget {\n"
"    background-color: #f8f9fa;\n"
"    color: #2c3e50;\n"
"    font-family: 'Segoe UI', 'Consolas', monospace;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QFrame {\n"
"    background-color: #ffffff;\n"
"    border: 2px solid #0d47a1;\n"
"    border-radius: 8px;\n"
"    margin: 4px;\n"
"    padding: 12px;\n"
"}\n"
"\n"
"QLabel {\n"
"    color: #2c3e50;\n"
"    border: none;\n"
"    background: transparent;\n"
"    font-weight: 500;\n"
"}\n"
"\n"
"/* HEADER STYLING */\n"
"QLabel#headerLabel {\n"
"    color: #ffffff;\n"
"    background-color: #0d47a1;\n"
"    font-weight: bold;\n"
"    font-size: 14px;\n"
"    padding: 8px;\n"
"    border: none;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"/* SECTION HEADERS */\n"
"QLabel#attitudeHeaderLabel, QLabel#systemsHeaderLabel {\n"
"    color: #0d47a1;\n"
"    font-weight: bold;\n"
"    font-size: 13px;\n"
"    background: transparent;\n"
"    border: none;\n"
"    padding: 4px 0px;\n"
"}\n"
"\n"
"/* DATA LAB"
                        "ELS */\n"
"QLabel#statusLabel, QLabel#gpsLabel, QLabel#speedLabel, \n"
"QLabel#headingLabel, QLabel#depthLabel {\n"
"    font-family: 'Consolas', monospace;\n"
"    font-size: 12px;\n"
"    color: #2c3e50;\n"
"    background: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"/* VALUE LABELS */\n"
"QLabel#statusValueLabel {\n"
"    color: #ff6b35;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QLabel#gpsValueLabel, QLabel#speedValueLabel, \n"
"QLabel#headingValueLabel, QLabel#depthValueLabel {\n"
"    color: #0277bd;\n"
"    font-weight: bold;\n"
"    font-family: 'Consolas', monospace;\n"
"}\n"
"\n"
"/* ATTITUDE VALUES */\n"
"QLabel#rollValueLabel, QLabel#pitchValueLabel {\n"
"    color: #2e7d32;\n"
"    font-weight: bold;\n"
"    font-family: 'Consolas', monospace;\n"
"}\n"
"\n"
"/* PROGRESS BARS - BATTERY */\n"
"QProgressBar#batteryProgressBar {\n"
"    border: 2px solid #2e7d32;\n"
"    border-radius: 4px;\n"
"    background-color: #f5f5f5;\n"
"    text-align: center;\n"
"    font-weight: bold;\n"
"    color: #2"
                        "c3e50;\n"
"    min-height: 20px;\n"
"}\n"
"\n"
"QProgressBar#batteryProgressBar::chunk {\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
"                                     stop:0 #4caf50, stop:0.6 #8bc34a, \n"
"                                     stop:1.0 #cddc39);\n"
"    border-radius: 2px;\n"
"}\n"
"\n"
"/* PROGRESS BARS - RUDDER */\n"
"QProgressBar#rudderProgressBar {\n"
"    border: 2px solid #ff6b35;\n"
"    border-radius: 4px;\n"
"    background-color: #f5f5f5;\n"
"    text-align: center;\n"
"    font-weight: bold;\n"
"    color: #2c3e50;\n"
"    min-height: 20px;\n"
"}\n"
"\n"
"QProgressBar#rudderProgressBar::chunk {\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
"                                     stop:0 #ff9800, stop:0.5 #ff6b35, \n"
"                                     stop:1.0 #f4511e);\n"
"    border-radius: 2px;\n"
"}\n"
"   ")
        self.mainLayout = QVBoxLayout(USVTelemetryWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.mainFrame = QFrame(USVTelemetryWidget)
        self.mainFrame.setObjectName(u"mainFrame")
        self.contentLayout = QVBoxLayout(self.mainFrame)
        self.contentLayout.setSpacing(8)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLabel = QLabel(self.mainFrame)
        self.headerLabel.setObjectName(u"headerLabel")
        self.headerLabel.setAlignment(Qt.AlignCenter)

        self.contentLayout.addWidget(self.headerLabel)

        self.separatorFrame = QFrame(self.mainFrame)
        self.separatorFrame.setObjectName(u"separatorFrame")
        self.separatorFrame.setMaximumSize(QSize(16777215, 2))
        self.separatorFrame.setStyleSheet(u"QFrame { \n"
"    background-color: #0d47a1; \n"
"    border: none; \n"
"    margin: 0px; \n"
"    padding: 0px;\n"
"}")
        self.separatorFrame.setFrameShape(QFrame.HLine)

        self.contentLayout.addWidget(self.separatorFrame)

        self.dataLayout = QVBoxLayout()
        self.dataLayout.setSpacing(6)
        self.dataLayout.setObjectName(u"dataLayout")
        self.statusLayout = QHBoxLayout()
        self.statusLayout.setObjectName(u"statusLayout")
        self.statusLabel = QLabel(self.mainFrame)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setMinimumSize(QSize(80, 0))

        self.statusLayout.addWidget(self.statusLabel)

        self.statusValueLabel = QLabel(self.mainFrame)
        self.statusValueLabel.setObjectName(u"statusValueLabel")

        self.statusLayout.addWidget(self.statusValueLabel)


        self.dataLayout.addLayout(self.statusLayout)

        self.gpsLayout = QHBoxLayout()
        self.gpsLayout.setObjectName(u"gpsLayout")
        self.gpsLabel = QLabel(self.mainFrame)
        self.gpsLabel.setObjectName(u"gpsLabel")
        self.gpsLabel.setMinimumSize(QSize(80, 0))

        self.gpsLayout.addWidget(self.gpsLabel)

        self.gpsValueLabel = QLabel(self.mainFrame)
        self.gpsValueLabel.setObjectName(u"gpsValueLabel")

        self.gpsLayout.addWidget(self.gpsValueLabel)


        self.dataLayout.addLayout(self.gpsLayout)

        self.speedLayout = QHBoxLayout()
        self.speedLayout.setObjectName(u"speedLayout")
        self.speedLabel = QLabel(self.mainFrame)
        self.speedLabel.setObjectName(u"speedLabel")
        self.speedLabel.setMinimumSize(QSize(80, 0))

        self.speedLayout.addWidget(self.speedLabel)

        self.speedValueLabel = QLabel(self.mainFrame)
        self.speedValueLabel.setObjectName(u"speedValueLabel")

        self.speedLayout.addWidget(self.speedValueLabel)


        self.dataLayout.addLayout(self.speedLayout)

        self.headingLayout = QHBoxLayout()
        self.headingLayout.setObjectName(u"headingLayout")
        self.headingLabel = QLabel(self.mainFrame)
        self.headingLabel.setObjectName(u"headingLabel")
        self.headingLabel.setMinimumSize(QSize(80, 0))

        self.headingLayout.addWidget(self.headingLabel)

        self.headingValueLabel = QLabel(self.mainFrame)
        self.headingValueLabel.setObjectName(u"headingValueLabel")

        self.headingLayout.addWidget(self.headingValueLabel)


        self.dataLayout.addLayout(self.headingLayout)

        self.depthLayout = QHBoxLayout()
        self.depthLayout.setObjectName(u"depthLayout")
        self.depthLabel = QLabel(self.mainFrame)
        self.depthLabel.setObjectName(u"depthLabel")
        self.depthLabel.setMinimumSize(QSize(80, 0))

        self.depthLayout.addWidget(self.depthLabel)

        self.depthValueLabel = QLabel(self.mainFrame)
        self.depthValueLabel.setObjectName(u"depthValueLabel")

        self.depthLayout.addWidget(self.depthValueLabel)


        self.dataLayout.addLayout(self.depthLayout)


        self.contentLayout.addLayout(self.dataLayout)

        self.attitudeHeaderLabel = QLabel(self.mainFrame)
        self.attitudeHeaderLabel.setObjectName(u"attitudeHeaderLabel")

        self.contentLayout.addWidget(self.attitudeHeaderLabel)

        self.attitudeLayout = QHBoxLayout()
        self.attitudeLayout.setSpacing(20)
        self.attitudeLayout.setObjectName(u"attitudeLayout")
        self.rollLayout = QHBoxLayout()
        self.rollLayout.setObjectName(u"rollLayout")
        self.rollLabel = QLabel(self.mainFrame)
        self.rollLabel.setObjectName(u"rollLabel")
        self.rollLabel.setMinimumSize(QSize(40, 0))

        self.rollLayout.addWidget(self.rollLabel)

        self.rollValueLabel = QLabel(self.mainFrame)
        self.rollValueLabel.setObjectName(u"rollValueLabel")

        self.rollLayout.addWidget(self.rollValueLabel)


        self.attitudeLayout.addLayout(self.rollLayout)

        self.pitchLayout = QHBoxLayout()
        self.pitchLayout.setObjectName(u"pitchLayout")
        self.pitchLabel = QLabel(self.mainFrame)
        self.pitchLabel.setObjectName(u"pitchLabel")
        self.pitchLabel.setMinimumSize(QSize(40, 0))

        self.pitchLayout.addWidget(self.pitchLabel)

        self.pitchValueLabel = QLabel(self.mainFrame)
        self.pitchValueLabel.setObjectName(u"pitchValueLabel")

        self.pitchLayout.addWidget(self.pitchValueLabel)


        self.attitudeLayout.addLayout(self.pitchLayout)

        self.attitudeSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.attitudeLayout.addItem(self.attitudeSpacer)


        self.contentLayout.addLayout(self.attitudeLayout)

        self.systemsHeaderLabel = QLabel(self.mainFrame)
        self.systemsHeaderLabel.setObjectName(u"systemsHeaderLabel")

        self.contentLayout.addWidget(self.systemsHeaderLabel)

        self.systemsLayout = QVBoxLayout()
        self.systemsLayout.setSpacing(8)
        self.systemsLayout.setObjectName(u"systemsLayout")
        self.batteryLayout = QHBoxLayout()
        self.batteryLayout.setObjectName(u"batteryLayout")
        self.batteryLabel = QLabel(self.mainFrame)
        self.batteryLabel.setObjectName(u"batteryLabel")
        self.batteryLabel.setMinimumSize(QSize(60, 0))

        self.batteryLayout.addWidget(self.batteryLabel)

        self.batteryProgressBar = QProgressBar(self.mainFrame)
        self.batteryProgressBar.setObjectName(u"batteryProgressBar")
        self.batteryProgressBar.setMinimum(0)
        self.batteryProgressBar.setMaximum(100)
        self.batteryProgressBar.setValue(85)

        self.batteryLayout.addWidget(self.batteryProgressBar)


        self.systemsLayout.addLayout(self.batteryLayout)

        self.rudderLayout = QHBoxLayout()
        self.rudderLayout.setObjectName(u"rudderLayout")
        self.rudderLabel = QLabel(self.mainFrame)
        self.rudderLabel.setObjectName(u"rudderLabel")
        self.rudderLabel.setMinimumSize(QSize(60, 0))

        self.rudderLayout.addWidget(self.rudderLabel)

        self.rudderProgressBar = QProgressBar(self.mainFrame)
        self.rudderProgressBar.setObjectName(u"rudderProgressBar")
        self.rudderProgressBar.setMinimum(-30)
        self.rudderProgressBar.setMaximum(30)
        self.rudderProgressBar.setValue(10)

        self.rudderLayout.addWidget(self.rudderProgressBar)


        self.systemsLayout.addLayout(self.rudderLayout)


        self.contentLayout.addLayout(self.systemsLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.contentLayout.addItem(self.verticalSpacer)


        self.mainLayout.addWidget(self.mainFrame)


        self.retranslateUi(USVTelemetryWidget)

        QMetaObject.connectSlotsByName(USVTelemetryWidget)
    # setupUi

    def retranslateUi(self, USVTelemetryWidget):
        USVTelemetryWidget.setWindowTitle(QCoreApplication.translate("USVTelemetryWidget", u"USV Telemetry Dashboard", None))
        self.headerLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"\ud83d\udcca USV TELEMETRY", None))
        self.statusLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Status:", None))
        self.statusValueLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"MANUAL", None))
        self.gpsLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"GPS:", None))
        self.gpsValueLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"41.0370, 29.0295", None))
        self.speedLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Speed:", None))
        self.speedValueLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"5.2 m/s (10.1 knots)", None))
        self.headingLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Heading:", None))
        self.headingValueLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"175\u00b0 (S)", None))
        self.depthLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Depth:", None))
        self.depthValueLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"15.4 m", None))
        self.attitudeHeaderLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Attitude:", None))
        self.rollLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Roll:", None))
        self.rollValueLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"2.1\u00b0", None))
        self.pitchLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Pitch:", None))
        self.pitchValueLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"1.5\u00b0", None))
        self.systemsHeaderLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Systems:", None))
        self.batteryLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Battery:", None))
        self.batteryProgressBar.setFormat(QCoreApplication.translate("USVTelemetryWidget", u"85%", None))
        self.rudderLabel.setText(QCoreApplication.translate("USVTelemetryWidget", u"Rudder:", None))
        self.rudderProgressBar.setFormat(QCoreApplication.translate("USVTelemetryWidget", u"10\u00b0 R", None))
    # retranslateUi

