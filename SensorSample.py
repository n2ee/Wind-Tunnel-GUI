#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 17:54:40 2017

@author: markm
"""
import datetime

class SensorSample(object):

    def __init__(self, volts = 0.0, amps = 0.0, aoa = 0.0, rpm = 0, 
                 airspeed = 0.0, hotwire = 0.0, liftRight = 0.0, 
                 liftCenter = 0.0, liftLeft = 0.0, drag = 0.0,
                 timestamp = datetime.datetime.now()):
        self.volts = volts
        self.amps = amps
        self.aoa = aoa
        self.rpm = rpm
        self.airspeed = airspeed
        self.hotwire = hotwire
        self.liftRight = liftRight
        self.liftCenter = liftCenter
        self.liftLeft = liftLeft
        self.drag = drag
        self.timestamp = timestamp

    def __repr__(self):
        return "volts: %f, amps: %f, aoa: %f, rpm: %d, airspeed: %f, " \
                "hotwire: %f, liftRight: %f, liftCenter: %f, liftLeft: %f, " \
                "drag: %f, timestamp: %s" % \
            (self.volts, self.amps, self.aoa, self.rpm, self.airspeed,
             self.hotwire, self.liftRight, self.liftCenter, self.liftLeft,
             self.drag, self.timestamp)        
        
if __name__ == "__main__":
    testSensor = [SensorSample(i / 10.0, i / 10.0, i / 10.0, i, i/ 10.0, \
                               i / 10.0, i / 10.0, i / 10.0, i / 10.0, \
                               i / 10.0) for i in range(10)]

    for i in range(10):
        print (testSensor[i])
 
    print ("done")
    