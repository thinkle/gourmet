import re
from pathlib import Path

from gourmet.importers.importManager import ImportFileList, ImportManager
from gourmet.plugins.import_export.mastercook_import_plugin.mastercook_plaintext_importer import Tester as MCTester  # noqa
from gourmet.recipeManager import RecipeManager

TEST_FILE_DIRECTORY = Path(__file__).parent / 'recipe_files'


class ThreadlessImportManager(ImportManager):
    def get_app_and_prefs(self):
        self.prefs = {}

    def do_import(self, importer_plugin, method, *method_args):
        # No threading, for profiling purposes!
        try:
            importer = getattr(importer_plugin, method)(*method_args)
        except ImportFileList as ifl:
            # recurse with new filelist...
            self.import_filenames(ifl.filelist)
        else:
            if hasattr(importer, 'pre_run'):
                importer.pre_run()
            importer.run()
            self.follow_up(None, importer)


class ImportTest:
    def __init__(self):
        self.im = ThreadlessImportManager.instance()
        self.db = RecipeManager.instance_for()

    def run_test(self, d):
        filename = str(TEST_FILE_DIRECTORY / d['filename'])
        self.im.import_filenames([filename])
        self.do_test(d['test'])

    def do_test(self, test):
        recs = self.db.search_recipes([{'column': 'deleted',
                                        'search': False,
                                        'operator': '='},
                                       {'column': 'title',
                                        'search': test['title'],
                                        'operator': '='}])
        if not recs:
            raise AssertionError(
                'No recipe found with title "%s".' % test['title']
            )
        rec = recs[0]
        ings = self.db.get_ings(rec)
        if test.get('all_ings_have_amounts', False):
            for i in ings:
                try:
                    assert (i.amount)
                except:
                    print(i, i.amount, i.unit, i.item, 'has no amount!')
                    raise
        if test.get('all_ings_have_units', False):
            for i in ings:
                try:
                    assert (i.unit)
                except:
                    print(i, i.amount, i.unit, i.item, 'has no unit')
                    raise
        for blobby_attribute in ['instructions', 'modifications']:
            if test.get(blobby_attribute, False):
                match_text = test[blobby_attribute]

                try:
                    assert (
                        re.match(match_text, getattr(rec, blobby_attribute)))
                except:
                    raise AssertionError('%s == %s != %s' % (blobby_attribute,
                                                             getattr(
                                                                 rec,
                                                                 blobby_attribute),
                                                             match_text)
                                         )
        for non_blobby_attribute in ['source', 'cuisine', 'preptime',
                                     'cooktime']:
            if test.get(non_blobby_attribute, None) is not None:
                try:
                    assert (getattr(rec, non_blobby_attribute)
                            == test[non_blobby_attribute])
                except:
                    raise AssertionError(
                        '%s == %s != %s' % (non_blobby_attribute,
                                            getattr(
                                                rec, non_blobby_attribute),
                                            test[non_blobby_attribute])
                        )
        if test.get('categories', None):
            cats = self.db.get_cats(rec)
            for c in test.get('categories'):
                try:
                    assert (c in cats)
                except:
                    raise AssertionError(
                        "Found no category %s, only %s" % (c, cats))
                cats.remove(c)
            try:
                assert (not cats)
            except:
                raise AssertionError(
                    'Categories include %s not specified in %s' % (
                    cats, test['categories']))
        print('Passed test:', test)


    def progress(self, bar, msg):
        pass


it = ImportTest()


def test_mastercook():
    it.run_test({'filename': 'athenos1.mx2',
                 'test': {'title': '5 Layer Mediterranean Dip',
                          'all_ings_have_amounts': True,
                          'all_ings_have_units': True,
                          }
                 })


def test_mealmaster():
    it.run_test({'filename': 'mealmaster.mmf',
                 'test': {'title': 'Almond Mushroom Pate',
                          'categories': ['Appetizers'],
                          'servings': 6,
                          }
                 })


def test_krecipes():
    it.run_test({'filename': 'sample.kreml',
                 'test': {
                     'title': 'Recipe title',
                     'source': 'Unai Garro, Jason Kivlighn',
                     'categories': ['Ethnic', 'Cakes'],
                     'servings': 5,
                     'preptime': 90 * 60,
                     'instructions': 'Write the recipe instructions here'
                 }
                 }
                )


def test_mycookbook():
    it.run_test({'filename': 'mycookbook.mcb',
                 'test': {
                     'title': 'Best Brownies',
                     'link': 'https://www.allrecipes.com/recipe/10549/best-brownies/',  # noqa
                    }
                 })


def test_mastercook_file_tester():
    filename = TEST_FILE_DIRECTORY / 'mastercook_text_export.mxp'
    tester = MCTester()
    assert tester.test(filename)
