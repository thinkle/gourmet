import gourmet.dialog_extras as de
from gourmet.gdebug import debug
from gettext import gettext as _
#import lprprinter
import html_exporter, xml.sax.saxutils
import StringIO
import wx
from wx.html import HtmlEasyPrinting
from wxPython.wx import wxPySimpleApp

class RecRenderer:
    """We use wx.html.HtmlEasyPrinting in order to print out our file on platforms without
    GNOME support. HtmlEasyPrinting takes care of everything for us: all we have to do is
    write our recipes as HTML and hand it over."""
    
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  change_units=True,
                  dialog_parent=None):
        self.app=wxPySimpleApp()
        # we use StringIO so we can call our standard HTML exporters (which write
        # to a file)
        self.html_out = StringIO.StringIO()
        # ugly, but necessary -- our exporters expect a file to have a name...
        self.html_out.name='/tmp/rec.html'
        # now we do the actual export
        SimpleHTML(rd, recs[0], self.html_out,                             
                   embed_css=True,
                   link_generator=None,
                   mult=mult,
                   change_units=change_units,
                   )
        # grab the value from our StringIO
        self.app.MainLoop()
        self.html=self.html_out.getvalue()
        # now we actually print outselves...
        self.hep = HtmlEasyPrinting()
        # if we wanted a preview, we'd do it here -- apparently the "preview" button isn't
        # built into the standard dialog, so we'll either have to learn more wxWindows stuff
        # to subclass and modify that dialog, or we'll have to add a separate dialog with the
        # preview option (too ugly for me to do right now)
        #self.do_preview()        
        self.do_print()
        print 'Done!'
        self.app.ExitMainLoop()

    def do_preview (self):
        """Show a print preview window"""
        #self.hep.SetHeader(_('Recipe'))
        self.hep.PreviewText(self.html)
    
    def do_print (self):
        """Print our recipe (actually, offer the user configuration options, then print)"""
        #self.hep.SetHeader(_('Recipe'))
        self.hep.PrintText(self.html)
        

class SimpleWriter:
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        """Arguments are here only for compatability with other SimpleWriter classes -- they
        are promptly ignored. We provide the write method and a "close" method that does the
        actual printing."""
        self.ofi = StringIO.StringIO()

    def close (self):
        htmlstring = self.ofi.getvalue()
        hep = HtmlEasyPrinting()
        hep.PrintText(htmlstring)
        
    def write_header (self, text):
        self.ofi.write('<h3>%s</h3>'%xml.sax.saxutils.escape(text))
        
    def write_subheader (self, text):
        self.ofi.write('<h4>%s</h4>'%xml.sax.saxutils.escape(text))

    def write_paragraph (self, text, *args, **kwargs):
        self.ofi.write('<p>%s</p>'%xml.sax.saxutils.escape(text))

class SimpleHTML (html_exporter.html_exporter):
    """We subclass our HTML writer in order to simplify the output for HtmlEasyPrinting,
    which doesn't seem to understand the CSS we use elsewhere."""
    def __init__ (self,*args,**kwargs):
        # kill off any CSS args
        kwargs['css']=None
        html_exporter.html_exporter.__init__(self,*args,**kwargs)
        
    def write_attr (self, label, text):
        if label==_('Title'):
            self.out.write("<h3>%s</h3>"%(text))
        else:
            self.out.write("<br>%s: %s"%(label,text))

    def write_ing (self, amount=1, unit=None,
                   item=None, key=None, optional=False):
        self.out.write("\n<br>")
        for o in [amount, unit, item]:
            if o: self.out.write(xml.sax.saxutils.escape("%s "%o))
        if optional:
            self.out.write("(%s)"%_('optional'))

    def write_ingfoot (self):
        self.out.write("<br>")

    def write_inghead (self):
        self.out.write("\n<h3>%s</h3>"%_('Ingredients'))

    def write_grouphead (self, name):
        self.out.write("\n<h4>%s</h4>"%name)

    def write_groupfoot (self):
        self.out.write("\n<br>\n")

