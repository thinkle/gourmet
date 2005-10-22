import recipeManager as rm
import time
import importers
import os,os.path
import importers.html_importer
import tempfile
import traceback

test_files = ['athenos1.gourmetcleaned.mx2', #mastercook
              'mealmaster.mmf', # mealmaster
              '200_Recipes.mmf', #mealmaster
              'sample.kreml', #krecipes
              ]

test_files = [os.path.join('/home/tom/Projects/recipe/Data',f) for f in test_files]
test_urls = [
    'http://beef.allrecipes.com/az/AsianBeefWithSnowPeas.asp', #allrecipes.com
    'http://www.eatingwell.com/articles_recipes/recipes/recipes_favorites/chocolate_zucchini_bread.htm', #eatingwell
    'http://www.foodnetwork.com/food/recipes/recipe/0,1977,FOOD_9936_31916,00.html', #foodnetwork
    ]

times = []
def time_me (f):
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
        self.db = self.setup_db()
        for f in test_files:
            try:
                self.test_import(f)
            except:
                print 'Failed to import file: ',f
                traceback.print_exc()
        for u in test_urls:
            try:
                self.test_web_import(u)
            except:
                print 'Failed to import url: ',u
                traceback.print_exc()

    @time_me
    def setup_db (self):
        rm.dbargs['file']=tempfile.mktemp('.mk')
        return rm.RecipeManager(**rm.dbargs)

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
        importers.html_importer.import_url(url,self.db,progress=self.progress)

    def progress (self, bar, msg):
        print int(10 * bar) * '|'
        if bar == 1: print msg
        

if __name__ == '__main__':
    it=ImportTest()
    it.run()
