from __future__ import print_function

import gtk, gobject, time, gglobals, os
import xml.sax.saxutils
from sound import Player
from gtk_extras import cb_extras as cb
from gettext import gettext as _

class TimeSpinnerUI:

    def __init__ (self, hoursSpin, minutesSpin, secondsSpin):
        self.timer_hooks = []
        self.running = False
        self.hoursSpin = hoursSpin
        self.minutesSpin = minutesSpin
        self.secondsSpin = secondsSpin        
        for s in [self.hoursSpin,self.minutesSpin,self.secondsSpin]:
            # This is set up to assure 2 digit entries... 00:00:00, etc.
            s.connect('changed',self.val_changed_cb)
            s.val_change_is_changing_entry = False
            s.set_width_chars(2)
            s.set_value(1)
            s.set_value(0)            

    def set_time (self, s):
        s = int(s)
        if s < 0: s = 0
        #self.hoursSpin.set_text(self.pad_n(s / 3600))
        self.hoursSpin.set_value(s / 3600)
        s = s % 3600
        #self.minutesSpin.set_text(self.pad_n(s / 60))
        self.minutesSpin.set_value(s / 60)
        #self.secondsSpin.set_text(self.pad_n(s % 60))
        self.secondsSpin.set_value(s % 60)

    def val_changed_cb (self, widg):
        if not widg.val_change_is_changing_entry:
            widg.val_change_is_changing_entry = True
            widg.set_text(self.pad_n(int(widg.get_value())))
            widg.val_change_is_changing_entry = False            

    def pad_n (self, int):
        s = str(int)
        if len(s)==1: return '0'+s
        else: return s

    def get_time (self):
        return self.hoursSpin.get_value()*3600 + self.minutesSpin.get_value()*60 + self.secondsSpin.get_value()

    # Methods to run the timer...
    def tick (self):
        if self.running:
            elapsed = time.time() - self.running
            t = self.start_time - elapsed
            #t = self.get_time() - 1
            self.set_time(t)
            if t<=0:
                self.finish_timer()
                return False
            else:
                return True
        else:
            return False

    def start_cb (self,*args):
        if not self.running and self.get_time():
            self.running = time.time()
            self.orig_time = self.start_time = self.get_time()
            gobject.timeout_add(1000,self.tick)

    def pause_cb (self, *args):
        if self.running:
            self.running = False
        else:
            self.running = time.time()
            self.start_time = self.get_time()
        if self.running: gobject.timeout_add(1000,self.tick)

    def reset_cb (self, *args):
        self.running = False
        self.set_time(self.orig_time)

    def connect_timer_hook (self, h, prepend=False):
        if prepend:
            self.timer_hooks = [h] + self.timer_hooks
        else:
            self.timer_hooks.append(h)

    def finish_timer (self):
        self.running  = False
        for h in self.timer_hooks: h()


from gtk_extras import dialog_extras as de

class TimerDialog:

    keep_annoying = False

    sounds_and_files = {
        _('Ringing Sound'):'phone.wav',
        _('Warning Sound'):'warning.wav',
        _('Error Sound'):'error.wav',
        }

    def __init__ (self):
        self.init_player()
        self.ui = gtk.Builder()
        self.ui.add_from_file(os.path.join(gglobals.uibase,'timerDialog.ui'))
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
        cb.set_model_from_list(self.soundComboBox,self.sounds_and_files.keys())
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

    def play_tune (self):
        sound_file = self.sounds_and_files[cb.cb_get_active_text(self.soundComboBox)]
        sound_file = os.path.join(gglobals.data_dir,'sound',sound_file)
        self.player.play_file(sound_file)

    def annoy_user (self):
        if self.keep_annoying:
            self.play_tune()
            return True

    def timer_done_cb (self):
        if hasattr(self.timerDialog,'set_urgency_hint'): self.timerDialog.set_urgency_hint(True)
        self.play_tune()
        if self.repeatCheckButton.get_active():
            self.keep_annoying = True
            gobject.timeout_add(3000,self.annoy_user)
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
        if resp == gtk.RESPONSE_APPLY:
            self.refresh()
        else:
            self.close_cb()

    def close_cb (self,*args):
        self.stop_annoying()
        if (not self.timer.running) or de.getBoolean(label=_('Stop timer?'),
                                                 sublabel=_("You've requested to close a window with an active timer. You can stop the timer, or you can just close the window. If you close the window, it will reappear when your timer goes off."),
                                                 custom_yes=_('Stop _timer'),custom_no=_('_Keep timing')
                                                 ):
            self.timer.running = False
            self.timerDialog.hide()
            self.timerDialog.destroy()
        else:
            self.timer.connect_timer_hook(self.timerDialog.show,1)
            self.timerDialog.hide()

    def run (self): self.timerDialog.run()
    def show (self): self.timerDialog.show()

def show_timer (time=600,
                note=''):
    td = TimerDialog()
    td.set_time(time)
    if note:
        td.noteEntry.set_text(note)
    td.show()

if __name__ == '__main__':
    w = gtk.Window()
    b = gtk.Button('Show timer')
    b.connect('clicked',lambda *args: show_timer())
    w.add(b)
    w.connect('delete-event',lambda *args: gtk.main_quit())
    w.show_all()
    gtk.main()
