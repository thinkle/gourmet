#!/usr/bin/env python

###############################################################################
# IMPORTS
###############################################################################
import gnome
import gtk
import os.path

from gettext import gettext as _
from defaults import lang as defaults

import gourmet
from gdebug import *
from gglobals import *
from gourmet import database, utils
from gourmet.preferences import prefs
from gourmet.ui.dialogs import GladeDialog
from gourmet.ui.ViewList import ViewList

class RecipeGui ():
    """This is the main application."""

    ###########################################################################
    # INITIALIZATION
    ###########################################################################
    
    def __init__ (self):
        gnome.program_init(gourmet.APPNAME, gourmet.VERSION)
        self.db = database.Database(**dbargs)
        self._init_actions()
        self._build_ui()
        self._load_plugins()
        self.ui_manager.ensure_update()
        self.window.present()

    ###########################################################################
    # INITIALIZATION STUFF
    ###########################################################################
    
    def _build_ui (self):
        self.window = gtk.Window()
        self.window.set_title(_('Gourmet Recipe Manager'))
        self.window.set_default_size(750, 600)
        self.window.connect('delete-event', self.quit)
        
        self.vbox = gtk.VBox()

        self.menubar = self.ui_manager.get_widget("/MenuBar")
        self.vbox.pack_start(self.menubar, expand=False)
        self.toolbar = self.ui_manager.get_widget("/ToolBar")
        self.vbox.pack_start(self.toolbar, expand=False)
        
        hpaned = gtk.HPaned()
        
        self.sidepane = gtk.ScrolledWindow()
        self.sidepane.set_shadow_type(gtk.SHADOW_IN)
        self.sidepane.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.viewlist = ViewList()
        self.viewlist.connect('view-changed', self.on_view_changed)
        self.sidepane.add(self.viewlist)
        hpaned.pack1(self.sidepane)
        
        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_show_tabs(False)
        hpaned.pack2(self.notebook)
        
        self.vbox.pack_start(hpaned)
        
        self.statusbar = gtk.Statusbar()
        self.vbox.pack_start(self.statusbar, False)
        
        accelgroup = self.ui_manager.get_accel_group()
        self.window.add_accel_group(accelgroup)
        self.window.add(self.vbox)
        self.window.show_all()
    
    def _init_actions (self):
        self.ui_manager = gtk.UIManager()
        main_actions = [
            ('FileMenu', None, '_File', None, None, None),
            ('EditMenu', None, '_Edit', None, None, None),
            ('ViewMenu', None, '_View', None, None, None),
            ('ToolsMenu', None, '_Tools', None, None, None),
            ('HelpMenu', None, '_Help', None, None, None),
            ('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Close Gourmet', self.quit),
            ('Preferences', gtk.STOCK_PREFERENCES, '_Preferences', None, 'Gourmet''s preferences', self.show_preferences),
            ('About', gtk.STOCK_ABOUT, '_About', None, 'About Gourmet', self.show_about),
            ('Help', gtk.STOCK_HELP, '_Help', None, 'Help', self.show_help)]
        toggle_actions = [
            ('Toolbar', None, '_Toolbar', None, 'Show or hide the toolbar', self.on_toolbar_view, True),
            ('Statusbar', None, '_Statusbar', None, 'Show or hide the statusbar', self.on_statusbar_view, True),
            ('Sidepane', None, 'Side _Pane', None, 'Show or hide the side pane', self.on_sidepane_view, True),
            ('Bottompane', None, '_Bottom Pane', None, 'Show or hide the bottom pane', self.on_bottompane_view, False)]
        ag = gtk.ActionGroup('Actions')
        ag.add_actions(main_actions)
        ag.add_toggle_actions(toggle_actions)
        self.ui_manager.insert_action_group(ag, -1)
        self.ui_manager.add_ui_from_file(os.path.join(uidir, 'ui.xml'))

    def _load_plugins(self):
        self.views = []
        self.plugins = []
        for name in ['recipes', 'categories']:
            plugin = __import__('gourmet.core.%s' % name, globals(), locals(), [name])
            self.plugins.append(plugin)
        for name in ['merge']:
            plugin = __import__('gourmet.plugins.%s' % name, globals(), locals(), [name])
            self.plugins.append(plugin)
        for plugin in self.plugins:
            plugin.attach_window(self)
        if len(self.views) > 0:
            self.current = self.views[0]

    ###########################################################################
    # HOOKS
    ###########################################################################
   
    def append_view (self, view):
        self.viewlist.append(view)
        page = self.notebook.append_page(view)
        view.attach_window(self)
        view.show()
        self.views.append(view)

    ###########################################################################
    # CALLBACKS
    ###########################################################################
    
    def on_toolbar_view(self, item):
        self.toolbar.props.visible = item.get_active()

    def on_statusbar_view(self, item):
        self.statusbar.props.visible = item.get_active()
        
    def on_sidepane_view(self, item):
        self.sidepane.props.visible = item.get_active()
        
    def on_bottompane_view(self, item):
        self.previewpane.props.visible = item.get_active()

    def on_view_changed(self, list, view):
        page = self.views.index(view)
        self.notebook.set_current_page(page)
        if self.current:
            #self.ui_manager.remove_ui(self.view_merge_id)
            self.ui_manager.remove_action_group(self.current.action_group)
        self.ui_manager.insert_action_group(view.action_group, -1)
        #self.view_merge_id = self.ui_manager.add_ui_from_string(view.ui)
        self.ui_manager.ensure_update()
        self.current = view
        
    ###########################################################################
    # CALLBACKS
    ###########################################################################
            
    def show_about(self, *args):
        """Show information about ourselves."""
        about = _AboutDialog()        

    def show_help(self, *args):
        print 'HELP' #FIXME

    def show_preferences(self, *args):
        if not hasattr(self, 'prefsGui'):
            self.prefsGui = PreferencesDialog()
        self.prefsGui.show()

    def show_converter(self, *args):
        if not hasattr(self, 'cg'):
            self.cg = ConvertDialog(unitModel=self.umodel)
        self.cg.show()

    def show_key_editor(self, *args):
        ke = KeyEditor(rd=self.db, rg=self)
        ke.show()

    def show_value_editor(self, *args):
        if not hasattr(self,'ve'):
            self.ve = ValueEditor(self.db)
        self.ve.show()

    def quit(self, *args):
        prefs.save()
        self.window.destroy()
        gtk.main_quit()

###############################################################################
# MAIN FUNCTION
###############################################################################
#FIXME Function name
def startGUI ():
    debug("startGUI ():",4)
    gt.gtk_threads_init()
    gt.gtk_enter()
    while gtk.events_pending():
        gtk.main_iteration()
    try:
        r = RecipeGui()
        debug("startGUI end", 4)
    except:
        while gtk.events_pending():
            gtk.main_iteration()
        raise
    gtk.main()
    gt.gtk_leave()


###############################################################################
# PREFERENCES DIALOG
###############################################################################
class PreferencesDialog (GladeDialog):
    """
    The preferences dialog
    """
    glade_file = 'preferenceDialog.glade'

    def __init__ (self):
        GladeDialog.__init__(self)
        #prefs.connect('changed', self.update_pref)

###############################################################################
# ABOUT DIALOG
###############################################################################
class _AboutDialog(gtk.AboutDialog):
    """ About dialog """
    def __init__(self):
        gtk.AboutDialog.__init__(self)
        translator=_("translator-credits")
        if hasattr(defaults, 'CREDITS') and defaults.CREDITS:
            if translator and translator.find(defaults.CREDITS) > -1:
                translator += "\n%s"%defaults.CREDITS
            else:
                translator = defaults.CREDITS
        logo = gtk.gdk.pixbuf_new_from_file(os.path.join(imagedir,"gourmet_logo.png"))
        self.set_logo(logo)
        self.set_name(gourmet.APPNAME)
        self.set_version(gourmet.VERSION)
        self.set_copyright(copyright)
        self.set_comments(description)
        self.set_website("http://grecipe-manager.viewforge.net")
        self.set_website_label(_("Gourmet Web Site"))
        self.set_authors(authors)
        if translator != "translator-credits":
            self.set_translator_credits(translator)
        self.connect('response', self.about_hide)
        self.show()
        
    def about_hide(self, *args):
        self.destroy()
