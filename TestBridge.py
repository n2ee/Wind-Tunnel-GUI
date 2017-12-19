#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:16:44 2017

@author: markm


"""

import sys
import time
import datetime

from Phidget22.PhidgetException import PhidgetException
from Phidget22.BridgeGain import BridgeGain
from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput


class ForceBalanceBridge(VoltageRatioInput):
    
    def __init__(self, serialNo, channel):
        VoltageRatioInput.__init__(self)
        
        self.setDeviceSerialNumber(serialNo)
        self.setChannel(channel)

        try:
            self.openWaitForAttachment(10000)
        except PhidgetException as e:
            print("PhidgetException on open - code %i: %s" % (e.code, e.details))
            raise PhidgetException(e)

        self.setDataInterval(self.getMinDataInterval())
        self.setBridgeGain(BridgeGain.BRIDGE_GAIN_128)
        self.setBridgeEnabled(True)
        
def main():
    sampleDelay = 0.1
    br = ForceBalanceBridge(407609,2)
               
    while (True):
        
        try: 
            value = br.getVoltageRatio()
            timestamp = datetime.datetime.now()
            print("value = %f, timestamp = %s\n" % (value, timestamp))
        except PhidgetException as e:
            print("Exception on getVoltageRatio %i: %s" % (e.code, e.details))

        time.sleep(sampleDelay)

if __name__ == "__main__":
    main()
    