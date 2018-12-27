#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:16:44 2017

@author: markm


"""

import time
import datetime

from Phidget22.PhidgetException import PhidgetException
from Phidget22.Devices.VoltageInput import VoltageInput


class AnalogInput(VoltageInput):
    
    def __init__(self, serialNo, channel):
        VoltageInput.__init__(self)

        self.setDeviceSerialNumber(serialNo)
        self.setChannel(channel)

        try:
            self.openWaitForAttachment(10000)
        except PhidgetException as e:
            print("PhidgetException on open - code %i: %s" % (e.code, e.details))
            raise PhidgetException(e.code)

        try:
            minDataInterval = self.getMinDataInterval()
            self.setDataInterval(minDataInterval)
        except PhidgetException as e:
            print("Ignored PhidgetException on set/getDataInterval - code %i: %s" % (e.code, e.details))

        self.minV = self.getMinVoltage()
        self.maxV = self.getMaxVoltage()
        self.rangeV = self.maxV - self.minV
        
    def getScaledValue(self, scalingValue):
        return int(((self.getVoltage() - self.minV) * scalingValue) / self.rangeV)
    
        
def main():

    ai = AnalogInput(315317, 1)
    
    print("minV = %f, maxV = %f, rangeV = %f" % (ai.minV, ai.maxV, ai.rangeV))
    
    while (True):
        try: 
            volts = ai.getVoltage()
            value = ai.getScaledValue(1000)
            timestamp = datetime.datetime.now()
            print("volts = %f, value = %d, timestamp = %s\n" % (volts, value, timestamp))
        except PhidgetException as e:
            print("Exception on getVoltageRatio %i: %s" % (e.code, e.details))

        time.sleep(0.5)

if __name__ == "__main__":
    main()
    
