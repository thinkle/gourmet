import xml.sax, re, sys, xml.sax.saxutils
from gourmet.importers import xml_importer
from gourmet.gdebug import *
from gourmet.gglobals import *
from PIL import Image
import gourmet.ImageExtras
import re

class RecHandler (xml_importer.RecHandler):
    ADD = 1
    IS = 2
    #mapping: 'mcb tag':('gourmet tag',method import),
    RECTAGS={'title':('title',IS),
             'url':('link',ADD),
             'category':('category',ADD),
             'serving':('servings',IS),
             'cooktime':('cooktime',IS),
             'preptime':('preptime',IS),
             'quantity':('yields',IS),
             'rating':('rating',IS),
             'comments':('modifications',IS),
             
             }
    RECIPE_TAG = 'recipe'
    ING_TAG = 'ingredient'
    INSTR_TAG = 'recipetext'
    
    current_section = ''
    
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
            self.current_section = 'ingredient'
        if name==self.INSTR_TAG:
            self.current_section = 'instruction'
            
    def endElement (self, name):
        key,method=None,None
        if name==self.RECIPE_TAG:
            self.commit_rec()
            return
        if name=='li' and self.current_section=='ingredient':
            if not hasattr(self,'db'):
                import gourmet.backends.db as db
                self.db = db.get_database()
            ingdic = self.db.parse_ingredient(self.elbuf.strip())
            self.start_ing(**ingdic)
            self.commit_ing()
        if name=='li' and self.current_section=='instruction':
            key = 'instructions'
            method = self.ADD
            obj = self.rec
        if name == 'imagepath':
            obj = self.rec
            #get the temp directory and build the image path
            (dirname, filename) = os.path.split(self.parent_thread.fn)
            (pic_dirname, pic_filename) = os.path.split(self.elbuf.strip())
            pic_fullpath = os.path.join(dirname,'images',pic_filename)
            
            #try to import the image
            if os.path.isfile(pic_fullpath):
                try:
                    im = Image.open(pic_fullpath)
                    obj['image'] = gourmet.ImageExtras.get_string_from_image(im)
                except Exception, e:
                    print 'Issue loading: '+pic_fullpath
                    print str(e)
                    #dont stop if corrupted image file
                    pass
        
        # times fixing
        if name == 'cooktime' or name == 'preptime':
            self.elbuf = self.elbuf.replace('mn','min')
            if re.match('([0-9]*)min', self.elbuf):
                self.elbuf = self.elbuf.replace('min',' min')
        
        #other tags
        if name==self.ING_TAG:
            self.current_section == ''
        elif name==self.INSTR_TAG:
            self.current_section == ''
        elif self.RECTAGS.has_key(name):
            obj = self.rec
            key,method = self.RECTAGS[name]

        if key:
            if method == self.ADD and obj.has_key(key):
                obj[key]=obj[key]+"\n "+self.elbuf
            else:
                obj[key]=self.elbuf

class Converter (xml_importer.Converter):
    def __init__ (self, filename, conv=None):
        xml_importer.Converter.__init__(self,filename,RecHandler,
                                        recMarker="</recipe>",
                                        conv=conv,
                                        name='MCB Importer')

