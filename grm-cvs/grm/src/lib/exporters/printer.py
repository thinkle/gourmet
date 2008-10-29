from gourmet.gdebug import debug
import os

# We grab the printer of choice and import methods from it. Each printer
# should provide a RecRenderer class which will do the actual printing.

def load_gnomeprint ():
    try:
        import gnomeprint
        global RecRenderer,SimpleWriter
        if hasattr(gnomeprint,'pango_create_context') and hasattr(gnomeprint,'pango_get_default_font_map'):            
            from gnomeprinter import RecRenderer, SimpleWriter
        else:
            # pre-pango gnomeprint
            debug("Using out-of-date gnomeprint (no pango layout support in printing)",0)
            from gnomeprinter_obsolete import RecRenderer, SimpleWriter
    except ImportError:
        debug('Gnome Printer is not available',0)
        return True

def load_winprinter ():
    global RecRenderer,SimpleWriter
    if os.name == 'nt':        
        from winprinter import RecRenderer, SimpleWriter
    else:
        return True
    

def load_lprprint ():
    if os.name == 'nt': return True
    global RecRenderer,SimpleWriter
    from lprprinter import RecRenderer, SimpleWriter


printers = {'gnomeprint':load_gnomeprint,
            'win':load_winprinter,
            'lpr':load_lprprint}

from gourmet.OptionParser import options

printer_names = ['lpr','win','gnomeprint']
printer = options.printer

try:
    printer_names.remove(printer)
except ValueError:
    print 'Printer type: ',printer,' not recognized!'
    printer = printer_names.pop()

# A return value of True means we failed to import
# so we'd better keep trying
while printers[printer]() and printers:
    print "Loading ",printer," failed:",
    printer = printer_names.pop()
    print "trying ",printer
    
