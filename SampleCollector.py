#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 21:48:24 2017

@author: markm

Listens on the dataQ and collects samples arriving there. Feeds
samples to the display UI and/or writes to a file.


"""
import os
from pathlib import Path
from math import radians, cos, sin, sqrt

from PyQt5.QtCore import QThread, pyqtSignal

from TunnelConfig import TunnelConfig
from TunnelPersist import TunnelPersist
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
    dragTare = 0.0
    updateLoadTare = False
    aoaTare = 0.0 # We call this 'tare' to distinguish from the y-intercept of the raw value
    updateAoAWingError = False
    airspeedZero = 0.0
    updateAirspeedZero = False
    dumpInterval = 0
    persist = TunnelPersist()
    runConfigComment = ""

    updateWindow = pyqtSignal('PyQt_PyObject')

    def __init__(self, dQ):
        QThread.__init__(self)
        self.dataQ = dQ
        config = TunnelConfig()
        self.liftLeftScaling = float(config.getItem("StrainGauges",
                                                    "liftleftscaling"))
        self.liftCenterScaling = float(config.getItem("StrainGauges",
                                                      "liftcenterscaling"))
        self.liftRightScaling = float(config.getItem("StrainGauges",
                                                     "liftrightscaling"))
        self.dragScaling = float(config.getItem("StrainGauges", "dragscaling"))

        self.aoaSlope = float(config.getItem("AoA", "slope"))
        self.aoaPlatformTare = int(config.getItem("AoA", "platformtare"))


        self.voltsSlope = float(config.getItem("Volts", "slope"))
        self.voltsZero = float(config.getItem("Volts", "zero"))

        self.ampsSlope = float(config.getItem("Amps", "slope"))
        self.ampsZero = float(config.getItem("Amps", "zero"))
        self.shuntOhms = float(config.getItem("Amps", "shunt"))

        self.airspeedSlope = float(config.getItem("Airspeed",  "slope"))
        self.airspeedLowerLimit = float(config.getItem("Airspeed",
                                                       "lowerlimit"))

        self.hotwireLowerLimit = float(config.getItem("Hotwire",
                                                       "lowerlimit"))

        self.hotwireZero = float(config.getItem("Hotwire", "zero"))
        self.hotwireSlope = float(config.getItem("Hotwire", "slope"))

        aoaWingError = self.persist.getItem("AoA", "wingerror")
        if aoaWingError == None:
            self.aoaWingError = 0
        else:
            self.aoaWingError = int(aoaWingError)

        airspeedZero = self.persist.getItem("Airspeed", "Zero")
        if airspeedZero == None:
            self.airspeedZero = 0.0
        else:
            self.airspeedZero = float(airspeedZero)


    def __del__(self):
        self.wait()

    def doSave(self, destFile = Path(os.devnull), runName = "", config = "",
               comments = ""):
        try:
            self.runConfigComment = ', "' + \
                                    runName + '", "' + \
                                    config + '", "' + \
                                    comments + '"\n'

            if not destFile.is_file():
                self.f = open(destFile, "w")
                self.f.write(str(ProcessedSample.header()))
                self.f.write(", run name, configuration, comments\n")
                self.f.close()

            self.f = open(destFile, "a")
            self.saveSamples = True
        except IOError:
            print ("Could not open: ", destFile)
            self.saveSamples = False

    def setLoadTare(self):
        self.updateLoadTare = True

    def setAoAZero(self):
        self.updateAoAWingError = True

    def setAirspeedZero(self):
        self.updateAirspeedZero = True

    def dumpData(self, processedSample):
        if self.dumpInterval == 10:
            self.dumpInterval = 0
            print("V=%f, A=%f, as=%f, hw=%f, platAoA=%f, aoa=%f, rawDrag=%f, drag=%f, LL=%f, LC=%f, LR=%f, TL=%f" \
                  % (processedSample.volts, processedSample.amps,
                     processedSample.airspeed, processedSample.hotwire,
                     self.platformAoA, processedSample.aoa, self.scaleDrag, processedSample.drag,
                     processedSample.liftLeft, processedSample.liftCenter,
                     processedSample.liftRight, processedSample.totalLift))
        else:
            self.dumpInterval += 1

    def run(self):
        # This method runs as its own thread, catching SensorSamples,
        # updating the GUI, processing data, and tossing it into a file
        # when asked to.

        liftLeftFilter = RollingAverageFilter(10)
        liftCenterFilter = RollingAverageFilter(10)
        liftRightFilter = RollingAverageFilter(10)
        totalLiftFilter = RollingAverageFilter(10)
        pitchMomentFilter = RollingAverageFilter(10)
        dragFilter = RollingAverageFilter(10)
        airspeedFilter = RollingAverageFilter(10)
        hotwireFilter = RollingAverageFilter(10)
        wingAoA = 0.0
        self.platformAoA = 0.0
        drag = 0.0

        while (True):
            latestSample = self.dataQ.get(True)

            if (self.updateLoadTare):
                self.updateLoadTare = False
                self.leftLoadTare = latestSample.liftLeft
                self.centerLoadTare = latestSample.liftCenter
                self.rightLoadTare = latestSample.liftRight
                self.dragTare = latestSample.drag

            if (self.updateAoAWingError):
                self.updateAoAWingError = False
                self.aoaWingError = latestSample.aoa - self.aoaPlatformTare
                self.persist.setItem("AoA", "WingError", str(self.aoaWingError))

            if (self.updateAirspeedZero):
                self.updateAirspeedZero = False
                self.airspeedZero = latestSample.airspeed
                self.persist.setItem("Airspeed", "Zero",
                                     str(self.airspeedZero))

            # Get the latest lift & drag, adjust for tare
            rawLiftLeft = latestSample.liftLeft - self.leftLoadTare
            rawLiftCenter = latestSample.liftCenter - self.centerLoadTare
            rawLiftRight = latestSample.liftRight - self.rightLoadTare
            rawDrag = latestSample.drag - self.dragTare

            # Scale to taste
            liftLeft = rawLiftLeft * self.liftLeftScaling
            liftCenter = rawLiftCenter * self.liftCenterScaling
            liftRight = rawLiftRight * self.liftRightScaling
            volts = latestSample.volts * self.voltsSlope + self.voltsZero
            # Because of the A/D resolution and the small values of deltaVolts,
            # we may need to filter amps to smooth out the appearance on the
            # display.
            deltaVolts = latestSample.amps * self.ampsSlope + self.ampsZero
            amps = deltaVolts / self.shuntOhms

            # Crunch the total lift and pitching moments
            totalLift = liftLeft + liftCenter + liftRight
            pitchMoment = (liftCenter * 5.63) + \
                            (liftLeft + liftRight) * 1.44

            # Get the AoA
            self.platformAoA = (latestSample.aoa - self.aoaPlatformTare) * \
                          self.aoaSlope
            
            wingAoA = (latestSample.aoa - self.aoaWingError - \
                       self.aoaPlatformTare) * self.aoaSlope

            # Scale the drag value and remove the lift component
            self.scaleDrag = rawDrag * self.dragScaling
            drag = (self.scaleDrag - (totalLift * sin(radians(self.platformAoA)))) / cos(radians(self.platformAoA))

            # Compute actual airspeed
            asCounts = latestSample.airspeed
            asPressure = (asCounts - self.airspeedZero) / 1379.3
            try:
                airspeed = self.airspeedSlope * sqrt((asPressure * 144.0 * 2.0) / 0.002378) * 0.682
            except ValueError:
                # airspeedPressure went negative due to rounding errors
                airspeed = 0.0

            if (airspeed < self.airspeedLowerLimit):
                # Think of this as a high-pass brickwall filter
                airspeed = 0.0

            # Compute hotwire speed
            hotwire = latestSample.hotwire
            hotwire = hotwire * self.hotwireSlope + self.hotwireZero
            if (hotwire < self.airspeedLowerLimit):
                hotwire = 0.0


            # Generate filtered values
            fLiftLeft = liftLeftFilter.get_filtered_value(liftLeft)
            fLiftCenter = liftCenterFilter.get_filtered_value(liftCenter)
            fLiftRight = liftRightFilter.get_filtered_value(liftRight)
            fDrag = dragFilter.get_filtered_value(drag)
            fTotalLift = totalLiftFilter.get_filtered_value(totalLift)
            fPitchMoment = pitchMomentFilter.get_filtered_value(pitchMoment)
            fTotalLiftStdDev = sqrt(totalLiftFilter.get_variance())
            fDragStdDev = sqrt(dragFilter.get_variance())
            fPitchMomentStdDev = sqrt(pitchMomentFilter.get_variance())
            fAirspeed = airspeedFilter.get_filtered_value(airspeed)
            fHotwire = hotwireFilter.get_filtered_value(hotwire)

            processedSample = ProcessedSample(volts,
                                              amps,
                                              (volts * amps),
                                              wingAoA,
                                              fAirspeed,
                                              fHotwire,
                                              fLiftLeft,
                                              fLiftCenter,
                                              fLiftRight,
                                              fTotalLift,
                                              fTotalLiftStdDev,
                                              fDrag,
                                              fDragStdDev,
                                              fPitchMoment,
                                              fPitchMomentStdDev,
                                              latestSample.timestamp)

            if (self.saveSamples):
                self.saveSamples = False
                # f is opened in doSave(), and remains open until
                # the requested samples are written here.
                self.f.write(str(processedSample) + self.runConfigComment)
                self.f.close()

            self.updateWindow.emit(processedSample)

            self.dumpData(processedSample)






