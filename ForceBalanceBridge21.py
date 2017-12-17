#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:16:44 2017

@author: markm


"""

import time
import datetime

from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.Bridge import Bridge, BridgeGain


class ForceBalanceBridge(Bridge):
    
    def __init__(self, serialNo, channel):
        Bridge.__init__(self)
        
        self.channel = channel

        try:
            self.openPhidget(serialNo)
            self.waitForAttach(10000)
        except PhidgetException as e:
            print("PhidgetException on open - code %i: %s" % (e.code, e.details))
            raise PhidgetException(e.code)
            
        self.setDataRate(self.getDataRateMax())
        self.setGain(self.channel, BridgeGain.PHIDGET_BRIDGE_GAIN_128)
        self.setEnabled(self.channel, True)

    def getBridgeValue(self):
        return self.getBridgeValue(self.channel)
    
def main():

    br = ForceBalanceBridge(407609, 2)
               
    while (True):
        try: 
            value = br.getBridgeValue()
            timestamp = datetime.datetime.now()
            print("value = %f, timestamp = %s\n" % (value, timestamp))
        except PhidgetException as e:
            print("Exception on getVoltageRatio %i: %s" % (e.code, e.details))

        time.sleep(0.5)

if __name__ == "__main__":
    main()
    