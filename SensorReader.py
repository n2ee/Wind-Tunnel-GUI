#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 17:00:51 2017

@author: markm
"""

import sys
import time
import datetime
from queue import Queue
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread

from PhidgetBoardWait import Ui_Dialog
from Phidget22.PhidgetException import PhidgetException

from TunnelConfig import TunnelConfig
from SensorSample import SensorSample
from ForceBalanceBridge import ForceBalanceBridge
from AnalogInput import AnalogInput

class SensorReader(QThread):
    
    def __init__(self, tw, dataQ):
        QThread.__init__(self)
        self.dataQ = dataQ
        self.tw = tw
        
        print ("Waiting for phidget boards...\n")

        config = TunnelConfig()
        

        waitDialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(waitDialog)
        
        if (tw == None):
            # ui.buttonBox.clicked.connect(self.close)
            pass
        else:
            ui.buttonBox.clicked.connect(tw.close)
        
        waitDialog.show()

        
        try:
            # Connect up to the phidget boards
            serialNo = int(config.getItem("PhidgetBoards", "liftboardserialno"))
            liftLeftPort = int(config.getItem("PhidgetBoards", "liftleftport"))
            self.liftLeft = ForceBalanceBridge(serialNo, liftLeftPort)
                    
            liftCenterPort = int(config.getItem("PhidgetBoards", "liftcenterport"))
            self.liftCenter = ForceBalanceBridge(serialNo, liftCenterPort)
            
            liftRightPort = int(config.getItem("PhidgetBoards", "liftrightport"))
            self.liftRight = ForceBalanceBridge(serialNo, liftRightPort)
            
            dragPort = int(config.getItem("PhidgetBoards", "dragport"))
            self.drag = ForceBalanceBridge(serialNo, dragPort)

            serialNo = int(config.getItem("PhidgetBoards", "airspeedserialno"))
            airspeedPort = int(config.getItem("PhidgetBoards", "airspeedport"))
            hotwirePort = int(config.getItem("PhidgetBoards", "hotwireport"))
            aoaPort = int(config.getItem("PhidgetBoards", "aoaport"))
            voltsPort = int(config.getItem("PhidgetBoards", "voltsport"))
            ampsPort = int(config.getItem("PhidgetBoards", "ampsport"))
            
            self.airspeed = AnalogInput(serialNo, airspeedPort)
            self.hotwire = AnalogInput(serialNo, hotwirePort)
            self.aoa = AnalogInput(serialNo, aoaPort)
            self.volts = AnalogInput(serialNo, voltsPort)
            self.amps = AnalogInput(serialNo, ampsPort)

        except PhidgetException as e:
            print ("__init__: PhidgetException %i: %s" % (e.code, e.details))
            sys.exit(1)
            

        waitDialog.close()

    def __del__(self):
        
        # Cleanup all the phidget channels
        self.aoa.close()
        self.hotwire.close()
        self.airspeed.close()
        self.drag.close()
        self.liftRight.close()
        self.liftCenter.close()
        self.liftLeft.close()
        
        self.wait()
     
    def run(self):
        currentSample = SensorSample()
        
        while (True):           
            try:
                currentSample.airspeed = self.airspeed.getScaledValue(1000)
                currentSample.hotwire = self.hotwire.getScaledValue(1000)
                
                currentSample.aoa = self.aoa.getScaledValue(1000)
                
                currentSample.volts = self.volts.getVoltage()
                currentSample.amps = self.amps.getVoltage()
            
                currentSample.liftLeft = self.liftLeft.getVoltageRatio()
                currentSample.liftCenter = self.liftCenter.getVoltageRatio()
                currentSample.liftRight = self.liftRight.getVoltageRatio()
                currentSample.drag = self.drag.getVoltageRatio()
                
                currentSample.timestamp = datetime.datetime.now()
                self.dataQ.put_nowait(currentSample)
            except PhidgetException as e:
                print ("PhidgetException %i: %s" % (e.code, e.details))
            if (self.tw == None):
                sampleDelay = 1.0 / 2.0
            else:
                sampleDelay = (1.0 / self.tw.outSampleRate.value())
                
            time.sleep(sampleDelay)

if __name__ == "__main__":
    
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    else:
        print('QApplication instance already exists: %s' % str(app))

    # app.exec_()
    
    print('Creating testQ')

    testQ = Queue(16384)
    sensorRdr = SensorReader(None, testQ)
    sensorRdr.start()

    while (True):
        testSample = testQ.get(True)
        print (testSample)
        
        
    sys.exit(0)
