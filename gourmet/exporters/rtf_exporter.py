from gi.repository import Pango
import xml.sax.saxutils
import PyRTF, types
from . import exporter
from gourmet import convert
from gourmet.gdebug import debug
from gourmet.image_utils import write_image_tempfile
from gettext import gettext as _

class rtf_exporter_multidoc (exporter.ExporterMultirec):
    def __init__ (self, rd, recipe_table, out, conv=None):
        debug('rtf_exporter_multidoc starting!',5)
        self.doc = PyRTF.Document()
        exporter.ExporterMultirec.__init__(self,
                                           rd,
                                           recipe_table,
                                           out,
                                           one_file=True, ext='rtf',
                                           exporter=rtf_exporter,
                                           exporter_kwargs={'doc':self.doc,
                                                            'multidoc':True})
        debug('rtf_exporter_multidoc done!',5)

    def write_footer (self):
        renderer = PyRTF.Renderer()
        renderer.Write(self.doc,self.ofi)

class rtf_exporter (exporter.exporter_mult):
    def __init__ (self, rd, r, out,
                  conv=convert.Converter(),
                  imgcount=1,
                  mult=1,
                  change_units=False,
                  order=['image','attr','ings','text'],
                  doc=None,
                  multidoc=False,
                  ss=None):
        self.setup_document(doc,ss)
        self.multidoc=multidoc
        exporter.exporter_mult.__init__(self, rd, r, out,
                                        conv=conv,
                                        imgcount=imgcount,
                                        order=order,
                                        change_units=change_units,
                                        mult=mult,
                                        fractions=convert.FRACTIONS_NORMAL, #1/2 1/4 3/4 fractions
                                        do_markup=False #we'll handle this internally...
                                        )


    def setup_document (self, doc=None, ss=None):
        if doc: self.doc=doc
        else: self.doc = PyRTF.Document()
        if ss: self.ss=ss
        else: self.ss = self.doc.StyleSheet
        self.ss.ParagraphStyles.Normal.TextStyle.TextPropertySet.Font = self.ss.Fonts.TimesNewRoman
        self.ss.ParagraphStyles.Heading1.TextStyle.TextPropertySet.Bold = True
        if not hasattr(self.ss.ParagraphStyles, 'Heading3'):
            ps = PyRTF.ParagraphStyle('Heading 3',
                                      PyRTF.TextStyle(PyRTF.TextPropertySet(self.ss.Fonts.Arial, 22)),
                                      PyRTF.ParagraphPropertySet( space_before=240,
                                                                  space_after = 60),
                                      )
            self.ss.ParagraphStyles.append( ps )

    def write_head (self):
        self.recsection = PyRTF.Section(break_type=PyRTF.Section.PAGE)
        self.doc.Sections.append( self.recsection )
        self.add_paragraph("%s\n"%self.r.title,self.ss.ParagraphStyles.Heading1)

    def write_foot (self):
        if not self.multidoc:
            renderer = PyRTF.Renderer()
            renderer.Write(self.doc,self.out)

    def write_attr_head (self):
        #self.add_paragraph(" ")
        pass

    def write_attr (self, label, text):
        if label!=_('Title'):
            self.add_paragraph("\n%s: %s"%(label,text))

    def write_attr_foot (self):
        self.add_paragraph(" ")

    def write_text (self, label, text):
        if not text: return
        self.add_paragraph(label, style=self.ss.ParagraphStyles.Heading2)
        pars=text.split("\n")
        # since we may have to deal with markup, we're going to handle this
        # on our own...
        for par in pars:
            p = PyRTF.Paragraph(self.ss.ParagraphStyles.Normal)
            # this code is partly copied from handle_markup in
            # exporter.py (a bit dumb, I know...)
            try:
                al,txt,sep = Pango.parse_markup(par,'\x00')
            except:
                al,txt,sep = Pango.parse_markup(xml.sax.saxutils.escape(par),'\x00')
            ai = al.get_iterator()
            more = True
            while more:
                fd,lang,atts=ai.get_font()
                chunk=xml.sax.saxutils.escape(txt.__getslice__(*ai.range()))
                fields=fd.get_set_fields()
                style_args = {'font':self.ss.Fonts.TimesNewRoman}
                if fields != 0:
                    if 'style' in fields.value_nicks and fd.get_style()==Pango.Style.ITALIC:
                        style_args['italic']=True
                    if 'weight' in fields.value_nicks and fd.get_weight()==Pango.Weight.BOLD:
                        style_args['bold']=True
                if [att for att in atts if att.type==Pango.ATTR_UNDERLINE and att.value==Pango.Underline.SINGLE]:
                    style_args['underline']=True
                p.append(
                         PyRTF.Elements.TEXT(encode_text(chunk),
                                             **style_args)
                         )
                more = next(ai)
            self.recsection.append(p)

    def write_inghead (self):
        self.add_paragraph("Ingredients", style=self.ss.ParagraphStyles.Heading2)

    def write_grouphead (self, text):
        self.add_paragraph(text,style=self.ss.ParagraphStyles.Heading3)

    def write_ingref (self, amount=1, unit=None,
                      item=None, optional=False,
                      refid=None):
        ### DOES RTF SUPPORT LINKING? IF SO, WE SHOULD DO BETTER HERE...
        self.write_ing(amount,unit,item,None,optional)

    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        txt = ""
        for p in amount, unit, item:
            if p: txt += "%s "%p
        if optional: txt += "(optional) "
        txt = txt[0:-1] #strip trailing space
        self.add_paragraph(txt)

    def write_image (self, image):
        try:
            i=PyRTF.Image(write_image_tempfile(image))
            self.recsection.append(i)
            self.add_paragraph(" ")
        except AttributeError:
            # If PyRTF has no attribute Image, this is an old version
            # and we can't do anything with images.
            pass

    def add_paragraph (self, text, style=None):
        args = []
        if style: args.append(style)
        else: args.append(self.ss.ParagraphStyles.Normal)
        p=PyRTF.Paragraph(*args)
        p.append(encode_text(text))
        self.recsection.append(p)


def encode_text (txt):
    """Encode our text in codepage 1252."""
    #return txt
    try:
        return txt.encode('cp1252','strict')
    except:
        try:
            return txt.encode('cp1252','strict')
        except:
            return txt.encode('cp1252','replace')

if __name__ == '__main__':
    from .__init__ import Tester,RTF
    t = Tester()
    print('Exporting test to /tmp/test_recs.rtf')
    import sys
    t.run_export(**{'format':RTF,
                    'rv':t.rm.recipe_table[4:9],
                    'rec':t.rm.recipe_table[-1],
                    #'mode':'exporter',
                    'mode':'mult_exporter',
                    'file':'/tmp/test_recs.rtf',
                    'prog':lambda *args,**kwargs: sys.stderr.write("%s%s"%(args,kwargs)),
                    'out':open('/tmp/test_rec.rtf', 'wb'),
                    })

