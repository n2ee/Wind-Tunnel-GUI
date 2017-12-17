#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:16:44 2017

@author: markm


"""

import time
import datetime

from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit


class AnalogInput(InterfaceKit):
    
    def __init__(self, serialNo, channel):
        InterfaceKit.__init__(self)

        self.channel = channel

        try:
            self.openPhidget(serialNo)
            self.waitForAttach(10000)
        except PhidgetException as e:
            print("PhidgetException on open - code %i: %s" % (e.code, e.details))
            raise PhidgetException(e.code)
            
        self.setDataRate(self.getDataRateMax())
        
        def getVoltage(self):
            return self.getSensorValue(self.channel)
        

def main():

    ai = AnalogInput(315317, 3)
               
    while (True):
        try: 
            value = ai.getVoltage()
            timestamp = datetime.datetime.now()
            print("value = %f, timestamp = %s\n" % (value, timestamp))
        except PhidgetException as e:
            print("Exception on getVoltageRatio %i: %s" % (e.code, e.details))

        time.sleep(0.5)

if __name__ == "__main__":
    main()
    