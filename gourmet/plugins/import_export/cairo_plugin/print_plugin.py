import gtk
import pango
import re
from types import StringTypes
import gourmet.exporters.exporter as exporter
from gourmet.plugin import PrinterPlugin
from gourmet import ImageExtras,gglobals,convert
from gourmet.gdebug import *
from gettext import gettext as _
import gourmet.plugins.import_export.pdf_plugin.pdf_exporter as pdf_exporter
from gourmet.plugins.import_export.pdf_plugin.pdf_exporter import DEFAULT_PDF_ARGS
from gourmet.plugins.import_export.cairo_plugin.pdf_exporter import CairoRenderer
import reportlab.lib.pagesizes as pagesizes
from gourmet.plugins.import_export.pdf_plugin.print_plugin import rl2gtk_papersizes
import xml.sax.saxutils

class CairoPageRenderer (CairoRenderer):
    """This is a thin-wrapping subclass of CairoRenderer that encapsulates
    the GtkPrintOperation specific stuff to keep CairoRenderer output surface
    agnostic.
    
    """
    def __init__ (self, operation, context, args):
        CairoRenderer.__init__(self)
        self.pn = 0
        self.setup_defaults()
        self.move_down_hooks = []
        self.simple_escaper = re.compile("&(?=[^ ;]*($| ))")
        self.args = args
        self.gpc = context
        self.cr = context.get_cairo_context()

        self.setup_page(operation)

    def setup_page (self, operation):
        if type(self.args['pagesize']) in StringTypes:
            self.pagesize = getattr(pagesizes,self.args['pagemode'])(getattr(pagesizes,self.args['pagesize']))
        else:
            self.pagesize = getattr(pagesizes,self.args['pagemode'])(self.args['pagesize'])

        width = self.pagesize[0]
        height = self.pagesize[1]
        size = int(round(width)),int(round(height))

        gtk_size = rl2gtk_papersizes.get(size,None)
        if gtk_size:
            ps = gtk.PaperSize(gtk_size)
        else:
            ps = gtk.paper_size_new_custom('','',w,h,gtk.UNIT_POINTS)

        page_setup = gtk.PageSetup()
        page_setup.set_paper_size_and_default_margins(ps)

        if self.args['pagemode'] == 'portrait':
            page_setup.set_orientation(gtk.PAGE_ORIENTATION_PORTRAIT)
        else:
            page_setup.set_orientation(gtk.PAGE_ORIENTATION_LANDSCAPE)

        operation.set_default_page_setup(page_setup)

        self.width = self.gpc.get_width()
        self.height = self.gpc.get_height()
        self.default_left = 0
        self.left = self.default_left
        self.top = 0
        self.default_right = self.width
        self.right = self.default_right
        self.bottom = self.height

    def printBlock (self, markup):
        paras = markup.split("\n")
        for p in paras: self.printPara(p)


    def make_pango_layout(self):
        return self.gpc.create_pango_layout()

    def write_foot (self):
        #if not self.multidoc:
        self.close() # Finish the document if this is all-in-one
        
    def close(self):
        self.cr.show_page()

class GtkPrintOperationWriter:
    """GtkPrintOperationWriter is employed by CairoPrintPlugin to render
    recipes for printing (via gtk.PrintOperation). Its __init__
    function signature must thus comply to the requirements of a PrintPlugin's
    RecWriter (see PrintManager.print_recipes in gourmet/printer.py).
    
    """
    def __init__ (self, rd, recs, filename=None, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None, change_units=True,
                  action=gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, pdf_args=DEFAULT_PDF_ARGS):
        debug('GtkPrintOperationWriter.__init__ ',3)

        self.printing_error = False
        self.change_units = change_units
        self.mult = mult
        self.parent = dialog_parent
        self.rd = rd
        self.recs = recs
        self.action = action
        self.args = pdf_args
        self.filename = filename
        self.setup_printer(self.parent)

    def setup_printer (self, parent=None):
        po = gtk.PrintOperation()
        po.connect('draw_page',self.draw_page)
        po.connect('begin-print',self.begin_print)
        po.connect('create-custom-widget',self.create_custom_widget)
        po.props.custom_tab_label = _('Page Layout')
        po.connect('custom-widget-apply',self.custom_widget_apply)
        if self.action == gtk.PRINT_OPERATION_ACTION_EXPORT:
            po.set_export_filename(self.filename)
        po.run(self.action, parent=parent)

    def draw_page (self,operation, context, page_num):
        cr = context.get_cairo_context()
        pos = self.print_writer.positions[page_num]
        para = self.print_writer.paragraphs[page_num]

        for i in xrange(len(pos)):
            cr.move_to(*pos[i])
            if i < len(para):
                if type(para[i]) is pango.Layout:
                    cr.show_layout(para[i])
                elif type(para[i]) is gtk.gdk.Pixbuf:
                    cr.save()
                    cr.set_source_pixbuf(para[i], *pos[i])
                    cr.paint()
                    cr.restore()

    def create_custom_widget (self, operation):
        self.ppt = pdf_exporter.PdfPrefTable()
        self.opts = self.ppt.opts
        self.args = self.ppt.get_args_from_opts(self.opts)
        return self.ppt.widg
        
    def custom_widget_apply (self, operation, widget):
        self.args = self.ppt.get_args_from_opts(self.opts)

    def begin_print (self, operation, context):
        self.print_writer = CairoPageRenderer(operation, context, self.args)
        r = RecWriter(self.rd, self.recs[0], self.print_writer, change_units=self.change_units, mult=self.mult)
        r.do_run()
        operation.set_n_pages(len(self.print_writer.positions))

    def handle_error (self,obj,errno, summary, traceback):
        print 'There was an error generating a PDF to print.'
        print summary
        print traceback
        self.printing_error = True
        raise Exception('There was an error generating a PDF to print')

class RecWriter (exporter.exporter_mult):
    def __init__ (self, rd, r, printwriter, change_units=True, mult=1):
        debug('__init__ rd=%s r=%s printwriter=%s change_units=%s mult=%s'%(rd,r,printwriter,change_units,mult),3)
        self.print_writer = printwriter
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
        self.print_writer.write_paragraph(text, first_indent=25)
        
    def write_inghead (self):
        debug('write_inghead ',3)
        self.print_writer.write_heading(xml.sax.saxutils.escape(_('Ingredients')), space_before=0.5, space_after=0)

    def write_grouphead (self, name):
        debug('write_grouphead ',3)
        self.print_writer.write_heading(xml.sax.saxutils.escape(name),
                                        size=self.print_writer.default_head_size-2,
                                        style=pango.STYLE_NORMAL,
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


class SimpleWriter (CairoPageRenderer):
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        debug('__init__ ',3)
        print_writer.__init__(self) #,dialog_parent=dialog_parent,show_dialog=show_dialog)

    def write_header (self, text):
        debug('write_header ',3)
        self.dont_escape=True
        self.write_heading(xml.sax.saxutils.escape(text), size=14, space_before=0.5, space_after=0)
        self.dont_escape=False

    def write_subheader (self, text):
        debug('write_subheader ',3)
        self.dont_escape=True
        try:
            self.write_heading(xml.sax.saxutils.escape(text),
                               size=12,
                               style="normal",
                               space_after=0,
                               space_before=0.5)
        except:
            print 'Trouble printing "%s"'%text
            raise
        self.dont_escape=False

    def write_paragraph (self, text, *args, **kwargs):
        if not self.dont_escape: text=xml.sax.saxutils.escape(text)
        print_writer.write_paragraph(self,text,*args,**kwargs)


class CairoPrintPlugin (PrinterPlugin):
    SimpleWriter = SimpleWriter
    simpleWriterPriority = 1
    RecWriter = GtkPrintOperationWriter
    recWriterPriority = 1

