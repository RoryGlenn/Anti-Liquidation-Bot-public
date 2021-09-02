from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")

        MainWindow.resize(760, 480)
        MainWindow.setMinimumSize(QSize(760, 480))
        MainWindow.setMaximumSize(QSize(760, 480))
        MainWindow.setStyleSheet(u"background-color: rgb(77, 77, 127);") 
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.circularProgressBar_Main = QFrame(self.centralwidget)
        self.circularProgressBar_Main.setObjectName(u"circularProgressBar_Main")
        self.circularProgressBar_Main.setGeometry(QRect(10, 80, 240, 240))
        self.circularProgressBar_Main.setStyleSheet(u"background-color: none;")
        self.circularProgressBar_Main.setFrameShape(QFrame.NoFrame)
        self.circularProgressBar_Main.setFrameShadow(QFrame.Raised)
        self.circularProgressCPU = QFrame(self.circularProgressBar_Main)
        self.circularProgressCPU.setObjectName(u"circularProgressCPU")
        self.circularProgressCPU.setGeometry(QRect(10, 10, 220, 220))
        self.circularProgressCPU.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.400 rgba(85, 170, 255, 255), stop:0.395 rgba(255, 255, 255, 0));\n"
"}")
        self.circularProgressCPU.setFrameShape(QFrame.StyledPanel)
        self.circularProgressCPU.setFrameShadow(QFrame.Raised)
        self.circularBg = QFrame(self.circularProgressBar_Main)
        self.circularBg.setObjectName(u"circularBg")
        self.circularBg.setGeometry(QRect(10, 10, 220, 220))
        self.circularBg.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: rgba(85, 85, 127, 100);\n"
"}")
        self.circularBg.setFrameShape(QFrame.StyledPanel)
        self.circularBg.setFrameShadow(QFrame.Raised)
        self.circularContainer = QFrame(self.circularProgressBar_Main)
        self.circularContainer.setObjectName(u"circularContainer")
        self.circularContainer.setGeometry(QRect(25, 25, 190, 190))
        self.circularContainer.setBaseSize(QSize(0, 0))
        self.circularContainer.setStyleSheet(u"QFrame{\n"
"	border-radius: 95px;	\n"
"	background-color: rgb(58, 58, 102);\n"
"}")
        self.circularContainer.setFrameShape(QFrame.StyledPanel)
        self.circularContainer.setFrameShadow(QFrame.Raised)
        self.layoutWidget = QWidget(self.circularContainer)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 40, 171, 125))
        self.infoLayout = QGridLayout(self.layoutWidget)
        self.infoLayout.setObjectName(u"infoLayout")
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.labelAplicationName = QLabel(self.layoutWidget)
        self.labelAplicationName.setObjectName(u"labelAplicationName")
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(10)
        self.labelAplicationName.setFont(font)
        self.labelAplicationName.setStyleSheet(u"color: #FFFFFF; background-color: none;")
        self.labelAplicationName.setAlignment(Qt.AlignCenter)

        self.infoLayout.addWidget(self.labelAplicationName, 0, 0, 1, 1)

        self.labelPercentageCPU = QLabel(self.layoutWidget)
        self.labelPercentageCPU.setObjectName(u"labelPercentageCPU")
        font1 = QFont()
        font1.setFamily(u"Roboto Thin")
        font1.setPointSize(30)
        self.labelPercentageCPU.setFont(font1)
        self.labelPercentageCPU.setStyleSheet(u"color: rgb(115, 185, 255); padding: 0px; background-color: none;")
        self.labelPercentageCPU.setAlignment(Qt.AlignCenter)
        self.labelPercentageCPU.setIndent(-1)

        self.infoLayout.addWidget(self.labelPercentageCPU, 1, 0, 1, 1)

        self.labelCredits = QLabel(self.layoutWidget)
        self.labelCredits.setObjectName(u"labelCredits")
        font2 = QFont()
        font2.setFamily(u"Segoe UI")
        font2.setPointSize(8)
        self.labelCredits.setFont(font2)
        self.labelCredits.setStyleSheet(u"color: rgb(148, 148, 216); background-color: none;")
        self.labelCredits.setAlignment(Qt.AlignCenter)

        self.infoLayout.addWidget(self.labelCredits, 2, 0, 1, 1)

        self.circularBg.raise_()
        self.circularProgressCPU.raise_()
        self.circularContainer.raise_()
        self.circularProgressBar_Main_2 = QFrame(self.centralwidget)
        self.circularProgressBar_Main_2.setObjectName(u"circularProgressBar_Main_2")
        self.circularProgressBar_Main_2.setGeometry(QRect(260, 80, 240, 240))
        self.circularProgressBar_Main_2.setStyleSheet(u"background-color: none;")
        self.circularProgressBar_Main_2.setFrameShape(QFrame.NoFrame)
        self.circularProgressBar_Main_2.setFrameShadow(QFrame.Raised)
        self.circularProgressGPU = QFrame(self.circularProgressBar_Main_2)
        self.circularProgressGPU.setObjectName(u"circularProgressGPU")
        self.circularProgressGPU.setGeometry(QRect(10, 10, 220, 220))
        self.circularProgressGPU.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.600 rgba(85, 255, 127, 255), stop:0.595 rgba(255, 255, 255, 0));\n"
"}")
        self.circularProgressGPU.setFrameShape(QFrame.StyledPanel)
        self.circularProgressGPU.setFrameShadow(QFrame.Raised)
        self.circularBg_2 = QFrame(self.circularProgressBar_Main_2)
        self.circularBg_2.setObjectName(u"circularBg_2")
        self.circularBg_2.setGeometry(QRect(10, 10, 220, 220))
        self.circularBg_2.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: rgba(85, 85, 127, 100);\n"
"}")
        self.circularBg_2.setFrameShape(QFrame.StyledPanel)
        self.circularBg_2.setFrameShadow(QFrame.Raised)
        self.circularContainer_2 = QFrame(self.circularProgressBar_Main_2)
        self.circularContainer_2.setObjectName(u"circularContainer_2")
        self.circularContainer_2.setGeometry(QRect(25, 25, 190, 190))
        self.circularContainer_2.setBaseSize(QSize(0, 0))
        self.circularContainer_2.setStyleSheet(u"QFrame{\n"
"	border-radius: 95px;	\n"
"	background-color: rgb(58, 58, 102);\n"
"}")
        self.circularContainer_2.setFrameShape(QFrame.StyledPanel)
        self.circularContainer_2.setFrameShadow(QFrame.Raised)
        self.layoutWidget_2 = QWidget(self.circularContainer_2)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(10, 40, 171, 127))
        self.infoLayout_2 = QGridLayout(self.layoutWidget_2)
        self.infoLayout_2.setObjectName(u"infoLayout_2")
        self.infoLayout_2.setContentsMargins(0, 0, 0, 0)
        self.labelAplicationName_2 = QLabel(self.layoutWidget_2)
        self.labelAplicationName_2.setObjectName(u"labelAplicationName_2")
        self.labelAplicationName_2.setFont(font)
        self.labelAplicationName_2.setStyleSheet(u"color: #FFFFFF; background-color: none;")
        self.labelAplicationName_2.setAlignment(Qt.AlignCenter)

        self.infoLayout_2.addWidget(self.labelAplicationName_2, 0, 0, 1, 1)

        self.labelPercentageGPU = QLabel(self.layoutWidget_2)
        self.labelPercentageGPU.setObjectName(u"labelPercentageGPU")
        self.labelPercentageGPU.setFont(font1)
        self.labelPercentageGPU.setStyleSheet(u"color: rgb(115, 255, 171); padding: 0px; background-color: none;")
        self.labelPercentageGPU.setAlignment(Qt.AlignCenter)
        self.labelPercentageGPU.setIndent(-1)

        self.infoLayout_2.addWidget(self.labelPercentageGPU, 1, 0, 1, 1)

        self.labelCredits_2 = QLabel(self.layoutWidget_2)
        self.labelCredits_2.setObjectName(u"labelCredits_2")
        self.labelCredits_2.setFont(font2)
        self.labelCredits_2.setStyleSheet(u"color: rgb(148, 148, 216); background-color: none;")
        self.labelCredits_2.setAlignment(Qt.AlignCenter)

        self.infoLayout_2.addWidget(self.labelCredits_2, 2, 0, 1, 1)

        self.circularBg_2.raise_()
        self.circularProgressGPU.raise_()
        self.circularContainer_2.raise_()
        self.circularProgressBar_Main_3 = QFrame(self.centralwidget)
        self.circularProgressBar_Main_3.setObjectName(u"circularProgressBar_Main_3")
        self.circularProgressBar_Main_3.setGeometry(QRect(510, 80, 240, 240))
        self.circularProgressBar_Main_3.setStyleSheet(u"background-color: none;")
        self.circularProgressBar_Main_3.setFrameShape(QFrame.NoFrame)
        self.circularProgressBar_Main_3.setFrameShadow(QFrame.Raised)
        self.circularProgressRAM = QFrame(self.circularProgressBar_Main_3)
        self.circularProgressRAM.setObjectName(u"circularProgressRAM")
        self.circularProgressRAM.setGeometry(QRect(10, 10, 220, 220))
        self.circularProgressRAM.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.750 rgba(255, 0, 127, 255), stop:0.745 rgba(255, 255, 255, 0));\n"
"}")
        self.circularProgressRAM.setFrameShape(QFrame.StyledPanel)
        self.circularProgressRAM.setFrameShadow(QFrame.Raised)
        self.circularBg_3 = QFrame(self.circularProgressBar_Main_3)
        self.circularBg_3.setObjectName(u"circularBg_3")
        self.circularBg_3.setGeometry(QRect(10, 10, 220, 220))
        self.circularBg_3.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: rgba(85, 85, 127, 100);\n"
"}")
        self.circularBg_3.setFrameShape(QFrame.StyledPanel)
        self.circularBg_3.setFrameShadow(QFrame.Raised)
        self.circularContainer_3 = QFrame(self.circularProgressBar_Main_3)
        self.circularContainer_3.setObjectName(u"circularContainer_3")
        self.circularContainer_3.setGeometry(QRect(25, 25, 190, 190))
        self.circularContainer_3.setBaseSize(QSize(0, 0))
        self.circularContainer_3.setStyleSheet(u"QFrame{\n"
"	border-radius: 95px;	\n"
"	background-color: rgb(58, 58, 102);\n"
"}")
        self.circularContainer_3.setFrameShape(QFrame.StyledPanel)
        self.circularContainer_3.setFrameShadow(QFrame.Raised)
        self.layoutWidget_3 = QWidget(self.circularContainer_3)
        self.layoutWidget_3.setObjectName(u"layoutWidget_3")
        self.layoutWidget_3.setGeometry(QRect(10, 40, 171, 125))
        self.infoLayout_3 = QGridLayout(self.layoutWidget_3)
        self.infoLayout_3.setObjectName(u"infoLayout_3")
        self.infoLayout_3.setContentsMargins(0, 0, 0, 0)
        self.labelAplicationName_3 = QLabel(self.layoutWidget_3)
        self.labelAplicationName_3.setObjectName(u"labelAplicationName_3")
        self.labelAplicationName_3.setFont(font)
        self.labelAplicationName_3.setStyleSheet(u"color: #FFFFFF; background-color: none;")
        self.labelAplicationName_3.setAlignment(Qt.AlignCenter)

        self.infoLayout_3.addWidget(self.labelAplicationName_3, 0, 0, 1, 1)

        self.labelPercentageRAM = QLabel(self.layoutWidget_3)
        self.labelPercentageRAM.setObjectName(u"labelPercentageRAM")
        self.labelPercentageRAM.setFont(font1)
        self.labelPercentageRAM.setStyleSheet(u"color: rgb(255, 44, 174); padding: 0px; background-color: none;")
        self.labelPercentageRAM.setAlignment(Qt.AlignCenter)
        self.labelPercentageRAM.setIndent(-1)

        self.infoLayout_3.addWidget(self.labelPercentageRAM, 1, 0, 1, 1)

        self.labelCredits_3 = QLabel(self.layoutWidget_3)
        self.labelCredits_3.setObjectName(u"labelCredits_3")
        self.labelCredits_3.setFont(font2)
        self.labelCredits_3.setStyleSheet(u"color: rgb(148, 148, 216); background-color: none;")
        self.labelCredits_3.setAlignment(Qt.AlignCenter)

        self.infoLayout_3.addWidget(self.labelCredits_3, 2, 0, 1, 1)

        self.circularBg_3.raise_()
        self.circularProgressRAM.raise_()
        self.circularContainer_3.raise_()
        self.label_title = QLabel(self.centralwidget)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setGeometry(QRect(19, 4, 641, 50))
        font3 = QFont()
        font3.setFamily(u"Roboto")
        font3.setPointSize(14)
        self.label_title.setFont(font3)
        self.label_title.setStyleSheet(u"color: rgb(115, 185, 255); background-color: none;")
        
        self.btn_close = QPushButton(self.centralwidget)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setGeometry(QRect(724, 20, 17, 17))
        self.btn_close.setMinimumSize(QSize(16, 16))
        self.btn_close.setMaximumSize(QSize(17, 17))
        self.btn_close.setStyleSheet(u"QPushButton {\n"
"	border: none;\n"
"	border-radius: 8px;		\n"
"	background-color: rgb(255, 0, 0);\n"
"}\n"
"QPushButton:hover {		\n"
"	background-color: rgba(255, 0, 0, 150);\n"
"}")


        self.label_13 = QLabel(self.centralwidget)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(90, 410, 582, 40))
        self.label_13.setMaximumSize(QSize(600, 40))
        font4 = QFont()
        font4.setFamily(u"Roboto Light")
        font4.setPointSize(20)
        self.label_13.setFont(font4)
        self.label_13.setStyleSheet(u"color: rgb(220, 220, 220);\n"
        "background-color: rgb(98, 98, 162);\n"
        "border-radius: 20px;")
        self.label_13.setAlignment(Qt.AlignCenter)

        self.btn_maximize = QPushButton(self.centralwidget)
        self.btn_maximize.setObjectName(u"btn_maximize")
        self.btn_maximize.setGeometry(QRect(670, 20, 17, 17))
        self.btn_maximize.setMinimumSize(QSize(16, 16))
        self.btn_maximize.setMaximumSize(QSize(17, 17))
        self.btn_maximize.setStyleSheet(u"QPushButton {\n"
"	border: none;\n"
"	border-radius: 8px;	\n"
"	background-color: rgb(85, 255, 127);\n"
"}\n"
"QPushButton:hover {	\n"
"	background-color: rgba(85, 255, 127, 150);\n"
"}")

        self.btn_minimize = QPushButton(self.centralwidget)
        self.btn_minimize.setObjectName(u"btn_minimize")
        self.btn_minimize.setGeometry(QRect(697, 20, 17, 17))
        self.btn_minimize.setMinimumSize(QSize(16, 16))
        self.btn_minimize.setMaximumSize(QSize(17, 17))
        self.btn_minimize.setStyleSheet(u"QPushButton {\n"
"	border: none;\n"
"	border-radius: 8px;		\n"
"	background-color: rgb(255, 170, 0);\n"
"}\n"
"QPushButton:hover {	\n"
"	background-color: rgba(255, 170, 0, 150);\n"
"}")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)



    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow",          u"Anti-Liquidation Bot", None))
        
        self.labelAplicationName.setText(QCoreApplication.translate("MainWindow",   u"<strong>Futures Wallet Value</strong>", None))

        self.labelPercentageCPU.setText(QCoreApplication.translate("MainWindow",    u"<p align=\"center\"><span style=\" font-size:50pt;\">0</span><span style=\" font-size:40pt; vertical-align:super;\"></span></p>", None))
        self.labelCredits.setText(QCoreApplication.translate("MainWindow",          u"<html><head/><body><p>Unrealized PnL: <span style=\" color:#ffffff;\">0</span></p></body></html>", None))
        
        self.labelAplicationName_2.setText(QCoreApplication.translate("MainWindow", u"<strong>Margin Ratio</strong>", None))
        self.labelPercentageGPU.setText(QCoreApplication.translate("MainWindow",    u"<p align=\"center\"><span style=\" font-size:50pt;\">0</span><span style=\" font-size:40pt; vertical-align:super;\">%</span></p>", None))
        self.labelCredits_2.setText(QCoreApplication.translate("MainWindow",        u"<html><head/><body><p>short: <span style=\"color:#ffffff;\">0</span>long: <span style=\"color:#ffffff;\">0</span> </p></body></html>", None))
        
        self.labelAplicationName_3.setText(QCoreApplication.translate("MainWindow", u"<strong>USDT Available</strong>", None))
        self.labelPercentageRAM.setText(QCoreApplication.translate("MainWindow",    u"<p align=\"center\"><span style=\" font-size:50pt;\">0</span><span style=\" font-size:40pt; vertical-align:super;\"></span></p>", None))
        self.labelCredits_3.setText(QCoreApplication.translate("MainWindow",        u"<html><head/><body><p>open positions: <span style=\" color:#ffffff;\">0</span></p></body></html>", None))
        self.label_title.setText(QCoreApplication.translate("MainWindow",           u"Anti-Liquidation Bot", None))

        self.btn_close.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"00:00:00", None))
        self.btn_maximize.setToolTip(QCoreApplication.translate("MainWindow", u"Maximize", None))
        self.btn_minimize.setToolTip(QCoreApplication.translate("MainWindow", u"Minimize", None))
        
        # self.btn_close.setText("x")
        # self.btn_maximize.setText("O")
        # self.btn_minimize.setText("-")
        