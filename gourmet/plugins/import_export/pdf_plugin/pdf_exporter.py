from io import BytesIO
from gi.repository import Gtk
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch,mm
from reportlab.pdfgen import canvas
import reportlab.platypus as platypus
from reportlab.platypus.flowables import ParagraphAndImage
import reportlab.lib.pagesizes as pagesizes
import reportlab.lib.fonts as fonts
import reportlab.lib.units as units
import reportlab.lib.styles as styles
from gettext import gettext as _
from gettext import ngettext
from gourmet import convert
from gourmet import gglobals
from gourmet.gtk_extras import dialog_extras as de
from gourmet.gtk_extras import optionTable
from gourmet.gtk_extras import cb_extras
from gourmet import image_utils
from gourmet.prefs import Prefs
import xml.sax.saxutils
import gourmet.exporters.exporter as exporter
import types, re
import tempfile, os.path
import math
from .page_drawer import PageDrawer
import webbrowser

DEFAULT_PDF_ARGS = {'bottom_margin': 72, 'pagesize': 'letter', 'right_margin': 72, 'top_margin': 72, 'left_margin': 72, 'pagemode': 'portrait', 'base_font_size': 10, 'mode': ('column', 1)}

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
        for theta in range(0, 360, 360 // (points * 2)):
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

# Copied from http://two.pairlist.net/pipermail/reportlab-users/2004-April/002917.html
# A convenience class for bookmarking
class Bookmark(platypus.Flowable):
    """ Utility class to display PDF bookmark. """

    def __init__(self, title, key):
        self.title = title
        self.key = key
        platypus.Flowable.__init__(self)

    def wrap(self, availWidth, availHeight):
        """ Doesn't take up any space. """
        return (0, 0)

    def draw(self):
        # set the bookmark outline to show when the file's opened
        self.canv.showOutline()
        # step 1: put a bookmark on the
        self.canv.bookmarkPage(str(self.key))
        # step 2: put an entry in the bookmark outline
        self.canv.addOutlineEntry(self.title,
                                  self.key, 0, 0)


class PdfWriter:

    def __init__ (self, allrecs=[]):
        pass

    def setup_document (self, file, mode=('column',1), size='default', pagesize='letter',
                        pagemode='portrait',left_margin=inch,right_margin=inch,
                        top_margin=inch,
                        bottom_margin=inch,
                        base_font_size=10
                        ):
        frames = self.setup_frames(mode,size,pagesize,pagemode,
                                   left_margin,right_margin,top_margin,
                                   bottom_margin,base_font_size)
        pt = platypus.PageTemplate(frames=frames)
        self.doc = platypus.BaseDocTemplate(file,pagesize=self.pagesize,
                                            pageTemplates=[pt],)
        self.doc.frame_width = frames[0].width
        self.doc.frame_height = frames[0].height
        self.styleSheet = styles.getSampleStyleSheet()
        perc_scale = float(base_font_size)/self.styleSheet['Normal'].fontSize
        if perc_scale!=1.0:
            self.scale_stylesheet(perc_scale)
        self.txt = []

    def setup_frames (self,mode=('column',1), size='default', pagesize='letter',
                        pagemode='portrait',left_margin=inch,right_margin=inch,
                        top_margin=inch,
                        bottom_margin=inch,
                        base_font_size=10):
        if not isinstance(mode, tuple):
            raise Exception("What is this mode! %s" % str(mode))
        if isinstance(pagesize, str):
            self.pagesize = getattr(pagesizes,pagemode)(getattr(pagesizes,pagesize))
        else:
            self.pagesize = getattr(pagesizes,pagemode)(pagesize)
        self.margins = (left_margin,right_margin,top_margin,bottom_margin)
        if mode[0] == 'column':
            frames = self.setup_column_frames(mode[1])
        elif mode[0] == 'index_cards':
            frames = self.setup_multiple_index_cards(mode[1])
        else:
            raise Exception("WTF - mode = %s" % str(mode))
        return frames

    def scale_stylesheet (self, perc):
        for name,sty in list(self.styleSheet.byName.items()):
            for attr in ['firstLineIndent',
                         'fontSize',
                         'leftIndent',
                         'rightIndent',
                         'leading']:
                setattr(sty,attr,int(perc*getattr(sty,attr)))

    def setup_column_frames (self, n):
        COLUMN_SEPARATOR = 0.5 * inch
        x = self.pagesize[0]
        y = self.pagesize[1]
        leftM,rightM,topM,bottomM = self.margins
        FRAME_Y = bottomM
        FRAME_HEIGHT = y - topM - bottomM
        FRAME_WIDTH = (x - (COLUMN_SEPARATOR*(n-1)) - leftM - rightM)/n
        frames = []
        for i in range(n):
            left_start = leftM + (FRAME_WIDTH + COLUMN_SEPARATOR)*i
            frames.append(
                platypus.Frame(
                left_start,FRAME_Y,width=FRAME_WIDTH,height=FRAME_HEIGHT
                )
                )
        return frames

    def setup_multiple_index_cards (self,card_size):
        leftM,rightM,topM,bottomM = self.margins
        MINIMUM_SPACING = 0.1*inch
        drawable_x = self.pagesize[0] - leftM - rightM
        drawable_y = self.pagesize[1] - topM - bottomM
        fittable_x = int(drawable_x / (card_size[0]+MINIMUM_SPACING))
        fittable_y = int(drawable_y / (card_size[1]+MINIMUM_SPACING))
        # Raise a ValueError if we can't actually fit multiple index cards on this page.
        if (not fittable_x) or (not fittable_y):
            raise ValueError("Card size %s does not fit on page %s with margins %s"%(
                card_size,self.pagesize,self.margins
                )
                             )
        x_spacer = (
            # Extra space =
            fittable_x * # Number of cards times
            ((drawable_x/fittable_x) # space per card
             - card_size[0] ) # - space occupied by card
            / # Divide extra space by n+1, so we get [   CARD    ], [  CARD  CARD  ], etc.
            (fittable_x+1)
            )
        y_spacer = (
            fittable_y *
            ((drawable_y/fittable_y)
              - (card_size[1]))
             /
            (fittable_y+1)
            )
        frames = []
        for x in range(fittable_x):
            x_start = leftM + (x_spacer*(x+1)) + (card_size[0]*x)
            for y in range(fittable_y-1,-1,-1):
                # Count down for the y, since we start from the bottom
                # and move up
                y_start = bottomM + (y_spacer*(y+1)) +  (card_size[1]*y)
                frames.append(
                    platypus.Frame(x_start,y_start,
                                   width=card_size[0],
                                   height=card_size[1],
                                   showBoundary=1)
                    )
        return frames

    def make_paragraph (self, txt, style=None, attributes="",keep_with_next=False):
        if attributes:
            xmltxt = '<para %s>%s</para>'%(attributes,txt)
        else:
            xmltxt = '<para>%s</para>'%txt
        if not style: style = self.styleSheet['Normal']
        try:
            return platypus.Paragraph(str(xmltxt),style)
        except UnicodeDecodeError:
            try:
                #print 'WORK AROUND UNICODE ERROR WITH ',txt[:20]
                # This seems to be the standard on windows.
                platypus.Paragraph(xmltxt,style)
            except:
                print('Trouble with ',xmltxt)
                raise
        except:
            # Try escaping text...
            print('TROUBLE WITH',txt[:20],'TRYING IT ESCAPED...')
            return self.make_paragraph(xml.sax.saxutils.escape(txt),
                                style,
                                attributes,
                                keep_with_next)

    def write_paragraph (self, txt, style=None, keep_with_next=False, attributes=""):
        p = self.make_paragraph(txt,style,attributes,keep_with_next=keep_with_next)
        if keep_with_next:
            # Keep with next isn't working, so we use a conditional
            # page break, on the assumption that no header should have
            # less than 3/4 inch of stuff after it on the page.
            self.txt.append(platypus.CondPageBreak(0.75*inch))
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
        t = self.txt[:]
        try: self.doc.build(self.txt)
        except:
            print('Trouble building',t[:20])
            raise

class PdfExporter (exporter.exporter_mult, PdfWriter):

    def __init__ (self, rd, r, out,
                  doc=None,
                  styleSheet=None,
                  txt=[],
                  pdf_args=DEFAULT_PDF_ARGS,
                  all_recipes=[], # For learning about references...
                  **kwargs):
        self.all_recipes = all_recipes
        PdfWriter.__init__(self)
        if isinstance(out, str):
            self.out = open(out, 'wb')
        else:
            self.out = out
        if not doc:
            self.setup_document(self.out,**pdf_args)
            self.multidoc = False
        else:
            self.doc = doc; self.styleSheet = styleSheet; self.txt = []
            self.master_txt = txt
            self.multidoc = True
            # Put nice lines to separate multiple recipes out...
            #if pdf_args.get('mode',('columns',1))[0]=='columns':
            #    self.txt.append(MCLine(self.doc.frame_width*0.8))
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

    def write_foot (self):
        if not self.multidoc:
            self.close() # Finish the document if this is all-in-one
            #self.out.close()
        else:
            #self.txt.append(platypus.PageBreak()) # Otherwise, a new page
            # Append to the txt list we were handed ourselves in a KeepTogether block
            #self.txt.append(platypus.Spacer(0,inch*0.5))
            #if pdf_args.get('mode',('column',1))[0]=='column':
            #    self.master_txt.append(platypus.KeepTogether(self.txt))
            #else:
            if self.master_txt:
                self.master_txt.append(platypus.FrameBreak())
            self.master_txt.extend(self.txt)
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
        if not proportion: proportion = inch/100 # we want 100 dots per image
        image.drawHeight = image.drawHeight*proportion
        image.drawWidth = image.drawWidth*proportion

    def write_image(self, data: bytes):
        buf = BytesIO(data)
        i = platypus.Image(buf)
        self.scale_image(i)
        factor = 1
        MAX_WIDTH = self.doc.frame_width * 0.35
        MAX_HEIGHT = self.doc.frame_height * 0.5
        if i.drawWidth > MAX_WIDTH:
            factor = MAX_WIDTH/i.drawWidth
        if i.drawHeight > MAX_HEIGHT:
            f = MAX_HEIGHT/i.drawHeight
            if f < factor: factor = f
        if factor < 1.0:
            self.scale_image(i,factor)
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
        elif hasattr(self,'image') and self.image.drawWidth > (self.doc.frame_width / 2.25):
            self.txt.append(self.image)
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
            first_col_size = nattributes//2 + nattributes % 2
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
        if not isinstance(val, int):
            raise TypeError("Rating %s is not an integer"%val)
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
        attr = gglobals.NAME_TO_ATTR.get(label,label)
        if attr=='title':
            self.txt.append(Bookmark(self.r.title,'r'+str(self.r.id)))
            self.write_paragraph(text,style=self.styleSheet['Heading1'])
            return
        if attr=='rating':
            from gourmet.importers.importer import string_to_rating
            val = string_to_rating(text)
            if val:
                self.attributes.append(self.make_rating(label,val))
                return
        if attr=='link':
            trimmed = text.strip()
            if len(trimmed)>32:
                trimmed=trimmed[:29]+'&#8230;' # ellipsis dots
            self.attributes.append(self.make_paragraph('%s: <link href="%s">%s</link>'%(label,text,trimmed)))
            return
        if attr=='source':
            trimmed = text.strip()
            if len(trimmed)>32:
                trimmed=trimmed[:29]+'&#8230;' # ellipsis dots
            self.attributes.append(self.make_paragraph('%s: %s'%(label,trimmed)))
            return
        # If nothing else has returned...
        self.attributes.append(self.make_paragraph("%s: %s"%(label,text)))

    def write_text (self, label, text):
        self.write_subheader(label)
        first_para = True
        for t in text.split('\n'):
            # HARDCODING paragraph style to space
            if first_para:
                first_para = False
            self.write_paragraph(t,attributes="spacebefore='6'")

    def write_inghead (self):
        self.save_txt = self.txt[:]
        self.txt = []
        self.write_subheader(xml.sax.saxutils.escape(_('Ingredients')))

    def write_grouphead (self, name):
        self.write_paragraph(name,self.styleSheet['Heading3'])

    def write_ingfoot (self):
        # Ugly -- we know that heads comprise two elements -- a
        # condbreak and a head...
        ings = self.txt[2:]
        if len(ings) > 4:
            half = (len(ings) / 2)
            first_half = ings[:-half]
            second_half = ings[-half:]
            t = platypus.Table(
                [[first_half,second_half]]
                )
            t.hAlign = 'LEFT'
            t.setStyle(
                platypus.TableStyle([
                ('VALIGN',(0,0),(1,0),'TOP'),
                ]
                                    )
                )
            self.txt = self.txt[:2] + [t]
        self.txt = self.save_txt + [platypus.KeepTogether(self.txt)]

    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        txt = ""
        for blob in [amount,unit,item,(optional and _('optional') or '')]:
            if not blob: continue
            if txt: txt += " %s"%blob
            else: txt = blob
        hanging = inch*0.25
        self.write_paragraph(
            txt,
            attributes=' firstLineIndent="-%(hanging)s" leftIndent="%(hanging)s"'%locals()
            )

    def write_ingref (self, amount, unit, item, refid, optional):
        if refid in [r.id for r in self.all_recipes]:
            txt = ""
            for blob in [amount,unit,item,(optional and _('optional') or '')]:
                if blob == item:
                    blob = '<link href="r%s">'%refid + blob + '</link>'
                elif not blob:
                    continue
                if txt: txt += " %s"%blob
                else: txt = blob
            hanging = inch*0.25
            self.write_paragraph(
                txt,
                attributes=' firstLineIndent="-%(hanging)s" leftIndent="%(hanging)s"'%locals()
                )
        else:
            return self.write_ing(amount,unit,item,optional=optional)

class PdfExporterMultiDoc (exporter.ExporterMultirec, PdfWriter):
    def __init__ (self, rd, recipes, out, conv=None, pdf_args=DEFAULT_PDF_ARGS,
                  **kwargs):
        PdfWriter.__init__(self)
        if isinstance(out, str):
            out = open(out, 'wb')
        self.setup_document(out,**pdf_args)
        self.output_file = out
        kwargs['doc'] = self.doc
        kwargs['styleSheet'] = self.styleSheet
        kwargs['txt'] = self.txt
        kwargs['pdf_args'] = pdf_args
        kwargs['all_recipes']=recipes
        exporter.ExporterMultirec.__init__(
            self,
            rd, recipes, out,
            one_file=True, ext='pdf',
            exporter=PdfExporter,
            conv=conv,
            exporter_kwargs=kwargs,
            )

    def write_footer (self):
        self.close()
        self.output_file.close()

class Sizer (PdfWriter):

    def get_size (self, *args, **kwargs):
        frames = self.setup_frames(*args,**kwargs)
        return self.pagesize,frames

    def get_pagesize_and_frames_for_widget (self, *args, **kwargs):
        ps,ff = self.get_size(*args,**kwargs)
        frames = [
            (f.x1, # X (top corner)
             ps[1]-f._y2, #Y (top corner)
             f.width,f.height) for f in ff]
        return ps,frames

class PdfPageDrawer (PageDrawer):

    def __init__ (self,*args,**kwargs):
        PageDrawer.__init__(self,*args,**kwargs)
        self.sizer = Sizer()
        self.set_page()

    def set_page (self, *args, **kwargs):
        self.last_kwargs = kwargs
        size,areas = self.sizer.get_pagesize_and_frames_for_widget(*args,**kwargs)
        self.set_page_area(size[0],size[1],areas)

PDF_PREF_DEFAULT={
    'page_size':_('Letter'),
    'orientation':_('Portrait'),
    'font_size':10,
    'page_layout':_('Plain'),
    'left_margin':1.0*inch,
    'right_margin':1.0*inch,
    'top_margin':1.0*inch,
    'bottom_margin':1.0*inch,
    }

class CustomUnitOption (optionTable.CustomOption):

    '''An option for optionTable with adjustable units -- used for margins.
    '''

    units = {
        '"':inch,
        _('cm'):10*mm,
        _('points'):1,
        }

    min_val = 0.125*inch
    max_val = 8*inch

    adjustments = {
        inch:(0.125,0.5),
        10*mm:(0.5,1),
        1:(5,25),
        }

    def __init__ (self, default_value = inch):
        Gtk.HBox.__init__(self) # do we really inherit from HBox?
        self.__quiet__ = False
        self.unit_combo = Gtk.ComboBoxText()
        for key in self.units:
            self.unit_combo.append_text(key)
        unit = Prefs.instance().get('default_margin_unit', _('cm'))
        if unit not in self.units: unit = _('cm')
        self.last_unit = self.units[unit]
        cb_extras.setup_typeahead(self.unit_combo)
        cb_extras.cb_set_active_text(self.unit_combo,unit)
        self.unit_combo.connect('changed',self.unit_changed_cb)
        self.value_adjustment = Gtk.Adjustment(
            value=self.adjust_to_unit(default_value),
            lower= self.min_val / self.last_unit,
            upper = self.max_val / self.last_unit,
            step_incr = self.adjustments[self.last_unit][0],
            page_incr = self.adjustments[self.last_unit][1],
            )
        def emit_changed (*args):
            self.emit('changed')
        self.value_adjustment.connect('changed', emit_changed)
        self.value_widget = Gtk.SpinButton()
        self.value_widget.set_adjustment(self.value_adjustment)
        self.value_widget.set_digits(2)
        self.value_widget.connect('changed', emit_changed)
        self.value_widget.show()
        self.unit_combo.show()
        self.pack_start(self.value_widget, True, True, 0)
        self.pack_start(self.unit_combo, True, True, 0)

    def set_unit (self, unit):
        cb_extras.cb_set_active_text(self.unit_combo,unit)

    def unit_changed_cb (self, widget):
        new_unit = self.units[self.unit_combo.get_active_text()]
        Prefs.instance()['default_margin_unit'] = self.unit_combo.get_active_text()
        old_val = self.value_adjustment.get_value() * self.last_unit
        self.last_unit = self.units[self.unit_combo.get_active_text()]
        new_val = self.adjust_to_unit(old_val)
        self.value_adjustment.set_upper(self.max_val / self.last_unit)
        self.value_adjustment.set_lower(self.min_val / self.last_unit)
        self.value_adjustment.set_step_increment(self.adjustments[self.last_unit][0])
        self.value_adjustment.set_page_increment(self.adjustments[self.last_unit][1])
        self.value_adjustment.set_value(new_val)
        if not self.__quiet__:
            self.emit('changed')

    def adjust_to_unit (self, raw_val):
        '''Round the value to an appropriate number for our current
        unit
        '''
        val = raw_val / self.last_unit
        adj = self.adjustments[self.last_unit][0]
        # "Round" to the increment adjustment specified for our unit
        floor =  int(val/adj) * adj
        ceiling = (int(val/adj)+1) * adj
        # Pick whatever is closest...
        if abs(floor - val) > abs(ceiling - val):
            return ceiling
        else:
            return floor

    def get_value (self):
        return self.last_unit * self.value_adjustment.get_value()

    def set_value (self, value):
        self.value_adjustment.set_value(value/self.last_unit)
        if not self.__quiet__:
            self.emit('changed')

    def sync_to_other_cuo (self, cuo):
        def change_cb (other_cuo):
            self.__quiet__ = True
            self.set_unit(other_cuo.unit_combo.get_active_text())
            self.__quiet__ = False
        cuo.connect('changed',change_cb)

class PdfPrefGetter:
    page_sizes = {
        _('11x17"'):'elevenSeventeen',
        _('Index Card (3.5x5")'):(3.5*inch,5*inch),
        _('Index Card (4x6")'):(4*inch,6*inch),
        _('Index Card (5x8")'):(5*inch,8*inch),
        _('Index Card (A7)'):(74*mm,105*mm),
        _('Letter'):'letter',
        _('Legal'):'legal',
        'A0':'A0','A1':'A1','A2':'A2','A3':'A3','A4':'A4','A5':'A5','A6':'A6',
        'B0':'B0','B1':'B1','B2':'B2','B3':'B3','B4':'B4','B5':'B5','B6':'B6',
        }

    INDEX_CARDS = [(3.5*inch,5*inch),(4*inch,6*inch),(5*inch,8*inch),(74*mm,105*mm)]
    INDEX_CARD_LAYOUTS = [_('Index Cards (3.5x5)'),
                          _('Index Cards (4x6)'),
                          _('Index Cards (A7)'),
                          ]
    layouts = {
        _('Plain'):('column',1),
        _('Index Cards (3.5x5)'):('index_cards',(5*inch,3.5*inch)),
        _('Index Cards (4x6)'):('index_cards',(6*inch,4*inch)),
        _('Index Cards (A7)'):('index_cards',(105*mm,74*mm)),
        }

    page_modes = {
        _('Portrait'):'portrait',
        _('Landscape'):'landscape',
        }

    OPT_PS,OPT_PO,OPT_FS,OPT_PL,OPT_LM,OPT_RM,OPT_TM,OPT_BM = list(range(8))

    def __init__(self):
        self.prefs = Prefs.instance()
        defaults = self.prefs.get('PDF_EXP', PDF_PREF_DEFAULT)
        self.size_strings = list(self.page_sizes.keys())
        self.size_strings.sort()
        for n in range(2,5):
            self.layouts[ngettext('%s Column','%s Columns',n)%n]=('column',n)
        self.make_reverse_dicts()
        self.layout_strings = list(self.layouts.keys())
        self.layout_strings.sort()
        margin_widgets = [
            CustomUnitOption(defaults.get(pref,PDF_PREF_DEFAULT[pref]))
            for pref in ['left_margin','right_margin','top_margin','bottom_margin']
            ]
        # Make unit changes to one widget affect all the others!
        for m in margin_widgets:
            for mm in margin_widgets:
                if mm is not m:
                    m.sync_to_other_cuo(mm)

        self.opts = [
            [_('Paper _Size')+':',(defaults.get('page_size',PDF_PREF_DEFAULT['page_size']),
                                  self.size_strings)],
            [_('_Orientation')+':',(defaults.get('orientation',PDF_PREF_DEFAULT['orientation']),
                                    list(self.page_modes.keys()))],
            [_('_Font Size')+':',int(defaults.get('font_size',PDF_PREF_DEFAULT['font_size']))],
            [_('Page _Layout'),(defaults.get('page_layout',PDF_PREF_DEFAULT['page_layout']),
                                self.layout_strings)],
            [_('Left Margin')+':',margin_widgets[0]],
            [_('Right Margin')+':',margin_widgets[1]],
            [_('Top Margin')+':',margin_widgets[2]],
            [_('Bottom Margin')+':',margin_widgets[3]],
            ]

        self.page_drawer = PdfPageDrawer(yalign=0.0)
        self.in_ccb = False
        self.setup_widgets()
        self.table.connect('changed',self.change_cb)
        self.table.emit('changed')
        self.page_drawer.set_size_request(200,100)
        self.page_drawer.show()

    def make_reverse_dicts (self):
        self.page_sizes_r = {}; self.layouts_r = {}; self.page_modes_r = {}
        for dict,dict_r in [
            (self.page_sizes,self.page_sizes_r),
            (self.layouts,self.layouts_r),
            (self.page_modes,self.page_modes_r)]:
            for k,v in list(dict.items()): dict_r[v]=k

    def setup_widgets (self):
        self.pd = de.PreferencesDialog(self.opts,option_label=None,value_label=None,
                                  label=_('PDF Options'),
                                  )
        self.pd.hbox.pack_start(self.page_drawer, fill=True, expand=True,
                                padding=0)
        self.table = self.pd.table

    def run (self):
        self.pd.run()
        return self.get_args_from_opts(self.opts)

    def get_args_from_opts (self, opts):
        args = {}
        prefs = self.prefs.get('PDF_EXP', {})
        args['pagesize'] = self.page_sizes[opts[self.OPT_PS][1]] # PAGE SIZE
        prefs['page_size'] = self.page_sizes_r[args['pagesize']]
        args['pagemode'] = self.page_modes[opts[self.OPT_PO][1]] # PAGE MODE
        prefs['orientation'] = self.page_modes_r[args['pagemode']]
        prefs['font_size'] = args['base_font_size'] = opts[self.OPT_FS][1] # FONT SIZE
        args['mode'] = self.layouts[opts[self.OPT_PL][1]] # LAYOUT/MODE
        prefs['page_layout'] = self.layouts_r[args['mode']]
        prefs['left_margin'] = args['left_margin'] = opts[self.OPT_LM][1]
        prefs['right_margin'] = args['right_margin'] = opts[self.OPT_RM][1]
        prefs['top_margin'] = args['top_margin'] = opts[self.OPT_TM][1]
        prefs['bottom_margin'] = args['bottom_margin'] = opts[self.OPT_BM][1]
        return args

    def change_cb (self, option_table, *args,**kwargs):
        if self.in_ccb: return
        self.in_ccb = True
        option_table.apply()
        args = self.get_args_from_opts(self.opts)
        changed = False
        if args['pagesize']!=self.page_drawer.last_kwargs.get('pagesize','letter'):
            last_pagesize = self.page_drawer.last_kwargs.get('pagesize','letter')
            pagesize = args['pagesize']
            # If pagesize has changed from index to non-index card,
            # toggle orientation and margins by default for our user's
            # convenience...
            if pagesize in self.INDEX_CARDS and last_pagesize not in self.INDEX_CARDS:
                changed = True
                option_table.set_option(self.OPT_PO,_('Landscape'))
                for o in [self.OPT_LM,self.OPT_RM,self.OPT_BM,self.OPT_TM]:
                    option_table.set_option(o,0.25)
                option_table.set_option(self.OPT_FS,8)
                # Also -- make sure we don't allow index card layout in this...
                cb = option_table.widgets[self.OPT_PL][0]
                if not hasattr(self,'index_card_layouts_to_put_back'):
                    self.index_card_layouts_to_put_back = []
                    for i in self.INDEX_CARD_LAYOUTS:
                        pos=self.layout_strings.index(i)
                        self.index_card_layouts_to_put_back.append((pos,i))
                    self.index_card_layouts_to_put_back.sort()
                n = cb.get_active()
                if n in [i[0] for i in self.index_card_layouts_to_put_back]:
                    default_pos = self.layout_strings.index(_('Plain'))
                    cb.set_active(default_pos)
                self.index_card_layouts_to_put_back.reverse()
                for pos,txt in self.index_card_layouts_to_put_back:
                    cb.remove_text(pos)
                self.index_card_layouts_to_put_back.reverse()
            elif pagesize not in self.INDEX_CARDS and last_pagesize in self.INDEX_CARDS:
                changed = True
                option_table.set_option(self.OPT_PO,_('Portrait'))
                for o in [self.OPT_LM,self.OPT_RM,self.OPT_BM,self.OPT_TM]:
                    option_table.set_option(o,1)
                option_table.set_option(self.OPT_FS,10)
                # Also -- we allow index card layout in this...
                cb = option_table.widgets[self.OPT_PL][0]
                if hasattr(self,'index_card_layouts_to_put_back'):
                    for pos,txt in self.index_card_layouts_to_put_back:
                        cb.insert_text(pos,txt)

        if (args['mode'][0] != self.page_drawer.last_kwargs.get('mode',('column',1))[0]
            or
            (args['mode'][0]=='index_cards'
             and (args['mode'] != self.page_drawer.last_kwargs['mode']
                  or
                  (args['pagesize'] != self.page_drawer.last_kwargs['pagesize']
                   and
                   'elevenSeventeen' in [args['pagesize'],self.page_drawer.last_kwargs['pagesize']]
                   )
                  )
             )
            ):
            # If our mode has changed...
            changed = True
            if args['mode'][0]=='index_cards':
                option_table.set_option(self.OPT_FS,8)
                for o in [self.OPT_LM,self.OPT_RM,self.OPT_BM,self.OPT_TM]:
                    option_table.set_option(o,0.35)
                if (args['mode'][1][0] <= 5.2*inch) ^ (args['pagesize']=='elevenSeventeen'):
                    option_table.set_option(self.OPT_PO,_('Landscape'))
                else:
                    option_table.set_option(self.OPT_PO,_('Portrait'))
            else:
                # Otherwise it's columns...
                option_table.set_option(self.OPT_FS,10)
                for o in [self.OPT_LM,self.OPT_RM,self.OPT_BM,self.OPT_TM]:
                    option_table.set_option(o,1)
        if changed:
            option_table.apply()
            args = self.get_args_from_opts(self.opts)
        #backup_args = page_drawer.last_kwargs
        self.page_drawer.set_page(**args)
        self.page_drawer.queue_draw()
        self.in_ccb = False

class PdfPrefTable (PdfPrefGetter):

    # Like the dialog, but without the window -- lets it be embedded
    # in a print preferences widget.

    def setup_widgets (self):
        self.widg = Gtk.HBox()
        self.table = optionTable.OptionTable(options=self.opts,
                                             option_label=None,
                                             value_label=None,
                                             changedcb=None)
        self.widg.pack_start(self.table, True, True, 0)
        self.widg.pack_start(self.page_drawer,fill=True,expand=True)
        self.widg.show_all()

def get_pdf_prefs (defaults=None):
    if defaults: print('WARNING: ignoring provided defaults and using prefs system instead')
    pdf_pref_getter = PdfPrefGetter()
    return pdf_pref_getter.run()

if __name__ == '__main__':
    w = Gtk.Window()
    cuo = CustomUnitOption(44)
    cuo2 = CustomUnitOption(98)
    cuo.sync_to_other_cuo(cuo2)
    cuo2.sync_to_other_cuo(cuo)
    vb = Gtk.VBox()
    l = Gtk.Label(label='Hello World')
    vb.add(l)
    vb.pack_start(cuo, True, True, 0)
    vb.pack_start(cuo2, True, True, 0)
    w.add(vb)
    vb.show(); cuo.show(); cuo2.show()
    w.show()
    w.connect('delete_event',Gtk.main_quit)
    Gtk.main()
    raise Exception("Hell")

    from tempfile import tempdir
    import os.path
    #opts = get_pdf_prefs(); print opts
    test_3_x_5()

    #star_file = open(os.path.join(tempdir,'star.pdf'),'wb')
    #sw = PdfWriter()
    #sw.setup_document(star_file,mode='two_column')
    #for n in range(6,72,2):
    #    sw.write_paragraph("This is some text with a %s pt star"%n)
    #    sw.txt.append(FiveStars(n,filled=3.5))
    #
    #sw.close()
    #star_file.close()
    #import gnome
    #gnome.program_init('1.0','Gourmet PDF Exporter Test')
    #raise Exception("I don')t want to go any further")

    if os.name == 'nt':
        base = 'C:\\grm\grm'
    else:
        base = '/home/tom/Projects/grm'

    #import gourmet.recipeManager as rm
    #rd = rm.RecipeManager(file=os.path.join(base,'src','tests','reference_setup','recipes.db'))
    #rd = rm.RecipeManager()
    #ofi = open(os.path.join(tempdir,'test_rec.pdf'),'w')
    #rr = []
    #for n,rec in enumerate(rd.fetch_all(rd.recipe_table,deleted=False)):
    #    if rec.image:
    #        rr.append(rec)
    #pe = PdfExporterMultiDoc(rd,rd.fetch_all(rd.recipe_table),os.path.join(tempdir,'fooby.pdf'))
    #pe = PdfExporterMultiDoc(rd,rd.fetch_all(rd.recipe_table,deleted=False)[:10],os.path.join(tempdir,'fooby.pdf'))
    #pe = PdfExporterMultiDoc(rd,rr,os.path.join(tempdir,'fooby.pdf'))
    #pe.run()

    def test_formatting ():
        sw = PdfWriter()
        with open(os.path.join(tempdir,'format.pdf'),'wb') as f:
            sw.setup_document(f)
            sw.write_header('This is a header & isn\'t it nifty')
            sw.write_paragraph('<i>This</i> is a <b>paragraph</b> with <u>formatting</u>!')
            sw.write_header('<u>This is a formatted header &amp; it is also nifty &amp; cool</u>')
            sw.write_paragraph('<i>This is another formatted paragraph</i>')
            sw.write_paragraph('<span fg="\#f00">This is color</span>')
            sw.close()
        return os.path.join(tempdir,'format.pdf')

    def test_3_x_5 ():
        print('Test 3x5 layout')
        sw = PdfWriter()
        with open(os.path.join(tempdir,'foo.pdf'), 'wb') as f:
            sw.setup_document(f,
                              mode=('index_cards',(5*inch,3.5*inch)),
                              #pagesize=(5*inch,3.5*inch),
                              pagesize='letter',
                              pagemode='landscape',
                              left_margin=0.25*inch,right_margin=0.25*inch,
                              top_margin=0.25*inch,bottom_margin=0.25*inch,
                              base_font_size=8,
                              )
            #sw.write_header('Heading')
            #sw.write_subheader('This is a subheading')
            for n in range(5):
                sw.write_header(
                    "This is a header"
                    )
                #sw.write_subheader(
                #    u"This is a subheader"
                #    )
                sw.write_paragraph(
                    "%s: These are some sentences.  Hopefully some of these will be quite long sentences.  Some of this text includes unicode -- 45\u00b0F, for example... \u00bfHow's that?"%n*10
                    )
            #sw.write_paragraph('This is a <i>paragraph</i> with <b>some</b> <u>markup</u>.')
            #sw.write_paragraph(u"This is some text with unicode - 45\u00b0, \u00bfHow's that?".encode('iso-8859-1'))
            #sw.write_paragraph(u"This is some text with a unicode object - 45\u00b0, \u00bfHow's that?")
            sw.close()
        return os.path.join(tempdir,'foo.pdf')

    def test_grm_export (pdf_args=DEFAULT_PDF_ARGS):
        fname = tempfile.mktemp('.pdf')
        #if os.name == 'nt':
        #    base = 'C:\\grm\grm'
        #else:
        #    base = '/home/tom/Projects/grm'
        import gourmet.recipeManager as rm
        rd = rm.get_recipe_manager(file=os.path.join(base,'src','tests','reference_setup','recipes.db'))
        #rd = rm.RecipeManager()
        rr = []
        #for n,rec in enumerate(rd.fetch_all(rd.recipe_table,deleted=False)):
        #    if rec.image:
        #        rr.append(rec)
        pe = PdfExporterMultiDoc(rd,rd.fetch_all(rd.recipe_table,deleted=False),fname,pdf_args=pdf_args)
        pe.run()
        return fname

    #try:
    #    import gnome
    #    gnome.program_init('1.0','Gourmet PDF Exporter Test')
    #except ImportError:
    #    print 'We must be on windows...'

    #print 'TEST 3x5'
    webbrowser.open('file://'+test_3_x_5())
    webbrowser.open('file://'+test_formatting())
    #print 'END TEST'
    #print 'TEST GRM'
    webbrowser.open('file://'+test_grm_export())
    #print 'TEST CUSTOM GRM'
    #ppg = PdfPrefGetter()
    #print ppg.run()
    #print 'END TEST'

