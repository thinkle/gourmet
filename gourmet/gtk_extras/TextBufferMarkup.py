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
from typing import List, Optional, Union
from gi.repository import Gdk, GLib, Gtk, Pango
from gourmet.gtk_extras.pango_html import PangoToHtml


class PangoBuffer(Gtk.TextBuffer):
    """A supercharged Gtk.TextBuffer that handles HTML or Pango markup in its
    content"""

    def __init__(self):
        Gtk.TextBuffer.__init__(self)

    def set_text(self, text: Union[str, bytes]) -> None:
        if isinstance(text, bytes):
            # data loaded from the database are bytes, not str
            text = text.decode("utf-8")
        self.insert_markup(self.get_start_iter(), text, -1)

    def get_text(self,
                 start: Optional[Gtk.TextIter] = None,
                 end: Optional[Gtk.TextIter] = None,
                 include_hidden_chars: bool = False) -> str:
        """Get the buffer content.

        If `include_hidden_chars` is set, then the html markup content is
        returned. If False, then the text only is returned."""
        if start is None:
            start = self.get_start_iter()
        if end is None:
            end = self.get_end_iter()

        if include_hidden_chars is False:
            return super().get_text(start, end, include_hidden_chars=False)
        else:
            format_ = self.register_serialize_tagset()
            content = self.serialize(self, format_, start, end)
            return PangoToHtml().feed(content)

    def get_selection(self):
        """A get_selection that returns the word where the cursor is at, if
        there is no selection"""
        bounds = self.get_selection_bounds()

        if not bounds:
            itr = self.get_iter_at_mark(self.get_insert())
            if itr.inside_word():
                start_pos = itr.get_offset()
                itr.forward_word_end()
                word_end = itr.get_offset()
                itr.backward_word_start()
                word_start = itr.get_offset()
                itr.set_offset(start_pos)
                bounds = (self.get_iter_at_offset(word_start),
                          self.get_iter_at_offset(word_end+1))
            else:
                bounds = (itr, self.get_iter_at_offset(itr.get_offset()+1))
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
    def __init__(self,
                 normal_button=None,
                 toggle_widget_alist: Optional[List] = None):
        super().__init__()

        if normal_button is not None:
            normal_button.connect('clicked', self.remove_all_tags)
        self.tag_widgets = {}
        self.internal_toggle = False
        self.connect('mark-set', self._mark_set_cb)
        self.connect('changed', self._changed_cb)

        if toggle_widget_alist is not None:
            for w, tup in toggle_widget_alist:
                self.setup_widget(w,*tup)

    def setup_widget_from_pango(self,
                                widget: Gtk.ToggleButton,
                                markupstring: str):
        """setup widget from a pango markup string"""
        _, a, t, s = Pango.parse_markup(markupstring, -1, '\x00')
        ai = a.get_iterator()
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
        if self.internal_toggle:
            return
        if widget.get_active():
            for t in tags:
                self.apply_tag_to_selection(t)
        else:
            for t in tags:
                self.remove_tag_from_selection(t)

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
        insert_itr = self.get_iter_at_mark(self.get_insert())
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

        # self.ipb.set_text("""<b>This is bold</b>. <i>This is italic</i>
        #     <b><i>This is bold, italic, and <u>underlined!</u></i></b>
        #     <span background="blue">This is a test of bg color</span>
        #     <span foreground="blue">This is a test of fg color</span>
        #     <span foreground="white" background="blue">This is a test of fg and bg color</span>
        #     """)

        self.ipb.set_text("""<b>This is bold</b>. <i>This is italic</i>
            <i><b>This is bold, italic, and </b></i><i><b><u>underlined!</u></b></i>
            <span background="blue">This is a test of bg color</span>
            <span foreground="blue">This is a test of fg color</span>
            <span foreground="white" background="blue">This is a test of fg and bg color</span>
            """)

        self.tv.set_buffer(self.ipb)

        self.tag_italic = self.ipb.create_tag("italic", style=Pango.Style.ITALIC)
        button_italic = Gtk.ToolButton()
        button_italic.set_icon_name("format-text-italic-symbolic")
        button_italic.connect("clicked",
                              self.on_button_clicked,
                              self.tag_italic)
        self.editBox.add(button_italic)

        button_bold = Gtk.ToolButton()
        button_bold.set_icon_name("format-text-bold-symbolic")
        self.editBox.add(button_bold)

        button_underline = Gtk.ToolButton()
        button_underline.set_icon_name("format-text-underline-symbolic")
        self.editBox.add(button_underline)

        button_blue = Gtk.ToggleButton()
        button_blue.set_label("Blue")
        self.editBox.add(button_blue)

        button_red = Gtk.ToggleButton()
        button_red.set_label("Red")
        self.editBox.add(button_red)

        self.vb.add(self.editBox)
        self.vb.add(self.sw)
        self.actionBox = Gtk.HButtonBox()

        self.qb = Gtk.Button()
        self.qb.set_label('Quit')

        self.pmbut = Gtk.Button()
        self.pmbut.set_label('Print Markup')
        self.pmbut.connect('clicked', self.print_markup)
        self.actionBox.add(self.pmbut)

        self.pselectbut = Gtk.Button()
        self.pselectbut.set_label('Print Selection')
        self.pselectbut.connect('clicked', self.print_selection)
        self.actionBox.add(self.pselectbut)

        self.qb.connect('clicked',
                        lambda *args: self.w.destroy() or Gtk.main_quit())
        self.actionBox.add(self.qb)

        self.vb.add(self.actionBox)
        self.w.add(self.vb)
        self.w.show_all()

    def on_button_clicked(self, widget, tag):
        self.ipb.apply_tag_to_selection(tag)
        # self.ipb.remove_tag_from_selection(tag)

    def print_markup(self, *args):
        print(self.ipb.get_text(include_hidden_chars=True))

    def print_selection(self, *args):
        selection = self.ipb.get_selection()
        print(self.ipb.get_text(*selection))


if __name__ == '__main__':
    se = SimpleEditor()
    se.w.connect('delete-event', lambda *args: Gtk.main_quit())
    Gtk.main()
