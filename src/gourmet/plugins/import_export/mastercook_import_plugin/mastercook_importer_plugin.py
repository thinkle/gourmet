import gourmet.importers.importer as importer
from gourmet.i18n import _
from gourmet.plugin import ImporterPlugin

from . import mastercook_importer, mastercook_plaintext_importer


class MastercookImporterPlugin (ImporterPlugin):

    name = _('Mastercook XML File')
    patterns = ['*.mx2','*.xml','*.mxp']
    mimetypes = ['text/plain','text/xml','application/xml']

    def test_file (self, filename):
        return importer.Tester('.*<mx2[> ]').test(filename)

    def get_importer (self, filename):
        return mastercook_importer.MastercookImporter(filename)


class MastercookTextImporterPlugin (ImporterPlugin):

    name = _('Mastercook Text File')
    patterns = ['*.mxp','*.txt']
    mimetypes = ['text/plain','text/mastercook']

    def test_file (self, filename):
        return mastercook_plaintext_importer.Tester().test(filename)

    def get_importer (self, filename):
        return mastercook_plaintext_importer.MastercookPlaintextImporter(filename)
