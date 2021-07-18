# Copyright (C) 2005 Thomas M. Hinkle
# Copyright (C) 2009 Rolf Leggewie
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
from typing import Optional, Union

from gi.repository import Gtk, Pango

from gourmet.gtk_extras.pango_html import PangoToHtml


class PangoBuffer(Gtk.TextBuffer):
    """A supercharged Gtk.TextBuffer that handles HTML or Pango markup in its
    content"""

    def __init__(self):
        super().__init__()

        self.tag_bold = self.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic = self.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline = self.create_tag("underline",
                                             underline=Pango.Underline.SINGLE)

    def set_text(self, text: Union[str, bytes]) -> None:
        super().set_text('')  # Clear the widget
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

    def get_selection_bounds(self):
        """A get_selection_bounds that returns either the selection, or
        the word where the cursor is at
        """
        bounds = super().get_selection_bounds()

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

    def on_markup_toggle(self,
                         widget: Gtk.Action,
                         tag: Gtk.TextTag) -> None:
        """Apply or remove markup to selected text"""
        bounds = self.get_selection_bounds()
        if not bounds:
            return

        start, end = bounds

        prop = None
        if tag == self.tag_bold:
            prop = 'weight-set'
        elif tag == self.tag_italic:
            prop = 'style-set'
        elif tag == self.tag_underline:
            prop = 'underline-set'

        set_tag = [t for t in start.get_tags() if t.get_property(prop)]
        if set_tag:
            self.remove_tag(*set_tag, start, end)
        else:
            self.apply_tag(tag, start, end)

    def remove_all_tags(self, widget):
        """Remove all tags from selection"""
        selection = self.get_selection_bounds()
        if not selection:
            return
        start, end = selection
        for tag in start.get_tags():
            self.remove_tag(tag, start, end)


class SimpleEditor:
    """A demo of the TextBufferedMarkup class"""
    def __init__(self):
        self.w = Gtk.Window()
        vb = Gtk.VBox()
        tv = Gtk.TextView()
        sw = Gtk.ScrolledWindow()
        sw.add(tv)

        self.pb = PangoBuffer()
        self.pb.set_text("""<b>This is bold</b>. <i>This is italic</i>
<i><b>This is bold, italic, and <u>underlined!</u></b></i>
<span background="blue">This is a test of bg color</span>
<span foreground="blue">This is a test of fg color</span>
<span foreground="white" background="blue">This is a test of fg and bg color</span>  # noqa
""")
        tv.set_buffer(self.pb)

        edit_box = Gtk.HButtonBox()

        normal = Gtk.Button()
        normal.set_label('Normal')
        normal.connect('clicked', self.pb.remove_all_tags)
        edit_box.add(normal)

        button_italic = Gtk.ToolButton()
        button_italic.set_icon_name("format-text-italic-symbolic")
        button_italic.connect("clicked",
                              self.pb.on_markup_toggle,
                              self.pb.tag_italic)
        edit_box.add(button_italic)

        button_bold = Gtk.ToolButton()
        button_bold.set_icon_name("format-text-bold-symbolic")
        button_bold.connect('clicked',
                            self.pb.on_markup_toggle,
                            self.pb.tag_bold)
        edit_box.add(button_bold)

        button_underline = Gtk.ToolButton()
        button_underline.set_icon_name("format-text-underline-symbolic")
        button_underline.connect('clicked',
                                 self.pb.on_markup_toggle,
                                 self.pb.tag_underline)
        edit_box.add(button_underline)

        button_blue = Gtk.ToggleButton()
        button_blue.set_label("Blue")
        edit_box.add(button_blue)

        button_red = Gtk.ToggleButton()
        button_red.set_label("Red")
        edit_box.add(button_red)

        vb.add(edit_box)
        vb.add(sw)

        action_box = Gtk.HButtonBox()

        pmbut = Gtk.Button()
        pmbut.set_label('Print Markup')
        pmbut.connect('clicked', self.print_markup)
        action_box.add(pmbut)

        pselectbut = Gtk.Button()
        pselectbut.set_label('Print Selection')
        pselectbut.connect('clicked', self.print_selection)
        action_box.add(pselectbut)

        qb = Gtk.Button()
        qb.set_label('Quit')
        qb.connect('clicked',
                   lambda *args: self.w.destroy() or Gtk.main_quit())
        action_box.add(qb)

        vb.add(action_box)
        self.w.add(vb)
        self.w.show_all()

    def print_markup(self, *args):
        print(self.pb.get_text(include_hidden_chars=True))

    def print_selection(self, *args):
        selection = self.pb.get_selection_bounds()
        print(self.pb.get_text(*selection))


if __name__ == '__main__':
    se = SimpleEditor()
    se.w.connect('delete-event', lambda *args: Gtk.main_quit())
    Gtk.main()
