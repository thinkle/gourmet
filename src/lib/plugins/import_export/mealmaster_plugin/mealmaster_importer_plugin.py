import mealmaster_importer
from gourmet.plugin import ImporterPlugin
from gourmet.importers.importer import Tester
from gourmet.threadManager import get_thread_manager

class MealmasterImporterPlugin (ImporterPlugin):

    get_source = 'source'
    name = _('MealMaster file')
    patterns = ['*.mmf','*.txt']
    mimetypes = ['text/mealmaster','text/plain']

    def test_file (self, filename):
        '''Given a filename, test whether the file is of this type.'''
        Tester(mealmaster_importer.mm_start_pattern).test(filename)

    def get_importer (self, filename):
        return mealmaster_importer.mmf_importer(filename=filename)
                                                   


    
