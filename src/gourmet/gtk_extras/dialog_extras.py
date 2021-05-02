import fnmatch
import os.path
import re
import traceback
import xml.sax.saxutils
from gettext import gettext as _
from pathlib import Path
from pkgutil import get_data
from typing import List, Optional

from gi.repository import GObject, Gtk, Pango
from gi.repository.GLib import UserDirectory, get_user_special_dir

from gourmet.gdebug import debug
from gourmet.image_utils import image_to_pixbuf, make_thumbnail

from . import optionTable

H_PADDING = 12
Y_PADDING = 12


class UserCancelledError(Exception):
    pass


def is_markup(s):
    try:
        Pango.parse_markup(s, '0')
        return True
    except:
        return False


class ModalDialog (Gtk.Dialog):
    def __init__(self, default=None, title="", okay=True, label=False,
                 sublabel=False, parent=None, cancel=True,
                 modal=True, expander=None):
        """Our basic class. We allow for a label. Possibly an expander
        with extra information, and a simple Okay button.  The
        expander is are only fancy option. It should be a list ['Name
        of expander', CONTENTS]. CONTENTS can be a string (to be put
        in a label), a widget (to be packed in the expander), or a
        list of strings and widgets to be packed in order."""
        self.widget_that_grabs_focus = None
        self.setup_dialog(title=title, parent=parent)
        self.connect('destroy', self.cancelcb)
        self.set_border_width(15)
        self.default = default
        self.ret = default
        self.responses = {Gtk.ResponseType.OK: self.okcb,
                          Gtk.ResponseType.CANCEL: self.cancelcb,
                          Gtk.ResponseType.NONE: self.cancelcb,
                          Gtk.ResponseType.CLOSE: self.cancelcb,
                          Gtk.ResponseType.DELETE_EVENT: self.cancelcb}
        if modal:
            self.set_modal(True)
        else:
            self.set_modal(False)
        if label:
            self.setup_label(label)
        if sublabel:
            self.setup_sublabel(sublabel)
        if expander:
            self.set_resizable(True)  # should users want to resize the dialog
            self.setup_expander(expander)
        self.setup_buttons(cancel, okay)
        self.vbox.set_vexpand(True)
        self.vbox.show_all()

    def setup_dialog(self, *args, **kwargs):
        Gtk.Dialog.__init__(self, *args, **kwargs)

    def setup_label(self, label: str):
        """Add Pango markup to label"""
        self.set_title(label)
        label = '<span weight="bold" size="larger">%s</span>' % label
        self.label = Gtk.Label(label=label)
        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.vbox.pack_start(self.label, expand=False, fill=False, padding=0)
        self.label.set_padding(H_PADDING, Y_PADDING)
        self.label.set_alignment(0, 0)
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.set_use_markup(True)
        self.label.show()

    def setup_sublabel(self, sublabel):
        self.sublabel = Gtk.Label(label=sublabel)
        self.sublabel.set_selectable(True)
        self.vbox.pack_start(self.sublabel, False, True, 0)
        self.sublabel.set_padding(H_PADDING, Y_PADDING)
        self.sublabel.set_alignment(0, 0)
        self.sublabel.set_justify(Gtk.Justification.LEFT)
        self.sublabel.set_use_markup(True)
        self.sublabel.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.sublabel.show()

    def setup_buttons(self, cancel, okay):
        if cancel:
            self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        if okay:
            self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.connect('response', self.response_cb)

    def response_cb(self, dialog, response, *params):
        # print 'response CB ',dialog,response,params
        if response in self.responses:
            # print 'we have a response!'
            self.responses[response]()
        else:
            print('WARNING, no response for ', response)

    def setup_expander(self, content: List[str]):
        _, body = content

        self.expander = Gtk.Expander()
        self.expander.set_use_underline(True)
        self.expander_vbox = Gtk.VBox()

        sw = Gtk.ScrolledWindow()
        sw.add_with_viewport(self.expander_vbox)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.set_min_content_height(150)
        self.expander.add(sw)

        self._add_expander_item(body)
        self.expander.show()
        self.expander_vbox.show_all()
        self.vbox.add(self.expander)

    def _add_expander_item(self, item):
        if isinstance(item, str):
            label = Gtk.Label(label=item)
            label.set_selectable(True)
            label.set_line_wrap_mode(Pango.WrapMode.WORD)
            self.expander_vbox.pack_start(label, False, False, 0)
        elif isinstance(item, (list, tuple)):
            list(map(self._add_expander_item, item))
        else:
            self.expander_vbox.pack_start(item, True, True, 0)

    def run(self):
        self.show()
        if self.widget_that_grabs_focus:
            self.widget_that_grabs_focus.grab_focus()
        if self.get_modal():
            Gtk.main()
        return self.ret

    def okcb(self, *args):
        self.hide()
        if self.get_modal():
            Gtk.main_quit()

    def cancelcb(self, *args):
        self.hide()
        self.ret = None
        if self.get_modal():
            Gtk.main_quit()


class MessageDialog(Gtk.MessageDialog, ModalDialog):
    """A simple class for displaying messages to our users."""

    def __init__(self, title="", default=None, okay=True, cancel=True,
                 label=False, sublabel=False, expander=None,
                 message_type=Gtk.MessageType.INFO, parent=None, modal=True):
        self.message_type = message_type
        ModalDialog.__init__(self, title=title, default=default, okay=okay,
                             cancel=cancel, label=label, sublabel=sublabel,
                             parent=parent, expander=expander, modal=modal)

    def setup_dialog(self, *args, **kwargs):
        kwargs['type'] = self.message_type
        title = kwargs.pop('title', None)
        super().__init__(self, *args, **kwargs)
        self.set_title(title)

    def setup_label(self, label: str):
        if not is_markup(label):
            label = xml.sax.saxutils.escape(label)
        label = f'<span weight="bold" size="larger">{label}</span>'
        self.set_markup(label)

    def setup_sublabel(self, sublabel: str):
        self.format_secondary_markup(sublabel)


class NumberDialog (ModalDialog):
    """A dialog to get a number from our user."""

    def __init__(self, default=None, label=False, sublabel=False, step_incr=1,
                 page_incr=10, digits=0, min=0, max=10000, parent=None):
        ModalDialog.__init__(self, default=default, parent=parent)
        self.hbox = Gtk.HBox()
        self.vbox.add(self.hbox)
        self.spinButton = Gtk.SpinButton()

        if not default:
            val = 0
        else:
            val = float(default)

        self.adjustment = Gtk.Adjustment(val,
                                         lower=min,
                                         upper=max,
                                         step_incr=step_incr,
                                         page_incr=page_incr)
        self.spinButton.set_adjustment(self.adjustment)

        if default:
            self.spinButton.set_value(default)
        if label:
            self.label = Gtk.Label(label=label)
            self.label.set_selectable(True)
            self.label.set_line_wrap_mode(Pango.WrapMode.WORD)
            self.label.set_padding(H_PADDING, Y_PADDING)
            self.hbox.add(self.label)
            self.label.show()
        self.hbox.add(self.spinButton)
        self.spinButton.get_adjustment().connect("value_changed",
                                                 self.update_value)
        self.spinButton.get_adjustment().connect("changed", self.update_value)
        self.spinButton.show()
        self.spinButton.connect('activate', self.entry_activate_cb)
        self.hbox.show()

    def update_value(self, *args):
        self.ret = self.spinButton.get_value()

    def entry_activate_cb(self, *args):
        self.okcb()


class EntryDialog (ModalDialog):

    """A dialog to get some text from an Entry from our user."""

    def __init__(self, default=None,
                 label=None,
                 sublabel=None,
                 entryLabel=False,
                 entryTip=None,
                 parent=None,
                 visibility=True,
                 default_value=None,
                 default_character_width=None):
        ModalDialog.__init__(self, default=default,
                             parent=parent, label=label, sublabel=sublabel)
        self.hbox = Gtk.HBox()
        self.vbox.add(self.hbox)
        if entryLabel:
            self.elabel = Gtk.Label(label=entryLabel)
            self.elabel.set_line_wrap_mode(Pango.WrapMode.WORD)
            self.elabel.set_selectable(True)
            self.elabel.set_alignment(0, 0)
            self.hbox.add(self.elabel)
            self.elabel.show()
            self.elabel.set_padding(H_PADDING, Y_PADDING)
        self.entry = Gtk.Entry()
        self.entry.set_visibility(visibility)
        self.entry.connect('activate', self.entry_activate_cb)
        if default_character_width:
            if hasattr(self.entry, 'set_width_chars'):
                self.entry.set_width_chars(default_character_width)
            if hasattr(self, 'label') and hasattr(self.label, 'set_width_chars'):
                self.label.set_width_chars(default_character_width)
            if hasattr(self, 'sublabel') and hasattr(self.sublabel, 'set_width_chars'):
                self.sublabel.set_width_chars(default_character_width)
        self.hbox.add(self.entry)
        self.entry.set_can_default(True)
        self.entry.grab_default()
        self.hbox.show()
        if default:
            self.entry.set_text(default)
        if entryTip:
            self.entry.set_tooltip_text(entryTip)
        self.entry.connect("changed", self.update_value)
        # Set the default value after connecting our handler so our
        # value gets updated!
        if default_value:
            self.entry.set_text(default_value)
        self.entry.show_all()
        self.entry.show()
        self.widget_that_grabs_focus = self.entry

    def update_value(self, *args):
        self.ret = self.entry.get_text()

    def entry_activate_cb(self, *args):
        if self.ret:
            self.okcb()


class RadioDialog (ModalDialog):

    """A dialog to offer our user a choice between a few options."""

    def __init__(self, default=None, label="Select Option", sublabel=None,
                 options=[], parent=None, expander=None, cancel=True):
        ModalDialog.__init__(self, okay=True, label=label, sublabel=sublabel,
                             parent=parent, expander=expander, cancel=cancel)
        # defaults value is first value...
        self.default = default
        self.setup_radio_buttons(options)
        if options and default is None:
            self.ret = options[0][1]

    def setup_radio_buttons(self, options):
        previous_radio = None
        self.buttons = []
        for label, value in options:
            rb = Gtk.RadioButton(group=previous_radio,
                                 label=label, use_underline=True)
            rb.connect('activate', self.okcb)
            self.vbox.add(rb)
            rb.show()
            rb.connect('toggled', self.toggle_cb, value)
            self.buttons.append(rb)
            previous_radio = rb
            if self.default == value:
                rb.set_active(True)
                self.widget_that_grabs_focus = rb
        if self.default is None:
            self.buttons[0].set_active(True)
            self.widget_that_grabs_focus = self.buttons[0]

    def toggle_cb(self, widget, value):
        if widget.get_active():
            self.ret = value


class OptionDialog(ModalDialog):
    """Offer users a choice between options using an option menu"""

    def __init__(self, default=None, label="Select Option", sublabel=None,
                 options=[], parent=None, expander=None, cancel=True):
        """Options can be a simple option or can be a tuple or a list
        where the first item is the label and the second the value"""
        ModalDialog.__init__(self, okay=True, label=label, sublabel=sublabel,
                             parent=parent, expander=expander, cancel=cancel)

        self.combobox = Gtk.ComboBoxText()
        self.vbox.pack_start(
            self.combobox, expand=False, fill=False, padding=0
        )
        self.option_values = []
        for o in options:
            if isinstance(o, str):
                label = value = o
            else:
                label, value = o
            self.combobox.append_text(label)
            self.option_values.append(value)

        # set the default value to the first item
        self.ret = self.option_values[0]
        self.combobox.connect('changed', self.get_option)
        self.combobox.set_active(0)
        self.combobox.show()

    def get_option(self, widget):
        self.ret = self.option_values[self.combobox.get_active()]
        # return self.ret

    def set_value(self, value):
        self.ret = value


class ProgressDialog (ModalDialog):
    """A dialog to show a progress bar"""

    def __init__(self, title="", okay=True, label="", sublabel=False,
                 parent=None, cancel=False, stop=False, pause=False,
                 modal=False):
        # stop, cancel, and pause are set as callbacks to their buttons
        self.custom_pausecb = pause
        self.custom_cancelcb = cancel
        self.custom_pause_handlers = []
        self.custom_stop_handlers = []
        self.custom_stopcb = stop
        ModalDialog.__init__(self, title, okay=okay, label=label,
                             sublabel=sublabel, parent=parent,
                             cancel=cancel, modal=modal)
        self.set_title(label)
        self.progress_bar = Gtk.ProgressBar()
        self.vbox.add(self.progress_bar)
        self.detail_label = Gtk.Label()
        self.vbox.add(self.detail_label)
        self.detail_label.set_use_markup(True)
        self.detail_label.set_padding(H_PADDING, Y_PADDING)
        self.detail_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.vbox.show_all()
        if okay:
            # we're false by default!
            self.set_response_sensitive(Gtk.ResponseType.OK, False)
        if not stop:
            self.stop.hide()
        if not pause:
            self.pause.hide()

    def reset_label(self, label):
        self.set_title(label)
        self.label.set_text(
            '<span weight="bold" size="larger">%s</span>' % label)
        self.label.set_use_markup(True)

    def reassign_buttons(self, pausecb=None, stopcb=None):
        debug('reassign_buttons called with pausecb=%s, stopcb=%s' %
              (pausecb, stopcb), 1)
        while self.custom_pause_handlers:
            h = self.custom_pause_handlers.pop()
            if self.pause.handler_is_connected(h):
                self.pause.disconnect(h)
        if pausecb:
            self.pause.connect('toggled', pausecb)
            self.pause.set_property('visible', True)
        else:
            self.pause.set_property('visible', False)
        while self.custom_stop_handlers:
            h = self.custom_stop_handlers.pop()
            if self.stop.handler_is_connected(h):
                self.stop.disconnect(h)
        if stopcb:
            self.stop.connect('clicked', stopcb)
            # self.stop.connect('clicked',self.cancelcb)
            self.stop.set_property('visible', True)
        else:
            self.stop.set_property('visible', False)

    def setup_buttons(self, cancel, okay):
        # setup pause button
        self.pause = Gtk.ToggleButton(_('_Pause'))
        self.pause.set_use_underline(True)
        self.action_area.pack_end(self.pause, True, True, 0)
        # only show it/connect it if we want to...
        if self.custom_pausecb:
            # we keep a list of handlers for possible disconnection later
            self.custom_pause_handlers.append(
                self.pause.connect('toggled', self.custom_pausecb))
            self.pause.set_property('visible', True)
        else:
            self.pause.set_property('visible', False)
            self.pause.hide()
        # setup stop button
        self.stop = Gtk.Button(_('_Stop'))
        self.action_area.pack_end(self.stop, True, True, 0)
        if self.custom_stopcb:
            self.stop.set_property('visible', True)
            # we keep a list of handlers for possible disconnection later
            self.custom_stop_handlers.append(
                self.stop.connect('clicked', self.custom_stopcb))
            # self.custom_stop_handlers.append(self.stop.connect('clicked',self.cancelcb))
        else:
            self.stop.set_property('visible', False)
            self.stop.hide()
        ModalDialog.setup_buttons(self, cancel, okay)
        if self.custom_cancelcb:
            self.cancelcb = self.custom_cancelcb
            # self.cancel.connect('clicked',self.custom_cancelcb)

    def set_progress(self, prog, message=None):
        if prog < 0:
            self.progress_bar.pulse()
        else:
            self.progress_bar.set_fraction(prog)
        if message:
            self.progress_bar.set_text(message)
        if prog == 1:
            self.set_response_sensitive(Gtk.ResponseType.OK, True)


class PreferencesDialog(ModalDialog):
    """Get user preferences as a list."""

    def __init__(self, options=([None, None]), option_label="Option",
                 value_label="Value", default=True, label=None, sublabel=False,
                 apply_func=None, parent=None, dont_ask_cb=None,
                 dont_ask_custom_text=None):
        """Options is a tuple of tuples where each tuple is ('option', VALUE),
        handed to OptionTable

        VALUE can be any of the following:
        a string (will be editable)
        a number (will be editable and returned as a number)
        true or false (will be a checkbox)

        If apply_func is True, we will have an apply button, which
        will hand the option tuple as its argument. Otherwise, okay will simply
        return the list on okay."""
        if apply_func:
            modal = False
        else:
            modal = True
        self.apply_func = apply_func
        self.options = options
        ModalDialog.__init__(self, okay=True, label=label,
                             sublabel=sublabel, parent=parent, modal=modal)
        self.table = optionTable.OptionTable(options=self.options,
                                             option_label=option_label,
                                             value_label=value_label,
                                             changedcb=self.changedcb)
        for widget_info in self.table.widgets:
            widget = widget_info[0]
            # Activating any widget activates the dialog...
            try:
                widget.connect('activate', self.okcb)
            except TypeError:
                # not all widgets have a signal -- no biggy
                pass
        self.hbox = Gtk.HBox()
        self.hbox.show()
        self.hbox.add(self.table)
        self.vbox.add(self.hbox)
        if dont_ask_cb:
            if not dont_ask_custom_text:
                dont_ask_custom_text = _("Don't ask me this again.")
            self.dont_ask = Gtk.CheckButton(dont_ask_custom_text)
            self.dont_ask.connect('toggled', dont_ask_cb)
            self.vbox.add(self.dont_ask)
        self.vbox.show_all()

    def setup_buttons(self, cancel, okay):
        if self.apply_func:
            self.revert = Gtk.Button(stock=Gtk.STOCK_REVERT_TO_SAVED)
            self.revert.connect('clicked', self.revertcb)
            self.action_area.add(self.revert)
            self.apply = Gtk.Button(stock=Gtk.STOCK_APPLY)
            self.apply.set_sensitive(False)
            self.apply.connect('clicked', self.applycb)
            self.action_area.add(self.apply)
            self.apply.show()
            self.changedcb = lambda *args: self.apply.set_sensitive(True)
        else:
            self.changedcb = None
            self.set_modal(False)
        ModalDialog.setup_buttons(self, cancel, okay)

    def revertcb(self, *args):
        self.table.revert()

    def applycb(self, *args):
        self.table.apply()
        self.apply_func(self.table.options)
        self.apply.set_sensitive(False)

    def run(self):
        self.show()
        if self.apply_func:
            return
        else:
            Gtk.main()
            return self.ret

    def okcb(self, *args):
        if self.apply_func:
            if self.apply.get_property('sensitive'):
                # if there are unsaved changes...
                if getBoolean(label="Would you like to apply the changes you've made?"):
                    self.applycb()
            self.hide()
        else:
            self.table.apply()
            self.ret = self.table.options
            self.hide()
            Gtk.main_quit()

    def cancelcb(self, *args):
        self.hide()
        self.ret = None


class BooleanDialog (MessageDialog):
    def __init__(self, title="", default=True, label=_("Do you really want to do this"),
                 sublabel=False, cancel=True,
                 parent=None, custom_yes=None, custom_no=None, expander=None,
                 dont_ask_cb=None, dont_ask_custom_text=None,
                 cancel_returns=None, message_type=Gtk.MessageType.QUESTION
                 ):
        """Setup a BooleanDialog which returns True or False.
        parent is our parent window.
        custom_yes is custom text for the button that returns true or a dictionary
                   to be handed to Gtk.Button as keyword args.
        custom_no is custom text for the button that returns False or a dictionary
                   to be handed to Gtk.Button as keyword args
        expander is a list whose first item is a label and second is a widget to be packed
        into an expander widget with more information.
        if dont_ask_variable is set, a Don't ask me again check
        button will be displayed which the user can check to avoid this kind
        of question again. (NOTE: if dont_ask_variable==None, this won't work!)
        dont_ask_custom_text is custom don't ask text."""
        self.cancel_returns = cancel_returns
        self.yes, self.no = custom_yes, custom_no
        if not self.yes:
            self.yes = Gtk.STOCK_YES
        if not self.no:
            self.no = Gtk.STOCK_NO
        MessageDialog.__init__(self, title=title, okay=False, label=label, cancel=cancel,
                               sublabel=sublabel, parent=parent, expander=expander, message_type=message_type)
        self.responses[Gtk.ResponseType.YES] = self.yescb
        self.responses[Gtk.ResponseType.NO] = self.nocb
        if not cancel:
            # if there's no cancel, all cancel-like actions
            # are the equivalent of a NO response
            self.responses[Gtk.ResponseType.NONE] = self.nocb
            self.responses[Gtk.ResponseType.CANCEL] = self.nocb
            self.responses[Gtk.ResponseType.CLOSE] = self.nocb
            self.responses[Gtk.ResponseType.DELETE_EVENT] = self.nocb
        if dont_ask_cb:
            if not dont_ask_custom_text:
                dont_ask_custom_text = _("Don't ask me this again.")
            self.dont_ask = Gtk.CheckButton(dont_ask_custom_text)
            self.dont_ask.connect('toggled', dont_ask_cb)
            self.vbox.add(self.dont_ask)
            self.dont_ask.show()

    def setup_buttons(self, *args, **kwargs):
        MessageDialog.setup_buttons(self, *args, **kwargs)
        self.add_button((self.no or Gtk.STOCK_NO), Gtk.ResponseType.NO)
        self.add_button((self.yes or Gtk.STOCK_YES), Gtk.ResponseType.YES)

    def yescb(self, *args):
        self.ret = True
        self.okcb()

    def cancelcb(self, *args):
        if self.cancel_returns is not None:
            self.ret = self.cancel_returns
        self.okcb()

    def nocb(self, *args):
        self.ret = False
        self.okcb()


class SimpleFaqDialog (ModalDialog):
    """A dialog to view a plain old text FAQ in an attractive way"""

    INDEX_MATCHER = re.compile("^[0-9]+[.][A-Za-z0-9.]* .*")

    # We except one level of nesting in our headers.
    # NESTED_MATCHER should match nested headers
    NESTED_MATCHER = re.compile("^[0-9]+[.][A-Za-z0-9.]+ .*")

    def __init__(self,
                 title="Frequently Asked Questions",
                 jump_to=None,
                 parent=None,
                 modal=True):
        # print faq_file
        ModalDialog.__init__(
            self, title=title, parent=parent, modal=modal, cancel=False)
        self.set_default_size(950, 500)
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_left_margin(18)
        self.textview.set_right_margin(18)
        self.textbuf = self.textview.get_buffer()
        self.boldtag = self.textbuf.create_tag()
        self.boldtag.set_property('weight', Pango.Weight.BOLD)
        self.textwin = Gtk.ScrolledWindow()
        self.textwin.set_policy(Gtk.PolicyType.AUTOMATIC,
                                Gtk.PolicyType.AUTOMATIC)
        self.textwin.add(self.textview)

        self.index_lines = []
        self.index_dic = {}
        self.text = ""

        self.parse_faq()
        if self.index_lines:
            self.paned = Gtk.Paned()
            self.indexView = Gtk.TreeView()
            self.indexWin = Gtk.ScrolledWindow()
            self.indexWin.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            self.indexWin.add(self.indexView)
            self.setup_index()
            self.paned.add1(self.indexWin)
            self.paned.add2(self.textwin)
            self.vbox.add(self.paned)
            self.vbox.show_all()
            self.paned.set_position(325)
            self.paned.set_vexpand(True)
        else:
            self.vbox.add(self.textwin)
            self.vbox.show_all()
        if jump_to:
            self.jump_to_header(jump_to)

    def jump_to_header(self, text):
        """Jump to the header/index items that contains text.
        """
        text = text.lower()
        for line in self.index_lines:
            if line.lower().find(text) > 0:
                itr = self.index_iter_dic[line]
                # select our iter...
                # as a side effect, we will jump to the right part of the text
                self.indexView.get_selection().select_iter(itr)
                # expand our iter
                mod = self.indexView.get_model()
                self.indexView.expand_row(mod.get_path(itr), True)
                return

    def parse_faq(self) -> None:
        """Parse the FAQ for display."""

        # Clear data
        self.index_lines = []
        self.index_dic = {}
        self.text = ""

        faq = get_data('gourmet', 'data/FAQ').decode()
        assert faq
        for l in faq.split('\n'):
            line = l.strip()
            if self.INDEX_MATCHER.match(line):  # it is a heading
                self.index_lines.append(line)
                curiter = self.textbuf.get_iter_at_mark(
                    self.textbuf.get_insert())
                self.index_dic[line] = self.textbuf.create_mark(None,
                                                                curiter,
                                                                left_gravity=True)
                self.textbuf.insert_with_tags(curiter,
                                              line + " ",
                                              self.boldtag)
            elif line:  # it is body content
                self.textbuf.insert_at_cursor(line + " ")
            else:  # an empty line is a paragraph break
                self.textbuf.insert_at_cursor("\n\n")

    def setup_index(self):
        """Set up a clickable index view"""
        self.imodel = Gtk.TreeStore(str)
        self.index_iter_dic = {}
        last_parent = None
        for line in self.index_lines:
            if self.NESTED_MATCHER.match(line):
                itr = self.imodel.append(last_parent, [line])
            else:
                itr = self.imodel.append(None, [line])
                last_parent = itr
            self.index_iter_dic[line] = itr
        # setup our lone column
        self.indexView.append_column(
            Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=0)
        )
        self.indexView.set_model(self.imodel)
        self.indexView.set_headers_visible(False)
        self.indexView.connect('row-activated', self.index_activated_cb)
        self.indexView.get_selection().connect('changed',
                                               self.index_selected_cb)

    def index_activated_cb(self, *args):
        """Toggle expanded state of rows."""
        mod, itr = self.indexView.get_selection().get_selected()
        path = mod.get_path(itr)
        if self.indexView.row_expanded(path):
            self.indexView.collapse_row(path)
        else:
            self.indexView.expand_row(path, True)

    def index_selected_cb(self, *args):
        mod, itr = self.indexView.get_selection().get_selected()
        val = self.indexView.get_model().get_value(itr, 0)
        self.textview.scroll_to_mark(mark=self.index_dic[val],
                                     within_margin=0.1,
                                     use_align=True,
                                     xalign=0.5,
                                     yalign=0.0)

    def jump_to_text(self, txt, itr=None):
        if not itr:
            itr = self.textbuf.get_iter_at_offset(0)
        match_start, match_end = itr.forward_search(
            txt, Gtk.TextSearchFlags.VISIBLE_ONLY)
        self.textview.scroll_to_iter(
            match_start, False, use_align=True, yalign=0.1)


class RatingsConversionDialog (ModalDialog):
    """A dialog to allow the user to select the number of stars
    distinct ratings should convert to.

    This dialog exists to aid conversion of ratings from old gourmet
    exports or databases or from other imports that use strings of
    some kind ('great','groovy',etc.) to aid in conversion.
    """

    def __init__(self,
                 strings,
                 star_generator,
                 defaults={_("excellent"): 10,
                           _("great"): 8,
                           _("good"): 6,
                           _("fair"): 4,
                           _("poor"): 2, },
                 parent=None,
                 modal=True):
        """strings is a list of strings that are currently used for ratings.

        The user will be asked to give the star equivalent of each string.
        """
        self.strings = strings
        self.star_generator = star_generator
        self.defaults = defaults
        ModalDialog.__init__(
            self,
            title=_("Convert ratings to 5 star scale."),
            label=_("Convert ratings."),
            sublabel=_(
                "Please give each of the ratings an equivalent on a scale of 1 to 5"),
            parent=parent,
            modal=modal
        )
        self.set_default_size(750, 500)
        self.ret = {}
        self.setup_tree()

    def setup_tree(self):
        self.tv = Gtk.TreeView()
        self.setup_model()
        self.tv.set_model(self.tm)
        from .ratingWidget import TreeWithStarMaker
        textcol = Gtk.TreeViewColumn(
            _('Current Rating'), Gtk.CellRendererText(), text=0)
        textcol.set_sort_column_id(0)
        self.tv.append_column(textcol)
        TreeWithStarMaker(self.tv,
                          self.star_generator,
                          col_title=_("Rating out of 5 Stars"),
                          col_position=-1,
                          data_col=1,
                          handlers=[self.ratings_change_cb],
                          )
        self.sw = Gtk.ScrolledWindow()
        self.sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.sw.add(self.tv)
        self.vbox.add(self.sw)
        self.sw.show_all()

    def setup_model(self):
        self.tm = Gtk.ListStore(str, int)
        for s in self.strings:
            val = self.defaults.get(s.lower(), 0)
            self.tm.append([s, val])
            self.ret[s] = val

    def ratings_change_cb(self, value, model, treeiter, colnum):
        string = model.get_value(treeiter, 0)
        self.ret[string] = value
        model.set_value(treeiter, colnum, value)


def show_traceback(label: str = "Error", sublabel: Optional[str] = None):
    """Show an error dialog with a traceback viewable."""
    error_mess = traceback.format_exc()
    show_message(label=label,
                 sublabel=sublabel,
                 expander=(_("_Details"), error_mess),
                 message_type=Gtk.MessageType.ERROR)


def show_message(*args, **kwargs):
    """Show a message dialog.
    Args and Kwargs are handed to MessageDialog
    We most likely want to hand it label= and sublabel=
    """
    # if not kwargs.has_key(message_type):
    #    message_type=Gtk.MessageType.INFO
    if 'cancel' not in kwargs:
        kwargs['cancel'] = False
    d = MessageDialog(*args, **kwargs)
    d.run()
    return d


def select_file(title,
                filename=None,
                filters=[],
                # filters are lists of a name, a list of mime types and a list of
                # patterns ['Plain Text', ['text/plain'], '*txt']
                action=Gtk.FileChooserAction.OPEN,
                set_filter=True,
                select_multiple=False,
                buttons=None,
                parent=None
                ):
    sfd = FileSelectorDialog(title,
                             filename=filename,
                             filters=filters,
                             select_multiple=select_multiple,
                             action=action,
                             set_filter=set_filter,
                             buttons=buttons, parent=parent)
    return sfd.run()


def saveas_file(title: str,
                filename: Optional[str] = None,
                filters: Optional[List[str]] = None,
                action: Gtk.FileChooserAction = Gtk.FileChooserAction.SAVE,
                set_filter: bool = True,
                buttons: List[Gtk.FileChooserButtonClass] = None,
                parent: Gtk.Window = None,
                show_filetype: bool = True):
    """Almost identical to select_file, except that we return a tuple containing
    the filename and the export type (the string the user selected)"""
    sfd = FileSelectorDialog(title,
                             filename=filename,
                             filters=filters,
                             action=action,
                             set_filter=set_filter,
                             buttons=buttons,
                             show_filetype=show_filetype,
                             parent=parent)
    filename = sfd.run()
    if not filename:
        return None, None
    filename, *_ = filename

    exp_type = get_type_for_filters(filename, filters[:])
    if not exp_type:
        # If we don't have a type based on our regexps... then lets
        # just see what the combobox was set to...
        exp_type = filters[sfd.saveas.get_active()][0]
    return filename, exp_type


def get_type_for_filters(fname, filters):
    base, ext = os.path.splitext(fname)
    exp_type = None
    while filters and not exp_type:
        name, mime, rgxps = filters.pop()
        for r in rgxps:
            if os.path.splitext(r)[1] == ext:
                exp_type = name
    return exp_type


def select_image(title,
                 filename=None,
                 action=Gtk.FileChooserAction.OPEN,
                 buttons=None):
    sfd = ImageSelectorDialog(title, filename=filename,
                              action=action, buttons=buttons)
    return sfd.run()


class FileSelectorDialog:
    """A dialog to ask the user for a file. We provide a few custom additions to the
    standard file dialog, including a special choose-filetype menu and including dynamic update
    of the filetype based on user input of an extension"""

    def __init__(self,
                 title,
                 filename=None,
                 filters=[],
                 # filters are lists of a name, a list of mime types and a list of
                 # patterns ['Plain Text', ['text/plain'], '*txt']
                 action=Gtk.FileChooserAction.SAVE,
                 set_filter=True,
                 buttons=None,
                 show_filetype=True,
                 parent=None,
                 select_multiple=False
                 ):
        self.parent = parent
        self.buttons = buttons
        self.multiple = select_multiple
        self.set_filter = set_filter
        self.action = action
        self.filename = filename
        self.title = title
        self.filters = filters
        self.show_filetype = show_filetype
        self.setup_dialog()
        self.post_dialog()

    def post_dialog(self):
        """Run after the dialog is set up (to allow subclasses to do further setup)"""
        pass

    def setup_dialog(self):
        """Create our dialog"""
        self.setup_buttons()
        self.fsd = Gtk.FileChooserDialog(self.title,
                                         action=self.action,
                                         parent=self.parent,
                                         buttons=self.buttons)
        self.fsd.set_default_response(Gtk.ResponseType.OK)
        self.fsd.set_select_multiple(self.multiple)
        self.fsd.set_do_overwrite_confirmation(True)
        if self.filename:
            path, name = os.path.split(os.path.expanduser(self.filename))
            if path:
                self.fsd.set_current_folder(path)
            if name:
                self.fsd.set_current_name(name)
        self.setup_filters()
        if self.action == Gtk.FileChooserAction.SAVE:
            self.setup_saveas_widget()

    def setup_buttons(self):
        """Set our self.buttons attribute"""
        if not self.buttons:
            if self.action == Gtk.FileChooserAction.OPEN or self.action == Gtk.FileChooserAction.SELECT_FOLDER:
                self.buttons = (
                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            else:
                self.buttons = (
                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)

    def setup_filters(self):
        """Create and set filters for the dialog."""
        self.extensions = []
        for fil in self.filters:
            filter = Gtk.FileFilter()
            filter_name, filter_mime_types, filter_patterns = fil
            filter.set_name(filter_name)
            if filter_mime_types:
                for f in filter_mime_types:
                    filter.add_mime_type(f)
            if filter_patterns:
                for f in filter_patterns:
                    filter.add_pattern(f)
                    self.extensions.append(f)
            self.fsd.add_filter(filter)
        if self.set_filter and self.filters:
            self.fsd.set_filter(self.fsd.list_filters()[0])

    def setup_saveas_widget(self):
        """Set up the filter widget."""
        if not self.filters:
            self.do_saveas = False
            return
        self.do_saveas = True
        n = 0
        self.ext_to_filter = {}
        self.name_to_ext = {}
        for name, mimetypes, regexps in self.filters:
            # name_to_ext lets us grab the correct extension from our active iter
            self.name_to_ext[name] = os.path.splitext(regexps[0])[-1]
            for r in regexps:
                ext = os.path.splitext(r)[-1]
                # ext_to_filter let's us select the correct iter from the extension typed in
                self.ext_to_filter[ext] = self.fsd.list_filters()[n]
            n += 1

        self.fn = None
        self.fsd.connect('notify::filter', self.change_file_extension)
        self.fsd.connect('selection-changed', self.update_filetype_widget)
        self.internal_extension_change = False
        self.update_filetype_widget()
        # and now for a hack -- since we can't connect to the Entry widget,
        # we're going to simply check to see if the filename has changed with
        # an idle call.
        self.timeout = GObject.timeout_add(100, self.update_filetype_widget)

    def update_filetype_widget(self, *args):
        fn = self.fsd.get_filename()
        if self.fn != fn:
            self.fn = fn
            if not fn:
                return True
            ext = os.path.splitext(fn)[1]
            if ext in self.ext_to_filter:
                self.internal_extension_change = True
                self.fsd.set_filter(self.ext_to_filter[ext])
                self.internal_extension_change = False
        return True

    def change_file_extension(self, fsd, data: GObject.GParamSpec):
        if self.internal_extension_change:
            return
        filename = Path(self.fsd.get_filename())
        stem = filename.stem
        ext = self.name_to_ext[fsd.get_filter().get_name()]
        if self.show_filetype:
            self.fsd.set_current_name(stem + ext)
        else:
            self.fsd.set_current_name(stem)

    def is_extension_legal(self, filenames: List[str]) -> bool:
        if filenames:
            for extension in self.extensions:
                if not extension:
                    extension = ""
                if fnmatch.fnmatch(filenames[0], extension):
                    return True
        return False

    def run(self) -> List[str]:
        """Run our dialog and return the filename(s)"""
        response = self.fsd.run()
        if response == Gtk.ResponseType.OK:
            if self.multiple:
                fn = self.fsd.get_filenames()
            else:
                fn = [self.fsd.get_filename()]
            if not fn:
                show_message(label=_('No file selected'),
                             sublabel=_(
                                 'No file was selected, so the action has been cancelled')
                             )
                return []
            if self.action == Gtk.FileChooserAction.SAVE:
                # add the extension if need be...
                if self.do_saveas and not self.is_extension_legal(fn):
                    if self.fsd.get_filter().get_name() in self.name_to_ext:
                        add_ext = self.name_to_ext[self.fsd.get_filter(
                        ).get_name()]
                        if add_ext:
                            fn += add_ext
            self.quit()
            return fn
        else:
            self.quit()
            return []

    def quit(self, *args):
        if hasattr(self, 'timeout'):
            GObject.source_remove(self.timeout)
        self.fsd.destroy()


class ImageSelectorDialog (FileSelectorDialog):
    IMAGE_FILTERS = [
        ['Image',
         ['image/jpeg', 'image/png', 'image/tiff',
          'image/bmp', 'image/cgf', ],
         ['*.jpeg', '*.jpg', 'gif', 'bmp', 'png',
          '*.JPEG', '*.JPG', 'GIF', 'BMP', 'PNG']
         ],
        ['Jpeg Image', ['image/jpeg'], ['*.jpeg', '*.jpg', '*.JPG', '*.JPEG']],
        ['PNG Image', ['image/png'], ['*.png', '*.PNG']],
        ['Bmp Image', ['image/bmp'], ['*.bmp', '*.BMP']],
        ['CGF Image', ['image/cgf'], ['*.cgf', '*.CFG']],
        ['Tiff Image', ['image/tiff'], ['*.tiff', '*.TIFF']]
    ]

    def __init__(self,
                 title,
                 filename=None,
                 filters=IMAGE_FILTERS,
                 action=Gtk.FileChooserAction.OPEN,
                 set_filter=True,
                 buttons=None
                 ):
        FileSelectorDialog.__init__(
            self, title, filename, filters, action, set_filter, buttons)
        pictures_dir = get_user_special_dir(UserDirectory.DIRECTORY_PICTURES)
        if pictures_dir is not None:
            self.fsd.set_current_folder(pictures_dir)

    def post_dialog(self):
        self.preview = Gtk.Image()
        self.fsd.set_preview_widget(self.preview)
        self.fsd.connect('selection-changed', self.update_preview)
        self.preview.show()

    def update_preview(self, *args):
        uri = self.fsd.get_uri()
        thumbnail = None
        if uri is not None:
            thumbnail = make_thumbnail(uri)

        if thumbnail is not None:
            self.preview.set_from_pixbuf(image_to_pixbuf(thumbnail))
            self.preview.show()
        else:
            self.preview.hide()


def getNumber(*args, **kwargs):
    """Run NumberDialog, passing along all args, waiting on input and passing along
    the results."""
    d = NumberDialog(*args, **kwargs)
    return d.run()


def getEntry(*args, **kwargs):
    """Run EntryDialog, passing along all args, waiting on input and passing along
    the results."""
    d = EntryDialog(*args, **kwargs)
    return d.run()


def getBoolean(*args, **kwargs) -> bool:
    """Run BooleanDialog, passing along all args, waiting on input and
    passing along the results."""
    d = BooleanDialog(*args, **kwargs)
    retval = d.run()
    if retval is None:
        retval = False
    return retval


def getOption(*args, **kwargs):
    d = OptionDialog(*args, **kwargs)
    return d.run()


def getRadio(*args, **kwargs):
    d = RadioDialog(*args, **kwargs)
    return d.run()


def show_faq(*args, **kwargs):
    d = SimpleFaqDialog(*args, **kwargs)
    return d.run()


def get_ratings_conversion(*args, **kwargs):
    d = RatingsConversionDialog(*args, **kwargs)
    return d.run()


def show_amount_error(txt):
    """Show an error that explains how numeric amounts work."""
    show_message(label=_("""I'm sorry, I can't understand
the amount "%s".""") % txt,
                 sublabel=_(
                     "Amounts must be numbers (fractions or decimals), ranges of numbers, or blank."),
                 expander=[_("_Details"),
                           _("""
The "unit" must be in the "unit" field by itself.
For example, if you want to enter one and a half cups,
the amount field could contain "1.5" or "1 1/2". "cups"
should go in the separate "unit" field.

To enter a range of numbers, use a "-" to separate them.
For example, you could enter 2-4 or 1 1/2 - 3 1/2.
""")])


def getUsernameAndPassword(username='', pw='', label='Enter password', sublabel=False):
    pd = PreferencesDialog(
        label=label, sublabel=sublabel,
        value_label=False, option_label=False,
        options=[[_('Username'), username], [_('Password'), pw]]
    )
    pd.table.widgets[1][0].set_visibility(False)  # Hide password :-)
    pd.run()
    return pd.options[0][1], pd.options[1][1]


if __name__ == '__main__':
    print('Got', saveas_file('Saveas'))
    w = Gtk.Window()
    w.connect('delete_event', Gtk.main_quit)
    b = Gtk.Button("show dialog (modal)")
    opts = (["Toggle Option", True],
            ["String Option", "Hello"],
            ["Integer Option", 1],
            ["Float Option", float(3)],
            ["Option Option", ("B", ["A", "B", "C"])],
            )
    pd = PreferencesDialog(options=opts)

    def run_prefs(*args):
        pd.run()
    b.connect('clicked', run_prefs)

    def show_options(options):
        print(options)
    b2 = Gtk.Button("show dialog (not modal)")
    vb = Gtk.VBox()

    def msg(*args):
        for a in args:
            print(a)
    char_measure = ""
    for n in range(10):
        char_measure = "%s %s" % (char_measure, n)
    char_measure = char_measure * 50
    from .ratingWidget import StarGenerator
    for s, f in [
            ['show dialog (modal)', run_prefs],
            ['show ratings dialog', lambda *args: get_ratings_conversion(['Good', 'Great', 'So so', 'Hot shit'],
                                                                         StarGenerator(),
                                                                         )],
            ['show dialog (not modal)', lambda *args: PreferencesDialog(
                options=opts, apply_func=show_options).show()],
            ['show FAQ', lambda *args: show_faq(parent=w, jump_to='shopping')],
            ['show message', lambda *args: show_message('howdy', label='Hello there. This is a very long label for the top of a dialog.',
                                                        sublabel='And this is a sub message.', message_type=Gtk.MessageType.WARNING)],
            ['get entry', lambda *args: getEntry(
                label='Main label', sublabel='sublabel', entryLabel='Entry Label: ')],
            ['get number',
                lambda *args: getNumber(label='Main label', sublabel='sublabel')],
            ['get long entry', lambda *args: getEntry(label='Main label', sublabel=char_measure,
                                                      entryLabel='Entry Label: ', default_character_width=75, entryTip='Enter something long here.')],
            ['show boolean', lambda *args: getBoolean()],
            ['get password', lambda *args: getUsernameAndPassword()],
            ['show custom boolean', lambda *args: getBoolean(custom_yes='_Replace',
                                                             custom_no=Gtk.STOCK_CANCEL,
                                                             cancel=False
                                                             )],
            ['show radio dialog', lambda *args: getRadio(label='Main label',
                                                         sublabel='sublabel'*10, default=2,
                                                         options=[('First', 1),
                                                                  ('Second', 2),
                                                                  ('Third', 3)]), ],
            ['get image dialog',
                lambda *args: msg(select_image('Select Image'))],
            ['get file dialog', lambda *args: msg(select_file('Select File',
                                                              filters=[['Plain Text', ['text/plain'], ['*.txt', '*.TXT']],
                                                                       ['PDF', [
                                                                           'application/pdf'], ['*.pdf', '*.PDF']],
                                                                       ['Postscript', [
                                                                           'application/postscript'], ['*.ps', '*.PS']],
                                                                       ['Web Page (HTML)', [
                                                                           'text/html'], ['*.htm', '*.HTM', '*.html', '*.HTML']],
                                                                       ['Mealmaster File', ['text/mmf'], ['*.mmf', '*.MMF']]],
                                                              select_multiple=True
                                                              )),
             ],
            ['save file with types',
             lambda *args: msg(saveas_file('export', filename='/tmp/test.mmf',
                                           filters=[['Plain Text', ['text/plain'], ['*.txt', '*.TXT']],
                                                    ['PDF', ['application/pdf'],
                                                     ['*.pdf', '*.PDF']],
                                                    ['Postscript', [
                                                        'application/postscript'], ['*.ps', '*.PS']],
                                                    ['Web Page (HTML)', [
                                                        'text/html'], ['*.htm', '*.HTM', '*.html', '*.HTML']],
                                                    ['Mealmaster File', ['text/mmf'], ['*.mmf', '*.MMF']]]))],
    ]:
        print(b, f, s)
        b = Gtk.Button(s)

        def wrap(f):
            def _(*args, **kwargs):
                print('Doing ', f)
                print('f returns:', f())
                print('Done')
            return _
        b.connect('clicked', wrap(f))
        vb.add(b)
    w.add(vb)
    vb.show_all()
    w.show_all()
    Gtk.main()
