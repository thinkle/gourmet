import sys
sys.path.append('/usr/share/gourmet/')
import gtk
import poppler
import os.path
import pdf_exporter
import tempfile

class PDFPrinter:

    def __init__ (self, rd, recs):
        self.rd = rd
        self.recs = recs

    def draw_page (self,operation, context, page_num):
        page = self.d.get_page(page_num)
        page.render_for_printing(context.get_cairo_context())

    def begin_print (self, operation, context):
        fn = tempfile.mktemp()
        pe = PdfExporterMultiDoc(self.rd,self.recs,fn,pdf_args=self.args)
        pe.run()
        self.d = poppler.document_new_from_file(fn,None)

    def create_custom_widget (self, operation):
        print 'create!'
        self.ppt = pdf_exporter.PdfPrefTable()
        return self.ppt.widg

    def custom_widget_apply (self, operation, widget):
        self.opts = self.ppt.opts
        print self.opts
        self.args = self.ppt.get_args_from_opts(self.opts)

def setup_printer (pp):
    po = gtk.PrintOperation()
    po.set_n_pages(pp.d.get_n_pages())
    po.connect('draw_page',pp.draw_page)
    po.connect('begin-print',pp.begin_print)
    po.connect('create-custom-widget',pp.create_custom_widget)
    po.connect('custom-widget-apply',pp.custom_widget_apply)
    po.set_export_filename('/tmp/foo.pdf')
    po.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
    
def print_pdf (pdf_filename):
    if not pdf_filename.startswith('file'):
        pdf_filename = 'file://' + os.path.realpath(pdf_filename)
        setup_printer(PDFPrinter(pdf_filename))
            
print_pdf('/home/tom/list.pdf')
