from gourmet.gdebug import debug
import os

# We grab the printer of choice and import methods from it. Each printer
# should provide a RecRenderer class which will do the actual printing.

try:
    # UNCOMMENT TO TEST NON-GNOME PRINTING
    #import asdf
    import gnomeprint
    # to test, uncomment...
    #if False:
    if hasattr(gnomeprint,'pango_create_context') and hasattr(gnomeprint,'pango_get_default_font_map'):
        from gnomeprinter import *
    else:
        # pre-pango gnomeprint
        debug("Using out-of-date gnomeprint (no pango layout support in printing)",0)
        from gnomeprinter_obsolete import *
except ImportError:
    debug('Gnome Printer is not available',0)
    # UNCOMMENT TO TEST WINDOWS PRINTING
    #if 1:
    if os.name == 'nt':
        try:
            from wxprinter import *
        except ImportError:
            print 'Install wxWindows to print on Windows'
            from winprinter import *
    else:
        from lprprinter import *
