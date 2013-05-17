### Copyright (C) 2005 Thomas M. Hinkle
### Copyright (C) 2009 Rolf Leggewie
###
### This library is free software; you can redistribute it and/or
### modify it under the terms of the GNU General Public License as
### published by the Free Software Foundation; either version 2 of the
### License, or (at your option) any later version.
###
### This library is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
### General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this library; if not, write to the Free Software
### Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301
### USA 

import gtk, re, gobject, time
from gettext import gettext as _
import gourmet.convert as convert
import gobject
import cb_extras, validatingEntry

TIME_TO_READ = 1000

class TimeEntry (validatingEntry.ValidatingEntry):
    __gtype_name__ = 'TimeEntry'

    def __init__ (self, conv=None):
        if not conv: self.conv = convert.get_converter()
        else: self.conv = conv
        validatingEntry.ValidatingEntry.__init__(self)
        self.entry.get_value = self.get_value
        self.entry.set_value = self.set_value        

    def find_errors_in_progress (self, txt):
        if (not txt) or self.conv.timestring_to_seconds(txt):
            return None
        elif not convert.NUMBER_MATCHER.match(txt.split()[0]):
            return _('Time must begin with a number or fraction followed by a unit (minutes, hours, etc.).')
        else:
            words = txt.split()
            #if len(words) == 1:
            #    self._hide_warning_slowly()
            #    return
            if convert.NUMBER_MATCHER.match(words[-1]):
                return None
            else:
                partial_unit = words[-1]
            for u in self.conv.unit_to_seconds.keys():
                if u.lower().find(partial_unit.lower())==0:
                    return None
                    #self._hide_warning_slowly()
                    #return
            return _('Invalid input.') + \
                   _('Time must be expressed in hours, minutes, seconds, etc.')
            self._show_warning()
        #else:
        #    self.set_warning_text("Invalid or incomplete time")
        #    self._show_warning()

    def find_completed_errors (self,*args):
        txt = self.entry.get_text()
        if txt and not self.conv.timestring_to_seconds(txt):
            return _('Invalid input.') + \
                   _('Time must be expressed in hours, minutes, seconds, etc.')

            words = txt.split()
            if len(words) == 1:
                self._hide_warning_slowly()
                return
            elif convert.NUMBER_MATCHER.match(words[-1]):
                return
            else:
                partial_unit = words[-1]
            for u in self.conv.unit_to_seconds.keys():
                if u.lower().find(partial_unit.lower())==0:
                    self._hide_warning_slowly()
                    return
            self.valid = False
            self.warn = True
            self.set_warning_text('Invalid input.' + 'Time must be expressed in hours, minutes, seconds, etc.')
            self._show_warning()

    def set_value (self,seconds):
        self.entry.set_text(
            convert.seconds_to_timestring(seconds,
                                  fractions=convert.FRACTIONS_ASCII)
            )

    def get_value (self):
        return self.conv.timestring_to_seconds(self.entry.get_text())
        
def make_time_entry():
    te=TimeEntry()
    te.show()
    return te

if __name__ == '__main__':
    w=gtk.Window()
    vb = gtk.VBox()
    hb = gtk.HBox()
    l=gtk.Label('_Label')
    l.set_use_underline(True)
    l.set_alignment(0,0.5)
    hb.pack_start(l)
    te=TimeEntry()
    import sys
    te.connect('changed',lambda w: sys.stderr.write('Time value: %s'%w.get_value()))
    l.set_mnemonic_widget(te)
    hb.pack_start(te,expand=False,fill=False)
    vb.add(hb)
    qb = gtk.Button(stock=gtk.STOCK_QUIT)
    vb.add(qb)
    l.show()
    hb.show()
    qb.show()
    te.show()
    vb.show()
    qb.connect('clicked',lambda *args: w.hide() and gtk.main_quit() or gtk.main_quit())
    w.add(vb)
    w.show()
    w.connect('delete_event',gtk.main_quit)
    gtk.main()
    
