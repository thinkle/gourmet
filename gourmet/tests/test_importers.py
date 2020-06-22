import time
import os,os.path,re
import unittest
from ..importers.importManager import ImportManager, ImportFileList
from ..recipeManager import get_recipe_manager

TEST_FILE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'recipe_files')

times = []
def time_me (f):
    def _ (*args, **kwargs):
        start = time.time()
        ret = f(*args,**kwargs)
        end = time.time()
        times.append(
            ((f.__name__,args,kwargs),end-start)
            )
        return ret
    return f

def old_time_me (f):
    def _ (*args,**kwargs):
        print('Running',f.__name__,args,kwargs)
        start = time.time()
        try:
            ret = f(*args,**kwargs)
        except:
            end = time.time()
            times.append((f.__name__,args,kwargs,start,end,end-start))
            print('Failed after ',end-start,'seconds.')
            raise
        else:
            end = time.time()
            times.append((f.__name__,args,kwargs,start,end,end-start))
            print('Finished in ',end-start,'seconds.')
            return ret
    return _

class ThreadlessImportManager (ImportManager):

    def get_app_and_prefs (self):
        self.prefs = {}

    def do_import (self, importer_plugin, method, *method_args):
        # No threading, for profiling purposes!
        try:
            importer = getattr(importer_plugin,method)(*method_args)
        except ImportFileList as ifl:
            # recurse with new filelist...
            self.import_filenames(ifl.filelist)
        else:
            if hasattr(importer,'pre_run'):
                importer.pre_run()
            importer.run()
            self.follow_up(None,importer)


class ImportTest:

    #failures = []
    __count = 1

    def run (self, tests):
        for d in tests: self.run_test(d)

    def run_test (self, d):
        if 'filename' in d:
            d['filename']=os.path.join(TEST_FILE_DIRECTORY,
                                       d['filename'])
            self.test_import(d['filename'])
        elif 'url' in d:
            self.test_web_import(d['url'])
        else:
            print('WTF: no test contained in ',d)
        if 'test' in d:
            self.do_test(d['test'])

    def do_test (self, test):
        recs = self.db.search_recipes(
            [
                {'column':'deleted',
                 'search':False,
                 'operator':'='},
                {'column':'title',
                 'search':test['title'],
                 'operator':'=',
                 }
             ]
            )
        if not recs:
            raise AssertionError(
                'No recipe found with title "%s".'%test['title']
                )
        rec = recs[0]
        ings = self.db.get_ings(rec)
        if test.get('all_ings_have_amounts',False):
            for i in ings:
                try:
                    assert(i.amount)
                except:
                    print(i,i.amount,i.unit,i.item,'has no amount!')
                    raise
        if test.get('all_ings_have_units',False):
            for i in ings:
                try:
                    assert(i.unit)
                except:
                    print(i,i.amount,i.unit,i.item,'has no unit')
                    raise
        for blobby_attribute in ['instructions','modifications']:
            if test.get(blobby_attribute,False):
                match_text = test[blobby_attribute]
                match_text = re.sub(r'\s+',r'\s+',match_text)
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
        print('Passed test:',test)

    @time_me
    def setup_db (self):
        self.im = ThreadlessImportManager.instance()
        self.db = get_recipe_manager(custom_url='sqlite:///:memory:')

    @time_me
    def test_import (self,filename):
        self.im.import_filenames([filename])

    @time_me
    def test_web_import (self, url):
        self.im.import_url(url)

    def progress (self, bar, msg):
        pass
        #print int(10 * bar) * '|'
        #if bar == 1: print msg


class ImportTestCase (unittest.TestCase):

    def setUp (self):
        print('setUp')
        self.it = ImportTest()
        self.it.setup_db()

    def tearDown (self):
        print('tearDown')
        from gourmet.plugins.import_export.gxml_plugin.gxml2_exporter import recipe_table_to_xml as gxml_exporter
        n = 1
        while os.path.exists('/tmp/gourmet_import_test_%s.grmt'%n): n+=1
        print('Saving export of imported files to /tmp/gourmet_import_test_%s.grmt'%n)
        ge=gxml_exporter(self.it.db,self.it.db.fetch_all(self.it.db.recipe_table,deleted=False),'/tmp/gourmet_import_test_%s.grmt'%n)
        ge.run()
        # Trash all our recipes so they don't contaminate the next test...
        self.it.db.recipe_table.update().execute({'deleted':True}) #; self.it.db.db.commit()

#    def testArchive (self):
#        self.it.run_test({
#                'filename' : 'mealmaster_recs.zip',
#                'test' : {'title':'Almond Mushroom Pate'},
#                }
#                         )
#        self.it.run_test({
#                'filename' : 'recipes.tar.bz2',
#                }
#                         )

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

    # AllRecipes import is broken as of 1/2/07
    #def testAllRecipes (self):
    #    self.it.run_test({'url':'http://allrecipes.com/recipe/asian-beef-with-snow-peas/',
    #
    #                 'test':{'title':'Asian Beef with Snow Peas',
    #                         'all_ings_have_amounts':True,
    #                         'all_ings_have_units':True,
    #                         'source':'Holly (beef.allrecipes.com)',
    #                         'instructions':'''Stir-fried beef with snow peas in a light gingery sauce.
    # In a small bowl, combine the soy sauce, rice wine, brown sugar and cornstarch. Set aside.
    # Heat oil in a wok or skillet over medium high heat. Stir-fry ginger and garlic for 30 seconds. Add the steak and stir-fry for 2 minutes or until evenly browned. Add the snow peas and stir-fry for an additional 3 minutes. Add the soy sauce mixture, bring to a boil, stirring constantly. Lower heat and simmer until the sauce is thick and smooth. Serve immediately.
    #Retrieved from http://beef.allrecipes.com/az/AsianBeefWithSnowPeas.asp.''',
    #}
    #                          })#allrecipes.com

    #def testEpicurious (self):
    #     self.it.run_test(
    #       {'url':'http://www.epicurious.com/recipes/recipe_views/views/106711'}
    #        ) #eatingwell

    #def testFoodNetwork (self):
    #     self.it.run_test(
    #        {'url':'http://www.foodnetwork.com/food/recipes/recipe/0,1977,FOOD_9936_31916,00.html'}
    #       )


if __name__ == '__main__':
    unittest.main()

