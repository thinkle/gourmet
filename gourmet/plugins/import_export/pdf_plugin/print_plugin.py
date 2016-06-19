from __future__ import print_function

import gtk
import sys
if sys.platform != "win32":
    import poppler
import os.path
import pdf_exporter
import tempfile
import reportlab.lib.pagesizes as pagesizes
from gourmet.plugin import PrinterPlugin
from gettext import gettext as _

rl2gtk_papersizes = {
    tuple([int(round(s)) for s in pagesizes.letter]) : gtk.PAPER_NAME_LETTER,
    tuple([int(round(s)) for s in pagesizes.legal]) : gtk.PAPER_NAME_LEGAL,    
    tuple([int(round(s)) for s in pagesizes.B5]):gtk.PAPER_NAME_B5,
    tuple([int(round(s)) for s in pagesizes.A5]):gtk.PAPER_NAME_A5,
    tuple([int(round(s)) for s in pagesizes.A4]):gtk.PAPER_NAME_A4,
    tuple([int(round(s)) for s in pagesizes.A3]):gtk.PAPER_NAME_A3,
    }

class WindowsPDFPrinter:

    def setup_printer (self, parent=None):
        self.args = pdf_exporter.get_pdf_prefs()
        self.begin_print(None, None)

    def set_document (self, filename, operation,context):
        try:
            from subprocess import Popen
            import _winreg
            regPathKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                         "Software\Microsoft\Windows\CurrentVersion\App Paths\AcroRd32.exe")
            regPathValue, regPathType = _winreg.QueryValueEx(regPathKey, "")
            if regPathType != _winreg.REG_SZ:
                raise TypeError
        except:
            from gourmet.gtk_extras.dialog_extras import show_message
            show_message(label=_("Could not find Adobe Reader on your system."),
                         sublabel=_("This version of Gourmet Recipe Manager "
                         "requires Adobe Reader "
                         "to be able to print; other PDF viewers will not work.\n"
                         "Please install Adobe Reader from http://get.adobe.com/reader/. \n"
                         "Alternatively, export your recipe(s) to PDF "
                         "and print it with another PDF viewer."))
        else:
            # Launch a new instance (/n) of Adobe Reader with our temporary
            # PDF to display the print dialog (/p).
            Popen(regPathValue + " /n /p " + os.path.realpath(filename))

class PDFPrinter:

    def setup_printer (self, parent=None):
        po = gtk.PrintOperation()
        #po.set_n_pages(self.d.get_n_pages())
        po.connect('draw_page',self.draw_page)
        po.connect('begin-print',self.begin_print)
        po.connect('create-custom-widget',self.create_custom_widget)
        po.props.custom_tab_label = _('Page Layout')
        po.connect('custom-widget-apply',self.custom_widget_apply)
        po.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, parent=parent)

    def set_document (self, filename, operation,context):
        if not filename.startswith('file'):
            filename = 'file://' + os.path.realpath(filename)
        self.d = poppler.document_new_from_file(filename,None)
        operation.set_n_pages(self.d.get_n_pages())
        # Assume all pages are same
        page = self.d.get_page(0)
        w,h = page.get_size()
        if w > h:
            w,h = h,w
            ori = gtk.PAGE_ORIENTATION_LANDSCAPE
        else:
            ori = gtk.PAGE_ORIENTATION_PORTRAIT
        page_setup = gtk.PageSetup()
        page_setup.set_orientation(ori)
        size = int(round(w)),int(round(h))
        gtk_size = rl2gtk_papersizes.get(size,None)
        if gtk_size:
            ps = gtk.PaperSize(gtk_size)
        else:
            ps = gtk.paper_size_new_custom('','',w,h,gtk.UNIT_POINTS)
        page_setup.set_paper_size(ps)
        operation.set_default_page_setup(page_setup)
        
    def draw_page (self,operation, context, page_num):
        page = self.d.get_page(page_num)
        w,h = page.get_size()
        #page_setup = context.get_page_setup()
        #ps = gtk.paper_size_new_custom('','',w,h,gtk.UNIT_POINTS)
        #page_setup.set_paper_size(ps)
        page.render_for_printing(context.get_cairo_context())

    def create_custom_widget (self, operation):
        self.ppt = pdf_exporter.PdfPrefTable()
        self.opts = self.ppt.opts
        self.args = self.ppt.get_args_from_opts(self.opts)
        return self.ppt.widg
        
    def custom_widget_apply (self, operation, widget):
        self.args = self.ppt.get_args_from_opts(self.opts)

if sys.platform == "win32":
    PDFPrinter = WindowsPDFPrinter

def record_args (func):
    
    def _ (self, *args, **kwargs):
        self.export_commands.append(
            (func.__name__,args,kwargs)
            )
    return _

class PDFSimpleWriter (PDFPrinter):

    def __init__ (self, dialog_parent=None):
        self.parent = dialog_parent
        self.export_commands = []

    @record_args
    def write_header (self, *args, **kwargs): pass

    @record_args
    def write_subheader (self, *args, **kwargs): pass

    @record_args
    def write_paragraph (self, *args, **kwargs): pass

    def close (self, *args, **kwargs):
        self.export_commands.append(('close',[],{}))
        self.setup_printer(self.parent)
    
    def begin_print (self, operation, context):
        fn = tempfile.mktemp()
        writer = pdf_exporter.PdfWriter()
        writer.setup_document(fn,**self.args)
        # Playback all the commands we recorded
        for commandname,args,kwargs in self.export_commands:
            func = getattr(writer,commandname)
            func(*args,**kwargs)
        # And now we trust the documents been written...
        self.set_document(fn,operation,context)

        
class PDFRecipePrinter (PDFPrinter):

    def __init__ (self, rd, recs,
                  mult=1, dialog_title=_('Print Recipes'),
                  dialog_parent=None, change_units=True):
        self.printing_error = False
        self.change_units = change_units
        self.mult = mult
        self.parent = dialog_parent
        self.rd = rd
        self.recs = recs
        self.setup_printer(self.parent)
        
    def begin_print (self, operation, context):
        fn = tempfile.mktemp()
        pe = pdf_exporter.PdfExporterMultiDoc(self.rd,self.recs,fn,pdf_args=self.args,
                                              change_units=self.change_units, mult=self.mult)
        pe.connect('error',self.handle_error)
        pe.run()
        if self.printing_error:
            print('PRINTING ERROR!')
            raise Exception("There was an error generating PDF")
        self.set_document(fn, operation,context)

    def handle_error (self,obj,errno, summary, traceback):
        print('There was an error generating a PDF to print.')
        print(summary)
        print(traceback)
        self.printing_error = True
        raise Exception('There was an error generating a PDF to print')

def setup_printer (pp):
    po = gtk.PrintOperation()
    po.set_n_pages(pp.d.get_n_pages())
    po.connect('draw_page',pp.draw_page)
    po.connect('begin-print',pp.begin_print)
    po.connect('create-custom-widget',pp.create_custom_widget)
    po.connect('custom-widget-apply',pp.custom_widget_apply)
    po.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
    
def print_pdf (pdf_filename):
    if not pdf_filename.startswith('file'):
        pdf_filename = 'file://' + os.path.realpath(pdf_filename)
        setup_printer(PDFPrinter(pdf_filename))

def test_simplewriter ():
    pwriter = PDFSimpleWriter()
    pwriter.write_header("TEST HEADER")
    pwriter.write_subheader('Test subheading')
    pwriter.write_paragraph('This is a test  ' * 10)
    pwriter.write_paragraph('This is a test  ' * 15)
    for n in range(3):
        pwriter.write_subheader('Test subheading for time number %s'%(n+2))
        for i in range(5,(5*(n+1))):
            pwriter.write_paragraph('So is this a test? Or is it. '*i)
    pwriter.close()

class PDFPrintPlugin (PrinterPlugin):
    SimpleWriter = PDFSimpleWriter
    simpleWriterPriority = 1
    RecWriter = PDFRecipePrinter
    recWriterPriority = 1
    
if __name__ == '__main__':
    test_simplewriter()
