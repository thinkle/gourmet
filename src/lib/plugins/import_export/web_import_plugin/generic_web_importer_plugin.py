from gourmet.plugin import ImporterPlugin, PluginPlugin
from gourmet.plugin_loader import Pluggable
import webpage_importer
from gettext import gettext as _

class GenericWebImporter (ImporterPlugin, Pluggable):

    name = _('Webpage')
    patterns = ['*.htm','.*.html']
    mimetypes = ['text/html','text/xhtml']
    targets = ['webimport_plugin']

    def __init__ (self, *args, **kwargs):
        print 'Instantiate GenericWebImporter!'
        Pluggable.__init__(self, [PluginPlugin])

    #def activate (self, pluggable):
    #    print 'activate GenericWebImporter for pluggable',pluggable
    #    return ImporterPlugin.activate(self,pluggable)

    def test_file (self, filename):
        '''Given a file name, test whether the file is of this type.'''
        print 'GenericWebImporter.test_file(',filename,')'
        if filename.endswith('.htm') or filename.endswith('.html'):
            return True # We are a fallback option

    def test_url (self, url, data, content_type):
        print 'GenericWebImporter.test_url(',url,data[:20],content_type,')'
        for p in self.plugins:
            if p.test_url(url, data):
                return 1
        if 'html' in content_type:
            return -1 # We are the fallback option

    def get_web_importer (self, url, data, content_type):
        highest = 0
        importer = webpage_importer.MenuAndAdStrippingWebParser
        for p in self.plugins:
            test_val = p.test_url(url, data)
            if test_val and test_val > highest:
                # pass the module as an arg... very awkward inheritance
                importer = p.get_importer(webpage_importer) 
                highest = test_val
        return importer(url,data,content_type)

    def get_importer (self, filename):
        url = 'file://'+filename
        data = file(filename).read()
        content_type = 'text/html'
        return get_web_importer(url,data,content_type)
