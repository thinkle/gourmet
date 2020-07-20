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

# Largely based on hypertext.py example in pygtk docs by
# Maik Hertha <maik.hertha@berlin.de>

import re
from typing import Optional
from gi.repository import Gdk, GObject, Gtk, Pango
from gourmet.gtk_extras.TextBufferMarkup import PangoBuffer


class LinkedPangoBuffer(PangoBuffer):

    href_regexp = re.compile(r"<a href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>")
    url_markup = 'underline="single" color="blue"'
    url_props = [('underline', Pango.Underline.SINGLE),
                 ('foreground-gdk', Gdk.color_parse('blue'))]
    markup_dict = {}

    def set_text(self, txt: str) -> None:
        m = self.href_regexp.search(txt)
        if m:
            while m:
                href = m.groups()[0]
                body = m.groups()[1]
                if body in self.markup_dict and self.markup_dict[body] != href:
                    raise ValueError("Cannot handle duplicated link bodies",
                                     body, self.markup_dict[body], href)
                self.markup_dict[body] = href
                m = self.href_regexp.search(txt,m.end())
            txt = self.href_regexp.sub(r'<span %s>\2</span>'%self.url_markup,txt)
        super().set_text(txt)

    def get_text(self,
                 start: Optional[Gtk.TextIter] = None,
                 end: Optional[Gtk.TextIter] = None,
                 include_hidden_chars: bool = False) -> str:
        """Get the buffer content.

        If `include_hidden_chars` is set, then the html markup content is
        returned.
        """
        content = super().get_text(start, end, include_hidden_chars)

        # TODO: Replace all colored and underlined text tags with links, if
        # these are links
        # if include_hidden_chars: ...
        return content


class LinkedTextView(Gtk.TextView):
    __gtype_name__ = 'LinkedTextView'

    hovering_over_link = False
    hand_cursor = Gdk.Cursor.new(Gdk.CursorType.HAND2)
    text_cursor = Gdk.Cursor.new(Gdk.CursorType.XTERM)  # I-beam shaped

    __gsignals__ = {'link-activated': (GObject.SignalFlags.RUN_LAST,
                                       GObject.TYPE_STRING,
                                       [GObject.TYPE_STRING])}

    def __init__ (self):
        # GObject.GObject.__init__(self) # do we need both constructor calls?
        Gtk.TextView.__init__(self)
        self.set_buffer(self.make_buffer())
        buf = self.get_buffer()
        self.set_text = buf.set_text
        self.connect('key-press-event',self.key_press_event)
        self.connect('event-after',self.event_after)
        self.connect('motion-notify-event',self.motion_notify_event)
        self.connect('visibility-notify-event',self.visibility_notify_event)

    def make_buffer(self):
        return LinkedPangoBuffer()

    def key_press_event(self,
                        text_view: 'LinkedTextView',
                        event: Gdk.Event) -> bool:
        """Handle Enter key-press on time links."""
        keyname = Gdk.keyval_name(event.keyval)
        if keyname in ['Return', 'KP_Enter']:
            buffer = text_view.get_buffer()
            itr = buffer.get_iter_at_mark(buffer.get_insert())
            return self.follow_if_link(text_view, itr)
        return False

    def event_after(self,
                    text_view: 'LinkedTextView',
                    event: Gdk.Event) -> bool:
        """Handle mouse clicks on time links."""
        _, button = event.get_button()

        # Check for a left mouse click (as set by the system, not hardware).
        if event.type == Gdk.EventType.BUTTON_RELEASE and button == 1:
            buffer = text_view.get_buffer()

            # we shouldn't follow a link if the user has selected something
            try:
                start, end = buffer.get_selection_bounds()
            except ValueError:
                # If there is nothing selected, None is returned
                pass
            else:
                if start.get_offset() != end.get_offset():
                    return False

            x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
                int(event.x), int(event.y))
            _, itr = text_view.get_iter_at_location(x, y)
            self.follow_if_link(text_view, itr)
        return False

    def set_cursor_if_appropriate(self,
                                  text_view: 'LinkedTextView',
                                  x: int,
                                  y: int) -> None:
        """Set the mouse cursor to be a hand when hovering over a time link.

        Check each tag covering the position (x, y) within the text view.
        If the text happens to be coloured, which only time links are allowed
        to be in this application, then set the cursor to a hand.
        If leaving the area of a time link, set the cursor to an I-beam.
        """
        _, itr = text_view.get_iter_at_location(x, y)
        tags = itr.get_tags()

        hovering_over_link = False

        blue = Gdk.RGBA(red=0, green=0, blue=1., alpha=1.)
        for tag in tags:
            color = tag.get_property('foreground-rgba')
            if color and color == blue:
                hovering_over_link = True
                break

        cursor = self.hand_cursor if hovering_over_link else self.text_cursor
        text_view.get_window(Gtk.TextWindowType.TEXT).set_cursor(cursor)

    # Update the cursor image if the pointer moved.
    def motion_notify_event(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        return False

    # Also update the cursor image if the window becomes visible
    # (e.g. when a window covering it got iconified).
    def visibility_notify_event(self, text_view, event):
        _, wx, wy, _ = text_view.get_window(Gtk.TextWindowType.WIDGET).get_pointer()
        bx, by = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def follow_if_link(self,
                       text_view: 'LinkedTextView',
                       itr: Gtk.TextIter) -> None:
        """Looks at all tags covering the position of iter in the text view,
            and if one of them is a link, follow it by showing the page identified
            by the data attached to it.
        """
        blue = Gdk.RGBA(red=0, green=0, blue=1., alpha=1.)

        tags = itr.get_tags()
        for tag in tags:
            color = tag.get_property('foreground-rgba')
            if color is not None and color == blue:
                begin = itr.copy()
                begin.forward_to_tag_toggle(tag)

                end = itr.copy()
                end.backward_to_tag_toggle(tag)

                link_text = text_view.get_buffer().get_text(begin, end)
                target = text_view.get_buffer().markup_dict[link_text]

                self.emit('link-activated', target)
                break


if __name__ == '__main__':
    def print_link (tv,l):
        print(l)
    tv = LinkedTextView()
    tv.connect('link-activated',print_link)
    w = Gtk.Window()
    w.add(tv)
    tv.get_buffer().set_text("""This is some text
    Some <i>fancy</i>, <u>fancy</u>, text.
    This is <a href="foo">a link</a>, a
    <a href="fancy_desc">fancy, fancy</a> link.

    <a href="123:foo">recipe link</a>

    <a href="456:boo">\xbc recipe boogoochooboo</a>

    <b>Yeah!</b>
    """)

    w.show_all()
    w.connect('delete-event', lambda *args: Gtk.main_quit())
    Gtk.main()
