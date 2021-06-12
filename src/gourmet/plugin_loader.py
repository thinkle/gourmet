import glob
import logging
import os.path
import pkg_resources
import sys
import traceback
from typing import Dict, List

from gourmet import gglobals
from gourmet.prefs import Prefs

from .defaults.defaults import loc
from .gdebug import debug

PRE = 0
POST = 1

try:
    current_path = os.path.split(os.path.join(os.getcwd(), __file__))[0]
except IndexError:
    current_path = ''


class MasterLoader:
    """This module provides a base class for loading plugins. Everything
    that is plug-in-able in Gourmet should subclass the plugin loader.

    Everything that is a plugin needs to provide a python module with a plugins
    attribute containing the plugin classes that make up the plugin.
    In addition, we need a .gourmet-plugin configuration file pointing to the
    module (with the module parameter) and giving the name and comment for the
    plugin.
    """
    __single = None
    default_active_plugin_sets = [
        # tools
        'unit_converter',
        'duplicate_finder',
        'spellcheck',
        # import/export
        'gxml_plugin',
        'html_plugin',
        'mastercook_import_plugin',
        'mealmaster_plugin',
        'archive_plugin',
        'pdf_plugin',
        'plaintext_plugin',
        'web_import_plugin',
        'website_import_plugins',
        'krecipe_plugin',
        'mycookbook_plugin',
        'epub_plugin',
        'copy_paste_plugin'
        ]

    @classmethod
    def instance(cls):
        if MasterLoader.__single is None:
            MasterLoader.__single = MasterLoader()

        return MasterLoader.__single

    def __init__(self):
        # TODO!!! Discover plugins using namespace packages(?)
        # If gourmet is running as a built (i.e., non-source) distribution,
        # this is probably not going to work with bundled plugins.
        self.plugin_directories = [
            # user plug-ins
            os.path.join(gglobals.gourmetdir, 'plugins'),
            # bundled plugins
            os.path.join(current_path, 'plugins'),
            os.path.join(current_path, 'plugins', 'import_export'),
        ]
        self.errors = set()
        self.pluggables_by_class: Dict = dict()
        self.active_plugin_sets: List[str] = []
        self.available_plugin_sets: Dict[str, LegacyPlugin] = self.load_legacy_plugins(self.plugin_directories)
        self.available_plugin_sets.update(self.load_plugins_from_namespace())
        self.load_active_plugins()

    @staticmethod
    def load_legacy_plugins(directories: List[str]) -> Dict[str, object]:
        """Look through plugin directories for legacy gourmet-plugins."""
        ret: Dict[str, object] = {}
        for d in directories:
            debug('Loading plugins from %s'%os.path.realpath(d),1)
            plugins = glob.glob(os.path.join(d, '*.gourmet-plugin'))
            for ppath in plugins:
                debug('Found %s'%ppath,1)
                plugin_set = LegacyPlugin(ppath)
                if plugin_set.module in ret.keys():
                    print('Ignoring duplicate plugin ',plugin_set.module,'found in ',ppath)
                else:
                    ret[plugin_set.module] = plugin_set
        return ret

    @staticmethod
    def load_plugins_from_namespace() -> Dict[str, object]:
        """Look for plugins in the gourmet.plugins namespace."""
        debug('Loading plugins from namespace', 1)
        exporters = list(pkg_resources.iter_entry_points('gourmet.plugins.exporters'))
        file_importers = list(pkg_resources.iter_entry_points('gourmet.plugins.fileimporters'))
        web_importers = list(pkg_resources.iter_entry_points('gourmet.plugins.webimporters'))

        ret: Dict[str, object] = {}
        for entrypoint in exporters:
            try:
                plugin = entrypoint.load()
            except BaseException as e:  # ModuleNotFoundError, ImportError, etc.
                print(f'Could not load plugin {entrypoint}: {e}')
            else:
                ret[entrypoint.name] = Plugin(plugin)

        return ret

    def load_active_plugins(self):
        """Enable plugins that were previously saved to the preferences"""
        prefs = Prefs.instance()
        self.active_plugin_sets = prefs.get(
            'plugins',
            list(self.default_active_plugin_sets))
        self.active_plugins = []
        self.instantiated_plugins = {}

        for p in self.active_plugin_sets:
            if p in self.available_plugin_sets:
                try:
                    self.active_plugins.extend(self.available_plugin_sets[p].plugins)
                except:
                    print('WARNING: Failed to load plugin %s'%p)
                    self.errors[p] = traceback.format_exc()
                    logging.exception('')
            else:
                print('Plugin ',p,'not found')

    def save_active_plugins(self):
        prefs = Prefs.instance()
        prefs['plugins'] = self.active_plugin_sets
        prefs.save()

    def check_dependencies(self, plugin_set):
        if plugin_set.dependencies:
            missing = []
            depends = plugin_set.dependencies or []
            for dep in depends:
                if not dep in self.active_plugin_sets:
                    missing.append(dep)
            if missing:
                raise DependencyError(plugin_set,missing)

    def check_if_depended_upon (self, plugin_set):
        """Return a list of active plugin set objects that depend on
        plugin_set.
        """
        depending_on_me = []
        for module in self.active_plugin_sets:
            if module in self.available_plugin_sets:
                ps = self.available_plugin_sets[module]
                if ps.dependencies:
                    try:
                        if plugin_set.module in ps.dependencies:
                            depending_on_me.append(ps)
                    except:
                        print('Problem checking dependencies of ',ps,ps.Dependencies)
                        raise
        return depending_on_me

    def activate_plugin_set(self, plugin_set: 'LegacyPlugin'):
        """Activate a set of plugins.
        """
        if plugin_set in self.active_plugin_sets:
            return
        self.check_dependencies(plugin_set)
        # plugin_set.get_module() returns None if there's been a
        # problem -- we want to raise that problem now.
        if plugin_set.get_module() is None:
            e = plugin_set.error
            self.errors[plugin_set] = f"{type(e).__name__}: {e}"
            raise e
        self.active_plugin_sets.append(plugin_set.module)
        self.active_plugins.extend(plugin_set.plugins)
        for plugin in plugin_set.plugins:
            for klass in list(self.pluggables_by_class.keys()):
                if issubclass(plugin,klass):
                    for pluggable in self.pluggables_by_class[klass]:
                        pluggable.plugin_plugin(self.get_instantiated_plugin(plugin))

    def deactivate_plugin_set (self, plugin_set: 'LegacyPlugin'):
        # Deactivate any plugin sets that depend upon us...
        for ps in self.check_if_depended_upon(plugin_set):
            self.deactivate_plugin_set(ps)
        if plugin_set.module in self.active_plugin_sets:
            self.active_plugin_sets.remove(plugin_set.module)
        else:
            print('Odd',plugin_set.module,'is not listed as active.')
        if plugin_set.get_module():
            for plugin in plugin_set.plugins:
                for klass in list(self.pluggables_by_class.keys()):
                    if issubclass(plugin,klass):
                        for pluggable in self.pluggables_by_class[klass]:
                            plugin().deactivate(pluggable)

                if plugin in self.instantiated_plugins:
                    self.instantiated_plugins[plugin].remove()
                self.active_plugins.remove(plugin)

    def get_instantiated_plugin (self, plugin):
        if plugin in self.instantiated_plugins:
            return self.instantiated_plugins[plugin]
        else:
            debug('Instantiate %s from %s'%(plugin,
                                            plugin.__module__),
                  1)
            self.instantiated_plugins[plugin] = plugin()
            return self.instantiated_plugins[plugin]

    def register_pluggable (self, pluggable, klass):
        if klass not in self.pluggables_by_class:
            self.pluggables_by_class[klass] = []
        self.pluggables_by_class[klass].append(pluggable)
        for p in self.active_plugins:
            if issubclass(p,klass):
                try:
                    plugin_instance = self.get_instantiated_plugin(p)
                except:
                    print('WARNING: Failed to instantiate plugin %s of type %s'%(p,klass))
                    self.errors[p] = traceback.format_exc()
                    traceback.print_exc()
                else:
                    pluggable.plugin_plugin(plugin_instance)

    def unregister_pluggable (self, pluggable, klass):
        self.pluggables_by_class[klass].remove(pluggable)


class Plugin:
    """Load a plugin from the gourmet-plugins namespace."""

    def __init__(self, plugin_class: type):
        self.props = dict.fromkeys(
            ['Name', 'Comment', 'Authors', 'Version', 'API_Version', 'Website',
             'Copyright','Dependencies'])
        self._loaded = plugin_class
        self.name = plugin_class.__name__
        self.comment = self._loaded.__doc__.split('\n')[0]
        self.authors = plugin_class.AUTHOR
        self.api_version = 2.0
        self.copyright = plugin_class.COPYRIGHT
        self.website = plugin_class.WEBSITE
        attrs = pkg_resources.require(self.name)[0]
        self.version = attrs.version

        # The following is a backward compatibility hack: pip took care to
        # install the plugin and its dependencies.
        # Moreover, Gtk bindings are packaged as pygobject but installed as gi.
        # We have it anyway.
        self.dependencies = [r.name for r in attrs.requires()]
        self.dependencies.remove('pygobject')

        self.module = plugin_class.__module__
        self.plugins = [plugin_class]

    def get_module(self):
        return self._loaded


class LegacyPlugin:
    """A lazy-loading set of plugins.

    This class encapsulates what to the end-user is a plugin.

    From our perspective, plugins can really be a bundle of plugins --
    for example, your plugin might require a DatabasePlugin, a
    RecCardDisplayPlugin and a MainPlugin to function.
    """
    _loaded = None

    def __init__(self, plugin_info_path: str):
        with open(plugin_info_path, 'r') as fin:
            self.load_plugin_file_data(fin)
        self.curdir, plugin_info_file = os.path.split(plugin_info_path)
        self.plugin_modules_dir = os.path.join(os.path.dirname(__file__),
                                               'plugins')
        self.import_export_modules_dir = os.path.join(self.plugin_modules_dir,
                                                      'import_export')
        self.module = self.props['Module']

    def get_module(self):
        if self._loaded is not None:
            return self._loaded
        else:
            if self.curdir not in sys.path:
                sys.path.append(self.curdir)
            if self.plugin_modules_dir not in sys.path:
                sys.path.append(self.plugin_modules_dir)
            if self.import_export_modules_dir not in sys.path:
                sys.path.append(self.import_export_modules_dir)

            try:
                self._loaded = __import__(self.module)
            except ImportError as ie:
                print('WARNING: Plugin module import failed')
                print('PATH:', sys.path)
                traceback.print_exc()
                self.error = ie
                return None
            else:
                return self._loaded

    def __getattr__ (self, attr):
        if attr == 'plugins':
            return self.get_plugins()
        elif attr in self.props:
            return self.props[attr]
        elif attr.capitalize() in self.props:
            return self.props[attr.capitalize()]
        raise AttributeError

    def get_plugins(self):
        return self.get_module().plugins

    def load_plugin_file_data (self,plugin_info_file):
        # This should really use GKeyFile but there are no python
        # bindings that I can find atm. One possibility would be to
        # use this:
        # http://svn.async.com.br/cgi-bin/viewvc.cgi/kiwi/trunk/kiwi/desktopparser.py?revision=7336&view=markup
        self.props = dict.fromkeys(
            ['Name', 'Comment', 'Authors', 'Version', 'API_Version',
             'Website', 'Copyright', 'Dependencies'])

        for line in plugin_info_file.readlines():
            if '[Gourmet Plugin]' in line:
                pass
            elif line.find('=')>0:
                key,val = line.split('=')
                key = key.strip(); val = val.strip()
                key = key.strip('_')
                if (loc is not None) and ('[' in key):
                    key,locale = key.strip(']').split('[')
                    if locale==loc:
                        self.props[key] = val
                    elif locale[:2]==loc[:2]:
                        self.props[key] = val
                else:
                    self.props[key]=val
            else:
                print('Ignoring line',line)
        if self.dependencies:
            self.props['Dependencies'] = [d.strip() for d in self.dependencies.split(',')]

class Pluggable:
    """A plugin-able class."""

    def __init__ (self, plugin_klasses):
        """plugin_klasses is the list class of which each of our
        plugins should be a sub-class.

        A pluggable can take multiple types of sub-classes if it
        likes.
        """
        #print 'Pluggable.__init__([',plugin_klasses,'])'
        self.pre_hooks = {} # stores hooks to be run before methods by
                            # method name
        self.post_hooks = {} # stores hooks to be run after methods by
                             # method name
        self.loader = MasterLoader.instance()
        self.klasses = plugin_klasses
        self.plugins = []
        for klass in self.klasses:
            #print 'register self ',self,'as pluggable for ',klass
            self.loader.register_pluggable(self,klass)

    def plugin_plugin (self, plugin_instance):
        try:
            self.plugins.append(plugin_instance)
            plugin_instance.activate(self)
        except:
            print('WARNING: PLUGIN FAILED TO LOAD',plugin_instance)
            traceback.print_exc()

    def destroy (self):
        self.loader.unregister_pluggable(self,self.klass)
        for pi in self.plugins:
            pi.deactivate(self)

    def run_pre_hook (self, fname, *args, **kwargs):
        for hook in self.pre_hooks.get(fname,[]):
            try:
                new_args,new_kwargs = hook(self,*args,**kwargs)
                assert(isinstance(args,tuple))
                assert(isinstance(kwargs,dict))
            except:
                print('WARNING',hook,'did not return args,kwargs')
            else:
                args,kwargs = new_args,new_kwargs
        return args,kwargs

    def run_post_hook (self, fname, retval, *args, **kwargs):
        for hook in self.post_hooks.get(fname,[]):
            retval = hook(retval,self,*args,**kwargs)
        return retval

    def add_hook (self, type, name, hook):
        if type==PRE: hookdic = self.pre_hooks
        else: hookdic = self.post_hooks
        if name not in hookdic:
            hookdic[name] = []
        hookdic[name].append(hook)

    def remove_hook (self, type, name, hook):
        if type==PRE: hookdic = self.pre_hooks
        else: hookdic = self.post_hooks
        hookdic.pop(name, None)

    def get_plugin_by_module (self, module):
        for p in self.plugins:
            if p.__module__ == module:
                return p


class DependencyError (Exception):

    def __init__ (self, pluginset, missing_dependencies):
        self.plugin_set = pluginset
        self.dependencies = missing_dependencies
        print(self.plugin_set,'requires but did not find',self.dependencies)

    def __repr__ (self):
        return ('<DependencyError '
                + repr(self.plugin_set)
                + ' missing required dependencies '
                + repr(self.dependencies)
                )

def pluggable_method (f):
    def _ (self, *args, **kwargs):
        '''Run hooks around method'''
        args,kwargs = self.run_pre_hook(f.__name__,*args,**kwargs)
        retval = f(self,*args,**kwargs)
        retval = self.run_post_hook(f.__name__,retval,*args,**kwargs)
        return retval
    return _
