#!/usr/bin/python2.3
from OptionParser import *
import time

debug_level=options.debug

timestamp = options.time

def debug (message, level=10):
    if timestamp:
        message += " (%s)"%time.time()
    if level <= debug_level:
        print "DEBUG: ",message

timers = {}

class TimeAction:
    def __init__ (self, name, level=10):
        self.level = level
        if level <= debug_level:
            self.name = name            
            self.start = time.time()

    def end (self):        
        if self.level <= debug_level:            
            end = time.time()
            t=end-self.start
            print "DEBUG: %s TOOK %s SECONDS"%(self.name,t)
            if not timers.has_key(self.name): timers[self.name]=[t]
            else: timers[self.name].append(t)


def print_timer_info ():
    for n,times in timers.items():
        print "%s:"%n,
        for t in times: print "%.02e"%t,",",
        print ""
    
