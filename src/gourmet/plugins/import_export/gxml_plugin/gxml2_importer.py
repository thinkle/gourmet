import base64
import re
import sys
import xml.sax
import xml.sax.saxutils

from gourmet.convert import NUMBER_FINDER
from gourmet.gglobals import REC_ATTRS, TEXT_ATTR_DIC
from gourmet.importers import xml_importer


class RecHandler (xml_importer.RecHandler):
    ING_ATTRS =  {
        # XML : DATABASE COLUMN
        "item":"item",
        "unit":"unit",
        "amount":"amount",
        "key":"ingkey",
        }

    def __init__ (self, total=None, conv=None, parent_thread=None):
        xml_importer.RecHandler.__init__(self,total,conv=conv, parent_thread=parent_thread)
        self.REC_ATTRS = [r[0] for r in REC_ATTRS]
        self.REC_ATTRS += [r for r in list(TEXT_ATTR_DIC.keys())]

    def startElement(self, name, attrs):
        self.elbuf = ""
        if name=='recipe':
            id=attrs.get('id',None)
            if id:
                self.start_rec(dict={'id':id})
            else:
                self.start_rec()

        if name=='ingredient':
            self.start_ing(recipe_id=self.rec['id'])
            if attrs.get('optional',False):
                if attrs.get('optional',False) not in ['no','No','False','false','None']:
                    self.ing['optional']=True
        if name=='ingref':
            self.start_ing(id=self.rec['id'])
            self.add_ref(unquoteattr(attrs.get('refid')))
            self.add_amt(unquoteattr(attrs.get('amount')))

    def endElement (self, name):
        if name=='recipe':
            self.commit_rec()
        elif name=='groupname':
            self.group=xml.sax.saxutils.unescape(self.elbuf.strip())
        elif name=='inggroup':
            self.group=None
        elif name=='ingref':
            self.add_item(xml.sax.saxutils.unescape(self.elbuf.strip()))
            self.commit_ing()
        elif name=='ingredient':
            self.commit_ing()
        elif name=='image':
            self.rec['image']=base64.b64decode(self.elbuf.strip())
        elif name=='yields':
            txt = xml.sax.saxutils.unescape(self.elbuf.strip())
            match = NUMBER_FINDER.search(txt)
            if match:
                number = txt[match.start():match.end()]
                unit = txt[match.end():].strip()
                self.rec['yields'] = number
                self.rec['yield_unit'] = unit
            else:
                self.rec['yields'] = 1
                self.rec['yield_unit'] = unit
                print('Warning, recorded',txt,'as 1 ',unit)
        elif name in self.REC_ATTRS:
            self.rec[str(name)]=xml.sax.saxutils.unescape(self.elbuf.strip())
        elif name in list(self.ING_ATTRS.keys()):
            self.ing[str(self.ING_ATTRS[name])]=xml.sax.saxutils.unescape(self.elbuf.strip())


class Converter (xml_importer.Converter):

    def __init__ (self, filename, conv=None):
        xml_importer.Converter.__init__(self,filename,RecHandler,
                                        recMarker="</recipe>",
                                        conv=conv,
                                        name='GXML2 Importer')


def unquoteattr (str):
    return xml.sax.saxutils.unescape(str).replace("_"," ")
