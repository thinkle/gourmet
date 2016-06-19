from __future__ import print_function

from exporter import exporter_mult
import xml.dom
import types
# Base XML exporter class

class XmlExporter (exporter_mult):

    #doc_element = 'rec'
    #doctype_desc = ''
    #dtd_path = ''
    
    def __init__ (self, rd, r, out,
                  order=['attr','image','ings','text'],
                  xmlDoc=None,
                  **kwargs):
        if xmlDoc:
            self.xmlDoc = xmlDoc
            self.i_created_this_document = False
            self.top_element = self.xmlDoc.childNodes[1]
        else:
            self.create_xmldoc()
        exporter_mult.__init__(self, rd,r,out,
                               use_ml=True,
                               convert_attnames=False,
                               do_markup=True,
                               order=order,
                               **kwargs)

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
        try:
            assert(type(text) in types.StringTypes)
        except:
            print('Text is not text')
            print('append_text received', element, text)
            raise TypeError(text+' is not a StringType')
        try:
            t = self.xmlDoc.createTextNode(text)
            element.appendChild(t)
        except:
            print('FAILED WHILE WORKING ON ', element)
            print('TRYING TO APPEND', text[:100])
            raise
            
    def create_text_element (self, element_name, text, attrs={}):
        element = self.create_element_with_attrs(element_name,attrs)
        self.append_text(element,text)
        return element

    def create_element_with_attrs (self, element_name, attdic):
        element = self.xmlDoc.createElement(element_name)
        for k,v in attdic.items():
            self.set_attribute(element,k,str(v))
        return element

