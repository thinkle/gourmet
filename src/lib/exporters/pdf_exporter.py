from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import reportlab.platypus as platypus
from reportlab.platypus.flowables import ParagraphAndImage
import reportlab.lib.pagesizes as pagesizes
import reportlab.lib.fonts as fonts
import reportlab.lib.units as units
import reportlab.lib.styles as styles
from gettext import gettext as _
from gourmet import convert
from gourmet import gglobals
from gourmet import ImageExtras
import xml.sax.saxutils
import exporter
import types


# Code for MCLine from:
# http://two.pairlist.net/pipermail/reportlab-users/2005-February/003695.html
class MCLine(platypus.Flowable):
    """Line flowable --- draws a line in a flowable"""
    
    def __init__(self,width):
        platypus.Flowable.__init__(self)
        self.width = width
        
    def __repr__(self):
        return "Line(w=%s)" % self.width
    
    def draw(self):
        self.canv.line(0,0,self.width,0)
        
class PdfWriter:

    def setup_document (self, file, **kwargs):
        self.doc = platypus.SimpleDocTemplate(file)
        self.styleSheet=styles.getSampleStyleSheet()
        self.txt = []

    def write_header (self, txt):
        self.write_paragraph(
            txt,
            style=self.styleSheet['Heading1']
            )

    def write_subheader (self, txt):
        self.write_paragraph(
            txt,
            style=self.styleSheet['Heading2']
            )

    def make_paragraph (self, txt, style=None):
        if not style: style = self.styleSheet['Normal']
        try:
            return platypus.Paragraph(unicode(txt).encode('iso-8859-1','replace'),style)
        except UnicodeDecodeError:
            print 'Trouble with ',txt
            raise
            
    def write_paragraph (self, txt, style=None):
        self.txt.append(self.make_paragraph(txt,style))

    def close (self):
        self.doc.build(self.txt)
        
class PdfExporter (exporter.exporter_mult, PdfWriter):

    def __init__ (self, rd, r, out,
                  doc=None,
                  styleSheet=None,
                  txt=[],
                  **kwargs):
        if type(out) in types.StringTypes:
            out = file(out,'w')
        if not doc:
            self.setup_document(out)
            self.multidoc = False
        else:
            self.doc = doc; self.styleSheet = styleSheet; self.txt = []
            self.master_txt = txt
            self.multidoc = True
            # Put nice lines to separate multiple recipes out...
            self.txt.append(MCLine(inch*6))
        exporter.exporter_mult.__init__(
            self,
            rd,r,
            None, # exporter_mult has no business touching a file
            do_markup=False,
            use_ml=True,
            order=['image','attr','ings','text'],
            fractions=convert.FRACTIONS_NORMAL,
            **kwargs
            )
        if not self.multidoc:
            self.close() # Finish the document if this is all-in-one
            out.close()
        else:
            #self.txt.append(platypus.PageBreak()) # Otherwise, a new page
            # Append to the txt list we were handed ourselves in a KeepTogether block
            self.txt.append(platypus.Spacer(0,inch*0.5))
            self.master_txt.append(platypus.KeepTogether(self.txt))


    def write_image (self, data):
        fn = ImageExtras.write_image_tempfile(data)
        i = platypus.Image(fn)
        self.image = i

    def write_attr_head (self):
        # just move .txt aside through the attrs -- this way we can
        # use our regular methods to keep adding attribute elements 
        self.attributes = []

    def write_attr_foot (self):
        # If we have 3 or fewer attributes and no images, we don't
        # need a table
        if len(self.attributes)<=3 and not hasattr(self,'image'):
            self.txt.extend(self.attributes)
            return
        # Otherwise, we're going to make a table...
        if hasattr(self,'image'):
            # If we have an image, we put attributes on the
            # left, image on the right
            table_data = [
                [# 1 row
                # column 1 = attributes
                self.attributes,
                # column 2 = image
                self.image
                ],
                # End of "table"
                ]
        else:
            nattributes = len(self.attributes)
            first_col_size = nattributes/2 + nattributes % 2
            first = self.attributes[:first_col_size]
            second = self.attributes[first_col_size:]
            table_data = []
            for n,left in enumerate(first):
                right = len(second)>n and second[n] or ''
                table_data.append([left,right])
        t = platypus.Table(table_data)
        t.setStyle(
            platypus.TableStyle([
            ('VALIGN',(0,0),(0,-1),'TOP'),
            ]
                                )
            )
        self.txt.append(t)


    def write_attr (self, label, text):
        attr = gglobals.NAME_TO_ATTR[label]
        if attr=='title':
            self.write_header(text)
        else:
            self.attributes.append(self.make_paragraph("%s: %s"%(label,text)))

    def write_text (self, label, text):
        self.write_subheader(label)
        self.write_paragraph(text)

    def write_inghead (self):
        self.write_subheader(xml.sax.saxutils.escape(_('Ingredients')))

    def write_grouphead (self, name):
        self.write_paragraph(name,self.styleSheet['Heading3'])

    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        txt = ""
        for blob in [amount,unit,item,optional and _('optional') or None]:
            if txt: txt += " %s"%blob
            else: txt = blob
        self.write_paragraph(txt)

class PdfExporterMultiDoc (exporter.ExporterMultirec, PdfWriter):
    def __init__ (self, rd, recipes, out, **kwargs):
        if type(out) in types.StringTypes:
            out = file(out,'w')
        self.setup_document(out)
        self.output_file = out
        exporter.ExporterMultirec.__init__(
            self,
            rd, recipes, out,
            one_file=True, ext='pdf',
            exporter=PdfExporter,
            exporter_kwargs={'doc':self.doc,
                             'styleSheet':self.styleSheet,
                             'txt':self.txt,
                             },
            **kwargs
            )

    def write_footer (self):
        print 'We have ',len(self.txt),'elements.'
        self.close()
        self.output_file.close()
            

def write_shopping_list (shopper, recs, file, head=_('Shopping List')):
    # setup document
    self.styleSheet=styles.getSampleStyleSheet()
    normsty=styleSheet['Normal']
    catheadsty=styleSheet['Heading3']
    headsty = styleSheet['Heading1']
    spacer = platypus.Spacer(1,0.2*units.inch)
    # organize shopping output
    org = shopper.organize(shopper.dic)
    txt = []
    txt.append(platypus.Paragraph(head,headsty))
    txt.append(platypus.Paragraph(_("Shopping list for: "),catheadsty))
    for r,mult in recs.items():
        recline = "%s"%r.title

        if mult: recline += " x%s"%convert.float_to_frac(mult)
        p=platypus.Paragraph(recline,normsty)
        txt.append(p)
    txt.append(spacer)
    for c,d in org:
        print 'category: ',c,' d: ',d
        p=platypus.Paragraph(c,catheadsty)
        # space around the paragraph...        
        #txt.append(spacer)
        txt.append(p)
        for i,a in d:
            p=platypus.Paragraph("%s %s"%(a,i),normsty)
            txt.append(p)
        # space around the list...
        #txt.append(spacer)
    #print 'txt: ',txt
    doc.build(txt)

if __name__ == '__main__':
    sw = PdfWriter()
    f = file('/tmp/foo.pdf','w')
    sw.setup_document(f)
    sw.write_header('Heading')
    sw.write_subheader('This is a subheading')
    sw.write_paragraph('These are some sentences.  '*24)
    sw.write_paragraph('This is a <i>paragraph</i> with <b>some</b> <u>markup</u>.')
    #sw.write_paragraph(u"This is some text with unicode - 45\u00b0, \u00bfHow's that?".encode('iso-8859-1'))
    sw.write_paragraph(u"This is some text with a unicode object - 45\u00b0, \u00bfHow's that?")
    sw.close()
    f.close()

    import gourmet.recipeManager as rm
    rd = rm.RecipeManager()
    #ofi = file('/tmp/test_rec.pdf','w')
    pe = PdfExporterMultiDoc(rd,rd.fetch_all(rd.rview)[0:10],'/tmp/fooby.pdf').run()
    
    
    
