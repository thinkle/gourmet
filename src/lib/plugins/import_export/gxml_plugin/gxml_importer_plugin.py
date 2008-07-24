from gourmet.plugin import ImporterPlugin
from gourmet.importers.importer import Tester
from gourmet.threadManager import get_thread_manager
import gxml2_importer, gxml_importer

class GourmetXML2Plugin (ImporterPlugin):

    name = _('Gourmet XML File')
    patterns = ['*.xml','*.grmt','*.gourmet']
    mimetypes = ['text/xml','application/xml','text/plain']

    def test_file (self, filename):
        return Tester('.*<gourmetDoc[> ]').test(filename)

    def get_importer (self, filename):
        return gxml2_importer.Converter(filename)


class GourmetXMLPlugin (ImporterPlugin):

    name = _('Gourmet XML File (Obsolete)')
    patterns = ['*.xml','*.grmt','*.gourmet']
    mimetypes = ['text/xml','application/xml','text/plain']

    def test_file (self, filename):
        return Tester('.*<recipeDoc[> ]').test(filename)

    def get_importer (self, filename):
        return gxml_importer.Converter(filename)

