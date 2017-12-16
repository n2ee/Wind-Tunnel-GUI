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

        self.setDataInterval(self.getMinDataInterval())

def main():

    ai = AnalogInput(315317, 3)
               
    while (True):
        try: 
            value = ai.getVoltageRatio()
            timestamp = datetime.datetime.now()
            print("value = %f, timestamp = %s\n" % (value, timestamp))
        except PhidgetException as e:
            print("Exception on getVoltageRatio %i: %s" % (e.code, e.details))

        time.sleep(0.5)

if __name__ == "__main__":
    main()
    