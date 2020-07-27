"""Scan text for time and show links that will pop up a timer if the
user clicks on any time in the TextView."""
import re
from typing import Union

from gi.repository import Gdk, GObject, Gtk

from gourmet import timer, convert
from gourmet.convert import Converter
from gourmet.gtk_extras.LinkedTextView import LinkedPangoBuffer, LinkedTextView

all_units = set()
for base, units in Converter.time_units:
    for u in units:
        u = re.escape(str(u))
        all_units.add(u)

time_matcher = re.compile(
    '(?P<firstnum>'+convert.NUMBER_FINDER_REGEXP + ')(' + \
    convert.RANGE_REGEXP + convert.NUMBER_FINDER_REGEXP.replace('int','int2').replace('frac','frac2') + ')?' \
    + r'\s*' + '(?P<unit>' + '|'.join(all_units) + r')(?=$|\W)',
    re.UNICODE
    )


def make_time_links(s: str) -> str:
    return time_matcher.sub(r'<a href="\g<firstnum> \g<unit>">\g<0></a>', s)


class TimeBuffer(LinkedPangoBuffer):
    def set_text(self, txt: Union[bytes, str]) -> None:
        if isinstance(txt, bytes):
            txt = txt.decode("utf-8")
        super().set_text(make_time_links(txt))


class LinkedTimeView(LinkedTextView):
    __gtype_name__ = 'LinkedTimeView'

    __gsignals__ = {
        'time-link-activated': (GObject.SignalFlags.RUN_LAST,
                                GObject.TYPE_STRING,
                                [GObject.TYPE_STRING, GObject.TYPE_STRING]),
    }

    def make_buffer(self):
        return TimeBuffer()

    def follow_if_link(self,
                       text_view: 'LinkedTimeView',
                       itr: Gtk.TextIter) -> bool:
        """Launch a timer if a link was clicked.

        This is done by emitting the `time-link-activated` signal defined in
        this class.
        Whether or not the it was a link, the click won't be processed further.
        """
        # Get the displayed text sentence, to use as a label in the timer.
        start_sentence = itr.copy()
        start_sentence.backward_sentence_start()

        end_sentence = itr.copy()
        if not end_sentence.ends_sentence():
            end_sentence.forward_sentence_end()

        sentence = self.get_buffer().get_slice(start_sentence,
                                               end_sentence,
                                               False)

        # Get the time duration (target of the link).
        start_ts = itr.copy()
        start_ts.backward_to_tag_toggle()
        itr.forward_to_tag_toggle()
        end_ts = itr.copy()
        time_string = self.get_buffer().get_slice(start_ts, end_ts, False)

        # Confirm that is is in the links dictionary.
        if self.get_buffer().markup_dict.get(time_string) == time_string:
            self.emit("time-link-activated", time_string, sentence)

        return False  # Do not process the signal further.


def show_timer_cb(tv: LinkedTimeView, line: str, note: str) -> None:
    """Callback that expects a widget, a time string, and a note to display"""
    timer.show_timer(Converter.instance().timestring_to_seconds(line), note)


if __name__ == '__main__':
    tv = LinkedTimeView()
    tv.connect('time-link-activated', show_timer_cb)
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
