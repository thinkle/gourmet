#!/usr/bin/env python

import gtk, cb_extras
from gettext import gettext as _

class TimeEntry (gtk.HBox):
    def __init__ (self, *args, **kwargs):
        gtk.HBox.__init__(self, *args, **kwargs)
        self.adj = gtk.Adjustment(value=0, lower=0, upper=100, step_incr=1, page_incr=10)
        self.spin = gtk.SpinButton(adjustment=self.adj, digits=1)
        self.spin.set_numeric(True)
        self.spin.set_update_policy(gtk.UPDATE_IF_VALID)
        self.units = [_('seconds'),_('minutes'),_('hours'),_('days'),_('weeks'),_('months')]
        self.combo = gtk.ComboBoxEntry()
        cb_extras.set_model_from_list(self.combo,self.units)
        #self.combo.set_popdown_strings(self.units)
        self.pack_start(self.spin, True, True, 6)
        self.spin.show()
        self.pack_start(self.combo, True, True, 6)
        self.combo.show()
        #self.combo.entry.set_text(_('minutes'))
        cb_extras.cb_set_active_text(self.combo,_('minutes'))        
        
    def set_text (self, text):
        """We only accept text of the form '# unit'"""
        try:
            num,unit = text.split()
        except:
            num,unit = 0,_("minutes") #defaults
        self.spin.set_value(float(num))
        self.combo.entry.set_text(str(unit))
        
    def get_text (self):
        """We return text in the form of '# unit'"""
        num,unit=self.get_value()
        if num:
            if int(num)==num: num=int(num)
            return "%s %s"%(num,unit)
        else: return ""

    def get_value (self):
        """We return a tuple #,unit"""
        return (self.spin.get_value(),self.combo.entry.get_text())

    def set_value (self, number, unit):
        self.spin.set_value(float(number))
        self.combo.entry.set_text(str(unit))

    def connect (self, signal, handler):
        self.spin.connect(signal, handler)
        self.combo.entry.connect(signal, handler)

    def mnemonic_activate (self, group_cycling):
        print 'activate!'
        self.combo.grab_focus()
        return group_cycling
        
        
def makeTimeEntry ():
    te=TimeEntry()
    te.show()
    return te

if __name__ == '__main__':
    w=gtk.Window()
    te=TimeEntry()
    w.add(te)
    te.show()
    w.show()
    w.connect('delete_event',gtk.main_quit)
    gtk.main()
    
