# -*- coding: utf-8 -*-
import unittest
import tempfile
import os
import gourmet.gglobals
tmpdir = tempfile.mktemp()
os.makedirs(tmpdir)
gourmet.gglobals.gourmetdir = tmpdir  # TODO: replace deprecated mktemp()
from gourmet.GourmetRecipeManager import get_application, GourmetApplication
from gourmet.backends import db
db.RecData.__single = None
GourmetApplication.__single = None
from gourmet.exporters import exportManager

class SampleRecipeSetterUpper:

    __single = None

    recipes = {
        'simple recipe' : {
            'recipe' : {'title':'Simple Test','cuisine':'Indian','instructions':'Cook as usual','modifications':'Unless you want to get fancy',
                        'preptime':3600,'cooktime':11239},
            'categories':['Healthy','Bread'],
            'ingredients':[
                {'amount':1,'unit':'cup','item':'water','ingkey':'water, municipal'},
                {'amount':2,'unit':'cups','item':'atta flour','ingkey':'flour, atta (whole wheat)'},
                {'amount':2,'unit':'Tbs','item':'salt','ingkey':'salt, table'},
                {'amount':1,'unit':'tsp','item':'black pepper','ingkey':'pepper, black', 'optional':True},
                ],
            },
        'unicode': {
            'recipe' : {'title':u'¡Jalapeño extravaganza!','yields':3,'yield_unit':'cups'},
            'categories': ['Spicy','Healthy'],
            'ingredients':[
                {'amount':1,'unit':'cup','item':'water','ingkey':'water, municipal'},
                {'amount':1,'unit':'lb','item':u'jalapeño','ingkey':'pepper, habañero'},
                {'amount':2,'unit':u'más','item':u'habañeros','ingkey':u'pepper, habañero'},
                ]
            },
        'formatting': {
            'recipe' : {
                'title':u'Recipe with formatting',
                'instructions':u'''These are my <i>instructions</i> I would like to <b>see</b> what you <u>think</u> of them.

<span color="red">Aren\'t these pretty nifty?</span>''',
                'modifications':u'''These are my <i>notes</i> I would like to <b>see</b> what you <u>think</u> of them.

<span color="blue">Aren\'t these pretty nifty?</span>''',
                },
            'ingredients':[
                {'amount':1,'unit':'cup','item':'water','ingkey':'water, municipal'},
                {'amount':1,'unit':'lb','item':u'jalapeño','ingkey':'pepper, habañero'},
                {'amount':2,'unit':u'más','item':u'habañeros','ingkey':u'pepper, habañero'},
                ]
            },


        }

    def __init__ (self):
        print 'Instantiate SampleRecipeSetterUpper',self
        if SampleRecipeSetterUpper.__single: raise SampleRecipeSetterUpper.__single
        else: SampleRecipeSetterUpper.__single = self
        self.db = db.get_database()
        for rec in self.recipes:
            self.add_rec(self.recipes[rec])

    def add_rec (self, recdic):
        recdic['recipe']['deleted']=False
        r = self.db.add_rec(recdic['recipe'])
        recid = r.id; print 'added rec',r.id
        recdic['recipe_id'] = r.id
        if recdic.has_key('categories'):
            for c in recdic['categories']:
                print 'add categories',c
                self.db.do_add_cat({'recipe_id':recid,'category':c})
        if recdic.has_key('ingredients'):
            print 'Add ingredients...'
            for i in recdic['ingredients']:
                i['recipe_id'] = recid; i['deleted']=False
                print i
            self.db.add_ings(recdic['ingredients'])
        print 'done add_rec\n-------'
        rec = self.db.get_rec(recdic['recipe_id']); print rec
        print self.db.get_cats(rec)
        print self.db.get_ings(rec)
        print '^^^^^^^^^^^^^^^^^^^^'

def setup_sample_recs ():
    try:
        return SampleRecipeSetterUpper()
    except SampleRecipeSetterUpper, srsu:
        print 'Returning single...'
        return srsu

class TestSetterUpper (unittest.TestCase):
    def setUp (self):
        setup_sample_recs()

    def testSetup(self):
        # GourmetApplication.__single = None
        app = get_application()
        app.window.show()
        import gtk
        gtk.main()

class TestExports (unittest.TestCase):
    def setUp (self):
        self.sample_recs = setup_sample_recs()
        self.recs = self.sample_recs.recipes
        self.em = exportManager.get_export_manager()
        self.db = db.get_database()

    def testMultipleExporters (self):

        def fail_on_fail (thread, errorval, errortext, tb):
            self.failUnless(False,errortext+'\n\n'+tb)

        for format,plugin in self.em.plugins_by_name.items():
            filters = plugin.saveas_filters
            ext = filters[-1][-1].strip('*.')
            exceptions = []
            recs =   [self.db.get_rec(self.recs['simple recipe']['recipe_id']),
                      self.db.get_rec(self.recs['unicode']['recipe_id']),
                      self.db.get_rec(self.recs['formatting']['recipe_id']),
                      ]
            plugin,exporter = self.em.get_multiple_exporter(recs,'/tmp/All.'+ext,format,
                                                   extra_prefs=exportManager.EXTRA_PREFS_DEFAULT)
            exporter.connect('error', fail_on_fail)
            done = False
            def done (*args):
                done = True
            exporter.connect('done',done)
            exporter.do_run()


    def testSingleExport (self):
        for format,plugin in self.em.plugins_by_name.items():
            filters = plugin.saveas_single_filters
            ext = filters[-1][-1].strip('*.')
            for rec, f in [(self.db.get_rec(self.recs['simple recipe']['recipe_id']),'/tmp/Simple.'+ext),
                           (self.db.get_rec(self.recs['unicode']['recipe_id']),'/tmp/Uni.'+ext),
                           (self.db.get_rec(self.recs['formatting']['recipe_id']),'/tmp/Formatted.'+ext),
                           ]:
                self.em.do_single_export(rec,f,format,
                                         extra_prefs=exportManager.EXTRA_PREFS_DEFAULT)
                if hasattr(plugin,'check_export'):
                    print 'Checking export for ',plugin,rec,f
                    fi = open(f,'r')
                    try:
                        plugin.check_export(rec,fi)
                    except:
                        import traceback
                        self.assertEqual(1,2,'Exporter test for %s on file %s raised error %s'%(
                            plugin,f,traceback.format_exc()
                            )
                                          )
                    finally:
                        fi.close()

if __name__ == '__main__':
    unittest.main()
