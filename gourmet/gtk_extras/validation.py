import time
from typing import Optional

from gettext import gettext as _
from gi.repository import Gdk, GObject, Gtk

from gourmet.convert import (Converter, FRACTIONS_ASCII,
                             NUMBER_MATCHER, seconds_to_timestring)

TIME_TO_READ = 1000


class ValidatingEntry(Gtk.VBox, GObject.GObject):

    __gsignals__ = {'mnemonic-activate': 'override'}

    def __init__(self):
        super().__init__(self)

        # TODO: entry needn't be a property of self, but this requires
        # reworking all derived classes
        self.entry = Gtk.Entry()
        self.entry.set_name('entry')
        self.entry.connect('changed', self._validate)
        self.entry.connect('focus-out-event', self._validate_completed)
        self.get_text = self.entry.get_text
        self.set_text = self.entry.set_text
        self.entry.show()

        self.warning_box = Gtk.HBox()
        self.image = Gtk.Image()
        self.warning = Gtk.Label()
        self.warning_box.add(self.image)
        self.image.set_from_icon_name(Gtk.STOCK_DIALOG_WARNING,
                                      Gtk.IconSize.MENU)
        self.warning_box.add(self.warning)
        a = Gtk.Alignment(xscale=1)
        a.add(self.entry)
        a.show()
        self.warning_box.show()
        self.valid = True
        self.validating = False
        self.add(self.warning_box)
        self.add(a)
        self.show()

        self.warned = -1

        screen = Gdk.Screen.get_default()
        gtk_provider = Gtk.CssProvider()
        gtk_context = Gtk.StyleContext()
        gtk_context.add_provider_for_screen(screen, gtk_provider,
                                            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)  # noqa
        gtk_provider.load_from_data(b"""
        #entry.error { background-color: #FF8888; color: white; }
        """)

    def do_activate(self, *args):
        self.entry.grab_focus()
        return True

    def do_mnemonic_activate(self, *args):
        self.entry.grab_focus()
        return True

    def connect(self, *args, **kwargs):
        return self.entry.connect(*args, **kwargs)

    def set_warning_text(self, text: str):
        self.warning.set_text(f'<i><span color="red">{text}</span></i>')
        self.warning.set_use_markup(True)

    def _show_warning(self):
        if not self.warned > 0:
            self.warned = time.time()
            self.warning_box.show_all()

    def _hide_warning_slowly(self):
        self.warn = False
        if self.warned == -1:
            return  # Already hidden
        warned_for = time.time() - self.warned
        remaining = TIME_TO_READ - warned_for * 1000
        if remaining > 0:
            GObject.timeout_add(int(remaining), int(self._hide_warning))
        else:
            self._hide_warning()

    def _hide_warning(self):
        if not self.warn:
            self.warned = -1
            self.warning_box.hide()
            self.validating = False

    def _validate(self, entry: Gtk.Entry):
        text = entry.get_text()
        context = entry.get_style_context()
        error = self.find_errors_in_progress(text)

        if error is not None:
            self.valid = False
            self.warn = True
            self.set_warning_text(error)
            self._show_warning()
            context.add_class('error')
        else:
            self.valid = True
            self.warn = False
            self._hide_warning()
            context.remove_class('error')

    def _validate_completed(self, entry: Gtk.Entry, focus: Gdk.EventFocus):
        text = entry.get_text()
        context = entry.get_style_context()
        error = self.find_completed_errors(text)
        if error:
            context.add_class('error')
            self.set_warning_text(error)
            self._show_warning()
        else:
            self._hide_warning_slowly()
            context.remove_class('error')

    def find_errors_in_progress(self, text: str) -> Optional[str]:
        """Return a string describing any errors.
        Return None if there are no errors.

        This will be called as the user types.
        """
        raise NotImplementedError

    def find_completed_errors(self, text: str) -> Optional[str]:
        """return a string describing any errors.
        Return none if there are no errors.

        This will be called when the user has finished typing.
        """
        raise NotImplementedError


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
        text = text.strip()
        if text and not self.conv.timestring_to_seconds(text):
            return self._error_msg

    def set_value(self, seconds: float):
        self.entry.set_text(seconds_to_timestring(seconds,
                                                  fractions=FRACTIONS_ASCII))

    def get_value(self):
        return self.conv.timestring_to_seconds(self.entry.get_text())
