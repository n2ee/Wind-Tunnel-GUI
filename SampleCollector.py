#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 21:48:24 2017

@author: markm

Listens on stdin|designated pipe and collects samples arriving there. Feeds
samples to the display UI and/or writes to a file.


"""
import os
from pathlib import Path
from math import sqrt

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
    dragTare = 0.0
    updateLoadTare = False
    
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

        self.voltsSlope = float(config.getItem("Volts", "slope"))
        self.voltsZero = float(config.getItem("Volts", "zero"))

        self.ampsSlope = float(config.getItem("Amps", "slope"))
        self.ampsZero = float(config.getItem("Amps", "zero"))
        self.shuntOhms = float(config.getItem("Amps", "shunt"))
        
        self.aoaSlope = float(config.getItem("AoA", "slope"))
        self.aoaZero = float(config.getItem("AoA", "zero"))

        self.airspeedLowerLimit = float(config.getItem("Airspeed",
                                                       "lowerlimit"))

        self.airspeedZero = float(config.getItem("Airspeed", "zero"))
        self.airspeedSlope = float(config.getItem("Airspeed", "slope"))
                  
        self.hotwireLowerLimit = float(config.getItem("Hotwire",
                                                       "lowerlimit"))

        self.hotwireZero = float(config.getItem("Hotwire", "zero"))
        self.hotwireSlope = float(config.getItem("Hotwire", "slope"))
                  
    def __del__(self):
        self.wait()

    def doSave(self, destFile = Path(os.devnull), config = ""):
        try:
            self.config = ', "' + config + '"\n'

            # does destFile exist?
            # no - open, write header, close
            
            if not destFile.is_file():
                self.f = open(destFile, "w")
                self.f.write(str(ProcessedSample.header()))
                self.f.write(", comment\n")
                self.f.close()
                
            self.f = open(destFile, "a")
            self.saveSamples = True
        except IOError:
            print ("Could not open: ", destFile)
            self.saveSamples = False

    def setLoadTare(self):
        self.updateLoadTare = True

    def dumpData(self, volts, amps, airspeed, hotwire, aoa, drag, liftLeft, liftCenter, liftRight, 
                 totalLift):
        print("V=%f, A=%f, as=%f, hw=%f, aoa=%f, drag=%f, LL=%f, LC=%f, LR=%f, TL=%f" \
              % (volts, amps, airspeed, hotwire, aoa, drag,
                 liftLeft, liftCenter, liftRight, totalLift))
    
    def run(self):
        # This method runs as its own thread, catching SensorSamples,
        # updating the GUI, processing data, and tossing it into a file
        # when asked to.
        
        # KalmanFilters still need tuning.
        # totalLiftFilter = KalmanFilter(150e-06, 1.5e-03)
        # pitchMomentFilter = KalmanFilter(150e-06, 1.5e-03)
        # dragFilter = KalmanFilter(150e-06, 1.5e-03)
        
        liftLeftFilter = RollingAverageFilter()
        liftCenterFilter = RollingAverageFilter()
        liftRightFilter = RollingAverageFilter()
        totalLiftFilter = RollingAverageFilter()
        pitchMomentFilter = RollingAverageFilter()
        dragFilter = RollingAverageFilter()
    
        while (True):
            latestSample = self.dataQ.get(True)

            if (self.updateLoadTare):
                self.updateLoadTare = False
                self.leftLoadTare = latestSample.liftLeft
                self.centerLoadTare = latestSample.liftCenter
                self.rightLoadTare = latestSample.liftRight
                self.dragTare = latestSample.drag

            # Get the AoA
            aoa = latestSample.aoa

            # Get the latest lift & drag, adjust for tare
            drag = latestSample.drag - self.dragTare
            rawLiftLeft = latestSample.liftLeft - self.leftLoadTare
            rawLiftCenter = latestSample.liftCenter - self.centerLoadTare
            rawLiftRight = latestSample.liftRight - self.rightLoadTare

            # Scale to taste
            liftLeft = rawLiftLeft * self.liftLeftScaling
            liftCenter = rawLiftCenter * self.liftCenterScaling
            liftRight = rawLiftRight * self.liftRightScaling
            
            aoa = aoa * self.aoaSlope + self.aoaZero
            drag = drag * self.dragScaling
            
            volts = latestSample.volts * self.voltsSlope + self.voltsZero
            
            # Because of the A/D resolution and the small values of deltaVolts,
            # we may need to filter amps to smooth out the appearance on the
            # display.
            deltaVolts = latestSample.amps * self.ampsSlope + self.ampsZero
            amps = deltaVolts / self.shuntOhms

            # Crunch the total lift and pitching moments
            totalLift = liftLeft + liftCenter + liftRight
            pitchMoment = (totalLift * 5.63) + \
                            (liftLeft + liftRight) * 1.44

            # Generate filtered values
            fLiftLeft = liftLeftFilter.get_filtered_value(liftLeft)
            fLiftCenter = liftCenterFilter.get_filtered_value(liftCenter)
            fLiftRight = liftRightFilter.get_filtered_value(liftRight)
            fDrag = dragFilter.get_filtered_value(drag) * self.dragScaling          
            fTotalLift = totalLiftFilter.get_filtered_value(totalLift)
            fPitchMoment = pitchMomentFilter.get_filtered_value(pitchMoment)
            fTotalLiftStdDev = sqrt(totalLiftFilter.get_variance())
            fDragStdDev = sqrt(dragFilter.get_variance())
            fPitchMomentStdDev = sqrt(pitchMomentFilter.get_variance())
            
            # Compute actual airspeed
            airspeed = latestSample.airspeed
            airspeed = airspeed * self.airspeedSlope + self.airspeedZero
            airspeed = sqrt((airspeed * 144.0 * 2.0) / (0.952 * 0.002378)) * 0.682
            if (airspeed < self.airspeedLowerLimit):
                # Think of this as a high-pass brickwall filter
                airspeed = 0.0
            
            # Compute hotwire speed
            # FIXME - need to calibrate values
            hotwire = latestSample.hotwire
            hotwire = hotwire * self.hotwireSlope + self.hotwireZero
            if (hotwire < self.airspeedLowerLimit):
                hotwire = 0.0
                                              
            self.tunnelWindow.setPower(volts * amps)
            self.tunnelWindow.setAoa(aoa)
            self.tunnelWindow.tblLiftDragMoment.setUpdatesEnabled(False)
            self.tunnelWindow.setAirspeed(airspeed)
            self.tunnelWindow.setAnenometer(hotwire)
            self.tunnelWindow.setLift(fTotalLift, fTotalLiftStdDev)
            self.tunnelWindow.setDrag(fDrag, fDragStdDev)
            self.tunnelWindow.setMoment(fPitchMoment, fPitchMomentStdDev)
            self.tunnelWindow.tblLiftDragMoment.setUpdatesEnabled(True)

            self.tunnelWindow.updateGraphs(fTotalLift, fDrag, fPitchMoment,
                                           airspeed)

            self.dumpData(volts, amps, airspeed, hotwire, aoa, drag, liftLeft,
                          liftCenter, liftRight, totalLift)
            
            if (self.saveSamples):
                self.saveSamples = False
                processedSample = ProcessedSample(volts,
                                                  amps,
                                                  latestSample.aoa,
                                                  latestSample.rpm,
                                                  airspeed,
                                                  hotwire,
                                                  fLiftLeft,
                                                  fLiftCenter,
                                                  fLiftRight,
                                                  fTotalLift,
                                                  fDrag,
                                                  fPitchMoment,
                                                  latestSample.timestamp)
                # f is opened in doSave(), and remains open until
                # the requested samples are written here.
                self.f.write(str(processedSample) + self.config)
                self.f.close()






