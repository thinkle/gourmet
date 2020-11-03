import base64
import re
import sys
import xml.sax
import xml.sax.saxutils

from gourmet.importers import xml_importer


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
    INGTAGS={'name':(('item','ingkey'),AND),
             'amount':('amount',IS),
             'unit':('unit',IS),
             'prep':('item',ADD),
             }
    RECIPE_TAG = 'krecipes-recipe'
    ING_TAG = 'ingredient'

    def __init__ (self, total=None, conv=None, parent_thread=None):
        self.in_mixed = 0
        self.rec={}
        self.ing={}
        xml_importer.RecHandler.__init__(self,total,conv=conv,parent_thread=parent_thread)

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
        elif name in self.RECTAGS:
            obj = self.rec
            key,method = self.RECTAGS[name]
        elif name in self.INGTAGS:
            obj = self.ing
            key,method = self.INGTAGS[name]
        if key:
            if method == self.ADD and key in obj:
                obj[key]=obj[key]+", "+self.elbuf
            elif method == self.AND:
                for k in key:
                    obj[k]=self.elbuf
            elif method == self.BASE_64:
                obj[key]=base64.b64decode(self.elbuf)
            else:
                obj[key]=self.elbuf


class Converter (xml_importer.Converter):
    def __init__ (self, filename):
        xml_importer.Converter.__init__(self,filename,KrecHandler,
                              recMarker="</krecipe-recipe>"
                              )
