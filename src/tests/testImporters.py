import test # Get our path set so we work...
import recipeManager as rm
import time
import importers
import os,os.path,re
import importers.html_importer
import tempfile
import traceback
import unittest

TEST_FILE_DIRECTORY = 'recipe_files'

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
                try:
                    assert(i.amount)
                except:
                    print i,i.amount,i.unit,i.item,'has no amount!'
                    raise
        if test.get('all_ings_have_units',False):
            for i in ings:
                try:
                    assert(i.unit)
                except:
                    print i,i.amount,i.unit,i.item,'has no unit'
                    raise
        for blobby_attribute in ['instructions','modifications']:
            if test.get(blobby_attribute,False):
                match_text = test[blobby_attribute]
                match_text = re.sub('\s+','\s+',match_text)
                try:
                    assert(re.match(match_text,getattr(rec,blobby_attribute)))
                except:
                    raise AssertionError('%s == %s != %s'%(blobby_attribute,
                                                           getattr(rec,blobby_attribute),
                                                           match_text)
                                         )
        for non_blobby_attribute in ['source','cuisine','preptime','cooktime']:
            if test.get(non_blobby_attribute,None) is not None:
                try: assert(getattr(rec,non_blobby_attribute)==test[non_blobby_attribute])
                except:
                    raise AssertionError('%s == %s != %s'%(non_blobby_attribute,
                                                           getattr(rec,non_blobby_attribute),
                                                           test[non_blobby_attribute])
                                         )
        if test.get('categories',None):
            cats = self.db.get_cats(rec)
            for c in test.get('categories'):
                try:
                    assert(c in cats)
                except:
                    raise AssertionError("Found no category %s, only %s"%(c,cats))
                cats.remove(c)
            try:
                assert(not cats)
            except:
                raise AssertionError('Categories include %s not specified in %s'%(cats,test['categories']))
    
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
        self.it.run_test({'filename':'mealmaster.mmf',
                          'test':{'title':'Almond Mushroom Pate',
                                  'categories':['Appetizers'],
                                  'servings':6,
                                  }
                          }) # mealmaster

    def testKrecipes (self):
        self.it.run_test({'filename':'sample.kreml',
                          'test':{
            'title':'Recipe title',
            'source':'Unai Garro, Jason Kivlighn',
            'categories':['Ethnic','Cakes'],
            'servings':5,
            'preptime':90*60,
            'instructions':'Write the recipe instructions here'
            }
                          }
                         ) #krecipes

    def testAllRecipes (self):
        self.it.run_test({'url':'http://beef.allrecipes.com/az/AsianBeefWithSnowPeas.asp',

                     'test':{'title':'Asian Beef with Snow Peas',
                             'all_ings_have_amounts':True,
                             'all_ings_have_units':True,
                             'source':'Holly (beef.allrecipes.com)',
                             'instructions':'''Stir-fried beef with snow peas in a light gingery sauce.
In a small bowl, combine the soy sauce, rice wine, brown sugar and cornstarch. Set aside.
Heat oil in a wok or skillet over medium high heat. Stir-fry ginger and garlic for 30 seconds. Add the steak and stir-fry for 2 minutes or until evenly browned. Add the snow peas and stir-fry for an additional 3 minutes. Add the soy sauce mixture, bring to a boil, stirring constantly. Lower heat and simmer until the sauce is thick and smooth. Serve immediately.
Retrieved from http://beef.allrecipes.com/az/AsianBeefWithSnowPeas.asp.''',
                          }
                          })#allrecipes.com

    def testEpicurious (self):
        self.it.run_test(
            {'url':'http://www.epicurious.com/recipes/recipe_views/views/106711'}
            ) #eatingwell

    def testFoodNetwork (self):
        self.it.run_test(
            {'url':'http://www.foodnetwork.com/food/recipes/recipe/0,1977,FOOD_9936_31916,00.html'}
            )


if __name__ == '__main__':
    PROFILE = False

    if PROFILE:

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
                    lambda *args: it.run_test({'filename':os.path.join(TEST_FILE_DIRECTORY,'b1q97.txt')})
                    )
                stats = hotshot.stats.load(os.path.join(tempfile.tempdir,'GOURMET_IMPORTER_HOTSHOT_PROFILE'))
                stats.strip_dirs()
                stats.sort_stats('time','calls')
                stats.print_stats()
                self.quit()

        ip = ImportProfiler()
        ip.start()
    else:
        unittest.main()
    #pass
    
