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

import gtk, re, gobject, time
from gettext import gettext as _
from gourmet.recipe import converter
from ValidatingEntry import ValidatingEntry

TIME_TO_READ = 1000

class TimeEntry (ValidatingEntry):

    def __init__ (self, conv=None):
        if not conv: self.conv = converter.conv
        else: self.conv = conv
        ValidatingEntry.__init__(self)    
        self.show()

    def find_errors_in_progress (self, txt):
        if (not txt) or self.conv.timestring_to_seconds(txt):
            return None
        elif not converter.NUMBER_MATCHER.match(txt.split()[0]):
            return _('Time must begin with a number or fraction followed by a unit (minutes, hours, etc.).')
        else:
            words = txt.split()
            if converter.NUMBER_MATCHER.match(words[-1]):
                return None
            else:
                partial_unit = words[-1]
            for u in self.conv.unit_to_seconds.keys():
                if u.lower().find(partial_unit.lower())==0:
                    return None
            return _('Invalid input.') + \
                   _('Time must be expressed in hours, minutes, seconds, etc.')
            self._show_warning()

    def find_completed_errors (self,*args):
        txt = self.get_text()
        if txt and not self.conv.timestring_to_seconds(txt):
            return _('Invalid input.') + \
                   _('Time must be expressed in hours, minutes, seconds, etc.')

            words = txt.split()
            if len(words) == 1:
                self._hide_warning_slowly()
                return
            elif converter.NUMBER_MATCHER.match(words[-1]):
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
        self.set_text(
            converter.seconds_to_timestring(
                seconds, fractions=converter.FRACTIONS_ASCII)
            )

    def get_value (self):
        return self.conv.timestring_to_seconds(self.get_text())
