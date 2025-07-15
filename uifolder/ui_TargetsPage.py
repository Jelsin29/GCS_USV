# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TargetsPage.ui'
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
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_TargetsPage(object):
    def setupUi(self, TargetsPage):
        if not TargetsPage.objectName():
            TargetsPage.setObjectName(u"TargetsPage")
        TargetsPage.resize(800, 600)
        TargetsPage.setStyleSheet(u"\n"
"/* MODERN MISSION CONTROL - TESLA STYLE */\n"
"QWidget {\n"
"    background-color: #f5f5f5;\n"
"    color: #2c3e50;\n"
"    font-family: 'Segoe UI', 'San Francisco', Arial, sans-serif;\n"
"}\n"
"\n"
"QFrame {\n"
"    background-color: #ffffff;\n"
"    border: none;\n"
"    border-radius: 16px;\n"
"    margin: 8px;\n"
"    padding: 20px;\n"
"    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);\n"
"}\n"
"\n"
"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: none;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #e9ecef, stop:1 #dee2e6);\n"
"    transform: translateY(-2px);\n"
"    box-shadow: 0 4px 16px rgba(0,"
                        " 0, 0, 0.12);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    transform: translateY(0px);\n"
"    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);\n"
"}\n"
"\n"
"QComboBox {\n"
"    background: #ffffff;\n"
"    border: 2px solid #e9ecef;\n"
"    border-radius: 8px;\n"
"    padding: 12px 16px;\n"
"    color: #495057;\n"
"    font-weight: 500;\n"
"    font-size: 14px;\n"
"    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border-color: #0d6efd;\n"
"    box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);\n"
"}\n"
"\n"
"QLabel {\n"
"    color: #2c3e50;\n"
"    font-weight: 600;\n"
"    font-size: 16px;\n"
"    background: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"/* HOVER EFFECTS FOR FRAMES */\n"
"QFrame:hover {\n"
"    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);\n"
"    transform: translateY(-2px);\n"
"}\n"
"   ")
        self.mainVerticalLayout = QVBoxLayout(TargetsPage)
        self.mainVerticalLayout.setSpacing(20)
        self.mainVerticalLayout.setObjectName(u"mainVerticalLayout")
        self.mainVerticalLayout.setContentsMargins(30, 30, 30, 30)
        self.missionPlanningFrame = QFrame(TargetsPage)
        self.missionPlanningFrame.setObjectName(u"missionPlanningFrame")
        self.missionPlanningFrame.setStyleSheet(u"QFrame{\n"
"    background-color: #f8f9fa;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 8px;\n"
"}")
        self.missionPlanningFrame.setFrameShape(QFrame.StyledPanel)
        self.missionPlanningLayout = QVBoxLayout(self.missionPlanningFrame)
        self.missionPlanningLayout.setSpacing(15)
        self.missionPlanningLayout.setObjectName(u"missionPlanningLayout")
        self.missionPlanningLayout.setContentsMargins(20, 20, 20, 20)
        self.missionPlanningLabel = QLabel(self.missionPlanningFrame)
        self.missionPlanningLabel.setObjectName(u"missionPlanningLabel")

        self.missionPlanningLayout.addWidget(self.missionPlanningLabel)

        self.modeSelectionWidget = QWidget(self.missionPlanningFrame)
        self.modeSelectionWidget.setObjectName(u"modeSelectionWidget")
        self.modeSelectionLayout = QHBoxLayout(self.modeSelectionWidget)
        self.modeSelectionLayout.setSpacing(12)
        self.modeSelectionLayout.setObjectName(u"modeSelectionLayout")
        self.modes_comboBox = QComboBox(self.modeSelectionWidget)
        self.modes_comboBox.addItem("")
        self.modes_comboBox.addItem("")
        self.modes_comboBox.addItem("")
        self.modes_comboBox.addItem("")
        self.modes_comboBox.setObjectName(u"modes_comboBox")
        self.modes_comboBox.setMinimumHeight(40)

        self.modeSelectionLayout.addWidget(self.modes_comboBox)

        self.btn_chooseMode = QPushButton(self.modeSelectionWidget)
        self.btn_chooseMode.setObjectName(u"btn_chooseMode")
        self.btn_chooseMode.setMinimumHeight(40)

        self.modeSelectionLayout.addWidget(self.btn_chooseMode)

        self.modeSelectionLayout.setStretch(0, 3)
        self.modeSelectionLayout.setStretch(1, 1)

        self.missionPlanningLayout.addWidget(self.modeSelectionWidget)

        self.missionButtonsLayout = QHBoxLayout()
        self.missionButtonsLayout.setSpacing(12)
        self.missionButtonsLayout.setObjectName(u"missionButtonsLayout")
        self.btn_setMission = QPushButton(self.missionPlanningFrame)
        self.btn_setMission.setObjectName(u"btn_setMission")
        self.btn_setMission.setMinimumHeight(40)

        self.missionButtonsLayout.addWidget(self.btn_setMission)

        self.btn_undo = QPushButton(self.missionPlanningFrame)
        self.btn_undo.setObjectName(u"btn_undo")
        self.btn_undo.setMinimumHeight(40)

        self.missionButtonsLayout.addWidget(self.btn_undo)

        self.btn_clearAll = QPushButton(self.missionPlanningFrame)
        self.btn_clearAll.setObjectName(u"btn_clearAll")
        self.btn_clearAll.setMinimumHeight(40)

        self.missionButtonsLayout.addWidget(self.btn_clearAll)


        self.missionPlanningLayout.addLayout(self.missionButtonsLayout)


        self.mainVerticalLayout.addWidget(self.missionPlanningFrame)

        self.antennaFrame = QFrame(TargetsPage)
        self.antennaFrame.setObjectName(u"antennaFrame")
        self.antennaFrame.setStyleSheet(u"QFrame{\n"
"    background-color: #f8f9fa;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 8px;\n"
"}")
        self.antennaFrame.setFrameShape(QFrame.StyledPanel)
        self.antennaLayout = QVBoxLayout(self.antennaFrame)
        self.antennaLayout.setSpacing(15)
        self.antennaLayout.setObjectName(u"antennaLayout")
        self.antennaLayout.setContentsMargins(20, 20, 20, 20)
        self.antennaLabel = QLabel(self.antennaFrame)
        self.antennaLabel.setObjectName(u"antennaLabel")

        self.antennaLayout.addWidget(self.antennaLabel)

        self.btn_antenna = QPushButton(self.antennaFrame)
        self.btn_antenna.setObjectName(u"btn_antenna")
        self.btn_antenna.setStyleSheet(u"QPushButton{\n"
"    border-radius: 4px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                      stop:0 #dc3545, stop:1 #c82333);\n"
"    border: 1px solid #bd2130;\n"
"    color: #ffffff;\n"
"    font-weight: 600;\n"
"    padding: 12px 16px;\n"
"    min-height: 24px;\n"
"}\n"
"QPushButton:hover{ \n"
"    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                      stop:0 #c82333, stop:1 #bd2130);\n"
"}\n"
"QPushButton:pressed{\n"
"    background-color: #bd2130;\n"
"}\n"
"QPushButton:disabled{ \n"
"    background-color: #6c757d;\n"
"    border-color: #6c757d;\n"
"    color: #ffffff;\n"
"}")
        self.btn_antenna.setMinimumHeight(50)

        self.antennaLayout.addWidget(self.btn_antenna)


        self.mainVerticalLayout.addWidget(self.antennaFrame)

        self.missionExecutionFrame = QFrame(TargetsPage)
        self.missionExecutionFrame.setObjectName(u"missionExecutionFrame")
        self.missionExecutionFrame.setStyleSheet(u"QFrame{\n"
"    background-color: #f8f9fa;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 8px;\n"
"}")
        self.missionExecutionFrame.setFrameShape(QFrame.StyledPanel)
        self.missionExecutionLayout = QVBoxLayout(self.missionExecutionFrame)
        self.missionExecutionLayout.setSpacing(15)
        self.missionExecutionLayout.setObjectName(u"missionExecutionLayout")
        self.missionExecutionLayout.setContentsMargins(20, 20, 20, 20)
        self.missionExecutionLabel = QLabel(self.missionExecutionFrame)
        self.missionExecutionLabel.setObjectName(u"missionExecutionLabel")

        self.missionExecutionLayout.addWidget(self.missionExecutionLabel)

        self.executionButtonsLayout = QHBoxLayout()
        self.executionButtonsLayout.setSpacing(12)
        self.executionButtonsLayout.setObjectName(u"executionButtonsLayout")
        self.btn_startMission = QPushButton(self.missionExecutionFrame)
        self.btn_startMission.setObjectName(u"btn_startMission")
        self.btn_startMission.setMinimumHeight(50)

        self.executionButtonsLayout.addWidget(self.btn_startMission)

        self.btn_abort = QPushButton(self.missionExecutionFrame)
        self.btn_abort.setObjectName(u"btn_abort")
        self.btn_abort.setMinimumHeight(50)

        self.executionButtonsLayout.addWidget(self.btn_abort)


        self.missionExecutionLayout.addLayout(self.executionButtonsLayout)

        self.btn_rtl = QPushButton(self.missionExecutionFrame)
        self.btn_rtl.setObjectName(u"btn_rtl")
        self.btn_rtl.setMinimumHeight(40)

        self.missionExecutionLayout.addWidget(self.btn_rtl)


        self.mainVerticalLayout.addWidget(self.missionExecutionFrame)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainVerticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(TargetsPage)

        QMetaObject.connectSlotsByName(TargetsPage)
    # setupUi

    def retranslateUi(self, TargetsPage):
        TargetsPage.setWindowTitle(QCoreApplication.translate("TargetsPage", u"Mission Control", None))
        self.missionPlanningLabel.setText(QCoreApplication.translate("TargetsPage", u"Mission Planning", None))
        self.missionPlanningLabel.setStyleSheet(QCoreApplication.translate("TargetsPage", u"QLabel { font-size: 16px; font-weight: bold; color: #495057; }", None))
        self.modes_comboBox.setItemText(0, QCoreApplication.translate("TargetsPage", u"Select Map Mode", None))
        self.modes_comboBox.setItemText(1, QCoreApplication.translate("TargetsPage", u"Marker Mode", None))
        self.modes_comboBox.setItemText(2, QCoreApplication.translate("TargetsPage", u"Area Selection Mode", None))
        self.modes_comboBox.setItemText(3, QCoreApplication.translate("TargetsPage", u"Waypoint Mode", None))

        self.btn_chooseMode.setText(QCoreApplication.translate("TargetsPage", u"Select Mode", None))
        self.btn_setMission.setText(QCoreApplication.translate("TargetsPage", u"Define Mission", None))
        self.btn_undo.setText(QCoreApplication.translate("TargetsPage", u"Undo", None))
        self.btn_clearAll.setText(QCoreApplication.translate("TargetsPage", u"Clear All", None))
        self.antennaLabel.setText(QCoreApplication.translate("TargetsPage", u"Antenna Control", None))
        self.antennaLabel.setStyleSheet(QCoreApplication.translate("TargetsPage", u"QLabel { font-size: 16px; font-weight: bold; color: #495057; }", None))
        self.btn_antenna.setText(QCoreApplication.translate("TargetsPage", u"Antenna Tracking", None))
        self.missionExecutionLabel.setText(QCoreApplication.translate("TargetsPage", u"Mission Execution", None))
        self.missionExecutionLabel.setStyleSheet(QCoreApplication.translate("TargetsPage", u"QLabel { font-size: 16px; font-weight: bold; color: #495057; }", None))
        self.btn_startMission.setText(QCoreApplication.translate("TargetsPage", u"Start Mission", None))
        self.btn_startMission.setStyleSheet(QCoreApplication.translate("TargetsPage", u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                stop:0 #28a745, stop:1 #20c997);\n"
"    border: 1px solid #1e7e34;\n"
"    color: #ffffff;\n"
"    font-weight: 600;\n"
"    padding: 12px 16px;\n"
"    min-height: 24px;\n"
"}\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                stop:0 #20c997, stop:1 #1e7e34);\n"
"}", None))
        self.btn_abort.setText(QCoreApplication.translate("TargetsPage", u"Stop Tracking", None))
        self.btn_abort.setStyleSheet(QCoreApplication.translate("TargetsPage", u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                stop:0 #ffc107, stop:1 #e0a800);\n"
"    border: 1px solid #d39e00;\n"
"    color: #212529;\n"
"    font-weight: 600;\n"
"    padding: 12px 16px;\n"
"    min-height: 24px;\n"
"}\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                                stop:0 #e0a800, stop:1 #d39e00);\n"
"}", None))
        self.btn_rtl.setText(QCoreApplication.translate("TargetsPage", u"Return Home", None))
    # retranslateUi

