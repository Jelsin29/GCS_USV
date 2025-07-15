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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_TargetsPage(object):
    def setupUi(self, TargetsPage):
        if not TargetsPage.objectName():
            TargetsPage.setObjectName(u"TargetsPage")
        TargetsPage.resize(828, 1060)
        TargetsPage.setStyleSheet(u"/* MODERN MISSION CONTROL - LIGHT THEME TESLA STYLE */\n"
"QWidget {\n"
"    background-color: #f5f5f5;\n"
"    color: #2c3e50;\n"
"    font-family: 'Segoe UI', 'San Francisco', Arial, sans-serif;\n"
"}\n"
"\n"
"/* MAIN FRAMES - CLEAN CARDS WITH SHADOWS */\n"
"QFrame {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 16px;\n"
"    margin: 8px;\n"
"    padding: 20px;\n"
"}\n"
"\n"
"/* SECTION TITLES - MODERN STYLE */\n"
"QLabel#missionLabel, QLabel#guidedLabel, QLabel#consoleLabel {\n"
"    color: #2c3e50;\n"
"    font-size: 18px;\n"
"    font-weight: 600;\n"
"    background: transparent;\n"
"    border: none;\n"
"    margin-bottom: 16px;\n"
"    padding: 0px;\n"
"}\n"
"\n"
"/* MODERN BUTTONS - WITH BORDERS, NO SHADOWS */\n"
"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    col"
                        "or: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #e9ecef, stop:1 #dee2e6);\n"
"    border-color: #0d6efd;\n"
"    color: #0d6efd;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}\n"
"\n"
"/* MODERN COMBO BOX - WITH BORDERS */\n"
"QComboBox {\n"
"    background: #ffffff;\n"
"    border: 2px solid #e9ecef;\n"
"    border-radius: 8px;\n"
"    padding: 12px 16px;\n"
"    color: #495057;\n"
"    font-weight: 500;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border-color: #0d6efd;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    border: none;\n"
"    width: 30px;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: none;\n"
"    border-left: 5px solid transparent;\n"
"    border-right: 5px solid t"
                        "ransparent;\n"
"    border-top: 5px solid #495057;\n"
"    margin-right: 10px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #e9ecef;\n"
"    border-radius: 8px;\n"
"    selection-background-color: #0d6efd;\n"
"    color: #495057;\n"
"}\n"
"\n"
"/* SPECIAL BUTTON COLORS - WITH BORDERS */\n"
"QPushButton#btn_antenna {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #dc3545, stop:1 #c82333);\n"
"    border: 2px solid #bd2130;\n"
"    color: #495057;\n"
"}\n"
"\n"
"QPushButton#btn_antenna:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #c82333, stop:1 #bd2130);\n"
"    border-color: #a71e2a;\n"
"}\n"
"\n"
"QPushButton#btn_startMission {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #28a745, stop:1 #20c997);\n"
"    border: 2px solid #1e7e34;\n"
"    color: #495057;\n"
"}\n"
"\n"
"QP"
                        "ushButton#btn_startMission:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #20c997, stop:1 #1e7e34);\n"
"    border-color: #155724;\n"
"}\n"
"\n"
"QPushButton#btn_abort {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #ffc107, stop:1 #e0a800);\n"
"    border: 2px solid #d39e00;\n"
"    color: #495057;\n"
"}\n"
"\n"
"QPushButton#btn_abort:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #e0a800, stop:1 #d39e00);\n"
"    border-color: #b8860b;\n"
"}\n"
"\n"
"/* CONSOLE - DARK TERMINAL STYLE */\n"
"QTextBrowser {\n"
"    background-color: #212529;\n"
"    color: #00ff88;\n"
"    border: 1px solid #495057;\n"
"    border-radius: 8px;\n"
"    font-family: 'Consolas', 'SF Mono', monospace;\n"
"    font-size: 12px;\n"
"    padding: 16px;\n"
"}\n"
"\n"
"/* SECTION BACKGROUNDS - SUBTLE DIFFERENT COLORS WITH BORDERS */\n"
"QFrame#missionFrame"
                        " {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #e9ecef;\n"
"}\n"
"\n"
"QFrame#guidedFrame {\n"
"    background-color: #f8f9fa;\n"
"    border: 1px solid #dee2e6;\n"
"}\n"
"\n"
"QFrame#consoleFrame {\n"
"    background-color: #2d3748;\n"
"    border: 1px solid #4a5568;\n"
"}\n"
"\n"
"/* CLEAN LABELS */\n"
"QLabel {\n"
"    color: #2c3e50;\n"
"    background: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"/* CONSOLE LABEL - WHITE FOR DARK BACKGROUND */\n"
"QLabel#consoleLabel {\n"
"    color: #ffffff;\n"
"}\n"
"   ")
        self.mainHorizontalLayout = QHBoxLayout(TargetsPage)
        self.mainHorizontalLayout.setSpacing(16)
        self.mainHorizontalLayout.setObjectName(u"mainHorizontalLayout")
        self.mainHorizontalLayout.setContentsMargins(16, 16, 16, 16)
        self.leftColumn = QWidget(TargetsPage)
        self.leftColumn.setObjectName(u"leftColumn")
        self.leftColumn.setMinimumSize(QSize(400, 0))
        self.leftColumnLayout = QVBoxLayout(self.leftColumn)
        self.leftColumnLayout.setSpacing(20)
        self.leftColumnLayout.setObjectName(u"leftColumnLayout")
        self.leftColumnLayout.setContentsMargins(0, 0, 0, 0)
        self.missionFrame = QFrame(self.leftColumn)
        self.missionFrame.setObjectName(u"missionFrame")
        self.missionLayout = QVBoxLayout(self.missionFrame)
        self.missionLayout.setSpacing(20)
        self.missionLayout.setObjectName(u"missionLayout")
        self.missionLayout.setContentsMargins(0, 0, 0, 0)
        self.missionLabel = QLabel(self.missionFrame)
        self.missionLabel.setObjectName(u"missionLabel")

        self.missionLayout.addWidget(self.missionLabel)

        self.modeSelectionWidget = QWidget(self.missionFrame)
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

        self.modeSelectionLayout.addWidget(self.modes_comboBox)

        self.btn_chooseMode = QPushButton(self.modeSelectionWidget)
        self.btn_chooseMode.setObjectName(u"btn_chooseMode")
        self.btn_chooseMode.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.modeSelectionLayout.addWidget(self.btn_chooseMode)


        self.missionLayout.addWidget(self.modeSelectionWidget)

        self.missionButtonsGrid = QGridLayout()
        self.missionButtonsGrid.setSpacing(12)
        self.missionButtonsGrid.setObjectName(u"missionButtonsGrid")
        self.btn_setMission = QPushButton(self.missionFrame)
        self.btn_setMission.setObjectName(u"btn_setMission")
        self.btn_setMission.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.missionButtonsGrid.addWidget(self.btn_setMission, 0, 0, 1, 1)

        self.btn_undo = QPushButton(self.missionFrame)
        self.btn_undo.setObjectName(u"btn_undo")
        self.btn_undo.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.missionButtonsGrid.addWidget(self.btn_undo, 0, 1, 1, 1)

        self.btn_clearAll = QPushButton(self.missionFrame)
        self.btn_clearAll.setObjectName(u"btn_clearAll")
        self.btn_clearAll.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.missionButtonsGrid.addWidget(self.btn_clearAll, 1, 0, 1, 2)


        self.missionLayout.addLayout(self.missionButtonsGrid)

        self.btn_antenna = QPushButton(self.missionFrame)
        self.btn_antenna.setObjectName(u"btn_antenna")
        self.btn_antenna.setStyleSheet(u"\n"
"/* ANTENNA BUTTON - RED STATE (DEFAULT) */\n"
"QPushButton#btn_antenna {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #dc3545, stop:1 #c82333);\n"
"    border: 2px solid #bd2130;\n"
"    color: #ffffff;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"/* ANTENNA BUTTON - DARKER RED ON HOVER (WHEN NOT ACTIVE) */\n"
"QPushButton#btn_antenna:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #c82333, stop:1 #a71e2a);\n"
"    border-color: #a71e2a;\n"
"    color: #ffffff;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"/* ANTENNA BUTTON - PRESSED STATE (MOMENTARY) */\n"
"QPushButton#btn_antenna:pressed {\n"
"    background: #a71e2a;\n"
"    border-color: #921924;\n"
"    transform: translateY(0px);\n"
"}\n"
"\n"
"/* ANTENNA BUTTON - ACTIVE/TRACKING STATE (GREEN) */\n"
"QPushButton#btn_antenn"
                        "a[tracking=\"true\"] {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #28a745, stop:1 #1e7e34);\n"
"    border: 2px solid #155724;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"/* ANTENNA BUTTON - GREEN STATE HOVER (DARKER GREEN) */\n"
"QPushButton#btn_antenna[tracking=\"true\"]:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #1e7e34, stop:1 #155724);\n"
"    border-color: #0f5132;\n"
"    color: #ffffff;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"/* ANTENNA BUTTON - GREEN STATE PRESSED */\n"
"QPushButton#btn_antenna[tracking=\"true\"]:pressed {\n"
"    background: #155724;\n"
"    border-color: #0f5132;\n"
"    transform: translateY(0px);\n"
"}")

        self.missionLayout.addWidget(self.btn_antenna)

        self.executionButtonsLayout = QHBoxLayout()
        self.executionButtonsLayout.setSpacing(12)
        self.executionButtonsLayout.setObjectName(u"executionButtonsLayout")
        self.btn_startMission = QPushButton(self.missionFrame)
        self.btn_startMission.setObjectName(u"btn_startMission")
        self.btn_startMission.setStyleSheet(u"QPushButton#btn_startMission {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #28a745, stop:1 #20c997);\n"
"    border: 2px solid #1e7e34;\n"
"    color: #ffffff;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton#btn_startMission:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #1e7e34, stop:1 #155724);\n"
"    border-color: #0f5132;\n"
"    color: #ffffff;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton#btn_startMission:pressed {\n"
"    background: #155724;\n"
"    border-color: #0f5132;\n"
"    transform: translateY(0px);\n"
"}")

        self.executionButtonsLayout.addWidget(self.btn_startMission)

        self.btn_abort = QPushButton(self.missionFrame)
        self.btn_abort.setObjectName(u"btn_abort")
        self.btn_abort.setStyleSheet(u"QPushButton#btn_abort {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #dc3545, stop:1 #c82333);\n"
"    border: 2px solid #bd2130;\n"
"    color: #ffffff;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton#btn_abort:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #c82333, stop:1 #a71e2a);\n"
"    border-color: #a71e2a;\n"
"    color: #ffffff;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton#btn_abort:pressed {\n"
"    background: #a71e2a;\n"
"    border-color: #921924;\n"
"    transform: translateY(0px);\n"
"}")

        self.executionButtonsLayout.addWidget(self.btn_abort)


        self.missionLayout.addLayout(self.executionButtonsLayout)

        self.btn_rtl = QPushButton(self.missionFrame)
        self.btn_rtl.setObjectName(u"btn_rtl")
        self.btn_rtl.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.missionLayout.addWidget(self.btn_rtl)


        self.leftColumnLayout.addWidget(self.missionFrame)

        self.guidedFrame = QFrame(self.leftColumn)
        self.guidedFrame.setObjectName(u"guidedFrame")
        self.guidedLayout = QVBoxLayout(self.guidedFrame)
        self.guidedLayout.setSpacing(20)
        self.guidedLayout.setObjectName(u"guidedLayout")
        self.guidedLayout.setContentsMargins(0, 0, 0, 0)
        self.guidedLabel = QLabel(self.guidedFrame)
        self.guidedLabel.setObjectName(u"guidedLabel")

        self.guidedLayout.addWidget(self.guidedLabel)

        self.guidedButtonsGrid = QGridLayout()
        self.guidedButtonsGrid.setSpacing(12)
        self.guidedButtonsGrid.setObjectName(u"guidedButtonsGrid")
        self.btn_takeoff = QPushButton(self.guidedFrame)
        self.btn_takeoff.setObjectName(u"btn_takeoff")
        self.btn_takeoff.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.guidedButtonsGrid.addWidget(self.btn_takeoff, 0, 0, 1, 1)

        self.btn_move = QPushButton(self.guidedFrame)
        self.btn_move.setObjectName(u"btn_move")
        self.btn_move.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.guidedButtonsGrid.addWidget(self.btn_move, 0, 1, 1, 1)

        self.btn_track_all = QPushButton(self.guidedFrame)
        self.btn_track_all.setObjectName(u"btn_track_all")
        self.btn_track_all.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.guidedButtonsGrid.addWidget(self.btn_track_all, 1, 0, 1, 1)

        self.btn_land = QPushButton(self.guidedFrame)
        self.btn_land.setObjectName(u"btn_land")
        self.btn_land.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.guidedButtonsGrid.addWidget(self.btn_land, 1, 1, 1, 1)

        self.btn_rtl_2 = QPushButton(self.guidedFrame)
        self.btn_rtl_2.setObjectName(u"btn_rtl_2")
        self.btn_rtl_2.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.guidedButtonsGrid.addWidget(self.btn_rtl_2, 2, 0, 1, 2)

        self.btn_set_roi = QPushButton(self.guidedFrame)
        self.btn_set_roi.setObjectName(u"btn_set_roi")
        self.btn_set_roi.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.guidedButtonsGrid.addWidget(self.btn_set_roi, 3, 0, 1, 1)

        self.btn_cancel_roi = QPushButton(self.guidedFrame)
        self.btn_cancel_roi.setObjectName(u"btn_cancel_roi")
        self.btn_cancel_roi.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"    border: 2px solid #dee2e6;\n"
"    border-radius: 12px;\n"
"    padding: 16px 24px;\n"
"    color: #495057;\n"
"    font-weight: 600;\n"
"    font-size: 15px;\n"
"    min-height: 24px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"                               stop:0 #f1f3f4, stop:1 #e8eaed);\n"
"    border-color: #ced4da;\n"
"    color: #343a40;\n"
"    transform: translateY(-1px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #dee2e6;\n"
"    border-color: #ced4da;\n"
"    transform: translateY(0px);\n"
"}")

        self.guidedButtonsGrid.addWidget(self.btn_cancel_roi, 3, 1, 1, 1)


        self.guidedLayout.addLayout(self.guidedButtonsGrid)


        self.leftColumnLayout.addWidget(self.guidedFrame)


        self.mainHorizontalLayout.addWidget(self.leftColumn)

        self.consoleFrame = QFrame(TargetsPage)
        self.consoleFrame.setObjectName(u"consoleFrame")
        self.consoleFrame.setMinimumSize(QSize(380, 0))
        self.consoleLayout = QVBoxLayout(self.consoleFrame)
        self.consoleLayout.setSpacing(20)
        self.consoleLayout.setObjectName(u"consoleLayout")
        self.consoleLayout.setContentsMargins(0, 0, 0, 0)
        self.consoleLabel = QLabel(self.consoleFrame)
        self.consoleLabel.setObjectName(u"consoleLabel")

        self.consoleLayout.addWidget(self.consoleLabel)

        self.textBrowser = QTextBrowser(self.consoleFrame)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setMinimumSize(QSize(0, 500))

        self.consoleLayout.addWidget(self.textBrowser)


        self.mainHorizontalLayout.addWidget(self.consoleFrame)


        self.retranslateUi(TargetsPage)

        QMetaObject.connectSlotsByName(TargetsPage)
    # setupUi

    def retranslateUi(self, TargetsPage):
        TargetsPage.setWindowTitle(QCoreApplication.translate("TargetsPage", u"Mission Control", None))
        self.leftColumn.setStyleSheet(QCoreApplication.translate("TargetsPage", u"QWidget { background: transparent; }", None))
        self.missionLabel.setText(QCoreApplication.translate("TargetsPage", u"MISSION PLANNING", None))
        self.modeSelectionWidget.setStyleSheet(QCoreApplication.translate("TargetsPage", u"QWidget { background: transparent; }", None))
        self.modes_comboBox.setItemText(0, QCoreApplication.translate("TargetsPage", u"Select Map Mode", None))
        self.modes_comboBox.setItemText(1, QCoreApplication.translate("TargetsPage", u"Marker Mode", None))
        self.modes_comboBox.setItemText(2, QCoreApplication.translate("TargetsPage", u"Area Selection Mode", None))
        self.modes_comboBox.setItemText(3, QCoreApplication.translate("TargetsPage", u"Waypoint Mode", None))

        self.btn_chooseMode.setText(QCoreApplication.translate("TargetsPage", u"SELECT", None))
        self.btn_setMission.setText(QCoreApplication.translate("TargetsPage", u"DEFINE MISSION", None))
        self.btn_undo.setText(QCoreApplication.translate("TargetsPage", u"UNDO", None))
        self.btn_clearAll.setText(QCoreApplication.translate("TargetsPage", u"CLEAR ALL", None))
        self.btn_antenna.setText(QCoreApplication.translate("TargetsPage", u"ANTENNA TRACKING", None))
        self.btn_startMission.setText(QCoreApplication.translate("TargetsPage", u"START MISSION", None))
        self.btn_abort.setText(QCoreApplication.translate("TargetsPage", u"STOP", None))
        self.btn_rtl.setText(QCoreApplication.translate("TargetsPage", u"RETURN HOME", None))
        self.guidedLabel.setText(QCoreApplication.translate("TargetsPage", u"GUIDED CONTROL", None))
        self.btn_takeoff.setText(QCoreApplication.translate("TargetsPage", u"TAKEOFF", None))
        self.btn_move.setText(QCoreApplication.translate("TargetsPage", u"GO TO POINT", None))
        self.btn_track_all.setText(QCoreApplication.translate("TargetsPage", u"TRACK ALL", None))
        self.btn_land.setText(QCoreApplication.translate("TargetsPage", u"LAND", None))
        self.btn_rtl_2.setText(QCoreApplication.translate("TargetsPage", u"RETURN HOME", None))
        self.btn_set_roi.setText(QCoreApplication.translate("TargetsPage", u"SET ROI", None))
        self.btn_cancel_roi.setText(QCoreApplication.translate("TargetsPage", u"CANCEL ROI", None))
        self.consoleLabel.setText(QCoreApplication.translate("TargetsPage", u"CONSOLE", None))
    # retranslateUi

