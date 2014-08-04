import gourmet.exporters.exporter as exporter
import xml.sax.saxutils, base64
from gourmet.exporters.xml_exporter import XmlExporter

from gourmet.util.yields import Yield

class rec_to_xml (XmlExporter):
    """A vastly simplified recipe XML exporter.

    The previous XML format was written as a format designed for
    itself (its design predated gourmet). This one is really written
    as a simple way to save, load and exchange Gourmet recipes. As a
    result, the code is much simpler, and the format should be quicker
    to write and more convenient for exchanging single recipes.

    This implementation actually uses the DOM to ensure correctness.
    """

    doc_element = 'gourmetDoc'
    doctype_desc = ''
    dtd_path = ''
    ALLOW_PLUGINS_TO_WRITE_NEW_FIELDS = False
    
    def write_head (self):
        self.rec_el = self.create_element_with_attrs("recipe",{'id':self.r.id})
        self.top_element.appendChild(self.rec_el)

    def write_attr (self, attr, item):
        if isinstance(item, Yield):
            item=format(item, "{'fractions': %s}"%self.fractions)
        else:
            item=unicode(item)
        self.rec_el.appendChild(self.create_text_element(attr.replace(' ',''),item))
        
    def write_text (self, attr, text):
        self.rec_el.appendChild(
            self.create_text_element(attr.replace(' ',''),text)
            )

    def write_image (self, image):
        image_el = self.create_element_with_attrs('image',{'format':'jpeg'})
        image_el.appendChild(
            self.xmlDoc.createCDATASection(base64.b64encode(image))
            )
        self.rec_el.appendChild(image_el)
    
    def handle_italic (self, chunk): return '&lt;i&gt;'+chunk+'&lt;/i&gt;'
    def handle_bold (self, chunk): return '&lt;b&gt;'+chunk+'&lt;/b&gt;'    
    def handle_underline (self, chunk): return '&lt;u&gt;'+chunk+'&lt;/u&gt;'    
        
    def write_foot (self):
        if self.i_created_this_document:
            self.xmlDoc.writexml(self.ofi, newl = '\n', addindent = "\t", 
                                 encoding = "UTF-8")

    def write_inghead (self):
        self.inglist_el = self.xmlDoc.createElement('ingredient-list')
        self.top_inglist = self.inglist_el # because groups will let us nest...
        self.rec_el.appendChild(self.inglist_el)

    def write_ingref (self, ingredient):
        self.inglist_el.appendChild(
            self.create_text_element('ingref',
                                     ingredient.item,
                                     {'refid':str(ingredient.refid),
                                      'amount':ingredient.amount}
                                     )
            )
        
    def write_ing (self, ingredient):
        if ingredient.optional:
            ing_el = self.create_element_with_attrs('ingredient',{'optional':'yes'})
        else:
            ing_el = self.create_element_with_attrs('ingredient',{})
        self.inglist_el.appendChild(ing_el)
        if ingredient.amount:
            ing_el.appendChild(
                self.create_text_element('amount',
                                         format(ingredient.amt,
                                                "{'fractions': %s}"%
                                                self.fractions))
                )
        if ingredient.unit:
            ing_el.appendChild(
               self.create_text_element('unit',ingredient.unit)
               )
        if ingredient.item:
            ing_el.appendChild(
                self.create_text_element('item',ingredient.item)
                )
        if ingredient.ingkey:
            ing_el.appendChild(
                self.create_text_element('key',ingredient.ingkey)
                )

    def write_grouphead (self, name):
        group_el = self.xmlDoc.createElement('inggroup')
        group_el.appendChild(
            self.create_text_element('groupname',name)
            )
        self.inglist_el = group_el
        
    def write_groupfoot (self):
        self.top_inglist.appendChild(self.inglist_el)
        self.inglist_el = self.top_inglist
    

class recipe_table_to_xml (exporter.ExporterMultirec, XmlExporter):
    doc_element = 'gourmetDoc'
    doctype_desc = ''
    dtd_path = ''
    
    def __init__ (self, recipe_table, out, one_file=True, change_units=False):
        self.create_xmldoc()
        exporter.ExporterMultirec.__init__(
            self, recipe_table, out, one_file=True, ext='xml', exporter=rec_to_xml,
            exporter_kwargs={'change_units':change_units,
                             'xmlDoc':self.xmlDoc,
                             # This order is now in our DTD so we'd
                             # better make it solid.
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
        self.xmlDoc.writexml(self.ofi, newl = '\n', addindent = "\t", 
                             encoding = "UTF-8")
        
def quoteattr (str):
    return xml.sax.saxutils.quoteattr(xml.sax.saxutils.escape(str))
