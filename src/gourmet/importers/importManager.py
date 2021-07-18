import tempfile
from fnmatch import fnmatch
from typing import Any, List, Optional, Tuple
from urllib.parse import urlparse

from gi.repository import Gtk

import gourmet.gtk_extras.dialog_extras as de
import gourmet.plugin_loader as plugin_loader
from gourmet.i18n import _
from gourmet.plugin import ImporterPlugin, ImportManagerPlugin
from gourmet.threadManager import (NotThreadSafe, get_thread_manager,
                                   get_thread_manager_gui)

from .webextras import URLReader


class ImportFileList (Exception):
    """A special case error -- if an importer throws this error
    instead of returning an importer, our importer will import the
    list of files returned... This is basically a thread-safe way
    around the problem of how to let an importer initiate other
    imports (for zip files etc)"""
    def __init__ (self, filelist):
        self.filelist = filelist

class ImportManager (plugin_loader.Pluggable):

    '''A class to
    manage importers.
    '''

    __single = None

    @classmethod
    def instance(cls):
        if ImportManager.__single is None:
            ImportManager.__single = cls()

        return ImportManager.__single

    def __init__ (self):
        self.tempfiles = {}
        self.extensions_by_mimetype = {}
        self.plugins_by_name = {}
        self.plugins = []
        self.importer_plugins = []
        plugin_loader.Pluggable.__init__(self,
                                         [ImporterPlugin,
                                          ImportManagerPlugin]
                                         )
        self.get_app_and_prefs()

    def get_app_and_prefs (self):
        from gourmet.GourmetRecipeManager import get_application
        self.app = get_application()
        self.prefs = self.app.prefs

    def offer_web_import(self, parent: Gtk.Window = None):
        """Offer to import a URL.

        Once the file is downloaded, it can be treated by any of our
        normal plugins for acting on files, or by special web-aware
        plugins.
        """
        sublabel = _('Enter the URL of a recipe archive or recipe website.')
        url = de.getEntry(label=_('Enter website address'),
                          sublabel=sublabel,
                          entryLabel=_('Enter URL:'),
                          entryTip=_('Enter the address of a website or recipe archive.'),
                          default_character_width=60,
                          )
        if url:
            return self.import_url(url)

    def import_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme:
            # there is an `http[s]` prefix
            url = "{}://{}{}".format(parsed_url.scheme, parsed_url.netloc, parsed_url.path)
        else:
            # no `https` prefix, we add one
            url = 'https://' + parsed_url.path
        reader = URLReader(url)
        reader.connect('completed',
                       self.finish_web_import)
        self.setup_thread(reader,'Downloading %s'%url, connect_follow_up=False)

    def finish_web_import (self, reader):
        # Filter by mimetype...
        if reader.content_type:
            base_content_type=reader.content_type.split(';')[0]
            possible_plugins = [p for p in self.importer_plugins if base_content_type in p.mimetypes]
        else:
            possible_plugins = self.importer_plugins
        fallback = None; plugin = None
        for p in possible_plugins:
            result = p.test_url(reader.url,reader.data,reader.content_type)
            if result == -1:
                fallback = p
            elif result:
                plugin = p
                break
        if not plugin:
            plugin = fallback
        if not plugin:
            de.show_message(
                title=_('Unable to import URL'),
                label=_('Gourmet does not have a plugin capable of importing URL'),
                sublabel=_('Unable to import URL %(url)s of mimetype %(type)s. File saved to temporary location %(fn)s')%{
                'url':reader.url,
                'type':reader.content_type or 'Unknown',
                'fn':self.get_tempfilename(reader.url,reader.data,reader.content_type)
                },
                )
        else:
            print('Doing import of',reader.url,plugin)
            self.do_import(plugin, 'get_web_importer', reader.url,
                           reader.data.decode(), reader.content_type)

    def offer_import(self, parent: Optional[Gtk.Window] = None):
        """Offer to import a file or group of files.

        Begin the import if we can in a separate dialog.
        """
        filenames = de.select_file(_('Open recipe...'),
                                   filters=self.get_filters(),
                                   parent=parent,
                                   select_multiple=True)
        if filenames is None:
            return
        self.import_filenames(filenames)

    def import_filenames(self, filenames: List[str]) -> List[Any]:
        """Import list of filenames, filenames, based on our currently
        registered plugins.

        Return a list of importers (mostly useful for testing purposes)
        """
        importers = []
        while filenames:
            fn = filenames.pop()
            fallback = None
            found_plugin = False
            for plugin in self.importer_plugins:
                for pattern in plugin.patterns:
                    if fnmatch(fn.upper(),pattern.upper()):
                        result = plugin.test_file(fn)
                        if result==-1: # FALLBACK
                            fallback = plugin
                        elif result:
                            importers.append((fn,plugin))
                            found_plugin = True
                        else:
                            print('File ',fn,'appeared to match ',plugin,'but failed test.')
                        break
                if found_plugin: break
            if not found_plugin:
                if fallback:
                    importers.append((fn,fallback))
                else:
                    print('Warning, no plugin found for file ',fn)
        ret_importers = [] # a list of importer instances to return
        for fn,importer_plugin in importers:
            print('Doing import for ',fn,importer_plugin)
            ret_importers.append(
                self.do_import(importer_plugin,'get_importer',fn)
                )
        print('import_filenames returns',ret_importers)
        return ret_importers

    def do_import(self, importer_plugin: Any,
                  method: str, *method_args: Tuple[str]):
        try:
            importer = getattr(importer_plugin, method)(*method_args)
            self.setup_notification_message(importer)
        except ImportFileList as ifl:
            # recurse with new filelist...
            return self.import_filenames(ifl.filelist)
        else:
            if hasattr(importer, 'pre_run'):
                importer.pre_run()
            if isinstance(importer, NotThreadSafe):
                #print 'Running manually --- not threadsafe!'
                importer.run()
                self.follow_up(None,importer)
            else:
                label = _('Import') + ' ('+importer_plugin.name+')'
                self.setup_thread(importer, label)
            print('do_importer returns importer:',importer)
            return importer

    def setup_notification_message(self, importer):
        tmg = get_thread_manager_gui()
        importer.connect('completed',tmg.importer_thread_done)

    @plugin_loader.pluggable_method
    def follow_up (self, threadmanager, importer):
        if hasattr(importer,'post_run'):
            importer.post_run()
        if hasattr(self,'app'):
            self.app.make_rec_visible()

    def setup_thread (self, importer, label, connect_follow_up=True):
        tm = get_thread_manager()
        tm.add_thread(importer)
        tmg = get_thread_manager_gui()
        tmg.register_thread_with_dialog(label,
                                        importer)
        if connect_follow_up:
            importer.connect('completed',
                             self.follow_up,
                             importer
                             )

    def get_importer (self, name):
        return self.plugins_by_name[name]

    def get_tempfilename(self, url: str,
                         data: bytes,
                         content_type: str) -> str:
        """Get a temporary filename for the file to parse.

        The url is a page where a recipe is found, for which Gourmet should have
        a plugin.
        data is the retrieved html document.
        content_type is the mime-type string representation (eg. 'text/html')

        The value returned is a string containing the temporary file path.

        TODO: self.tempfiles could store pathlib.Path objects, and this function
              return these.
        """
        if url in self.tempfiles:
            return self.tempfiles[url]
        else:
            fn = url.split('/')[-1]
            if '.' in fn:
                ext = fn.split('.')[-1]
            elif content_type:
                ext = self.guess_extension(content_type)
        if ext:
            tf = tempfile.mktemp('.'+ext)
        else:
            tf = tempfile.mktemp()
        self.tempfiles[url] = tf
        with open(tf, "wb") as fout:
            fout.write(data)
        return self.tempfiles[url]

    def guess_extension (self, content_type):
        if content_type in self.extensions_by_mimetype:
            answers = list(self.extensions_by_mimetype[content_type].items())
            return max(answers, key=lambda x: x[1])[0] # Return the most frequent by count...
        else:
            import mimetypes
            return mimetypes.guess_extension(content_type)

    def get_filters (self):
        all_importable_mimetypes = []
        all_importable_patterns = []
        filters = []; names = []
        for plugin in self.importer_plugins:
            if plugin.name in names:
                i = names.index(plugin.name)
                filters[i][1] += plugin.mimetypes
                filters[i][2] += plugin.patterns
            else:
                names.append(plugin.name)
                filters.append([plugin.name,plugin.mimetypes,plugin.patterns])
            all_importable_mimetypes += plugin.mimetypes
            all_importable_patterns += plugin.patterns
        filters = [[_('All importable files'),all_importable_mimetypes,all_importable_patterns]] + filters
        return filters

    def register_plugin (self, plugin):
        self.plugins.append(plugin)
        if isinstance(plugin,ImporterPlugin):
            name = plugin.name
            if name in self.plugins_by_name:
                print('WARNING','replacing',self.plugins_by_name[name],'with',plugin)
            self.plugins_by_name[name] = plugin
            self.learn_mimetype_extension_mappings(plugin)
            self.importer_plugins.append(plugin)


    def learn_mimetype_extension_mappings (self, plugin):
        for mt in plugin.mimetypes:
            if mt not in self.extensions_by_mimetype:
                self.extensions_by_mimetype[mt] = {}
            for ptrn in plugin.patterns:
                if ptrn.find('*.')==0:
                    ext = ptrn.split('.')[-1]
                    if ext.isalnum():
                        # Then increment our count for this...
                        self.extensions_by_mimetype[mt][ext] = self.extensions_by_mimetype[mt].get(ext,0) + 1

    def unregister_plugin (self, plugin):
        if isinstance(plugin,ImporterPlugin):
            name = plugin.name
            if name in self.plugins_by_name:
                del self.plugins_by_name[name]
                self.plugins.remove(plugin)
            else:
                print('WARNING: unregistering ',plugin,'but there seems to be no plugin for ',name)
        else:
            self.plugins.remove(plugin)

def get_import_manager ():
    return ImportManager.instance()

if __name__ == '__main__':
    im = ImportManager.instance()
    im.offer_import()
    Gtk.main()
