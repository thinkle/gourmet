from testImporters import ImportTest
import unittest
import profile, tempfile, os.path

#class profileTest (ImportTestCase):
#    #def run (self,*args,**kwargs):
#    #    profile.run('ImportTestCase.run(self,*args,**kwargs)')

it = ImportTest()
print('Setting up DB')
it.setup_db()
print('Profiling gourmet importer')
profi = os.path.join(tempfile.tempdir,'GOURMET_PROFILE')
profile.run("""it.run_test({'filename':'/home/tom/Desktop/Junk/recipes.grmt'})""",profi)
#profile.run("""it.run_test({'filename':'/home/tom/Projects/recipe/Data/mealmaster.mmf'})""",profi)
import pstats
p = pstats.Stats(profi)
p.strip_dirs().sort_stats('cumulative').print_stats()

