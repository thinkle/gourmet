import tempfile
from pdf_exporter import PdfWriter, PdfExporterMultiDoc

from gettext import gettext as _
import gourmet.dialog_extras as de
import gourmet.gglobals as gglobals
from gourmet.convert import FRACTIONS_NORMAL
import exporter
import win32api


def print_file_with_windows (filename):
    # Method from:
    # http://tgolden.sc.sabren.com/python/win32_how_do_i/print.html#shellexecute
    win32api.ShellExecute(
        0,
        "print",
        filename,
        None,
        ".",
        0
        )    

class RecRenderer:
    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None):
        filename = tempfile.mktemp('.pdf')
        outfile = file(filename,'w')
        e = PdfExporterMultiDoc(rd,recs,outfile)
        e.run()
        print_file_with_windows(filename)
        #show_disappointing_message()
        #debug('printing not supported; showed dialog',0)

class SimpleWriter (PdfWriter):

    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        self.filename = tempfile.mktemp('.pdf')
        self.outfile = open(self.filename,'w')
        #PdfWriter.__init__(self)
        self.setup_document(self.outfile)

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
