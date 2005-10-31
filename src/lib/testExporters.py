import recipeManager as rm
import time
import exporters
import os,os.path
import tempfile
import traceback
import unittest
import tempfile

OUTPUT_DIRECTORY = os.path.join(
    '/tmp',
    'export_tests')
OUTPUT_DIRECTORY = os.path.join(OUTPUT_DIRECTORY,
                                time.strftime('%d.%m.%y'))
if os.path.exists(OUTPUT_DIRECTORY):
    n = 1
    while os.path.exists(OUTPUT_DIRECTORY + '-' + str(n)): n+=1
    OUTPUT_DIRECTORY += '-%s'%n

if not os.path.exists(OUTPUT_DIRECTORY): os.makedirs(OUTPUT_DIRECTORY)
TEST_FILE_DIRECTORY = 'exporters/reference_setup/recipes.mk'

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
        recs = self.db.search(self.db.rview,
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
        rm.dbargs['file']=os.path.abspath(TEST_FILE_DIRECTORY)
        print 'rm.dbargs[file]=',rm.dbargs['file']
        self.db = rm.RecipeManager(**rm.dbargs)
        print len(self.db.rview),'recipes total'
        if len(self.db.rview)==0: raise "No recipes in database."
        self.mult_export_args = {'rd':self.db,
                                 'rv':self.db.rview,
                                 'conv':None,
                                 'prog':None,
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
        print 'Testing export ',k,'to',new_file
        exporters.exporter_dict[k]['mult_exporter'](self.mult_export_args.copy()).run()
        print 'Done!'

    def test_all_exports (self):
        for k in exporters.exporter_dict: self.test_export(k)



def add_export_test_cases (name, bases, attrs):
    def make_method (k):
        def _ (self): self.it.test_export(k)
        return _
    for k in exporters.exporter_dict:
        method_name = 'test'+k.replace(' ','')
        attrs[method_name]= make_method(k)
    print "Our class has attrs:",attrs
    return type(name,bases,attrs)

class ExportTestCase (unittest.TestCase):

    __metaclass__ = add_export_test_cases

    def setUp (self):
        print 'setUp'
        self.it = ExportTest()
        self.it.setup_db()

    #def testAllExports (self):
    #    self.it.test_all_exports()

if __name__ == '__main__':
    #et=ExportTest()
    #et.setup_db()
    unittest.main()
    #pass
