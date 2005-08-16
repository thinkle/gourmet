import gtk, gnomeprint, gnomeprint.ui,  re, pango
import exporter
from MarkupString import MarkupString
from gourmet import ImageExtras,gglobals,convert
from gourmet.gdebug import *
from gettext import gettext as _
import xml.sax.saxutils

def do_print(dialog, job):
    debug('do_print',0)
    pc = gnomeprint.Context(dialog.get_config())
    job.render(pc)
    pc.close()

class renderer:
    def __init__ (self):
        "Print Preview the document"
        self.pn = 0
        self.config = gnomeprint.config_default()
        self.job = gnomeprint.Job(self.config)
        self.gpc = self.job.get_context()
        self.setup_defaults()
        self.setup_page()
        self.move_down_hooks = []
        self.simple_escaper = re.compile("&(?=[^ ;]*($| ))")

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

    def end (self):
        self.gpc.showpage()
        self.job.close()

    def setup_defaults (self):
        self.default_font='Serif'
        self.default_head_family='Sans'
        self.default_head_size=16
        self.default_head_style='normal'
        self.default_head_weight='bold'

    def setup_page (self):
        self.width,self.height = gnomeprint.job_get_page_size_from_config(self.job.get_config())
        self.margin = 50
        self.top = self.height - self.margin
        self.bottom = self.margin
        self.left = self.margin
        self.right = self.width - self.margin
        self.default_left = self.left
        self.default_right = self.right      
        self.new_page()

    def new_page (self):
        if self.pn > 0:
            self.gpc.showpage()
        self.pn += 1
        self.gpc.beginpage("%s"%self.pn)
        self.pos = [self.left,self.top]
        self.gpc.moveto(*self.pos)
        #self.gpc.moveto(10,10)
        #self.gpc.show("Page %s"%self.pn)
        #self.gpc.moveto(*self.pos)

    def printBlock (self, markup):
        paras = markup.split("\n")
        for p in paras: self.printPara(p)
        
    def write_heading (self, line,
                       size=None,
                       font_family=None,
                       style=None,
                       weight=None,
                       indent=None, space_before=1, space_after=1):
        if not size: size=self.default_head_size
        if type(size)==int:
            if size < 5000: size = size * 1000 # convenience, in case we typed a normal fontsize :)
        if not font_family: font_family=self.default_head_family
        if not style: style=self.default_head_style
        if not weight: weight=self.default_head_weight
        stag = '<span font_family="%(family)s" size="%(size)s" style="%(style)s" weight="%(weight)s">'%{
            'size':size,
            'weight':weight,
            'family':font_family,
            'style':style
            }
        l = stag + line + '</span>'
        if space_before:
            space_before = int(space_before+0.9)
            l = "\n"*space_before + l
        if space_after:
            space_after = int(space_after+0.9)
            l = l + "\n"*space_after
        #self.write_paragraph('<big><b>%s</b></big>'%line,indent=indent)
        self.write_paragraph(l,indent=indent)

    def write_paragraph (self, markup, indent=0, space=False, first_indent=0, force=False):
        "Print some markup to the supplied context"
        # first, we do a simple escape routine, just in case we're
        # not actually being handed valid markup. Not fail-safe by
        # any means, but should save us from the common "&"s that slip
        # through
        markup=self.escape(markup)
        #need to use pango.Layout to format paragraphs
        #for each block of text
        paraContext = gnomeprint.pango_create_context(gnomeprint.pango_get_default_font_map())
        para = pango.Layout(paraContext)
        para.set_wrap(pango.WRAP_WORD)
        if first_indent: para.set_indent(int(first_indent)*pango.SCALE)
        para.set_justify(True)
        para.set_width(int(self.right-self.left)*pango.SCALE)
        para.set_markup(markup)
        x,y=para.get_size()
        x = x/pango.SCALE
        y = y/pango.SCALE
        #print 'paragraph of size ',x,y
        botpos = self.pos[1] - y
        #print 'moves bottom to ',botpos, ' bottom at %s'%self.bottom
        if botpos < self.bottom and not force:
            # running off the bottom of the page. In 2.6 we'll be able to handle this gracefully.
            # in 2.4, we create a terrible, no-good, very bad hack.
            # (right is tied to left-to-right languages...) and we're definitely tied to horizontal
            # languages (left-to-right/right-to-left) in this whole routine.
            room = self.pos[1]-self.bottom
            shrink_by_percentage = float(room) / y
            mymarkup = MarkupString(markup)
            char = int(len(mymarkup.raw)*shrink_by_percentage)
            # we automatically backup until we find a space. If there are no spaces, we fail.
            while mymarkup[char]!=" ":
                char -= 1
            startmark = mymarkup[:char]
            endmark = mymarkup[char+1:]
            #print 'breaking block into %s and endblock (length of %s)'%(startmark,len(endmark))
            self.write_paragraph(startmark,force=True)
            self.new_page()
            self.write_paragraph(endmark,indent=False)
        else:
            self.gpc.pango_layout(para)
            #self.pos[1] = self.pos[1]-y
            self.move_down(y)
            #self.gpc.moveto(*self.pos)

    def move_down (self, amt):
        self.pos[1]=self.pos[1] - amt
        self.pos[0]=self.left
        if self.move_down_hooks:
            for f in self.move_down_hooks:
                f(self.pos[1])
            if self.pos[1] <= self.bottom:
                self.new_page()
        self.gpc.moveto(*self.pos)

    def write_pixbuf (self, pixbuf, inline=True, align='left', border=10):
        debug('write_pixbuf ',3)
        """Align can take "left", "right", or "center".
        "center" implies not inline."""
        raw_image = pixbuf.get_pixels()
        has_alpha = pixbuf.get_has_alpha()
        rowstride = pixbuf.get_rowstride()
        height = pixbuf.get_height()
        width = pixbuf.get_width()
        # if we're not at the top, give us our border
        if not self.pos[1] >= self.top:
            self.move_down(border)
        if (self.pos[1] - height) <= self.bottom:
            self.new_page()
        self.gpc.gsave()
        if align=='left':
            left = self.left
        if align=='right':
            left = self.right - width
        if align=='center':
            left = (self.width - width)/2
        self.gpc.translate(left,self.pos[1]-height)
        self.gpc.moveto(left, self.pos[1])
        self.gpc.show('just moved into place!')
        self.gpc.scale(width,height)        
        if has_alpha: self.gpc.rgbaimage(raw_image, width, height, rowstride)
        else: self.gpc.rgbimage(raw_image, width, height, rowstride)
        self.gpc.grestore()
        #self.gpc.show('just restored')
        # don't allow "inline" if our remaining width is less half
        remaining_width = self.right - self.left - width -border
        if remaining_width < 0.4 * width:
            inline = False
        if inline and align != 'center':
            # we shift the left and right side to allow for our image
            if align=='left':
                self.left = self.left + width + border
            else: # align=='right'
                self.right = self.right - width - border
            # we set up a hook to reset margins once we're beyond the image.
            image_end_pos = self.pos[1]
            def reset_margins (yposition):
                debug('reset_margins ',3)
                if yposition <= image_end_pos - (height + border):
                    self.left = self.default_left
                    self.right = self.default_right
                    self.move_down_hooks.remove(self.reset_margin_hook)
            self.reset_margin_hook=reset_margins
            self.pos[0]=self.left # shift ourselves into position
            #self.gpc.moveto(*self.pos)
            self.move_down_hooks.append(self.reset_margin_hook)
        else:
            self.move_down(height + border)

def show_preview(dialog,job):
    debug('show_preview',0)
    #job = gnomeprint.Job(dialog.get_config())
    #render_to_job(job)
    w = gnomeprint.ui.JobPreview(job, "Print Preview")
    w.set_property('allow-grow', 1)
    w.set_property('allow-shrink', 1)
    w.set_transient_for(dialog)
    w.show_all()
    w.present()

def print_dialog_response(dialog, resp, job):
    debug('print_dialog_response',3)
    if resp == gnomeprint.ui.DIALOG_RESPONSE_PREVIEW:
	show_preview(dialog,job)
    elif resp == gnomeprint.ui.DIALOG_RESPONSE_CANCEL:
	dialog.destroy()
    elif resp == gnomeprint.ui.DIALOG_RESPONSE_PRINT:
	do_print(dialog, job)
	dialog.destroy()

def render_to_job (job):
    debug('render_to_job ',3)
    r = renderer(job)
    for f in ['Sans','Serif','Monospace','Arial']:
        for s in [12,14,16,18,24]:
            for sty in ['normal','oblique','italic']:
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
        debug('print_writer.__init__ ',3)        
        renderer.__init__(self)
        self.show_dialog = show_dialog
        self.dialog_parent = dialog_parent
        self.dialog_title = dialog_title
        self.dialog_kwargs = dialog_kwargs

    def close (self):
        debug('close ',1)
        self.end()
        if self.show_dialog:
            debug('preparing dialog',1)
            dialog = gnomeprint.ui.Dialog(self.job, self.dialog_title,
                                          gnomeprint.ui.DIALOG_RANGE | gnomeprint.ui.DIALOG_COPIES,
                                          **self.dialog_kwargs)
            debug('preparing dialog 2',1)
            flags = (gnomeprint.ui.RANGE_CURRENT
                     |gnomeprint.ui.RANGE_ALL
                     |gnomeprint.ui.RANGE_RANGE
                     |gnomeprint.ui.RANGE_SELECTION)
            debug('preparing dialog 3',1)
            dialog.construct_range_page(flags, 1, 1, _("_Current"), _("_Range"))
            dialog.connect('response', print_dialog_response, self.job)
            if self.dialog_parent: dialog.set_transient_for(self.dialog_parent)
            debug('showing dialog',1)
            dialog.show()
            debug('showed dialog',1)
        
class RecRenderer (print_writer):
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None, change_units=True):
        debug('RecRenderer.__init__ ',3)        
        print_writer.__init__(self, show_dialog=True, dialog_title=dialog_title,
                              dialog_parent=dialog_parent)
        do_new_page = False
        for r in recs:
            if do_new_page:
                self.new_page()
            r=RecWriter(rd, r, self, change_units=change_units, mult=mult)
            do_new_page = True # put pagebreaks between recipes...
        self.close()
        

class RecWriter (exporter.exporter_mult):
    def __init__ (self, rd, r, printwriter, change_units=True, mult=1):
        debug('__init__ ',3)
        self.print_writer = printwriter
        self.r = r
        exporter.exporter_mult.__init__(self, rd, r, out=None, change_units=change_units, mult=mult,
                                        do_markup=False,
                                        use_ml=True)

    def write_head (self):
        debug('write_head ',3)
        pass

    def write_image (self, image):
        debug('write_image ',3)
        pb = ImageExtras.get_pixbuf_from_jpg(image)
        self.print_writer.write_pixbuf(pb, align='right')

    def write_attr (self, label, text):
        debug('write_attr ',3)
        attr=gglobals.NAME_TO_ATTR[label]
        if attr=='title':
            self.print_writer.write_heading(xml.sax.saxutils.escape(text))
            return
        self.print_writer.write_paragraph(xml.sax.saxutils.escape("%s: %s"%(label, text)))

    def write_text (self, label, text):
        debug('write_text ',3)
        self.print_writer.write_heading(label, space_after=0, space_before=0.5)
        pars = re.split("\n+", text)
        for p in pars: self.print_writer.write_paragraph(p, space=True)
        
    def write_inghead (self):
        debug('write_inghead ',3)
        self.print_writer.write_heading(xml.sax.saxutils.escape(_('Ingredients')), space_before=0.5, space_after=0)

    def write_grouphead (self, name):
        debug('write_grouphead ',3)
        self.print_writer.write_heading(xml.sax.saxutils.escape(name),
                                        size=self.print_writer.default_head_size-2,
                                        style='normal',
                                        indent=0,
                                        space_before=0.5,
                                        space_after=0)

    def write_ing (self, amount="1", unit=None, item=None, key=None, optional=False):
        debug('write_ing ',3)
        if amount: line = amount + " "
        else: line = ""
        if unit: line += "%s "%unit
        if item: line += "%s"%item
        if optional: line += " (%s)"%_("optional")
        self.print_writer.write_paragraph(xml.sax.saxutils.escape(line))

class SimpleWriter (print_writer):
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        debug('__init__ ',3)
        print_writer.__init__(self,dialog_parent=dialog_parent,show_dialog=show_dialog)

    def write_header (self, text):
        debug('write_header ',3)
        self.dont_escape=True
        self.write_heading(xml.sax.saxutils.escape(text), size=14, space_before=0.5, space_after=0)
        self.dont_escape=False

    def write_subheader (self, text):
        debug('write_subheader ',3)
        self.dont_escape=True
        self.write_heading(xml.sax.saxutils.escape(text),
                           size=12,
                           style="normal",
                           space_after=0,
                           space_before=0.5)
        self.dont_escape=False

    def write_paragraph (self, text, *args, **kwargs):
        if not self.dont_escape: text=xml.sax.saxutils.escape(text)
        print_writer.write_paragraph(self,text,*args,**kwargs)

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
    gtk.threads_init()
    gtk.main()
