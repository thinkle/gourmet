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
from typing import Union

import gi
gi.require_versions({"Gtk": "3.0", "Pango": "1.0"})
from gi.repository import Pango
from gi.repository import Gtk
from gi.repository import GObject
import xml.sax.saxutils
from gourmet.gdebug import debug

class PangoBuffer (Gtk.TextBuffer):
    # TODO: Fix this in 2to3
    # desc_to_attr_table = {
    #     'family':[Pango.AttrFamily,""],
    #     'style':[Pango.AttrStyle,Pango.Style.NORMAL],
    #     'variant':[Pango.AttrVariant,Pango.VARIANT_NORMAL],
    #     'weight':[Pango.AttrWeight,Pango.Weight.NORMAL],
    #     'stretch':[Pango.AttrStretch,Pango.STRETCH_NORMAL],
    #     }
    desc_to_attr_table = {}
    pango_translation_properties={}
    # pango_translation_properties={
    #         # pango ATTR TYPE : (pango attr property / tag property)
    #         Pango.ATTR_SIZE : 'size',
    #         Pango.ATTR_WEIGHT: 'weight',
    #         Pango.ATTR_UNDERLINE: 'underline',
    #         Pango.ATTR_STRETCH: 'stretch',
    #         Pango.ATTR_VARIANT: 'variant',
    #         Pango.ATTR_STYLE: 'style',
    #         Pango.ATTR_SCALE: 'scale',
    #         Pango.ATTR_STRIKETHROUGH: 'strikethrough',
    #         Pango.ATTR_RISE: 'rise',
    #         }
    attval_to_markup={}
    # attval_to_markup={
    #         'underline':{Pango.Underline.SINGLE:'single',
    #                      Pango.Underline.DOUBLE:'double',
    #                      Pango.Underline.LOW:'low',
    #                      Pango.Underline.NONE:'none'},
    #         'stretch':{Pango.STRETCH_ULTRA_EXPANDED:'ultraexpanded',
    #                    Pango.STRETCH_EXPANDED:'expanded',
    #                    Pango.STRETCH_EXTRA_EXPANDED:'extraexpanded',
    #                    Pango.STRETCH_EXTRA_CONDENSED:'extracondensed',
    #                    Pango.STRETCH_ULTRA_CONDENSED:'ultracondensed',
    #                    Pango.STRETCH_CONDENSED:'condensed',
    #                    Pango.STRETCH_NORMAL:'normal',
    #                    },
    #         'variant':{Pango.VARIANT_NORMAL:'normal',
    #                    Pango.VARIANT_SMALL_CAPS:'smallcaps',
    #                    },
    #         'style':{Pango.Style.NORMAL:'normal',
    #                  Pango.Style.OBLIQUE:'oblique',
    #                  Pango.Style.ITALIC:'italic',
    #                  },
    #         'stikethrough':{1:'true',
    #                         True:'true',
    #                         0:'false',
    #                         False:'false'},
    #         }
    def __init__ (self):
        self.tagdict = {}
        self.tags = {}
        #self.buf = buf
        #self.set_text(txt)
        Gtk.TextBuffer.__init__(self)

    def set_text (self, txt: Union[str, bytes]) -> None:
        if isinstance(txt, bytes):
            # data loaded from the database are bytes, not str
            txt = txt.decode()
        Gtk.TextBuffer.set_text(self, txt)   # TODO: should clear the buffer of text
        try:
            self.parsed, attributes, self.txt, self.separator = Pango.parse_markup(txt, -1, '\x00')
        except Exception as e:  # unescaped text (g-markup-error-quark), eg. contains &amp
            print(f"Problem encountered escaping text: {txt}: {e}")
            import traceback; traceback.print_exc()
            txt=xml.sax.saxutils.escape(txt)
            self.parsed, attributes, self.txt, self.separator = Pango.parse_markup(txt, -1, '\x00')

        self.add_attributes_to_buffer(attributes)

    def add_attributes_to_buffer(self, attributes: Pango.AttrList):
        """Add html markup attributes to the text buffered in this object.

        Given a list of text attributes, insert the markup tags around the text
        delimited by the indices provided by each `item` attribute in the list.
        """
        attrs_iter = attributes.get_iterator()
        while attrs_iter.next():
            start, end = attrs_iter.range()
            tags = []
            ret = attrs_iter.get_font(Pango.FontDescription(), None, None)
            if ret is not None:
                font, lang, attrs = ret
                tags = self.get_tags_from_attrs(font, lang, attrs)

            text = self.txt[start:end]
            try:
                item = self.get_end_attrs_iter()
            except AttributeError:
                item = self.get_end_iter()
            self.insert_with_tags(item,text,*tags)

        #  attrs_iter.destroy()  # TODO: check why calling destroy segfaults.

    def get_tags_from_attrs (self, font,lang,attrs):
        tags = []
        if font:
            font,fontattrs = self.fontdesc_to_attrs(font)
            fontdesc = font.to_string()
            if fontattrs:
                attrs.extend(fontattrs)
            if fontdesc and fontdesc!='Normal':
                if font.to_string() not in self.tags:
                    tag=self.create_tag()
                    tag.set_property('font-desc',font)
                    if tag not in self.tagdict: self.tagdict[tag]={}
                    self.tagdict[tag]['font_desc']=font.to_string()
                    self.tags[font.to_string()]=tag
                tags.append(self.tags[font.to_string()])
        if lang:
            if lang not in self.tags:
                tag = self.create_tag()
                tag.set_property('language',lang)
                self.tags[lang]=tag
            tags.append(self.tags[lang])
        if attrs:
            for a in attrs:
                if a.type == Pango.ATTR_FOREGROUND:
                    gdkcolor = self.pango_color_to_gdk(a.color)
                    key = 'foreground%s'%self.color_to_hex(gdkcolor)
                    if key not in self.tags:
                        self.tags[key]=self.create_tag()
                        self.tags[key].set_property('foreground-gdk',gdkcolor)
                        self.tagdict[self.tags[key]]={}
                        self.tagdict[self.tags[key]]['foreground']="#%s"%self.color_to_hex(gdkcolor)
                    tags.append(self.tags[key])
                if a.type == Pango.ATTR_BACKGROUND:
                    gdkcolor = self.pango_color_to_gdk(a.color)
                    key = 'background%s'%self.color_to_hex(gdkcolor)
                    if key not in self.tags:
                        self.tags[key]=self.create_tag()
                        self.tags[key].set_property('background-gdk',gdkcolor)
                        self.tagdict[self.tags[key]]={}
                        self.tagdict[self.tags[key]]['background']="#%s"%self.color_to_hex(gdkcolor)
                    tags.append(self.tags[key])
                if a.type in self.pango_translation_properties:
                    prop=self.pango_translation_properties[a.type]
                    #print 'setting property %s of %s (type: %s)'%(prop,a,a.type)
                    val=getattr(a,'value')
                    #tag.set_property(prop,val)
                    mval = val
                    if prop in self.attval_to_markup:
                        #print 'converting ',prop,' in ',val
                        if val in self.attval_to_markup[prop]:
                            mval = self.attval_to_markup[prop][val]
                        else:
                            debug("hmmm, didn't know what to do with value %s"%val,0)
                    key="%s%s"%(prop,val)
                    if key not in self.tags:
                        self.tags[key]=self.create_tag()
                        self.tags[key].set_property(prop,val)
                        self.tagdict[self.tags[key]]={}
                        self.tagdict[self.tags[key]][prop]=mval
                    tags.append(self.tags[key])
                else:
                    debug("Don't know what to do with attr %s"%a,1)
        return tags

    def get_tags (self):
        tagdict = {}
        for pos in range(self.get_char_count()):
            iter=self.get_iter_at_offset(pos)
            for tag in iter.get_tags():
                if tag in tagdict:
                    if tagdict[tag][-1][1] == pos - 1:
                        tagdict[tag][-1] = (tagdict[tag][-1][0],pos)
                    else:
                        tagdict[tag].append((pos,pos))
                else:
                    tagdict[tag]=[(pos,pos)]
        return tagdict

    def get_text (self, start=None, end=None, include_hidden_chars=True):
        tagdict=self.get_tags()
        if not start: start=self.get_start_iter()
        if not end: end=self.get_end_iter()
        txt = Gtk.TextBuffer.get_text(self, start, end,
                                      include_hidden_chars=False)
        cuts = {}
        for k,v in list(tagdict.items()):
            if k not in self.tagdict: continue
            stag,etag = self.tag_to_markup(k)
            for st,e in v:
                if st in cuts: cuts[st].append(stag) #add start tags second
                else: cuts[st]=[stag]
                if e+1 in cuts: cuts[e+1]=[etag]+cuts[e+1] #add end tags first
                else: cuts[e+1]=[etag]
        last_pos = 0
        outbuff = ""
        cut_indices = list(cuts.keys())
        cut_indices.sort()
        soffset = start.get_offset()
        eoffset = end.get_offset()
        cut_indices = [i for i in cut_indices if eoffset >= i >= soffset]
        for c in cut_indices:
            if not last_pos==c:
                outbuff += xml.sax.saxutils.escape(txt[last_pos:c])
                last_pos = c
            for tag in cuts[c]:
                outbuff += tag
        outbuff += xml.sax.saxutils.escape(txt[last_pos:])
        return outbuff

    def tag_to_markup (self, tag):
        stag = "<span"
        for k,v in list(self.tagdict[tag].items()):
            stag += ' %s="%s"'%(k,v)
        stag += ">"
        return stag,"</span>"

    def fontdesc_to_attrs (self,font):
        nicks = font.get_set_fields().value_nicks
        attrs = []
        for n in nicks:
            if n in self.desc_to_attr_table:
                Attr,norm = self.desc_to_attr_table[n]
                # create an attribute with our current value
                attrs.append(Attr(getattr(font,'get_%s'%n)()))
                # unset our font's value
                getattr(font,'set_%s'%n)(norm)
        return font,attrs

    def pango_color_to_gdk (self, pc):
        return Gdk.Color(pc.red,pc.green,pc.blue)

    def color_to_hex (self, color):
        hexstring = ""
        for col in 'red','green','blue':
            hexfrag = hex(getattr(color,col)/(16*16)).split("x")[1]
            if len(hexfrag)<2: hexfrag = "0" + hexfrag
            hexstring += hexfrag
        return hexstring

    def apply_font_and_attrs (self, font, attrs):
        tags = self.get_tags_from_attrs(font,None,attrs)
        for t in tags: self.apply_tag_to_selection(t)

    def remove_font_and_attrs (self, font, attrs):
        tags = self.get_tags_from_attrs(font,None,attrs)
        for t in tags: self.remove_tag_from_selection(t)

    def setup_default_tags (self):
        self.italics = self.get_tags_from_attrs(None,None,[Pango.AttrStyle('italic')])[0]
        self.bold = self.get_tags_from_attrs(None,None,[Pango.AttrWeight('bold')])[0]
        self.underline = self.get_tags_from_attrs(None,None,[Pango.AttrUnderline('single')])[0]

    def get_selection (self):
        bounds = self.get_selection_bounds()
        if not bounds:
            iter=self.get_iter_at_mark(self.insert_)
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

    def apply_tag_to_selection (self, tag):
        selection = self.get_selection()
        if selection:
            self.apply_tag(tag,*selection)

    def remove_tag_from_selection (self, tag):
        selection = self.get_selection()
        if selection:
            self.remove_tag(tag,*selection)

    def remove_all_tags (self):
        selection = self.get_selection()
        if selection:
            for t in list(self.tags.values()):
                self.remove_tag(t,*selection)

class InteractivePangoBuffer (PangoBuffer):
    def __init__ (self,
                  normal_button=None,
                  toggle_widget_alist=[]):
        """An interactive interface to allow marking up a Gtk.TextBuffer.
        txt is initial text, with markup.
        buf is the Gtk.TextBuffer
        normal_button is a widget whose clicked signal will make us normal
        toggle_widget_alist is a list that looks like this:
        [(widget, (font,attr)),
         (widget2, (font,attr))]
         """
        PangoBuffer.__init__(self)
        if normal_button: normal_button.connect('clicked',lambda *args: self.remove_all_tags())
        self.tag_widgets = {}
        self.internal_toggle = False
        self.insert_ = self.get_insert()
        self.connect('mark-set',self._mark_set_cb)
        self.connect('changed',self._changed_cb)
        for w,tup in toggle_widget_alist:
            self.setup_widget(w,*tup)

    def setup_widget_from_pango (self, widg, markupstring):
        """setup widget from a pango markup string"""
        #font = Pango.FontDescription(fontstring)
        _, a, t, s = Pango.parse_markup(markupstring, -1, '\x00')
        ai=a.get_iterator()
        ret = ai.get_font(Pango.FontDescription(), None, None)
        if ret is not None:
            font, _, attrs = ret
        else:
            font = attrs = None
        return self.setup_widget(widg,font,attrs)

    def setup_widget (self, widg, font, attr):
        tags=self.get_tags_from_attrs(font,None,attr)
        self.tag_widgets[tuple(tags)]=widg
        return widg.connect('toggled',self._toggle,tags)

    def _toggle (self, widget, tags):
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
    def __init__ (self):
        self.w = Gtk.Window()
        self.vb = Gtk.VBox()
        self.editBox = Gtk.HButtonBox()
        self.nb = Gtk.Button('Normal')
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
        #    Here are some more: 1-2, 2-3, 3-4, 10-20, 30-40, 50-60
        #    This is <span color="blue">blue</span>, <span color="red">red</span> and <span color="green">green</span>""")
        #self.ipb.set_text("""This is a numerical range (three hundred and fifty to four hundred) 350-400 which may get messed up.
        #Here are some more: 1-2, 2-3, 3-4, 10-20, 30-40, 50-60""")

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

    def print_markup (self,*args):
        print(self.ipb.get_text())

if __name__ == '__main__':
    se = SimpleEditor()
    se.w.connect('delete-event',lambda *args: Gtk.main_quit())
    Gtk.main()
