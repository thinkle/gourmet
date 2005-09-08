#!/usr/bin/env python

import gtk, re, cb_extras, gobject, time
from gettext import gettext as _
import convert
import gobject

TIME_TO_READ = 1000

class TimeEntry (gtk.VBox, gobject.GObject):

    __gsignals__ = {
        #'activate':'override',
        'mnemonic-activate':'override'
        }

    def __init__ (self, conv=None):
        if not conv: self.conv = convert.converter()
        else: self.conv = conv
        gobject.GObject.__init__(self)
        self.warning_box = gtk.HBox()
        self.entry = gtk.Entry()
        self.image = gtk.Image()
        self.warning = gtk.Label()
        self.warning_box.add(self.image)
        self.image.set_from_icon_name(gtk.STOCK_DIALOG_WARNING,gtk.ICON_SIZE_MENU)
        self.warning_box.add(self.warning)
        self.entry.show()
        self.warning_box.show()
        self.valid = True
        self.validating = False
        self.add(self.warning_box)
        self.add(self.entry)
        self.show()
        self.entry.connect('changed',self._validate)
        self.entry.connect('focus-out-event',self._validate_completed)
        self.warned = -1
        #self.add(self)
        #gobject.GObject.connect(self,'mnemonic-activate',self.mnemonic_activate_cb)
        #gobject.GObject.connect(self,'activate',self.mnemonic_activate_cb)

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

    def set_value (self,seconds):
        self.entry.set_text(
            convert.seconds_to_timestring(seconds,
                                  fractions=convert.FRACTIONS_ASCII)
            )

    def get_value (self):
        return self.conv.timestring_to_seconds(self.entry.get_text())

    def _show_warning_on_delay (self,delay):
        if not self.validating:
            gobject.timeout_add(CHECK_DELAY,lambda *args: not self.valid and self._show_warning())
            self.validating = True

    def _validate (self,*args):
        txt = self.entry.get_text()
        if (not txt) or self.conv.timestring_to_seconds(txt):
            self.valid = True
            self.warn = False
            self._hide_warning() # instant
        elif not convert.NUMBER_MATCHER.match(txt.split()[0]):
            self.valid = False
            self.warn = True
            self.set_warning_text('Time must begin with a number or fraction.')
            self._show_warning()
        else:
            # grab the last word and assume its our unit...
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
        #else:
        #    self.set_warning_text("Invalid or incomplete time")
        #    self._show_warning()


    def _validate_completed (self,*args):
        txt = self.entry.get_text()
        if txt and not self.conv.timestring_to_seconds(txt):
            self.set_warning_text('Invalid input.' + 'Time must be expressed in hours, minutes, seconds, etc.')
            self._show_warning()
        
if gtk.pygtk_version[1]<8:
    gobject.type_register(TimeEntry)

    def _show_warning_on_delay (self,delay):
        if not self.validating:
            gobject.timeout_add(CHECK_DELAY,lambda *args: not self.valid and self._show_warning())
            self.validating = True

    def _validate (self,*args):
        txt = self.entry.get_text()
        if (not txt) or self.conv.timestring_to_seconds(txt):
            self.valid = True
            self.warn = False
            self._hide_warning() # instant
        elif not convert.NUMBER_MATCHER.match(txt.split()[0]):
            self.valid = False
            self.warn = True
            self.set_warning_text('Time must begin with a number or fraction.')
            self._show_warning()
        else:
            # grab the last word and assume its our unit...
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
        #else:
        #    self.set_warning_text("Invalid or incomplete time")
        #    self._show_warning()


    def _validate_completed (self,*args):
        txt = self.entry.get_text()
        if txt and not self.conv.timestring_to_seconds(txt):
            self.set_warning_text('Invalid input.' + 'Time must be expressed in hours, minutes, seconds, etc.')
            self._show_warning()
        
if gtk.pygtk_version[1] < 8: gobject.type_register(TimeEntry)
        
def makeTimeEntry ():
    te=TimeEntry()
    te.show()
    return te

if __name__ == '__main__':
    w=gtk.Window()
    vb = gtk.VBox()
    hb = gtk.HBox()
    l=gtk.Label('_Label')
    l.set_use_underline(True)
    hb.add(l)
    te=TimeEntry()
    l.set_mnemonic_widget(te)
    hb.add(te)
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
    
