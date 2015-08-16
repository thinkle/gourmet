from gourmet.plugin import ImporterPlugin, PluginPlugin
from gourmet.plugin_loader import Pluggable
import scrapy_importer
from gettext import gettext as _

class ScrapyWebImporter (ImporterPlugin, Pluggable):

    name = _('WebScrap')
    patterns = ['*.htm','*.html','*.xhtml']
    mimetypes = ['text/html','text/xhtml','application/xhtml+xml','application/xhtml','application/html']
    targets = ['scrapyWeb_plugin']

    def __init__ (self, *args, **kwargs):
        Pluggable.__init__(self, [PluginPlugin])

    def activate (self, pluggable):
        return ImporterPlugin.activate(self,pluggable)

    def test_file (self, filename):
        '''Given a file name, test whether the file is of this type.'''
        return None

    def test_url (self, url, data, content_type):
        for p in self.plugins:
            if p.test_url(url, data):
                return 1
        return None

    def get_web_importer (self, url, data, content_type):
        highest = 0
        for p in self.plugins:
            test_val = p.test_url(url, data)
            if test_val and test_val > highest:
                # pass the module as an arg... very awkward inheritance
                parser = p.get_parser() 
                highest = test_val
        if parser: 
            return scrapy_importer.ScrapyImporter(url,data,parser)

    def get_importer (self, filename):
        url = 'file://'+filename
        data = file(filename).read()
        content_type = 'text/html'
        return self.get_web_importer(url,data,content_type)
