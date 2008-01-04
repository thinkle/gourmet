import tempfile, gtk
from pdf_exporter import PdfWriter, PdfExporterMultiDoc, get_pdf_prefs

from gettext import gettext as _
from gettext import ngettext
import gourmet.gtk_extras.dialog_extras as de
import gourmet.gglobals as gglobals
from gourmet.convert import FRACTIONS_NORMAL
import exporter

import win32api


def print_file_with_windows (filename):
    # Method from:
    # http://tgolden.sc.sabren.com/python/win32_how_do_i/print.html#shellexecute
    if de.getBoolean(label=_('Print'),
                  sublabel=_('Ready to print your recipe through the PDF file %s. Unfortunately, we have no print preview - shall we go ahead and print?')%filename):
        win32api.ShellExecute(
            0,
            "print",
            filename,
            None,
            ".",
            0
            )
        d = de.MessageDialog(label=_('Print job sent'),
                       sublabel=_("Print job has been sent. If something goes wrong, you can open the PDF file and try printing again."))
    else:
        d = de.MessageDialog(label=_('Print job cancelled'),
                       sublabel=_("If you'd like, you can open the PDF file.")
                              )
    b = gtk.Button(stock=gtk.STOCK_JUMP_TO)
    b.connect('clicked',lambda *args: gglobals.launch_url(filename))
    d.vbox.pack_end(b,expand=False); b.show()
    d.run()
        

class RecRenderer:
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None, **kwargs):
        filename = tempfile.mktemp('.pdf')
        pdf_args = get_pdf_prefs()
        kwargs['pdf_args']=pdf_args
        e = PdfExporterMultiDoc(rd,recs,filename, **kwargs)
        e.run()
        print_file_with_windows(filename)
        #show_disappointing_message()
        #debug('printing not supported; showed dialog',0)

class SimpleWriter (PdfWriter):

    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        self.filename = tempfile.mktemp('.pdf')
        self.outfile = open(self.filename,'wb')
        #PdfWriter.__init__(self)
        self.setup_document(self.outfile,
                            **get_pdf_prefs({
                'page_layout':(ngettext('%s Column','%s Columns',2)%2),
                })
                            )
                            
    def close (self):
        PdfWriter.close(self)
        self.outfile.close()
        print_file_with_windows(self.filename)
    
if __name__ == '__main__':
    sw = SimpleWriter()
    sw.write_header("This is a big heading")
    sw.write_paragraph("""This is a paragraph.
This is perhaps a silly sort of paragraph to write, but I'm in the mood for silly paragraphs.
In fact, I'm in the mood for extraordinarily silly paragraphs. Paragraphs so silly they go on and on and on and on and (not being tired continuing) on and so forth until (by now the reader tiring) they take a sudden left turn, careening around the bend (passing colorless, sleeping, furious green ideas), plummetting downward (toward what or whom I don't know, whether or not there is a netherworld being among the many things, such as the existence of fairies, which escape my knowledge), falling fast and furious until hitting that final (cliched) rock bottom and returning upward.
This is my final paragraph.""")
    sw.write_subheader("Foo")
    sw.write_paragraph("This is the section named foo.  "*12)
    sw.write_subheader("Final Section")
    sw.write_paragraph("And this is the final section." * 3)
    sw.close()
