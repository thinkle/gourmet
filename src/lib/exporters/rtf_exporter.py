import exporter, PyRTF
from gourmet import convert
from gdebug import *

class rtf_exporter_multidoc (exporter.ExporterMultirec):
    def __init__ (self, rd, rview, out, conv=None, ext='rtm', progress_func=None):
        debug('rtf_exporter_multidoc starting!',5)
        self.doc = PyRTF.Document()
        exporter.ExporterMultirec.__init__(self, rd, rview, out,
                                  one_file=True, ext=ext,
                                  progress_func=progress_func,
                                  exporter=rtf_exporter,
                                  exporter_kwargs={'doc':self.doc,
                                                   'multidoc':True})        
        debug('rtf_exporter_multidoc done!',5)

    def write_footer (self):
        renderer = PyRTF.Renderer()
        renderer.Write(self.doc,self.ofi)
        
class rtf_exporter (exporter.exporter):
    def __init__ (self, rd, r, out,
                  conv=convert.converter(),
                  imgcount=1,
                  order=['attr','text','ings'],doc=None, multidoc=False, ss=None):
        if doc: self.doc=doc        
        else: self.doc = PyRTF.Document()
        self.multidoc=multidoc        
        if ss: self.ss=ss
        else: self.ss = self.doc.StyleSheet
        if not hasattr(self.ss.ParagraphStyles, 'Heading3'):
            ps = PyRTF.ParagraphStyle('Heading 3',
                                      PyRTF.TextStyle(PyRTF.TextPropertySet(self.ss.Fonts.Arial, 22)),
                                      PyRTF.ParagraphPropertySet( space_before=240,
                                                                  space_after = 60),
                                      )
            self.ss.ParagraphStyles.append( ps )
        exporter.exporter.__init__(self, rd, r, out,conv,imgcount,order)

    def write_head (self):
        self.recsection = PyRTF.Section()
        self.doc.Sections.append( self.recsection )
        
    def write_foot (self):
        if self.multidoc:
            pp = PyRTF.ParagraphPS()
            pp.SetPageBreakBefore( True )
            self.add_paragraph(" ", pp)
        else:
            renderer = PyRTF.Renderer()
            renderer.Write(self.doc,self.out)
    
    def write_attr_head (self):
        pass

    def write_attr (self, label, text):
        if label=='Title':
            self.add_paragraph(text,style=self.ss.ParagraphStyles.Heading1)
        else:
            self.add_paragraph("%s: %s"%(label,text))

        
    def write_attr_foot (self):
        self.add_paragraph(" ")

    def write_text (self, label, text):
        if not text: return
        self.add_paragraph(label, style=self.ss.ParagraphStyles.Heading2)
        pars=text.split("\n")
        for p in pars:
            self.add_paragraph(p)

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
        if optional=='yes': txt += "(optional) "
        txt = txt[0:-1] #strip trailing space
        self.add_paragraph(txt)

    def write_image (self, image):
        # NOTE TO SELF: GRAMPS HAS NICE RTF SUPPORT
        # WITH IMAGE EXPORT IF YOU WANT TO COPY IT
        # EVENTUALLY, BUT YOU MAY HAVE TO STOP USING
        # PYRTF ALTOGETHER.
        pass
    
    def add_paragraph (self, text, style=None):
        args = []
        if style: args.append(style)
        else: args.append(self.ss.ParagraphStyles.Normal)
        p=PyRTF.Paragraph(*args)
        p.append(text)
        self.recsection.append(p)

    
