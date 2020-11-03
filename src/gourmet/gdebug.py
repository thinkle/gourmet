import time
import traceback

from .optionparser import args

debug_level=args.debug or 0
debug_file=args.debug_file
timestamp=args.time

if debug_file:
    import re
    debug_file = re.compile(debug_file)

if debug_level > 0: print('DEBUG_LEVEL=',debug_level)
if debug_file: print('DEBUG_FILE=',debug_file)


def debug (message, level=10):
    if timestamp: ts= '%s:'%time.time()
    else: ts = ''
    if level <= debug_level:
        stack = traceback.extract_stack()
        if len(stack) >= 2:
            caller=stack[-2]
            finame=caller[0]
            line = caller[1]
        else:
            finame = " ".join(stack)
            line = ""
        if args.debug_file:
            if debug_file.search(finame):
                print("DEBUG: ",ts,"%s: %s"%(finame,line),message)
        else:
            print("DEBUG: ",ts,"%s: %s"%(finame,line),message)

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
            # grab our location
            stack=traceback.extract_stack()
            if len(stack)>2:
                caller=stack[-2]
                finame=caller[0]
                line = caller[1]
            else:
                finame = " ".join(stack)
                line = ""
            if not args.debug_file or debug_file.search(finame):
                print("DEBUG: %s TOOK %s SECONDS"%(self.name,t))
                if self.name not in timers: timers[self.name]=[t]
                else: timers[self.name].append(t)


def print_timer_info ():
    for n,times in list(timers.items()):
        print("%s:"%n, end=' ')
        for t in times: print("%.02e"%t,",", end=' ')
        print("")

if __name__ == '__main__':
    t=TimeAction('this is a test',0)
    debug('This is a test',0)
    debug('This is another test',0)
    t.end()
    print_timer_info()
