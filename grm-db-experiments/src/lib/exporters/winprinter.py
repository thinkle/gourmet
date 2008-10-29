import gourmet.dialog_extras as de
from gourmet.gdebug import debug
from gettext import gettext as _

# currently, windows printing is only supported via wxWindows -- see wxprinter.py

def show_disappointing_message ():
    de.show_message(
        label=_('Printing not supported'),
        sublabel=_('To print recipes, first export them, then print from another program. If you install wxWindows, you can print directly from Gourmet.'))

class RecRenderer:
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None):
        show_disappointing_message()
        debug('printing not supported; showed dialog',0)

class SimpleWriter:
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        show_disappointing_message()
        
    
