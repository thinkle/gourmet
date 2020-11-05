import os as _os
import time
import xml.sax.saxutils
from gettext import gettext as _
from pkgutil import get_data as _get_data
from tempfile import mkstemp as _mkstemp
from typing import Callable, List, Optional

from gi.repository import GLib, Gtk

from gourmet.gtk_extras import cb_extras as cb
from gourmet.gtk_extras.dialog_extras import UserCancelledError, getBoolean
from gourmet.sound import Player


class TimeSpinnerUI:

    def __init__(self,
                 hoursSpin: Gtk.SpinButton,
                 minutesSpin: Gtk.SpinButton,
                 secondsSpin: Gtk.SpinButton):
        self.timer_hooks: List[Callable] = []  # actions rand when timer over
        self.is_running: bool = False  # State flag
        self.previous_iter_time: Optional[float] = None  # time, used for ticks
        self.remaining: Optional[float] = None  # time left when timer active
        self.orig_time: int = 0  # in seconds, user input time

        self.hoursSpin: Gtk.SpinButton = hoursSpin
        self.minutesSpin: Gtk.SpinButton = minutesSpin
        self.secondsSpin: Gtk.SpinButton = secondsSpin

        for spinner in (self.hoursSpin, self.minutesSpin, self.secondsSpin):
            # This is set up to assure 2 digit entries... 00:00:00, etc.
            spinner.connect('changed', self.val_changed_cb)
            spinner.val_change_is_changing_entry = False
            spinner.set_width_chars(2)

    def set_time(self, val: float) -> None:
        """Update the spinners on tick.

        Ran on every tick, the value, epoch stamp style, is split into hours,
        minutes, and seconds, and their respective spinner are set, to show
        time going down.
        """
        val = max(0., val)
        self.hoursSpin.set_value(val // 3600)
        val = val % 3600
        self.minutesSpin.set_value(val // 60)
        self.secondsSpin.set_value(val % 60)

    def get_time(self) -> int:
        """Get the time to run the timer for, in seconds"""
        return (self.hoursSpin.get_value() * 3600 +
                self.minutesSpin.get_value() * 60 +
                self.secondsSpin.get_value())

    def val_changed_cb(self, widg: Gtk.SpinButton) -> None:
        """On input callback to set the values to be always two digits"""
        if not widg.val_change_is_changing_entry:
            widg.val_change_is_changing_entry = True
            widg.set_text(widg.get_text().zfill(2))
            widg.val_change_is_changing_entry = False

    def tick(self) -> bool:
        """Run the timer

        This is done in two steps: first we compute the time elapsed between
        two ticks of the loop, and then we subtract it from the timer time,
        which is then updated.

        Returns a bool to notify the event-loop on whether the timer is done.
        """
        if self.is_running:
            if self.previous_iter_time is None or self.remaining is None:
                # 1 second is removed from the remaining time, in order to have
                # a smooth start of the timer.
                # Without this subtraction, after `self.previous_iter_time` is
                # set, the elapsed time for this initial iteration is
                # calculated, but the difference too small, making the first
                # timer second last two iterations (hence two actual seconds).
                self.remaining = self.get_time() - 1
                self.previous_iter_time = time.time()

            now = time.time()
            elapsed = now - self.previous_iter_time
            self.previous_iter_time = now

            self.remaining = self.remaining - elapsed
            self.set_time(self.remaining)

            if self.remaining <= 0:
                self.finish_timer()
                return False
            else:
                return True
        else:
            return False

    def start_cb(self, *args) -> None:
        if not self.is_running:
            self.previous_iter_time = None
            self.remaining = None
            self.is_running = True
            self.orig_time = self.get_time()
            GLib.timeout_add(100, self.tick)

    def pause_cb(self, *args) -> None:
        """The pause button callback, used to pausing and resuming"""
        if self.is_running:
            self.is_running = False
            self.previous_iter_time = None
            self.remaining = None
        else:  # resuming
            self.is_running = True
        if self.is_running:
            GLib.timeout_add(100, self.tick)

    def reset_cb(self, *args) -> None:
        """Resets the timer to the originally set value, after being started"""
        self.is_running = False
        self.previous_iter_time = None
        self.remaining = None
        self.set_time(self.orig_time)

    def connect_timer_hook(self, h: Callable,
                           prepend: Optional[bool] = False) -> None:
        if prepend:
            self.timer_hooks.insert(0, h)
        else:
            self.timer_hooks.append(h)

    def finish_timer(self) -> None:
        self.is_running = False
        self.previous_iter_time = None
        self.remaining = None
        self.set_time(0)
        for h in self.timer_hooks: h()


class TimerDialog:

    keep_annoying = False

    sounds_and_files = {_('Ringing Sound'): 'phone.opus',
                        _('Warning Sound'): 'warning.opus',
                        _('Error Sound'): 'error.opus'}

    def __init__ (self):
        self.init_player()
        self.ui = Gtk.Builder()
        self.ui.add_from_string(_get_data('gourmet', 'ui/timerDialog.ui').decode())
        self.timer = TimeSpinnerUI(
            self.ui.get_object('hoursSpinButton'),
            self.ui.get_object('minutesSpinButton'),
            self.ui.get_object('secondsSpinButton')
            )
        self.timer.connect_timer_hook(self.timer_done_cb)
        for w in ['timerDialog','mainLabel',
                  'soundComboBox','repeatCheckButton',
                  'noteEntry','expander1','timerBox','resetTimerButton',
                  'timerFinishedLabel','keepAnnoyingLabel'
                  ]:
            setattr(self,w,self.ui.get_object(w))
        cb.set_model_from_list(self.soundComboBox,list(self.sounds_and_files.keys()))
        cb.cb_set_active_text(self.soundComboBox,_('Ringing Sound'))
        self.ui.connect_signals(
            {'reset_cb':self.timer.reset_cb,
             'pause_cb':self.timer.pause_cb,
             'start_cb':self.timer.start_cb,
             'note_changed_cb':self.note_changed_cb,
             }
            )
        self.timerDialog.connect('response',self.response_cb)
        self.timerDialog.connect('close',self.close_cb)
        self.timerDialog.set_modal(False)
        self.note = ''

    def set_time (self, s):
        self.timer.set_time(s)

    def note_changed_cb (self, entry):
        txt = entry.get_text()
        self.note = txt
        if txt: txt = _('Timer')+': '+txt
        else: txt = _('Timer')
        self.timerDialog.set_title(txt)
        self.mainLabel.set_markup('<span weight="bold" size="larger">' + xml.sax.saxutils.escape(txt) + '</span>')

    def init_player (self):
        self.player = Player()

    def play_tune (self) -> None:
        sound = self.sounds_and_files[cb.cb_get_active_text(self.soundComboBox)]
        data = _get_data('gourmet', f'data/sound/{sound}')
        assert data

        # TODO!!! Delete the tempfile when we're done
        # TODO: Figure out how to make GStreamer play raw bytes
        fd, fname = _mkstemp('.opus')
        _os.write(fd, data)
        _os.close(fd)
        self.player.play_file(fname)

    def annoy_user (self):
        if self.keep_annoying:
            self.play_tune()
            return True

    def timer_done_cb (self):
        if hasattr(self.timerDialog,'set_urgency_hint'): self.timerDialog.set_urgency_hint(True)
        self.play_tune()
        if self.repeatCheckButton.get_active():
            self.keep_annoying = True
            # TODO: Timeout on when the audio file actually stops playing
            GLib.timeout_add(3000, self.annoy_user)
        self.timerBox.hide()
        self.expander1.hide()
        self.timerFinishedLabel.show()
        self.resetTimerButton.show()
        if self.keep_annoying: self.keepAnnoyingLabel.show()


    def stop_annoying (self):
        self.keep_annoying = False
        if hasattr(self.timerDialog,'set_urgency_hint'): self.timerDialog.set_urgency_hint(False)

    def refresh (self, *args):
        self.stop_annoying()
        self.timer.reset_cb()
        self.timerFinishedLabel.hide()
        self.keepAnnoyingLabel.hide()
        self.timerBox.show()
        self.resetTimerButton.hide()
        self.expander1.show()

    def response_cb (self, dialog, resp):
        if resp == Gtk.ResponseType.APPLY:
            self.refresh()
        else:
            self.close_cb()

    def close_cb(self, *args) -> None:
        """Close a timer window.

        There are three options: either the timer is not running, and it gets
        closed, the timer is running and it gets cancelled and closed, or the
        timer is running, and gets hidden ready to pop back up when finished.
        """
        self.stop_annoying()
        do_cancel = True
        if self.timer.is_running:
            msg = ("You've requested to close a window with an active timer. "
                   "You can stop the timer, or you can just close the window. "
                   "If you close the window, it will reappear when your timer "
                   "goes off.")
            try:
                do_cancel = getBoolean(label=_('Stop timer?'),
                                       sublabel=_(msg),
                                       custom_yes=_('Stop _timer'),
                                       custom_no=_('_Keep timing'))
            except UserCancelledError:
                return  # keep the timer window open

        if do_cancel:
            self.timer.is_running = False
            self.timerDialog.hide()
            self.timerDialog.destroy()
        else:
            self.timer.connect_timer_hook(self.timerDialog.show, 1)
            self.timerDialog.hide()

    def run (self): self.timerDialog.run()
    def show (self): self.timerDialog.show()


def show_timer(seconds: int = 600, note: Optional[str] = None) -> None:
    td = TimerDialog()
    td.set_time(seconds)
    if note is not None:
        td.noteEntry.set_text(note)
    td.show()


if __name__ == '__main__':
    w = Gtk.Window()
    b = Gtk.Button()
    b.set_label('Show timer')
    b.connect('clicked',lambda *args: show_timer())
    w.add(b)
    w.connect('delete-event',lambda *args: Gtk.main_quit())
    w.show_all()
    Gtk.main()
