import recipeManager as rm
import time
import importers
import os,os.path
import importers.html_importer
import tempfile
import traceback
import unittest

TEST_FILE_DIRECTORY = '/home/tom/Projects/Data'

times = []
def time_me (f): return f
def old_time_me (f):
    def _ (*args,**kwargs):
        print 'Running',f.__name__,args,kwargs
        start = time.time()
        try:
            ret = f(*args,**kwargs)
        except:
            end = time.time()
            times.append((f.__name__,args,kwargs,start,end,end-start))
            print 'Failed after ',end-start,'seconds.'
            raise
        else:
            end = time.time()
            times.append((f.__name__,args,kwargs,start,end,end-start))
            print 'Finished in ',end-start,'seconds.'
            return ret
    return _

class ImportTest:

    #failures = []

    def run (self):
        for d in tests: self.run_test(d)

    def run_test (self, d):
        if d.has_key('filename'):
            d['filename']=os.path.join(TEST_FILE_DIRECTORY,
                                       d['filename'])
            self.test_import(d['filename'])
        elif d.has_key('url'): self.test_web_import(d['url'])
        else: print 'WTF: no test contained in ',d
        if d.has_key('test'):
            self.do_test(d['test'])

    def do_test (self, test):
        recs = self.db.search_recipes(
            [{'column':'title',
             'search':test['title'],
             'operator':'=',
             }]
            )
        rec = recs[0]
        ings = self.db.get_ings(rec)
        if test.get('all_ings_have_amounts',False):
            for i in ings:
                assert(i.amount)
        if test.get('all_ings_have_units',False):
            for i in ings:
                assert(i.unit)
                
    
    @time_me
    def setup_db (self):
        rm.dbargs['file']=tempfile.mktemp('.mk')
        self.db = rm.RecipeManager(**rm.dbargs)

    @time_me
    def test_import (self,filename):
        filt = importers.FILTER_INFO[importers.select_import_filter(filename)]
        impClass,args,kwargs = filt['import']({'file':filename,
                                               'rd':self.db,
                                               'threaded':True,
                                               'progress':self.progress
                                               })
        impInstance = impClass(*args,**kwargs)
        impInstance.run()

    @time_me
    def test_web_import (self, url):
        importers.html_importer.import_url(url,self.db,progress=self.progress,
                                           interactive=False)

    def progress (self, bar, msg):
        pass
        #print int(10 * bar) * '|'
        #if bar == 1: print msg
        

class ImportTestCase (unittest.TestCase):

    def setUp (self):
        print 'setUp'
        self.it = ImportTest()
        self.it.setup_db()

    def tearDown (self):
        print 'tearDown'
        from exporters.gxml2_exporter import rview_to_xml as gxml_exporter
        n = 1
        while os.path.exists('/tmp/gourmet_import_test_%s.grmt'%n): n+=1
        ge=gxml_exporter(self.it.db,self.it.db.fetch_all(self.it.db.rview),'/tmp/gourmet_import_test_%s.grmt'%n)
        ge.run()

    def testMastercookXML (self):
        self.it.run_test({'filename':'athenos1.mx2',
                          'test':{'title':'5 Layer Mediterranean Dip',
                                  'all_ings_have_amounts':True,
                                  'all_ings_have_units':True,
                                  }
                          })

    def testMealmaster (self):
        self.it.run_test({'filename':'mealmaster.mmf'}), # mealmaster

    def testKrecipes (self):
        self.it.run_test({'filename':'sample.kreml'}), #krecipes

    def testAllRecipes (self):
        self.it.run_test({'url':'http://beef.allrecipes.com/az/AsianBeefWithSnowPeas.asp'}), #allrecipes.com

    def testEatingWell (self):
        self.it.run_test(
            {'url':'http://www.eatingwell.com/articles_recipes/recipes/recipes_favorites/chocolate_zucchini_bread.htm'}
            ) #eatingwell

    def testFoodNetwork (self):
        self.it.run_test(
            {'url':'http://www.foodnetwork.com/food/recipes/recipe/0,1977,FOOD_9936_31916,00.html'}
            )


if __name__ == '__main__':
    import tempfile,os.path
    import hotshot, hotshot.stats    

    import gtk
    class ImportProfiler:

        def __init__ (self):
            
            self.w = gtk.Window()
            self.vb = gtk.VBox(); self.vb.show()
            pb = gtk.Button('Profile'); pb.show()
            pb.connect('clicked',self.run_profile)
            qb = gtk.Button(stock=gtk.STOCK_QUIT); qb.show()
            qb.connect('clicked',self.quit)
            self.vb.pack_start(pb)
            self.vb.pack_start(qb)
            self.w.connect('delete-event',self.quit)
            self.w.add(self.vb)
            self.w.show()

        def start (self):
            gtk.main()

        def quit (self, *args): gtk.main_quit()

        def run_profile (self, *args):
            it=ImportTest()
            it.setup_db()
            prof = hotshot.Profile(os.path.join(tempfile.tempdir,'GOURMET_IMPORTER_HOTSHOT_PROFILE'))
            prof.runcall(
                lambda *args: it.run_test({'filename':'/home/tom/Desktop/big_rec_archive/b1q97.txt'})
                )
            stats = hotshot.stats.load(os.path.join(tempfile.tempdir,'GOURMET_IMPORTER_HOTSHOT_PROFILE'))
            stats.strip_dirs()
            stats.sort_stats('time','calls')
            stats.print_stats()
            self.quit()

    ip = ImportProfiler()
    ip.start()
    #it.run_test({'filename':'mealmaster.mmf'}), # mealmaster
    #it.setup_db()
    #it.run_test({'filename':'athenos1.mx2',
    #                      'test':{'title':'5 Layer Mediterranean Dip',
    #                              'all_ings_have_amounts':True,
    #                              'all_ings_have_units':True,
    #                              }
    #                      })
    #it.run_test({'filename':'mealmaster.mmf'}), # mealmaster
    #it.run_test({'filename':'sample.kreml'}), #krecipes
    #it.run_test({'url':'http://beef.allrecipes.com/az/AsianBeefWithSnowPeas.asp'}), #allrecipes.com
    #it.run_test(
    #        {'url':'http://www.eatingwell.com/articles_recipes/recipes/recipes_favorites/chocolate_zucchini_bread.htm'}
    #        ) #eatingwell
    #from exporters.gxml2_exporter import rview_to_xml as gxml_exporter
    #n = 1
    #while os.path.exists('/tmp/gourmet_import_test_%s.grmt'%n): n+=1
    #ge=gxml_exporter(it.db,it.db.fetch_all(it.db.rview),'/tmp/gourmet_import_test_%s.grmt'%n)
    #ge.run()
    #unittest.main()
    #pass
