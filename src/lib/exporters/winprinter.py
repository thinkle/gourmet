import gourmet.dialog_extras as de
from gourmet.gdebug import debug
from gettext import gettext as _
import lprprinter

class RecRenderer:
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None):
        de.show_message(
            label=_('Printing not supported'),
            sublabel=_('Sorry, printing is not yet supported on Windows. To print recipes, first export them, then print from another program.'))
        debug('printing not supported; showed dialog',0)

class SimpleWriter (lprprinter.SimpleWriter):
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        if file:
            lprprinter.SimpleWriter.__init__(self,file,dialog_parent,show_dialog)
        if not file:
            de.show_message(
                label=_('Printing not supported'),
                sublabel=_('Sorry, printing is not yet supported on Windows. To print your shopping list, try saving and printing from another program.'))

    def write_header (self, text):
        self.out.write("%s\n---\n"%text)
        
    def write_subheader (self, text):
        self.out.write("\n\n%s\n---\n"%text)

    def write_paragraph (self, text):
        self.out.write("%s\n"%text)

    def close (self):
        self.out.close()
    
        
        
