#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 17:13:08 2017

@author: markm
"""

import sys, re
from pathlib import Path

from TunnelConfig import TunnelConfig

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens. Borrowed from
    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    """
    import unicodedata
    value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
    # Chomp the leading 'b\'
    value = value[2:]
    value = str(re.sub("[^\w\s-]", "", value).strip().lower())
    value = str(re.sub("[-\s]+", "-", value))
    return value

def saveResults(fname):
    config = TunnelConfig()
    fname = slugify(fname)
    fname = Path(fname)
    destDirname = config.getItem("General", "DataDestinationDir")
    
    if (destDirname == None):
        destDirname = Path.cwd()
    else:
       Path(destDirname).mkdir(parents = True, exist_ok = True) 
    
    fname = destDirname / fname
    print ("Save Results clicked: %s" % fname)

def main():
    testFname = "ctest file\boo\baz"
    saveResults(testFname)
    
if __name__ == "__main__":
    main()
