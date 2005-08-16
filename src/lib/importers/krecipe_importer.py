import xml.sax, re, sys, xml.sax.saxutils
import base64
import xml_importer
from gourmet.gdebug import *
from gourmet.gglobals import *

class KrecHandler (xml_importer.RecHandler):
    ADD = 1
    IS = 2
    AND = 3
    BASE_64 = 4
    RECTAGS={'title':('title',IS),
             'author':('source',ADD),
             # FIX ME: IMAGE SUPPORT IS BROKEN!
             'pic':('image',BASE_64),
             'cat':('category',ADD),
             'serving':('servings',IS),
             'preparation-time':('preptime',IS),
             'krecipes-instructions':('instructions',ADD)
             }
    INGTAGS={'name':(('item','key'),AND),
             'amount':('amount',IS),
             'unit':('unit',IS),
             'prep':('item',ADD),
             }
    RECIPE_TAG = 'krecipes-recipe'
    ING_TAG = 'ingredient'
    
    def __init__ (self, recData, total=None, prog=None,conv=None):
        self.in_mixed = 0
        self.rec={}
        self.ing={}
        xml_importer.RecHandler.__init__(self,recData,total,prog,conv=conv)

    def startElement (self, name, attrs):
        self.elbuf = ""
        if name==self.RECIPE_TAG:
            self.start_rec()
        if name==self.ING_TAG:
            self.start_ing()
        if name=='ingredient-group':
            self.group=attrs.get('name','')
            
    def endElement (self, name):
        key,method=None,None
        # krecipe-recipe marks a recipe end!
        if name==self.RECIPE_TAG:
            self.commit_rec()
            return
        if name=='ingredient-group':
            self.group=None
        if name==self.ING_TAG:
            self.commit_ing()
        elif self.RECTAGS.has_key(name):
            obj = self.rec
            key,method = self.RECTAGS[name]
        elif self.INGTAGS.has_key(name):
            obj = self.ing
            key,method = self.INGTAGS[name]
        if key:
            if method == self.ADD and obj.has_key(key):
                obj[key]=obj[key]+", "+self.elbuf
            elif method == self.AND:
                for k in key:
                    obj[k]=self.elbuf
            elif method == self.BASE_64:
                obj[key]=base64.b64decode(self.elbuf)
            else:
                obj[key]=self.elbuf

    
class converter (xml_importer.converter):
    def __init__ (self, filename, rd, threaded=False, progress=None,conv=None):
        xml_importer.converter.__init__(self,filename,rd,KrecHandler,
                              recMarker="</krecipe-recipe>",threaded=threaded,
                              progress=progress,conv=conv)
        
