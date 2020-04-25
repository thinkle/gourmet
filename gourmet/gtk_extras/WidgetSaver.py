import os

from gi.repository import Gdk, Gtk

from gourmet.gdebug import debug


class WidgetSaver:

    """A class to save and load widget properties to/from a
    dictionary. We leave it to whoever hands us the dictionary to save
    the dictionary. dictionary should contain a property name as a key
    and a value as a value. On __init__, we will load these properties
    into the widget and who the widget. Each signal in signals will be
    connected to save_properties"""

    def __init__ (self, widget, dictionary={}, signals=['destroy'], show=True):
        self.w = widget
        self.dictionary = dictionary
        self.signals = signals
        self.load_properties()
        for s in self.signals:
            self.w.connect(s,self.save_properties)
        if show: self.w.show()

    def load_properties (self):
        for p,v in list(self.dictionary.items()):
            self.w.set_property(p,v)

    def save_properties (self, *args):
        for p in list(self.dictionary.keys()):
            self.dictionary[p]=self.w.get_property(p)
        return False # we don't handle any signals

class WindowSaver (WidgetSaver):
    def __init__ (self, widget, dictionary={},
                  signals=['configure-event','delete-event'],
                  show=True):
        """We save the position and state of the window
        in dictionary. The dictionary consists of
        {window_size: widget.get_size(),
         position: widget.get_position(),}"""

        # Window positioning is bad on Windows -- setting
        # GRAVITY_STATIC creates a nightmare for users, so we'll just
        # disable this whole thing
        if os.name=='nt': return

        widget.set_gravity(Gdk.Gravity.STATIC)
        #widget.set_gravity(Gdk.GRAVITY_NORTH_WEST)
        WidgetSaver.__init__(self, widget, dictionary, signals, show)

    def load_properties (self):
        #if os.name=='nt': return
        for p,f in ['window_size', self.w.resize],['position',self.w.move]:
            if p in self.dictionary and self.dictionary[p]:
                debug('applying %s %s'%(f,self.dictionary[p]),3)
                #if os.name=='nt' and p=='position' and self.dictionary['position'][1]<20:
                #    #print 'FIDDLING WITH WINDOW FOR WINDOWS'
                #    #self.dictionary[p] = self.dictionary[p][0],20
                f(*self.dictionary[p])

    def save_properties (self, *args):
        if os.name=='nt': return
        if isinstance(self.w, Gtk.Window) and not self.w.get_state()&Gdk.WindowState.MAXIMIZED:
            # ignore the maximized window when we save sizes
            self.dictionary['window_size']=self.w.get_size()
            self.dictionary['position']=self.w.get_position()
            # For Windows, we sometimes have windows put out of view...
            #if self.dictionary['position'][1] < 20:
            #    self.w.set_position((self.dictionary['position'][0],20))
            #    #self.dictionary['position']=self.w.get_position()
            debug('Saved properties: %s'%self.dictionary,4)
        return False

class WidgetPrefs:
    def __init__ (self, prefs, glade=None, hideable_widgets=[], basename='hide_'):
        """hideable_widgets is a list of tuples:
        (widget_name, widget_desc)
        OR
        ([widget_name,widget_name],widget_desc)

        widget_name is a string,  handed to glade: glade.get_widget(widget)
        Multiple widget_names are allowed so that we can hide things like widgets
        and labels in one fell swoop
        """
        self.glade = glade
        self.basename = basename
        self.hideable_widgets = hideable_widgets
        self.apply_widget_prefs()

    def toggle_widget (self, w, val):
        """Toggle the visibility of widget 'w'"""
        if val: method = 'hide'
        else: method = 'show'
        if type(w)==type(""): w = [w]
        for wn in w:
            widg = self.glade.get_widget(wn)
            if widg:
                getattr(widg,method)()
            else:
                debug('There is no widget %s'%wn,1)

    def apply_widget_prefs (self):
        """Apply our widget preferences."""
        for w,desc in self.hideable_widgets:
            if self.get_widget_pref(w):
                self.toggle_widget(w,True)
            else:
                self.toggle_widget(w,False)

    def get_widget_pref (self,w):
        """Get our widget preferences."""
        return self.prefs.get(self.keyname(w),False)

    def keyname (self, w):
        if type(w)==type([]): w = w[0]
        return "%s%s"%(self.basename,w)

    def set_widget_pref (self,w,val):
        self.prefs[self.keyname(w)]=val
        self.toggle_widget(w,val)

    def apply_option (self, options):
        for tup in options:
            desc,val = tup
            w=self.apply_pref_dic[desc]
            self.set_widget_pref(w,val)

    def make_option_list (self):
        option_list = []
        self.apply_pref_dic={}
        for w,desc in self.hideable_widgets:
            pref = (['Hide %s'%desc,self.get_widget_pref(w)])
            self.apply_pref_dic[pref[0]]=w
            option_list.append(pref)
        return option_list

    def show_pref_dialog (self,*args):
        from . import dialog_extras
        pd=dialog_extras.preferences_dialog(
            options=self.make_option_list(),
            apply_func=self.apply_option)
        pd.run()
