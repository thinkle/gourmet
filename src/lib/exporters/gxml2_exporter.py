import exporter
import sys, xml.sax.saxutils, base64
from gourmet.gdebug import *
from gourmet.gglobals import *

class rec_to_xml (exporter.exporter_mult):

    """A vastly simplified XML exporter. The previous XML format was
    written as a format designed for itself (its design predated
    gourmet). This one is really written as a simple way to save, load
    and exchange Gourmet recipes. As a result, the code is much
    simpler, and the format should be quicker to write and more
    convenient for exchanging single recipes."""
    
    def __init__ (self, rd, r, out,attdics={},change_units=False,mult=1):
        self.attdics = attdics
        exporter.exporter_mult.__init__(self, rd,r,out, use_ml=True,
                                        order=['attr','image','ings','text'],
                                        do_markup=True,
                                        change_units=change_units,
                                        mult=mult)

    def write_head (self):
        self.out.write("\n<recipe id='%s'>"%self.r.id)

    def write_attr (self, label, text):
        attr = NAME_TO_ATTR[label]
        self.out.write('\n<%s>%s</%s>'%(attr,
                                        xml.sax.saxutils.escape(text),
                                        attr,
                                        )
                       )
        
    def write_text (self, label, text):
        self.out.write("\n<%s>%s</%s>\n"%(label.lower(),text,label.lower()))

    def write_image (self, image):
        self.out.write('\n<image format="jpeg"><![CDATA[')
        self.out.write(base64.b64encode(image))
        self.out.write(']]></image>')
    
    def handle_italic (self, chunk): return '&lt;i&gt;'+chunk+'&lt;/i&gt;'
    def handle_bold (self, chunk): return '&lt;b&gt;'+chunk+'&lt;/b&gt;'    
    def handle_underline (self, chunk): return '&lt;u&gt;'+chunk+'&lt;/u&gt;'    
        
    def write_foot (self):
        self.out.write("</recipe>\n")

    def write_inghead (self):
        self.out.write("\n<ingredient-list>\n")

    def write_ingfoot (self):
        self.out.write("\n</ingredient-list>")

    def write_ingref (self, amount=1, unit=None, item=None, refid=None, optional=False):
        self.out.write("<ingref %srefid=%s amount=%s>%s</ingref>\n"%(
            (optional and " optional='yes' " or ""),
            quoteattr(str(refid)),
            quoteattr(amount.strip()),
            xml.sax.saxutils.escape(item))
                       )
        
    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        self.out.write("<ingredient")
        if optional: self.out.write(" optional='yes'>")
        else: self.out.write(">")
        if amount:
            self.out.write("<amount>%s</amount>"%xml.sax.saxutils.escape(amount))
        if unit:
            self.out.write("<unit>%s</unit>"%xml.sax.saxutils.escape(unit))
        if item:
            self.out.write("<item>%s</item>"%xml.sax.saxutils.escape(item))
        if key:
            self.out.write("<key>%s</key>"%xml.sax.saxutils.escape(key))
        self.out.write("</ingredient>\n")

    def write_grouphead (self, name):
        self.out.write('<inggroup><groupname>%s</groupname>\n'%xml.sax.saxutils.escape(name))
        
    def write_groupfoot (self):
        self.out.write('</inggroup>\n')
    

class rview_to_xml (exporter.ExporterMultirec):
    def __init__ (self, rd, rview, out, one_file=True, progress_func=None, change_units=False,
                  mult=1):
        self.rd=rd
        exporter.ExporterMultirec.__init__(
            self, rd, rview, out, one_file=True, ext='xml', exporter=rec_to_xml,
            progress_func=progress_func,
            exporter_kwargs={'change_units':change_units,
                             'mult':mult,
                             }
            )
        
    def write_header (self):        
        self.ofi.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
        self.ofi.write("<gourmetDoc>\n")
        
    def write_footer (self):
        self.ofi.write("</gourmetDoc>\n")        

def quoteattr (str):
    return xml.sax.saxutils.quoteattr(xml.sax.saxutils.escape(str))
