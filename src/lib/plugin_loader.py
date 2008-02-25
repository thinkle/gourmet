PRE = 0
POST = 1
import gglobals, os.path, glob, sys
import gobject
import plugin
from defaults.defaults import loc

try:
    current_path = os.path.split(os.path.join(os.getcwd(),__file__))[0]
except:
    current_path = ''

# This module provides a base class for loading plugins. Everything
# that is plug-in-able in Gourmet should subclass the plugin loader.

# Everything that is a plugin needs to provide a python module with a
# plugins attribute containing the plugin classes that make up the
# plugin. In addition, we need a .gourmet-plugin configuration file
# pointing to the module (with the module parameter) and giving the
# name and comment for the plugin.

class MasterLoader:

    # Singleton design pattern lifted from:
    # http://www.python.org/workshops/1997-10/proceedings/savikko.html
    # to get an instance, use the convenience function
    # get_master_loader()
    __single = None
    default_active_plugin_sets = [
        'unit_converter',
        'duplicate_finder',
        'key_editor',
        ]
    active_plugin_filename = os.path.join(gglobals.gourmetdir,'active_plugins')

    def __init__ (self):
        if MasterLoader.__single:
            raise MasterLoader.__single
        MasterLoader.__single = self
        curfile = gglobals.__file__ # we count on plugins/ being in the same dir as gglobals  
        self.plugin_directories = [os.path.join(gglobals.gourmetdir,'plugins/'), # user plug-ins
                                   os.path.join(current_path,'plugins'), # pre-installed plugins
                                   os.path.join(current_path,'plugins','export_plugins'), # pre-installed exporter plugins
                                   os.path.join(gglobals.datad,'plugins/'), # system-wide plug-ins (?)
                                   ]
        self.pluggables_by_class = {}
        self.load_plugin_directories()
        self.load_active_plugins()

    def load_plugin_directories (self):
        """Look through plugin directories for plugins.
        """
        self.available_plugin_sets = {}
        for d in self.plugin_directories:
            plugins = glob.glob('%s/*.gourmet-plugin'%d)
            print 'found plugins:',plugins,'in',d
            for ppath in plugins:
                plugin_set = PluginSet(ppath)
                if self.available_plugin_sets.has_key(plugin_set.module):
                    print 'Ignoring duplicate plugin ',plugin_set.module,'found in ',ppath
                else:
                    self.available_plugin_sets[plugin_set.module] = plugin_set

    def load_active_plugins (self):
        """Activate plugins that have been activated on startup
        """
        if os.path.exists(self.active_plugin_filename):
            infi = file(self.active_plugin_filename,'r')
            self.active_plugin_sets = [l.strip() for l in infi.readlines()]
            print 'active_plugin_sets = ',self.active_plugin_sets
        else:
            self.active_plugin_sets = self.default_active_plugin_sets[:]
        self.active_plugins = []
        self.instantiated_plugins = {}
        for p in self.active_plugin_sets:
            if self.available_plugin_sets.has_key(p):
                self.active_plugins.extend(self.available_plugin_sets[p].plugins)
            else:
                print 'Plugin ',p,'not found'

    def save_active_plugins (self):
        # If we have not changed from the defaults and no
        # configuration file exists, don't bother saving one.
        if ((self.active_plugin_sets != self.default_active_plugin_sets)
            or
            os.path.exists(self.active_plugin_filename)):
            print 'Saving active plugins to',self.active_plugin_filename
            ofi = file(self.active_plugin_filename,'w')
            for plugin_set in self.active_plugin_sets:
                print 'Save module...',plugin_set
                ofi.write(plugin_set+'\n')
            print 'Done saving.'
            ofi.close()
        elif self.active_plugin_sets == self.default_active_plugin_sets:
            print 'No change to plugins, nothing to save.'

    def activate_plugin_set (self, plugin_set):
        """Activate a set of plugins.
        """
        if not plugin_set in self.active_plugin_sets:
            print 'ADD ',plugin_set,'TO ACTIVE_PLUGIN_SETS'            
            self.active_plugin_sets.append(plugin_set.module)
        self.active_plugins.extend(plugin_set.plugins)
        for plugin in plugin_set.plugins:
            for klass in self.pluggables_by_class:
                if issubclass(plugin,klass):
                    for pluggable in self.pluggables_by_class[klass]:
                        pluggable.plugin_plugin(self.get_instantiated_plugin(plugin))

    def deactivate_plugin_set (self, plugin_set):
        if plugin_set in self.active_plugin_sets:
            print 'REMOVE ',plugin_set,'FROM ACTIVE_PLUGIN_SETS'
            self.active_plugin_sets.remove(plugin_set)
        for plugin in plugin_set.plugins:
            if self.instantiated_plugins.has_key(plugin):
                self.instantiated_plugins[plugin].remove()
            self.active_plugins.remove(plugin)

    def get_instantiated_plugin (self, plugin):
        if self.instantiated_plugins.has_key(plugin):
            return self.instantiated_plugins[plugin]
        else:
            self.instantiated_plugins[plugin] = plugin()
            return self.instantiated_plugins[plugin]
            
    def register_pluggable (self, pluggable, klass):
        if not self.pluggables_by_class.has_key(klass):
            self.pluggables_by_class[klass] = []
        self.pluggables_by_class[klass].append(pluggable)
        for plugin in self.active_plugins:
            print 'checking active plugin',plugin
            if issubclass(plugin,klass):
                print 'plugin ',plugin
                try:
                    plugin_instance = self.get_instantiated_plugin(plugin)
                except:
                    print 'Failed to instantiate plugin'
                    import traceback; traceback.print_exc()
                else:
                    pluggable.plugin_plugin(plugin_instance)

    def unregister_pluggable (self, pluggable, klass):
        self.pluggables_by_class[klass].remove(pluggable)

def get_master_loader ():
    # Singleton design pattern lifted from:
    # http://www.python.org/workshops/1997-10/proceedings/savikko.html    
    try:
        return MasterLoader()
    except MasterLoader, ml:
        return ml                

class PluginSet:
    """A lazy-loading set of plugins.

    This class encapsulates what to the end-user is a plugin.

    From our perspective, plugins can really be a bundle of plugins --
    for example, your plugin might require a DatabasePlugin, a
    RecCardDisplayPlugin and a MainPlugin to function.
    """

    _loaded = False
    
    def __init__ (self, plugin_info_path):
        f = file(plugin_info_path,'r')
        self.load_plugin_file_data(f)
        f.close()
        self.curdir, plugin_info_file = os.path.split(plugin_info_path)
        self.module = self.props['Module']

    def get_module (self):
        if self._loaded:
            return self._loaded
        else:
            if not self.curdir in sys.path:
                sys.path.append(self.curdir)
            try:
                self._loaded = __import__(self.module)
            except ImportError:
                print 'PATH:',sys.path
                raise
            return self._loaded

    def __getattr__ (self, attr):
        if attr == 'plugins': return self.get_plugins()
        elif self.props.has_key(attr): return self.props[attr]
        elif self.props.has_key(attr.capitalize()): return self.props[attr.capitalize()]
        else: raise AttributeError

    def get_plugins (self):
        return self.get_module().plugins

    def load_plugin_file_data (self,plugin_info_file):        
        # This should really use GKeyFile but there are no python
        # bindings that I can find atm. One possibility would be to
        # use this:
        # http://svn.async.com.br/cgi-bin/viewvc.cgi/kiwi/trunk/kiwi/desktopparser.py?revision=7336&view=markup
        self.props = dict([(k,None) for k in ['Name','Comment','Authors','Version','API_Version','Website','Copyright']])

        for line in plugin_info_file.readlines():
            if line=='[Gourmet Plugin]\n': pass
            elif line.find('=')>0:
                key,val = line.split('=')
                key = key.strip(); val = val.strip()
                key = key.strip('_')
                if '[' in key:
                    key,locale = key.strip(']').split('[')
                    if locale==loc:
                        self.props[key] = val
                    elif locale[:2]==loc[:2]:
                        self.props[key] = val
                else:
                    self.props[key]=val
            else:
                print 'Ignoring line',line

class Pluggable:
    """A plugin-able class."""
    
    def __init__ (self, plugin_klasses):
        """plugin_klasses is the list class of which each of our
        plugins should be a sub-class.

        A pluggable can take multiple types of sub-classes if it
        likes.
        """
        print 'Pluggabe.__init__([',plugin_klasses,'])'
        self.pre_hooks = {} # stores hooks to be run before methods by
                            # method name
        self.post_hooks = {} # stores hooks to be run after methods by
                             # method name
        self.loader = get_master_loader()
        self.klasses = plugin_klasses
        self.plugins = []
        for klass in self.klasses:
            print 'register self ',self,'as pluggable for ',klass
            self.loader.register_pluggable(self,klass)

    def plugin_plugin (self, plugin_instance):
        try:
            print 'plugging in ',plugin_instance
            self.plugins.append(plugin_instance)
            print 'activate!'
            plugin_instance.activate(self)
        except:
            print 'PLUGIN FAILED TO LOAD'
            import traceback; traceback.print_exc()

    def destroy (self):
        self.loader.unregister_pluggable(self,self.klass)
        for pi in self.plugins:
            print 'deactivate plugin',pi
            pi.deactivate(self)

    def run_pre_hook (self, fname, *args, **kwargs):
        print 'Looking for pre hooks for',fname
        for hook in self.pre_hooks.get(fname,[]):
            print 'run hook',hook
            hook(self,*args,**kwargs)

    def run_post_hook (self, fname, retval, *args, **kwargs):
        print 'Looking for post hooks for',fname        
        for hook in self.post_hooks.get(fname,[]):
            print 'run hook',hook
            hook(retval,self,*args,**kwargs)

    def add_hook (self, type, name, hook):
        if type==PRE: hookdic = self.pre_hooks
        else: hookdic = self.post_hooks
        if not hookdic.has_key(name):
            hookdic[name] = []
        hookdic[name].append(hook)

    def remove_hook (self, type, name, hook):
        if type==PRE: hookdic = self.pre_hooks
        else: hookdic = self.post_hooks
        del hookdic[name]

def pluggable_method (f):
    def _ (self, *args, **kwargs):
        '''Run hooks around method'''
        self.run_pre_hook(f.__name__,*args,**kwargs)
        retval = f(self,*args,**kwargs)
        self.run_post_hook(f.__name__,retval,*args,**kwargs)
        return retval
    return _

if __name__ == '__main__':
    class TestPlugin (plugin.Plugin):
        def activate ():
            print 'Activate!'
        def deactivate ():
            print 'Deactivate!'
    
    class UniversalPluggable (Pluggable):
        def __init__ (self):
            Pluggable.__init__(self,[plugin.Plugin])

    up = UniversalPluggable()
    #up.loader.activate_plugin(
    print up.plugins
