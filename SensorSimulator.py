#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 09:19:20 2017

@author: markm

SensorSimulator() generates fake sensor data, primarily for exercising the UI.
"""
import sys
import math
import time
import datetime
from queue import Queue
from PyQt5.QtCore import QThread

from SensorSample import SensorSample


class SensorSimulator(QThread):
    
    def __init__(self, tw, dataQ):
        QThread.__init__(self)
        self.dataQ = dataQ
        self.tw = tw
        
    def __del__(self):
        self.wait()
     
    def run(self):
        theta = 0
        dummySample = SensorSample()
        
        while (True):
            theta = (theta + 1) % 360 
            theta45Lead = (45 + theta) % 360
            theta45Lag = (theta + 315) % 360
            dummySample.volts = math.cos(math.radians(theta))
            dummySample.amps = math.sin(math.radians(theta)) 
            dummySample.aoa = (theta /45) - 4
            dummySample.rpm = 10 * theta / 2
            dummySample.airspeed = 500.0 + int(math.cos(math.radians(theta / 3)) * 500)
            dummySample.hotwire = 500.0 + int(math.cos(math.radians(theta / 3)) * 500)
            dummySample.liftLeft = math.cos(math.radians(theta45Lead))
            dummySample.liftCenter = math.cos(math.radians(theta))
            dummySample.liftRight = math.cos(math.radians(theta45Lag))
            dummySample.drag = theta / 8
            dummySample.timestamp = datetime.datetime.now()
            self.dataQ.put_nowait(dummySample)
            if (self.tw == None):
                sampleDelay = 1.0 / 2.0
            else:
                sampleDelay = (1.0 / self.tw.outSampleRate.value())
                
            time.sleep(sampleDelay)
         

if __name__ == "__main__":
    testQ = Queue(16384)
    sensorSim = SensorSimulator(None, testQ)
    sensorSim.start()
    
    while (True):
        testSample = testQ.get(True)
        print (testSample)
        
        
    sys.exit(0)
