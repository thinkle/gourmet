def test_rec_basics (db):
    rec = db.add_rec({'title':'Fooboo'})
    assert(rec.title=='Fooboo')
    rec2 = db.new_rec()
    rec2 = db.modify_rec(rec,{'title':'Foo','cuisine':'Bar'})
    assert(rec2.title=='Foo')
    assert(rec2.cuisine=='Bar')
    db.delete_rec(rec)
    db.delete_rec(rec2)    

def test_ing_basics (db):
    rid = db.new_rec().id
    ing = db.add_ing({'amount':1,
                      'unit':'c.',
                      'item':'Carrot juice',
                      'ingkey':'juice, carrot',
                      'recipe_id':rid
                      })
    ing2 = db.add_ing({'amount':2,
                       'unit':'c.',
                      'item':'Tomato juice',
                      'ingkey':'juice, tomato',
                      'recipe_id':rid
                       })
    assert(len(db.get_ings(rid))==2)
    ing = db.modify_ing(ing,{'amount':2})
    assert(ing.amount==2)
    ing = db.modify_ing(ing,{'unit':'cup'})    
    assert(ing.unit=='cup')
    db.delete_ing(ing)
    db.delete_ing(ing2)

def test_unique (db):
    db.delete_by_criteria(db.ingredients_table,{}) # Clear out ingredients
    for i in ['juice, tomato',
              'broccoli',
              'spinach',
              'spinach',
              'spinach',]:
        db.add_ing({'amount':1,'unit':'c.','item':i,'ingkey':i})
    vv=db.get_unique_values('ingkey',db.ingredients_table)
    assert(len(vv)==3)
    cvw = db.fetch_count(db.ingredients_table,'ingkey',ingkey='spinach',sort_by=[('count',-1)])
    assert(cvw[0].count==3)    
    assert(cvw[0].ingkey=='spinach')

def test_search (db):
    db.delete_by_criteria(db.ingredients_table,{}) # Clear out ingredients
    db.delete_by_criteria(db.recipe_table,{}) # Clear out recipes
    db.delete_by_criteria(db.categories_table,{}) # Clear out categories        
    db.add_rec({'title':'Foo','cuisine':'Bar','source':'Z'})
    db.add_rec({'title':'Fooey','cuisine':'Bar','source':'Y'})
    db.add_rec({'title':'Fooey','cuisine':'Foo','source':'X'})
    db.add_rec({'title':'Foo','cuisine':'Foo','source':'A'})
    db.add_rec({'title':'Boe','cuisine':'Fa'})
    result = db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                {'column':'cuisine','search':'Foo','operator':'='}])
    assert(len(result)==2)
    result = db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                {'column':'cuisine','search':'F.*','operator':'REGEXP'}])

    assert(len(result)==3)
    result = db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                {'column':'cuisine','search':'Foo'},
                                {'column':'title','search':'Foo','operator':'='},])
    assert(len(result)==1)
    result = db.search_recipes([{'column':'title','search':'Fo.*','operator':'REGEXP'}],
                               [('source',1)])
    assert(result[0].title=='Foo' and result[0].source=='A')
    # Advanced searching
    db.add_rec({'title':'Spaghetti','category':'Entree'})
    db.add_rec({'title':'Quiche','category':'Entree, Low-Fat, High-Carb'})
    assert(len(db.search_recipes([
        {'column':'deleted','search':False,'operator':'='},
        {'column':'category','search':'Entree','operator':'='}]))==2)
    # Test fancy multi-category searches...
    assert(len(db.search_recipes([{'column':'category','search':'Entree','operator':'='},
                                  {'column':'category','search':'Low-Fat','operator':'='}])
               )==1)
    # Test ingredient search
    recs = db.fetch_all(db.recipe_table)
    r = recs[0]
    db.add_ing({'recipe_id':r.id,'ingkey':'apple'})
    db.add_ing({'recipe_id':r.id,'ingkey':'cinnamon'})
    db.add_ing({'recipe_id':r.id,'ingkey':'sugar, brown'})
    r2 = recs[1]
    db.add_ing({'recipe_id':r2.id,'ingkey':'sugar, brown'})
    db.add_ing({'recipe_id':r2.id,'ingkey':'flour, all-purpose'})
    db.add_ing({'recipe_id':r2.id,'ingkey':'sugar, white'})
    db.add_ing({'recipe_id':r2.id,'ingkey':'vanilla extract'})
    r3 = recs[2]
    db.add_ing({'recipe_id':r3.id,'ingkey':'sugar, brown'})
    db.add_ing({'recipe_id':r3.id,'ingkey':'sugar, brown','unit':3,'unit':'c.'} )
    assert(len(db.search_recipes([{'column':'ingredient',
                                   'search':'sugar%',
                                   'operator':'LIKE',
                                  }])
               )==3)
    assert(len(db.search_recipes([{'column':'ingredient',
                                  'search':'sugar, brown'},
                                 {'column':'ingredient',
                                  'search':'apple'}])
               )==1)
    
def test_unicode (db):
    rec = db.add_rec({'title':u'Comida de \xc1guila',
                'source':u'C\xc6SAR',})
    assert(rec.title == u'Comida de \xc1guila')
    assert(rec.source == u'C\xc6SAR')

def test_id_reservation (db):
    rid = db.new_id()
    rid2 = db.new_id()
    r1 = db.add_rec({'title':'intermittent'})
    r1i = db.add_rec({'title':'intermittent2'})
    r12 = db.add_rec({'title':'intermittent3'})    
    r2 = db.add_rec({'title':'reserved','id':rid})
    r3 = db.add_rec({'title':'reserved2','id':rid2})
    try: assert(r2.id==rid)
    except:
        print 'reserved ID',rid
        print 'fetched ID',r2.id
        print 'intermittent ID',r1.id
        raise
    for r in [r1,r1i,r12,r2,r3]: db.delete_rec(r)

img='\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00(\x00#\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xf5\x01#r\xc0\x1c\x01\x92q\xd0S\x9a\xea+x\x1a{\xa9\x92(\x82\x16R\xc7n\xefl\x9e+\x07\xc6z\xf0\xd3$\x16p\xa4A\xf2\xb2d\xb1S\x8eq\xfc\'=\xff\x00:\xcf\x9a\xf7Q\xf1O\x85\x9eDB\xa9\x14\xdbJ\xc7\xceO\xe4\x0f\x7f\xd6\xaeUU\xb4*4\x9bj\xfb\x1d5\x9e\xadk}m\xba\x19\xe3\x92U8a\x1b\x02\x05`k\xfe\'m1\x84\x0bl\x1d\x87F.F>\xb8\xebShKi\xa0\xe9-4\xf8I\xe7E\r\xba,\x98\xd8\x03\x81\x8c\xe4\xf5\xcf^A\x14\x96\x97:>\xb5rl\xae\x00\xbd\x91\x8b"\xbbB\xcaz\xfd\xe1\xe9\xeb\xc1\x1c}1I\xc9\xc9+n5\x15\x17\xaa\xba,\xe9\xda\xb5\xd6\xa3a\r\xdb\xa2\xabH2F\x07c\x8f\xe9Etp\xd9\xc1o\x04p\xc5\x10\x11\xc6\xa1T{\n+U-52v\xbe\x86\x0f\x8c\xbc2\xfa\xcc\x90\xdc@3 \xc4dd\x0f\xa7\xf3\xadm\x13H\x87C\xd2\xa2\xb2\x1f31\xdc\xe4\x0e\x0b\x1cg\xf9\x01Z\x8e\xe7#\x18\x1e\xe6\xa2\xbb\xbb\x8a\xd9Y\x9d\x86\xc03\x9a\xc9E\'r\xdc\xdb\x8f)\xc6\xfcF\xd3e\xb9\xb3\x82\xea0\xc7h*v\xfey\xff\x00>\x95\x93\xf0\xfbIxo\x1e\xfex\xdbj\x02\xa8I\xfe#\xd7\xf4\xcf\xe7]\xcc\x97\xd1\xdd\xda\xc8\x8a\x98S\xf2\xe5\xfe\\\xfd;\xf1\x8c\xfe\x1d\xba\xd3\x86AX\xc4,\x15F7\xed\x00\x13\xdf\x8c\xf1\xcei{?{\x98~\xd3\xdc\xe5,1%\x89\x07\x03\xd0QF(\xadL\xc9\xd9\xc6*\xa5\xec"x\n\xed\xdcr\x1b\x1e\xb84QR\x80\xa0\xc8\xb3C\xf6i"|0\xc6\x0eG\x1f^\xb9\xabS\\}\x968`p\xca\xa3\x01X\xe4\x8f\xc4\xff\x00\x8d\x14U\x89\n\xf7r+m\x8ebT\x01\x8c-\x14QH\x0f\xff\xd9'

def test_data (db):
    r = db.add_rec({'image':img})
    assert(r.img == img)

def test_update (db):
    r = db.add_rec({'title':'Foo','cuisine':'Bar','source':'Z'})
    db.update_by_criteria(db.recipe_table,{'title':'Foo'},{'title':'Boo'})
    assert(db.get_rec(r.id).title == 'Boo')

def test_nut (db):
    db = RecData()
    db.fetch_join(db.nutritionaliases_table,db.nutrition_table,'ndbno','ndbno',sort_by=[('ingkey',1)])
    
def test_db (db):
    tests = [test_rec_basics,
             test_ing_basics,
             test_unique,
             test_search,
             test_unicode,
             test_id_reservation,
             test_update,
             test_nut,
             ]
    success = 0
    for t in tests:
        print t.__name__
        try:
            t(db)
            print 'Passed'
            success += 1
        except:
            print 'Failed'
            import traceback; traceback.print_exc()
    print 'Completed ',len(tests),'tests'
    print 'Passed',"%s/%s"%(success,len(tests)),'tests'
