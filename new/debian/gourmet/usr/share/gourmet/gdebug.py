#!/usr/bin/python2.3
from OptionParser import *

debug_level=options.debug

timestamp = options.time

def debug (message, level=10):
    if timestamp:
        message += " (%s)"%time.time()
    if level <= debug_level:
        print "DEBUG: ",message
