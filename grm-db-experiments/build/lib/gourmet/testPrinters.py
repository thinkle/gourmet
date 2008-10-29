import gglobals
import recipeManager as rm
import traceback, unittest, os, tempfile
from gettext import gettext as _
import gettext

TEST_FILE_DIRECTORY = 'exporters/reference_setup/recipes.mk'

class PrinterTester:

    printer_modules = ['gnomeprinter','wxprinter','lprprinter']
    
    def setup_db (self):
        rm.dbargs['file']=os.path.abspath(tempfile.mktemp('.db'))
        print 'Loading reference database'
        self.db = rm.RecipeManager(**rm.dbargs)
        self.add_recs()
        print 'Done.'

    def add_recs (self):
        r = self.db.add_rec({'title':'Test',
                         'cuisine':'French',
                         'servings':4,
                         'rating':8,
                         'source':'Guido van Rossom',
                         'instructions':'This is some line of instructions repeated a number of times.'*10,
                         'modifications':'These are some notes'*5,
                         })
        self.db.add_ing({'id':r.id,
                         'item':'tomato',
                         'ingkey':'tomato, fresh',
                         'unit':2,
                         'amount':None,
                         })
        self.db.add_ing({'id':r.id,
                         'item':'French bread',
                         'ingkey':'bread, french',
                         'unit':'baguettes',
                         'amount':0.5
                         })

    def testAllPrinters (self):
        failed_imports = []
        other_failures = []
        for m in self.printer_modules:
            print 'Testing ',m
            try:
                self.testPrintingModule(m)
            except ImportError:
                failed_imports.append((m,traceback.format_exc()))
                print 'Failed to import'
            except:
                other_failures.append((m,traceback.format_exc()))
                print 'Failed'
        for m,e in failed_imports:
            print m,'Failed'
            print e
            print '---'
        for m,e in other_failures:
            print m,'Failed!'
            print e
            print '---'            
        n_imported = len(self.printer_modules)-len(failed_imports)
        n_worked = len(self.printer_modules) - len(failed_imports) - len(other_failures)
        print 'Imported ','%s/%s'%(n_imported,len(self.printer_modules)),'printing modules'
        print n_worked,'of',n_imported,'imported modules succeeded!'


    def testPrintingModule (self, m):
        mod = __import__('exporters.'+m,globals(),locals(),['exporters'])
        self.testPrinter(mod.RecRenderer)

    def testPrinter (self, RecRenderer):
        print 'Test 3 recipes'
        RecRenderer(self.db,
                    # print 3 recipes from our test suite
                    [self.db.fetch_all(self.db.rview)[0]],
                    #self.db.rview[0],
                    mult=1,
                    dialog_title=gettext.ngettext('Print %s recipe',
                                                  'Print %s recipes',
                                                  1)%1,
                    dialog_parent = None,
                    change_units = False
                    )
        print 'Test individual recipe, multiplied * 3'
        RecRenderer(self.db,
                    # print 3 recipes from our test suite
                    [self.db.fetch_all(self.db.rview)[0]],
                    #self.db.rview[0],
                    mult=1,
                    dialog_title='Print 1 recipe, multiplied by 3',
                    dialog_parent = None,
                    change_units = True,
                    )
        
class PrinterTestCase (unittest.TestCase):
    def setUp (self):
        self.pt = PrinterTester()
        self.pt.setup_db()

    def testAllPrinters (self):
        self.pt.testAllPrinters()

if __name__ == '__main__':
    unittest.main()
