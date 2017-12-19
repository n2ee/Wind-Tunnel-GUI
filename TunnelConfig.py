#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 16:29:58 2017

@author: markm
"""

from configparser import ConfigParser

class TunnelConfig():

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")

    def getSectionMap(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
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

if __name__ == "__main__":
    tunnelConfig = TunnelConfig()

    print (tunnelConfig.getItem("Version", "version"))
    print (tunnelConfig.getItem("PhidgetBoards", "liftboardserialno"))



