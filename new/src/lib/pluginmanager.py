import os
import imp

import gobject

from gourmet import gglobals

class PluginManager(gobject.GObject):

    __gsignals__ = {
        "plugin-enabled-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT)),
        "plugin-installed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT)),
        "plugin-uninstalled" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT)),
    }

    def __init__(self):
        """ 
        Initialize a new plugin manager 
        """
        gobject.GObject.__init__(self)
        self.pluginbag = {}
        self.plugin_paths = [gglobals.core_plugin_path,]
        self.load_all()

    def load_all(self)
        for path in self.plugin_paths:
            pass

    def enable_plugin(self, plugin):
        """
        Enable a plugin
        """
        plugin.enabled = True
        self.emit('plugin-enabled-changed', plugin.name)

    def disable_plugin(self, plugin):
        """
        Disable a plugin
        """
        plugin.enabled = False
        self.emit('plugin-enabled-changed', plugin.name)
