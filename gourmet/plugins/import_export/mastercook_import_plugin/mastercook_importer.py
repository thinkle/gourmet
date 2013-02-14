#!/usr/bin/env python
import gourmet.importers.importer as importer
import xml.sax, re, os.path
from gourmet.gdebug import debug
from gourmet.importers.xml_importer import unquoteattr
import gourmet.importers.xml_importer as xml_importer
from gettext import gettext as _

class Mx2Cleaner:
    def __init__ (self):
        self.regs_to_toss = ["<\?xml[^?]+\?>","<!DOCTYPE[^>]+>"]
        self.toss_regexp = "("
        for r in self.regs_to_toss:
            self.toss_regexp = self.toss_regexp + r + "|"
        self.toss_regexp = self.toss_regexp[0:-1] + ")"
        self.toss_regexp = re.compile(self.toss_regexp)
        self.attr_regexp = '(<[^>]+?)\"([^=]+[\"<>][^=]+)\"'
        self.attr_regexp = re.compile(self.attr_regexp)
        self.encodings = ['cp1252','iso8859','ascii','latin_1','cp850','utf-8']
        
    def cleanup (self, infile, outfile):
        infile = open(infile,'r')
        outfile = open(outfile,'w')
        for l in infile.readlines():
            l = self.toss_regs(l)
            l = self.fix_attrs(l)
            l = self.encode(l)
            outfile.write(l)
        infile.close()
        outfile.close()
            
    def toss_regs (self, instr):
        m = self.toss_regexp.search(instr)
        if m:
            outstr = instr[0:m.start()] + instr[m.end():]
            debug('Converted "%s" to "%s"'%(instr,outstr),1)
            return outstr
        else:
            return instr

    def fix_attrs (self, instr):
        match = self.attr_regexp.search(instr)
        outstr = ""
        while match:
            outstr = outstr + instr[0:match.start()]
            pre,badattr = match.groups()
            outstr = outstr + pre
            outstr = outstr + xml.sax.saxutils.quoteattr(badattr)
            debug('Fixed broken attribute: %s -> %s'%(instr,outstr),0)
            instr = instr[match.end():]
            match = self.attr_regexp.search(instr)
        outstr = outstr + instr
        return outstr

    def encode (self, l):
        for e in self.encodings:
            try:
                return l.decode(e)
            except:
                debug('Could not decode as %s'%e,2)
                pass
        raise Exception("Could not encode %s" % l)
        
class MastercookXMLHandler (xml_importer.RecHandler):
    """We handle MasterCook XML Files"""
    def __init__ (self, parent_thread=None,conv=None):
        debug('MastercookXMLHandler starting',0)
        xml_importer.RecHandler.__init__(self,parent_thread=parent_thread,conv=None)
        self.total = 0
        self.recs_done = 0
        self.elements = {
            'mx2':['source','date'],
            #'Summ':[],
            'Nam':[],
            'RcpE':['name'],
            'RTxt':[],
            'Serv':['qty'],
            'PropT':['elapsed'],
            'IngR':['name','unit','qty'],
            'IPrp':[],
            #'DirS':[],
            'DirT':[],
            'Desc':[],
            'Srce':[],
            'Note':[],
            'CatT':[],
            'Yield':['unit','qty'],
            }
        self.current_elements = []
        self.bufs = []
        xml.sax.ContentHandler.__init__(self)
        importer.Importer.__init__(self,conv=conv)

    def grabattr (self, attrs, name, default=''):
        return unquoteattr(attrs.get(name,default))

    def startElement (self, name, attrs):
        self.in_mixed=0
        if not self.elements.has_key(name):
            debug('Unhandled element: %s'%name,0)
            return
        else:
            self.current_elements = [name] + self.current_elements
            handler = self._get_handler(name)
            handler(start=True,attrs=attrs)

    def endElement (self, name):
        if not self.elements.has_key(name):
            return
        else:
            self.current_elements.remove(name)
            handler = self._get_handler(name)
            handler(end=True)


    def endDocument (self):
        self.emit('progress',1,_("Mastercook import finished."))
    
    def _get_handler (self, name):
        return getattr(self,'%s_handler'%name)

    def mx2_handler (self, start=False, end=False, attrs=None):
        if start:
            pass

    def characters (self, ch):
        debug('adding to %s bufs: %s'%(len(self.bufs),ch),0)
        for buf in self.bufs:
            setattr(self,buf,getattr(self,buf)+ch)
        
    def Nam_handler (self, start=False, end=False, attrs=None):
        if start:
            # we simply count recipes so that we can
            # indicate progress.
            self.total += 1
    
    def RcpE_handler (self, start=False, end=False, attrs=None):
        if start:
            self.start_rec()
            #if self.source:
            #    self.rec['source']=self.source
            if attrs:
                self.rec['title']=self.grabattr(attrs,'name')
        if end:
            if self.rec.has_key('yield'):
                self._add_to_instructions("\nYield: %s %s"%self.rec['yield'])
                del self.rec['yield']
            self.commit_rec()
        
    def RTxt_handler (self, start=False, end=False, attrs=None):
        if start:
            self.cdata_buf = ""
            self.bufs.append('cdata_buf')
        if end:
            self.bufs.remove('cdata_buf')

    def Serv_handler (self, start=False, end=False, attrs=None):
        if attrs:
            self.rec['servings']=self.grabattr(attrs,'qty')

    def Yield_handler (self, start=False, end=False, attrs=None):
        if attrs:
            self.rec['yield']=(self.grabattr(attrs,'qty'),self.grabattr(attrs,'unit'))

    def CatT_handler (self, start=False, end=False, attrs=None):
        if start:
            self.catbuf = ""
            self.bufs.append('catbuf')
        if end:
            self.bufs.remove('catbuf')
            self.catbuf = self.catbuf.strip()
            if self.rec.has_key('category'):
                self.rec['category']=self.rec['category']+" "+self.catbuf
            else:
                self.rec['category']=xml.sax.saxutils.unescape(self.catbuf)

    def IngR_handler (self, start=False, end=False, attrs=None):
        if attrs:
            self.start_ing()
            self.item = self.grabattr(attrs,'name')
            self.add_amt(self.grabattr(attrs,'qty'))
            self.ing['unit']=self.grabattr(attrs,'unit')
            
        if end:
            if self.item.find("===")==0:
                self.group = self.item[4:-4]
            else:
                self.add_item(self.item)
                debug(
                    "item=%s, unit=%s"%(self.item,self.ing['unit']),
                    0
                    )
                self.commit_ing()

    def _add_to_instructions (self, buf):
        debug('adding to instructions: %s'%buf,0)
        if self.rec.has_key('instructions'):
            self.rec['instructions'] = self.rec['instructions'] + "\n%s"%xml.sax.saxutils.unescape(buf)
        else:
            self.rec['instructions'] = xml.sax.saxutils.unescape(buf)

    def DirT_handler (self, start=False, end=False, attrs=None):
        if start:
            self.dbuf = ""
            self.bufs.append('dbuf')
        if end:
            self.bufs.remove('dbuf')
            self._add_to_instructions(self.dbuf.strip())

    # this also gets added to instructions
    Desc_handler = DirT_handler

    def Note_handler (self, start=False, end=False, attrs=None):
        if start:
            self.dbuf = ""
            self.bufs.append('dbuf')
        if end:
            self.bufs.remove('dbuf')
            buf = xml.sax.saxutils.unescape(self.dbuf.strip())
            if self.rec.has_key('modifications'):
                self.rec['modifications'] = self.rec['modifications'] + "\n%s"%buf
            else:
                self.rec['modifications'] = buf

    def IPrp_handler (self, start=False, end=False, attrs=None):
        if start:
            self.ipbuf = ""
            self.bufs.append('ipbuf')
        if end:
            self.item += "; %s"%xml.sax.saxutils.unescape(self.ipbuf.strip())
            self.bufs.remove('ipbuf')
        
    def Srce_handler (self, start=False, end=False, attrs=None):
        if start:
            self.srcbuf = ""
            self.bufs.append('srcbuf')
        if end:
            self.rec['source']=self.srcbuf.strip()
            self.bufs.remove('srcbuf')
    
class MastercookImporter (xml_importer.Converter):
    def __init__ (self, filename):
        xml_importer.Converter.__init__(self,
                                        recHandler=MastercookXMLHandler,
                                        recMarker='<RcpE',
                                        filename=filename,
                                        )

    def pre_run (self):
        self.emit('progress',0.03, _("Tidying up XML"))
        cleaner = Mx2Cleaner()
        base,ext=os.path.splitext(self.fn)
        cleanfn = base + ".gourmetcleaned" + ext
        cleaner.cleanup(self.fn,cleanfn)
        debug('Cleaned up file saved to %s'%cleanfn,1)
        self.orig_fn = self.fn
        self.fn = cleanfn


