import re
import threading
from gettext import ngettext
from pkgutil import get_data
from typing import Set

from gi.repository import Gdk, GLib, GObject, Gtk

from gourmet import (batchEditor, convert, plugin, plugin_gui, plugin_loader,
                     prefs, prefsGui, reccard, recipeManager, shopgui, version)
from gourmet.defaults.defaults import get_pluralized_form
from gourmet.defaults.defaults import lang as defaults
from gourmet.exporters.exportManager import ExportManager
from gourmet.exporters.printer import PrintManager
from gourmet.gdebug import debug
from gourmet.gglobals import DEFAULT_HIDDEN_COLUMNS, REC_ATTRS
from gourmet.gtk_extras import WidgetSaver
from gourmet.gtk_extras import dialog_extras as de
from gourmet.gtk_extras import (fix_action_group_importance, mnemonic_manager,
                                ratingWidget)
from gourmet.gtk_extras import treeview_extras as te
from gourmet.i18n import _
from gourmet.image_utils import load_pixbuf_from_resource
from gourmet.importers.importManager import ImportManager
from gourmet.plugins.clipboard_exporter import ClipboardExporter
from gourmet.recindex import RecIndex
from gourmet.threadManager import (SuspendableThread, get_thread_manager,
                                   get_thread_manager_gui)
from gourmet.timer import show_timer

UNDO = 1
SHOW_TRASH = 2


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

    @classmethod
    def instance(cls):
        if GourmetApplication.__single is None:
            GourmetApplication.__single = cls()

        return GourmetApplication.__single

    def __init__ (self):
        self.conv = convert.get_converter()
        self.star_generator = ratingWidget.StarGenerator()
        # Setup methods...
        self.setup_prefs() # Setup preferences...
        self.setup_plugins()
        self.setup_recipes() # Setup recipe database
        #self.setup_nutrition()
        self.setup_shopping()
        self.setup_go_menu()
        self.rc={}

    def setup_plugins (self):
        pass

    def show_preferences (self, *args):
        self.prefsGui.show_dialog(page=self.prefsGui.INDEX_PAGE)

    # Setup preferences system
    def setup_prefs (self):
        self.conf = []
        self.prefs = prefs.Prefs.instance()
        self.prefsGui = prefsGui.PreferencesGui(
            self.prefs,
            buttons={'clear_remembered_optional_button':\
                    lambda *args: self.forget_remembered_optional_ingredients()}
            )
        self.prefsGui.apply_prefs_dic['recipes_per_page'] = lambda p,v: getattr(getattr(self,'rmodel'),
                                                                               'change_items_per_page')(v)

        def toggleFractions (prefname,use):
            if use:
                convert.USE_FRACTIONS = convert.FRACTIONS_NORMAL
            else:
                convert.USE_FRACTIONS = convert.FRACTIONS_OFF
        self.prefsGui.apply_prefs_dic['useFractions'] = toggleFractions
        # Call our method once with the default prefs to apply saved
        # user settings
        toggleFractions(None,
                        self.prefs.get('useFractions',
                                       defaults.LANG_PROPERTIES['useFractions']
                                       )
                        )

    # Convenience method for showing progress dialogs for import/export/deletion
    def show_progress_dialog (self, thread, progress_dialog_kwargs=None,
                              message=_("Import paused"),
                              stop_message=_("Stop import")):
        """Show a progress dialog"""
        if progress_dialog_kwargs is None:
            progress_dialog_kwargs = dict()
        name = getattr(thread, 'name', '')
        for k,v in [('okay',True),
                    ('label',name),
                    ('parent',self.app),
                    ('pause',self.pause_cb),
                    ('stop',self.stop_cb),
                    ('modal',False),]:
            if k not in progress_dialog_kwargs:
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
    def setup_recipes(self):
        """Initialize recipe database from the recipe manager."""
        self.rd = recipeManager.default_rec_manager()

        # Add auto save
        def autosave():
            self.rd.save()
            return True

        autosave_timeout = 2 * 60 * 1000  # in milliseconds
        GLib.timeout_add(autosave_timeout, autosave)

        # Connect views to update on modifications
        self.rd.modify_hooks.append(self.update_attribute_models)
        self.rd.add_hooks.append(self.update_attribute_models)
        self.rd.delete_hooks.append(self.update_attribute_models)

        # Create models that are accessed by other objects
        self.umodel = UnitModel(self.conv)
        self.attributeModels = []
        self.inginfo = reccard.IngInfo(self.rd)

    def setup_shopping (self):
        """Setup shopping related stuff"""
        #self.create_rmodel(self.rd.recipe_table)
        self.sl = shopgui.ShopGui()
        self.sl.hide()

    # Methods for keeping track of open recipe cards...
    def del_rc (self, id):
        """Forget about recipe card identified by id"""
        if id in self.rc:
            del self.rc[id]
        self.update_go_menu()

    def update_reccards (self, rec):
        if rec.id in self.rc:
            rc=self.rc[rec.id]
            rc.updateRecipe(rec,show=False)
            self.update_go_menu()

    def go_menu (self):
        """Build a _View menu based on recipes currently
        opened in recipe cards."""
        m=Gtk.Menu()
        ri=Gtk.MenuItem(_('Recipe _Index'))
        sh=Gtk.MenuItem(_('Shopping _List'))
        separator=Gtk.MenuItem()
        ri.connect('activate',lambda *args: self.app.present())
        sh.connect('activate',self.sl.show)
        m.append(ri)
        ri.show()
        m.append(sh)
        sh.show()
        m.append(separator)
        separator.show()
        for rc in list(self.rc.values()):
            i=Gtk.MenuItem("_%s"%rc.current_rec.title)
            i.connect('activate', lambda *args: rc.show())
            m.append(i)
            i.show()
        return m

    def setup_go_menu (self):
        self.goActionGroup = Gtk.ActionGroup(name='GoActions')
        self.goActionGroup.add_actions([('Go',None,_('_Go'))])
        self.uimanagers = {}
        self.merged_go_menus = {}

    def add_uimanager_to_manage (self, id, uimanager, menu_root_name):
        fix_action_group_importance(self.goActionGroup)
        uimanager.insert_action_group(self.goActionGroup,0)
        uimanager.add_ui_from_string(self.shared_go_menu%{'name':menu_root_name})
        self.uimanagers[id] = [uimanager,menu_root_name,
                               {} # a dictionary of added menu items
                               ]

    def update_action_group(self):
        """Attach actions for this recipe, using its title."""
        for rc in self.rc.values():
            action_name = f'GoRecipe{rc.current_rec.id}'
            title = rc.current_rec.title or 'Untitled'
            title = f'_{title}'

            existing_action = self.goActionGroup.get_action(action_name)
            if not existing_action:
                self.goActionGroup.add_actions([(
                    action_name, None, title, None, None, lambda *args: rc.show()
                )])
            else:
                existing_action.set_property('label', title)

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
        for rc in list(self.rc.values()):
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
            if idkey not in self.rc:
                uimanager.remove_ui(merged_dic[idkey])

    def update_attribute_models(self):
        """Methods to keep one set of listmodels for each attribute for
           which we might want text completion or a dropdown...
        """
        for attr, mod in self.attributeModels:
            self.update_attribute_model(attr)

    def update_attribute_model(self, attribute: str) -> Gtk.ListStore:
        slist = self.create_attribute_list(attribute)
        model = getattr(self, f'{attribute}Model')
        for n, item in enumerate(slist):
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

    def create_attribute_list(self, attribute: str) -> Set[str]:
        """Create a ListModel with unique values of attribute.
        """
        if attribute == 'category':
            slist = self.rg.rd.get_unique_values(attribute,
                                                 self.rg.rd.categories_table)
        else:
            slist = self.rg.rd.get_unique_values(attribute, deleted=False)
        if not slist:
            slist = self.rg.rd.get_default_values(attribute)
        else:
            for default_value in self.rg.rd.get_default_values(attribute):
                if default_value not in slist:
                    slist.append(default_value)

        slist = sorted(slist)
        if 'None' in slist:
            slist.remove('None')
        slist = set(slist)
        return slist

    def get_attribute_model(self, attribute: str) -> Gtk.ListStore:
        """Return a ListModel with a unique list of values for attribute.
        """
        # This was stored here so that all the different comboboxes that
        # might need e.g. a list of categories can share 1 model and
        # save memory.
        slist = self.create_attribute_list(attribute)
        store = Gtk.ListStore(str)
        for element in slist:
            store.append([element])

        setattr(self, f'{attribute}Model', store)
        self.attributeModels.append((attribute, store))
        return store

    # About/Help
    def show_about (self, *args):
        """Show information about ourselves."""
        debug("show_about (self, *args):",5)
        translator=_("translator-credits")
        # translators should translate the string 'translator-credits'
        # If we're not using a translation, then this isn't shown
        if translator == "translator-credits":
            translator = None
        # Grab CREDITS from our defaults_LANG file too!
        if hasattr(defaults,'CREDITS') and defaults.CREDITS:
            if translator and translator.find(defaults.CREDITS) > -1:
                translator += "\n%s"%defaults.CREDITS
            else:
                translator = defaults.CREDITS

        logo = load_pixbuf_from_resource('gourmet.svg')

        # load LICENSE text file
        license_text = get_data('gourmet', 'data/LICENSE').decode()
        assert license_text

        paypal_link = """https://www.paypal.com/cgi-bin/webscr?cmd=_donations
&business=Thomas_Hinkle%40alumni%2ebrown%2eedu
&lc=US&item_name=Gourmet%20Recipe%20Manager%20Team&no_note=0&currency_code=USD
&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHostedGuest"""
        gratipay_link = "https://gratipay.com/on/github/thinkle/"
        flattr_link = "http://flattr.com/profile/Thomas_Hinkle/things"

        about = Gtk.AboutDialog(parent=self.window)
        about.set_artists(version.artists)
        about.set_authors(version.authors)
        about.set_comments(version.description)
        about.set_copyright(version.copyright)
        #about.set_documenters(None)
        about.set_license(license_text)
        about.set_logo(logo)
        about.set_program_name(version.appname)
        about.set_translator_credits(translator)
        about.set_version(version.version)
        #about.set_wrap_license(True)
        about.set_website(version.url)
        #about.set_website_label('Gourmet website')

        donation_buttons = Gtk.HButtonBox()
        donation_buttons.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        donations_label = Gtk.Label(_("Please consider making a donation to "
        "support our continued effort to fix bugs, implement features, "
        "and help users!"))
        donations_label.set_line_wrap(True)
        donations_label.show()
        paypal_button = Gtk.LinkButton(paypal_link, _("Donate via PayPal"))
        paypal_button.show()
        flattr_button = Gtk.LinkButton(flattr_link, _("Micro-donate via Flattr"))
        flattr_button.show()
        gratipay_button = Gtk.LinkButton(gratipay_link, _("Donate weekly via Gratipay"))
        gratipay_button.show()
        donation_buttons.add(paypal_button)
        donation_buttons.add(gratipay_button)
        donation_buttons.add(flattr_button)
        donation_buttons.show()
        content = about.get_content_area()
        content.add(donations_label)
        content.add(donation_buttons)

        about.run()
        about.destroy()

    def show_help (self, *args):
        de.show_faq(parent=self.window)

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
        # TODO: check if this method is called.
        for c in self.conf:
            c.save_properties()
        for r in list(self.rc.values()):
            for c in r.conf:
                c.save_properties()
            if r.edited and de.getBoolean(parent=self.app,
                                             label=_("Save your edits to %s")%r.current_rec.title):
                r.recipe_editor.save_cb()
            else:
                r.edited=False # in case someone else checks this (e.g. reccard on close)
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
                                        custom_yes=Gtk.STOCK_QUIT,
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
                            #self.save_default()
                            return True
                if not use_threads:
                    for t in self._threads:
                        try:
                            t.terminate()
                            self.threads = self.threads - 1
                        except:
                            # try not to lose data if this is going to
                            # end up in a force quit
                            #self.save_default()
                            return True
            else:
                return True
        # Delete our deleted ingredient keys -- we don't need these
        # for posterity since there is no "trash" interface for
        # ingredients anyway.
        self.rd.delete_by_criteria(self.rd.ingredients_table,{'deleted':True})
        # Save our recipe info...
        self.save()
        for r in list(self.rc.values()):
            r.hide()

class SuspendableDeletions (SuspendableThread):

    def __init__ (self, recs, name=None):
        self.recs = recs
        self.rg = RecGui.instance()
        SuspendableThread.__init__(self, name=name)

    def do_run (self):
        tot = len(self.recs)
        for n,r in enumerate(self.recs):
            self.check_for_sleep()
            self.rg.rd.delete_rec(r)
            self.emit('progress',float(n)/tot,_('Permanently deleted %s of %s recipes')%(n,tot))

class RecTrash (RecIndex):

    default_searches = [{'column':'deleted','operator':'=','search':True}]
    RESPONSE_DELETE_PERMANENTLY = 1
    RESPONSE_UNDELETE = 2
    RESPONSE_EMPTY_TRASH = 3

    def __init__ (self, rg):
        self.rg = rg
        self.rmodel = self.rg.rmodel
        self.ui=Gtk.Builder()
        self.ui.add_from_string(get_data('gourmet', 'ui/recipe_index.ui').decode())
        RecIndex.__init__(self, self.ui, self.rg.rd, self.rg)
        self.setup_main_window()

    def setup_main_window (self):
        self.window = Gtk.Dialog(_("Trash"),
                                 self.rg.window,
                                 Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 ("_Empty trash",self.RESPONSE_EMPTY_TRASH,
                                  "_Delete permanently",self.RESPONSE_DELETE_PERMANENTLY,
                                  "_Undelete",self.RESPONSE_UNDELETE,
                                  Gtk.STOCK_CLOSE,Gtk.ResponseType.CLOSE))
        self.window.set_default_response(Gtk.ResponseType.CLOSE)
        #a = Gtk.Alignment.new(); a.set_padding(12,12,12,12)
        box = Gtk.VBox(); box.show()
        box.set_border_width(12)
        #a.add(box); a.show();
        #self.window.vbox.add(a)
        self.window.vbox.add(box)
        top_label = Gtk.Label(); top_label.set_alignment(0.0,0.5)
        top_label.set_markup('<span weight="bold" size="large">'\
                +_('Trash')+'</span>\n<i>'\
                +_('Browse, permanently delete or undelete deleted recipes')+'</i>')
        box.pack_start(top_label, expand=False, fill=False, padding=0)
        top_label.show()
        self.recipe_index_interface = self.ui.get_object('recipeIndexBox')
        self.recipe_index_interface.unparent()
        box.pack_start(self.recipe_index_interface, fill=True,
                       expand=True, padding=0)
        self.recipe_index_interface.show()
        self.rg.conf.append(WidgetSaver.WindowSaver(self.window,
                                                    self.prefs.get('trash_window',
                                                                   {'size':(600,800)}),
                                                    show=False))
        self.window.connect('response',self.response_cb)
        # So we can let delete key delete recipe when treeview is focused

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
        debug("recTreeDeleteRec (self, *args):",5)
        sel = self.rectree.get_selection()
        if not sel: return
        mod,rr=sel.get_selected_rows()
        recs = [mod[path][0] for path in rr]
        self.rg.purge_rec_tree(recs,rr,mod)
        self.update_from_db()

    def purge_all (self, *args):
        self.rg.purge_rec_tree(self.rvw)
        self.update_from_db()

class UnitModel (Gtk.ListStore):
    def __init__ (self, converter):
        debug('UnitModel.__init__',5)
        self.conv = converter
        Gtk.ListStore.__init__(self, str, str)
        # the first item of each conv.units
        ## areckx: is there a reason why this is formatted this way?
        lst = [(a[1][0],a[0]) for a in [x for x in self.conv.units if not (x[1][0] in converter.unit_to_seconds
                                                                  or
                                                                  x[0] in converter.unit_to_seconds
                                                                  )]]
        ##
        lst.sort()
        for ulong,ushort in lst:
            iter=self.append()
            self.set_value(iter,0,ushort)
            if ulong != ushort:
                ulong = "%s (%s)"%(ulong,ushort)
            self.set_value(iter,1,"%s"%ulong)

def set_accel_paths (ui, widgets, base='<main>'):
    """A convenience function. Hand us a function and set accel
    paths based on it."""
    for s in widgets:
        w=ui.get_object(s)
        if type(w) == Gtk.MenuItem: set_path_for_menuitem(w)
        else:
            for c in w.get_children():
                if type(c) == Gtk.MenuItem:
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

def launch_webbrowser(dialog, link, user_data):
    import webbrowser
    webbrowser.open_new_tab(link)


def launch_app():
    RecGui.instance()
    Gtk.main()


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
        printManager = PrintManager.instance()
        printManager.print_recipes(
            self.rd,
            recs,
            parent=self.app,
            change_units=self.prefs.get('readableUnits',True)
            )

    __import_manager = None

    @property
    def importManager(self):
        if self.__import_manager is None:
            self.__import_manager = ImportManager.instance()
        return self.__import_manager

    def import_webpageg(self, action: Gtk.Action):
        self.importManager.offer_web_import(parent=self.app.get_toplevel())

    def do_import(self, action: Gtk.Action):
        self.importManager.offer_import(parent=self.app.get_toplevel())

    __export_manager = None

    @property
    def exportManager(self):
        # FIXME: The export manager is a singleton, this property can be
        # refactored out.
        if self.__export_manager is None:
            self.__export_manager = ExportManager.instance()
        return self.__export_manager

    def do_export (self, export_all=False):
        if export_all:
            recs = self.rd.fetch_all(self.rd.recipe_table,deleted=False,sort_by=[('title',1)])
        else:
            recs = self.get_selected_recs_from_rec_tree()
        self.exportManager.offer_multiple_export(
            recs,
            self.prefs,
            prog=self.set_progress_thr,
            parent=self.app.get_toplevel(),
            export_all=True)


class StuffThatShouldBePlugins:
    # As you can tell by the name, everything in this class should
    # really be re-implemented as a plugin. Once that process is
    # complete, this class will disappear!

    def shop_recs (self, *args):
        debug("recTreeShopRec (self, *args):",5)
        rr=self.get_selected_recs_from_rec_tree()
        #r = self.recTreeSelectedRec()
        for r in rr:
            if r.yields and r.yields != "None":
                debug("yields=%s"%r.yields,5)
                serv = de.getNumber(default=float(r.yields),
                                    label=_("Number of %(unit)s of %(title)s to shop for")%{
                        'title':r.title,
                        'unit':get_pluralized_form(r.yield_unit,2),
                        },
                                    parent=self.app.get_toplevel()
                                    )
                if serv: mult = float(serv)/float(r.yields)
                else:
                    debug('getNumber cancelled',2)
                    return
            else:
                mult = de.getNumber(default=float(1),
                                    label=_("Multiply %s by:")%r.title,
                                    parent=self.app.get_toplevel(),
                                    digits=2)
                if not mult:
                    debug('getNumber cancelled', 2)
                    return
            d=self.sl.getOptionalIngDic(self.rd.get_ings(r),mult,self.prefs)
            self.sl.addRec(r,mult,d)
            self.sl.show()

    def copy_recipes_callback(self, action: Gtk.Action):
        recipes = self.get_selected_recs_from_rec_tree()
        ingredients = [self.rd.rd.get_ings(recipe.id)
                       for recipe in recipes]
        ce = ClipboardExporter(list(zip(recipes, ingredients)))
        ce.export()

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
            attributes = ', '.join([_(k) for k in list(changes.keys())])
            msg = ngettext('Set %(attributes)s for %(num)s selected recipe?',
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
                             custom_yes=Gtk.STOCK_OK,custom_no=Gtk.STOCK_CANCEL,):
                for r in recs:
                    # Need to copy in case we're dealing with
                    # categories as they would get messed up by
                    # modify_rec
                    changes = self.batchEditor.values.copy()
                    if only_where_blank:
                        for attribute in list(changes.keys()):
                            if (attribute == 'category' and \
                                self.rd.get_cats(r)) or \
                                (hasattr(r, attribute) and \
                                getattr(r, attribute)):
                                del changes[attribute]
                        if changes:
                            self.rd.modify_rec(r,changes)
                    else:
                        self.rd.modify_rec(r,changes)
                    self.rmodel.update_recipe(r)
            else:
                print('Cancelled')
        self.batchEditor.dialog.hide()
        self.update_attribute_models()

ui_string = '''<ui>
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
    <menuitem action="CopyRecipes"/>
    <menuitem action="EditRec"/>
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
    <menuitem action="search_regex_toggle"/>
    <menuitem action="search_typing_toggle"/>
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

class RecGui (RecIndex, GourmetApplication, ImporterExporter, StuffThatShouldBePlugins, plugin_loader.Pluggable, BaseException):

    __single = None

    @classmethod
    def instance(cls):
        if RecGui.__single is None:
            RecGui.__single = cls()

        return RecGui.__single

    def __init__(self):
        self.ui_manager = Gtk.UIManager()
        self.ui_manager.add_ui_from_string(ui_string)

        self.doing_multiple_deletions = False
        GourmetApplication.__init__(self)
        self.setup_index_columns()
        self.setup_hacks()
        self.ui = Gtk.Builder()
        self.ui.add_from_string(get_data('gourmet', 'ui/recipe_index.ui').decode())  # noqa
        self.setup_actions()
        RecIndex.__init__(self,
                          ui=self.ui,
                          rd=self.rd,
                          rg=self,
                          editable=False)
        self.setup_database_hooks()

        fix_action_group_importance(self.search_actions)
        self.ui_manager.insert_action_group(self.search_actions, 0)

        self.setup_main_window()
        self.window.add_accel_group(self.ui_manager.get_accel_group())
        self.setup_column_display_preferences()
        self.setup_toolbar_display_preferences()
        plugin_loader.Pluggable.__init__(self,
                                         [plugin.MainPlugin,plugin.ToolPlugin])
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.add_toplevel_widget(self.window)
        self.mm.fix_conflicts_peacefully()
        self.window.show()

    def setup_hacks (self):
        # These are properties that we need to set to test with our
        # current recindex class. However, each of these properties
        # should die with our redesign once done.
        self.act_on_row_widgets = []

    def setup_column_display_preferences (self, *args):
        already_hidden=self.prefs.get('rectree_hidden_columns',DEFAULT_HIDDEN_COLUMNS)
        if not already_hidden: already_hidden=[]
        options=[self.rtcolsdic[i] for i in self.rtcols]
        options=[[i, i not in already_hidden] for i in options]
        #pd = de.preferences_dialog(options=options, option_label=None, value_label=_("Show in Index View"),
        #                           apply_func=self.configure_columns, parent=self.app)
        self.prefsGui.add_pref_table(options,
                                     'indexViewVBox',
                                     self.configure_columns)

    def setup_toolbar_display_preferences (self):
        def toggleToolbar (prefname,use):
            tb = self.ui_manager.get_widget('/RecipeIndexToolBar')
            if use:
                tb.show()
            else:
                tb.hide()
        self.prefsGui.apply_prefs_dic['showToolbar'] = toggleToolbar
        # Call our method once with the default prefs to apply saved
        # user settings
        toggleToolbar(None, self.prefs.get('showToolbar',True))

    def configure_columns (self, retcolumns):
        hidden=[]
        for c,v in retcolumns:
            if not v: hidden.append(c)
        self.rectree_conf.hidden=self.prefs['rectree_hidden_columns']=hidden
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

    def selection_changed(self, selected=False):
        if selected != self.selected:
            self.selected = selected
            self.onSelectedActionGroup.set_sensitive(self.selected)

    def setup_main_window(self):
        self.window = self.app = Gtk.Window()
        self.window.set_icon(load_pixbuf_from_resource('gourmet.svg'))
        saver = WidgetSaver.WindowSaver(
            self.window,
            self.prefs.get('app_window', {'window_size': (800, 600)})
        )
        self.conf.append(saver)

        self.window.set_default_size(*self.prefs['app_window']['window_size'])
        self.window.set_title(version.appname)
        self.main = Gtk.VBox()
        self.window.add(self.main)
        self.window.connect('delete-event',self.quit)
        mb = self.ui_manager.get_widget('/RecipeIndexMenuBar'); mb.show()
        self.main.pack_start(mb,False,False,0)
        tb = self.ui_manager.get_widget('/RecipeIndexToolBar')
        self.main.pack_start(tb,False,False,0)
        self.messagebox = Gtk.VBox()
        self.main.pack_start(self.messagebox,False,False,0)
        self.main_notebook = Gtk.Notebook()
        self.recipe_index_interface = self.ui.get_object('recipeIndexBox')
        self.recipe_index_interface.unparent()
        self.main_notebook.append_page(self.recipe_index_interface,
                                       tab_label=Gtk.Label(label=_('Search recipes')))
        self.main.add(self.main_notebook)
        self.recipe_index_interface.show()

        self.main_notebook.show(); self.main_notebook.set_show_tabs(False)

        # Set up right-clicking again
        self.rectree.connect('popup-menu',self.rectree_popup)
        def popcb (tv, event):
            if event.button==3:
                self.rectree_popup(tv,event)
                return True
        # Set up popup menu in treeview
        self.rectree.connect('button-press-event',popcb)
        # Set up delete key in recipe treeview
        self.rectree.connect('key-press-event',self.rec_tree_keypress_cb)
        self.srchentry.grab_focus()
        self.main.show()

    def rectree_popup (self, tv, event, *args):
        menu = self.ui_manager.get_widget("/RecipeIndexMenuBar/Actions/").get_submenu()
        menu.popup_at_pointer(None)
        return True

    def setup_actions(self):
        self.onSelectedActionGroup = Gtk.ActionGroup(name='IndexOnSelectedActions')  # noqa
        self.onSelectedActionGroup.add_actions([
            ('OpenRec','recipe-card',_('Open recipe'),
             '<Control>O',_('Open selected recipe'),self.rec_tree_select_rec),
            ('DeleteRec',Gtk.STOCK_DELETE,_('Delete recipe'),
             None,_('Delete selected recipes'),self.rec_tree_delete_rec_cb),
            ('EditRec',Gtk.STOCK_EDIT,_('Edit recipe'),
             '<Control>E',_('Open selected recipes in recipe editor view'),
             self.rec_tree_edit_rec),
            ('ExportSelected',None,_('E_xport selected recipes'),
             '<Control>T',_('Export selected recipes to file'),
             lambda *args: self.do_export(export_all=False)),
            ('Print',Gtk.STOCK_PRINT,_('_Print'),
             '<Control>P',None,self.print_recs),
            ('CopyRecipes', Gtk.STOCK_COPY, _('_Copy recipes'),
             '<Control>C', None, self.copy_recipes_callback),
            ('BatchEdit',None,_('Batch _edit recipes'),
             '<Control><Shift>E',None,self.batch_edit_recs),
            ('ShopRec', 'add-to-shopping-list', _('Add to Shopping List'),
             '<Control>B', None, self.shop_recs)
            ])

        self.mainActionGroup = Gtk.ActionGroup(name='MainActions')
        self.mainActionGroup.add_actions([
            ('File',None,_('_File')),
            ('New',Gtk.STOCK_NEW,_('_New'),
             None,None,self.new_rec_card),
            ('ImportFile',None,_('_Import file'),
             '<Control>M',_('Import recipe from file'),self.do_import),
            ('ImportWeb',None,_('Import _webpage'),
             '<Control><Shift>M',_('Import recipe from webpage'),self.import_webpageg),
            ('ExportAll',None,_('Export _all recipes'),
             '<Control><Shift>T',_('Export all recipes to file'),lambda *args: self.do_export(export_all=True)),
            ('Quit', Gtk.STOCK_QUIT, _('_Quit'),
             None, None, self.quit),

            ('Actions',None,_('_Actions')),
            ('Edit',None,_('_Edit')),

            ('ViewTrash', None, _('Open _Trash'), None, None,
             self.show_deleted_recs),

            ('Preferences', Gtk.STOCK_PREFERENCES, _('_Preferences'),
             None, None, self.show_preferences),
            ('Plugins',None,_('_Plugins'),
             None,_('Manage plugins which add extra functionality to Gourmet.'),
             lambda *args: plugin_gui.show_plugin_chooser()),
            ('Settings',None,_('Setti_ngs')),

            ('HelpMenu',None,_('_Help')),
            ('About',Gtk.STOCK_ABOUT,_('_About'),
             None,None,self.show_about),
            ('Help',Gtk.STOCK_HELP,_('_Help'),
             None,None,self.show_help),
            ])

        self.toolActionGroup = Gtk.ActionGroup(name='ToolActions')
        self.toolActionGroup.add_actions([
            ('Tools',None,_('_Tools')),
            ('Timer',None,_('_Timer'),
             None,_('Show timer'),lambda *args: show_timer()),
            ])

        self.goActionGroup.add_actions([
            ('GoRecipeIndex',None,_('Recipe _Index'),
             None,_('Searchable index of recipes in the database.'),self.present)
            ])

        fix_action_group_importance(self.onSelectedActionGroup)
        self.ui_manager.insert_action_group(self.onSelectedActionGroup, 0)
        fix_action_group_importance(self.mainActionGroup)
        fix_action_group_importance(self.mainActionGroup)
        self.ui_manager.insert_action_group(self.mainActionGroup,0)
        fix_action_group_importance(self.toolActionGroup)
        self.ui_manager.insert_action_group(self.toolActionGroup,0)
        self.add_uimanager_to_manage(-1,self.ui_manager,'RecipeIndexMenuBar')

    # Status bar stuff
    def message (self, msg):
        debug("message (self, msg): %s"%msg,5)
        self.stat.push(self.contid,msg)
        GLib.timeout_add(1500, self.flush_messages)

    def flush_messages (self, ret=False):
        debug("flush_messages (self):",5)
        self.stat.pop(self.contid)
        return ret


    # Basic callbacks
    def new_rec_card (self, *args):
        self.app.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        def show ():
            rc=reccard.RecCard(self)
            self.make_rec_visible(rc.current_rec)
            self.rc[rc.current_rec.id]=rc
            self.app.get_window().set_cursor(None)
            self.update_go_menu()
        GObject.idle_add(show)

    def open_rec_card(self, rec):
        if rec.id in self.rc:
            self.rc[rec.id].show()
        else:
            def show():
                w = reccard.RecCard(self, rec)
                self.rc[rec.id] = w
                self.update_go_menu()
                self.app.get_window().set_cursor(None)
            self.app.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
            GObject.idle_add(show)


    # Extra callbacks for actions on our treeview
    @plugin_loader.pluggable_method
    def get_selected_recs_from_rec_tree (self):
        return RecIndex.get_selected_recs_from_rec_tree(self)

    @plugin_loader.pluggable_method
    def update_recipe (self, recipe):
        return RecIndex.update_recipe(self, recipe)

    @plugin_loader.pluggable_method
    def redo_search (self, *args):
        return RecIndex.redo_search(self, *args)

    def rec_tree_select_rec (self, *args):
        debug("rec_tree_select_rec (self, *args):",5)
        for rec in self.get_selected_recs_from_rec_tree():
            self.open_rec_card(rec)

    def rec_tree_edit_rec (self, *args):
        for rec in self.get_selected_recs_from_rec_tree():
            if rec.id in self.rc:
                self.rc[rec.id].show_edit()
            else:
                def show ():
                    w=reccard.RecCard(self, rec, manual_show=True)
                    self.rc[rec.id]=w
                    self.update_go_menu()
                    w.show_edit()
                    self.app.get_window().set_cursor(None)
                self.app.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
                GObject.idle_add(show)

    # Deletion
    def show_deleted_recs (self, *args):
        if not hasattr(self,'recTrash'):
            self.recTrash = RecTrash(self.rg)
            self.recTrash.show()
        else:
            self.recTrash.show()

    def rec_tree_keypress_cb (self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Delete' or keyname == 'BackSpace':
            self.rec_tree_delete_rec_cb()
            return True

    def rec_tree_delete_rec_cb (self, *args,**kwargs):
        """Make a watch show up (this can be slow
        if lots of recs are selected!"""
        self.rec_tree_delete_recs(
            self.get_selected_recs_from_rec_tree()
            )

    def delete_open_card_carefully (self, rec):
        """Delete any open card windows, confirming if the card is edited.

        We return True if the user cancels deletion.
        """
        if rec.id in self.rc:
            rc = self.rc[rec.id]
            if rc.edited:
                rc.show_edit()
                if not de.getBoolean(
                    label=_('Delete %s?'),
                    sublabel=_('You have unsaved changes to %s. Are you sure you want to delete?'),
                    custom_yes=Gtk.STOCK_DELETE,
                    custom_no=Gtk.STOCK_CANCEL,
                    cancel=False):
                    return True
            rc.hide()
            self.del_rc(rec.id)

    @plugin_loader.pluggable_method
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
        self.setup_delete_messagebox(
            _((f'You just moved {len(recs)} recipe to the trash.\nYou can '
               'recover this recipe or permanently delete it at any time by '
               'clicking Tools->Open Trash.'))
        )
        self.set_reccount()
        if hasattr(self,'recTrash'):
            self.recTrash.update_from_db()
        self.message(_("Deleted") + ' ' + ', '.join((r.title or _('Untitled')) for r in recs))

    def purge_rec_tree (self, recs, paths=None, model=None):
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

            deleterThread = SuspendableDeletions(recs,name='delete_recs')
            deleterThread.connect('done',lambda *args: self.recTrash.update_from_db())
            tm = get_thread_manager()
            tmg = get_thread_manager_gui()
            tm.add_thread(deleterThread)
            tmg.register_thread_with_dialog(_('Delete Recipes'), deleterThread)
            deleterThread.connect('completed', tmg.notification_thread_done,
                    _('Recipes deleted'))
            tmg.show()
        else:
            return True

    def delete_rec (self, rec):
        if rec.id in self.rc:  # Close the related recipe card window
            window = self.rc[rec.id].widget
            self.rc[rec.id].hide()
            window.destroy()
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
                    print('wtf?!?',rec,':',rec.id,' not real?')
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

    def _on_bar_response(self, button, response_id):
        if (response_id == UNDO):
            self.history[-1].inverse()
        elif (response_id == SHOW_TRASH):
            self.show_deleted_recs()
        self.messagebox.hide()

    # Code to show message/undo-button on deletion
    def setup_delete_messagebox (self, msg):
        # Clear existing messages...
        for child in self.messagebox.get_children():
            self.messagebox.remove(child)
        # Add new message
        l = Gtk.Label(label=msg)
        l.set_line_wrap(True)
        l.show()
        infobar = Gtk.InfoBar()
        infobar.set_message_type(Gtk.MessageType.INFO)
        infobar.get_content_area().add(l)
        infobar.add_button(_('See Trash Now'), SHOW_TRASH)
        infobar.add_button(Gtk.STOCK_UNDO, UNDO)
        infobar.add_button(Gtk.STOCK_DISCARD, Gtk.ResponseType.CLOSE)
        infobar.connect('response', self._on_bar_response)
        infobar.show()
        self.messagebox.pack_start(infobar, True, True, 0)
        self.messagebox.show()
    # end deletion

    # end Extra Callbacks for actions on treeview

    # Methods to handle threading
    def pause_cb (self, button, *args):
        if button.get_active():
            debug('Suspending thread from pause_cb',0)
            self.thread.suspend()
            self.stat.push(self.pauseid, self.pause_message)
            self.flusher = GLib.timeout_add(1000,lambda *args: self.flush_messages(True))
        else:
            self.stat.pop(self.pauseid)
            GObject.source_remove(self.flusher)
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
        Gtk.main_quit()


def get_application():
    # TODO: refactor this function away. All its calls can be replaced by:
    return RecGui.instance()

if __name__ == '__main__':
    launch_app()
