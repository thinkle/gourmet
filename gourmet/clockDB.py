import recipeManager as rm
import time, random, tempfile

class StressTester:

    times = []

    CUISINES = ['Indian','American','Spanish','Italian','Polish']
    INGS = ['Chicken','Beef','Broccoli','Tofu','Shrimp']
    SOURCES = ['Sue','Sally',
               'Jon','Meg',
               'Tom','Judy',
               'Martha','Steve',
               'Fred','Priscilla']

    def time_method (fun):
        name = fun.__name__
        def _ (self,*args, **kwargs):
            t = time.time()
            ret = fun(self,*args,**kwargs)
            total = time.time() - t
            self.times.append((name,total))
            return ret
        return _

    def __init__ (self):
        rm.dbargs['file']=tempfile.mktemp('test.db')
        self.db = rm.RecipeManager(**rm.dbargs)

    def run_tests (self):
        for n in range(3):
            print 'Start',(n+1),'*1000','recipes'
            self.add_1000_recipes()
            print 'fetching'
            self.test_fetch_recipe()
            print 'exact searches'
            self.test_exact_search()
            print 'regexp searches'
            self.test_regexp_search()
            print 'ing search'
            self.test_ing_search()
            #print 'like searches'            
            #self.test_like_search()            
            print 'committing...'
            self.commit_recs()
        print 'Done running tests!'
        print
        print 'Method\t\tTime'
        print '------\t\t----'
        for t in self.times:
            print t[0],"\t\t",t[1]

    @time_method
    def commit_recs (self):
        self.db.save()

    @time_method
    def add_1000_recipes (self):
        count = 0
        t = time.time()
        # 4 * 
        for cat in ['Dessert','Entree','Salad','Appetizer']:
            # 5 = 20
            for cuisine in self.CUISINES:
                # * 5 = 100
                for main_ing in self.INGS:
                    # * 10 = 1000
                    for source in self.SOURCES:
                        r = self.db.add_rec(
                            {'title':"%(source)s's %(cuisine)s %(main_ing)s %(cat)s"%locals(),
                             'category':cat,
                             'cuisine':cuisine,
                             'source':source,
                             'preptime':60*random.randint(5,240),
                             'cooktime':60*random.randint(10,90),
                             'instructions':'This is a long long description of how you cook'*25,
                             'modifications':'These are some funny notes.'*5,
                             })
                        self.db.add_ing({'id':r.id,'unit':'piece','item':main_ing,'ingkey':main_ing})
                        for n in range(3):
                            for u in ['tsp.','c.','lb.','oz.']:
                                self.db.add_ing(
                                    {'id':r.id,
                                     'unit':u,
                                     'item':'Item number %s'%n,
                                     'ingkey':'ingredient, %s'%n,
                                     }
                                    )
                        count += 1
                        if count % 100 == 0:
                            print "At ",count,"recipes.",time.time()-t,'seconds'

    def search (self,operator):
        for cuisine in random.sample(self.CUISINES,2):
            self.db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                    {'column':'cuisine','search':cuisine,'operator':operator},
                                    ])
            for source in random.sample(self.SOURCES,2):
                self.db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                        {'column':'cuisine','search':cuisine,'operator':operator},
                                        {'column':'source','search':cuisine,'operator':operator},
                                        ])

    @time_method
    def test_ing_search (self):
        for ing in random.sample(self.INGS,2):
            srch = ''
            for ltr in ing[0:4]:
                srch += ltr
                self.db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                        {'column':'ingredient',
                                         'search':srch+'%',
                                         'operator':'LIKE'}]
                                       )

    @time_method
    def test_exact_search (self): self.search('=')

    @time_method
    def test_regexp_search (self): self.search('regexp')

    @time_method
    def test_like_search (self): self.search('LIKE')

    @time_method
    def test_fetch_recipe (self,min=0,max=10):
        for r in range(100):
            recipe = self.db.fetch_all(self.db.recipe_table)[random.randint(min,max)]
            for prop in ['title','cuisine','source',
                         'preptime','cooktime','instructions',
                         'modifications']:
                getattr(recipe,prop)
            self.db.get_cats(recipe)
            for i in recipe.ingredients:
                getattr(i,'amount')
                getattr(i,'rangeamount')
                getattr(i,'unit')
                getattr(i,'item')
                getattr(i,'optional')
                getattr(i,'ingkey')

if __name__ == '__main__':
    st = StressTester()
    st.run_tests()
