import test
import os,os.path
DIR = os.path.abspath(os.path.join(os.path.split(__file__)[0],'reference_setup/'))
TEST_FILE_DIRECTORY = os.path.join(DIR,'recipes.db')
import gourmet.gglobals as gglobals

gglobals.gourmetdir = DIR
gglobals.dbargs['file'] = TEST_FILE_DIRECTORY

import recipeManager as rm
import time
import exporters

import tempfile
import traceback
import unittest
import re

OUTPUT_DIRECTORY = os.path.join(
    tempfile.tempdir,
    'export_tests')
OUTPUT_DIRECTORY = os.path.join(OUTPUT_DIRECTORY,
                                time.strftime('%d.%m.%y'))
if os.path.exists(OUTPUT_DIRECTORY):
    n = 1
    while os.path.exists(OUTPUT_DIRECTORY + '-' + str(n)): n+=1
    OUTPUT_DIRECTORY += '-%s'%n

if not os.path.exists(OUTPUT_DIRECTORY): os.makedirs(OUTPUT_DIRECTORY)

def confirm_strings_are_in_file (ss, fi):
    whole_file = file(fi,'r').read()
    for s in ss:
        try:
            assert(re.search(s,whole_file))
        except:
            raise AssertionError('Fail to find %s in exported file %s.'%(s,fi))

confirmation_tests = {
    # These are extra tests that should be run -- each method must
    # take the filename of the exported file as its argument and raise
    # an error if it fails

    # Gourmet File Format Test
    'Gourmet XML File':lambda f: confirm_strings_are_in_file([
    '''<ingref''',
    '''<link''',
    # Nested ingredients...
    '''<inggroup>\s*<groupname>\s*Dressing\s*</groupname>\s*<ingredient>\s*<amount>\s*1/2\s*</amount>\s*<unit>\s*tsp\.\s*</unit>\s*<item>\s*red pepper flakes\s*</item>\s*<key>\s*red pepper flakes\s*</key>\s*</ingredient>''',
    # Image
    '''<image format="jpeg">\s*<!\[CDATA\[/9j''',
    # Times
    '''<cooktime>\s*20 minutes''',
    '''<preptime>\s*1/2 hour''',
    '''<rating>\s*4/5 stars''',
    '''<servings>\s*4\s*''',
    '''<category>\s*Dessert''',
    '''<cuisine>\s*Asian/Chinese''',
    # Formatting
    re.escape('''&amp;lt;i&amp;gt;But this should be in italics'''),
    re.escape('''&amp;lt;b&amp;gt;And this should be in bold'''),
    ],
                                                  f),
    # End Gourmet File Format Test

    # MealMaster test
    'MealMaster file': lambda f: confirm_strings_are_in_file([
    # formatting
    re.escape('''*But this should be in italics*'''),
    '''AND THIS SHOULD BE IN BOLD''',
    'Title: Ranges', # title
    '1\s*recipe\s*Ranges', # recipe reference
    '-+DRESSING-+\s*1/2\s*t\s*red pepper flakes' # Ingredient group
    ],
                                                             f),
    # End MealMaster test

    # RTF Tests
    'RTF':lambda f: confirm_strings_are_in_file([
    # Formatting
    '\\i.*But this should be in italics',
    '\\b.*And this should be in bold',
    '1 recipe Ranges', #Recipe reference
    re.escape('\pict{\jpegblip'), #Image
    ],
                                                f),
    # End RTF Tests

    }


class ExportTest:

    #failures = []

    def run (self):
        for d in tests: self.run_test(d)

    def run_test (self, d):

        if d.has_key('filename'):
            d['filename']=os.path.join(OUTPUT_DIRECTORY,
                                       d['filename'])
            self.test_import(d['filename'])
        elif d.has_key('url'): self.test_web_import(d['url'])
        else: print 'WTF: no test contained in ',d
        if d.has_key('test'):
            self.do_test(d['test'])

    def do_test (self, test):
        recs = self.db.search(self.db.recipe_table,
                              'title',
                              test['title'],
                              exact=True,
                              use_regexp=False)
        rec = recs[0]
        ings = self.db.get_ings(rec)
        if test.get('all_ings_have_amounts',False):
            for i in ings:
                assert(i.amount)
        if test.get('all_ings_have_units',False):
            for i in ings:
                assert(i.unit)


    def setup_db (self):
        print 'rm.dbargs[file]=',rm.dbargs['file']
        self.db = rm.RecipeManager(**rm.dbargs)
        if self.db.fetch_len(self.db.recipe_table)==0:
            raise Exception("No recipes in database.")
        self.mult_export_args = {'rd':self.db,
                                 'rv':self.db.fetch_all(self.db.recipe_table),
                                 'conv':None,
                                 'prog':None,
                                 'extra_prefs':{}
                                 }

    def test_export (self, k):
        n = 1
        new_file = os.path.join(OUTPUT_DIRECTORY,
                                '.'.join([k,str(n)])
                                )
        while os.path.exists(new_file):
            n += 1
            new_file = os.path.join(OUTPUT_DIRECTORY,
                                    '.'.join([k,str(n)])
                                    )
        self.mult_export_args['file']=new_file
        print 'Testing export ',k,'to',new_file,self.mult_export_args
        exporters.exporter_dict[k]['mult_exporter'](self.mult_export_args.copy()).run()
        if confirmation_tests.has_key(k):
            print 'Running confirmation test on ',k
            confirmation_tests[k](new_file) # Test!
        print 'Done!'

    def test_all_exports (self):
        for k in exporters.exporter_dict: self.test_export(k)



def add_export_test_cases (name, bases, attrs):
    def make_method (k):
        def _ (self): self.et.test_export(k)
        return _
    for k in exporters.exporter_dict:
        method_name = 'test'+k.replace(' ','')
        attrs[method_name]= make_method(k)
    print "Our class has attrs:",attrs
    return type(name,bases,attrs)

et = None

class ExportTestCase (unittest.TestCase):

    __metaclass__ = add_export_test_cases # Makes us testFoo methods
                                          # for each type of Foo we
                                          # support

    def setUp (self):
        print 'setUp'
        global et
        if not et:
            print 'Initialize DB'
            et = self.et = ExportTest()
            self.et.setup_db()
        else:
            print 'Use previously initialized DB'
            self.et = et

    #def testAllExports (self):
    #    self.it.test_all_exports()

if __name__ == '__main__':
    #et=ExportTest()
    #et.setup_db()
    unittest.main()
    #pass
