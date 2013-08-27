"""
A plugin that tries to import recipes from the ica.se site
"""
from gourmet.plugin import PluginPlugin
import schema_org_parser
from schema_org_parser import Excluder

class IcaSePlugin (PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        "Is this url from ica.se"
        if 'ica.se' in url:
            return 5
        return 0

    def get_importer (self, webpage_importer):
        IcaSeParser = schema_org_parser.generate(webpage_importer.WebParser)
        #ica.se doesn't specify cookTime, so we use totalTime instead
        IcaSeParser.schema_org_mappings['totalTime'] = 'cooktime'
        return IcaSeParser

