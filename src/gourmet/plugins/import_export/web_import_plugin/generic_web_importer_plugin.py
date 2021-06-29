from typing import Any, Union

from gourmet.i18n import _
from gourmet.plugin import ImporterPlugin, PluginPlugin
from gourmet.plugin_loader import Pluggable
from gourmet.plugins.import_export.website_import_plugins.state import \
    WebsiteTestState  # noqa

from . import webpage_importer


class GenericWebImporter (ImporterPlugin, Pluggable):

    name = _('Webpage')
    patterns = ['*.htm','*.html','*.xhtml']
    mimetypes = ['text/html','text/xhtml','application/xhtml+xml','application/xhtml','application/html']
    targets = ['webimport_plugin']

    def __init__ (self, *args, **kwargs):
        Pluggable.__init__(self, [PluginPlugin])

    def activate (self, pluggable):
        print('activate GenericWebImporter for pluggable',pluggable)
        return ImporterPlugin.activate(self,pluggable)

    def test_file (self, filename):
        '''Given a file name, test whether the file is of this type.'''
        #if filename.endswith('.htm') or filename.endswith('.xhtml') or filename.endswith('.html'):
        return -1 # We are a fallback option

    def test_url (self, url, data, content_type):
        for p in self.plugins:
            if p.test_url(url, data):
                return 1
        try:
            iter(content_type)
        except:
            # In this case, content_type cannot be html...
            return None
        else:
            if 'html' in content_type:
                return -1 # We are the fallback option

    def get_web_importer(self, url: str,
                         data: Union[bytes, str], content_type: str) -> Any:
        # Rank importers by most appropriate based on url
        highest = 0
        importer = webpage_importer.MenuAndAdStrippingWebParser
        for p in self.plugins:
            test_val = p.test_url(url, data)
            if test_val is not None and test_val.value > highest:
                # pass the module as an arg... very awkward inheritance
                importer = p.get_importer(webpage_importer)
                highest = test_val.value
        return importer(url, data)

    def get_importer (self, filename):
        url = 'file://'+filename
        with open(filename, 'r') as f:
            data = f.read()
        content_type = 'text/html'
        return self.get_web_importer(url,data,content_type)
