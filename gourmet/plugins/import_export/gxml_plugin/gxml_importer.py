import xml.sax, re, sys, xml.sax.saxutils
from gourmet.importers import xml_importer
from gourmet.gdebug import *
from gourmet.gglobals import *
import base64
from gettext import gettext as _

unquoteattr = xml_importer.unquoteattr

class RecHandler (xml_importer.RecHandler):
    def __init__ (self, total=None, conv=None, parent_thread=None):
        xml_importer.RecHandler.__init__(self,total,conv=conv,parent_thread=parent_thread)
        self.meta={}
        self.in_mixed = 0
        self.meta['cuisine']={}
        self.meta['source']={}
        self.meta['category']={}
        #self.start_rec()
        
    def startElement(self, name, attrs):
        self.elbuf = ""        
        if name=='category' or name=='cuisine' or name=='source':
            self.in_mixed=0
            self.metaid=unquoteattr(attrs.get('id',""))
        if name=='recipe':
            self.in_mixed=0
            self.start_rec()
            for att in ['cuisine','servings',
                        'rating','description','category','source']:
                self.rec[att]=unquoteattr(attrs.get(att,""))
            for att in ['cuisine','source','category']:
                raw = unquoteattr(attrs.get(att,''))
                if raw:
                    if self.meta[att].has_key(raw):
                        self.rec[att]=self.meta[att][raw]
                    else:
                        self.rec[att]=raw
                        print "Warning: can't translate ",raw
        if name=='image':
            self.in_mixed=0            
        if name=='inggroup':
            self.in_mixed=0
            self.group=unquoteattr(attrs.get('name'))
        if name=='ingredient':
            self.in_mixed=0
            self.start_ing(id=self.rec['id'])
            if attrs.get('optional',False):
                if attrs.get('optional',False) not in ['no','false','False','No','None']: #support for obsolete values
                    self.ing['optional']=True
        if name=='ingref':
            self.in_mixed=0
            self.start_ing(id=self.rec['id'])
            self.add_ref(unquoteattr(attrs.get('refid')))
            self.add_amt(unquoteattr(attrs.get('amount')))
        if name=='amount':
            self.in_mixed=0
            for att in ['unit']:
                self.ing[att]=unquoteattr(attrs.get(att,""))
        if name=='item':
            self.in_mixed=0
            for att in ['ingkey']:
                self.ing[att]=unquoteattr(attrs.get(att,""))
        if self.in_mixed:
            self.mixed += "<%s" % name
            for (n,v) in attrs.items():
                self.mixed += " %s='%s'" % (n,v)
            self.mixed += ">"
        if name=='instructions' or name=='modifications':
            self.in_mixed = 1
            self.mixed = ""
            
    def endElement (self, name):
        if name=='category' or name=='cuisine' or name=='source':
            self.meta[name][self.metaid]=xml.sax.saxutils.unescape(self.elbuf)
        if name=='title':
            self.rec['title']=xml.sax.saxutils.unescape(self.elbuf)
        if name=='image':
            self.rec['image']=base64.b64decode(self.elbuf)
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
            self.mixed += self.elbuf
            # special unescaping of our grand little tags
            for (eop,op,ecl,cl) in [('&lt;%s&gt;'%t,'<%s>'%t,'&lt;/%s&gt;'%t,'</%s>'%t)
                                    for t in 'b','i','u']:
                self.mixed=self.mixed.replace(eop,op)
                self.mixed=self.mixed.replace(ecl,cl)
            self.rec[name]=self.mixed
        if self.in_mixed:
            self.mixed += self.elbuf
            self.mixed += "</%s>" % name

class Converter (xml_importer.Converter):
    def __init__ (self, filename, conv=None):
        xml_importer.Converter.__init__(self,filename,RecHandler,
                                        recMarker="</recipe>",
                                        conv=conv,
                                        name='GXML Importer')

def unquoteattr (str):
    return xml.sax.saxutils.unescape(str).replace("_"," ")
