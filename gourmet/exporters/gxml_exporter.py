import exporter
import sys, xml.sax.saxutils
from gourmet.gdebug import debug
from gourmet.gglobals import NAME_TO_ATTR
import base64

class rec_to_xml (exporter.exporter):
    def __init__ (self, rd, r, out,attdics={}):
        self.attdics = attdics
        exporter.exporter.__init__(self, rd,r,out, use_ml=True,
                                   order=['attr','text','ings'],
                                   do_markup=True)

    def write_head (self):
        self.out.write("\n<recipe")

    def write_attr (self, label, text):
        if NAME_TO_ATTR[label]=="title":
            # title is not an xml attribute... we'll handle it later
            self.my_title=xml.sax.saxutils.escape(text)
        else:
            name = NAME_TO_ATTR[label]
            if self.attdics.has_key(name):
                text = self.attdics[name][text]
            self.out.write("\n %s=%s"%(name, quoteattr(text)))

    def write_attr_foot (self):
        self.out.write(">\n")
        # now we handle the title...
        if self.my_title:
            self.out.write("\n<title>%s</title>"%self.my_title)

    def write_text (self, label, text):
        self.out.write("\n<%s>%s</%s>\n"%(NAME_TO_ATTR[label],text,NAME_TO_ATTR[label]))

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
            (optional and " optional='yes'>" or ""),
            quoteattr(str(refid)),
            quoteattr(amount.strip()),
            xml.sax.saxutils.escape(item))
                       )

    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        self.out.write("<ingredient")
        if optional: self.out.write(" optional='yes'>")
        else: self.out.write(">")
        if amount:
            self.out.write("<amount")
            if unit:
                self.out.write(" unit=%s"%quoteattr(unit))
            self.out.write(">%s</amount>"%xml.sax.saxutils.escape("%s"%amount).strip())
        self.out.write("<item key=%s>%s</item>"%(quoteattr(key),xml.sax.saxutils.escape(item)))
        self.out.write("</ingredient>\n")

    def write_grouphead (self, name):
        self.out.write('<inggroup name=%s>\n'%quoteattr(name))

    def write_groupfoot (self):
        self.out.write('</inggroup>\n')

    def write_image (self, image):
        self.out.write('<image format="jpeg"><![CDATA[')
        self.out.write(base64.b64encode(image))
        self.out.write(']]></image>')

class recipe_table_to_xml (exporter.ExporterMultirec):
    def __init__ (self, rd, recipe_table, out, one_file=True):
        self.rd=rd
        self.catDic = self.createDictionary('category')
        self.srcDic = self.createDictionary('source')
        self.cuiDic = self.createDictionary('cuisine')
        exporter.ExporterMultirec.__init__(
            self, rd, recipe_table, out, one_file=True, ext='xml', exporter=rec_to_xml,
            exporter_kwargs={'attdics':{'cuisine':self.cuiDic,
                                        'category':self.catDic,
                                        'source':self.srcDic,},
                             }
                                           )

    def write_header (self):
        #self.ofi.write('<!DOCTYPE recipeDoc PUBLIC "-//GOURMET//GOURMET RECIPE MANAGER XML//EN" "%s/recipe.dtd">'%datad)
        self.ofi.write("<recipeDoc>\n")
        self.ofi.write( "<recipeHead>\n")
        self.dic2decl("category",self.catDic,self.ofi)
        self.dic2decl("cuisine",self.cuiDic,self.ofi)
        self.dic2decl("source",self.srcDic,self.ofi)
        self.ofi.write( "</recipeHead>\n")
        self.ofi.write( "<recipe-list>\n")

    def write_footer (self):
        self.ofi.write("</recipe-list>\n")
        self.ofi.write("</recipeDoc>\n")

    def createDictionary(self,attr):
        dic = {}
        cnt = 1
        for r in self.rd.recipe_table:
            itm = getattr(r,attr)
            if not dic.has_key(itm):
                dic[itm]="%s%s"%(attr,cnt)
                cnt += 1
        return dic

    def dic2decl (self, name, dic, out=sys.stderr):
        out.write( "<%sDecl>\n"%name)
        for itm,key in dic.items():
            out.write( "<%s id=%s>%s</%s>\n"%(name,quoteattr(key),xml.sax.saxutils.escape(itm),name))
        out.write( "</%sDecl>\n"%name)

def quoteattr (str):
    return xml.sax.saxutils.quoteattr(xml.sax.saxutils.escape(str)).replace(" ","_")
