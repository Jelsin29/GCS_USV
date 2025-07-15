# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TelemetryWidget.ui'
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
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_TelemetryWidget(object):
    def setupUi(self, TelemetryWidget):
        if not TelemetryWidget.objectName():
            TelemetryWidget.setObjectName(u"TelemetryWidget")
        TelemetryWidget.resize(429, 731)
        TelemetryWidget.setStyleSheet(u"\n"
"/* MODERN TELEMETRY WIDGET - LIGHT THEME */\n"
"QWidget {\n"
"    background-color: #f8f9fa;\n"
"    color: #495057;\n"
"    font-family: 'Segoe UI', Arial, sans-serif;\n"
"}\n"
"\n"
"QFrame {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"}\n"
"\n"
"QLabel {\n"
"    color: #495057;\n"
"    border: none;\n"
"    background: transparent;\n"
"}\n"
"   ")
        self.mainLayout = QVBoxLayout(TelemetryWidget)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.titleLabel = QLabel(TelemetryWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.titleLabel)

        self.batteryFrame = QFrame(TelemetryWidget)
        self.batteryFrame.setObjectName(u"batteryFrame")
        self.batteryFrame.setMinimumSize(QSize(0, 80))
        self.batteryLayout = QHBoxLayout(self.batteryFrame)
        self.batteryLayout.setSpacing(15)
        self.batteryLayout.setObjectName(u"batteryLayout")
        self.batteryLabel = QLabel(self.batteryFrame)
        self.batteryLabel.setObjectName(u"batteryLabel")

        self.batteryLayout.addWidget(self.batteryLabel)

        self.batteryPercentLabel = QLabel(self.batteryFrame)
        self.batteryPercentLabel.setObjectName(u"batteryPercentLabel")
        self.batteryPercentLabel.setAlignment(Qt.AlignCenter)

        self.batteryLayout.addWidget(self.batteryPercentLabel)

        self.batteryBarFrame = QFrame(self.batteryFrame)
        self.batteryBarFrame.setObjectName(u"batteryBarFrame")
        self.batteryBarFrame.setMinimumSize(QSize(100, 20))

        self.batteryLayout.addWidget(self.batteryBarFrame)


        self.mainLayout.addWidget(self.batteryFrame)

        self.telemetryFrame = QFrame(TelemetryWidget)
        self.telemetryFrame.setObjectName(u"telemetryFrame")
        self.telemetryLayout = QVBoxLayout(self.telemetryFrame)
        self.telemetryLayout.setSpacing(12)
        self.telemetryLayout.setObjectName(u"telemetryLayout")
        self.rangeFrame = QFrame(self.telemetryFrame)
        self.rangeFrame.setObjectName(u"rangeFrame")
        self.rangeLayout = QHBoxLayout(self.rangeFrame)
        self.rangeLayout.setObjectName(u"rangeLayout")
        self.rangeLabel = QLabel(self.rangeFrame)
        self.rangeLabel.setObjectName(u"rangeLabel")

        self.rangeLayout.addWidget(self.rangeLabel)

        self.rangeValueLabel = QLabel(self.rangeFrame)
        self.rangeValueLabel.setObjectName(u"rangeValueLabel")
        self.rangeValueLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.rangeLayout.addWidget(self.rangeValueLabel)


        self.telemetryLayout.addWidget(self.rangeFrame)

        self.consumptionFrame = QFrame(self.telemetryFrame)
        self.consumptionFrame.setObjectName(u"consumptionFrame")
        self.consumptionLayout = QHBoxLayout(self.consumptionFrame)
        self.consumptionLayout.setObjectName(u"consumptionLayout")
        self.consumptionLabel = QLabel(self.consumptionFrame)
        self.consumptionLabel.setObjectName(u"consumptionLabel")

        self.consumptionLayout.addWidget(self.consumptionLabel)

        self.consumptionValueLabel = QLabel(self.consumptionFrame)
        self.consumptionValueLabel.setObjectName(u"consumptionValueLabel")
        self.consumptionValueLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.consumptionLayout.addWidget(self.consumptionValueLabel)


        self.telemetryLayout.addWidget(self.consumptionFrame)

        self.speedFrame = QFrame(self.telemetryFrame)
        self.speedFrame.setObjectName(u"speedFrame")
        self.speedLayout = QHBoxLayout(self.speedFrame)
        self.speedLayout.setObjectName(u"speedLayout")
        self.speedLabel = QLabel(self.speedFrame)
        self.speedLabel.setObjectName(u"speedLabel")

        self.speedLayout.addWidget(self.speedLabel)

        self.speedValueLabel = QLabel(self.speedFrame)
        self.speedValueLabel.setObjectName(u"speedValueLabel")
        self.speedValueLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.speedLayout.addWidget(self.speedValueLabel)


        self.telemetryLayout.addWidget(self.speedFrame)

        self.headingFrame = QFrame(self.telemetryFrame)
        self.headingFrame.setObjectName(u"headingFrame")
        self.headingLayout = QHBoxLayout(self.headingFrame)
        self.headingLayout.setObjectName(u"headingLayout")
        self.headingLabel = QLabel(self.headingFrame)
        self.headingLabel.setObjectName(u"headingLabel")

        self.headingLayout.addWidget(self.headingLabel)

        self.headingValueLabel = QLabel(self.headingFrame)
        self.headingValueLabel.setObjectName(u"headingValueLabel")
        self.headingValueLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.headingLayout.addWidget(self.headingValueLabel)


        self.telemetryLayout.addWidget(self.headingFrame)


        self.mainLayout.addWidget(self.telemetryFrame)

        self.connectionStatusLabel = QLabel(TelemetryWidget)
        self.connectionStatusLabel.setObjectName(u"connectionStatusLabel")
        self.connectionStatusLabel.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.connectionStatusLabel)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)


        self.retranslateUi(TelemetryWidget)

        QMetaObject.connectSlotsByName(TelemetryWidget)
    # setupUi

    def retranslateUi(self, TelemetryWidget):
        TelemetryWidget.setWindowTitle(QCoreApplication.translate("TelemetryWidget", u"Telemetry", None))
        self.titleLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #ffffff;\n"
"    background-color: #495057;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"    padding: 12px;\n"
"    border-radius: 8px;\n"
"    text-align: center;\n"
"}", None))
        self.titleLabel.setText(QCoreApplication.translate("TelemetryWidget", u"AUTONOMOUS USV", None))
        self.batteryFrame.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QFrame {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 15px;\n"
"}", None))
        self.batteryLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #495057;\n"
"    font-size: 18px;\n"
"    font-weight: 600;\n"
"    background: transparent;\n"
"    border: none;\n"
"}", None))
        self.batteryLabel.setText(QCoreApplication.translate("TelemetryWidget", u"Battery:", None))
        self.batteryPercentLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #28a745;\n"
"    font-size: 32px;\n"
"    font-weight: bold;\n"
"    background: transparent;\n"
"    border: none;\n"
"}", None))
        self.batteryPercentLabel.setText(QCoreApplication.translate("TelemetryWidget", u"50%", None))
        self.batteryBarFrame.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QFrame {\n"
"    background-color: #e9ecef;\n"
"    border: 1px solid #ced4da;\n"
"    border-radius: 10px;\n"
"}", None))
        self.telemetryFrame.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QFrame {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 15px;\n"
"}", None))
        self.rangeFrame.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QFrame {\n"
"    background-color: #e3f2fd;\n"
"    border: 1px solid #bbdefb;\n"
"    border-radius: 8px;\n"
"    padding: 12px;\n"
"}", None))
        self.rangeLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #1976d2;\n"
"    font-weight: 600;\n"
"    font-size: 14px;\n"
"}", None))
        self.rangeLabel.setText(QCoreApplication.translate("TelemetryWidget", u"Estimated Range", None))
        self.rangeValueLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #1976d2;\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"}", None))
        self.rangeValueLabel.setText(QCoreApplication.translate("TelemetryWidget", u"164 km", None))
        self.consumptionFrame.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QFrame {\n"
"    background-color: #fff3e0;\n"
"    border: 1px solid #ffcc02;\n"
"    border-radius: 8px;\n"
"    padding: 12px;\n"
"}", None))
        self.consumptionLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #f57c00;\n"
"    font-weight: 600;\n"
"    font-size: 14px;\n"
"}", None))
        self.consumptionLabel.setText(QCoreApplication.translate("TelemetryWidget", u"Avg. Consumption", None))
        self.consumptionValueLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #f57c00;\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"}", None))
        self.consumptionValueLabel.setText(QCoreApplication.translate("TelemetryWidget", u"304 Wh/km", None))
        self.speedFrame.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QFrame {\n"
"    background-color: #f3e5f5;\n"
"    border: 1px solid #ce93d8;\n"
"    border-radius: 8px;\n"
"    padding: 12px;\n"
"}", None))
        self.speedLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #7b1fa2;\n"
"    font-weight: 600;\n"
"    font-size: 14px;\n"
"}", None))
        self.speedLabel.setText(QCoreApplication.translate("TelemetryWidget", u"Avg. Speed", None))
        self.speedValueLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #7b1fa2;\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"}", None))
        self.speedValueLabel.setText(QCoreApplication.translate("TelemetryWidget", u"43 km/h", None))
        self.headingFrame.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QFrame {\n"
"    background-color: #e8f5e8;\n"
"    border: 1px solid #c3e6cb;\n"
"    border-radius: 8px;\n"
"    padding: 12px;\n"
"}", None))
        self.headingLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #155724;\n"
"    font-weight: 600;\n"
"    font-size: 14px;\n"
"}", None))
        self.headingLabel.setText(QCoreApplication.translate("TelemetryWidget", u"Heading", None))
        self.headingValueLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #155724;\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"}", None))
        self.headingValueLabel.setText(QCoreApplication.translate("TelemetryWidget", u"045\u00b0", None))
        self.connectionStatusLabel.setStyleSheet(QCoreApplication.translate("TelemetryWidget", u"QLabel {\n"
"    color: #28a745;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    background-color: #d4edda;\n"
"    border: 1px solid #c3e6cb;\n"
"    border-radius: 8px;\n"
"    padding: 12px;\n"
"}", None))
        self.connectionStatusLabel.setText(QCoreApplication.translate("TelemetryWidget", u"\u25cf CONNECTED", None))
    # retranslateUi

