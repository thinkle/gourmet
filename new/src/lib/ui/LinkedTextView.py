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

# Largely based on hypertext.py example in pygtk docs by
# Maik Hertha <maik.hertha@berlin.de>

import pango, gtk, gobject, sexy
import re, xml.sax.saxutils
from TextBufferMarkup import PangoBuffer
from gourmet.gdebug import *

class LinkedPangoBuffer (PangoBuffer):

    href_regexp = re.compile(r"<a href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>")

    url_markup = 'underline="single" color="blue"'

    url_props = [('underline',pango.UNDERLINE_SINGLE),
                 ('foreground-gdk',gtk.gdk.color_parse('blue')),
                 ]

    markup_dict = {}

    def set_text (self, txt):
        m = self.href_regexp.search(txt)
        if m:
            while m:
                href = m.groups()[0]
                body = xml.sax.saxutils.unescape(m.groups()[1])
                if self.markup_dict.has_key(body) and self.markup_dict[body]!=href:
                    raise """Damn -- our not-so-clever implementation of <a href=""> parsing requires
                    that no two distinct links have the same text describing them!"""
                self.markup_dict[body]=href
                m = self.href_regexp.search(txt,m.end())
            txt = self.href_regexp.sub(r'<span %s>\2</span>'%self.url_markup,txt)
        PangoBuffer.set_text(self,txt)

    def insert_with_tags (self, itr, text, *tags):
        match = True
        for p,v in self.url_props:
            match = False
            for t in tags:
                if isinstance(v,gtk.gdk.Color):
                    c = t.get_property(p)
                    if v.red==c.red and v.blue==c.blue and v.green==c.green:
                        match=True
                elif t.get_property(p)==v:
                    match=True
            if not match:
                break
        text = unicode(text)
        if match and self.markup_dict.has_key(text):
            new_tag = self.create_tag()
            new_tag.set_data('href',self.markup_dict[text])
            tags = list(tags)
            tags.append(new_tag)
        elif match:
            print 'Funny',text,'looks like a link, but is not in markup_dict',self.markup_dict
        PangoBuffer.insert_with_tags(self,itr,text,*tags)

class LinkedTextView (sexy.UrlLabel):

    __gsignals__ = {
        'link-activated':(gobject.SIGNAL_RUN_LAST,
                          gobject.TYPE_STRING,
                          [gobject.TYPE_STRING]),
        }
    
    def __init__ (self):
        gobject.GObject.__init__(self)
        sexy.UrlLabel.__init__(self)
    
    def make_buffer (self):
        return LinkedPangoBuffer()

class LinkedTextView2 (gtk.TextView):

    hovering_over_link = False
    hand_cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
    regular_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)

    __gsignals__ = {
        'link-activated':(gobject.SIGNAL_RUN_LAST,
                          gobject.TYPE_STRING,
                          [gobject.TYPE_STRING]),
        }
    
    def __init__ (self):
        gobject.GObject.__init__(self)
        gtk.TextView.__init__(self)
        self.set_buffer(self.make_buffer())
        buf = self.get_buffer()
        self.set_text = buf.set_text
        self.connect('key-press-event',self.key_press_event)
        self.connect('event-after',self.event_after)
        self.connect('motion-notify-event',self.motion_notify_event)
        self.connect('visibility-notify-event',self.visibility_notify_event)

    def make_buffer (self):
        return LinkedPangoBuffer()

    # Links can be activated by pressing Enter.
    def key_press_event(self, text_view, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname in ['Return','KP_Enter']:
            buffer = text_view.get_buffer()
            iter = buffer.get_iter_at_mark(buffer.get_insert())
            return self.follow_if_link(text_view, iter)
        return False
    # Links can also be activated by clicking.
    def event_after(self, text_view, event):
        if event.type != gtk.gdk.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False
        buffer = text_view.get_buffer()

        # we shouldn't follow a link if the user has selected something
        try:
            start, end = buffer.get_selection_bounds()
        except ValueError:
            # If there is nothing selected, None is return
            pass
        else:
            if start.get_offset() != end.get_offset():
                return False

        x, y = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
            int(event.x), int(event.y))
        iter = text_view.get_iter_at_location(x, y)
        self.follow_if_link(text_view, iter)
        return False

    # Looks at all tags covering the position (x, y) in the text view,
    # and if one of them is a link, change the cursor to the "hands" cursor
    # typically used by web browsers.
    def set_cursor_if_appropriate(self, text_view, x, y):
        hovering = False
        buffer = text_view.get_buffer()
        iter = text_view.get_iter_at_location(x, y)
        tags = iter.get_tags()

        for tag in tags:
            href = tag.get_data("href")
            if href:
                hovering = True
                break
        if hovering != self.hovering_over_link:
            self.hovering_over_link = hovering

        if self.hovering_over_link:
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.hand_cursor)
        else:
            text_view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.regular_cursor)

    # Update the cursor image if the pointer moved.
    def motion_notify_event(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        text_view.window.get_pointer()
        return False

    # Also update the cursor image if the window becomes visible
    # (e.g. when a window covering it got iconified).
    def visibility_notify_event(self, text_view, event):
        wx, wy, mod = text_view.window.get_pointer()
        bx, by = text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def follow_if_link (self, text_view, iter):
        ''' Looks at all tags covering the position of iter in the text view,
            and if one of them is a link, follow it by showing the page identified
            by the data attached to it.
        '''
        tags = iter.get_tags()
        for tag in tags:
            href = tag.get_data('href')
            if href:
                self.emit('link-activated',href)
                return True

if gtk.pygtk_version[1] < 8:
    gobject.type_register(LinkedTextView)    

if __name__ == '__main__':
    def print_link (tv,l):
        print l
    tv = LinkedTextView()
    tv.connect('link-activated',print_link)    
    w = gtk.Window()
    w.add(tv)
    tv.get_buffer().set_text(u"""This is some text
    Some <i>fancy</i>, <u>fancy</u>, text.
    This is <a href="foo">a link</a>, a
    <a href="fancy_desc">fancy, fancy</a> link.

    <a href="123:foo">recipe link</a>

    <a href="456:boo">\xbc recipe boogoochooboo</a>
    
    <b>Yeah!</b>
    """)

    w.show_all()
    w.connect('delete-event',lambda *args: gtk.main_quit())
    gtk.main()
