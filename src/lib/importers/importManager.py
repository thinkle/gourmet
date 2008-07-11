import gourmet.plugin_loader as plugin_loader
from gourmet.plugin import ImporterPlugin
import gourmet.gtk_extras.dialog_extras as de
from gourmet.recipeManager import default_rec_manager
import os.path
from fnmatch import fnmatch
from gourmet.threadManager import get_thread_manager, get_thread_manager_gui
from zip_importer import archive_to_filelist

class ImportFileList (Exception):
    """A special case error -- if an importer throws this error
    instead of returning an importer, our importer will import the
    list of files returned... This is basically a thread-safe way
    around the problem of how to let an importer initiate other
    imports (for zip files etc)"""
    def __init__ (self, filelist):
        self.filelist = filelist

class ImportManager (plugin_loader.Pluggable):

    '''A class to manage importers.
    '''

    __single = None

    def __init__ (self):
        if ImportManager.__single: raise ImportManager.__single
        else: ImportManager.__single = self
        self.plugins_by_name = {}
        self.plugins = []
        plugin_loader.Pluggable.__init__(self,
                                         [ImporterPlugin]
                                         )
        from gourmet.GourmetRecipeManager import get_application
        self.app = get_application()
        self.prefs = self.app.prefs

    def offer_import (self, parent=None):
        """Offer to import a file or group of files.

        Begin the import if we can in a separate dialog.
        """
        filenames = de.select_file(_('Open recipe...'),                                           
                                   filters=self.get_filters(),
                                   parent=parent,
                                   select_multiple = True
                                   )
        if not filenames: return

        self.import_filenames(filenames)
        
    def import_filenames (self, filenames):
        """Import list of filenames, filenames, based on our currently
        registered plugins...
        """
        importers = []        
        while filenames:
            fn = filenames.pop()
            found_plugin = False
            print 'we have the following plugins:',self.plugins
            for plugin in self.plugins:
                for pattern in plugin.patterns:
                    print 'Testing ',pattern,'against',fn
                    if fnmatch(fn,pattern):
                        print 'A match!'
                        importers.append((fn,plugin))
                        found_plugin = True
                        break
                if found_plugin: break
            if not found_plugin: print 'Warning, no plugin found for file ',fn
        for fn,importer_plugin in importers:
            print 'Doing import for ',fn,importer_plugin
            try:
                importer = importer_plugin.get_importer(fn)
            except ImportFileList, ifl:
                # recurse with new filelist...
                self.import_filenames(ifl.filelist)
            else:
                if hasattr(importer,'pre_run'):
                    importer.pre_run()
                tm = get_thread_manager()
                tm.add_thread(importer)
                tmg = get_thread_manager_gui()
                tmg.register_thread_with_dialog(_('Import') + '('+importer_plugin.name+')',
                                                importer)
                tmg.show()
                def follow_up ():
                    from gourmet.GourmetRecipeManager import get_application
                    get_application().make_rec_visible()
                importer.connect('completed',
                                 follow_up
                                 )
                #importer_plugin.do_import(file=fn,
                #                          rd=default_rec_manager(),
                #                          )
        
    def get_importer (self, name):
        return self.plugins_by_name[name]

    def get_filters (self):
        filters = []
        for plugin in self.plugins:
            filters.append([plugin.name,plugin.mimetypes,plugin.patterns])
        return filters

    def register_plugin (self, plugin):
        name = plugin.name
        if self.plugins_by_name.has_key(name):
            print 'WARNING','replacing',self.plugins_by_name[name],'with',plugin
        self.plugins_by_name[name] = plugin
        self.plugins.append(plugin)

    def unregister_plugin (self, plugin):
        name = plugin.name
        if self.plugins_by_name.has_key(name):
            del self.plugins_by_name[name]
            self.plugins.remove(plugin)
        else:
            print 'WARNING: unregistering ',plugin,'but there seems to be no plugin for ',name
    
def get_import_manager ():
    try:
        return ImportManager()
    except ImportManager, im:
        return im
    
if __name__ == '__main__':
    im = ImportManager()
    im.offer_import()
    gtk.main()
