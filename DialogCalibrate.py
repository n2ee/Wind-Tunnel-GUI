# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DialogCalibrate.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogCalibrate(object):
    def setupUi(self, DialogCalibrate):
        DialogCalibrate.setObjectName("DialogCalibrate")
        DialogCalibrate.resize(451, 240)
        self.btnAoAWingTare = QtWidgets.QPushButton(DialogCalibrate)
        self.btnAoAWingTare.setEnabled(True)
        self.btnAoAWingTare.setGeometry(QtCore.QRect(260, 80, 161, 32))
        self.btnAoAWingTare.setObjectName("btnAoAWingTare")
        self.lblRawAoA = QtWidgets.QLabel(DialogCalibrate)
        self.lblRawAoA.setGeometry(QtCore.QRect(280, 20, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.lblRawAoA.setFont(font)
        self.lblRawAoA.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblRawAoA.setObjectName("lblRawAoA")
        self.txtRawAoA = QtWidgets.QLabel(DialogCalibrate)
        self.txtRawAoA.setGeometry(QtCore.QRect(370, 20, 56, 20))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.txtRawAoA.setFont(font)
        self.txtRawAoA.setObjectName("txtRawAoA")
        self.lblRawAirspeed = QtWidgets.QLabel(DialogCalibrate)
        self.lblRawAirspeed.setGeometry(QtCore.QRect(10, 20, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.lblRawAirspeed.setFont(font)
        self.lblRawAirspeed.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblRawAirspeed.setObjectName("lblRawAirspeed")
        self.txtRawAirspeed = QtWidgets.QLabel(DialogCalibrate)
        self.txtRawAirspeed.setGeometry(QtCore.QRect(150, 20, 56, 20))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.txtRawAirspeed.setFont(font)
        self.txtRawAirspeed.setObjectName("txtRawAirspeed")
        self.btnAirspeedTare = QtWidgets.QPushButton(DialogCalibrate)
        self.btnAirspeedTare.setGeometry(QtCore.QRect(30, 50, 161, 32))
        self.btnAirspeedTare.setObjectName("btnAirspeedTare")
        self.btnDone = QtWidgets.QPushButton(DialogCalibrate)
        self.btnDone.setGeometry(QtCore.QRect(310, 190, 110, 32))
        self.btnDone.setDefault(True)
        self.btnDone.setObjectName("btnDone")
        self.btnAoAPlatformTare = QtWidgets.QPushButton(DialogCalibrate)
        self.btnAoAPlatformTare.setEnabled(True)
        self.btnAoAPlatformTare.setGeometry(QtCore.QRect(260, 50, 161, 32))
        self.btnAoAPlatformTare.setObjectName("btnAoAPlatformTare")
        self.inpAoAOffset = QtWidgets.QDoubleSpinBox(DialogCalibrate)
        self.inpAoAOffset.setGeometry(QtCore.QRect(350, 120, 62, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.inpAoAOffset.setFont(font)
        self.inpAoAOffset.setDecimals(1)
        self.inpAoAOffset.setMaximum(90.0)
        self.inpAoAOffset.setSingleStep(0.1)
        self.inpAoAOffset.setProperty("value", 0.0)
        self.inpAoAOffset.setObjectName("inpAoAOffset")
        self.lblAoAOffset = QtWidgets.QLabel(DialogCalibrate)
        self.lblAoAOffset.setGeometry(QtCore.QRect(260, 120, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lblAoAOffset.setFont(font)
        self.lblAoAOffset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblAoAOffset.setObjectName("lblAoAOffset")

        self.retranslateUi(DialogCalibrate)
        self.btnDone.clicked.connect(DialogCalibrate.accept)
        QtCore.QMetaObject.connectSlotsByName(DialogCalibrate)

    def retranslateUi(self, DialogCalibrate):
        _translate = QtCore.QCoreApplication.translate
        DialogCalibrate.setWindowTitle(_translate("DialogCalibrate", "Dialog"))
        self.btnAoAWingTare.setText(_translate("DialogCalibrate", "Set AoA Wing Tare"))
        self.lblRawAoA.setText(_translate("DialogCalibrate", "Raw AoA:"))
        self.txtRawAoA.setText(_translate("DialogCalibrate", "N/A"))
        self.lblRawAirspeed.setText(_translate("DialogCalibrate", "Raw Airspeed:"))
        self.txtRawAirspeed.setText(_translate("DialogCalibrate", "N/A"))
        self.btnAirspeedTare.setText(_translate("DialogCalibrate", "Set Airspeed Tare"))
        self.btnDone.setText(_translate("DialogCalibrate", "Done"))
        self.btnAoAPlatformTare.setText(_translate("DialogCalibrate", "Set AoA Platform Tare"))
        self.lblAoAOffset.setText(_translate("DialogCalibrate", "AoA Offset:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogCalibrate = QtWidgets.QDialog()
    ui = Ui_DialogCalibrate()
    ui.setupUi(DialogCalibrate)
    DialogCalibrate.show()
    sys.exit(app.exec_())

