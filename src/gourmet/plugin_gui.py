from gettext import gettext as _
from typing import Any, List, Tuple, Union
from xml.sax.saxutils import escape

from gi.repository import GObject, Gtk

from .gtk_extras import dialog_extras as de
from .plugin_loader import DependencyError, MasterLoader


class PluginChooser:

    def __init__ (self):
        self.loader = MasterLoader.instance()
        self.window = Gtk.Dialog()
        self.notebook = Gtk.Notebook()
        for cat,plugins in list(self.categorize_plugins().items()):
            plugin_view = self.make_treeview(plugins)
            lab = Gtk.Label(label=cat); lab.show()
            self.notebook.append_page(plugin_view,lab)
            plugin_view.show_all()
        self.add_labels()
        self.window.vbox.add(self.notebook); self.notebook.show()
        self.window.add_buttons(
            #Gtk.STOCK_ABOUT,1, # TODO: find the description of plugins
            Gtk.STOCK_CLOSE,Gtk.ResponseType.CLOSE
            )
        self.window.set_default_size(375,400)
        self.window.connect('response',self.response_cb)

    def add_labels (self):
        head = Gtk.Label()
        head.set_markup(
            '<b><span size="large">'+_('Plugins')+'</span></b>'
            )
        desc = Gtk.Label()
        desc.set_markup('<i>'+_('Plugins add extra functionality to Gourmet.')+'</i>')
        head.set_alignment(0.0,0.0); desc.set_alignment(0.0,0.0)
        self.window.vbox.pack_start(head, expand=False, fill=False, padding=0)
        self.window.vbox.pack_start(desc, expand=False, fill=False, padding=0)
        self.window.vbox.set_border_width(12)
        head.show(); desc.show()

    def categorize_plugins (self):
        categorized = {}
        for module_name,plugin_set in list(self.loader.available_plugin_sets.items()):
            try:
                cat = plugin_set.category
            except AttributeError:
                cat = 'Main'
            if cat not in categorized: categorized[cat]=[]
            categorized[cat].append((module_name,plugin_set))
        return categorized

    def make_list_store(self, plugin_list: List[Tuple[str, Union['LegacyPlugin', 'Plugin']]]) -> Gtk.ListStore:
        ls = Gtk.ListStore(bool,  # plugin activated
                           GObject.TYPE_PYOBJECT)  # plugin and its info
        for module_name, plugin_set in plugin_list:
            ls.append((module_name in self.loader.active_plugin_sets, plugin_set))
        return ls

    @staticmethod
    def plugin_description_formatter(col: Gtk.TreeViewColumn,
                                     renderer: Gtk.CellRendererText,
                                     mod: Gtk.ListStore,
                                     itr: Gtk.TreeIter,
                                     data: Any):
        """ Format plugin name and description in the plugin window
        """
        plugin_set = mod[itr][1]
        renderer.set_property('markup',
                              ('<b>' + escape(plugin_set.name) + '</b>' +
                               '\n<span size="smaller">' + escape(plugin_set.comment) + '</span>')
                              )

    def make_treeview (self, plugin_list):
        tv = Gtk.TreeView()
        toggle_renderer = Gtk.CellRendererToggle()
        toggle_renderer.set_property('activatable',True)
        toggle_renderer.set_property('sensitive',True)
        toggle_renderer.connect('toggled',self.toggled_cb,tv)
        active_col = Gtk.TreeViewColumn('Active',toggle_renderer,active=0)
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_property('wrap-width',350)
        plugin_col = Gtk.TreeViewColumn('Plugin',text_renderer)
        plugin_col.set_cell_data_func(text_renderer, self.plugin_description_formatter)
        plugin_col.set_property('expand',True)
        plugin_col.set_property('min-width',250)
        tv.append_column(plugin_col)
        tv.append_column(active_col)
        ls = self.make_list_store(plugin_list)
        tv.set_model(ls)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        sw.add(tv)
        return sw

    def toggled_cb (self, renderer, path, tv):
        ls = tv.get_model()
        plugin_set = ls[path][1]
        prev_state = ls[path][0]
        state = not prev_state
        self.do_change_plugin(plugin_set, state, ls)
        ls[path][0] = state

    def do_change_plugin (self, plugin_set, state, ls):
        try:
            if state:
                try:
                    self.loader.check_dependencies(plugin_set)
                except DependencyError as dep_error:
                    print('Missing dependencies:',dep_error.dependencies)
                    for row in ls:
                        ps = row[1]
                        if ps.module in dep_error.dependencies and not row[0]:
                            print('Activate dependency ',ps.module)
                            self.do_change_plugin(ps,True, ls)
                            row[0] = True
                self.loader.activate_plugin_set(plugin_set)
            else:
                dependers = self.loader.check_if_depended_upon(plugin_set)
                if dependers:
                    if de.getBoolean(
                        label=_("Plugin is needed for other plugins. Deactivate plugin anyway?"),
                        sublabel=(_('The following plugins require %s:'%plugin_set.name) + '\n' +
                                  '\n'.join(plugin_set.name for plugin_set in dependers)
                                  ),
                        custom_yes=_('Deactivate anyway'),
                        custom_no=_('Keep plugin active')
                        ):
                        self.loader.deactivate_plugin_set(plugin_set)
                        for row in ls:
                            if row[1] in dependers:
                                row[0] = False
                    else:
                        raise Exception("Cancelled")
                else:
                    self.loader.deactivate_plugin_set(plugin_set)
        except:
            details = self.loader.errors.get(plugin_set,'')
            if 'ImportError' in details:
                modname = details.split()[-1]; n = modname.lower()
                modpossibilities = '"python-%s" '%n+_('or')+' "%s"'%n
                details += '\n\nYou may need to install additional python packages for this module to work properly. If you have a package management system on your computer, use it to search for a package containing "%s", such as %s'%(modname,modpossibilities)
            if state:
                de.show_message(message_type=Gtk.MessageType.ERROR,
                                label=_('An error occurred activating plugin.'),
                                sublabel=details)
            else:
                de.show_message(message_type=Gtk.MessageType.ERROR,
                                label=_('An error occurred deactivating plugin.'),
                                sublabel=details
                                )

            raise

    def response_cb (self, window, response):
        if response==Gtk.ResponseType.CLOSE: self.window.hide()

def show_plugin_chooser ():
    pc = PluginChooser()
    pc.window.show()
    return pc

if __name__ == '__main__':
    pc = show_plugin_chooser()
    pc.window.connect('delete-event',Gtk.main_quit)
    Gtk.main()
