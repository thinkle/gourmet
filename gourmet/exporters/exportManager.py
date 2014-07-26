import gourmet.plugin_loader as plugin_loader
from gourmet.plugin import ExporterPlugin
import gourmet.gtk_extras.dialog_extras as de
from gourmet.threadManager import get_thread_manager, get_thread_manager_gui
from glib import get_user_special_dir, USER_DIRECTORY_DOCUMENTS
import os.path

EXTRA_PREFS_AUTOMATIC = -1
EXTRA_PREFS_DEFAULT = 0

class ExportManager (plugin_loader.Pluggable):

    '''A class to manage exporters.
    '''

    __single = None

    def __init__ (self):
        if ExportManager.__single: raise ExportManager.__single
        else: ExportManager.__single = self
        self.plugins_by_name = {}
        plugin_loader.Pluggable.__init__(self,
                                         [ExporterPlugin]
                                         )
        from gourmet.GourmetRecipeManager import get_application
        self.app = get_application()

    def offer_single_export (self, rec, prefs, mult=1, parent=None):
        """Offer to export a single file.

        Return the filename if we have in fact exported said file.
        """
        default_extension = prefs.get('save_recipe_as','html')
        # strip the period if one ended up on our default extension
        if default_extension and default_extension[0]=='.':
            default_extension = default_extension[1:]
        exp_directory = prefs.get('rec_exp_directory',
                                  get_user_special_dir(USER_DIRECTORY_DOCUMENTS)
                                  )
        filename,exp_type = de.saveas_file(_('Save recipe as...'),
                                           filename='%s%s%s%s%s'%(exp_directory,
                                                                  os.path.sep,
                                                                  rec.title,
                                                                  os.path.extsep,
                                                                  default_extension),
                                           filters=self.get_single_filters(),
                                           parent=parent
                                           )
        if not filename: return
        if not exp_type or not self.can_export_type(exp_type):
            de.show_message(label=_('Gourmet cannot export file of type "%s"')%os.path.splitext(filename)[1])
            return
        return self.do_single_export(rec, filename, exp_type, mult)
        
    def do_single_export (self, rec, filename, exp_type, mult=1, extra_prefs=EXTRA_PREFS_AUTOMATIC):
        exporter_plugin = self.get_exporter(exp_type)
        extra_prefs = self.get_extra_prefs(exporter_plugin,extra_prefs)
        #extra_prefs = exporter_plugin.run_extra_prefs_dialog() or {}
        if hasattr(exporter_plugin,'mode'):
            export_file_mode = exporter_plugin.mode
            if export_file_mode not in ['w','a','wb']:
                print 'IGNORING INVALID FILE MODE',export_file_mode
                export_file_mode = 'w'
        else:
            export_file_mode = 'w'
        outfi = file(filename,
                     export_file_mode)
        # this should write to our file...
        exporter_plugin.do_single_export({
            'rd':self.app.rd,
            'rec':rec,
            'out':outfi,
            'conv':self.app.conv,
            'change_units':self.app.prefs.get('readableUnits',True),
            'mult':mult,     
            'extra_prefs':extra_prefs,
            })
        outfi.close()
        return filename

    def offer_multiple_export (self, recs, prefs, parent=None, prog=None,
                               export_all=False):
        """Offer user a chance to export multiple recipes at once.

        Return the exporter class capable of doing this and a
        dictionary of arguments for the progress dialog.
        """
        if (not export_all) or (len(recs) < 950):
            # inelegantly avoid bug that happens when this code runs
            # on large numbers of recipes. The good news is that this
            # that that will almost only ever happen when we're
            # exporting all recipes, which makes this code irrelevant
            # anyway.
            self.app.rd.include_linked_recipes(recs)
        ext = prefs.get('save_recipes_as','%sxml'%os.path.extsep)
        exp_directory = prefs.get('rec_exp_directory',
                                  get_user_special_dir(USER_DIRECTORY_DOCUMENTS)
                                  )
        fn,exp_type=de.saveas_file(_("Export recipes"),
                                     filename="%s%s%s%s"%(exp_directory,
                                                          os.path.sep,
                                                          _('recipes'),
                                                          ext),
                                     parent=parent,
                                     filters=self.get_multiple_filters())
        if fn:
            prefs['rec_exp_directory']=os.path.split(fn)[0]
            prefs['save_recipes_as']=os.path.splitext(fn)[1]
            instance = self.do_multiple_export(recs, fn, exp_type)
            if not instance:
                de.show_message(
                    okay=gtk.STOCK_CLOSE,
                    cancel=False,
                    label=_('Unable to export: unknown filetype "%s"'%fn),
                    sublabel=_('Please make sure to select a filetype from the dropdown menu when saving.'),
                    message_type=gtk.MESSAGE_ERROR,
                    )
                return
            return instance

    def get_extra_prefs (self, myexp, extra_prefs):
        if extra_prefs == EXTRA_PREFS_AUTOMATIC:
            extra_prefs = myexp.run_extra_prefs_dialog() or {}
        elif extra_prefs == EXTRA_PREFS_DEFAULT:
            extra_prefs = myexp.get_default_prefs()
        else:
            extra_prefs = extra_prefs
        return extra_prefs
        
    def get_multiple_exporter (self, recs, fn, exp_type=None,
                               setup_gui=True, extra_prefs=EXTRA_PREFS_AUTOMATIC):
        if not exp_type:
            exp_type = de.get_type_for_filters(fn,self.get_multiple_filters())
        if self.can_export_type(exp_type):
            myexp = self.get_exporter(exp_type)
            extra_prefs = self.get_extra_prefs(myexp,extra_prefs)
            pd_args={'label':myexp.label,'sublabel':myexp.sublabel%{'file':fn}}
            exporterInstance = myexp.get_multiple_exporter({'rd':self.app.rd,
                                                         'rv': recs,
                                                            #'conv':self.app.conv,
                                                            #'prog':,
                                                         'file':fn,
                                                         'extra_prefs':extra_prefs,
                                                         })        
            return myexp, exporterInstance
        else:
            print 'WARNING: CANNOT EXPORT TYPE',exp_type        

    def do_multiple_export (self, recs, fn, exp_type=None,
                                           setup_gui=True, extra_prefs=EXTRA_PREFS_AUTOMATIC):
            myexp, exporterInstance = self.get_multiple_exporter(recs,fn,exp_type,setup_gui,extra_prefs)
            tm = get_thread_manager()
            tm.add_thread(exporterInstance)
            if setup_gui:
                tmg = get_thread_manager_gui()
                tmg.register_thread_with_dialog(_('Export')+' ('+myexp.label+')',
                                                _('Recipes successfully exported to <a href="file:///%s">%s</a>')%(fn,fn),
                                                exporterInstance)
                tmg.show()
            print 'Return exporter instance'
            return exporterInstance        

    def can_export_type (self, name): return self.plugins_by_name.has_key(name)

    def get_exporter (self, name):
        return self.plugins_by_name[name]

    def get_single_filters (self):
        filters = []
        for plugin in self.plugins:
            filters.append(plugin.saveas_single_filters)
        return filters

    def get_multiple_filters (self):
        filters = []
        for plugin in self.plugins:
            filters.append(plugin.saveas_filters)
        return filters

    def register_plugin (self, plugin):
        name = plugin.saveas_filters[0]
        if self.plugins_by_name.has_key(name):
            print 'WARNING','replacing',self.plugins_by_name[name],'with',plugin
        self.plugins_by_name[name] = plugin

    def unregister_plugin (self, plugin):
        name = plugin.saveas_filters[0]
        if self.plugins_by_name.has_key(name):
            del self.plugins_by_name[name]
        else:
            print 'WARNING: unregistering ',plugin,'but there seems to be no plugin for ',name
    
def get_export_manager ():
    try:
        return ExportManager()
    except ExportManager, em:
        return em
