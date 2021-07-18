# This module provides base classes for all of our plugins. Plugin
# writers will subclass these plugins in their own modules. Thus, each
# plugin module should start with
#
# from gourmet.plugin import ...
#
# The plugins should then sub-class the relevant class.
#
# Importer and Exporter plugins are somewhat special -- they merely
# provide information about what they can import or export and then
# provide a do_import or do_export method to do the importing and
# exporting.
#
# StandardPlugins are given an instance of a pluggable class and are
# then imported and exported accordingly.
#
# UIPlugin - this is a useful sub-class that makes it trivial to use
# UIManager to add new actions to windows.
#
# ToolPlugin - will be plugged into all windows that have tool
# menus. Which menu bars we add ourselves to is controlled with the
# menu_bars parameter.
#
# MainPlugin - this is given an instance of the main Gourmet
# Application to muck about with.
#
# RecDisplayPlugin - given an instance of the recipe display card.
# RecEditorPlugin - given an instance of the recipe editor.
# DatabasePlugin - given an instance of the base database class.

import sqlalchemy
from gi.repository import GObject, Gtk

from gourmet import Undo

from . import plugin_loader
from .gtk_extras import fix_action_group_importance


class Plugin:
    pass

class StandardPlugin (Plugin):

    def activate (self, pluggable):
        """Called when plugin is activated. Once each time the
        pluggable instance is instantiated.
        """
        pass

    def deactivate (self, pluggable):
        """Called when plugin is deactivated.

        Once each time the pluggable instance is destroyed.
        """
        pass

    def remove (self):
        """Remove the plugin from the UI (the user has turned it off).
        """
        pass

class ImportManagerPlugin (StandardPlugin):
    '''A class for extending the methods of the ImportManager itself.

    In order to add importers, subclass ImporterPlugin, not this class.
    '''

    url_needs_login_patterns = {
        # Glob patterns for URLs w/ method that will do log in for us...
        # i.e.
        # '.*nytimes.com.*' : read_nytimes_url
        # where do_nytimes_login is a function that takes the URL
        # and does the login necessarily to grab it...
    }


    pass

class ImporterPlugin (StandardPlugin):

    # Do we let users type in a source to associate with these
    # recipes.
    ask_user_for_source = False

    name = None # The name of our importer
    patterns = [] # Glob patterns to match this filetype
    mimetypes = [] # mimetypes associated with this filetype

    def activate (self, pluggable):
        pluggable.register_plugin(self)
        self.importManager = pluggable

    def deactivate (self, pluggable):
        pluggable.unregister_plugin(self)

    def test_file (self,filename):
        '''Test whether file filename is importable by this plugin.'''
        return True

    def get_importer (self, filename):
        """Return an importer class for filename.

        rd is our recipe database object.
        """
        raise NotImplementedError

    def test_url (self, url, data, content_type):
        '''Test whether data retrieved from url is importable by this plugin.
        '''
        tempfilename = self.importManager.get_tempfilename(url,data,content_type)
        return self.test_file(tempfilename)

    def get_web_importer (self, url, data, content_type):
        '''Get an importer for data data retrieved from url'''
        tempfilename = self.importManager.get_tempfilename(url,data,content_type)
        return self.get_importer(tempfilename)




class ExporterPlugin (StandardPlugin):

    label = ''
    sublabel = ''
    single_completed_string = ''
    filetype_desc = ''
    saveas_filters = []
    saveas_single_filters = []

    def activate (self, pluggable):
        pluggable.register_plugin(self)

    def deactivate (self, pluggable):
        pluggable.unregister_plugin(self)

    def get_multiple_exporter (self, args):
        pass

    def do_single_export (self, args):
        pass

    def run_extra_prefs_dialog (self):
        pass

    def get_default_prefs (self):
        return {}

class BaseExporterPlugin (Plugin):
    '''This is designed to change the behavior of other exporters.

    For example, a plugin that created a new attribute or text field
    could add it to the export by creating a ChangeExporterPlugin that
    plugs into the write_attr or write_text methods.
    '''
    TEXT = 0
    ATTR = 1

    def __init__ (self):
        self.hooks_to_add = []

    def activate (self, pluggable):
        self.pluggable = pluggable
        for hook in self.hooks_to_add:
            pluggable.add_hook(*hook)

    def remove (self):
        for hook in self.hooks_to_add:
            self.pluggable.remove_hook(*hook)
        self.pluggable.plugins.remove(self)

    def add_field (self, field_name, field_fetcher,
                   type,
                   position=plugin_loader.POST,
                   write_empty_field=False):
        '''Add a text field to our export.

        field_name is the name of the field.

        field_fetcher is a function that is given the recipe object as
        its only argument and should return the text blurb.

        type is what kind of field we\'re adding to the export
        (self.TEXT, self.ATTR, self.ING, self.IMG)

        position is either PRE or POST -- whether we come before or
        after other text fields.

        if write_empty_field is True, we will write the field
        regardless of the value. Otherwise, non-True (i.e. blank)
        values will not print.
        '''
        if type==self.TEXT:
            def do_write (*args):
                #print 'do_write received arguments',args
                if position==plugin_loader.POST:
                    klass = args[1]
                else:
                    klass = args[0]
                val = field_fetcher(klass.r)
                if klass.do_markup:
                    val = klass.handle_markup(val)
                if not val: val = ''
                if klass.ALLOW_PLUGINS_TO_WRITE_NEW_FIELDS and (val or write_empty_field):
                    klass.write_text(field_name,val)
            self.hooks_to_add.append((position,'_write_text_',do_write))
        else:
            def do_write (*args):
                #print 'do_write received arguments',args
                if position==plugin_loader.POST:
                    klass = args[1]
                else:
                    klass = args[0]
                val = field_fetcher(klass.r)
                if klass.do_markup:
                    val = klass.handle_markup(val)
                if klass.ALLOW_PLUGINS_TO_WRITE_NEW_FIELDS and (val or write_empty_field):
                    klass.write_attr(field_name,val)
            self.hooks_to_add.append((position,'_write_attrs_',do_write))

class BaseExporterMultiRecPlugin (Plugin):
    '''This is designed to change the behavior of other exporters.

    This plugs in at the level of the MultiRecPlugin, used for
    exporting recipe collections.
    '''
    pass


class DatabasePlugin (StandardPlugin):

    name = '' # The name of our database -- subclasses should provide
              # this -- it will allow Gourmet to store version
              # information for database updates

    version = 1 # Version information -- this will allow Gourmet to
                # store information on the plugin version for future
                # updates.

    active = False

    def activate (self, db):
        if self.active:
            print('Strange -- activate called twice')
            print('Activate plugin',self,db,'from:')
            import traceback; traceback.print_stack()
            print('ignoring')
            return
        self.db = db
        if db._created:
            # For creation after DB is initialized...
            try:
                self.create_tables()
            except sqlalchemy.exc.InvalidRequestError as error:
                print(("An InvalidRequestError was caught: {0}".format(error.args, error.message)))
            self.db.metadata.create_all()
            db.update_plugin_version(self)
        else:
            db.add_hook(plugin_loader.POST,'setup_tables',self.create_tables)
        self.active = True

    def remove (self):
        self.db.remove_hook(plugin_loader.POST,'setup_tables',self.create_tables)
        self.active = False

    def create_tables (self):
        """Handed the database, create table definitions as necessary.

        This will happen at program initiation.
        """
        pass

    def update_version (self, gourmet_stored, plugin_stored,
                        gourmet_current, plugin_current):
        """Given the old version number, perform any updates to the
        database as necessary.

        The Gourmet version #s are tuples with version_super, version_major
        and version_minor.

        The plugin version numbers are single numbers corresponding to
        the version attribute of your your plugin class.
        """
        pass

class UIModule:
    ui_string = '' # an XML UI description for merging with the target UIManager
    name = '' # the name of this module (not i18n'd)
    label = '' # The label of the tab where this interface goes. (should be i18n'd)

    def __init__ (self):
        self.action_groups = []
        self.added = []
        self.setup_action_groups()
        self.setup_main_interface()

    def setup_action_groups (self):
        pass

    def setup_main_interface (self):
        pass

    def enter_page (self):
        pass

    def leave_page (self):
        pass

class UIPlugin (StandardPlugin, UIModule):

    """A plugin that works through UIManager.
    """

    def __init__ (self):
        self.merged = {}
        UIModule.__init__(self)

    def activate (self, pluggable):
        self.pluggable = pluggable
        self.add_to_uimanager(pluggable.ui_manager)

    def remove (self):
        for uimanager in self.merged:
            merge_id,action_ids = self.merged[uimanager]
            for ag in action_ids: uimanager.remove_action_group(ag)
            uimanager.remove_ui(merge_id)

    def add_to_uimanager (self, uimanager):
        merge_id = uimanager.add_ui_from_string(self.ui_string)
        action_ids = []
        for ag in self.action_groups:
            fix_action_group_importance(ag)
            uimanager.insert_action_group(ag,0)
            action_ids.append(ag)
        self.merged[uimanager] = merge_id,action_ids

class ToolPlugin (UIPlugin):

    """A plugin that plugs an action into the tool menu.
    """

    menu_items = '<menuitem action=""/>'
    menu_bars = ['RecipeDisplayMenuBar','RecipeEditorMenuBar','RecipeIndexMenuBar']

    def __init__ (self):
        self.ui_string = '\n'.join('''<menubar name="%(mb)s">
        <menu name="Tools" action="Tools">
        %(menu_items)s
        </menu>
        </menubar>'''%{'menu_items':self.menu_items,
                       'mb':mb} for mb in self.menu_bars)
        UIPlugin.__init__(self)

class RecDisplayPlugin (StandardPlugin):

    moduleKlass = None

    def activate (self, pluggable):
        if not hasattr(self,'pluggables'): self.pluggables = []
        pluggable.add_plugin_to_left_notebook(self.moduleKlass)
        self.pluggables.append(pluggable)

    def remove (self):
        for pluggable in self.pluggables:
            pluggable.remove_plugin_from_left_notebook(self.moduleKlass)

class RecEditorPlugin (StandardPlugin):

    '''A plugin for our recipe editor.

    moduleKlass is a module to add (provides a new tabby interface on
    the recEditor) and position is the position of that new module.

    '''

    moduleKlass = None
    position = None

    def activate (self, pluggable):
        if not hasattr(self,'pluggables'): self.pluggables = []
        pluggable.add_plugin(self.moduleKlass,self.position)
        self.pluggables.append(pluggable)

class MainPlugin (StandardPlugin):

    added_tabs = []

    def activate (self, pluggable):
        self.main = pluggable

    def deactivate (self, pluggable):
        for t in self.added_tabs:
            pluggable.main_notebook.remove_page(t)
        if pluggable.main_notebook.get_n_pages() <= 1:
            pluggable.main_notebook.set_show_tabs(False)

    def add_tab (self, widget, label):
        self.added_tabs.append(self.main.main_notebook.append_page(widget,
                                                              Gtk.Label(label=label))
                          )
        widget.show()
        self.main.main_notebook.set_show_tabs(True)


class PluginPlugin (StandardPlugin):
    """This class is used for plugins that plugin to other plugins.
    """

    target_pluggable = None

    def activate (self, pluggable):
        # Check whether we are actually intended for this pluggable,
        # then call do_activate, or remove ourselves from the plugins
        # list accordingly.
        if self.target_pluggable in pluggable.targets:
            # do_activate is where we do our real activation
            self.do_activate(pluggable)
        else:
            # nevermind... we're not for this pluggable
            pluggable.plugins.remove(self)

    def do_activate (self, pluggable):
        pass

class RecDisplayModule (UIModule):

    def __init__ (self, recDisplay):
        self.rd = recDisplay; self.rg = self.rd.rg
        UIModule.__init__(self)

class RecEditorModule (UIModule, GObject.GObject, object):

    __gsignals__ = {
        'saved':(GObject.SignalFlags.RUN_LAST, None,[]),
        'toggle-edited':(GObject.SignalFlags.RUN_LAST, None,[GObject.TYPE_BOOLEAN]),
        }

    def __init__ (self, recEditor):
        GObject.GObject.__init__(self)
        self.action_groups = [] # a list of ActionGroups to be inserted into the uimanager.
        self.re = recEditor
        self.rg = self.re.rg
        self.current_rec = self.re.current_rec
        self.setup()
        self.setup_undo()
        self.setup_main_interface()

    __edited = False

    @property
    def edited(self):
        return self.__edited

    @edited.setter
    def edited(self, val):
        self.__edited = val
        self.emit('toggle-edited', val)

    def setup_undo (self):
        self.undoActionGroup = Gtk.ActionGroup(name=f'{self.name}UndoActions')
        self.undoActionGroup.add_actions([
            ('Undo',Gtk.STOCK_UNDO,None,'<Control>Z'),
            ('Redo',Gtk.STOCK_REDO,None,'<Control><Shift>Z'),
            ('Reapply',None,'Reapply','<Control>Y'),
            ])
        self.action_groups.append(self.undoActionGroup)
        self.history = Undo.UndoHistoryList(
            self.undoActionGroup.get_action('Undo'),
            self.undoActionGroup.get_action('Redo'),
            self.undoActionGroup.get_action('Reapply')
            )
        self.history.add_action_hook(self.undo_action_callback)

    def setup (self):
        pass

    def setup_main_interface (self):
        self.main = Gtk.Label(label='%s Interface not yet implemented'%self.label)

    def save (self, recdict):
        """Modify recipe dictionary with properties to be saved.
        Do any modifications to other tables.
        Return possibly modified recipe dictionary
        """
        self.emit('saved')
        return recdict

    def undo_action_callback (self, undo_history, action, typ):
        # For all actions that go into the undo system, not just UNDO
        widget = action.widget
        #prop = self.get_prop_for_widget(widget)
        prop = (hasattr(widget,'db_prop') and getattr(widget,'db_prop')) or None
        if prop:
            # For all changes to simple recipe attributes (Title,
            # Cuisine, etc.), we look at every change and compare with
            # the original value. If it has, we delete the change from
            # our dictionary of changes. If all changes have been set
            # back to original value, we are no longer "Edited"
            if hasattr(widget,'get_value'): val = widget.get_value()
            elif hasattr(widget,'get_text'): val = widget.get_text()
            elif hasattr(widget,'entry'): val = widget.entry.get_text()
            elif hasattr(widget,'get_buffer'): val = widget.get_buffer().get_text()
            elif isinstance(widget, Gtk.ComboBoxText):
                val = widget.get_active_text()
            else: raise TypeError("I don't know how to get the value from action %s widget %s"%(action,widget))
            # HAVE TO HANDLE CATEGORIES
            if prop=='category':
                orig_value = ', '.join(self.rg.rd.get_cats(self.current_rec))
            else:
                orig_value = getattr(self.current_rec,prop)
            if isinstance(orig_value, str):
                val = val.strip(); orig_value=orig_value.strip()
            else:
                if not val: val = 0
                if not orig_value: orig_value = 0
            if orig_value==val:
                if prop in self.re.widgets_changed_since_save:
                    del self.re.widgets_changed_since_save[prop]
            else:
                self.re.widgets_changed_since_save[prop]=val
        else:
            # If we can't compare with original values, we keep a
            # dictionary of all changes made on a per-widget basis.
            if not widget:
                self.re.widgets_changed_since_save['UntrackableChange']=True
            else:
                # We store each change in our dictionary... if the
                # change has disappeared from the history list, then
                # we can surmise it has been "undone"
                if widget in self.re.widgets_changed_since_save:
                    old_change = self.re.widgets_changed_since_save[widget][-1]
                    if (old_change.is_undo != action.is_undo
                        and
                        old_change not in undo_history):
                        # If we are the inverse of the old action and
                        # the old action is no longer in history, then
                        # we can assume (safely?) that we have undone
                        # the old action
                        del self.re.widgets_changed_since_save[widget][-1]
                        if not self.re.widgets_changed_since_save[widget]:
                            del self.re.widgets_changed_since_save[widget]
                    else:
                        self.re.widgets_changed_since_save[widget].append(action)
                else:
                    self.re.widgets_changed_since_save[widget]=[action]
        if self.re.widgets_changed_since_save:
            self.edited = True
        else:
            self.edited = False

    def grab_focus (self):
        """Put focus on appropriate widget for editing."""
        pass

class IngredientControllerPlugin (StandardPlugin):
    '''Plugins for mucking about with how ingredient information is
    edited and stored.
    '''
    pass

class ShoppingListPlugin (UIPlugin):

    ui_string = ''

    def __init__ (self):
        UIPlugin.__init__(self)


class PrinterPlugin (StandardPlugin):

    # SimpleWriter class
    SimpleWriter = None
    # how good this printer is (0 = use it if nothing else is there,
    # and up from there)
    simpleWriterPriority = -2
    RecWriter = None # RecWriter class
    recWriterPriority = -2
    pass

    def activate (self, pluggable):
        pluggable.register_plugin(self)

    def deactivate (self, pluggable):
        pluggable.unregister_plugin(self)

class PrefsPlugin (StandardPlugin):

    '''Add a tab to the preferences notebook.

    Pretty much all of the handling is offloaded to the widget you add.

    If you want to handle applying using the prefsGui system, you can do it with...

    self.prefsGui.apply_prefs_dic['prefname']=function

    where function takes then name and value of the preference as its arguments.
    '''

    label = None
    widget = None

    def activate (self, pluggable):
        self.prefsGui = pluggable
        self.notebook = pluggable.notebook
        if self.label and self.widget:
            self.page_no = self.notebook.append_page(self.widget,tab_label=Gtk.Label(label=self.label))
            self.widget.show()

    def deactivate (self, pluggable):
        self.notebook = None
        self.prefsGui = None

    def remove (self):
        if self.notebook:
            self.notebook.remove_page(self.page_no)

    def set_pref (self, name, value):
        self.prefsGui.set_pref(name,value)
