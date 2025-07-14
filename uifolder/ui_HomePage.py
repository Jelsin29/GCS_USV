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
"/* MODERN HOMEPAGE STYLING */\n"
"QWidget {\n"
"    background-color: #ffffff;\n"
"    color: #495057;\n"
"}\n"
"\n"
"QFrame {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 8px;\n"
"}\n"
"   ")
        self.mainHorizontalLayout = QHBoxLayout(HomePage)
        self.mainHorizontalLayout.setSpacing(12)
        self.mainHorizontalLayout.setObjectName(u"mainHorizontalLayout")
        self.mainHorizontalLayout.setContentsMargins(12, 12, 12, 12)
        self.leftFrame = QFrame(HomePage)
        self.leftFrame.setObjectName(u"leftFrame")
        self.leftFrame.setMinimumSize(QSize(400, 0))
        self.leftFrame.setMaximumSize(QSize(450, 16777215))
        self.leftFrame.setStyleSheet(u"QFrame{\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 8px;\n"
"}")
        self.leftFrame.setFrameShape(QFrame.StyledPanel)
        self.leftFrame.setFrameShadow(QFrame.Raised)
        self.leftVerticalLayout = QVBoxLayout(self.leftFrame)
        self.leftVerticalLayout.setSpacing(12)
        self.leftVerticalLayout.setObjectName(u"leftVerticalLayout")
        self.leftVerticalLayout.setContentsMargins(12, 12, 12, 12)
        self.cameraFrame = QWidget(self.leftFrame)
        self.cameraFrame.setObjectName(u"cameraFrame")
        self.cameraFrame.setMinimumSize(QSize(0, 350))
        self.cameraFrame.setMaximumSize(QSize(16777215, 400))
        self.cameraFrame.setStyleSheet(u"QWidget{\n"
"    background-color: #f8f9fa;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 8px;\n"
"}")
        self.horizontalLayout_3 = QHBoxLayout(self.cameraFrame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.leftVerticalLayout.addWidget(self.cameraFrame)

        self.futureContentFrame = QFrame(self.leftFrame)
        self.futureContentFrame.setObjectName(u"futureContentFrame")
        self.futureContentFrame.setStyleSheet(u"QFrame{\n"
"    background-color: #f8f9fa;\n"
"    border: 2px dashed #ced4da;\n"
"    border-radius: 8px;\n"
"}")
        self.futureContentFrame.setFrameShape(QFrame.StyledPanel)
        self.futureContentFrame.setFrameShadow(QFrame.Raised)
        self.futureContentLayout = QVBoxLayout(self.futureContentFrame)
        self.futureContentLayout.setSpacing(0)
        self.futureContentLayout.setObjectName(u"futureContentLayout")
        self.futureContentLabel = QLabel(self.futureContentFrame)
        self.futureContentLabel.setObjectName(u"futureContentLabel")
        self.futureContentLabel.setAlignment(Qt.AlignCenter)

        self.futureContentLayout.addWidget(self.futureContentLabel)


        self.leftVerticalLayout.addWidget(self.futureContentFrame)


        self.mainHorizontalLayout.addWidget(self.leftFrame)

        self.mapFrame = QWidget(HomePage)
        self.mapFrame.setObjectName(u"mapFrame")
        self.mapFrame.setMinimumSize(QSize(650, 0))
        self.mapFrame.setStyleSheet(u"QWidget{\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dee2e6;\n"
"    border-radius: 8px;\n"
"}")
        self.horizontalLayout_2 = QHBoxLayout(self.mapFrame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, 8, 8, 8)

        self.mainHorizontalLayout.addWidget(self.mapFrame)


        self.retranslateUi(HomePage)

        QMetaObject.connectSlotsByName(HomePage)
    # setupUi

    def retranslateUi(self, HomePage):
        HomePage.setWindowTitle(QCoreApplication.translate("HomePage", u"Form", None))
        self.futureContentLabel.setText(QCoreApplication.translate("HomePage", u"Reserved Space\n"
"Future Content Area", None))
        self.futureContentLabel.setStyleSheet(QCoreApplication.translate("HomePage", u"QLabel { \n"
"    color: #6c757d; \n"
"    font-size: 14px; \n"
"    font-style: italic;\n"
"    border: none;\n"
"}", None))
    # retranslateUi

