import metakit, xml.sax, re, sys, xml.sax.saxutils
import importer, exporter, rmetakit
from gdebug import *
from gglobals import *



class RecHandler (xml.sax.ContentHandler, importer.importer):
    def __init__ (self, recData):
        xml.sax.ContentHandler.__init__(self)
        importer.importer.__init__(self,rd=recData)
        self.meta={}
        self.meta['cuisine']={}
        self.meta['source']={}        
        self.meta['category']={}
        #self.start_rec()
    
    def startElement(self, name, attrs):
        gt.gtk_update()
        self.elbuf = ""
        self.in_mixed=0
        if name=='category' or name=='cuisine' or name=='source':
            self.metaid=unquoteattr(attrs.get('id',""))
        if name=='recipe':
            self.start_rec()            
            for att in ['date','audience','cuisine','servings',
                        'rating','description','category','source']:
                self.rec[att]=unquoteattr(attrs.get(att,""))
            for att in ['cuisine','source','category']:
                raw = unquoteattr(attrs.get(att,''))
#                print "DEBUG:",att,raw
                if raw:
                    if self.meta[att].has_key(raw):
                        self.rec[att]=self.meta[att][raw]
                    else:
                        self.rec[att]=raw
                        print "Warning: can't translate ",raw
        if name=='inggroup':
            self.group=unquoteattr(attrs.get('name'))
        if name=='ingredient':
            self.start_ing(id=self.rec['id'])
            self.ing['optional']=attrs.get('optional','no')            
        if name=='ingref':
            self.start_ing(id=self.rec['id'])
            self.add_ref(unquoteattr(attrs.get('refid')))
            self.add_amt(unquoteattr(attrs.get('amount')))
        if name=='amount':
            for att in ['unit','norm']:
                self.ing[att]=unquoteattr(attrs.get(att,""))
        if name=='item':
            for att in ['ingkey','alternative']:
                self.ing[att]=unquoteattr(attrs.get(att,""))
        if self.in_mixed:
            self.mixed += "<%s" % name
            for (n,v) in attrs.items():
                self.mixed += " %s='%s'" % (n,v)
            self.mixed += ">"
        if name=='instructions' or name=='modifications':
#            print "Begin adding to mixed!"
            self.in_mixed = 1
            self.mixed = ""
            
    def characters (self, ch):
        self.elbuf += ch
            
    def endElement (self, name):
        if name=='category' or name=='cuisine' or name=='source':
            self.meta[name][self.metaid]=xml.sax.saxutils.unescape(self.elbuf)
        if name=='title':
            self.rec['title']=xml.sax.saxutils.unescape(self.elbuf)
        if name=='recipe':
            #self.rd.add_rec(self.rec)
            self.commit_rec()

        if name=='inggroup':
            self.group=None
        if name=='ingref':
            self.add_item(xml.sax.saxutils.unescape(self.elbuf))
            self.commit_ing()
        if name=='ingredient':
            self.commit_ing()
        if name=='item':
            self.add_item(xml.sax.saxutils.unescape(self.elbuf))
        if name=='amount':
            self.add_amt(self.elbuf)
        if name=='instructions' or name=='modifications':
            self.in_mixed = 0
            self.mixed += xml.sax.saxutils.unescape(self.elbuf)
#            print "%s: %s" %(name, self.mixed)
            self.rec[name]=xml.sax.saxutils.unescape(self.mixed)
        if self.in_mixed:
#            print "Adding to mixed..."
            self.mixed += xml.sax.saxutils.unescape(self.elbuf)
            self.mixed += "</%s>" % name

class converter:
    def __init__ (self, filename, rd=None, threaded=False):
        if rd:
            self.rh = RecHandler(recData=rd)
        else:
            self.rh = RecHandler()
        ## Note to self: change this nomenclature to self.rd -- it's confusing
        self.db = self.rh.rd
        ## first, we clear out the old recipes
        #self.db.delete_table(self.db.rview)
        #self.db.delete_table(self.db.iview)
        self.fn = filename
        self.threaded = threaded
        self.terminate = self.rh.terminate
        self.suspend = self.rh.suspend
        self.resume = self.rh.resume
        if not self.threaded: self.run()

    def run (self):
        self.parse = xml.sax.parse(self.fn, self.rh)


class rec_to_xml (exporter.exporter):
    def __init__ (self, rd, r, out,attdics={}):
        self.attdics = attdics
        exporter.exporter.__init__(self, rd,r,out)

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
        self.out.write("\n<%s>%s</%s>\n"%(NAME_TO_ATTR[label],xml.sax.saxutils.escape(text),NAME_TO_ATTR[label]))
        
    def write_foot (self):
        self.out.write("</recipe>\n")

    def write_inghead (self):
        self.out.write("\n<ingredient-list>\n")

    def write_ingfoot (self):
        self.out.write("\n</ingredient-list>")

    def write_ingref (self, amount=1, unit=None, item=None, refid=None, optional=False):
        self.out.write("<ingref refid=%s amount=%s>%s</ingref>\n"%(quoteattr(refid),
                                                                   quoteattr(amount.strip()),
                                                                   xml.sax.saxutils.escape(item))
                       )
        
    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        self.out.write("<ingredient")
        if optional=='yes': self.out.write(" optional='yes'>")
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
    

class rview_to_xml (exporter.ExporterMultirec):
    def __init__ (self, rd, rview, out, one_file=True, progress_func=None):
        self.rd=rd
        self.catDic = self.createDictionary('category')
        self.srcDic = self.createDictionary('source')
        self.cuiDic = self.createDictionary('cuisine')
        exporter.ExporterMultirec.__init__(
            self, rd, rview, out, one_file=True, ext='xml', exporter=rec_to_xml,
            exporter_kwargs={'attdics':{'cuisine':self.cuiDic,
                                        'category':self.catDic,
                                        'source':self.srcDic}
                             },
            progress_func=progress_func)

    def write_header (self):        
        self.ofi.write('<!DOCTYPE recipeDoc PUBLIC "-//GOURMET//GOURMET RECIPE MANAGER XML//EN" "%s/recipe.dtd">'%datad)
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
        for r in self.rd.rview:
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

def unquoteattr (str):
    return xml.sax.saxutils.unescape(str).replace("_"," ")

def quoteattr (str):
    return xml.sax.saxutils.quoteattr(xml.sax.saxutils.escape(str)).replace(" ","_")

if __name__ == '__main__':
    c = converter('/usr/share/emacs21/site-lisp/recipe/recipe/r-data.xml')
    for r in c.db.rview:
        print "---------\n",r.title,"(",r.id,")"
        print "---------\n",r.instructions,"\n--------"
        for i in c.db.iview.select(id=r.id):
            print i.unit, i.amount, i.item
    for m in c.db.metaview:
        print "%s\t%s\t%s" % (m.type, m.id, m.description)
    c.db.save()
