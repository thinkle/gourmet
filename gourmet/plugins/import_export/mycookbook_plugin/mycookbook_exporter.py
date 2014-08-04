import gourmet.exporters.exporter as exporter
import xml.sax.saxutils
from gourmet.exporters.xml_exporter import XmlExporter
import os
import tempfile
import zipfile
from gourmet import convert
import gourmet.ImageExtras
import shutil
import unicodedata

class rec_to_mcb (XmlExporter):

    doc_element = 'cookbook'
    doctype_desc = ''
    dtd_path = ''
    ALLOW_PLUGINS_TO_WRITE_NEW_FIELDS = True
    current_title = ''
    
    def write_head (self):
        self.rec_el = self.create_element_with_attrs("recipe",{'id':self.r.id})
        self.top_element.appendChild(self.rec_el)
        
    def write_attr (self, attr, item):
        #attr mapping
        if (attr == 'link'):
            attr = 'url'
        elif (attr == 'category'):
            attr = 'category'
        elif (attr == 'servings'):
            attr = 'quantity'
        elif (attr == 'cooktime'):
            attr = 'cooktime'
            item = unicode(item)
        elif (attr == 'preptime'):
            attr = 'preptime'
            item = unicode(item)
        elif (attr == 'yields'):
            attr = 'quantity'
            item = unicode(item)
        elif (attr == 'rating'):
            if item:
                # MyCookbook's rating range is integers from 1 to 5, while
                # ours is from 1 to 10, so we have to floor divide by 2 when
                # exporting.
                self.rec_el.appendChild(self.create_text_element('rating', str(item//2)))
                return
        elif (attr == 'title'):
            self.current_title = item.replace(' ','_')

        self.rec_el.appendChild(self.create_text_element(attr.replace(' ',''),item))
        
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

    def write_ingref (self, ingredient):
        pass
        
    def write_ing (self, ingredient):
        ing_txt = format(ingredient, "{'fractions': %s}"%self.fractions)
        if ing_txt:
            ing_el = self.create_text_element('li', ing_txt)
        else:
            ing_el = self.create_text_element('li', '')
        self.inglist_el.appendChild(ing_el)
        
    def write_grouphead (self, name):
        self.write_ing(item=name)
        
    def write_groupfoot (self):
        pass
    

class recipe_table_to_xml (exporter.ExporterMultirec, XmlExporter):
    doc_element = 'cookbook'
    doctype_desc = ''
    dtd_path = ''
    dirname = ''
    
    def __init__ (self, recipe_table, out, one_file=True, change_units=False):
        
        self.outputfilename = ''
        
        if type(out) is file:
            self.out=out
            self.outputfilename=str(out.name)
        else:
            self.outputfilename=out
            self.out=open(out,'w')
        
        #prepare temp directory for images
        self.ostempdir_bck = tempfile.tempdir
        dirname = tempfile.mkdtemp()
        tempfile.tempdir = dirname
        picdirname = os.path.join(dirname,'images')
        if os.path.isdir(picdirname):
            shutil.rmtree(picdirname)
        os.mkdir(picdirname, 0777 );
        
        self.create_xmldoc()
        exporter.ExporterMultirec.__init__(
            self, recipe_table, out, one_file=True, ext='mcb', exporter=rec_to_mcb,
            exporter_kwargs={'change_units':change_units,
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
        # The exporter has opened a file for us, which we're not going to use.
        self.ofi.close()

        # We save our correctly named XML to the temp dir so it won't collide
        # with any files present in the user's selected export dir.
        basename = os.path.basename(self.outputfilename)
        xml_basename = os.path.splitext(basename)[0] +'.xml'
        xml_path = os.path.join(tempfile.gettempdir(), xml_basename)
        self.xml_ofi = open(xml_path,'wb')
        self.xmlDoc.writexml(self.xml_ofi, newl = '\n', addindent = "\t", encoding = "UTF-8")
        # flush to the disk
        self.xml_ofi.close()
        
        # add xml and images to the zip (mcb)
        myfile = zipfile.ZipFile(self.outputfilename, mode='w')
        try:
            myfile.write(xml_path, xml_basename, zipfile.ZIP_DEFLATED)
            picdirname = os.path.join(tempfile.gettempdir(),'images')
            for images in os.listdir(picdirname):
                full_image_path = os.path.join(picdirname, images)
                if os.path.isfile(full_image_path):
                    myfile.write(full_image_path, os.path.join('images',os.path.basename(full_image_path)), zipfile.ZIP_DEFLATED)
        finally:
            # close zipfile
            myfile.close()
        
        # cleanup temp dir
        shutil.rmtree(tempfile.gettempdir())
        tempfile.tempdir = self.ostempdir_bck
        
        
def quoteattr (str):
    return xml.sax.saxutils.quoteattr(xml.sax.saxutils.escape(str))
