#!/usr/bin/env python
import os.path, time, os, sys, re, threading, StringIO, pango, string
import Image
import gtk.glade, gtk, gobject, gtk.gdk, traceback
#import valueEditor, batchEditor
import recipeManager
import exporters.printer as printer
import prefs, prefsGui, shopgui, reccard, fnmatch, tempfile
import exporters, importers
from exporters.exportManager import get_export_manager
from importers.importManager import get_import_manager
import convert, version
from gtk_extras import ratingWidget, WidgetSaver
from gtk_extras import dialog_extras as de
from gtk_extras import treeview_extras as te
from ImageExtras import get_pixbuf_from_jpg
from gdebug import *
from gglobals import *
from recindex import RecIndex
#import exporters.recipe_emailer as recipe_emailer
import locale, gettext
from timer import show_timer
_ = gettext.gettext
from defaults.defaults import lang as defaults
import plugin_loader, plugin, plugin_gui

from zipfile import BadZipfile

if os.name == 'posix':
    # somewhat hackish -- we assume USR ==
    usr_share = os.path.join(os.path.split(datad)[0])
    if not os.path.exists(os.path.join(usr,'locale')):
        usr_share = os.path.join('/usr','share')
    DIR = os.path.join(usr_share,'locale')
else:
    pth = datad.split(os.path.sep)
    pth = pth[:-1] # strip off data
    dirparts = os.path.sep.join(pth)
    DIR = os.path.join(dirparts,'i18n')

import gettext_setup

try:
    import rtf_exporter
    rtf=True
except ImportError:
    debug('No RTF support',0)
    rtf=False

def check_for_data_to_import (rm):
    if rm.fetch_len(rm.recipe_table)==0:
        try:
            import legacy_db
        except ImportError:
            #print "Not trying to update."
            #print "We had an import error."
            #import traceback; traceback.print_exc()
            1
        else:
            pd = de.ProgressDialog(label=_('Importing old recipe data'),
                                   sublabel=_('Importing recipe data from a previous version of Gourmet into new database.'),
                                   )
            def set_prog (p,msg=None):
                p=float(p)
                pd.set_progress(p,msg)
                while gtk.events_pending():
                    gtk.main_iteration()
            legacy_db.backup_legacy_data(gourmetdir, pd, set_prog)
            backup_file = os.path.join(gourmetdir,'GOURMET_DATA_DUMP')
            if os.path.exists(backup_file):
                import upgradeHandler        
                pd.show()
                upgradeHandler.import_backup_file(
                    rm,backup_file,set_prog
                    )
                os.rename(backup_file,backup_file+'.ALREADY_LOADED')
                pd.hide()
                pd.destroy()

class GourmetApplication:
    """The main Gourmet Application.

    This handles everything that needs to be handled across the
    different interfaces -- updating the view menu, and so on.

    This handles plugin registration, configuration, and so on.
    """

    shared_go_menu = '''
    <ui>
    <menubar name="%(name)s">
    <menu name="Go" action="Go">
    <menuitem action="GoRecipeIndex"/>
    </menu></menubar></ui>
    '''
    go_path = '/%(name)s/Go/'

    __single = None
    
    def __init__ (self, splash_label=None):
        if GourmetApplication.__single:
            raise GourmetApplication.__single
        GourmetApplication.__single = self
        # These first two items might be better handled using a
        # singleton design pattern... 
        self.splash_label = splash_label
        self.conv = convert.Converter() 
        self.star_generator = ratingWidget.StarGenerator()        
        # Setup methods...
        self.setup_prefs() # Setup preferences...
        self.setup_plugins()
        self.setup_recipes() # Setup recipe database
        #self.setup_nutrition()
        self.setup_shopping()
        self.setup_go_menu()
        self.rc={}
        self.exportManager = get_export_manager()
        self.importManager = get_import_manager()

    def setup_plugins (self):
        pass

    def show_preferences (self, *args):
        self.prefsGui.show_dialog(page=self.prefsGui.INDEX_PAGE)

    # Setup preferences system
    def setup_prefs (self):
        self.conf = []        
        self.prefs = prefs.Prefs()
        self.prefsGui = prefsGui.PreferencesGui(
            self.prefs,
            buttons={'clear_remembered_optional_button':lambda *args: self.forget_remembered_optional_ingredients()}
            )
        self.prefsGui.apply_prefs_dic['recipes_per_page'] = lambda p,v: getattr(getattr(self,'rmodel'),
                                                                               'change_items_per_page')(v)
        
        def toggleFractions (prefname,use):
            if use:
                convert.USE_FRACTIONS = convert.FRACTIONS_NORMAL
            else:
                convert.USE_FRACTIONS = convert.FRACTIONS_OFF
        self.prefsGui.apply_prefs_dic['useFractions'] = toggleFractions
        if self.prefs.get('useFractions',
                          defaults.LANG_PROPERTIES['useFractions']
                          ):
            convert.USE_FRACTIONS = convert.FRACTIONS_NORMAL
        else:
            convert.USE_FRACTIONS = convert.FRACTIONS_OFF

    # Splash convenience method for start-up splashscreen
    def update_splash (self, text):
        """Update splash screen on startup."""
        debug("Setting splash text: %s"%text,3)
        if not self.splash_label: return
        self.splash_label.set_text(text)        
        while gtk.events_pending():
            gtk.main_iteration()
                
    # Convenience method for showing progress dialogs for import/export/deletion
    def show_progress_dialog (self, thread, progress_dialog_kwargs={},message=_("Import paused"),
                           stop_message=_("Stop import")):
        """Show a progress dialog"""
        if hasattr(thread,'name'): name=thread.name
        else: name = ''
        for k,v in [('okay',True),
                    ('label',name),
                    ('parent',self.app),
                    ('pause',self.pause_cb),
                    ('stop',self.stop_cb),
                    ('modal',False),]:
            if not progress_dialog_kwargs.has_key(k):
                progress_dialog_kwargs[k]=v
        if not hasattr(self,'progress_dialog') or not self.progress_dialog:
            self.progress_dialog = de.ProgressDialog(**progress_dialog_kwargs)
            self.prog = self.progress_dialog.progress_bar
        else:
            self.progress_dialog.reassign_buttons(pausecb=progress_dialog_kwargs['pause'],
                                              stopcb=progress_dialog_kwargs['stop'])
            self.progress_dialog.reset_label(progress_dialog_kwargs['label'])
        self.pause_message = message
        self.stop_message = stop_message
        self.thread = thread        
        self.progress_dialog.show()
        self.progress_dialog.connect('close',lambda *args: setattr(self.progress_dialog,None))
        
    def hide_progress_dialog (self):
        """Make the progress dialog go away."""
        if hasattr(self,'progress_dialog') and self.progress_dialog:
            self.progress_dialog.hide()
            self.progress_dialog.destroy()
            self.progress_dialog = None

    # setup recipe database
    def setup_recipes (self):
        """Initialize recipe database.

        We load our recipe database from recipeManager. If there's any problem,
        we display the traceback to the user so they can send it out for debugging
        (or possibly make sense of it themselves!)."""
        try:
            self.rd = recipeManager.default_rec_manager()
            check_for_data_to_import(self.rd)
            # initiate autosave stuff
            # autosave every 3 minutes (milliseconds * 1000 milliseconds/second * 60 seconds/minute)
            gobject.timeout_add(1000*60*3,lambda *args: self.rd.save() or True)
        except:
            self.prefs['db_backend'] = None
            self.prefs.save()
            from StringIO import StringIO
            f = StringIO()
            traceback.print_exc(file=f)
            error_mess = f.getvalue()
            de.show_message(label='Database Connection failed.',
                            sublabel='There was a problem with the database information you gave Gourmet',
                            expander=(_('_Details'),
                                      error_mess)
                            )
            raise
        # connect hooks to modify our view whenever and
        # whenceever our recipes are updated...
        self.rd.modify_hooks.append(self.update_attribute_models)
        self.rd.add_hooks.append(self.update_attribute_models)
        self.rd.delete_hooks.append(self.update_attribute_models)
        # we'll need to hand these to various other places
        # that want a list of units.
        self.umodel = UnitModel(self.conv)
        self.attributeModels = []
        self.inginfo = reccard.IngInfo(self.rd)

    def setup_shopping (self):
        """Setup shopping related stuff"""
        #self.create_rmodel(self.rd.recipe_table)
        self.sl = shopgui.ShopGui(self, conv=self.conv)
        self.sl.hide()

    # Methods for keeping track of open recipe cards...
    def del_rc (self, id):
        """Forget about recipe card identified by id"""
        if self.rc.has_key(id):
            del self.rc[id]
        self.update_go_menu()

    def update_reccards (self, rec):
        if self.rc.has_key(rec.id):
            rc=self.rc[rec.id]
            rc.updateRecipe(rec,show=False)
            self.update_go_menu()

    def go_menu (self):
        """Build a _View menu based on recipes currently
        opened in recipe cards."""
        m=gtk.Menu()
        ri=gtk.MenuItem(_('Recipe _Index'))
        sh=gtk.MenuItem(_('Shopping _List'))
        separator=gtk.MenuItem()
        ri.connect('activate',lambda *args: self.app.present())
        sh.connect('activate',self.sl.show)
        m.append(ri)
        ri.show()
        m.append(sh)
        sh.show()
        m.append(separator)
        separator.show()
        for rc in self.rc.values():
            i=gtk.MenuItem("_%s"%rc.current_rec.title)
            i.connect('activate',rc.show)
            m.append(i)
            i.show()
        return m

    def setup_go_menu (self):
        self.goActionGroup = gtk.ActionGroup('GoActions')
        self.goActionGroup.add_actions([('Go',None,_('_Go'))])
        self.uimanagers = {}
        self.merged_go_menus = {}

    def add_uimanager_to_manage (self, id, uimanager, menu_root_name):
        uimanager.insert_action_group(self.goActionGroup,0)
        uimanager.add_ui_from_string(self.shared_go_menu%{'name':menu_root_name})
        self.uimanagers[id] = [uimanager,menu_root_name,
                               {} # a dictionary of added menu items
                               ]

    def update_action_group (self):
        for rc in self.rc.values():
            action_name = 'GoRecipe'+str(rc.current_rec.id)
            existing_action = self.goActionGroup.get_action(action_name)
            if not existing_action:
                self.goActionGroup.add_actions(
                    [(action_name,None,'_'+rc.current_rec.title,
                      None,None,rc.show)]
                    )
            else:
                if existing_action.props.label != '_'+rc.current_rec.title:
                    existing_action.props.label = '_'+rc.current_rec.title

    def update_go_menu (self):
        self.update_action_group()
        for uiid in self.uimanagers:
            self.update_go_menu_for_ui(uiid)
            
    def update_go_menu_for_ui (self, id):
        """Update the go_menu of interface identified by ID

        The interface must have first been handed to
        add_uimanager_to_manage
        """
        uimanager,menu_root_name,merged_dic = self.uimanagers[id]
        for rc in self.rc.values():
            path = self.go_path%{'name':menu_root_name} + 'GoRecipe'+str(rc.current_rec.id)
            if not uimanager.get_widget(path):
                actionName = 'GoRecipe'+str(rc.current_rec.id)
                uistring = '''<menubar name="%(menu_root_name)s">
                <menu name="Go" action="Go">
                <menuitem action="%(actionName)s"/>
                </menu>
                </menubar>'''%locals()
                merge_id = uimanager.add_ui_from_string(uistring)
                merged_dic[rc.current_rec.id] = merge_id
                uimanager.ensure_update()                
        for idkey in merged_dic:
            if not self.rc.has_key(idkey):
                uimanager.remove_ui(merged_dic[idkey])

    # Methods to keep one set of listmodels for each attribute for
    # which we might want text completion or a dropdown...
    def update_attribute_models (self):
        for attr,mod in self.attributeModels:
            self.update_attribute_model(attr)
            
    def update_attribute_model (self, attribute):
        slist = self.create_attribute_list(attribute)
        model = getattr(self,'%sModel'%attribute)
        for n,item in enumerate(slist):
            if model[n][0] == item:
                continue
            else:
                # See if we match something later in the model -- if
                # we do, suck up the whole model
                additional = 1
                found_match = False
                while len(model) > (n+additional):
                    if model[n+additional][0] == item:
                        while additional > 0:
                            model.remove(model.get_iter(n))
                            additional -= 1
                            found_match = False
                        break
                    additional += 1
                if not found_match:
                    model.insert(n,[item])
        while len(model) > len(slist):
            last = model.get_iter(len(model) - 1)
            model.remove(last)
        return model

    def create_attribute_list (self, attribute):
        """Create a ListModel with unique values of attribute.
        """
        if attribute=='category':
            slist = self.rg.rd.get_unique_values(attribute,self.rg.rd.categories_table)
        else:
            slist = self.rg.rd.get_unique_values(attribute,deleted=False)
        if not slist:
            slist = self.rg.rd.get_default_values(attribute)
        else:
            for default_value in self.rg.rd.get_default_values(attribute):
                if default_value not in slist: slist.append(default_value)
        slist.sort()
        return slist

    def get_attribute_model (self, attribute):
        """Return a ListModel with a unique list of values for attribute.

        This is stored here so that all the different comboboxes that
        might need e.g. a list of categories can share 1 model and
        save memory.
        """
        if not hasattr(self,'%sModel'%attribute):
            slist = self.create_attribute_list(attribute)
            m = gtk.ListStore(str)
            for i in slist: m.append([i])
            setattr(self,'%sModel'%attribute,m)
            self.attributeModels.append((attribute,getattr(self,'%sModel'%attribute)))
        return getattr(self,'%sModel'%attribute)

    # About/Help
    def show_about (self, *args):
        """Show information about ourselves, using GNOME's
        nice interface if available."""
        debug("show_about (self, *args):",5)
        description=version.description
        copyright=version.copyright
        appname=version.appname
        myversion=version.version
        authors=version.authors
        website="http://grecipe-manager.sourceforge.net"
        documenters=None
        translator=_("translator-credits")
        # translator's should translate the string 'translator-credits'
        # If we're not using a translatino, then this isn't shown
        if translator == "translator-credits":
            translator = None
        # Grab CREDITS from our defaults_LANG file too!
        if hasattr(defaults,'CREDITS') and defaults.CREDITS:
            if translator and translator.find(defaults.CREDITS) > -1:
                translator += "\n%s"%defaults.CREDITS
            else:
                translator = defaults.CREDITS
        comments=None
        logo=gtk.gdk.pixbuf_new_from_file(os.path.join(imagedir,"gourmet_logo.png"))
        try:
            import gnome.ui
            # to test the non-GNOME hack on a GNOME system,
            # uncomment the following line
            # import asdflkjasdf
            args = [appname,
                    myversion,
                    copyright,
                    description,
                    authors,
                    comments,
                    translator,
                    logo]
            if not translator:
                args = args[0:5] + [None] + args[6:]
            about= gnome.ui.About(*args)
            try:
                about.set_website(website) #will be available in 2.6
            except AttributeError:
                debug('No website available in "about" with this version of gtk/gnome',2)
                c=about.get_property('comments')
                c += _("\nWebsite: %s")%website
                about.set_property('comments',c)
                pass
            about.show()
        except ImportError:
            sublabel = '%s\n%s\n'%(copyright,description)
            for a in authors:
                sublabel += '\n%s'%a
            if translator:
                sublabel += _('\nTranslated by: %s')%translator
            if website:
                sublabel += _('\nWebsite: %s')%website
            import xml.sax.saxutils
            de.show_message(label=xml.sax.saxutils.escape('%s %s'%(appname,myversion)),
                            sublabel=xml.sax.saxutils.escape(sublabel)) #new line that leaves strings as they are.
            
    def show_help (self, *args):
        de.show_faq(HELP_FILE)

    def save (self, file=None, db=None, xml=None):
        debug("save (self, file=None, db=None, xml=None):",5)
        if file and not xml and not db:
            if re.search(".xml$",file):
                xml=file
            else:
                db=file
        if xml:
            self.exportXML(file)
        else:
            self.rd.file=db
            self.rd.save()
            self.message(_("Saved!"))
        self.loader.save_active_plugins() # relies on us being a pluggable...
        
    def quit (self):
        for c in self.conf:
            c.save_properties()
        for r in self.rc.values():
            for c in r.conf:
                c.save_properties()
            if r.edited and de.getBoolean(parent=self.app,
                                             label=_("Save your edits to %s")%r.current_rec.title):
                r.saveEditsCB()
            else: r.edited=False # in case someone else checks this (e.g. reccard on close)
        for conf in self.sl.conf:
            conf.save_properties()
        self.prefs.save()
        threads=threading.enumerate()        
        if len(threads) > 1:
            msg = "Another process is in progress"
            for t in threads:
                if "import" in t.getName(): msg = _("An import is in progress.")
                if "export" in t.getName(): msg = _("An export is in progress.")
                if "delete" in t.getName(): msg = _("A delete is in progress.")
            quit_anyway = de.getBoolean(label=msg,
                                        sublabel=_("Exit program anyway?"),
                                        custom_yes=gtk.STOCK_QUIT,
                                        custom_no=_("Don't exit!"),
                                        cancel=False)
            if quit_anyway:
                for t in threads:
                    if t.getName() !='MainThread':
                        try:
                            t.terminate()
                        except:
                            debug("Unable to terminate thread %s"%t,0)
                            # try not to lose data if this is going to
                            # end up in a force quit
                            self.save_default() 
                            return True
                if not use_threads:
                    for t in self._threads:
                        try:
                            t.terminate()
                            self.threads = self.threads - 1
                        except:
                            # try not to lose data if this is going to
                            # end up in a force quit
                            self.save_default()
                            return True
            else:
                return True
        # Delete our deleted ingredient keys -- we don't need these
        # for posterity since there is no "trash" interface for
        # ingredients anyway.
        self.rd.delete_by_criteria(self.rd.ingredients_table,{'deleted':True})
        # Save our recipe info...
        self.save()
        for r in self.rc.values():
            r.hide()

class RecTrash (RecIndex):

    default_searches = [{'column':'deleted','operator':'=','search':True}]
    RESPONSE_DELETE_PERMANENTLY = 1
    RESPONSE_UNDELETE = 2
    RESPONSE_EMPTY_TRASH = 3    
    
    def __init__ (self, rg):
        self.rg = rg
        self.rmodel = self.rg.rmodel
        self.glade = gtk.glade.XML(os.path.join(gladebase,'recipe_index.glade'))
        RecIndex.__init__(self, self.glade, self.rg.rd, self.rg)
        self.setup_main_window()
        
    def setup_main_window (self):
        self.window = gtk.Dialog(_("Trash"),
                                 self.rg.window,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 ("_Empty trash",self.RESPONSE_EMPTY_TRASH,
                                  "_Delete permanently",self.RESPONSE_DELETE_PERMANENTLY,
                                  "_Undelete",self.RESPONSE_UNDELETE,
                                  gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE))
        self.window.set_default_response(gtk.RESPONSE_CLOSE)
        #a = gtk.Alignment(); a.set_padding(12,12,12,12)
        box = gtk.VBox(); box.show()
        box.set_border_width(12)
        #a.add(box); a.show(); 
        #self.window.vbox.add(a)
        self.window.vbox.add(box)
        top_label = gtk.Label(); top_label.set_alignment(0.0,0.5)
        top_label.set_markup('<span weight="bold" size="large">'+_('Trash')+'</span>\n<i>'+_('Browse, permanently delete or undelete deleted recipes')+'</i>')
        box.pack_start(top_label,expand=False,fill=False);top_label.show()
        self.recipe_index_interface = self.glade.get_widget('recipeIndexBox')
        self.recipe_index_interface.unparent()
        box.pack_start(self.recipe_index_interface,fill=True,expand=True)
        self.recipe_index_interface.show()
        self.rg.conf.append(WidgetSaver.WindowSaver(self.window,
                                                    self.prefs.get('trash_window',
                                                                   {'size':(600,800)}),
                                                    show=False))
        self.window.connect('response',self.response_cb)

    def response_cb (self, dialog, response):
        if response==self.RESPONSE_DELETE_PERMANENTLY:
            self.purge_selected_recs()
        elif response==self.RESPONSE_UNDELETE:
            self.undelete_selected_recs()
        elif response==self.RESPONSE_EMPTY_TRASH:
            self.purge_all()
        else:
            self.dismiss()

    def dismiss (self, *args):
        self.window.hide()
        return True
    
    def show (self, *args, **kwargs):
        self.window.show(*args,**kwargs)
        self.srchentry.grab_focus()

    #def setup_search_views (self):
    #    self.last_search = ["",""]
    #    self.rvw = self.rd.fetch_all(self.rd.recipe_table,deleted=True)
    #    self.searches = self.default_searches
    #    self.sort_by = []

    def update_from_db (self):
        self.update_rmodel(self.rg.rd.fetch_all(
            self.rg.rd.recipe_table,deleted=True
            ))

    def undelete_selected_recs (self, *args):
        mod,rr = self.rectree.get_selection().get_selected_rows()
        recs = [mod[path][0] for path in rr]
        msg = ''
        for r in recs:
            msg += r.title + ', '
            self.rg.rd.modify_rec(r,{'deleted':False})
        if msg: msg = msg[0:-2] # cut off the last comma
        self.update_from_db()
        self.rg.redo_search()
        self.rg.message(_('Undeleted recipes ') + msg)

    def purge_selected_recs (self, *args):
        if not use_threads and self.rg.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to delete recipes.')
                            )
            return
        debug("recTreeDeleteRec (self, *args):",5)
        sel = self.rectree.get_selection()
        if not sel: return
        mod,rr=sel.get_selected_rows()
        recs = map(lambda path: mod[path][0],rr)
        self.rg.purge_rec_tree(recs,rr,mod)
        self.update_from_db()

    def purge_all (self, *args):
        self.rg.purge_rec_tree(self.rvw)
        self.update_from_db()

class UnitModel (gtk.ListStore):
    def __init__ (self, converter):
        debug('UnitModel.__init__',5)
        self.conv = converter
        gtk.ListStore.__init__(self, str, str)
        # the first item of each conv.units
        lst = map(lambda a: (a[1][0],a[0]), filter(lambda x: not (converter.unit_to_seconds.has_key(x[1][0])
                                                                  or
                                                                  converter.unit_to_seconds.has_key(x[0])
                                                                  )
                                                   ,
                                                   self.conv.units)
                  )
        lst.sort()
        for ulong,ushort in lst:
            iter=self.append()
            self.set_value(iter,0,ushort)
            if ulong != ushort:
                ulong = "%s (%s)"%(ulong,ushort)
            self.set_value(iter,1,"%s"%ulong)

def set_accel_paths (glade, widgets, base='<main>'):
    """A convenience function. Hand us a function and set accel
    paths based on it."""
    for s in widgets:
        w=glade.get_widget(s)
        if type(w) == gtk.MenuItem: set_path_for_menuitem(w)
        else:
            for c in w.get_children():
                if type(c) == gtk.MenuItem:
                    set_path_for_menuitem(c,base)
                else:
                    debug("Can't handle %s"%c,1)

def set_path_for_menuitem (mi, base='<main>'):
    if mi.get_children():
        accelLab = mi.get_children()[0]
        l=accelLab.get_label().replace('_','')
        path = base + '/' + l
        mi.set_accel_path(path)
    sm = mi.get_submenu()
    if sm:
        sm.set_accel_path(path)
        for c in sm.get_children():
            set_path_for_menuitem(c,path)
    
def startGUI ():
    debug("startGUI ():",4)
    # show splash screen before we do anything...
    debug("showing splash screen...",1)    
    splash = gtk.Window()
    #splash.window_set_auto_startup_notification(False)
    splash.set_property('decorated',False)
    splash.set_position(gtk.WIN_POS_CENTER)
    splash.set_icon_from_file(os.path.join(imagedir,'recbox.png'))
    splash.set_title(_('Gourmet Recipe Manager starting up...'))
    pixbuf=gtk.gdk.pixbuf_new_from_file(os.path.join(imagedir,'splash.png'))
    pixmap, mask = pixbuf.render_pixmap_and_mask()
    width, height = pixmap.get_size()
    del pixbuf
    splash.set_app_paintable(True)
    splash.resize(width, height)
    splash.realize()
    splash.window.set_back_pixmap(pixmap, False)
    splash.label = gtk.Label(_("Starting gourmet..."))
    splash.label.set_alignment(0.5,1)
    splash.label.set_justify(gtk.JUSTIFY_CENTER)
    splash.label.set_line_wrap(True)
    #pal = pango.AttrList()
    #pal.insert(pango.AttrForeground(
    #    255,255,128
    #    ))
    #splash.label.set_property('attributes',pal)
    splash.label.show()
    splash.add(splash.label)    
    del pixmap
    splash.show()
    splash.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
    #gtk.threads_enter()
    while gtk.events_pending():
        # show our GUI
        gtk.main_iteration()
    try:
        r=RecGui(splash_label=splash.label)
    except RecGui, rg:
        r=rg
    except:
        splash.hide()
        while gtk.events_pending():
            gtk.main_iteration()
        #gtk.main_quit()
        raise
    debug('hiding splash screen.',1)
    splash.hide()
    gtk.main()



class ImporterExporter:
    """Provide importer exporter classes."""
    # WARNING: This is not actually an independent class.  This is a
    # crude method of bookkeeping as we update. Everything contained
    # in this class should be reworked within a plugin system. For
    # now, we just attach it to this class so we can have cleaner code
    # and maintain old functionality as we implement plugins
    # piece-by-piece.
    # IMPORT/EXPORT - this will be reworked within a plugin framework...
    def print_recs (self, *args):
        debug('printing recipes',3)
        recs = self.get_selected_recs_from_rec_tree()
        gt.gtk_leave()
        printer.RecRenderer(self.rd, recs,
                            dialog_title=gettext.ngettext('Print %s recipe',
                                                          'Print %s recipes',
                                                          len(recs))%len(recs),
                            dialog_parent = self.app,
                            change_units = self.prefs.get('readableUnits',True)
                            )
        gt.gtk_enter()

    def export_selected_recs (self, *args): self.do_export(export_all=False)
    def export_all_recs (self, *args): self.do_export(export_all=True)

    def do_export (self, export_all=False):
        if export_all: recs = self.rd.fetch_all(self.rd.recipe_table,deleted=False,sort_by=[('title',1)])
        else: recs = self.get_selected_recs_from_rec_tree()
        self.exportManager.offer_multiple_export(recs,
                                                 self.prefs,
                                                 prog=self.set_progress_thr,
                                                 parent=self.app.get_toplevel())

    def import_pre_hook (self, *args):
        debug('import_pre_hook, gt.gtk_enter()',1)
        debug('about to run... %s'%self.rd.add_hooks[1:-1],1)
        gt.gtk_enter()

    def import_post_hook (self, *args):
        debug('import_post_hook,gt.gtk_leave()',5)
        gt.gtk_leave()

    def import_webpageg (self, *args):
        import importers.html_importer
        sublabel = _('Enter the URL of a recipe archive or recipe website.')
        url = de.getEntry(label=_('Enter website address.'),
                          sublabel=sublabel,
                          entryLabel=_('Enter URL:'),
                          entryTip=_('Enter the address of a website or recipe archive. The address should begin with http://'),
                          default_character_width=60,
                          )
        if not url: return
        if url.find('//')<0:
            url = 'http://'+url
        self.show_progress_dialog(None,
                                  progress_dialog_kwargs={'label':_('Importing recipe from %s')%url,
                                                      'stop':False,
                                                      'pause':False,})
        try:
            i=importers.html_importer.import_url(
                url,
                self.rd,
                progress=self.set_progress_thr,
                threaded=True)
            #self.rd,
            #    url,
            #    prog=self.set_progress_thr,
            #    threaded=True)
            if type(i)==list:
                impClass,cant_import = self.prepare_import_classes(i)
                if impClass:
                    self.run_import(impClass,url,display_errors=False)
                else:
                    raise NotImplementedError("Gourmet cannot import")
            else:
                self.run_import(i,url,display_errors=False)
        except NotImplementedError:
            sublabel=_('Gourmet does not know how to import site %s')%url
            sublabel += "\n"
            sublabel += _('Are you sure %(url)s points to a page with a recipe on it?')%locals()
            de.show_message(label=_('Unable to import'),
                            sublabel=sublabel,
                            message_type=gtk.MESSAGE_ERROR)
            self.hide_progress_dialog()
        except BadZipfile:
            de.show_message(label=_('Unable to unzip'),
                            sublabel=_('Gourmet is unable to unzip the file %s')%url,
                            message_type=gtk.MESSAGE_ERROR)
        except IOError:
            self.hide_progress_dialog()
            de.show_traceback(label=_('Unable to retrieve URL'),
                              sublabel=_("""Gourmet was unable to retrieve the site %s. Are you sure your internet connection is working?  If you can retrieve the site with a webbrowser but continue to get this error, please submit a bug report at %s.""")%(url,BUG_URL)
                              )
            raise
        #except gt.Terminated:
        #    if self.threads > 0: self.threads = self.threads - 1
        #    self.lock.release()
        except:
            self.hide_progress_dialog()
            de.show_traceback(
                label=_('Error retrieving %(url)s.')%locals(),
                sublabel=_('Are you sure %(url)s points to a page with a recipe on it?')%locals()
                )
            raise
        self.make_rec_visible()

    def do_import (self, *args):
        self.importManager.offer_import(self.window)

    def importg (self, *args):
        if not use_threads and self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to start your import.')
                            )
            return
        import_directory = "%s/"%self.prefs.get('rec_import_directory',None)
        debug('show import dialog',0)
        ifiles=de.select_file(
            _("Import Recipes"),
            filename=import_directory,
            filters=importers.FILTERS,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            select_multiple=True)
        if ifiles:
            self.prefs['rec_import_directory']=os.path.split(ifiles[0])[0]
            self.import_multiple_files(ifiles)
        self.make_rec_visible()
            
    def prepare_import_classes (self, files):
        """Handed multiple import files, prepare to import.

        We return a tuple (importerClasses,cant_import)

        importClass - an instance of importers.importer.MultipleImport
        which handles the actual import when their run methods are
        called.

        cant_import - a list of files we couldn't import.

        This does most of the work of import_multiple_files, but
        leaves it up to our caller to display our progress dialog,
        etc.
        """
        impClass = None            
        importerClasses = []
        cant_import = []
        # we're going to make a copy of the list and chew it up. We do
        # this rather than doing a for loop because zip files or other
        # archives can end up expanding our list
        imp_files = files[0:] 
        while files:
            fn = files.pop()
            if type(fn)==str and os.path.splitext(fn)[1] in ['.gz','.gzip','.zip','.tgz','.tar','.bz2']:
                try:
                    debug('trying to unzip %s'%fn,0)
                    from importers.zip_importer import archive_to_filelist
                    archive_files = archive_to_filelist(fn)
                    for a in archive_files:
                        if type(a) == str:
                            files += [a]
                        else:
                            # if we have file objects, we're going to write
                            # them out to real files, so we don't have to worry
                            # about details later (this is stupid, but I'm sick of
                            # tracking down places where I e.g. closed files regardless
                            # of whether I opened them)
                            finame=tempfile.mktemp(a.name)
                            tfi=open(finame,'w')
                            tfi.write(a.read())
                            tfi.close()
                            files += [finame]
                    continue
                except:
                    cant_import.append(fn)
                    raise
                    continue
            try:
                impfilt = importers.FILTER_INFO[importers.select_import_filter(fn)]
            except NotImplementedError:
                cant_import.append(fn)
                continue
            impClass = impfilt['import']({'file':fn,
                                          'rd':self.rd,
                                          'threaded':True,
                                          })
            if impfilt['get_source']:
                if type(fn)==str: fname = fn
                else: fname = "file"
                source=de.getEntry(label=_("Default source for recipes imported from %s")%fname,
                                   entryLabel=_('Source:'),
                                   default=os.path.split(fname)[1], parent=self.app)
                # the 'get_source' dict is the kwarg that gets
                # set to the source
                impClass[2][impfilt['get_source']]=source
            if impClass: importerClasses.append((impClass,fn))
            else:
                debug('GOURMET cannot import file %s'%fn)
        if importerClasses:
            impClass = importers.importer.MultipleImporter(self,
                                                           importerClasses)
            return impClass,cant_import
        else:
            return None,cant_import

    def import_multiple_files (self, files):
        """Import multiple files,  showing dialog."""
        # This should probably be moved to importer with a quiet/not quiet options
        # and all of the necessary connections handed as arguments.
        impClass,cant_import=self.prepare_import_classes(files)
        if impClass:
            filenames = filter(lambda x: isinstance(x,str), files)
            self.run_import(
                impClass,
                import_source=string.join([os.path.split(f)[1] for f in filenames],", ")
                )
        if cant_import:
            # if this is a file with a name...
            BUG_URL="http://sourceforge.net/tracker/?group_id=108118&atid=649652"
            sublabel = gettext.ngettext("Gourmet could not import the file %s",
                                            "Gourmet could not import the following files: %s",
                                            len(cant_import))%", ".join(cant_import)
            sublabel += "\n"
            sublabel += gettext.ngettext(
                "If you believe this file is in one of the formats Gourmet supports, please submit a bug report at %s and attach the file.",
                "If you believe these files are in a format Gourmet supports, please submit a bug report at %s and attach the file.",
                len(cant_import))%BUG_URL
            self.offer_url(
                label=gettext.ngettext("Cannot import file.",
                                       "Cannot import files.",
                                       len(cant_import)),
                sublabel=sublabel,
                url=BUG_URL)
            return

    def run_import (self, impClass, import_source="", display_errors=True):
        """Run our actual import and display progress dialog."""
        # we have to make sure we don't filter while we go (to avoid
        # slowing down the process too much).
        self.wait_to_filter=True
        self.last_impClass = impClass
        pre_hooks = [lambda *args: self.inginfo.disconnect_manually()]
        post_hooks = [lambda *args: self.inginfo.reconnect_manually()]
        pre_hooks.append(lambda *args: self.rd.add_hooks.insert(0,self.import_pre_hook))
        pre_hooks.append(lambda *args: self.rd.add_hooks.append(self.import_post_hook))
        self.threads += 1
        release = lambda *args: self.lock.release()
        post_hooks.extend([self.import_cleanup,
                           lambda *args: setattr(self,'last_impClass',None),
                           release])
        def show_progress_dialog (t):
            debug('showing progress dialog',3)
            gt.gtk_enter()
            if import_source:
                sublab = _('Importing recipes from %s')%import_source
            else: sublab = None
            self.rg.show_progress_dialog(
                t,
                {'label':_('Importing Recipes'),
                 'sublabel':sublab
                 })
            gt.gtk_leave()
        pre_hooks.insert(0,show_progress_dialog)
        pre_hooks.insert(0, lambda *args: self.lock.acquire())
        t=gt.SuspendableThread(impClass,name="import",
                               pre_hooks=pre_hooks, post_hooks=post_hooks,
                               display_errors=display_errors)
        if self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Your import will start once the other process is finished.'))
        debug('starting thread',2)
        debug('PRE_HOOKS=%s'%t.pre_hooks,1)
        debug('POST_HOOKS=%s'%t.post_hooks,1)
        t.start()

    @plugin_loader.pluggable_method
    def import_cleanup (self, *args):
        """Remove our threading hooks"""
        debug('import_cleanup!',1)
        self.rd.add_hooks.remove(self.import_pre_hook)
        self.rd.add_hooks.remove(self.import_post_hook)
        debug('hooks: %s'%self.rd.add_hooks,1)
        self.wait_to_filter=False
        gt.gtk_enter()
        # Update our models for category, cuisine, etc.
        self.update_attribute_models()
        # Reset our index view

        self.redo_search()
        gt.gtk_leave()

    
class StuffThatShouldBePlugins:
    # As you can tell by the name, everything in this class should
    # really be re-implemented as a plugin. Once that process is
    # complete, this class will disappear!

    def shop_recs (self, *args):
        debug("recTreeShopRec (self, *args):",5)
        rr=self.get_selected_recs_from_rec_tree()
        #r = self.recTreeSelectedRec()
        for r in rr:
            if r.servings and r.servings != "None":
                debug("servings=%s"%r.servings,5)
                serv = de.getNumber(default=float(r.servings),
                                    label=_("Number of servings of %s to shop for")%r.title,
                                    parent=self.app.get_toplevel())
                if serv: mult = float(serv)/float(r.servings)
                else:
                    debug('getNumber cancelled',2)
                    return
            else:
                mult = de.getNumber(default=float(1),
                                    label=_("Multiply %s by:")%r.title,
                                    parent=self.app.get_toplevel(),
                                    digits=2)
                if not mult:
                    mult = float(1)
            d=shopgui.getOptionalIngDic(self.rd.get_ings(r),mult,self.prefs,self)
            self.sl.addRec(r,mult,d)
            self.sl.show()


    def batch_edit_recs (self, *args):
        recs = self.get_selected_recs_from_rec_tree()
        if not hasattr(self,'batchEditor'):
            self.batchEditor =  batchEditor.BatchEditor(self)
        self.batchEditor.set_values_from_recipe(recs[0])
        self.batchEditor.dialog.run()
        # If we have values...
        if self.batchEditor.values:
            changes = self.batchEditor.values
            only_where_blank = self.batchEditor.setFieldWhereBlank
            attributes = ', '.join(changes.keys())
            msg = gettext.ngettext('Set %(attributes)s for %(num)s selected recipe?',
                                   'Set %(attributes)s for %(num)s selected recipes?',
                                   len(recs))%{'attributes':attributes,
                                               'num':len(recs),
                                               }
            msg += '\n'
            if only_where_blank:
                msg += _('Any previously existing values will not be changed.')+'\n'
            else:
                msg += _('The new values will overwrite any previously existing values.')+'\n'
            msg += '<i>'+_('This change cannot be undone.')+'</i>'
            if de.getBoolean(label=_('Set values for selected recipes'),sublabel=msg,cancel=False,
                             custom_yes=gtk.STOCK_OK,custom_no=gtk.STOCK_CANCEL,):
                for r in recs:
                    if only_where_blank:
                        changes = self.batchEditor.values.copy()
                        for attribute in changes.keys():
                            if hasattr(r,attribute) and getattr(r,attribute):
                                del changes[attribute]
                        if changes:
                            self.rd.modify_rec(r,changes)
                    else:
                        self.rd.modify_rec(r,self.batchEditor.values)
                    self.update_rec_iter(r)
            else:
                print 'Cancelled'
        self.batchEditor.dialog.hide()
        self.update_attribute_models()

    def showValueEditor (self, *args):
        if not hasattr(self,'ve'):
            self.ve=valueEditor.ValueEditor(self.rd,self)
        self.ve.valueDialog.connect('response',lambda d,r: (r==gtk.RESPONSE_APPLY and self.update_attribute_models))
        self.ve.show()

    #def email_recs (self, *args):
    #    debug('email_recs called!',1)
    #    recs = self.get_selected_recs_from_rec_tree()
    #    d=recipe_emailer.EmailerDialog(recs, self.rd, self.prefs, self.conv)
    #    d.setup_dialog()
    #    d.email()

ui = '''<ui>
<menubar name="RecipeIndexMenuBar">
  <menu name="File" action="File">
    <menuitem action="New"/>
    <menuitem action="ImportFile"/>
    <menuitem action="ImportWeb"/>
    <separator/>
    <menuitem action="ExportSelected"/>
    <menuitem action="ExportAll"/>
    <separator/>
    <placeholder name="FileMenuTool"/>
    <separator/>
    <!-- <menuitem action="Email"/> -->
    <menuitem action="Print"/>
    <separator/>
    <menuitem action="Quit"/>
  </menu>
  <!--<menu name="Edit" action="Edit">
    <menuitem action="Undo"/>
    <menuitem action="Redo"/>
  </menu>-->  
  <menu name="Actions" action="Actions">
    <menuitem action="OpenRec"/>
    <menuitem action="ShopRec"/>
    <menuitem action="DeleteRec"/>    
    <separator/>
    <menuitem action="BatchEdit"/>
  </menu>
  <menu name="Go" action="Go">
  </menu>
  <menu name="Tools" action="Tools">
    <placeholder name="StandaloneTool">
    <menuitem action="Timer"/>
    </placeholder>
    <separator/>
    <placeholder name="DataTool"/>
    <separator/>
    <menuitem action="ViewTrash"/>
  </menu>
  <menu name="Settings" action="Settings">
    <menuitem action="toggleRegexp"/>
    <menuitem action="toggleSearchAsYouType"/>
    <!--<menuitem action="toggleSearchBy"/>-->
    <separator/>
    <menuitem action="Preferences"/>
    <menuitem action="Plugins"/>
  </menu>
  <menu name="HelpMenu" action="HelpMenu">
    <menuitem action="About"/>
    <menuitem action="Help"/>
  </menu>
</menubar>

<toolbar name="RecipeIndexToolBar">
  <toolitem action="New"/>
  <toolitem action="DeleteRec"/>
  <toolitem action="OpenRec"/>
  <toolitem action="ShopRec"/>
  <toolitem action="Print"/>
</toolbar>
</ui>
'''

class RecGui (RecIndex, GourmetApplication, ImporterExporter, StuffThatShouldBePlugins, plugin_loader.Pluggable):
    def __init__ (self, splash_label=None):
        self.doing_multiple_deletions = False
        GourmetApplication.__init__(self, splash_label=splash_label)
        self.setup_index_columns()
        self.setup_hacks()
        self.glade = gtk.glade.XML(os.path.join(gladebase,'recipe_index.glade'))
        self.setup_actions()
        RecIndex.__init__(self,
                          glade=self.glade,
                          rd=self.rd,
                          rg=self,
                          editable=False)
        self.setup_database_hooks()        
        self.setup_main_window()
        self.ui_manager.insert_action_group(self.search_actions,0)
        self.window.add_accel_group(self.ui_manager.get_accel_group())
        self.setup_column_display_preferences()
        plugin_loader.Pluggable.__init__(self,
                                         [plugin.MainPlugin,plugin.ToolPlugin])

    def setup_hacks (self):
        # THese are properties that we need to set to test with our
        # current recindex class. However, each of these properties
        # should die with our redesign once done.
        self.act_on_row_widgets = []

    def setup_column_display_preferences (self, *args):
        already_hidden=self.prefs.get('rectree_hidden_columns',DEFAULT_HIDDEN_COLUMNS)
        if not already_hidden: already_hidden=[]
        def mapper (i):
            if i in already_hidden: return [i, False]
            else: return [i, True]
        options=map(lambda i: self.rtcolsdic[i], self.rtcols)
        options=map(mapper, options)
        #pd = de.preferences_dialog(options=options, option_label=None, value_label=_("Show in Index View"),
        #                           apply_func=self.configure_columns, parent=self.app)
        self.prefsGui.add_pref_table(options,
                                     'indexViewVBox',
                                     self.configure_columns)        

    def configure_columns (self, retcolumns):
        print 'Configure columns->',retcolumns
        hidden=[]
        for c,v in retcolumns:
            if not v: hidden.append(c)
        self.rectree_conf.hidden=self.prefs['rectree_hidden_columns']=hidden
        print 'Apply visibility'
        self.rectree_conf.apply_visibility()


    def setup_index_columns (self):
        self.rtcolsdic={}
        self.rtwidgdic={}
        for a,l,w in REC_ATTRS:
            self.rtcolsdic[a]=l
            self.rtwidgdic[a]=w
            self.rtcols = [r[0] for r in REC_ATTRS]        

    def setup_database_hooks (self):
        self.rd.delete_hooks.append(
            lambda self,*args: (self.doing_multiple_deletions==False and self.redo_search())
            )
        self.rd.modify_hooks.append(self.rmodel.update_recipe)
        
    def selection_changed (self, selected=False):
        if selected != self.selected:
            if selected: self.selected=True
            else: self.selected=False
            self.onSelectedActionGroup.set_sensitive(
                self.selected
                )

    def setup_main_window (self):
        self.window = self.app = gtk.Window()
        self.conf.append(WidgetSaver.WindowSaver(self.window,
                                                 self.prefs.get('app_window',
                                                                {'window_size':(800,600)}),
                                                 )
                         )
        self.window.set_title(version.appname)
        self.main = gtk.VBox()
        self.window.add(self.main)
        self.window.connect('delete-event',self.quit)
        mb = self.ui_manager.get_widget('/RecipeIndexMenuBar'); mb.show()
        self.main.pack_start(mb,fill=False,expand=False);        
        self.recipe_index_interface = self.glade.get_widget('recipeIndexBox')
        self.recipe_index_interface.unparent()
        self.main.add(self.recipe_index_interface)
        self.recipe_index_interface.show()
        self.main.show()
        self.window.show()

    def setup_actions (self):
        self.ui_manager = gtk.UIManager()
        self.ui_manager.add_ui_from_string(ui)
        self.mainActionGroup = gtk.ActionGroup('MainActions')
        self.onSelectedActionGroup = gtk.ActionGroup('IndexOnSelectedActions')
        self.onSelectedActionGroup.add_actions([
            ('OpenRec','recipe-box',_('Open recipe'),
             '<Control>O',_('Open selected recipe'),self.rec_tree_select_rec),
            ('DeleteRec',gtk.STOCK_DELETE,_('Delete recipe'),
             'Delete',_('Delete selected recipes'),self.rec_tree_delete_rec_cb),
            ('ExportSelected',None,_('E_xport selected recipes'),
             None,_('Export selected recipes to file'),self.export_selected_recs),
            ('Print',gtk.STOCK_PRINT,_('_Print'),
             '<Control>P',None,self.print_recs),
            #('Email', None, _('E-_mail recipes'),
            # None,None,self.email_recs),
            ('BatchEdit',None,_('Batch _edit recipes'),
             '<Control>E',None,self.batch_edit_recs),
            ('ShopRec','add-to-shopping-list',None,None,None,self.shop_recs)
            ])

        self.mainActionGroup.add_actions([
            ('File',None,_('_File')),
            ('Edit',None,_('_Edit')),
            ('Actions',None,_('_Actions')),
            ('Settings',None,_('Setti_ngs')),
            ('HelpMenu',None,_('_Help')),            
            ('About',gtk.STOCK_ABOUT,_('_About'),
             None,None,self.show_about),
            ('New',gtk.STOCK_NEW,_('_New'),
             None,None,self.new_rec_card),
            ('Help',gtk.STOCK_HELP,_('_Help'),
             None,None,self.show_help),
            ('ImportFile',None,_('_Import file'),
             None,_('Import recipe from file'),self.do_import),
            ('ImportWeb',None,_('Import _webpage'),
             None,_('Import recipe from webpage'),self.import_webpageg),
            ('ExportAll',None,_('Export _all recipes'),
             None,_('Export all recipes to file'),self.export_all_recs),
            ('Plugins',None,_('_Plugins'),
             None,_('Manage plugins which add extra functionality to Gourmet.'),
             lambda *args: plugin_gui.show_plugin_chooser()),
            ('Preferences',gtk.STOCK_PREFERENCES,_('_Preferences'),
             None,None,self.show_preferences),
            #('Redo',gtk.STOCK_REDO,_('_Redo'),
            # None,None),
            #('Undo',gtk.STOCK_UNDO,_('_Undo'),
            # None,None),
            ('Quit',gtk.STOCK_QUIT,_('_Quit'),
             None,None,self.quit),
            ('ViewTrash',None,_('Open _Trash'),
             None,None,self.show_deleted_recs),
            ])

        self.toolActionGroup = gtk.ActionGroup('ToolActions')
        self.toolActionGroup.add_actions([
            ('Tools',None,_('_Tools')),
            ('Timer',None,_('_Timer'),
             None,_('Show timer'),lambda *args: show_timer()),
            #('UnitConverter',None,_('_Unit Converter'),
            # None,_('Calculate unit conversions'),self.showConverter),
            ])

        
        self.goActionGroup.add_actions([
            ('GoRecipeIndex',None,_('Recipe _Index'),
             None,_('Searchable index of recipes in the database.'),self.present)]
                                       )
        self.ui_manager.insert_action_group(self.onSelectedActionGroup,0)
        self.ui_manager.insert_action_group(self.mainActionGroup,0)
        self.ui_manager.insert_action_group(self.toolActionGroup,0)
        self.add_uimanager_to_manage(-1,self.ui_manager,'RecipeIndexMenuBar')

    # Status bar stuff
    def message (self, msg):
        debug("message (self, msg): %s"%msg,5)
        self.stat.push(self.contid,msg)
        gobject.timeout_add(1500,self.flush_messages)

    def flush_messages (self, ret=False):
        debug("flush_messages (self):",5)
        self.stat.pop(self.contid)
        return ret


    # Basic callbacks
    def new_rec_card (self, *args):
        self.app.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        def show ():
            rc=reccard.RecCard(self)
            self.make_rec_visible(rc.current_rec)
            self.rc[rc.current_rec.id]=rc
            self.app.window.set_cursor(None)
            self.update_go_menu()
        gobject.idle_add(show)

    def open_rec_card (self, rec):
        if self.rc.has_key(rec.id):
            self.rc[rec.id].show()
        else:
            def show ():
                w=reccard.RecCard(self, rec)
                self.rc[rec.id]=w
                self.update_go_menu()
                self.app.window.set_cursor(None)
            self.app.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
            gobject.idle_add(show)
        

    # Extra callbacks for actions on our treeview
    def rec_tree_select_rec (self, *args):
        debug("rec_tree_select_rec (self, *args):",5)
        for rec in self.get_selected_recs_from_rec_tree():
            self.open_rec_card(rec)
    
    # Deletion
    def show_deleted_recs (self, *args):
        if not hasattr(self,'recTrash'):
            self.recTrash = RecTrash(self.rg)
            self.recTrash.show()
        else:
            self.recTrash.show()
    
    def rec_tree_delete_rec_cb (self, *args):
        """Make a watch show up (this can be slow
        if lots of recs are selected!"""
        #gtk.app.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        #gobject.idle_add(self.recTreeDeleteRec)
        # this seems broken
        sel=self.rectree.get_selection()
        if not sel: return
        mod,rr=sel.get_selected_rows()
        recs = [mod[path][0] for path in rr]
        self.rec_tree_delete_recs(recs)

    def delete_open_card_carefully (self, rec):
        """Delete any open card windows, confirming if the card is edited.

        We return True if the user cancels deletion.
        """
        if self.rc.has_key(rec.id):
            rc = self.rc[rec.id]            
            if rc.edited:
                rc.widget.present()
                if not de.getBoolean(
                    label=_('Delete %s?'),
                    sublabel=_('You have unsaved changes to %s. Are you sure you want to delete?'),
                    custom_yes=gtk.STOCK_DELETE,
                    custom_no=gtk.STOCK_CANCEL,
                    cancel=False):
                    return True
            rc.widget.hide()
            self.del_rc(rec.id)
            
    def rec_tree_delete_recs (self, recs):
        cancelled = []
        for rec in recs:
            if self.delete_open_card_carefully(rec): # returns True if user cancels
                cancelled.append(rec)
        if cancelled:
            for c in cancelled: recs.remove(c)
        self.rd.undoable_delete_recs(
            [self.rd.get_rec(r.id) for r in recs],
            self.history,
            make_visible=lambda *args: self.redo_search()
            )
        self.set_reccount()
        if hasattr(self,'recTrash'):
            self.recTrash.update_from_db()
        self.message(_("Deleted") + ' ' + string.join([(r.title or _('Untitled')) for r in recs],', '))

    def purge_rec_tree (self, recs, paths=None, model=None):
        if not use_threads and self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to delete recipes.')
                            )
            return
        if not recs:
            # Do nothing if there are no recipes to delete.
            return
        if not paths: paths=[]
        expander=None
        bigmsg = _("Permanently delete recipes?")
        if len(recs) == 1:
            bigmsg = _("Permanently delete recipe?")
            msg = _("Are you sure you want to delete the recipe <i>%s</i>")%recs[0].title
        elif len(recs) < 5:
            msg = _("Are you sure you want to delete the following recipes?")
            for r in recs:
                msg += "\n<i>%s</i>"%r.title
        else:
            msg = _("Are you sure you want to delete the %s selected recipes?")%len(recs)
            tree = te.QuickTree([r.title for r in recs])
            expander = [_("See recipes"),tree]
        if de.getBoolean(parent=self.app,label=bigmsg,sublabel=msg,expander=expander):
            self.redo_search() # update all

            def show_progress (t):
                gt.gtk_enter()
                self.show_progress_dialog(t,
                                          progress_dialog_kwargs={'label':'Deleting recipes'},
                                          message=_('Deletion paused'), stop_message=_("Stop deletion"))
                gt.gtk_leave()
            def save_delete_hooks (t):
                self.saved_delete_hooks = self.rd.delete_hooks[0:]
                self.rd.delete_hooks = []
            def restore_delete_hooks (t):
                self.rd.delete_hooks = self.saved_delete_hooks
            pre_hooks = [
                lambda *args: self.lock.acquire(),
                save_delete_hooks,
                show_progress,
                ]
            post_hooks = [
                restore_delete_hooks,
                lambda *args: self.lock.release()]
            t=gt.SuspendableThread(gt.SuspendableDeletions(self, recs),
                                name='delete',
                                pre_hooks = pre_hooks,
                                post_hooks = post_hooks)
            if self.lock.locked_lock():
                de.show_message(label=_('An import, export or deletion is running'),
                                sublabel=_('The recipes will be deleted once the other process is finished.')
                                )
            debug('PRE_HOOKS=%s'%t.pre_hooks,1)
            debug('POST_HOOKS=%s'%t.post_hooks,1)
            debug('rd.add_hooks=%s'%self.rd.add_hooks,1)
            gt.gtk_leave()
            t.start()
            gt.gtk_enter()
        else:
            return True

    def delete_rec (self, rec):
        debug("delete_rec (self, rec): %s"%rec,5)
        debug("does %s have %s"%(self.rc,rec.id),5)
        if self.rc.has_key(rec.id):
            debug("Getting rid of open recipe card window.",2)
            w=self.rc[rec.id].widget
            self.rc[rec.id].hide()
            w.destroy()
            self.update_go_menu()
        if hasattr(rec,'id') and rec.id:
            if rec:
                titl = rec.title
                debug('deleting recipe %s'%rec.title,1)
                # try a workaround to segfaults -- grab rec anew from ID.
                dbrec = self.rd.get_rec(rec.id)
                if dbrec:
                    self.rd.delete_rec(dbrec)
                else:
                    print 'wtf?!?',rec,':',rec.id,' not real?'
            else: debug('no recipe to delete!?!',1)
            if not self.doing_multiple_deletions:
                gt.gtk_enter()
                self.message(_("Deleted recipe %s")%titl)
                self.doing_multiple_deletions=False
                gt.gtk_leave()
        else:
            debug("%s %s does not have an ID!"%(rec,rec.title),2)
        debug("returning None",2)
        return None
    # end deletion

    # end Extra Callbacks for actions on treeview

    def after_dialog_offer_url (self, linktype, file):
        url = "file:///%s"%file
        label = _("Export succeeded")
        if linktype == exporters.WEBPAGE:
            url += '/index.htm'
            linktype = _("webpage")
        sublabel = _("Exported %s to %s")%(linktype,file)
        def offerer (t):
            if t.completed:
                #self.idle_offer_url(label, sublabel, url, True)
                self.offer_url(label, sublabel, url, True)
        return offerer

    def idle_offer_url (self, label, sublabl, url, from_thread):
        if from_thread:
            gt.gtk_enter()
        gobject.idle_add(lambda *args: self.offer_url(label,sublabl,url,True))
        if from_thread:
            gt.gtk_leave()

    def offer_url (self, label, sublabel, url, from_thread=False):
        if from_thread:
            gt.gtk_enter()
        if hasattr(self,'progress_dialog'):
            self.hide_progress_dialog()            
        d=de.MessageDialog(label=label,
                           sublabel=sublabel,
                           cancel=False
                           )
        b = gtk.Button(stock=gtk.STOCK_JUMP_TO)
        b.connect('clicked',lambda *args: launch_url(url))
        d.vbox.pack_end(b,expand=False)
        b.show()
        d.run()
        if from_thread:
            gt.gtk_leave()

    # Methods to handle threading
    def pause_cb (self, button, *args):
        if button.get_active():
            debug('Suspending thread from pause_cb',0)
            self.thread.suspend()
            self.stat.push(self.pauseid, self.pause_message)
            self.flusher = gobject.timeout_add(1000,lambda *args: self.flush_messages(True))
        else:
            self.stat.pop(self.pauseid)            
            gobject.source_remove(self.flusher)
            self.thread.resume()
            
    def stop_cb (self, *args):
        debug('Stop_cb called; pausing thread',1)
        self.thread.suspend()
        if de.getBoolean(label=self.stop_message):
            debug('Stopping thread from stop cb',0)
            self.thread.terminate()
            if self.threads > 0:
                self.threads = self.threads - 1
                try: self.lock.release()
                except: pass
            self.hide_progress_dialog()
        else:
            debug('Resuming thread: stop_cb cancelled',0)
            self.thread.resume()
            return True

    def reset_prog_thr (self,message=_("Done!")):
        debug('reset_prog_thr',0)
        #self.prog.set_fraction(1)
        self.set_progress_thr(1,message)
        gt.gtk_enter()
        self.set_reccount()
        gt.gtk_leave()

    def set_progress_thr (self, prog, message=_("Importing...")):
        debug("set_progress_thr (self, %s,%s)"%(prog,message),1)
        gt.gtk_enter()
        if hasattr(self,'progress_dialog'):
            self.progress_dialog.set_progress(prog,message)
        gt.gtk_leave()
        
    # Stuff to show and destroy ourselves

    def present (self, *args): self.window.present()
    
    def quit (self, *args):
        GourmetApplication.quit(self)
        self.window.destroy()
        gtk.main_quit()

def get_application ():
    try:
        return RecGui()
    except RecGui, rg:
        return rg

if __name__ == '__main__' and False:
    if os.name!='nt':
        import profile, tempfile,os.path
        import hotshot, hotshot.stats
        #profi = os.path.join(tempfile.tempdir,'GOURMET_PROFILE')
        prof = hotshot.Profile(os.path.join(tempfile.tempdir,'GOURMET_HOTSHOT_PROFILE'))
        prof.runcall(startGUI)
        stats = hotshot.stats.load(os.path.join(tempfile.tempdir,'GOURMET_HOTSHOT_PROFILE'))
        stats.strip_dirs()
        stats.sort_stats('time','calls').print_stats()
        #profile.run('startGUI()',profi)
        #import pstats
        #p=pstats.Stats(profi)
        #p.strip_dirs().sort_stats('cumulative').print_stats()
    else:
        startGUI()

elif __name__ == '__main__':
    rgn = RecGui()
    gtk.main()
