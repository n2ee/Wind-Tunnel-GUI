#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 21:48:24 2017

@author: markm

Listens on stdin|designated pipe and collects samples arriving there. Feeds
samples to the display UI and/or writes to a file.


"""
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QThread

from TunnelConfig import TunnelConfig
from ProcessedSample import ProcessedSample
from Filter import KalmanFilter, RollingAverageFilter

class SampleCollector(QThread):
    dataQ = None
    tunnelWindow = None
    saveSamples = False
    samplesToSave = 1
    f = None
    leftLoadTare = 0.0
    centerLoadTare = 0.0
    rightLoadTare = 0.0
    updateLoadTare = False
    aoaTare = 0.0
    updateAoATare = False

    def __init__(self, tw, dQ):
        QThread.__init__(self)
        self.dataQ = dQ
        self.tunnelWindow = tw
        config = TunnelConfig()
        self.liftLeftScaling = float(config.getItem("StrainGauges",
                                                    "liftleftscaling"))
        self.liftCenterScaling = float(config.getItem("StrainGauges",
                                                      "liftcenterscaling"))
        self.liftRightScaling = float(config.getItem("StrainGauges",
                                                     "liftrightscaling"))
        self.dragScaling = float(config.getItem("StrainGauges", "dragscaling"))

        self.aoaSlope = float(config.getItem("AoA", "slope"))
        self.aoaZero = float(config.getItem("AoA", "zero"))
        self.airspeedLowerLimit = float(config.getItem("Airspeed",
                                                       "lowerlimit"))

    def __del__(self):
        self.wait()

    def doSave(self, destFile = os.devnull, config = ""):
        try:
            self.config = ', "' + config + '"\n'

            self.f = open(destFile, "a")
            self.saveSamples = True
        except IOError:
            print ("Could not open: ", destFile)
            self.saveSamples = False

    def setLoadTare(self):
        self.updateLoadTare = True

    def setAoATare(self):
        self.updateAoATare = True

    def run(self):
        # This method runs as its own thread, catching SensorSamples,
        # updating the GUI, processing data, and tossing it into a file
        # when asked to.
        
        # KalmanFilters still need tuning.
        # liftLeftFilter = KalmanFilter(150e-06, 1.5e-03)
        # liftCenterFilter = KalmanFilter(150e-06, 1.5e-03)
        # liftRightFilter = KalmanFilter(150e-06, 1.5e-03)
        # dragFilter = KalmanFilter(150e-06, 1.5e-03)
        liftLeftFilter = RollingAverageFilter()
        liftCenterFilter = RollingAverageFilter()
        liftRightFilter = RollingAverageFilter()
        dragFilter = RollingAverageFilter()


        while (True):
            latestSample = self.dataQ.get(True)

            if (self.updateLoadTare):
                self.updateLoadTare = False
                self.leftLoadTare = latestSample.liftLeft
                self.centerLoadTare = latestSample.liftCenter
                self.rightLoadTare = latestSample.liftRight

            if (self.updateAoATare):
                self.updateAoATare = False
                self.aoaTare = latestSample.aoa

            # Get the AoA
            aoa = latestSample.aoa - self.aoaTare

            # Get the latest lift & drag, adjust for tare
            drag = latestSample.drag
            liftLeft = latestSample.liftLeft - self.leftLoadTare
            liftCenter = latestSample.liftCenter - self.centerLoadTare
            liftRight = latestSample.liftRight - self.rightLoadTare

            # Generate filtered values
            fDrag = dragFilter.get_filtered_value(drag) * self.dragScaling
            fLiftLeft = liftLeftFilter.get_filtered_value(liftLeft) * \
                                                    self.liftLeftScaling
            fLiftCenter = liftCenterFilter.get_filtered_value(liftCenter) * \
                                                    self.liftCenterScaling
            fLiftRight = liftRightFilter.get_filtered_value(liftRight) * \
                                                        self.liftRightScaling
            airspeed = latestSample.airspeed
            if (airspeed < self.airspeedLowerLimit):
                # Think of this as a high-pass brickwall filter
                airspeed = 0.0

            # Scale to taste
            aoa = aoa * self.aoaSlope + self.aoaZero

            drag = drag * self.dragScaling
            liftLeft = liftLeft * self.liftLeftScaling
            liftCenter = liftCenter * self.liftCenterScaling
            liftRight = liftRight * self.liftRightScaling

            # Crunch the total lift and pitching moments
            totalLift = liftLeft + liftCenter + liftRight
            pitchMoment = (totalLift * 5.63) + \
                            (liftLeft + liftRight) * 1.44
            fTotalLift = fLiftLeft + fLiftCenter + fLiftRight
            fPitchMoment = (fTotalLift * 5.63) + \
                            (fLiftLeft + fLiftRight) * 1.44

            self.tunnelWindow.setAoa(aoa)
            self.tunnelWindow.tblLiftDragMoment.setUpdatesEnabled(False)
            self.tunnelWindow.setAirspeed(airspeed)
            self.tunnelWindow.setLift(totalLift, fTotalLift)
            self.tunnelWindow.setDrag(drag, fDrag)
            self.tunnelWindow.setMoment(pitchMoment, fPitchMoment)
            self.tunnelWindow.tblLiftDragMoment.setUpdatesEnabled(True)

            self.tunnelWindow.updateGraphs(fTotalLift, fDrag, fPitchMoment,
                                           airspeed)

            if (self.saveSamples):
                self.saveSamples = False
                processedSample = ProcessedSample(latestSample.volts,
                                                  latestSample.amps,
                                                  latestSample.aoa,
                                                  latestSample.rpm,
                                                  latestSample.airspeed,
                                                  latestSample.hotwire,
                                                  fTotalLift,
                                                  fDrag,
                                                  fPitchMoment,
                                                  latestSample.timestamp)
                # f is opened in doSave(), and remains open until
                # the requested samples are written here.
                self.f.write(str(processedSample) + self.config)
                self.f.close()






