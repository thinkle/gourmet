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

def load_wxprint ():
    # We don't want to use wxprint anymore -- it crashes
    return True
    #try:
    #    print 'importing wxprinter'
    #    global RecRenderer,SimpleWriter
    #    from wxprinter import RecRenderer, SimpleWriter
    #except:
    #    return True

def load_lprprint ():
    global RecRenderer,SimpleWriter
    if os.name == 'nt':
        print 'Install wxWindows to print on Windows'
        from winprinter import RecRenderer, SimpleWriter
    else:
        from lprprinter import RecRenderer, SimpleWriter


printers = {'gnomeprint':load_gnomeprint,
            'wx':load_wxprint,
            'lpr':load_lprprint}

from gourmet.OptionParser import options

printer_names = ['lpr','wx','gnomeprint']
printer = options.printer

try:
    printer_names.remove(printer)
except ValueError:
    print 'Printer type: ',printer,' not recognized!'
    printer = printers_names.pop()

# A return value of True means we failed to import
# so we'd better keep trying
while printers[printer]() and printers:
    print "Loading ",printer," failed:",
    printer = printer_names.pop()
    print "trying ",printer
