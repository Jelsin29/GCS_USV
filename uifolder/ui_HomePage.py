# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'HomePage.ui'
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

class Ui_HomePage(object):
    def setupUi(self, HomePage):
        if not HomePage.objectName():
            HomePage.setObjectName(u"HomePage")
        HomePage.resize(1400, 900)
        HomePage.setStyleSheet(u"\n"
"/* MODERN HOMEPAGE - TESLA DASHBOARD STYLE */\n"
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
"}\n"
"\n"
"/* CAMERA FRAME - CLEAN MODERN */\n"
"QWidget#cameraFrame {\n"
"    background: #ffffff;\n"
"    border: none;\n"
"    border-radius: 16px;\n"
"    margin: 8px;\n"
"}\n"
"\n"
"/* MAP FRAME - TESLA STYLE */\n"
"QWidget#mapFrame {\n"
"    background: #ffffff;\n"
"    border: none;\n"
"    border-radius: 16px;\n"
"    margin: 8px;\n"
"}\n"
"\n"
"/* TELEMETRY FRAME - MODERN CARD */\n"
"QFrame#futureContentFrame {\n"
"    background: #ffffff;\n"
"    border: none;\n"
"    border-radius: 16px;\n"
"    margin: 8px;\n"
"    padding: 16px;\n"
"}\n"
"   ")
        self.mainHorizontalLayout = QHBoxLayout(HomePage)
        self.mainHorizontalLayout.setSpacing(0)
        self.mainHorizontalLayout.setObjectName(u"mainHorizontalLayout")
        self.mainHorizontalLayout.setContentsMargins(16, 16, 16, 16)
        self.leftFrame = QFrame(HomePage)
        self.leftFrame.setObjectName(u"leftFrame")
        self.leftFrame.setMinimumSize(QSize(400, 0))
        self.leftFrame.setMaximumSize(QSize(450, 16777215))
        self.leftFrame.setStyleSheet(u"QFrame {\n"
"    background: transparent;\n"
"    border: none;\n"
"    margin: 0px;\n"
"}")
        self.leftFrame.setFrameShape(QFrame.StyledPanel)
        self.leftFrame.setFrameShadow(QFrame.Raised)
        self.leftVerticalLayout = QVBoxLayout(self.leftFrame)
        self.leftVerticalLayout.setSpacing(16)
        self.leftVerticalLayout.setObjectName(u"leftVerticalLayout")
        self.leftVerticalLayout.setContentsMargins(0, 0, 8, 0)
        self.cameraFrame = QWidget(self.leftFrame)
        self.cameraFrame.setObjectName(u"cameraFrame")
        self.cameraFrame.setMinimumSize(QSize(0, 350))
        self.cameraFrame.setMaximumSize(QSize(16777215, 400))
        self.cameraFrame.setStyleSheet(u"QWidget{\n"
"    background: transparent;\n"
"    border: none;\n"
"}")
        self.horizontalLayout_3 = QHBoxLayout(self.cameraFrame)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.leftVerticalLayout.addWidget(self.cameraFrame)

        self.futureContentFrame = QFrame(self.leftFrame)
        self.futureContentFrame.setObjectName(u"futureContentFrame")
        self.futureContentFrame.setStyleSheet(u"QFrame{\n"
"     background: transparent;\n"
"     border: none;\n"
" }")
        self.futureContentFrame.setFrameShape(QFrame.StyledPanel)
        self.futureContentFrame.setFrameShadow(QFrame.Raised)
        self.futureContentLayout = QVBoxLayout(self.futureContentFrame)
        self.futureContentLayout.setSpacing(0)
        self.futureContentLayout.setObjectName(u"futureContentLayout")
        self.futureContentLayout.setContentsMargins(0, 0, 0, 0)
        self.futureContentLabel = QLabel(self.futureContentFrame)
        self.futureContentLabel.setObjectName(u"futureContentLabel")
        self.futureContentLabel.setAlignment(Qt.AlignCenter)

        self.futureContentLayout.addWidget(self.futureContentLabel)


        self.leftVerticalLayout.addWidget(self.futureContentFrame)

        self.droneFrame = QFrame(self.leftFrame)
        self.droneFrame.setObjectName(u"droneFrame")
        self.droneFrame.setMinimumSize(QSize(0, 80))
        self.droneFrame.setStyleSheet(u"QFrame {\n"
"     background: transparent;\n"
"     border: none;\n"
"     margin: 0px;\n"
" }")
        self.droneFrame.setFrameShape(QFrame.StyledPanel)
        self.droneFrame.setFrameShadow(QFrame.Raised)
        self.droneFrameLayout = QVBoxLayout(self.droneFrame)
        self.droneFrameLayout.setSpacing(0)
        self.droneFrameLayout.setObjectName(u"droneFrameLayout")
        self.droneFrameLayout.setContentsMargins(0, 0, 0, 0)

        self.leftVerticalLayout.addWidget(self.droneFrame)


        self.mainHorizontalLayout.addWidget(self.leftFrame)

        self.mapFrame = QWidget(HomePage)
        self.mapFrame.setObjectName(u"mapFrame")
        self.mapFrame.setMinimumSize(QSize(650, 0))
        self.mapFrame.setStyleSheet(u"QWidget{\n"
"    background: transparent;\n"
"    border: none;\n"
"}")
        self.horizontalLayout_2 = QHBoxLayout(self.mapFrame)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)

        self.mainHorizontalLayout.addWidget(self.mapFrame)


        self.retranslateUi(HomePage)

        QMetaObject.connectSlotsByName(HomePage)
    # setupUi

    def retranslateUi(self, HomePage):
        HomePage.setWindowTitle(QCoreApplication.translate("HomePage", u"Form", None))
        self.futureContentLabel.setStyleSheet(QCoreApplication.translate("HomePage", u"QLabel { \n"
"     color: #6c757d; \n"
"     font-size: 14px; \n"
"     font-style: italic;\n"
"     border: none;\n"
"     background: transparent;\n"
" }", None))
        self.futureContentLabel.setText("")
    # retranslateUi

