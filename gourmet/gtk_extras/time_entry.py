from typing import Optional
from gettext import gettext as _
from gi.repository import Gdk, Gtk

from gourmet.convert import (Converter, FRACTIONS_ASCII,
                             NUMBER_MATCHER, seconds_to_timestring)
from gourmet.gtk_extras.validatingEntry import ValidatingEntry


class TimeEntry(ValidatingEntry):
    __gtype_name__ = 'TimeEntry'

    def __init__(self):
        super().__init__()
        self.conv = Converter.instance()
        self.entry.get_value = self.get_value
        self.entry.set_value = self.set_value

        self._error_msg = _('Time must consist of a number and a unit.')

    def find_errors_in_progress(self, text: str) -> Optional[str]:
        text = text.strip()  # Remove any leading or trailing whitespaces
        if text == '' or self.conv.timestring_to_seconds(text):
            return

        # The user entered something like `13 h` or `13 hours`
        if ' ' in text:
            number, partial_unit, *_ = text.split()
        else:
            number = text
            partial_unit = ''

        has_number = NUMBER_MATCHER.match(number)
        has_unit = any([unit.startswith(partial_unit)
                        for unit in self.conv.unit_to_seconds.keys()])
        if not (has_number and has_unit):
            return self._error_msg

    def find_completed_errors(self, text: str) -> Optional[str]:
        # Called when the widget looses focus
        text = text.strip()
        if text and not self.conv.timestring_to_seconds(text):
            self.entry.override_background_color(Gtk.StateFlags.NORMAL,
                                                 Gdk.RGBA(1., 0.5, 0.5))
            self.entry.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA())
            return self._error_msg

    def set_value(self, seconds: float):
        self.entry.set_text(seconds_to_timestring(seconds,
                                                  fractions=FRACTIONS_ASCII))

    def get_value(self):
        return self.conv.timestring_to_seconds(self.entry.get_text())