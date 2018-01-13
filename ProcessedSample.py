#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 17:54:40 2017

@author: markm
"""
import datetime

class ProcessedSample(object):

    def __init__(self, volts = 0.0, amps = 0.0, aoa = 0.0, rpm = 0, 
                 airspeed = 0.0, hotwire = 0.0,  liftLeft = 0.0, 
                 liftCenter = 0.0, liftRight = 0.0, totalLift = 0.0, 
                 drag = 0.0, pitchmoment = 0.0, 
                 timestamp = datetime.datetime.now()):
        self.volts = volts
        self.amps = amps
        self.aoa = aoa
        self.rpm = rpm
        self.airspeed = airspeed
        self.hotwire = hotwire
        self.liftLeft = liftLeft
        self.liftCenter = liftCenter
        self.liftRight = liftRight
        self.totalLift = totalLift
        self.drag = drag
        self.pitchMoment = pitchmoment
        self.timestamp = timestamp

    def __repr__(self):
        return "volts: %f, amps: %f, aoa: %f, rpm: %d, airspeed: %f, " \
                "hotwire: %f, liftLeft: %f, liftCenter: %f, liftRight: %f, " \
                "totalLift: %f, drag: %f, pitchMoment: %f, timestamp: %s" % \
            (self.volts, self.amps, self.aoa, self.rpm, self.airspeed,
             self.hotwire, self.liftLeft, self.liftCenter, self.liftRight, 
             self.totalLift, self.drag, self.pitchMoment, self.timestamp)        
        
if __name__ == "__main__":
    testSample = [ProcessedSample(i / 10.0, i / 10.0, i / 10.0, i, i/ 10.0, \
                                  i/ 10.0, i / 10.0, i / 10.0, i / 10.0, \
                                  i / 10.0, i / 10.0, i / 10.0, i) \
                    for i in range(10)]

    for i in range(10):
        print (testSample[i])
 
    print ("done")
    
