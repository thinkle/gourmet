from exporter import exporter_mult
import xml.dom
# Base XML exporter class

class XmlExporter (exporter_mult):

    #doc_element = 'rec'
    #doctype_desc = ''
    #dtd_path = ''

    def __init__ (self, rd, r, out, conv=None,
                  order=['attr','image','ings','text'],
                  change_units=True,
                  mult=1,
                  xmlDoc = None):
        if xmlDoc:
            self.xmlDoc = xmlDoc
            self.i_created_this_document = False
            self.top_element = self.xmlDoc.childNodes[1]
        else:
            self.create_xmldoc()
        exporter_mult.__init__(self, rd,r,out, use_ml=True,
                                        convert_attnames=False,
                                        order=order,
                                        do_markup=True,
                                        change_units=change_units,
                                        mult=mult)

    def create_xmldoc (self):
        self.i_created_this_document = True
        impl = xml.dom.getDOMImplementation()
        doctype = impl.createDocumentType(
            self.doc_element,
            self.doctype_desc,
            self.dtd_path
            )
        self.xmlDoc = impl.createDocument(None,self.doc_element,doctype)
        self.top_element = self.xmlDoc.documentElement

    # Convenience methods
    def set_attribute (self, element, attribute, value):
        a = self.xmlDoc.createAttribute(attribute)
        element.setAttributeNode(a)
        element.setAttribute(attribute,value)
        
    def append_text (self, element, text):
        t = self.xmlDoc.createTextNode(xml.sax.saxutils.escape(text))
        element.appendChild(t)
            
    def create_text_element (self, element_name, text, attrs={}):
        element = self.create_element_with_attrs(element_name,attrs)
        self.append_text(element,text)
        return element

    def create_element_with_attrs (self, element_name, attdic):
        element = self.xmlDoc.createElement(element_name)
        for k,v in attdic.items():
            self.set_attribute(element,k,str(v))
        return element

