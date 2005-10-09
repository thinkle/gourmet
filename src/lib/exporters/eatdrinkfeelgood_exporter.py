# Export Gourmet recipes to eatdrinkfeelgood XML format 
# Copyright (c) 2005 cozybit, Inc. 
#
# Author: Javier Cardona <javier_AT_cozybit.com>
# 
# Based on the Gourmet exporter interface developed by Thomas Hinkle
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

import exporter
import xml.dom
import sys, xml.sax.saxutils, base64
from gourmet.gdebug import *
from gourmet.gglobals import *

class EdfgXml(exporter.exporter_mult):

    """ An XML exported for the eatdrinkfeelgood dtd """
    
    def __init__ (self, rd, r, out,attdics={},change_units=False,mult=1):
        impl = xml.dom.getDOMImplementation()
        self.xmldoc = impl.createDocument(None, "eatdrinkfeelgood", None)
        self.top_element = self.xmldoc.documentElement
        self.attdics = attdics
        exporter.exporter_mult.__init__(self, rd,r,out, use_ml=True,
                                        order=['attr','image','ings','text'],
                                        do_markup=True,
                                        change_units=change_units,
                                        mult=mult)

    def write_head (self):
        pass

    def write_attr (self, label, text):
        attr = NAME_TO_ATTR[label]
        e = self.xmldoc.createElement(attr)
        t = self.xmldoc.createTextNode(xml.sax.saxutils.escape(text))
        e.appendChild(t)
        self.top_element.appendChild(e)
        
    def write_text (self, label, text):
        t = self.xmldoc.createTextNode(xml.sax.saxutils.escape(text))
        e.appendChild(t)
        self.top_element.appendChild(e)

    def write_image (self, image):
        e = self.xmldoc.createElement('image')
        a = self.xmldoc.createAttribute('content-type')
        e.setAttributeNode(a)
        e.setAttribute('content-type', 'jpeg')
        a = self.xmldoc.createAttribute('rel')
        e.setAttributeNode(a)
        e.setAttribute('content-type', 'photo')

        e_bin64b = self.xmldoc.createElement('bin64b')
        t = self.xmldoc.createTextNode(base64.b64encode(image))
        e_bin64b.appendChild(t)
        e.appendChild(e_bin64b)
        self.top_element.appendChild(e)
    
    def handle_italic (self, chunk): return '&lt;i&gt;'+chunk+'&lt;/i&gt;'
    def handle_bold (self, chunk): return '&lt;b&gt;'+chunk+'&lt;/b&gt;'    
    def handle_underline (self, chunk): return '&lt;u&gt;'+chunk+'&lt;/u&gt;'    
    def write_foot (self):
        # this should be called last.  Time to write our file.
        self.xmldoc.writexml(self.out, newl = '\n', addindent = "\t")

    def write_inghead (self):
        print 'write_inghead not implemented yet'

    def write_ingfoot (self):
        print 'write_ingfoot not implemented yet'

    def write_ingref (self, amount=1, unit=None, item=None, refid=None, optional=False):
        print 'write_ingref not implemented yet'
        
    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        print 'write_ing not implemented yet'

    def write_grouphead (self, name):
        print 'write_grouphead not implemented yet'
        
    def write_groupfoot (self):
        print 'write_groupfoot not implemented yet'

#
# Everything below this comment is just a minimal unit test for the exporter.
# I could not find an easy way to create a test backend to for this test, so I
# wrote an ugly very limited one.
#
# When this module is run standalone, it will produce a bogus edfg-out.xml
# file
#

if __name__ == '__main__':

    class Ingredient:
        foo = 0

    class Recipe:
        attr = 'foo'
        servings = 4

    class FakeRecDb:
        def get_cats(self, rec):
            return ['food', 'poison']

        def get_ings(self, rec):
            return Ingredient() 

        def order_ings(self, iview):
            return [[None,['mucus']]] 

        def get_amount_and_unit (self, ing, mult=1,
            conv=None,fractions = None):
            return (1, 'gigaspoon')  

    f = file('edfg-out.xml', 'w')
    exporter = EdfgXml(FakeRecDb(),Recipe(),f)

