from gourmet.i18n import _
from gourmet.importers.importer import Tester
from gourmet.plugin import ImporterPlugin
from gourmet.threadManager import get_thread_manager

from . import krecipe_importer


class KrecipeImporterPlugin (ImporterPlugin):

    name = _('KRecipe XML File')
    patterns = ['*.xml','*.kreml']
    mimetypes = ['text/xml','application/xml','text/plain']

    def test_file (self, filename):
        return Tester('.*<krecipes.*[> ]').test(filename)

    def get_importer (self, filename):
        return krecipe_importer.Converter(filename)
