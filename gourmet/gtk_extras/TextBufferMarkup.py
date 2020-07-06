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
from typing import Any, Dict, List, Optional, Tuple, Union
from gi.repository import Gdk, GLib, Gtk, Pango


class PangoBuffer(Gtk.TextBuffer):
    """A supercharged Gtk.TextBuffer that handles HTML or Pango markup in its
    content"""

    def __init__(self):
        Gtk.TextBuffer.__init__(self)

    def set_text(self, txt: Union[str, bytes]) -> None:
        if isinstance(txt, bytes):
            # data loaded from the database are bytes, not str
            txt = txt.decode("utf-8")
        self.insert_markup(self.get_start_iter(), txt, -1)

    def get_text(self,
                 start: Optional[Gtk.TextIter] = None,
                 end: Optional[Gtk.TextIter] = None,
                 include_hidden_chars: bool = False) -> str:
        """Return the content as html markup"""
        if start is None:
            start = self.get_start_iter()
        if end is None:
            end = self.get_end_iter()

        text = super().get_text(start, end, include_hidden_chars=False)

        if include_hidden_chars is False:
            return text

        # Iterate through the tags to find opening and closing.
        # As tags were set automatically, they are anonymous (they do not have
        # their `name` property set.)
        # As such, we get the properties, and check their state later to find
        # out what tags they are meant to be. There are only a few valid
        # combinations: bold, italic, underlined, and time-link (underlined and
        # blue text colour).
        itr = start  # Same iterator, renamed to keep code easy to grok

        tag_list: List[Tuple[int, int, Dict[str, Any]]] = []
        while itr.forward_to_tag_toggle():  # move to opening of tags
            open_pos = itr.get_offset()
            tags = itr.get_tags()

            # active_tags could have been a set, but Gtk.Color are not hashable
            active_tags = {}
            for tag in tags:
                active_tags["style"] = tag.get_property("style")  # ie. italic
                active_tags["underline"] = tag.get_property("underline")
                active_tags["weight"] = tag.get_property("weight")  # ie. bold
                active_tags["foreground"] = tag.get_property("foreground-rgba")

            itr.forward_to_tag_toggle(tag)  # move to closing tags
            close_pos = itr.get_offset()

            tag_list.append((open_pos, close_pos, active_tags))

        return self.to_html(text, tag_list)

    @staticmethod
    def to_html(text: str,
                tag_list: List[Tuple[int, int, Dict[str, Any]]]) -> str:
        blue = Gdk.RGBA(red=0, green=0, blue=1., alpha=1.)

        for start, stop, tags in tag_list:
            if tags["foreground"] == blue:
                text = (text[:start] + f'<a href="{text[start:stop]}">' +
                        text[start:stop] + "</a>" + text[stop:])
                continue  # skip handling the underscore here
            if tags["weight"] == 400:  # FIXME: use the correct enum
                text = (text[:start] +
                        "<b>" + text[start:stop] + "</b>" +
                        text[stop:])
            if tags["underline"] is Pango.Underline.SINGLE:
                text = (text[:start] +
                        "<u>" + text[start:stop] + "</u>" +
                        text[stop:])
            if tags["style"] is Pango.Style.ITALIC:
                text = (text[:start] +
                        "<i>" + text[start:stop] + "</i>" +
                        text[stop:])
        return text

    def get_selection(self):
        """A get_selection that returns the word where the cursor is at, if
        there is no selection"""
        bounds = self.get_selection_bounds()

        if not bounds:
            iter = self.get_iter_at_mark(self.insert_)
            if iter.inside_word():
                start_pos = iter.get_offset()
                iter.forward_word_end()
                word_end = iter.get_offset()
                iter.backward_word_start()
                word_start = iter.get_offset()
                iter.set_offset(start_pos)
                bounds = (self.get_iter_at_offset(word_start),
                          self.get_iter_at_offset(word_end+1))
            else:
                bounds = (iter,self.get_iter_at_offset(iter.get_offset()+1))
        return bounds

    def apply_tag_to_selection(self, tag):
        start, stop = self.get_selection()
        self.apply_tag(tag, start, stop)

    def remove_tag_from_selection(self, tag):
        start, stop = self.get_selection()
        self.remove_tag(tag, start, stop)

    def remove_all_tags(self):
        start, stop = self.get_selection()
        for tag in list(self.tags.values()):
            self.remove_tag(tag, start, stop)


class InteractivePangoBuffer(PangoBuffer):
    def __init__ (self,
                  normal_button=None,
                  toggle_widget_alist: Optional[List] = None):
        """An interactive interface to allow marking up a Gtk.TextBuffer.
        normal_button is a widget whose clicked signal will make us normal
        toggle_widget_alist is a list that looks like this:
        [(widget, (font,attr)),
         (widget2, (font,attr))]
         """
        PangoBuffer.__init__(self)
        if normal_button is not None:
            normal_button.connect('clicked', self.remove_all_tags)
        self.tag_widgets = {}
        self.internal_toggle = False
        self.insert_ = self.get_insert()
        self.connect('mark-set',self._mark_set_cb)
        self.connect('changed',self._changed_cb)

        if toggle_widget_alist is not None:
            for w,tup in toggle_widget_alist:
                self.setup_widget(w,*tup)

    def setup_widget_from_pango(self,
                                widget: Gtk.ToggleButton,
                                markupstring: str):
        """setup widget from a pango markup string"""
        _, a, t, s = Pango.parse_markup(markupstring, -1, '\x00')
        ai=a.get_iterator()
        ret = ai.get_font(Pango.FontDescription(), None, None)
        if ret is not None:
            font, _, attrs = ret
        else:
            font = attrs = None
        return self.setup_widget(widget, font, attrs)

    def setup_widget(self, widget, font, attr):
        tags=self.get_tags_from_attrs(font, None, attr)
        self.tag_widgets[tuple(tags)] = widget
        return widget.connect('toggled', self._toggle, tags)

    def _toggle(self, widget: Gtk.ToggleButton, tags: List[Gtk.TextTag]):
        if self.internal_toggle: return
        if widget.get_active():
            for t in tags: self.apply_tag_to_selection(t)
        else:
            for t in tags: self.remove_tag_from_selection(t)

    def _mark_set_cb (self, buffer, iter, mark, *params):
        # Every time the cursor moves, update our widgets that reflect
        # the state of the text.
        if hasattr(self,'_in_mark_set') and self._in_mark_set: return
        self._in_mark_set = True
        if mark.get_name()=='insert':
            for tags,widg in list(self.tag_widgets.items()):
                active = True
                for t in tags:
                    if not iter.has_tag(t):
                        active=False
                self.internal_toggle=True
                widg.set_active(active)
                self.internal_toggle=False
        if hasattr(self,'last_mark'):
            self.move_mark(self.last_mark,iter)
        else:
            self.last_mark = self.create_mark('last',iter,left_gravity=True)
        self._in_mark_set = False

    def _changed_cb (self, tb):
        if not hasattr(self,'last_mark'): return
        # If our insertion point has a mark, we want to apply the tag
        # each time the user types...
        old_itr = self.get_iter_at_mark(self.last_mark)
        insert_itr = self.get_iter_at_mark(self.insert_)
        if old_itr!=insert_itr:
            # Use the state of our widgets to determine what
            # properties to apply...
            for tags,w in list(self.tag_widgets.items()):
                if w.get_active():
                    #print 'apply tags...',tags
                    for t in tags: self.apply_tag(t,old_itr,insert_itr)


class SimpleEditor:
    """A demo of the TextBufferedMarkup class"""
    def __init__(self):
        self.w = Gtk.Window()
        self.vb = Gtk.VBox()
        self.editBox = Gtk.HButtonBox()
        self.nb = Gtk.Button()
        self.nb.set_label("Normal")
        self.editBox.add(self.nb)
        self.sw = Gtk.ScrolledWindow()
        self.tv = Gtk.TextView()
        self.sw.add(self.tv)
        self.ipb = InteractivePangoBuffer(
            normal_button=self.nb)

        self.ipb.set_text("""<b>This is bold</b>. <i>This is italic</i>
            <b><i>This is bold, italic, and <u>underlined!</u></i></b>
            <span background="blue">This is a test of bg color</span>
            <span foreground="blue">This is a test of fg color</span>
            <span foreground="white" background="blue">This is a test of fg and bg color</span>
            """)

        self.tv.set_buffer(self.ipb)
        for lab,stock,font in [('gtk-italic',True,'<i>italic</i>'),
                               ('gtk-bold',True,'<b>bold</b>'),
                               ('gtk-underline',True,'<u>underline</u>'),
                               ('Blue',True,'<span foreground="blue">blue</span>'),
                               ('Red',False,'<span foreground="red">smallcaps</span>'),
                               ]:
            button = Gtk.ToggleButton(lab)
            self.editBox.add(button)
            if stock: button.set_use_stock(True)
            self.ipb.setup_widget_from_pango(button,font)
        self.vb.add(self.editBox)
        self.vb.add(self.sw)
        self.actionBox = Gtk.HButtonBox()
        self.qb = Gtk.Button(stock='quit')
        self.pmbut = Gtk.Button('Print markup')
        self.pmbut.connect('clicked',self.print_markup)
        self.qb.connect('clicked',lambda *args: self.w.destroy() or Gtk.main_quit())
        self.actionBox.add(self.pmbut)
        self.actionBox.add(self.qb)
        self.vb.add(self.actionBox)
        self.w.add(self.vb)
        self.w.show_all()

    def print_markup(self, *args):
        print(self.ipb.get_text())


if __name__ == '__main__':
    se = SimpleEditor()
    se.w.connect('delete-event',lambda *args: Gtk.main_quit())
    Gtk.main()
