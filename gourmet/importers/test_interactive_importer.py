import unittest
import interactive_importer

class TestConvenientImporter (unittest.TestCase):

    def setUp (self):
        self.ci = interactive_importer.ConvenientImporter()

    def testImport (self):
        self.ci.start_rec()
        self.ci.add_attribute('title','Test')
        self.ci.add_attribute('category','foo')
        self.ci.add_attribute('category','bar')
        self.ci.add_ings_from_text(
            '''6 garlic cloves, peeled 
  1/2 pound linguine 
  1/4 cup plus 1 tablespoon olive oil 
  2 to 2 1/2 pounds small fresh squid (about 10), cleaned and cut into 3/4-inch thick rings, tentacles cut in half* 
  1 1/2 teaspoons Baby Bam or Emeril's Original Essence, to taste 
  1/4 cup chopped green onions 
  1 teaspoon crushed red pepper, or to taste 
  1/4 teaspoon salt 
  1/4 cup fish stock, shrimp stock, or water 
  2 tablespoons fresh lemon juice 
  1 tablespoon unsalted butter 
  1/4 cup chopped fresh parsley leaves 
  1/2 cup freshly grated Parmesan'''
            )
        self.ci.commit_rec()
        rec = self.ci.added_recs[-1]
        self.assertEqual(rec.title,'Test')
        cats = rec.categories
        cats.sort()
        self.assertEqual(len(cats),2)
        self.assertEqual(cats[0],'bar')
        self.assertEqual(cats[1],'foo')
        ings = self.ci.rd.get_ings(rec)
        self.assertEqual(len(ings),13)
        self.assertEqual(ings[1].amount,0.5)
        self.assertEqual(ings[1].unit,'pound')
        self.assertEqual(ings[1].item,'linguine')                

if __name__ == '__main__':
    unittest.main()
