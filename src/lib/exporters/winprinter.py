import tempfile, PyRTF
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

# class RecRenderer:
#     def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
#                   dialog_parent=None):
#         filename = tempfile.mktemp('.rtf')
# 	print "Exporting temporary RTF file to ",filename
# 	outfile = file(filename,'w')
#         e = rtf_exporter_multidoc(rd,recs,outfile)
#         e.run()
# 	print "Print file ",filename
#         print_file_with_windows(filename)
#         #show_disappointing_message()
#         #debug('printing not supported; showed dialog',0)

import win32ui
import win32print
import win32con

#INCH = 1440

HORZRES = 8
VERTRES = 10
LOGPIXELSX = 88
LOGPIXELSY = 90
PHYSICALWIDTH = 110
PHYSICALHEIGHT = 111
PHYSICALOFFSETX = 112
PHYSICALOFFSETY =113

class SimpleWriter:

    def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
        print 'SimpleWriter loading...'
        self.parent = dialog_parent
        self.show_dialog = show_dialog
        self.hDC = win32ui.CreateDC ()
        try:
            assert(self.hDC)
            self.hDC.CreatePrinterDC (win32print.GetDefaultPrinter ())
        except:
            de.show_message(label=_("Unable to print"),
                            sublabel=_("Unable to set printint up correctly. Perhaps you can save as text and then use another program to print.")
                            )
        self.hDC.StartDoc ("Gourmet Recipe Manager Document")
        self.hDC.SetMapMode(win32con.MM_TWIPS)
        self.xINCH = float(self.hDC.GetDeviceCaps(LOGPIXELSX))
        self.yINCH = float(self.hDC.GetDeviceCaps(LOGPIXELSY))
        self.printable_area = (
            self.hDC.GetDeviceCaps(HORZRES)/self.xINCH,
            self.hDC.GetDeviceCaps(VERTRES)/self.yINCH
            )
        self.printer_size = (self.hDC.GetDeviceCaps(PHYSICALWIDTH)/self.xINCH,
                             self.hDC.GetDeviceCaps(PHYSICALHEIGHT)/self.yINCH
                             )
        #self.printer_margins = (self.hDC.GetDeviceCaps(PHYSICALOFFSETX)/self.xINCH,
        #                        self.hDC.GetDeviceCaps(PHYSICALOFFSETY)/self.yINCH
        #                        )
        self.margins = [1,1]
        self.top = -1*self.margins[1]
        self.left = self.margins[1]
        self.right = self.printer_size[0] - self.margins[0]
        self.bottom = -1*(self.printer_size[1] - self.margins[1])

        self.hDC.StartPage()
        self.INCH = 1440 # TWIP
        self.hDC.SetMapMode(win32con.MM_TWIPS)
        
        self.cursor = (self.top * self.INCH)


    def get_current_rectangle (self):
        return (int(self.left*self.INCH), # left 
                int(self.cursor), # top
                int(self.right*self.INCH), # right
                int(self.bottom*self.INCH)) # bottom

    def set_font (self, name, pointsize, formatting_options={}):
        formatting_options['name']=name
        formatting_options['height']=pointsize*20 #TWIP = 20*pt.        
        self.hDC.SelectObject(
            win32ui.CreateFont(formatting_options)
            )

    def write_header (self, text):
        self.set_font('Arial',14,{'weight':win32con.FW_BOLD})
        self.write_text('%s\n'%text)
        
    def write_subheader (self, text):
        self.set_font('Arial',12,{'weight':win32con.FW_SEMIBOLD})
        self.write_text('\n%s\n'%text)

    def write_subsubheader (self, text):
        self.set_font('Arial',10,{'weight':win32con.FW_SEMIBOLD})
        self.write_text('\n%s'%text)
        
    def write_paragraph (self, text):
        self.set_font('Times',10)
        self.write_text(text)

    def write_text (self, text):
        text = str(text).encode('mbcs','replace')
        height = self.hDC.DrawText (
            text,
            self.get_current_rectangle(),
            win32con.DT_WORDBREAK | win32con.DT_LEFT | win32con.DT_CALCRECT)
        if height > (self.printable_area[1]*self.INCH):
            # Uh oh -- our text is too big to fit on a page
            # Let's approximate where we should split...
            times_too_much = height / (float(self.printable_area[1])*self.INCH)
            break_text_at = int(len(text)/times_too_much)
            # Now we split...
            while text[break_text_at]!=' ' and text[:break_text_at].find(' '):
                break_text_at -= 1
            self.write_paragraph(text[:break_text_at])
            self.write_paragraph(text[break_text_at:])
            return
        if (self.cursor - height) < (self.bottom*self.INCH):
            self.new_page()
        #print 'WRITING TEXT TO ',self.get_current_rectangle()
        height = self.hDC.DrawText(text,
                              self.get_current_rectangle(),
                                   win32con.DT_WORDBREAK | win32con.DT_LEFT)
        self.cursor += height

    def new_page (self):
        self.hDC.EndPage()
        self.hDC.StartPage()
        self.cursor = self.top * self.INCH

    def close (self):
        self.hDC.EndPage ()
        self.hDC.EndDoc ()
        if self.show_dialog:
            de.show_message(
                label=_("Printing completed."),
                sublabel=_("Printing is done. I hope this worked! Unfortunately, printing on Windows doesn't have a very fancy interface."),
                parent=self.parent
                )

class RecRenderer:

    def __init__ (self, rd, recs, mult=1, dialog_title=_("Print Recipes"),
                  dialog_parent=None, change_units=True):
        self.writer = SimpleWriter(dialog_parent=dialog_parent)
        do_new_page = False
        for r in recs:
            if do_new_page: self.writer.new_page()
            print 'Printing Recipe'
            r = RecWriter(rd,r,self.writer,change_units=change_units,mult=mult)
        print 'Closing print job'
        self.writer.close()

class RecWriter (exporter.exporter_mult):

    def __init__ (self, rd, r, writer, change_units=True, mult=1):
        self.writer = writer
        self.r = r
        self.rd = rd
        exporter.exporter_mult.__init__(self, rd, r, out=None, change_units=change_units, mult=mult,
                                        do_markup=True,
                                        use_ml=True,
                                        fractions=FRACTIONS_NORMAL)
        

    def write_head (self):
        pass

    def write_image (self, data):
        # This is do-able but hard...
        pass 

    def write_attr (self, label, text):
        attr=gglobals.NAME_TO_ATTR[label]
        if attr=='title':
            self.writer.write_header(text)
            return
        self.writer.write_paragraph("%s: %s"%(label,text))

    def write_text (self, label, text):
        self.writer.write_subheader("%s"%label)
        self.writer.write_paragraph("%s\n"%text)

    def write_inghead (self):
        self.writer.write_subheader("Ingredients")

    def write_grouphead (self, head):
        if head: self.writer.write_subsubheader("%s"%head)

    def write_ing (self, amount='1', unit=None, item=None, key=None, optional=False):
        out = ''
        for itm in [amount,unit,item,optional and _("(Optional)")]:
            if itm:
                if out:
                    out = out + ' ' + itm
                else:
                    out = itm
        self.writer.write_paragraph(out)
    

# class SimpleWriterRTF (rtf_exporter):
#     def __init__ (self, file=None, dialog_parent=None, show_dialog=True):
# 	print 'RTF printer SimpleWriter beginning'
#         self.setup_document()
#         self.recsection = PyRTF.Section(break_type=PyRTF.Section.PAGE) # This is where add_paragraph adds paragraphs
#         self.doc.Sections.append( self.recsection )
        
#     def write_header (self, text):
#         self.add_paragraph("%s\n"%text,self.ss.ParagraphStyles.Heading1)

#     def write_subheader (self, text):    
#         self.add_paragraph("%s\n"%text,self.ss.ParagraphStyles.Heading3)

#     def write_paragraph (self, text):
#         self.add_paragraph(text)

#     def close (self):
#         renderer = PyRTF.Renderer()
#         filename = tempfile.mktemp('.rtf')
#         outfile = file(filename,'w')
#         renderer.Write(self.doc,outfile)
#         outfile.close()
#         print_file_with_windows(filename)
        
    
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
