import gourmet.exporters.exporter as exporter
import sys, xml.sax.saxutils, base64
from gourmet.exporters.xml_exporter import XmlExporter
from PIL import Image
import os
import tempfile
import zipfile
import gourmet.ImageExtras
import shutil
import unicodedata

class rec_to_mcb (XmlExporter):

    doc_element = 'cookbook'
    doctype_desc = ''
    dtd_path = ''
    ALLOW_PLUGINS_TO_WRITE_NEW_FIELDS = True
    tempimagedirpath=''
    current_title = ''
    
    def write_head (self):
        self.rec_el = self.create_element_with_attrs("recipe",{'id':self.r.id})
        self.top_element.appendChild(self.rec_el)
        
    def write_attr (self, attr, text):
        #attr mapping
        if (attr == 'link'):
            attr = 'url'
        if (attr == 'category'):
            attr = 'category'
        if (attr == 'servings'):
            attr = 'serving'
        if (attr == 'cooktime'):
            attr = 'cooktime'
        if (attr == 'preptime'):
            attr = 'preptime'
        if (attr == 'yields'):
            attr = 'quantity'
        if (attr == 'rating'):
            attr = 'rating'
        if (attr == 'title'):
            self.current_title = text.replace(' ','_')

        self.rec_el.appendChild(self.create_text_element(attr.replace(' ',''),text))
        
    def write_text (self, attr, text):
        #attr mapping with li
        if (attr == 'instructions'):
            attr = 'recipetext'
        if (attr == 'modifications'):
            attr = 'comments'
        
        if (attr == 'recipetext' or attr == 'comments'):
			linelist = text.split('\n')
			self.attrlist_el = self.xmlDoc.createElement(attr.replace(' ',''))
			self.rec_el.appendChild(self.attrlist_el)
			for l in linelist:
				attr_el = self.create_text_element('li',l)
				self.attrlist_el.appendChild(attr_el)
            

    def write_image (self, image):
        # write image file to the temp directory
        imageFilename = unicodedata.normalize('NFKD', unicode(self.current_title + '.png')).encode('ascii', 'ignore')
        pic_fullpath = os.path.join(tempfile.gettempdir(),'images',imageFilename)
        result = gourmet.ImageExtras.get_image_from_string(image)
        result.save(pic_fullpath)
        
        # write imagepath in the xml
        self.rec_el.appendChild(self.create_text_element('imagepath','images/' + imageFilename))
    
    def handle_italic (self, chunk): return chunk
    def handle_bold (self, chunk): return chunk    
    def handle_underline (self, chunk): return chunk    
        
    def write_foot (self):
        if self.i_created_this_document:
            self.xmlDoc.writexml(self.ofi, newl = '\n', addindent = "\t", 
                                 encoding = "UTF-8")

    def write_inghead (self):
        self.inglist_el = self.xmlDoc.createElement('ingredient')
        self.top_inglist = self.inglist_el # because groups will let us nest...
        self.rec_el.appendChild(self.inglist_el)

    def write_ingref (self, amount=1, unit=None, item=None, refid=None, optional=False):
        pass
        
    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        ing_txt=''
        if type(amount)==type(1.0) or type(amount)==type(1):
            amount = convert.float_to_frac(amount)
        ing_txt = ing_txt + amount
        if unit:
            ing_txt = ing_txt + ' ' + unit
        if item:
            ing_txt = ing_txt + ' ' + item
        
        ing_el = self.create_text_element('li',ing_txt)
        self.inglist_el.appendChild(ing_el)
        
    def write_grouphead (self, name):
        write_ing(item=name)
        
    def write_groupfoot (self):
        pass
    

class recipe_table_to_xml (exporter.ExporterMultirec, XmlExporter):
    doc_element = 'cookbook'
    doctype_desc = ''
    dtd_path = ''
    dirname = ''
    
    def __init__ (self, rd, recipe_table, out, one_file=True, change_units=False,
                  mult=1):
                      
        self.out=out
        
        #prepare temp directory for images
        dirname = tempfile.mkdtemp()
        tempfile.tempdir = dirname
        picdirname = os.path.join(dirname,'images')
        if os.path.isdir(picdirname):
            shutil.rmtree(picdirname)
        os.mkdir(picdirname, 0777 );
                      
        self.create_xmldoc()
        exporter.ExporterMultirec.__init__(
            self, rd, recipe_table, out, one_file=True, ext='mcb', exporter=rec_to_mcb,
            exporter_kwargs={'change_units':change_units,
                             'mult':mult,
                             'xmlDoc':self.xmlDoc,
                             'attr_order':('title',
                                           'category','cuisine',
                                           'source','link',
                                           'rating',
                                           'preptime','cooktime',
                                           'yields',
                                           ),
                             'order':['attr','image','ings','text'],
                             }
            )
        

    def write_footer (self, *args):
        self.xmlDoc.writexml(self.ofi, newl = '\n', addindent = "\t", encoding = "UTF-8")
        # flush to the disk
        self.ofi.close()
        
        # rename generated mcb file as xml file
        xmlpath = self.out[:-3]+'xml'
        os.rename(self.out,xmlpath)
        
        # add xml and images to the zip (mcb)
        file = zipfile.ZipFile(self.out, "w")
        file.write(xmlpath, os.path.basename(xmlpath), zipfile.ZIP_DEFLATED)
        picdirname = os.path.join(tempfile.gettempdir(),'images')
        for images in os.listdir(picdirname):
    		full_image_path = os.path.join(picdirname, images)
    		if os.path.isfile(full_image_path):
    			file.write(full_image_path, os.path.join('images',os.path.basename(full_image_path)), zipfile.ZIP_DEFLATED)
    			
    	# close and cleanup tempdir
        file.close()
        shutil.rmtree(tempfile.gettempdir())
        
        
        
def quoteattr (str):
    return xml.sax.saxutils.quoteattr(xml.sax.saxutils.escape(str))
