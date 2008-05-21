import gourmet.plugin_loader as plugin_loader
from gourmet.plugin import ExporterPlugin
import gourmet.gtk_extras.dialog_extras as de
from gourmet.threadManager import get_thread_manager, get_thread_manager_gui
import os.path

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

    def offer_single_export (self, rec, prefs, parent=None):
        """Offer to export a single file.

        Return the filename if we have in fact exported said file.
        """
        default_extension = prefs.get('save_recipe_as','html')
        # strip the period if one ended up on our default extension
        if default_extension and default_extension[0]=='.':
            default_extension = default_extension[1:]
        filename,exp_type = de.saveas_file(_('Save recipe as...'),
                                           filename='~/%s%s%s'%(rec.title,
                                                                os.path.extsep,
                                                                default_extension),
                                           filters=self.get_single_filters(),
                                           parent=parent
                                           )
        if not filename: return
        if not exp_type or not self.can_export_type(exp_type):
            de.show_message(label=_('Gourmet cannot export file of type "%s"')%os.path.splitext(fn)[1])
            return
        exporter_plugin = self.get_exporter(exp_type)
        extra_prefs = exporter_plugin.run_extra_prefs_dialog() or {}
        outfi = file(filename,
                     exporter_plugin.mode)
        exporter_plugin.do_single_export(**{
            'rd':self.rg.rd,
            'rec':self.current_rec,
            'out':outfi,
            'conv':self.rg.conv,
            'change_units':self.prefs.get('readableUnits',True),
            'mult':self.mult,            
            'extra_prefs':extra_prefs,
            })
        outfi.close()
        import gourmet.GourmetRecipeManager
        main_app =  gourmet.GourmetRecipeManager.get_application()
        main_app.offer_url(_('Export complete!'),
                           _('Recipe exported to %s')%filename,
                           url='file:///%s'%filename)
        return filename
    

    def offer_multiple_export (self, recs, prefs, parent=None, prog=None):
        """Offer user a chance to export multiple recipes at once.

        Return the exporter class capable of doing this and a
        dictionary of arguments for the progress dialog.
        
        exporter class will be suitable to run in a threaded mode -- it has a run, terminate, and pau
        """
        ext = prefs.get('save_recipes_as','%sxml'%os.path.extsep)
        exp_directory = prefs.get('rec_exp_directory','~')
        fn,exp_type=de.saveas_file(_("Export recipes"),
                                     filename="%s/%s%s"%(exp_directory,_('recipes'),ext),
                                     parent=parent,
                                     filters=self.get_multiple_filters())
        if fn:
            prefs['rec_exp_directory']=os.path.split(fn)[0]
            prefs['save_recipes_as']=os.path.splitext(fn)[1]
            expClass=None
            if self.can_export_type(exp_type):
                myexp = self.get_exporter(exp_type)
                extra_prefs = myexp.run_extra_prefs_dialog() or {}
                pd_args={'label':myexp.label,'sublabel':myexp.sublabel%{'file':fn}}
                print 'exporting',len(recs),'recs'
                exporterInstance = myexp.get_multiple_exporter({'rd':self.app.rd,
                                                             'rv': recs,
                                                             'conv':self.app.conv,
                                                             'prog':prog,
                                                             'file':fn,
                                                             'extra_prefs':extra_prefs,
                                                             })
                import gourmet.GourmetRecipeManager
                main_app =  gourmet.GourmetRecipeManager.get_application()
                tm = get_thread_manager()
                tmg = get_thread_manager_gui()
                tm.add_thread(exporterInstance)
                tmg.register_thread_with_dialog(_('Export')+'('+myexp.label+')',exporterInstance)
                tmg.show()
                exporterInstance.connect('completed',
                                         lambda *args: main_app.offer_url('Export complete!',
                                                                          'Recipes exported to %s'%fn,
                                                                          url='file:///%s'%fn))
                

    def can_export_type (self, name): return self.plugins_by_name.has_key(name)

    def get_exporter (self, name):
        return self.plugins_by_name[name]

    def get_single_filters (self):
        filters = []
        for plugin in self.plugins:
            filters.extend(plugin.saveas_single_filters)
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
    except ExporterManager, em:
        return em
