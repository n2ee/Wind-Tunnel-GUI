#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 17:13:08 2017

@author: markm
"""

import re
import sys
import time
import unicodedata

from pathlib import Path

from queue import Queue
from PyQt5 import  QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, QTime
from PyQt5.QtWidgets import QTableWidgetItem

import Tunnel_Model
from DialogCalibrate import Ui_DialogCalibrate
from TunnelConfig import TunnelConfig
from TunnelPersist import TunnelPersist
from SensorSimulator import SensorSimulator
from SensorReader import SensorReader
from SampleCollector import SampleCollector
from ProcessedSample import ProcessedSample
from LiveGraph import LiveGraph

class TunnelGui(QtWidgets.QMainWindow, Tunnel_Model.Ui_MainWindow):

    sensorRdr = None
    sampleCollector = None
    
    enableGraphs = False
    liftGraph = None
    dragGraph = None
    pitchMomentGraph = None
    airspeedGraph = None
    config = TunnelConfig()
    
    def __init__(self, qApp):
        super().__init__()
        self.qApp = qApp
        self.setupUi(self)

        # setup the calibrattion dialog
        self.dialogCalibrate = QtWidgets.QDialog()
        self.dialogCalibrateUi = Ui_DialogCalibrate()
        self.dialogCalibrateUi.setupUi(self.dialogCalibrate)

        # Update displayed sample rate
        sampleRate = self.config.getItem("General", "samplerate")

        self.outSampleRate.display(sampleRate)

        # Connect buttons to their corresponding functions
        self.btnCalibrate.clicked.connect(self.showCalibrateDialog)
        self.btnLoadTare.clicked.connect(self.loadTare)
        self.btnSaveResults.clicked.connect(self.saveResults)

        self.dialogCalibrateUi.btnDone.clicked.connect(self.calibrationDone)
        self.dialogCalibrateUi.btnAirspeedTare.clicked.connect(self.airspeedTare)
        self.dialogCalibrateUi.btnAoAWingTare.clicked.connect(self.aoaWingTare)
        self.dialogCalibrateUi.btnAoAPlatformTare.clicked.connect(self.aoaPlatformTare)

        # Initialize the platform offset from the persist file. Can't wait
        # until SampleCollector is alive, so we read it directly from the
        # file. Woe be unto me if I change the name of the persist value...
        aoaPlatformOffset = TunnelPersist().getItem("AoA", "PlatformOffset")
        if aoaPlatformOffset == None:
            aoaPlatformOffset = 0.0
        else:
            aoaPlatformOffset = float(aoaPlatformOffset)

        self.dialogCalibrateUi.inpAoAOffset.setValue(aoaPlatformOffset)
        self.setAoAOffset(aoaPlatformOffset)
        
        # Set the Saving... text to nothing for now. When the Save button
        # is clicked, we'll light it up for a moment.
        self.lblSaving.setText("")

        # Show the directory path
        destDirname = self.config.getItem("General", "DataDestinationDir")
        self.lblDirPath.setText(destDirname)
 
    def showCalibrateDialog(self):
        self.dialogCalibrate.show()

    def calibrationDone(self):
        offset = self.dialogCalibrateUi.inpAoAOffset.value()
        self.sampleCollector.setAoAPlatformOffset(offset)
        self.setAoAOffset(offset)
        
    def aoaWingTare(self):
        self.sampleCollector.setAoAWingTare()

    def aoaPlatformTare(self):
        self.sampleCollector.setAoAPlatformTare()

    def airspeedTare(self):
        self.sampleCollector.setAirspeedTare()

    def loadTare(self):
        self.sampleCollector.setLoadTare()

    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens. Borrowed from
        https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
        """
        value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
        # Chomp the leading 'b\'
        value = value[2:]
        value = str(re.sub("[^\w.\s-]", "", value).strip().lower())
        value = str(re.sub("[-\s]+", "-", value))
        return value

    def saveResults(self):
        fname = self.slugify(str(self.inpRunName.text()))
        if (fname == ""):
            fname = self.config.getItem("General", "DefaultFileName")

        # Append '.csh' if not already there
        if not fname.endswith(".csv"):
            fname += ".csv"
            
        fname = Path(fname)
        destDirname = self.config.getItem("General", "DataDestinationDir")

        if (destDirname is None):
            destDirname = Path.cwd()
        else:
            Path(destDirname).mkdir(parents = True, exist_ok = True)

        fname = destDirname / fname
        print ("Save Results clicked: %s" % fname)
        
        self.lblSaving.setText("Saving...")
        
        self.sampleCollector.doSave(fname, str(self.inpRunName.text()),
                                    str(self.inpConfiguration.text()),
                                    str(self.inpComments.text()))

        dieTime = QTime.currentTime().addSecs(1)
        while (QTime.currentTime() < dieTime):
            self.qApp.processEvents()

        self.lblSaving.setText("")
        self.lblSaving.repaint()
        self.qApp.processEvents()

    def startReadingSensors(self):
        sampleRate = self.outSampleRate.value()
        print ("Start sampling at " + str(sampleRate) + " samples/sec")

    def setAoa(self, aoa):
        aoa = float('%.1f' % aoa)
        self.outAoaDeg.display(str(aoa))

    def setAoAOffset(self, offset):
        offset = float('%.1f' % offset)
        self.outAoaOffsetDeg.display(str(offset))

    def setAirspeed(self, speed):
        speed = float('%.1f' % speed)
        self.outSpeedMPH.display(str(speed))
        speed = speed * 5280.0 / 3600.0
        speed = float('%.1f' % speed)
        self.outSpeedFps.display(str(speed))

    def setAnenometer(self, speed):
        speed = float('%.1f' % speed)
        self.outAnemometerFps.display(str(speed))
        speed = speed * 3600.0 / 5280.0
        speed = float('%.1f' % speed)
        self.outAnemometerMPH.display(str(speed))

    def setLift(self, lift, stddev):
        lift = float('%.2f' % lift)
        stddev = float('%.2f' % stddev)
        itemKg = QTableWidgetItem()
        itemKg.setData(Qt.DisplayRole, lift)
        self.tblLiftDragMoment.setItem(0, 0, itemKg)
        itemLb = QTableWidgetItem()
        itemLb.setData(Qt.DisplayRole, float('%.2f' % (lift * 2.2046)))
        self.tblLiftDragMoment.setItem(0, 1, itemLb)
        fItemKg = QTableWidgetItem()
        fItemKg.setData(Qt.DisplayRole, stddev)
        self.tblLiftDragMoment.setItem(0, 2, fItemKg)

    def setDrag(self, drag, stddev):
        drag = float('%.2f' % drag)
        stddev = float('%.2f' % stddev)
        itemKg = QTableWidgetItem()
        itemKg.setData(Qt.DisplayRole, drag)
        self.tblLiftDragMoment.setItem(1, 0, itemKg)
        itemLb = QTableWidgetItem()
        itemLb.setData(Qt.DisplayRole, float('%.2f' % (drag * 2.2046)))
        self.tblLiftDragMoment.setItem(1, 1, itemLb)
        fItemKg = QTableWidgetItem()
        fItemKg.setData(Qt.DisplayRole, stddev)
        self.tblLiftDragMoment.setItem(1, 2, fItemKg)

    def setMoment(self, moment, stddev):
        moment = float('%.2f' % moment)
        stddev = float('%.2f' % stddev)
        itemKgM = QTableWidgetItem()
        itemKgM.setData(Qt.DisplayRole, moment)
        self.tblLiftDragMoment.setItem(2, 0, itemKgM)
        itemLbFt = QTableWidgetItem()
        itemLbFt.setData(Qt.DisplayRole, float('%.2f' % (moment * 8.8507)))
        self.tblLiftDragMoment.setItem(2, 1, itemLbFt)
        fItemKgM = QTableWidgetItem()
        fItemKgM.setData(Qt.DisplayRole, stddev)
        self.tblLiftDragMoment.setItem(2, 2, fItemKgM)

    def setPower(self, power):
        power = float('%.1f' % power)
        self.outPower.display(str(power))

    def setRawAoA(self, aoa):
        self.dialogCalibrateUi.txtRawAoA.setText(str(aoa))
        
    def setRawAirspeed(self, airspeed):
        self.dialogCalibrateUi.txtRawAirspeed.setText(str(airspeed))
       
    def saveRunNameAndConfiguration(self):
        if self.savedRunNameText != self.inpRunName.text():
            self.savedRunNameText = self.inpRunName.text()
            self.sampleCollector.saveRunName(self.savedRunNameText)

        if self.savedConfigurationText != self.inpConfiguration.text():
            self.savedConfigurationText = self.inpConfiguration.text()
            self.sampleCollector.saveConfiguration(self.savedConfigurationText)
            
    @pyqtSlot(ProcessedSample)
    def refreshWindow(self, currentData):
        self.setRawAoA(currentData.rawAoA)
        self.setRawAirspeed(currentData.rawAirspeed)
        
        self.setPower(currentData.volts * currentData.amps)
        self.setAoa(currentData.wingAoA)
        self.setAirspeed(currentData.airspeed)
        self.setAnenometer(currentData.hotwire)

        self.tblLiftDragMoment.setUpdatesEnabled(False)
        self.setLift(currentData.totalLift, currentData.totalLiftStdDev)
        self.setDrag(currentData.drag, currentData.dragStdDev)
        self.setMoment(currentData.pitchMoment,
                       currentData.pitchMomentStdDev)
        self.tblLiftDragMoment.setUpdatesEnabled(True)

        self.updateGraphs(currentData.totalLift, currentData.drag,
                          currentData.pitchMoment, currentData.airspeed)

        self.saveRunNameAndConfiguration()

    def startSensorReader(self, tunnelWindow, tunnelDataQ):
        useSimulatedData = self.config.getItem("General",
                                               "UseSimulatedData")
        if (useSimulatedData is None):
            self.sensorRdr = SensorReader(tunnelWindow, tunnelDataQ)

        if (useSimulatedData.lower() == "true"):
            print ("Starting data simulator")
            self.sensorRdr = SensorSimulator(tunnelWindow, tunnelDataQ)
        else:
            self.sensorRdr = SensorReader(tunnelWindow, tunnelDataQ)

        self.sensorRdr.daemon = True
        self.sensorRdr.start()

    def stopSensorReader(self):
        self.sensorRdr.terminate()

    def startSampleCollector(self, tunnelDataQ):
        self.sampleCollector = SampleCollector(tunnelDataQ)
        self.sampleCollector.updateWindow.connect(self.refreshWindow)
        self.sampleCollector.daemon = True
        self.sampleCollector.start()
        
        # Once SampleCollector is up and running, we can ask it for the 
        # previously saved run name and configuraiton
        self.savedRunNameText = self.sampleCollector.getRunName()
        self.savedConfigurationText = self.sampleCollector.getConfiguration()
        self.inpRunName.setText(self.savedRunNameText)
        self.inpConfiguration.setText(self.savedConfigurationText)

    def stopSampleCollector(self):
        self.sampleCollector.terminate()

    def startGraphs(self):

        enableGraphs = self.config.getItem("General", "EnableGraphs")

        if (enableGraphs is None):
            self.enableGraphs = False
            return

        if (enableGraphs.lower() != "true"):
            self.enableGraphs = False
            return

        self.enableGraphs = True
        self.liftGraph = LiveGraph(QtCore.QRect(50, 150, 500, 200),
                                   "Lift", "kg", True)
        self.liftGraph.show()

        self.dragGraph = LiveGraph(QtCore.QRect(50, 375, 500, 200),
                                   "Drag", "Kg", True)
        self.dragGraph.show()

        self.pitchMomentGraph = LiveGraph(QtCore.QRect(50, 600, 500, 200),
                                          "Moment", "Kg-M", True)
        self.pitchMomentGraph.show()

        self.airspeedGraph = LiveGraph(QtCore.QRect(50, 825, 500, 200),
                                       "Airspeed", "Kt", True)
        self.airspeedGraph.show()

    def updateGraphs(self, lift, drag, pitchMoment, airspeed):
        if (self.enableGraphs):
            self.liftGraph.addDataToGraph(lift)
            self.dragGraph.addDataToGraph(drag)
            self.pitchMomentGraph.addDataToGraph(pitchMoment)
            self.airspeedGraph.addDataToGraph(airspeed)

def main():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    else:
        print('QApplication instance already exists: %s' % str(app))

    tg = TunnelGui(app)
    tg.startGraphs()

    tg.show()
    tdQ = Queue(16384)  # Just a guess - probably shouldn't make it too big.
    tg.startSensorReader(tg, tdQ)
    tg.startSampleCollector(tdQ)

    app.exec_()

    tg.stopSensorReader()
    tg.stopSampleCollector()

if __name__ == "__main__":
    main()
