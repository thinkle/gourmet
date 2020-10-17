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

from gourmet.exporters import exporter
import xml.dom
import sys, xml.sax.saxutils, base64
from gourmet.gdebug import debug
from gourmet.gglobals import NAME_TO_ATTR
import gourmet.convert as convert
import unittest

def string_to_number_type (n):
    if n.find('/')>-1:
        return 'frac'
    elif n.find('.')>-1:
        return 'float'
    else:
        return 'int'

def set_attribute (xmlDoc, element, attribute, value):
    a = xmlDoc.createAttribute(attribute)
    element.setAttributeNode(a)
    element.setAttribute(attribute,value)

class EdfgXmlBase:
    def write_header (self):
        a = self.xmlDoc.createAttribute('xmlns')
        self.top_element.setAttributeNode(a)
        self.top_element.setAttribute('xmlns',
            'http://www.eatdrinkfeelgood.org/1.1/ns')
        a = self.xmlDoc.createAttribute('xmlns:dc')
        self.top_element.setAttributeNode(a)
        self.top_element.setAttribute('xmlns:dc',
            'http://purl.org/dc/elements/1.1')
        a = self.xmlDoc.createAttribute('xmlns:xlink')
        self.top_element.setAttributeNode(a)
        self.top_element.setAttribute('xmlns:xlink',
            'http://www.w3.org/1999/xlink')
        a = self.xmlDoc.createAttribute('xmlns:xi')
        self.top_element.setAttributeNode(a)
        self.top_element.setAttribute('xmlns:xi',
            'http://www.w3.org/2001/XInclude')

class EdfgXml(exporter.exporter_mult, EdfgXmlBase):

    """ An XML exported for the eatdrinkfeelgood dtd """

    units = ['kilogram','gram','milligram',
             'litre','millilitre','gallon',
             'quart','pint','gill','cup',
             'tablespoon','teaspoon','bushel',
             'peck','pound','dram','ounce']

    def __init__ (self, rd, r, out, xmlDoc = None, conv = None, attdics={},
            change_units=False, mult=1):
        self.e_current_step = None
        self.e_directions = None
        if xmlDoc:
            self.single_recipe_file = False
            self.xmlDoc = xmlDoc
        else:
            # no xmlDoc passed.  create one...
            self.single_recipe_file = True
            impl = xml.dom.getDOMImplementation()
            doctype = impl.createDocumentType("eatdrinkfeelgood",
                "-//Aaron Straup Cope//DTD Eatdrinkfeelgood 1.2//EN//XML",
                "./eatdrinkfeelgood.dtd")
            self.write_header()

        exporter.exporter_mult.__init__(self, rd,r,out, use_ml=True,
                                        order=['attr','image','ings','text'],
                                        do_markup=True,
                                        change_units=change_units,
                                        mult=mult)


    def write_head (self):
        e = self.xmlDoc.createElement('recipe')
        self.xmlDoc.documentElement.appendChild(e)
        self.e_recipe = e


    def write_attr (self, label, text):
        attr = NAME_TO_ATTR[label]
        e_parent = self.e_recipe
        if attr == 'title':
            e = self.xmlDoc.createElement('name')
            e_parent.appendChild(e)
            e_parent = e
            attr = 'common'
        e = self.xmlDoc.createElement(attr)
        t = self.xmlDoc.createTextNode(xml.sax.saxutils.escape(text))
        e.appendChild(t)
        e_parent.appendChild(e)

    def write_text (self, label, text, time=None):
        """write_text() is called for each 'step' in the recipe"""
        if not self.e_directions:
            self.e_directions = self.xmlDoc.createElement('directions')
            self.e_recipe.appendChild(self.e_directions)
        e = self.xmlDoc.createElement('step')
        self.e_directions.appendChild(e)
        self.e_current_step = e
        e_para = self.xmlDoc.createElement('para')
        self.e_current_step.appendChild(e_para)
        t = self.xmlDoc.createTextNode(xml.sax.saxutils.escape(text))
        e_para.appendChild(t)
        if time:
            second_element = self.xmlDoc.createElement('seconds')
            n_element = self.n_element(time)
            second_element.appendChild(n_element)
            prep_element = self.xmlDoc.createElement('preparation')
            prep_element.appendChild(second_element)
            self.e_current_step.appendChild(prep_element)



    def write_image (self, image):
        e = self.xmlDoc.createElement('image')
        a = self.xmlDoc.createAttribute('content-type')
        e.setAttributeNode(a)
        e.setAttribute('content-type', 'jpeg')
        a = self.xmlDoc.createAttribute('rel')
        e.setAttributeNode(a)
        e.setAttribute('content-type', 'photo')

        e_bin64b = self.xmlDoc.createElement('bin64b')
        t = self.xmlDoc.createTextNode(base64.b64encode(image))
        e_bin64b.appendChild(t)
        e.appendChild(e_bin64b)
        if self.e_current_step:
            self.e_current_step.appendChild(e)
        else:
            self.e_recipe.appendChild(e)

    def handle_italic (self, chunk): return '&lt;i&gt;'+chunk+'&lt;/i&gt;'
    def handle_bold (self, chunk): return '&lt;b&gt;'+chunk+'&lt;/b&gt;'
    def handle_underline (self, chunk): return '&lt;u&gt;'+chunk+'&lt;/u&gt;'
    def write_foot (self):
        if self.single_recipe_file:
            self.xmlDoc.writexml(self.out, newl = '\n', addindent = "\t",
                    encoding = "UTF-8")

    def write_inghead (self):
        req_el = self.xmlDoc.createElement('requirements')
        self.e_recipe.appendChild(req_el)
        ing_el = self.xmlDoc.createElement('ingredients')
        req_el.appendChild(ing_el)
        self.e_ingredients  = ing_el

    def write_ingfoot (self):
        pass

    def write_ingref (self, amount=1, unit=None, item=None,
                      refid=None, optional=False):
        print('write_ingref not implemented yet')

    def write_ing (self, amount=1, unit=None, item=None,
                   key=None, optional=False):
        # item's are the same as keys in cozyland...
        if not key: key = item
        # grab info from our nutrition data info. This relies on rd.nd
        # being a reference to our NutritionData class -- this is
        # hackishly taken care of in CozyImporter.py.
        #
        # If this code is ever included in Gourmet proper, we should
        # delete all references to self.rd.nd
        ndbno = self.rd.nd.get_ndbno(key)
        if amount.find('-')>=0:
            gram_amount = [self.rd.nd.convert_to_grams(convert.frac_to_float(a),
                                                       unit,
                                                       item)
                           for a in amount.split('-')]
        else:
            gram_amount = self.rd.nd.convert_to_grams(convert.frac_to_float(amount),unit,item)
        # Write our XML
        e_parent = self.e_ingredients
        e = self.xmlDoc.createElement('ing')
        e_parent.appendChild(e)
        e_parent = e
        e_amount = self.xmlDoc.createElement('amount')
        if gram_amount:
            if not isinstance(gram_amount, (tuple, list)) or None not in gram_amount:
                e_amount.appendChild(
                    self.quantity_element(gram_amount,
                                          'gram')
                    )
        e_parent.appendChild(e_amount)
        e_displayamount = self.xmlDoc.createElement('displayamount')
        e_displayamount.appendChild(
            self.quantity_element(amount,unit)
            )
        e_parent.appendChild(e_displayamount)
        e_item = self.xmlDoc.createElement('item')
        e_parent.appendChild(e_item)
        t = self.xmlDoc.createTextNode(item)
        e_item.appendChild(t)
        if ndbno:
            e_usda = self.xmlDoc.createElement('usdaid')
            if ndbno:
                t = self.xmlDoc.createTextNode("%05i"%ndbno)
                e_usda.appendChild(t)
                e_parent.appendChild(e_usda)

    def write_grouphead (self, name):
        print('write_grouphead not implemented yet')

    def write_groupfoot (self):
        print('write_groupfoot not implemented yet')

    def quantity_element (self, amount, unit):
        """Make a quantity element based on our amount and unit.
        """
        customunit = unit not in self.units
        e_qty = self.xmlDoc.createElement('quantity')
        if amount:
            if isinstance(amount, str) and amount.find('-')>=0:
                amount = amount.split('-')
            if isinstance(amount,tuple) or isinstance(amount,list) and len(amount)==2:
                e_rng = self.xmlDoc.createElement('range')
                e_qty.appendChild(e_rng)
                for a,typ in [(amount[0],'min'),(amount[1],'max')]:
                    e = self.xmlDoc.createElement(typ)
                    e_rng.appendChild(e)
                    e.appendChild(self.n_element(a))
            else:
                if isinstance(amount, (list, tuple)):
                    # If we have a list here, something's gone a bit screwy...
                    for possible_n in amount:
                        try:
                            e = self.n_element(amount)
                        except TypeError:
                            continue
                        else:
                            e_qty.appendChild(e)
                            break
                else:
                    e_qty.appendChild(self.n_element(amount))
        # Now for the measure...
        if unit:
            e_msr = self.xmlDoc.createElement('measure')
            e_qty.appendChild(e_msr)
            if customunit:
                e_unit = self.xmlDoc.createElement('customunit')
                e_unit.appendChild(
                    self.xmlDoc.createTextNode(unit)
                    )
            else:
                e_unit = self.xmlDoc.createElement('unit')
                set_attribute(self.xmlDoc,e_unit,'unit',unit)
            e_msr.appendChild(e_unit)
        return e_qty

    def n_element (self, n):
        if isinstance(n, str):
            typ = string_to_number_type(n)
        elif isinstance(n, int):
            typ = 'int'
        elif isinstance(n, float):
            typ = 'float'
        else:
            raise TypeError("%s is not a number"%n)
        e_n = self.xmlDoc.createElement('n')
        set_attribute(self.xmlDoc,e_n,'type',typ)
        set_attribute(self.xmlDoc,e_n,'value',str(n))
        return e_n


class EdfgXmlM(exporter.ExporterMultirec, EdfgXmlBase):
    def __init__ (self, rd, recipe_table, out, one_file=True,
        change_units=False, mult=1):
        self.rd=rd
        impl = xml.dom.getDOMImplementation()
        doctype = impl.createDocumentType("eatdrinkfeelgood",
            "-//Aaron Straup Cope//DTD Eatdrinkfeelgood 1.2//EN//XML",
            "./eatdrinkfeelgood.dtd")
        self.xmlDoc = impl.createDocument(None, "eatdrinkfeelgood", doctype)
        self.top_element = self.xmlDoc.documentElement
        exporter.ExporterMultirec.__init__(
            self, rd, recipe_table, out, one_file=True, ext='xml', exporter=EdfgXml,
            exporter_kwargs={'change_units':change_units,
                             'mult':mult,
                             'xmlDoc':self.xmlDoc
                             }
            )

    def write_footer (self):
        self.xmlDoc.writexml(self.ofi, newl = '\n', addindent = "\t",
                encoding = "UTF-8")

class ExportTestCase (unittest.TestCase):

    TEST_RECS = [
        [{'title':'Foo',
          'source':'Bar',
          'season':'Winter'},
         ['1 tsp. sugar',
          '2 c. wine',
          '3 cloves garlic',
          '4 1/2 apples'
          'salt',
          'pepper'],
         ['Eat','Cook','Try\nSome\nNew\nLines']
         ],
        [{'title':'Screwy',
          'season':'123',
          'servings':'34'},
         ['1- baseballs',
          '2-3 cups',
          '3-4 wild and crazy recipes.'],
         []],
        ]

    out_file = 'eatdrinkfeelgood_test.xml'

    def setUp (self):
        import fake_db, tempfile
        from cozy_interactive_importer import CozyInteractiveImporter
        from gourmet.importers.interactive_importer import ConvenientImporter
        self.rd = fake_db.RecData(tempfile.mktemp('.db'))
        import gourmet.nutrition.nutrition as nutrition
        import gourmet.convert
        c = gourmet.convert.Converter()
        self.rd.nd = nutrition.NutritionData(self.rd,c)

        class DumbImporter (CozyInteractiveImporter):
            added_to = False
            def __init__ (self, rd):
                ConvenientImporter.__init__(self,rd,threaded=True)
            def set_added_to (self,bool):
                self.added_to = bool

        imp = DumbImporter(self.rd)
        for attrs,ings,steps in self.TEST_RECS:
            imp.start_rec()
            for a,v in list(attrs.items()): imp.add_attribute(a,v)
            for i in ings:
                imp.add_ing_from_text(i)
            for s in steps:
                imp.add_text('step',s)
            imp.commit_rec()


    def testExport (self):
        from gourmet.exporters import exporter
        e=EdfgXmlM(
            self.rd,
            [self.rd.recipe_table[k] for k in self.rd.recipe_table],
            self.out_file,
            #threaded = False
            )
        e.run()

if __name__ == '__main__':
    unittest.main()
