import tempfile, PyRTF
from rtf_exporter import rtf_exporter_multidoc
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
        filename = tempfile.mktemp('.rtf')
        outfile = file(filename,'w')
        e = rtf_exporter_multidoc(rd,recs,outfile)
        e.run()
        print_file_with_windows(filename)
        #show_disappointing_message()
        #debug('printing not supported; showed dialog',0)

class SimpleWriter (rtf_exporter.rtf_exporter):
    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        self.setup_document()
        self.recsection = PyRTF.Section(break_type=PyRTF.Section.PAGE) # This is where add_paragraph adds paragraphs
        self.doc.Sections.append( self.recsection )
        
    def write_header (self, text):
        self.add_paragraph("%s\n"%text,self.ss.ParagraphStyles.Heading1)

    def write_subheader (self, text):    
        self.add_paragraph("%s\n"%text,self.ss.ParagraphStyles.Heading3)

    def write_paragraph (self, text):
        self.add_paragraph(text)

    def close (self):
        renderer = PyRTF.Renderer()
        filename = tempfile.mktemp('.rtf')
        outfile = file(filename,'w')
        renderer.Write(self.doc,outfile)
        outfile.close()
        print_file_with_windows(filename)
        
    
