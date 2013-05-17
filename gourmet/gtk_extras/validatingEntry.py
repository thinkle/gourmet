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

import gobject
import gtk, re, cb_extras, gobject, time

TIME_TO_READ = 1000

class ValidatingEntry (gtk.VBox, gobject.GObject):

    __gsignals__ = {
        #'activate':'override',
        'mnemonic-activate':'override'
        }

    def __init__ (self, conv=None):
        gobject.GObject.__init__(self)
        self.warning_box = gtk.HBox()
        self.entry = gtk.Entry()
        self.image = gtk.Image()
        self.warning = gtk.Label()
        self.warning_box.add(self.image)
        self.image.set_from_icon_name(gtk.STOCK_DIALOG_WARNING,gtk.ICON_SIZE_MENU)
        self.warning_box.add(self.warning)
        a = gtk.Alignment()
        a.set_property('xalign',0)
        a.set_property('xscale',1)
        a.add(self.entry)
        a.show()
        self.entry.show()
        self.warning_box.show()
        self.valid = True
        self.validating = False
        self.add(self.warning_box)
        self.add(a)
        self.show()
        self.entry.connect('changed',self._validate)
        self.entry.connect('focus-out-event',self._validate_completed)
        self.warned = -1
        self.get_text = self.entry.get_text
        self.set_text = self.entry.set_text

    def do_activate (self,*args):
        self.entry.grab_focus()
        return True

    def do_mnemonic_activate (self,*args):
        self.entry.grab_focus()
        return True

    def connect (self, *args,**kwargs):
        """Hackish override"""
        return self.entry.connect(*args,**kwargs)

    def set_warning_text (self,text):
        self.warning.set_text('<i><span color="red">%s</span></i>'%text)
        self.warning.set_use_markup(True)

    def _show_warning (self):
        if not self.warned > 0:
            self.warned = time.time()
            self.warning_box.show_all()

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
            self.warning_box.hide()
            self.validating = False
    
    def _show_warning_on_delay (self,delay):
        if not self.validating:
            gobject.timeout_add(CHECK_DELAY,lambda *args: not self.valid and self._show_warning())
            self.validating = True

    def _validate (self, *args):
        txt = self.entry.get_text()
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
        txt = self.entry.get_text()
        error = self.find_completed_errors(txt)
        if error:
            self.set_warning_text(error)
            self._show_warning()
        else:
            self._hide_warning_slowly()

    def find_errors_in_progress (self, text):
        """Return a string describing any errors.
        Return None if there are no errors.

        This will be called as the user types.
        """
        raise NotImplementedError

    def find_completed_errors (self, text):
        """return a string describing any errors.
        Return none if there are no errors.

        This will be called when the user has finished typing.
        """
        raise NotImplementedError
