'''This set of unit tests uses dogtail to do interface
testing. Dogtail works by running the application "from the outside",
so to speak. These tests cannot access Gourmet internals, but they can
simulate actual user clicks, etc.

'''
import unittest
import time
import tempfile
import os.path

import gtk
import dogtail
import dogtail.procedural as dp
from dogtail.utils import screenshot

GOURMET_APP_PATH = './gourmet_in_place'
APPNAME = 'gourmet_in_place'

class BasicTests (unittest.TestCase):

    gdir = tempfile.mktemp()
    firstRun = True

    def setUp (self):
        # Start application
        print self,'set up!'
        print 'running',GOURMET_APP_PATH,self.gdir
        dp.run(GOURMET_APP_PATH,'--gourmet-directory=%s'%self.gdir,APPNAME)
        print 'Done with run!'
        if BasicTests.firstRun:
            print 'first run, sleep a bit extra...'
            time.sleep(3)
            BasicTests.firstRun = False
        time.sleep(2)
        print 'focus frame'
        dp.focus.application(APPNAME)
        print 'setUp done!'

    def tearDown (self):
        print 'tearDown!'
        # Quit application!
        print 'Quit app!'
        dp.focus.application(APPNAME)
        dp.focus.frame('Gourmet Recipe Manager')
        dp.keyCombo('<Ctrl>Q')
        print 'Hit quit!'
        time.sleep(2)
        print 'tearDown done!'
        os.system('killall gourmet_in_place') # Maek sure it's really dead...

    def testEditingNewCard (self):
        dp.focus.application(APPNAME)
        dp.focus.frame('Gourmet Recipe Manager')
        #dp.keyCombo('<Ctrl>N')
        dp.click('File')
        dp.click('New')
        dp.focus.frame(u'New Recipe (Edit)')
        dp.keyCombo('<Alt>l')
        dp.focus.widget('Title Entry')
        time.sleep(1)        
        dp.type('Testing!')
        dp.focus.widget('Preparation Time Entry')
        time.sleep(1)                
        dp.type('30 minutes')
        dp.focus.widget('Rating Entry')
        time.sleep(1)                
        dp.type('4')
        screenshot('Edited_recipe.png')
        #dp.keyCombo('<Ctrl>W')
        dp.click("Recipe")
        dp.click("Close")
        screenshot('save_changes_to_edited_rec.png')
        dp.focus.dialog('Question')
        #dp.keyCombo('<Alt>C')
        dp.click("Cancel")
        #self.assertEqual(hasattr(rc,'recipe_editor'),True,'Cancelling save-changes did not work')
        dp.focus.frame(u'New Recipe (Edit)')
        time.sleep(3)
        dp.keyCombo('<Ctrl>W')
        time.sleep(3)
        dp.focus.dialog('Question')
        dp.keyCombo('<Alt>S')
        screenshot('new_rec_saved.png')

    def testWebImport (self):
        self.do_testWebImport('file:///home/tom/Projects/grecipe-manager/src/tests/recipe_files/sample_site.html')
        self.search_and_open("Spaghetti")
        screenshot('web_imported_recipe_card-sample_site.png')        

    def testFileImport (self):
        self.do_testFileImport("/home/tom/Projects/grecipe-manager/src/tests/recipe_files/test_set.grmt")

    def testMastercookFileImport (self):
        self.do_testFileImport("/home/tom/Projects/grecipe-manager/src/tests/recipe_files/athenos1.mx2")

    def testMMFImport (self):
        self.do_testFileImport("/home/tom/Projects/grecipe-manager/src/tests/recipe_files/mealmaster.mmf")            

    def do_testFileImport (self, fn):
        shortname = os.path.split(fn)[1]
        dp.focus.application(APPNAME)
        dp.focus.frame('Gourmet Recipe Manager')
        dp.click("File")
        dp.click("Import file")
        dp.focus.dialog('Open recipe...')
        dp.keyCombo("<Alt>l")
        dp.type(fn)
        screenshot('import_dialog-%s-.png'%shortname)
        dp.keyCombo("Return")
        time.sleep(5) # wait for import to complete...
        print 'DONE SLEEPING -- IMPORT SHOULD BE DONE!'
        screenshot('import_done-%s.png'%shortname)
        dp.keyCombo("<Alt>C") # close dialog
        dp.focus.frame('Gourmet Recipe Manager')
        screenshot('with_imported_recs-%s.png'%shortname)

    def do_testWebImport (self, url):
        shortname = url.split('/')[-1]
        dp.focus.application(APPNAME)
        dp.focus.frame('Gourmet Recipe Manager')
        dp.click("File")
        dp.click('Import webpage')
        time.sleep(2)
        dp.focus.frame('Enter website address')
        print 'TYPING URL!'
        dp.type(url)
        dp.keyCombo("Return")
        time.sleep(1)
        screenshot('manual_web_import-%s.png'%shortname)
        dp.click('OK')
        screenshot('manual_web_import_done-%s.png'%shortname)
        dp.focus.dialog('Gourmet Import/Export')
        dp.click('Close')

    def search_and_open (self, txt):
        dp.focus.frame("Gourmet Recipe Manager")
        dp.keyCombo('<Alt>S') # Focus search
        dp.focus.text()
        dp.type(txt) # Search for our recipe
        dp.keyCombo('<Alt>L') # Focus recipe list
        dp.keyCombo('Return') # Open recipe
        time.sleep(1)


if __name__ == '__main__':
    print 'unittest.main()'
    unittest.main()
