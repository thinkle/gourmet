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
import types, re
import tempfile, os.path
import math

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

import reportlab.lib.colors as colors
class Star (platypus.Flowable):
    '''A hand flowable.'''
    def __init__(self, size=None, fillcolor=colors.tan, strokecolor=colors.green):
        from reportlab.lib.units import inch
        if size is None: size=12 # 12 point
        self.fillcolor, self.strokecolor = fillcolor, strokecolor
        self.size = size
        # normal size is 4 inches
        
    def getSpaceBefore (self):
        return 6 # 6 points

    def getSpaceAfter (self):
        return 6 # 6 points
        
    def wrap(self, availW, availH):
        if self.size > availW or self.size > availH:
            if availW > availH:
                self.size = availH
            else:
                self.size = availW
        return (self.size,self.size)

    def draw (self):
        size = self.size # * 0.8
        self.draw_star(inner_length=size/4,
                       outer_length=size/2)

    def draw_circle (self, x, y, r):
        # Test...
        canvas = self.canv
        canvas.setLineWidth(0)        
        canvas.setStrokeColor(colors.grey)
        canvas.setFillColor(colors.grey)        
        p = canvas.beginPath()
        p.circle(x,y,r)
        p.close()
        canvas.drawPath(p,fill=1)

    def draw_half_star (self, inner_length=1*inch, outer_length=2*inch, points=5, origin=None):
        canvas = self.canv
        canvas.setLineWidth(0)
        if not origin: canvas.translate(self.size*0.5,self.size*0.5)
        else: canvas.translate(*origin)
        canvas.setFillColor(self.fillcolor)
        canvas.setStrokeColor(self.strokecolor)
        p = canvas.beginPath()
        inner = False # Start on top
        is_origin = True
        #print 'Drawing star with radius',outer_length,'(moving origin ',origin,')'
        for theta in range(0,360,360/(points*2)):
            if 0 < theta < 180: continue
            if inner: r = inner_length
            else: r = outer_length
            x = (math.sin(math.radians(theta)) * r)
            y = (math.cos(math.radians(theta)) * r)
            #print 'POINT:',x,y
            if is_origin:
                p.moveTo(x,y)
                is_origin = False
            else:
                p.lineTo(x,y)
            inner = not inner
        p.close()
        canvas.drawPath(p,fill=1)

    def draw_star (self, inner_length=1*inch, outer_length=2*inch, points=5, origin=None):
        canvas = self.canv
        canvas.setLineWidth(0)
        if not origin: canvas.translate(self.size*0.5,self.size*0.5)
        else: canvas.translate(*origin)
        canvas.setFillColor(self.fillcolor)
        canvas.setStrokeColor(self.strokecolor)
        p = canvas.beginPath()
        inner = False # Start on top
        is_origin = True
        #print 'Drawing star with radius',outer_length,'(moving origin ',origin,')'
        for theta in range(0,360,360/(points*2)):
            if inner: r = inner_length
            else: r = outer_length
            x = (math.sin(math.radians(theta)) * r)
            y = (math.cos(math.radians(theta)) * r)
            #print 'POINT:',x,y
            if is_origin:
                p.moveTo(x,y)
                is_origin = False
            else:
                p.lineTo(x,y)
            inner = not inner
        p.close()
        canvas.drawPath(p,fill=1)


class FiveStars (Star):

    def __init__ (self, height, filled=5, out_of=5,
                  filled_color=colors.black,
                  unfilled_color=colors.lightgrey
                  ):
        self.height = self.size = height
        self.filled = filled
        self.out_of = out_of
        self.filled_color = filled_color; self.unfilled_color = unfilled_color
        self.width = self.height * self.out_of + (self.height * 0.2 * (self.out_of-1)) # 20% padding
        self.ratio = self.height / 12 # 12 point is standard
        

    def wrap (self, *args):
        return self.width,self.height

    def draw (self):
        #self.canv.scale(self.ratio,self.ratio)
        self.draw_stars()

    def draw_stars (self):
        #if self.height
        for n in range(self.out_of):
            if self.filled - n >= 1:
                # Then we draw a gold star
                self.fillcolor,self.strokecolor = self.filled_color,self.filled_color
                r = self.height * 0.5
            else:
                self.fillcolor,self.strokecolor = self.unfilled_color,self.unfilled_color
                r = self.height * 0.75 * 0.5
            origin = (
                # X coordinate
                ((n >= 1 and (self.height * 1.2)) or self.height*0.5),
                # Y coordinate
                ((n < 1 and self.height* 0.5) or 0)
                )
            #print 'origin = ',#origin,'or',
            #print origin[0]/self.height,origin[1]/self.height
            #self.draw_circle(origin[0],origin[1],r)
            self.draw_star(points=5,origin=origin,inner_length=r/2,outer_length=r)
            if self.filled - n == 0.5:
                # If we're a half star...
                self.fillcolor,self.strokecolor = self.filled_color,self.filled_color                
                self.draw_half_star(points=5,
                                    inner_length=self.height*0.25,
                                    outer_length=self.height*0.5,
                                    origin=(0,0)
                                    )
            
class PdfWriter:

    def __init__ (self):
        self.keep_with_next = []    

    def setup_document (self, file, **kwargs):
        self.doc = platypus.SimpleDocTemplate(file)
        self.styleSheet=styles.getSampleStyleSheet()
        self.txt = []
        # Flag for keeping two items together -- specifically, when we
        # define a header, we set this flag to True... then our lovely
        # methods wait for the next element we define and put it and
        # our Head into a KeepTogether block
        
    def make_paragraph (self, txt, style=None, attributes=""):
        if attributes:
            txt = '<para %s>%s</para>'%(attributes,txt)
        if not style: style = self.styleSheet['Normal']
        try:
            return platypus.Paragraph(unicode(txt).encode('iso-8859-1','replace'),style)
        except UnicodeDecodeError:
            try:
                #print 'WORK AROUND UNICODE ERROR WITH ',txt[:20]
                # This seems to be the standard on windows.
                return platypus.Paragraph(txt,style)
            except:
                print 'Trouble with ',txt
                raise
    
    def write_paragraph (self, txt, style=None, keep_with_next=False, attributes=""):
        p = self.make_paragraph(txt,style,attributes)
        if keep_with_next:
            # If we want to keep this together -- we append it to a
            # little "holder" class for now...
            self.keep_with_next.append(p)
            return
        elif self.keep_with_next:
            self.keep_with_next.append(p)
            self.txt.extend(self.keep_with_next)
            #p = platypus.KeepTogether(
            #    self.keep_with_next
            #    )
            self.keep_with_next = []
        #self.txt.append(p)
        else:
            self.txt.append(p)

    def write_header (self, txt):
        """Write a header.

        WARNING: If this is not followed by a call to our write_paragraph(...keep_with_next=False),
        the header won't necessarily be written.
        """
        self.write_paragraph(
            txt,
            style=self.styleSheet['Heading1'],
            keep_with_next = True
            )

    def write_subheader (self, txt):
        """Write a subheader.

        WARNING: If this is not followed by a call to our write_paragraph(...keep_with_next=False),
        the header won't necessarily be written.
        """        
        self.write_paragraph(
            txt,
            style=self.styleSheet['Heading2'],
            keep_with_next=True
            )

    def close (self):
        if self.keep_with_next:
            self.txt.append(platypus.KeepWithNext(self.keep_with_next))
        self.doc.build(self.txt)
        
class PdfExporter (exporter.exporter_mult, PdfWriter):

    def __init__ (self, rd, r, out,
                  doc=None,
                  styleSheet=None,
                  txt=[],
                  **kwargs):
        PdfWriter.__init__(self)
        if type(out) in types.StringTypes:
            out = file(out,'wb')
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
            use_ml=True,
            order=['image','attr','ings','text'],
            do_markup=True,
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
            #self.master_txt.extend(self.txt)

    def handle_italic (self, chunk):
        return '<i>' + chunk + '</i>'
    
    def handle_bold (self, chunk):
        return '<b>' + chunk + '</b>'
    
    def handle_underline (self, chunk):
        return '<u>' + chunk + '</u>'

    def scale_image (self, image, proportion=None):
        # Platypus assumes image size is in points -- this appears to
        # be off by the amount below.
        if not proportion: proportion = inch/200 # we want 200 dots per image
        image.imageHeight = image.imageHeight*proportion
        image.imageWidth = image.imageWidth*proportion

    def write_image (self, data):
        fn = ImageExtras.write_image_tempfile(data)
        i = platypus.Image(fn)
        self.scale_image(i)
        factor = 1
        MAX_WIDTH = self.doc.width * 0.75
        MAX_HEIGHT = self.doc.height * 0.75
        if i.imageWidth > MAX_WIDTH:
            factor = MAX_WIDTH/i.imageWidth
        if i.imageHeight > MAX_HEIGHT:
            f = MAX_HEIGHT/i.imageHeight
            if f < factor: factor = f
        if factor < 1.0:
            #print 'Shrinking by ',factor
            self.scale_image(i,factor)
        #print 'Image resized to ',i.imageWidth,i.imageHeight
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
        if not self.attributes and hasattr(self,'image'):
            # If we only have an image...
            self.txt.append(self.image)
            return
        elif hasattr(self,'image') and self.image.imageWidth > (self.doc.width / 2.25):
            self.txt.append(self.image)
            self.txt.extend(self.attributes)
            #print 'Image too big -- no table for you!'
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
            ('LEFTPADDING',(0,0),(0,-1),0),
            # for debugging
            #('INNERGRID',(0,0),(-1,-1),.25,colors.red),
            #('BOX',(0,0),(-1,-1),.25,colors.red),            
            ]
                                )
            )
        self.txt.append(t)
        #self.txt = [platypus.KeepTogether(self.txt)]

    def make_rating (self, label, val):
        """Make a pretty representation of our rating.
        """
        try:
            assert(type(val)==int)
        except:
            raise TypeError("Rating %s is not an integer"%val)
        #print 'Get image file for ',val,
        i = FiveStars(10, filled=(val/2.0)) # 12 point
        lwidth = len(label+': ')*4 # A very cheap approximation of width
        t = platypus.Table(
            [[label+': ',i]],
            colWidths=[lwidth,inch],
            )
        t.hAlign = 'LEFT'
        t.setStyle(
            platypus.TableStyle([
            ('LEFTPADDING',(0,0),(-1,0),0),
            ('LEFTPADDING',(1,0),(1,0),6),
            ('TOPPADDING',(0,0),(-1,-1),0),
            ('ALIGNMENT',(1,0),(1,0),'LEFT'),
            ('VALIGN',(0,0),(0,0),'TOP'),
            # for debugging
            #('INNERGRID',(0,0),(-1,-1),.25,colors.black),
            #('BOX',(0,0),(-1,-1),.25,colors.black),            
             ]
                                )
            )
        return t
    
    def write_attr (self, label, text):
        attr = gglobals.NAME_TO_ATTR[label]
        if attr=='title':
            self.write_paragraph(text,style=self.styleSheet['Heading1'])
            return
        if attr=='rating':
            from gourmet.importers.importer import string_to_rating
            val = string_to_rating(text)
            if val:
                self.attributes.append(self.make_rating(label,val))
                return
        self.attributes.append(self.make_paragraph("%s: %s"%(label,text)))

    def write_text (self, label, text):
        #text = '<para>' + re.sub('\n(?!=$)','</para>\n<para>',text) + '</para>'
        #print 'text ->',unicode(text).encode('iso-8859-1','replace')
        self.write_subheader(label)
        first_para = True
        for t in text.split('\n'):
            # HARDCODING paragraph style to space
            if first_para:
                first_para = False
            else:
                self.write_paragraph(t,attributes="spacebefore='6'")

    def write_inghead (self):
        self.write_subheader(xml.sax.saxutils.escape(_('Ingredients')))

    def write_grouphead (self, name):
        self.write_paragraph(name,self.styleSheet['Heading3'])

    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        txt = ""
        for blob in [amount,unit,item,(optional and _('optional') or '')]:
            if not blob: continue
            if txt: txt += " %s"%blob
            else: txt = blob
        self.write_paragraph(txt)

class PdfExporterMultiDoc (exporter.ExporterMultirec, PdfWriter):
    def __init__ (self, rd, recipes, out, **kwargs):
        PdfWriter.__init__(self)
        if type(out) in types.StringTypes:
            out = file(out,'wb')
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
        #print 'We have ',len(self.txt),'elements.'
        #print 'Our first elements is:'
        #for n in range(1):
        #    print n,self.txt[n]
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
        #print 'category: ',c,' d: ',d
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
    from tempfile import tempdir
    import os.path
    sw = PdfWriter()
    f = file(os.path.join(tempdir,'foo.pdf'),'wb')
    sw.setup_document(f)
    #sw.write_header('Heading')
    #sw.write_subheader('This is a subheading')
    sw.write_paragraph('These are some sentences.  '*24)
    #sw.write_paragraph('This is a <i>paragraph</i> with <b>some</b> <u>markup</u>.')
    #sw.write_paragraph(u"This is some text with unicode - 45\u00b0, \u00bfHow's that?".encode('iso-8859-1'))
    #sw.write_paragraph(u"This is some text with a unicode object - 45\u00b0, \u00bfHow's that?")
    sw.close()
    f.close()
    star_file = file(os.path.join(tempdir,'star.pdf'),'wb')
    sw = PdfWriter()
    sw.setup_document(star_file)
    for n in range(6,72,2):
        sw.write_paragraph("This is some text with a %s pt star"%n)
        sw.txt.append(FiveStars(n,filled=3.5))
        
    sw.close()
    star_file.close()
    #import gnome
    #gnome.program_init('1.0','Gourmet PDF Exporter Test')
    #gglobals.launch_url('file:/os.path.join(tempdir,/star.pdf')
    #raise "I don')t want to go any further"
    #import gourmet.recipeManager as rm
    #import gnome
    #rd = rm.RecipeManager(file='/home/tom/Projects/grm/src/tests/reference_setup/recipes.db')
    #if os.name == 'nt':
    #    base = 'C:\\grm\grm'
    #else:
    #    base = '/home/tom/Projects/grm'
    #rd = rm.RecipeManager(file=os.path.join(base,'src','tests','reference_setup','recipes.db'))
    ##ofi = file(os.path.join(tempdir,'test_rec.pdf'),'w')
    ##rr = []
    #for n,rec in enumerate(rd.fetch_all(rd.rview)):
    #    if rec.image:
    #        rr.append(rec)
    #pe = PdfExporterMultiDoc(rd,rd.fetch_all(rd.rview),os.path.join(tempdir,'fooby.pdf'))
    #pe.run()
    import gourmet.gglobals as gglobals
    #gnome.program_init('1.0','Gourmet PDF Exporter Test')
    print 'Launching',os.path.join(tempdir,'foo.pdf')
    gglobals.launch_url(os.path.join(tempdir,'foo.pdf'))    
    print 'Launching',os.path.join(tempdir,'star.pdf')
    gglobals.launch_url(os.path.join(tempdir,'star.pdf'))

