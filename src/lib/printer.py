from gdebug import debug
import os

try:
    # UNCOMMENT TO TEST WINDOWS PRINTING
    #import asdf
    from gnomeprinter import *
except ImportError:
    debug('Gnome Printer is not available')
    # UNCOMMENT TO TEST WINDOWS PRINTING
    #if 1:
    if os.name == 'nt':
        from winprinter import *
    else:
        from lprprinter import *
