import gtk, os.path
import gglobals
from gtk_extras import optionTable
import plugin_loader, plugin

class PreferencesGui (plugin_loader.Pluggable):
    """The glue between our preferences dialog UI and our prefs modules.

    Instead of "connecting", as would be normal with pygtk objects, we set up handlers in the
    apply_prefs_dic which contains preference-handlers for each preference we wish.

    {'preference_name':lambda foo (name,val): bar(name,val)}
    """
    
    INDEX_PAGE = 0
    CARD_PAGE = 1
    SHOP_PAGE = 2

    def __init__ (
        self,
        prefs,
        uifile=os.path.join(gglobals.gladebase,
                            'preferenceDialog.ui'),
        radio_options={'shop_handle_optional':{'optional_ask':0,
                                               'optional_add':1,
                                               'optional_dont_add':-1
                                               }
                       },
        toggle_options={'remember_optionals_by_default':'remember_optionals_by_default',
                        'readableUnits':'toggle_readable_units',
                        'useFractions':'useFractions',
                        #'email_include_body':'email_body_checkbutton',
                        #'email_include_html':'email_html_checkbutton',
                        #'emailer_dont_ask':'remember_email_checkbutton',
                        },

        number_options = {'recipes_per_page':'recipesPerPageSpinButton'},
        
        buttons = {}
        #buttons = {'clear_remembered_optional_button':
        ):
        """Set up our PreferencesGui

        uifile points us to our UI file
        
        radio_options is a dictionary of preferences controlled by radio buttons.
                      {preference_name: {radio_widget: value,
                                         radio_widget: value, ...}
                                         }

        toggle_options is a dictionary of preferences controlled by toggle buttons.
                      {preference_name: toggle_widget_name}
        buttons = {button_name : callback}
                      
        """

        self.prefs = prefs
        self.ui = gtk.Builder()
        self.ui.add_from_file(uifile)
        self.notebook = self.ui.get_object('notebook')
        # pref name: {'buttonName':VALUE,...}
        self.radio_options = radio_options
        self.connect_radio_buttons()
        self.toggle_options = toggle_options
        self.apply_prefs_dic = {}
        self.widget_sensitivity_dic = {
            # pref : {'value':('widget':True,'widget':False,'widget':True...)}
            'shop_handle_optional':{0:{'remember_optionals_by_default':True,
                                       'clear_remembered_optional_button':True},
                                    1:{'remember_optionals_by_default':False,
                                       'clear_remembered_optional_button':False},
                                    -1:{'remember_optionals_by_default':False,
                                       'clear_remembered_optional_button':False}
                                    }
            }
        self.connect_toggle_buttons()
        self.buttons=buttons
        self.connect_buttons()
        self.number_options = number_options
        self.connect_number_options()
        self.build_pref_dictionary()
        self.set_widgets_from_prefs()
        self.prefs.set_hooks.append(self.update_pref)
        self.pref_tables={}
        self.ui.get_object('close_button').connect('clicked',lambda *args: self.hide_dialog())
        plugin_loader.Pluggable.__init__(self,[plugin.PrefsPlugin])

    def build_pref_dictionary (self):
        """Build our preferences dictionary pref_dic

        preference: BOOLEAN_WIDGET|{VALUE:RADIO_WIDGET,VALUE:RADIO_WIDGET...}
                    METHOD_TO_BE_HANDED_PREF_VALUE

        pref_dic will be used to e.g. set default values and watch
        changing preferences.
        """
        self.pref_dic = {}
        for pref,widget in self.toggle_options.items():
            self.pref_dic[pref]=('TOGGLE',widget)
        for pref,widgdic in self.radio_options.items():
            self.pref_dic[pref]={}
            # create a dictionary by value (reversed dictionary)...
            for widg,val in widgdic.items(): self.pref_dic[pref][val]=widg
        self.d=self.ui.get_object('dialog')
        self.d.connect('delete-event',self.hide_dialog)


    def set_widgets_from_prefs (self):
        for k in self.pref_dic.keys():
            if self.prefs.has_key(k): self.update_pref(k,self.prefs[k])

    def update_pref (self, pref, value):
        """Update GUI to reflect value 'value' of preference 'pref'."""
        if self.pref_dic.has_key(pref):
            action=self.pref_dic[pref]
            if type(action)== dict :
                # we fail if action is no
                widg=action[value]
                act,act_args=('set_active',True)
            elif action[0]=='TOGGLE':
                act,act_args=('set_active',value)
                widg=action[1]
            # in the future, we can handle Entries, etc...
            if type(widg)==str:
                widg=self.ui.get_object(widg)
            getattr(widg,act)(act_args)
            self.update_sensitivity_for_pref(pref,value)
            
    def show_dialog (self, page=None):
        """present our dialog."""        
        self.d.present()
        if page:
            self.notebook.set_current_page(page)

    def hide_dialog (self,*args):
        self.d.hide()
        return True

    def connect_buttons (self):
        for b,cb in self.buttons.items():
            self.ui.get_object(b).connect('clicked',cb)

    def connect_toggle_buttons (self):
        """Connect signals for toggle buttons in self.toggle_options."""
        for pref,widget in self.toggle_options.items():
            self.ui.get_object(widget).connect('toggled',self.toggle_callback,pref)

    def toggle_callback (self, button, pref_name):
        """Set preference 'pref_name' in response to toggle event on button."""
        self.set_pref(pref_name, button.get_active())
        
    def connect_radio_buttons (self):
        """Connect radio button signals to properly set preferences on toggle."""
        for pref_name,pref_dic in self.radio_options.items():
            for button,val in pref_dic.items():
                self.ui.get_object(button).connect(
                    'toggled',
                    self.radio_callback,
                    pref_name,
                    val)

    def radio_callback (self, button, pref_name, true_val=True):
        """Call back for radio button: if we are on, we set the pref to true_val."""
        if button.get_active():
            self.set_pref(pref_name,true_val)

    def connect_number_options (self):
        for pref_name,widgetname in self.number_options.items():
            widget = self.ui.get_object(widgetname)
            if hasattr(widget,'get_value'):
                get_method='get_value'
            elif hasattr(widget,'get_text'):
                get_method=lambda *args: float(widget.get_text())
            else:
                print 'widget',widgetname,widget,'is not very numberlike!'
                return
            curval = self.prefs.get(pref_name,None)
            if curval:
                try:
                    widget.set_value(curval)
                except:
                    widget.set_text(str(curval))
            if isinstance(widget,gtk.SpinButton):
                widget.get_adjustment().connect('value-changed',self.number_callback,pref_name,get_method)
            else:
                widget.connect('changed',self.number_callback,pref_name,get_method)

    def number_callback (self, widget, pref_name, get_method='get_value'):
        self.set_pref(pref_name,getattr(widget,get_method)())

    def set_pref (self, name, value):
        """Set preference 'name' to value 'value'

        Possibly apply the preference using callback looked up in
        apply_prefs_dic (callback must take name and value of pref as
        arguments.
        """
        self.prefs[name]=value
        if self.apply_prefs_dic.has_key(name):
            self.apply_prefs_dic[name](name,value)

    def update_sensitivity_for_pref (self, name, value):
        try:
            for k,v in self.widget_sensitivity_dic[name][value].items():
                self.ui.get_object(k).set_sensitive(v)
        except KeyError: pass
            

    def add_widget (self, target_widget, child_widget):
        """Add child_widget to target_widget"""
        if type(target_widget)==str: target_widget=self.ui.get_object(target_widget)
        if type(child_widget)==str: child_widget=self.ui.get_object(child_widget)
        target_widget.add(child_widget)
        target_widget.show_all()

    def add_pref_table (self, options, target_widget, callback=None):
        """Add a preference table based on an option list 'options' to the
        target_widget 'target_widget' (either a widget or a glade-reference)

        The options need to be appropriate for an OptionTable.

        The callback will be handed the options (as returned by
        OptionTable) each time OptionTable is changed.
        """
        table=optionTable.OptionTable(options=options, changedcb=self.preftable_callback)
        self.pref_tables[table]=callback
        self.add_widget(target_widget,table)

    def preftable_callback (self, widget):
        for table,cb in self.pref_tables.items():
            if widget in table.get_children():
                # then we know who's preferences we care about...
                table.apply()
                if cb: cb(table.options)
                return
        print "Oops: we couldn't handle widget %s"%widget
        
if __name__ == '__main__':
    class FauxPrefs (dict):
        def __init__ (self,*args,**kwargs):
            self.set_hooks = []
            dict.__init__(self,*args,**kwargs)

        def __setitem__ (self,k,v):
            print 'k:',k
            print 'v:',v
            dict.__setitem__(self,k,v)
            for h in self.set_hooks:
                print 'runnnig hook'
                h(k,v)
            
    gf='/home/tom/Projects/grm-db-experiments/glade/preferenceDialog.ui'
    import sys
    p=PreferencesGui(FauxPrefs(),gf)
    def printstuff (*args): print args
    p.add_pref_table([["Toggle Option",True],
                      ["String Option","Hello"],
                      ["Integer Option",1],
                      ["Float Option",float(3)]],
                     'cardViewVBox',
                     printstuff
                     )
    p.show_dialog()
    gtk.main()
