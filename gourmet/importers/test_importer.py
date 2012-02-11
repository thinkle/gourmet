import unittest
import importer

class TestImporter (unittest.TestCase):

    def setUp (self):
        self.i = importer.Importer()

    def _get_last_rec_ (self):
        return self.i.added_recs[-1] 

    def testRecImport (self):
        self.i.start_rec()
        attrs = [('title','Foo'),('cuisine','Bar'),('yields',3),('yield_unit','cups')]
        for att,val in attrs:
            self.i.rec[att] = val
        self.i.commit_rec()
        rec = self._get_last_rec_()
        for att,val in attrs:
            self.assertEqual(getattr(rec,att),val)
    
    def testIngredientImport (self):
        self.i.start_rec()
        self.i.rec['title']='Ingredient Import Test'
        self.i.start_ing()
        self.i.add_amt(2)
        self.i.add_unit('cups')
        self.i.add_item(u'water')
        self.i.commit_ing()
        self.i.commit_rec()
        ings = self.i.rd.get_ings(self._get_last_rec_())
        self.assertEqual(len(ings),1)
        ing = ings[0]
        self.assertEqual(ing.amount,2)
        self.assertEqual(ing.unit,'cups')
        self.assertEqual(ing.item,'water')

if __name__ == '__main__':
    unittest.main()
