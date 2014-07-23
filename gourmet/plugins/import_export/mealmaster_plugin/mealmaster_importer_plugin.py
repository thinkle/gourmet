import os.path

import mealmaster_importer
from gourmet.plugin import ImporterPlugin
from gourmet.importers.importer import Tester
from gourmet.threadManager import get_thread_manager

from gourmet.recipeManager import get_recipe_manager
    
test_dir = os.path.split(__file__)[0] # our directory src/lib/plugins/import_export/plugin/*/
test_dir = os.path.split(test_dir)[0] # one back... src/lib/plugins/import_export/plugin/
test_dir = os.path.split(test_dir)[0] # one back... src/lib/plugins/import_export/
test_dir = os.path.split(test_dir)[0] # one back... src/lib/plugins/
test_dir = os.path.split(test_dir)[0] # one back... src/lib/
test_dir = os.path.split(test_dir)[0] # one back... src/
test_dir = os.path.join(test_dir,'tests','recipe_files')

class MealmasterImporterPlugin (ImporterPlugin):

    get_source = 'source'
    name = _('MealMaster file')
    patterns = ['*.mmf','*.txt']
    mimetypes = ['text/mealmaster','text/plain']

    def test_file (self, filename):
        '''Given a filename, test whether the file is of this type.'''
        return Tester(mealmaster_importer.mm_start_pattern).test(filename)

    def get_importer (self, filename):
        return mealmaster_importer.mmf_importer(filename=filename)
                                                   
    def get_import_tests (self):
        return [
            (os.path.join(test_dir,
                          'mealmaster_2_col.mmf'),
             test_2_col),
            (os.path.join(test_dir,
                          'mealmaster.mmf'),
             test_mmf)
            ]

def assert_equal (val1,val2):
    assert val1==val2, 'Value expected: %s, Actual value: %s'%(val2,val1)

def assert_equal_ignorecase (val1, val2): return assert_equal(val1.lower(),val2.lower())

def test_mmf (recs, filename):
    rd = get_recipe_manager()
    assert_equal(recs[0].title,'Almond Mushroom Pate')
    assert_equal(recs[0].yields, 6)
    assert_equal(recs[0].yield_unit,'servings')
    assert_equal(recs[3].title,'Anchovy Olive Dip')
    ings = rd.get_ings(recs[3])
    assert_equal(ings[1].item,'Finely chopped stuffed green olives') # test line-wrap

def test_2_col (recs, filename):
    rd = get_recipe_manager()    
    assert len(recs) == 1,'Expected 1 recipes; got %s (%s)'%(len(recs),recs)
    chile_ings = rd.get_ings(recs[0])
    print 'chile_ings=',chile_ings
    assert_equal(chile_ings[0].amount, 2)
    assert_equal(chile_ings[1].amount, 1) # second column
    assert_equal_ignorecase(chile_ings[1].ingkey, 'eggs')
    assert_equal(chile_ings[1].item, 'Eggs; separated')
    assert_equal_ignorecase(chile_ings[0].ingkey, u'Chiles, calif.')
    assert_equal(recs[0].yields, 2)
    assert_equal(recs[0].yield_unit, 'servings')
    assert_equal(recs[0].title, u'Chiles Rellenos de Queso')
    assert_equal(chile_ings[5].item, 'Tomatoes; peeled')
    assert_equal_ignorecase(chile_ings[5].inggroup, 'Tomato Sauce')
