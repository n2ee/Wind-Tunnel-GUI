#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 17:13:08 2017

@author: markm
"""

import sys

from Queue import Queue
from PyQt5 import  QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

import Tunnel_Model
from TunnelConfig import TunnelConfig
from SensorSimulator import SensorSimulator
from SensorReader import SensorReader
from SampleCollector import SampleCollector
from LiveGraph import LiveGraph

class TunnelGui(QtWidgets.QMainWindow, Tunnel_Model.Ui_MainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.config = TunnelConfig()

        # Update displayed sample rate
        self.outSampleRate.display(self.dlSampleRate.value())

        # Connect buttons to their corresponding functions
        self.btnLoadTare.clicked.connect(self.loadTare)
        self.btnSaveResults.clicked.connect(self.saveResults)
        self.btnSetAOATare.clicked.connect(self.setAOATare)

        self.sensorRdr = None
        self.sampleCollector = None
        self.savingResults = False
        self.enableGraphs = False
        self.liftGraph = None
        self.dragGraph = None
        self.pitchMomentGraph = None
        self.airspeedGraph = None


    def loadTare(self):
        self.sampleCollector.setLoadTare()

    def saveResults(self):
        fname = str(self.inpRunName.text())
        # FIXME - Here would be a good place to sanity-check the file name
        print "Save Results clicked: %s" % fname
        self.sampleCollector.doSave(fname, str(self.inpConfiguration.text()))

    def setAOATare(self):
        self.sampleCollector.setAoATare()

    def startReadingSensors(self):
        sampleRate = self.outSampleRate.value()
        print "Start sampling at " + str(sampleRate) + " samples/sec"

    def setAoa(self, aoa):
        self.outAoaDeg.display(str(aoa))

    def setAirspeed(self, speed):
        self.outSpeedMPH.display(str(speed))
        self.outSpeedFps.display(str(speed * 5280 / (60 * 60)))

    def setLift(self, lift, fLift):
        itemKg = QTableWidgetItem()
        itemKg.setData(Qt.DisplayRole, lift)
        self.tblLiftDragMoment.setItem(0, 0, itemKg)
        itemLb = QTableWidgetItem()
        itemLb.setData(Qt.DisplayRole, (lift * 2.2046))
        self.tblLiftDragMoment.setItem(0, 1, itemLb)
        fItemKg = QTableWidgetItem()
        fItemKg.setData(Qt.DisplayRole, fLift)
        self.tblLiftDragMoment.setItem(0, 2, fItemKg)

    def setDrag(self, drag, fDrag):
        itemKg = QTableWidgetItem()
        itemKg.setData(Qt.DisplayRole, drag)
        self.tblLiftDragMoment.setItem(1, 0, itemKg)
        itemLb = QTableWidgetItem()
        itemLb.setData(Qt.DisplayRole, (drag * 2.2046))
        self.tblLiftDragMoment.setItem(1, 1, itemLb)
        fItemKg = QTableWidgetItem()
        fItemKg.setData(Qt.DisplayRole, fDrag)
        self.tblLiftDragMoment.setItem(1, 2, fItemKg)

    def setMoment(self, moment, fMoment):
        itemKgM = QTableWidgetItem()
        itemKgM.setData(Qt.DisplayRole, moment)
        self.tblLiftDragMoment.setItem(2, 0, itemKgM)
        itemLbFt = QTableWidgetItem()
        itemLbFt.setData(Qt.DisplayRole, (moment * 8.8507))
        self.tblLiftDragMoment.setItem(2, 1, itemLbFt)
        fItemKgM = QTableWidgetItem()
        fItemKgM.setData(Qt.DisplayRole, fMoment)
        self.tblLiftDragMoment.setItem(2, 2, fItemKgM)

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

        self.sensorRdr.start()

    def startSampleCollector(self, tunnelWindow, tunnelDataQ):
        self.sampleCollector = SampleCollector(tunnelWindow, tunnelDataQ)
        self.sampleCollector.start()

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

    tg = TunnelGui()
    tg.startGraphs()

    tg.show()
    tdQ = Queue(16384)  # Just a guess - probably shouldn't make it too big.
    tg.startSensorReader(tg, tdQ)
    tg.startSampleCollector(tg, tdQ)

    app.exec_()


if __name__ == "__main__":
    main()
