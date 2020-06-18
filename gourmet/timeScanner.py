"""Scan text for time and show links that will pop up a timer if the
user clicks on any time in the TextView."""

from . import convert
import re
from gi.repository import GObject, Gtk
from .gtk_extras import LinkedTextView
from . import timer
import xml.sax.saxutils

all_units = []
for base,units in convert.Converter.time_units:
    for u in units:
        u = re.escape(str(u))
        if u not in all_units: all_units.append(u)

time_matcher = re.compile(
    '(?P<firstnum>'+convert.NUMBER_FINDER_REGEXP + ')(' + \
    convert.RANGE_REGEXP + convert.NUMBER_FINDER_REGEXP.replace('int','int2').replace('frac','frac2') + ')?' \
    + '\s*' + '(?P<unit>' + '|'.join(all_units) + ')(?=$|\W)',
    re.UNICODE
    )



def make_time_links (s):
    return time_matcher.sub('<a href="\g<firstnum> \g<unit>">\g<0></a>',s)


class TimeBuffer (LinkedTextView.LinkedPangoBuffer):

    def set_text (self, txt):
         LinkedTextView.LinkedPangoBuffer.set_text(
             self,
             make_time_links(txt)
             )

class LinkedTimeView (LinkedTextView.LinkedTextView):
    __gtype_name__ = 'LinkedTimeView'

    __gsignals__ = {
        'time-link-activated':(GObject.SignalFlags.RUN_LAST,
                          GObject.TYPE_STRING,
                          [GObject.TYPE_STRING,GObject.TYPE_STRING]),
        }

    def make_buffer (self):
        return TimeBuffer()

    def follow_if_link (self, text_view, iter):
        tags = iter.get_tags()
        for tag in tags:
            href = tag.get_data('href')
            if href:
                start_sentence = iter.copy();
                start_sentence.backward_sentence_start()
                end_sentence = iter.copy()
                if not end_sentence.ends_sentence(): end_sentence.forward_sentence_end()
                self.emit('time-link-activated',href,self.get_buffer().get_slice(start_sentence,end_sentence))
                return True


def show_timer_cb (tv,l,note,c):
    """Callback that expects a widget, a time string, and a converter instance"""
    timer.show_timer(c.timestring_to_seconds(l),
               note)

if __name__ == '__main__':
    c = convert.get_converter()
    tv = LinkedTimeView()
    tv.connect('time-link-activated',show_timer_cb,c)
    tv.get_buffer().set_text(
        """Cook potatoes for 1/2 hour.

        When you are finished, leave in the refrigerator for up to three days.

        After that, boil onions for 20 to 30 minutes.

        When finished, bake everything for two and a half hours.

        15-25 seconds.
        """
        )

    w = Gtk.Window()
    w.add(tv)
    w.connect('delete-event',lambda *args: Gtk.main_quit())
    w.show_all()
    Gtk.main()
