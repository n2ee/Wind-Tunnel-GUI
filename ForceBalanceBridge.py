#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:16:44 2017

@author: markm


"""

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
            raise PhidgetException(e.code)

        self.setDataInterval(self.getMinDataInterval())
        self.setBridgeGain(BridgeGain.BRIDGE_GAIN_128)
        self.setBridgeEnabled(True)

def main():

    brLeft = ForceBalanceBridge(407635, 0)
    brCenter = ForceBalanceBridge(407635, 1)
    brRight = ForceBalanceBridge(407635, 2)
               
    while (True):
        try: 
            lValue = brLeft.getSensorValue()
            cValue = brCenter.getSensorValue()
            rValue = brRight.getSensorValue()
            timestamp = datetime.datetime.now()
            print("left value = %f, center value = %f, right value = %f, timestamp = %s\n" % (lValue, cValue, rValue, timestamp))
        except PhidgetException as e:
            print("Exception on getVoltageRatio %i: %s" % (e.code, e.details))

        time.sleep(0.5)

if __name__ == "__main__":
    main()
    
