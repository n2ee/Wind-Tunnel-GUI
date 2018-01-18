#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 16:29:58 2017

@author: markm
"""

from configparser import ConfigParser, NoSectionError
from pathlib import Path

class TunnelPersist():
    
    persistFilename = "persist.ini"
    
    def __init__(self):
        self.persist = ConfigParser()
        """
        Files are read in order listed below; if the later file has settings 
        that conflict with the earlier file, then those of the later file take
        precedence.
        
        The files don't have to exist, however, the the calling code may 
        not deal with some of the missing settings gracefully.
        
        This is a quick ripoff of TunnelConfig, to make it easy to load and
        save parameters across application restarts.
        """
        self.persistFile = Path(self.persistFilename)       
        self.persist.read(self.persistFilename)
        
    def getSectionMap(self, section):
        dict1 = {}
        try:
            options = self.persist.options(section)
        except NoSectionError:
            # File does not yet contain section. Create it.
            self.persist.add_section(section)
            dict1[0] = None
            return dict1
        
        for option in options:
            try:
                dict1[option] = self.persist.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
                
        return dict1

    def getItem(self, section, item):
        try:
            theItem = self.getSectionMap(section)[item.lower()]
        except KeyError:
            theItem = None
            
        return theItem

    def setItem(self, section, item, value):
        self.persist.set(section, item, value)
        try:      
            f = open(self.persistFile, "w")
            self.persist.write(f)
            f.close()
            
        except IOError:
            print ("Could not open: ", self.persistFile)

 
if __name__ == "__main__":
    tunnelPersist = TunnelPersist()
    
    aoaZero = tunnelPersist.getItem("AoA", "Zero")
    if aoaZero == None:
        aoaZero = 0.0
    else:
        aoaZero = float(aoaZero)

    airspeedZero = tunnelPersist.getItem("Airspeed", "Zero")
    if airspeedZero == None:
        airspeedZero = 0.0
    else:
        airspeedZero = float(airspeedZero)

    print("aoaZero = %f" % aoaZero)
    print("airspeedZero = %f" % airspeedZero)
    aoaZero += 1.1
    airspeedZero += 2.2
    tunnelPersist.setItem("AoA", "Zero", str(aoaZero))
    tunnelPersist.setItem("Airspeed", "Zero", str(airspeedZero))
