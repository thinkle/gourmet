# we keep this around because not all gnomeprints support the PANGO LAYOUT stuff we've moved to.
import gtk, gnomeprint, gnomeprint.ui,  re
import exporter
from gourmet import ImageExtras,gglobals,convert
from gourmet.gdebug import *
from gettext import gettext as _

def do_print(dialog, job):
    pc = gnomeprint.Context(dialog.get_config())
    job.render(pc)
    pc.close()

class renderer:
    def __init__(self, job=None):
        if not job:
            job = gnomeprint.Job(gnomeprint.config_default())
        self.job = job
        self.gpc = self.job.get_context()
        self.width, self.height = gnomeprint.job_get_page_size_from_config(job.get_config())
        self.margin = 48
        self.wmargin = 100
        self.left = self.wmargin
        self.right = self.width - self.wmargin
        self.top = self.height - self.margin
        self.bottom = self.margin
        self.default_left = self.left
        self.default_right = self.right      
        # units are  1/72 in.
        self.head_indent = -30
        self.move_down_hooks = []
        # <<<begin drawing>>>
        self.n = 0
        self.new_page()
        self.adjust = 0 # allows adjustments for more than one page...
        self.default_font='Serif'
        self.default_head='Sans'
        self.default_head_size=16
        self.default_head_style='Bold'
        self.set_font()

    def set_font (self, fontname=None, size=12, style='Regular'):
        if not fontname: fontname = self.default_font
        self.font = gnomeprint.font_find_closest("%s %s"%(fontname,style),size)
        self.lheight = size * 1.25
        self.gpc.setfont(self.font)

    def end (self):
        self.gpc.showpage()
        self.job.close()

    def setup_columns (columns=2, depth=None, ):
        pass

    def write_pixbuf (self, pixbuf, inline=True, align='left', border=10):
        """Align can take "left", "right", or "center".
        "center" implies not inline."""
        raw_image = pixbuf.get_pixels()
        has_alpha = pixbuf.get_has_alpha()
        rowstride = pixbuf.get_rowstride()
        height = pixbuf.get_height()
        width = pixbuf.get_width()
        # if we're not at the top, give us our border
        if not self.yposition >= self.top:
            self.move_down(border)
        if (self.yposition - height) <= self.bottom:
            self.new_page()
        self.gpc.gsave()
        if align=='left':
            left = self.left
        if align=='right':
            left = self.right - width
        if align=='center':
            left = (self.width - width)/2
        self.gpc.translate(left,self.yposition-height)
        #self.gpc.moveto(self.left, self.yposition)
        self.gpc.scale(width,height)
        if has_alpha: self.gpc.rgbaimage(raw_image, width, height, rowstride)
        else: self.gpc.rgbimage(raw_image, width, height, rowstride)
        self.gpc.grestore()
        # don't allow "inline" if our width is less than a few words
        remaining_width = self.right - self.left - width -border
        if remaining_width < self.font.get_width_utf8("A reasonable length"):
            inline = False
        if inline and align != 'center':
            # we shift the left and right side to allow for our image
            if align=='left':
                self.left = left + width + border
            else:
                self.right = left - border
            # we set up a hook to reset margins once we're beyond the image.
            image_end_pos = self.yposition
            def reset_margins (yposition):
                if yposition <= image_end_pos - (height + border):
                    self.left = self.default_left
                    self.right = self.default_right
                    self.move_down_hooks.remove(self.reset_margin_hook)
            self.reset_margin_hook=reset_margins
            self.move_down_hooks.append(self.reset_margin_hook)
        else:
            self.move_down(height + border)

    def write_line (self, text, indent=0):
        self.move_down(self.lheight)
        self.gpc.moveto(self.left + indent, self.yposition)
        self.gpc.show(text)

    def write_heading (self, line, size=None, fontname=None, style=None,
                       indent=None, space_before=1, space_after=1):
        if not size: size=self.default_head_size
        if not fontname: fontname=self.default_head
        if not style: style=self.default_head_style
        if indent == None: indent=self.head_indent
        self.set_font(fontname,size=16,style=style)
        if self.yposition <= self.lheight * 3:
            # start a new page if we're within three lines
            # of the bottom
            self.new_page()
        if self.yposition < self.top  and space_before:
            # give us space before if we're not at the top
            # of the page.
            self.move_down(self.lheight * space_before)
        self.write_paragraph(line, indent=indent)
        if space_after:
            self.move_down(self.lheight * space_after)
        self.set_font()
    
    def write_paragraph (self, text, indent=0, space=False,
                         first_indent=0):
        """first_indent is *relative* to indent."""
        words = text.split()
        line = []
        n = 0
        linestr = ""
        if space:
            self.move_down(self.lheight)
        first_line_flag = True
        while n < len(words):
            prev_line = linestr
            linestr += " %s"%words[n]
            lwidth = self.font.get_width_utf8(linestr)
            # this is mildly hackish: custom wmargin only modifies
            # our left margin, since this is what I'd usually want.
            if first_line_flag:
                length = self.right - self.left - indent - first_indent
            else:
                length = self.right - self.left - indent
            if lwidth >= length:
                # if we're over, we back up one...
                if first_line_flag:
                    self.write_line(prev_line, indent=indent + first_indent)
                    first_line_flag = False
                else:
                    self.write_line(prev_line, indent=indent)
                linestr=words[n]
            n += 1
        if first_line_flag:
            indent = indent + first_indent
        self.write_line(linestr, indent=indent)

    def new_page (self):
        if self.n > 0:
            self.gpc.showpage()
        self.n += 1
        self.gpc.beginpage("%s"%self.n)
        self.yposition = self.top

    def move_down (self, amt):
        """ Move position down """
        self.yposition = self.yposition - amt
        # we allow functions to act on the position each time we
        # move down. This allows us to handle things like embedded
        # images and columns.
        if self.move_down_hooks:
            for f in self.move_down_hooks:
                f(self.yposition)
        if self.yposition <= self.margin:
            self.new_page()

def show_preview(dialog,job):
    #job = gnomeprint.Job(dialog.get_config())
    #render_to_job(job)
    w = gnomeprint.ui.JobPreview(job, "Print Preview")
    w.set_property('allow-grow', 1)
    w.set_property('allow-shrink', 1)
    w.set_transient_for(dialog)
    w.show_all()
    w.present()

def print_dialog_response(dialog, resp, job):
    if resp == gnomeprint.ui.DIALOG_RESPONSE_PREVIEW:
	show_preview(dialog,job)
    elif resp == gnomeprint.ui.DIALOG_RESPONSE_CANCEL:
	dialog.destroy()
    elif resp == gnomeprint.ui.DIALOG_RESPONSE_PRINT:
	do_print(dialog, job)
	dialog.destroy()

def render_to_job (job):
    r = renderer(job)
    for f in ['Sans','Serif','Monospace','Arial']:
        for s in [12,14,16,18,24]:
            for sty in ['Regular','Bold','Italic']:
                r.set_font(f,s,sty)
                r.write_paragraph( "This is a paragraph in %s %s %s. "%(f,sty,s) * 5)
    for i in xrange(10):
        r.write_paragraph( "This is paragraph %s, indeed! "%i * 30 )
    for i in xrange(10):
        r.write_paragraph(
            "This is a paragraph that's not indented, and I have eaten a total of %s chocolate bars. "%i * 25,
            indent=0, space=True
            )
    r.end()

class print_writer (renderer):
    def __init__ (self, show_dialog=True, dialog_title=_("Print"), dialog_kwargs={},
                  dialog_parent=None):
        renderer.__init__(self)
        self.show_dialog = show_dialog
        self.dialog_parent = dialog_parent
        self.dialog_title = dialog_title
        self.dialog_kwargs = dialog_kwargs

    def write (self, text):
        lines = text.split("\n")
        if lines[-1]=='':
            lines = lines[0:-1]
        for l in lines: self.write_line(l)

    def close (self):
        self.end()
        if self.show_dialog:
            dialog = gnomeprint.ui.Dialog(self.job, self.dialog_title,
                                          gnomeprint.ui.DIALOG_RANGE | gnomeprint.ui.DIALOG_COPIES,
                                          **self.dialog_kwargs)
            flags = (gnomeprint.ui.RANGE_CURRENT
                     |gnomeprint.ui.RANGE_ALL
                     |gnomeprint.ui.RANGE_RANGE
                     |gnomeprint.ui.RANGE_SELECTION)            
            dialog.construct_range_page(flags, 1, 1, _("_Current"), _("_Range"))
            dialog.connect('response', print_dialog_response, self.job)
            if self.dialog_parent: dialog.set_transient_for(self.dialog_parent)
            dialog.show()
        
class RecRenderer (print_writer):
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None, change_units=True):
        print_writer.__init__(self, show_dialog=True, dialog_title=dialog_title,
                              dialog_parent=dialog_parent)
        do_new_page = False
        for r in recs:
            if do_new_page:
                self.new_page()
            r=RecWriter(rd, r, self, mult, change_units)
            do_new_page = True # put pagebreaks between recipes...
        self.close()
        

class RecWriter (exporter.exporter_mult):
    def __init__ (self, rd, r, printwriter, mult=1, change_units=True):
        self.print_writer = printwriter
        self.r = r
        exporter.exporter_mult.__init__(self, rd, r, out=None, mult=mult,
                                        change_units=True)

    def write_head (self):
        pass

    def write_image (self, image):
        pb = ImageExtras.get_pixbuf_from_jpg(image)
        self.print_writer.write_pixbuf(pb, align='right')

    def write_attr (self, label, text):
        attr=gglobals.NAME_TO_ATTR[label]
        if attr=='title':
            self.print_writer.write_heading(text)
            return
        if attr=='servings':
            num = convert.frac_to_float(text)
            if num:
                text = convert.float_to_frac(num * self.mult)
            else:
                return
        self.print_writer.write_paragraph("%s: %s"%(label, text))

    def write_text (self, label, text):
        self.print_writer.write_heading(label, space_after=0, space_before=0.5)
        pars = re.split("\n+", text)
        for p in pars: self.print_writer.write_paragraph(p, space=True)
        
    def write_inghead (self):
        self.print_writer.write_heading(_('Ingredients'), space_before=0.5, space_after=0)

    def write_grouphead (self, name):
        self.print_writer.write_heading(name,
                                        size=self.print_writer.default_head_size-2,
                                        style='Regular',
                                        indent=0,
                                        space_before=0.5,
                                        space_after=0)

    def write_ing (self, amount="1", unit=None, item=None, key=None, optional=False):
        amt,unit=self.multiply_amount(amount,unit)
        if amount: line = amt + " "
        else: line = ""
        if unit: line += "%s "%unit
        if item: line += "%s"%item
        if optional: line += " (%s)"%_("optional")
        self.print_writer.write_paragraph(line)

class SimpleWriter (print_writer):
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        print_writer.__init__(self,dialog_parent=dialog_parent,show_dialog=show_dialog)

    def write_header (self, text):
        self.write_heading(text, size=14, space_before=0.5, space_after=0)

    def write_subheader (self, text):
        self.write_heading(text, size=12, style="Regular", space_after=0, space_before=0.5)

if __name__ == '__main__':
    #dialog = show_print_dialog()
    #dialog.connect("destroy", lambda *args: gtk.main_quit())
    #gtk.mainloop()
    for do_this in range(2):
        o = print_writer(show_dialog=True)
        for h in range(10):
            o.write_heading('Heading %s'%h, size=16+h, indent=None)
            if (h/2) == float(h)/2:
                if h > 5: align='right'
                else: align='left'
            else: align='center'
            img = gtk.gdk.pixbuf_new_from_file("/tmp/gourmet_temporary_img.jpg")
            o.write_pixbuf(img, align=align)
            for n in range(15):
                o.write_paragraph('This is job number %s. The is paragraph number %s.  '%(do_this,n) * 10, first_indent=25)
        o.close()
    gtk.main()
