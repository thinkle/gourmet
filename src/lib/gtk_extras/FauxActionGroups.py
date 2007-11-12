#!/usr/bin/env python
import gtk.glade, gtk
from gourmet.gdebug import *
from gettext import gettext as _
from gettext import ngettext

# Here we have some classes that implement ActionGroups. This is
# somewhat ugly, but we're designing our interface in glade (which
# doesn't understand ActionGroups) and we still want to use this
# feature -- which lets us automatically associate multiple widgets
# with an action and have things like toggles just work.

class ActionTwoPointFourCompatability:
    """Provide functions that pygtk 2.4 fails to provide for the
    ActionGroup class.

    This class should be inherited from AFTER gtk.Action so that if
    the proper functions are available (i.e. > pygtk 2.6, we won't use
    these at all.
    """
    def set_visible (self, value):
        for w in self.get_proxies():
            if hasattr(w,'set_visible'): w.set_visible(value)

    def get_visible (self):
        for w in self.get_proxies():
            if hasattr(w,'get_visible'): return w.get_visible()

    def set_sensitive (self, value):
        for w in self.get_proxies():
            if hasattr(w,'set_sensitive'): w.set_sensitive(value)

    def get_sensitive (self):
        for w in self.get_proxies():
            if hasattr(w,'get_sensitive'): return w.get_sensitive()


class ToggleActionWithSeparators (gtk.ToggleAction,ActionTwoPointFourCompatability):
    """Create a ToggleAction which can include some separators.

    This allows us to make separators become visible/invisible in sync
    with controls for an action.
    
    This is much worse than the default UIManager way of handling
    separators automatically, but it works with glade as it is made at
    the moment.
    """
    def __init__ (self, *args, **kwargs):
        self.separators = []
        gtk.ToggleAction.__init__(self,*args,**kwargs)

    def add_separator (self, separator_widget):
        self.separators.append(separator_widget)

    def set_visible (self, *args, **kwargs):
        gtk.ToggleAction.set_visible(self,*args,**kwargs)
        if self.is_visible():
            for s in self.separators: s.set_visible(True)
        else:
            for s in self.separators: s.set_visible(False)
            
class ActionWithSeparators (gtk.Action,ActionTwoPointFourCompatability):
    """Create an Action which can include some separators.

    This allows us to make separators become visible/invisible in sync
    with controls for an action.

    This is much worse than the default UIManager way of handling
    separators automatically, but it works with glade as it is made at
    the moment.
    """
    def __init__ (self, *args, **kwargs):
        self.separators = []
        gtk.Action.__init__(self,*args,**kwargs)

    def add_separator (self, separator_widget):
        self.separators.append(separator_widget)

    def set_visible (self, *args, **kwargs):
        gtk.Action.set_visible(self,*args,**kwargs)
        if self.is_visible():
            for s in self.separators: s.set_visible(True)
        else:
            for s in self.separators: s.set_visible(False)

class ActionGroupWithSeparators (gtk.ActionGroup,ActionTwoPointFourCompatability):
    """Create an ActionGroup which can include some separators.

    This allows us to make separators become visible/invisible in sync
    with controls for an action.

    This is much worse than the default UIManager way of handling
    separators automatically, but it works with glade as it is made at
    the moment.
    """
    def __init__ (self, *args, **kwargs):
        self.separators = []
        gtk.ActionGroup.__init__(self,*args,**kwargs)

    def add_separator (self, separator_widget):
        self.separators.append(separator_widget)

    def set_visible (self, visible):
        gtk.ActionGroup.set_visible(self,visible)
        for s in self.separators:
            try:
                s.set_property('visible',visible)
            except:
                debug('no widget %s'%s,5)

class ActionManager:
    """This is a class to handle all Actions for a GUI

    This can be conveniently subclassed by any class handling the main
    GUI interactions.

    This class is made to be the glue between traditional glade and
    ActionManager kung-fu.
    """
    
    def __init__ (self, gladeobj, groups, callbacks):
        """Set up our ActionManager.

        gladeobj - Our route to glade stuff (created by
                   gtk.glade.XML('/path/to/glade')

        groups - a dictionary of group names and actions within them
                 actions are rather complicated...

                 actions are also dictionaries.
                 {'actionName' : [{'tooltip':...,'label':...,...},
                                  ['widgetName','widgetName','widgetName'...]
                                  ]},

                 If parameters 'label', 'stock-id' are not provided,
                 we will attempt to grab them from the first widget using methods
                 get_label() and  get_stock_id(). If we are unable, we will throw
                 an error, because you really do need a label. The solution is to
                 provide the label, or make the first widget in your list one that
                 supports these methods.
                 
        callbacks - an alist of action names and callbacks to be
                    called when the action is activated.
        """
        self.gladeobj = gladeobj
        self.groups = groups
        self.callbacks = callbacks
        self.action_groups = [self.init_group(gname, actions) for gname,actions in self.groups.items()]
        self.make_connections()

    def init_group (self, name, actions):
        setattr(self,name,ActionGroupWithSeparators(name))
        for a in actions:
            for n,ainfo in a.items():
                params,widgets = ainfo
                widg=None
                if not params.has_key('label'):
                    if not widg: widg = self.gladeobj.get_widget(widgets[0])
                    if not widg: raise "Can't find widget %s"%widgets[0]
                    label = widg.get_label()
                    params['label']=label
                if not params.has_key('stock-id'):
                    if not widg: widg = self.gladeobj.get_widget(widgets[0])
                    if not widg: raise "Can't find widget %s"%widgets[0]
                    stockid = widg.get_stock_id()
                    params['stock-id']=stockid
                if not params.has_key('tooltip'):
                    params['tooltip']=''
                widg = self.gladeobj.get_widget(widgets[0])
                try:
                    temp_connection=widg.connect('toggled',lambda *args: False)
                    widg.disconnect(temp_connection)                    
                except TypeError: #unknown signal name (i.e. not a toggle)
                    act = ActionWithSeparators(n,params['label'],params['tooltip'],params['stock-id'])
                else:
                    act = ToggleActionWithSeparators(n,params['label'],params['tooltip'],params['stock-id'])
                if params.has_key('separators'):
                    if type(params['separators']==str): params['separators']=[params['separators']]
                    act.separators=[self.gladeobj.get_widget(w) for w in params['separators']]
                    getattr(self,name).separators.extend(act.separators)
                for w in widgets:
                    ww = self.gladeobj.get_widget(w)
                    if ww:
                        act.connect_proxy(ww)
                    else:
                        debug('Widget %s does not exist!'%w,0)
                # create action as an attribute
                setattr(self,n,act)
                # attach to our ActionGroup                
                getattr(self,name).add_action(act)
        return getattr(self,name)

    def make_connections (self):
        for a,cb in self.callbacks:
            debug('connecting %s activate to %s'%(a,cb),5)
            getattr(self,a).connect('activate',cb)


            
