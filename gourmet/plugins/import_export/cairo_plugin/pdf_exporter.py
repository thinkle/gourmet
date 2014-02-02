from gourmet.exporters.MarkupString import MarkupString
from gourmet.gdebug import debug

import pango

class CairoRenderer:

    def __init__(self):
        self.positions = [[[0,0]]]
        self.paragraphs = [[]]

    def setup_defaults (self):
        self.default_font='Serif'
        self.default_head_family='Sans'
        self.default_head_size=16
        self.default_head_style='normal'
        self.default_head_weight='bold'

    def new_page (self):
        self.positions.append([[0,0]])
        self.paragraphs.append([])

    def escape (self, text):
        pos = 0
        out = ""
        for m in self.simple_escaper.finditer(text):
            s=m.start()
            e=m.end()
            out += text[pos:s]
            out += "&amp;"
            pos = e
        out += text[pos:]
        return out

    def write_paragraph (self, markup, indent=0, space=False, first_indent=0, force=False):
        print "write_paragraph %s %s %s %s %s" % (markup, indent, space, first_indent, force)
        "Print some markup to the supplied context"
        # first, we do a simple escape routine, just in case we're
        # not actually being handed valid markup. Not fail-safe by
        # any means, but should save us from the common "&"s that slip
        # through
        markup=self.escape(markup)
        #need to use pango.Layout to format paragraphs
        #for each block of text
        para = self.make_pango_layout()
        para.set_wrap(pango.WRAP_WORD_CHAR)
        if first_indent: para.set_indent(int(first_indent)*pango.SCALE)
        para.set_justify(True)
        para.set_width(int(self.right-self.left)*pango.SCALE)
        para.set_markup(markup)
        if space: para.set_spacing(1)
        x,y=para.get_pixel_size()
        print 'paragraph of size ',x,y
        botpos = self.positions[-1][-1][1] + y
        print 'moves bottom to ',botpos, ' bottom at %s'%self.bottom
        if botpos > self.bottom and not force:
            # running off the bottom of the page. In 2.6 we'll be able to handle this gracefully.
            # in 2.4, we create a terrible, no-good, very bad hack.
            # (right is tied to left-to-right languages...) and we're definitely tied to horizontal
            # languages (left-to-right/right-to-left) in this whole routine.
            room = self.bottom-self.positions[-1][-1][1]
            shrink_by_percentage = float(room) / y
            mymarkup = MarkupString(markup)
            char = int(len(mymarkup.raw)*shrink_by_percentage)
            # we automatically backup until we find a space. If there are no spaces, we fail.
            try:
                while mymarkup[char]!=" ":
                    char -= 1
            except IndexError:
                char += 1
            startmark = mymarkup[:char]
            endmark = mymarkup[char+1:]
            self.write_paragraph(startmark,force=True)
            self.new_page()
            self.write_paragraph(endmark,indent=False)
        else:
            self.paragraphs[-1].append(para)
            self.move_down(y)

    def write_heading (self, line,
                       size=16,
                       font_family='Sans',
                       style = pango.STYLE_NORMAL,
                       weight=pango.WEIGHT_BOLD,
                       indent=None, space_before=1, space_after=1):

        if not size: size=self.default_head_size
        if type(size)==int:
            if size < 5000: size = size * 1000 # convenience, in case we typed a normal fontsize :)

        fd = pango.FontDescription()
        fd.set_family(font_family)
        fd.set_style(style)
        fd.set_weight(weight)
        fd.set_size(size)

        if space_before:
            space_before = int(space_before+0.9)
            line = "\n"*space_before + line
        if space_after:
            space_after = int(space_after+0.9)
            line = line + "\n"*space_after

        para = self.make_pango_layout()
        para.set_font_description(fd)
        para.set_text(line)
        self.paragraphs[-1].append(para)
        _,y=para.get_pixel_size()
        self.move_down(y)

    def move_down (self, amt):
        x = self.left
        y = self.positions[-1][-1][1] + amt
        self.positions[-1].append([x, y])
        
        if self.move_down_hooks:
            for f in self.move_down_hooks:
                f(y)
            if y >= self.bottom:
                self.new_page()

    def write_pixbuf (self, pixbuf, inline=True, align='left', border=30):
        print 'write_pixbuf inline=%s align=%s border=%s'%(inline, align, border)
        debug('write_pixbuf inline=%s align=%s border=%s'%(inline, align, border),3)
        """Align can take "left", "right", or "center".
        "center" implies not inline."""
        height = pixbuf.get_height()
        width = pixbuf.get_width()
        # if we're not at the top, give us our border
        if self.positions[-1][-1][1] > self.top:
            self.move_down(border)
        if (self.positions[-1][-1][1] + height) >= self.bottom:
            self.new_page()
            print "write_pixbuf called new_page"

        if align=='left':
            left = 0
        if align=='right':
            left = self.width - width
        if align=='center':
            left = (self.width - width)/2

        y = self.positions[-1][-1][1]
        self.positions[-1].append([left, y])
        print self.positions #[-1][-1]
        self.paragraphs[-1].append(pixbuf)

        # don't allow "inline" if our remaining width is less half
        remaining_width = self.right - self.left - width - border
        if remaining_width < 0.4 * width:
            inline = False
        if inline and align != 'center':
            # we shift the left and right side to allow for our image
            if align=='left':
                self.left = self.left + width + border
            else: # align=='right'
                self.right = self.right - width - border
            # we set up a hook to reset margins once we're beyond the image.
            image_end_pos = self.positions[-1][-1][1]
            def reset_margins (yposition):
                debug('reset_margins ',3)
                print('reset_margins')
                if yposition >= image_end_pos: # - (height + border):
                    self.left = self.default_left
                    self.right = self.default_right
                    self.move_down_hooks.remove(self.reset_margin_hook)
            self.reset_margin_hook=reset_margins

            self.move_down_hooks.append(self.reset_margin_hook)
        else:
            self.move_down(height + border)

    