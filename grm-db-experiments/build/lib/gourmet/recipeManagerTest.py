import unittest
import tempfile
import recipeManager

class dbTest (unittest.TestCase):
    def setUp (self):
        recipeManager.dbargs['file']=tempfile.mktemp('.mk')
        self.db = recipeManager.RecipeManager(**recipeManager.dbargs)

    def tearDown (self):
        pass

