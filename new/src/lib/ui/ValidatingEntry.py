### Copyright (C) 2005 Thomas M. Hinkle
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
### Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
### 02111-1307, USA.

import gtk, re, gobject, time, sexy

TIME_TO_READ = 1000
CHECK_DELAY = 400

class ValidatingEntry (sexy.IconEntry, gobject.GObject):

    __gsignals__ = {
        'mnemonic-activate':'override'
        }

    def __init__ (self, conv=None):
        gobject.GObject.__init__(self)
        
        self.base = self.get_style().base[gtk.STATE_NORMAL]
        self.image = gtk.Image()
        self.image.set_from_stock(gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_MENU)
        self.image.show()
        self.empty = gtk.Image()
        
        self.show()
        self.connect('changed',self._validate)
        self.connect('focus-out-event',self._validate_completed)
        self.warned = -1
        self.validating = False

    def do_activate (self,*args):
        self.grab_focus()
        return True

    def do_mnemonic_activate (self,*args):
        self.grab_focus()
        return True

    def set_warning_text (self,text):
        pass

    def _show_warning (self):
        if not self.warned > 0:
            self.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(65535,55535,55535));
            self.set_icon(sexy.ICON_ENTRY_SECONDARY, self.image)
            #self.warned = time.time()
            
    def _hide_warning_slowly (self):
        self.warn = False
        if self.warned == -1: return #already hidden
        warned_for = time.time() - self.warned
        remaining = TIME_TO_READ - warned_for * 1000
        if remaining > 0:
            gobject.timeout_add(remaining,self._hide_warning)
        else:
            self._hide_warning()

    def _hide_warning (self):
        if not self.warn:
            self.warned = -1
            self.modify_base(gtk.STATE_NORMAL, self.base)
            self.set_icon(sexy.ICON_ENTRY_SECONDARY, self.empty)
            self.validating = False
    
    def _show_warning_on_delay (self,delay=CHECK_DELAY):
        if not self.validating:
            gobject.timeout_add(delay,lambda *args: not self.valid and self._show_warning())
            self.validating = True

    def _validate (self, *args):
        txt = self.get_text()
        error = self.find_errors_in_progress(txt)
        if not error:
            self.valid = True
            self.warn = False
            self._hide_warning()
        else:
            self.valid = False
            self.warn = True
            self.set_warning_text(error)
            self._show_warning()

    def _validate_completed (self, *args):
        txt = self.get_text()
        error = self.find_completed_errors(txt)
        if error:
            self.set_warning_text(error)
            self._show_warning()
        else:
            self._hide_warning_slowly()
