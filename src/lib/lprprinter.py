import dialog_extras as de
import exporter
import os
from gettext import gettext as _

class RecRenderer:
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None, change_units=True):        
        command = 'lpr'
        # TO TEST LOUSY COMMAND-ENTERING CODE, UNCOMMENT THE FOLLOWING
        #command = 'asdf'
        while os.system('which %s'%command) != 0:
            label = _("Unable to find command %s.  ")%command
            label += _('Enter a print command')
            command = de.getEntry(label=_('Enter print command'),
                                  sublabel=label,
                                  entryLabel=_('Command'))
            if not command: raise "User cancelled!"
        lpr = os.popen(command,'w')
        de.show_message(
            label=_('Printing via %s')%command,
            sublabel=_('If you install python-gnome, you will be able to print with a much more attractive interface.'))
        for r in recs:
            exporter.exporter_mult(rd, r, out=lpr,mult=mult,change_units=change_units)
        lpr.close()

class SimpleWriter:
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        if file:
            self.out = open(file,'w')
        else:
            self.out = os.popen('lpr','w')
        if show_dialog:
            de.show_message(
                label='Printing via LPR',
                sublabel='If you install python-gnome, you will be able to print with a much more attractive interface.')

    def write_header (self, text):
        self.out.write("%s\n---\n"%text)
        
    def write_subheader (self, text):
        self.out.write("\n\n%s\n---\n"%text)

    def write_paragraph (self, text):
        self.out.write("%s\n"%text)

    def close (self):
        self.out.close()
    
        
