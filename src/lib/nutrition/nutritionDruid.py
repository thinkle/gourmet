import gtk, gtk.glade, gobject
import gourmet.convert as convert
import gourmet.gglobals as gglobals
from gourmet.mnemonic_manager import MnemonicManager
from gourmet.defaults import lang as defaults
from gourmet.pageable_store import PageableViewStore
from nutritionLabel import NUT_LAYOUT, SEP, RECOMMENDED_INTAKE
from gourmet.numberEntry import NumberEntry
import gourmet.cb_extras as cb
import gourmet.dialog_extras as de
import gourmet.WidgetSaver as WidgetSaver
import re
import os,os.path

class SpecialAction:

    """A convenience class for a UI element where suddenly we want to
    highlight one action for a user to do and desensitize other
    elements of the UI temporarily.
    """

    def __init__ (self,
                  highlight_widgets=[],
                  initially_hidden=True,
                  grabs_focus=True,
                  hide_on_highlight=[],
                  all_controls=[],):
        """Initialize a SpecialAction that can be highlighted/sensitized/hidden conveniently.

        highlight_widgets is a list of the widgets we want to highlight.

        initially_hidden is a boolean or a list.
        If it's a boolean, it tells us whether all highlighted widgets are normally hidden.
        If it's a list, it is a list of widgets to hide.

        If grabs_focus is True, we grab focus for the first of the highlight_widgets.
        If grabs_focus is a widget, we grab focus for that widget.
        If grabs_focus is False, we don't grab focus.
        """
        self.highlight_widgets = highlight_widgets
        self.initially_hidden = initially_hidden
        self.all_controls = all_controls
        self.hide_on_highlight = hide_on_highlight
        if self.initially_hidden:
            if isinstance(self.initially_hidden,list):
                for w in self.initially_hidden: w.hide()
            else:
                for w in self.highlight_widgets: w.hide()

    def highlight_action (self,*args):
        self.prev_states = []
        for c in self.all_controls:
            self.prev_states.append(c.get_property('sensitive'))
            c.set_sensitive(False)
        for c in self.hide_on_highlight:
            c.hide()
        for w in self.highlight_widgets:
            w.set_sensitive(True)
            w.show()
        self.highlight_widgets[0].grab_focus()

    def dehighlight_action (self,*args):
        for n,c in enumerate(self.all_controls):
            c.set_sensitive(self.prev_states[n])
        if self.initially_hidden==True:
            for w in self.highlight_widgets: w.hide()
        if type(self.initially_hidden)==list:
            for w in self.initially_hidden: w.hide()
        for c in self.hide_on_highlight:
            c.show()
    
class NutritionInfoDruid (gobject.GObject):

    """A druid (or wizard) to guide a user through helping Gourmet
    calculate nutritional information for an ingredient.

    This consists in finding a USDA equivalent of the ingredient in
    question and possibly of converting a unit.
    """

    NUT_PAGE = 0
    UNIT_PAGE = 1
    CUSTOM_PAGE = 2

    __gsignals__ = {
        'finish':(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE,())
        }

    PACKAGED_FOODS = ['Soups, Sauces, and Gravies',
                      'Baked Products',
                      'Meals, Entrees, and Sidedishes',
                      'Fast Foods',
                      'Baby Foods']

    def __init__ (self, nd, prefs):
        # Very primitive custom handler here -- we just return a
        # NumberEntry no matter what glade says. Obviously if glade
        # gets updated we'd better fix this (see reccard.py for a more
        # sophisticated example).
        gtk.glade.set_custom_handler(lambda *args: NumberEntry())
        self.glade = gtk.glade.XML(os.path.join(gglobals.gladebase,'nutritionDruid.glade'))
        self.mm = MnemonicManager()
        self.mm.add_glade(self.glade)
        self.mm.fix_conflicts_peacefully()
        self.prefs = prefs
        self.nd = nd
        self.rd = self.nd.db
        self._setup_widgets_()
        self.backButton.set_sensitive(False)
        # keep track of pages/setups we've been on 
        self.path = []
        self.curpage = 0
        self._setup_nuttree_()
        self.__last_search__ = ''
        self.__override_search__ = False
        gobject.GObject.__init__(self)
        # Save our position with our widget saver...
        WidgetSaver.WindowSaver(self.glade.get_widget('window1'),
                                self.prefs.get('nutritionDruid',{})
                                )
        WidgetSaver.WidgetSaver(
            self.searchAsYouTypeToggle,
            self.prefs.get('sautTog',
                           {'active':True}),
            ['toggled'])

    # Setup functions
    def _setup_widgets_ (self):
        self.controls = []
        for widget_name in ['notebook',
                            'ingKeyLabel','ingKeyEntry','changeKeyButton','applyKeyButton',
                            'ingKeyLabel2',
                            'customNutritionAmountEntry',
                            'searchEntry','searchAsYouTypeToggle','findButton',
                            'firstButton','backButton','forwardButton','lastButton','showingLabel',
                            'treeview','customBox',
                            'convertUnitLabel','fromUnitComboBoxEntry','fromUnitLabel',
                            'changeUnitButton','cancelUnitButton','saveUnitButton',
                            'fromAmountEntry','toUnitCombo',
                            'toAmountEntry',
                            'prevDruidButton',
                            'ignoreButton',
                            'applyButton',
                            'massUnitComboBox',
                            'customNutritionAmountEntry',
                            ]:
            setattr(self,widget_name,self.glade.get_widget(widget_name))
            if not getattr(self,widget_name): print "WIDGET: ",widget_name,"NOT FOUND."
            # make a list of all core control widgets
            if widget_name!='notebook': self.controls.append(getattr(self,widget_name))
        self.glade.signal_autoconnect({
            'previousPage':self.previous_page_cb,
            'applyPage':self.apply_cb,
            'ignorePage':self.ignore_cb,
            'customPage':self.custom_cb,
            'usdaPage':self.usda_cb,
            }
                                      )
        # hide our tabs...
        self.notebook.set_show_tabs(False)
        # custom widgety stuff
        self.changeIngKeyAction = SpecialAction(highlight_widgets=[self.ingKeyEntry,self.applyKeyButton,
                                                                   ],
                                                initially_hidden=True,
                                                hide_on_highlight=[self.ingKeyLabel,self.changeKeyButton,
                                                                   ],
                                                all_controls=self.controls)
        self.changeKeyButton.connect('clicked',self.changeIngKeyAction.highlight_action)
        self.applyKeyButton.connect('clicked',self.apply_ingkey)
        self.changeUnitAction = SpecialAction(highlight_widgets=[self.fromUnitComboBoxEntry,
                                                                 self.saveUnitButton,
                                                                 self.cancelUnitButton,],
                                              initially_hidden=True,
                                              hide_on_highlight=[self.fromUnitLabel,self.changeUnitButton],
                                              all_controls=self.controls)
        self.changeUnitButton.connect('clicked',self.changeUnitAction.highlight_action)
        self.cancelUnitButton.connect('clicked',self.changeUnitAction.dehighlight_action)
        self.saveUnitButton.connect('clicked',self.save_unit_cb)
        # search
        self.searchEntry.connect('changed',self.search_type_cb)
        self.findButton.connect('clicked',self.search_cb)
        self.searchAsYouTypeToggle.connect('toggled',self.toggle_saut)
        # Nutrition box...
        self.custom_box=self.glade.get_widget('customBox')
        self.customNutritionAmountEntry.connect('changed',self.custom_unit_changed)
        self.massUnitComboBox.connect('changed',self.custom_unit_changed)
        self._setup_custom_box()

    def _setup_custom_box (self):
        t = gtk.Table()
        masses = [i[0] for i in defaults.UNIT_GROUPS['metric mass'] + defaults.UNIT_GROUPS['imperial weight']]
        cb.set_model_from_list(
            self.massUnitComboBox,
            masses)
        cb.cb_set_active_text(self.massUnitComboBox,'g.')
        self.customNutritionAmountEntry.set_value(100)
        self.nutrition_info = {}
        self.custom_box.add(t)
        self.changing_percent_internally = False
        self.changing_number_internally = False
        l=gtk.Label('%RDA'); l.show()
        t.attach(l,2,3,0,1)
        for n,nutstuff in enumerate(NUT_LAYOUT):
            if nutstuff == SEP:
                hs = gtk.HSeparator()
                t.attach(hs,0,2,n+1,n+2,xoptions=gtk.FILL)
                hs.show()
                continue
            label_txt,typ,name,properties,show_percent,unit = nutstuff
            if unit: label_txt += " (" + unit + ")"
            label = gtk.Label(label_txt); label.show()
            label.set_alignment(0,0.5)
            t.attach(label,0,1,n+1,n+2,xoptions=gtk.FILL)
            entry = NumberEntry(); entry.show()
            t.attach(entry,1,2,n+1,n+2,xoptions=gtk.FILL)
            if show_percent:
                percent_entry = NumberEntry(); percent_entry.show()
                percent_label = gtk.Label('%'); percent_label.show()
                t.attach(percent_entry,2,3,n+1,n+2)
                t.attach(percent_label,3,4,n+1,n+2)
                percent_label.set_alignment(0,0.5)
                percent_entry.connect('changed',self.percent_changed_cb,name,entry)
                percent_entry.entry.set_width_chars(5)
            else: percent_entry = None
            entry.connect('changed',self.number_changed_cb,name,percent_entry)
        t.set_row_spacings(6)
        t.set_col_spacings(12)
        t.show()

    def number_changed_cb (self, widget, name, percent_widget):
        v = widget.get_value()
        self.nutrition_info[name]=v
        if not v: return
        if self.changing_number_internally: return
        if percent_widget:
            rda = RECOMMENDED_INTAKE.get(name,None)*2000
            if rda:
                self.changing_percent_internally = True
                percent_widget.set_value((float(v)/rda)*100)
                self.changing_percent_internally = False
        
    def percent_changed_cb (self, widget, name, number_widget):
        if self.changing_percent_internally: return
        v = widget.get_value()
        if not v: return
        if number_widget:
            rda = RECOMMENDED_INTAKE.get(name,None)*2000
            if rda:
                self.changing_number_internally = True
                number_widget.set_value(
                    v*0.01*rda
                    )
                self.changing_number_internally = False

    def custom_unit_changed (self, *args):
        amount = self.customNutritionAmountEntry.get_value()
        unit = cb.cb_get_active_text(self.massUnitComboBox)
        if amount and unit:
            base_convert = self.nd.conv.converter(unit,'g.')/float(100)
            self.custom_factor = 1/(base_convert * amount)

    def _setup_nuttree_ (self):
        """Set up our treeview with USDA nutritional equivalents"""
        self.nutrition_store = PageableNutritionStore(self.rd.nview)
        self.firstButton.connect('clicked', lambda *args: self.nutrition_store.goto_first_page())
        self.lastButton.connect('clicked', lambda *args: self.nutrition_store.goto_last_page())
        self.forwardButton.connect('clicked', lambda *args: self.nutrition_store.next_page())
        self.backButton.connect('clicked', lambda *args: self.nutrition_store.prev_page())
        self.nutrition_store.connect('page-changed',self.update_nuttree_showing)
        self.nutrition_store.connect('view-changed',self.update_nuttree_showing)        
        self.update_nuttree_showing()
        self.searchvw = self.rd.nview
        self.treeview.set_model(self.nutrition_store)
        renderer = gtk.CellRendererText()
        col = gtk.TreeViewColumn('Item',renderer,text=1)
        self.treeview.append_column(col)

    def update_nuttree_showing (self,*args):
        self.showingLabel.set_text('Showing results %s to %s of %s'%self.nutrition_store.showing())
        # update buttons too
        cp = self.nutrition_store.page
        lp = self.nutrition_store.get_last_page()
        if cp == 0:
            self.firstButton.set_sensitive(False)
            self.backButton.set_sensitive(False)
        else:
            self.firstButton.set_sensitive(True)
            self.backButton.set_sensitive(True)
        if cp == lp:
            self.lastButton.set_sensitive(False)
            self.forwardButton.set_sensitive(False)
        else:
            self.lastButton.set_sensitive(True)
            self.forwardButton.set_sensitive(True)

    # methods to set our core values
    def set_ingkey (self, txt):
        self.ingKeyEntry.set_text(txt)
        self.ingKeyLabel.set_markup('<i><b>'+txt+'</b></i>')
        self.ingKeyLabel2.set_markup('<i><b>'+txt+'</b></i>')
        self.nutrition_info['desc']=txt
        self.ingkey = txt

    def set_from_unit (self, txt):
        if not self.ingkey:
            return
        if txt:
            self.fromUnitLabel.set_text(txt)
            self.fromUnitComboBoxEntry.get_children()[0].set_text(txt)
            self.fromUnit = txt
            curamt = ' '.join([convert.float_to_frac(self.amount,
                                                     fractions=convert.FRACTIONS_ASCII),
                               self.fromUnit,self.ingkey])
        else:
            self.fromUnitLabel.set_text(self.ingkey+' (no unit)')
            self.fromUnit = ''
            curamt = convert.float_to_frac(
                self.amount,
                fractions=convert.FRACTIONS_ASCII)+' '+self.ingkey
        self.convertUnitLabel.set_markup('<span weight="bold" size="larger">' + \
                                         _('Convert unit for %s')%self.ingkey + \
                                         '</span>' + \
                                         '\n<i>' + \
                                         _('In order to calculate nutritional information, Gourmet needs you to help it convert "%s" into a unit it understands.')%curamt + \
                                         '</i>')

    def setup_to_units (self):
        """Setup list of units we need to convert to.

        Usually, this will be a list of mass units.
        """
        masses = [i[0] for i in defaults.UNIT_GROUPS['metric mass'] + defaults.UNIT_GROUPS['imperial weight']]
        volumes = [i[0] for i in  defaults.UNIT_GROUPS['metric volume'] + defaults.UNIT_GROUPS['imperial volume']]
        to_units = masses
        self.to_to_grams = {}
        self.densities,self.extra_units = self.nd.get_conversions(self.ingkey)
        for d in self.densities.keys():
            if d:
                to_units.extend(["%s (%s)"%(u,d) for u in volumes])
            else:
                to_units.extend(volumes)
        to_units.sort()
        for u in self.extra_units:
            to_units = [u]+to_units
        cb.set_model_from_list(self.toUnitCombo,
                               to_units)
        self.toUnitCombo.set_active(0)
        self.toUnitCombo.set_wrap_width(3)

    # search callbacks &c.
    def toggle_saut (self, *args):
        if self.searchAsYouTypeToggle.get_active():
            self.findButton.hide()
        else:
            self.findButton.show()

    def search_type_cb (self, *args):
        if self.searchAsYouTypeToggle.get_active(): self.search_cb()

    def search_cb (self, *args):
        if self.__override_search__: return
        gobject.idle_add(self.search)

    def search (self):
        txt = self.searchEntry.get_text()
        if self.__last_search__ == txt:
            return
        if txt.find(self.__last_search__)==0:
            repeat = True
            search_in = self.searchvw
        else:
            repeat = False
            search_in = self.rd.nview
        words = re.split('\W+',txt)
        last_words = self.__last_search__.split()
        # Not exactly an efficient search algorithm...
        for w in words:
            if not w or w==' ': continue
            if w in last_words and repeat:
                continue
            if search_in:
                search_in = self.rd.search(search_in,
                                           'desc',
                                           w,
                                           use_regexp=False)
        self.searchvw = search_in
        self.__last_search__ = txt
        self.nutrition_store.change_view(self.searchvw)
        self.nutrition_store.set_page(self.NUT_PAGE)

    def autosearch_ingkey (self):
        """Automatically do a search for our current ingkey.

        We're pretty smart about this: in other words, we won't do a
        search that doesn't have results.
        """
        txt = self.ingkey
        words = re.split('\W+',txt)
        search_terms = []
        search_in = self.rd.nview
        for w in words:
            if w in [',',' ',';','.']: continue
            result = self.rd.search(search_in,'desc',w,use_regexp=False)
            if result:
                search_terms.append(w)
                search_in = result
        self.__override_search__ = True # turn off any handling of text insertion
        search_text = ' '.join(search_terms)
        self.searchEntry.set_text(search_text)
        self.searchvw = search_in
        # Some metakit specific hackery which should not be reproduced...
        try:
            tbl = self.rd.normalizations['foodgroup']
            PACKAGED_FOOD_IDS = []
            for n in self.PACKAGED_FOODS:
                id = tbl.find(foodgroup=n)
                if id >= 0:
                    PACKAGED_FOOD_IDS.append(tbl[id].id)
                if self.searchvw:
                    try:
                        filteredvw = self.rd.filter(self.searchvw,
                                                                lambda r: r.foodgroup not in PACKAGED_FOOD_IDS)
                    except:
                        print 'What was wrong with filtering this?'
                        print 'searchvw=',self.searchvw
                        raise
            if filteredvw:
                self.searchvw = filteredvw
        except NotImplementedError:
            print "No metakit present, so I'm not doing any funky filtering."
            pass
        
        self.nutrition_store.change_view(self.searchvw)
        self.__last_search__ = search_text
        self.__override_search__ = False # turn back on search handling!

    # callbacks for quick-changes
    def apply_ingkey (self,*args):
        key = self.ingKeyEntry.get_text()
        ings = self.nd.db.iview.select(ingkey=self.ingkey)
        self.nd.db.modify_ings(ings,{'ingkey':key})
        self.set_ingkey(key)
        self.autosearch_ingkey()
        self.changeIngKeyAction.dehighlight_action()
        if self.nd.get_nutinfo(key):
            self.setup_to_units()
            self.check_next_amount()
    
    def save_unit_cb (self,*args):
        from_unit = self.fromUnitComboBoxEntry.get_children()[0].get_text()
        ings = self.nd.db.iview.select(ingkey=self.ingkey,unit=self.fromUnit)
        self.nd.db.modify_ings(ings,{'unit':from_unit})
        self.set_from_unit(self.fromUnitComboBoxEntry.get_children()[0].get_text())
        self.changeUnitAction.dehighlight_action()
        
    # Callbacks to handle our druid-like walking-through of actions.

    def add_ingredients (self, inglist):
        """Add a list of ingredients for our druid to guide the user through.

        Our ingredient list is in the following form for, believe it
        or not, good reason:

        [(ingkey, [(amount,unit),(amount,unit),(amount,unit)]),
         (ingkey, [(amount,unit),(amount,unit),(amount,unit)]),
         ...
         ]

        The ingkey is a string, of course.
        amount can be a float or None
        unit can be a string or None

        For each item in the list, we will ask the user to select a
        USDA equivalent.

        Once we've done that, we'll check if the user needs to convert
        the unit as well.
        """
        # to start, we take our first ing
        self.inglist = inglist
        self.ing_index = 0
        self.setup_next_ing()

    def setup_next_ing (self):
        if self.ing_index >= len(self.inglist):
            self.finish()
            return
        ing = self.inglist[self.ing_index]
        self.ing_index+=1    
        if not ing:
            return
        ingkey,amounts = ing
        self.amounts = amounts
        self.amount_index = 0
        self.set_ingkey(ingkey)
        if not self.nd.get_nutinfo(ingkey):
            self.autosearch_ingkey()
            self.goto_page_key_to_nut()
        else:
            self.setup_to_units()
            self.check_next_amount()
        #self.from_unit = unit
        #self.from_amount = amount

    def check_next_amount (self):
        """Check the next amount on our amounts list.

        If the amount is already convertible, we don't do anything.
        If the amount is not convertible, we ask our user for help!
        """
        if self.amount_index >= len(self.amounts):
            self.setup_next_ing()
            return
        amount,unit = self.amounts[self.amount_index]
        if not amount: amount=1
        self.amount = amount
        self.amount_index += 1
        existing_conversion = self.nd.get_conversion_for_amt(amount,unit,self.ingkey)
        if existing_conversion:
            self.check_next_amount()
        else:
            self.set_from_unit(unit)
            self.fromAmountEntry.set_text(convert.float_to_frac(amount,
                                                                fractions=convert.FRACTIONS_ASCII)
                                          )
            self.toAmountEntry.set_text(convert.float_to_frac(amount,
                                                              fractions=convert.FRACTIONS_ASCII)
                                        )
            self.goto_page_unit_convert()

    def finish (self):
        self.glade.get_widget('window1').hide()
        self.emit('finish')

    def goto_page_key_to_nut (self):
        self.notebook.set_current_page(self.NUT_PAGE)

    def goto_page_unit_convert(self):
        self.notebook.set_current_page(self.UNIT_PAGE)

    def goto_page_custom (self):
        self.notebook.set_current_page(self.CUSTOM_PAGE)

    def apply_custom (self, *args):
        nutinfo = self.nutrition_info.copy()
        for k,v in nutinfo.items():
            if type(v)==int or type(v)==float: nutinfo[k]=v*self.custom_factor
        print 'committed',nutinfo
        ndbno = self.nd.add_custom_nutrition_info(self.nutrition_info)

    def apply_nut_equivalent (self,*args):
        if len(self.searchvw)==1:
            nut = self.searchvw[0].ndbno
        else:
            mod,itr = self.treeview.get_selection().get_selected()
            nut = mod.get_value(itr,0)
        self.nd.set_key_from_ndbno(self.ingkey,nut)
        self.setup_to_units()
        # Now see if we need to do any conversion or not

    def apply_amt_convert (self,*args):
        to_unit = cb.cb_get_active_text(self.toUnitCombo)
        base_convert = self.nd.conv.converter('g.',to_unit)
        if not base_convert:
            if self.extra_units.has_key(to_unit):
                base_convert = 1/self.extra_units[to_unit]
            else:
                # this is a density, we hope...
                if to_unit.find(' (')>0:
                    to_unit,describer = to_unit.split(' (')
                    describer = describer[0:-1]
                    density = self.densities[describer]
                else:
                    density = self.densities[None]
                base_convert = self.nd.conv.converter('g.',to_unit,density=density)
        to_amount = convert.frac_to_float(self.toAmountEntry.get_text())
        from_amount = convert.frac_to_float(self.fromAmountEntry.get_text())
        ratio = from_amount / to_amount
        factor = base_convert * ratio
        from_unit = self.fromUnit
        self.nd.set_conversion(self.ingkey,from_unit,factor)
    
    def previous_page_cb (self, *args):
        #self.notebook.set_current_page(self.notebook.get_current_page()-1)
        indx = self.curpage - 1
        typ,ingkey,amount_index = self.path[indx]
        if ingkey!=self.ingkey:
            self.ing_index -= 2
            self.setup_next_ing()
            if typ==self.UNIT_PAGE:
                self.amount_index = amount_index - 1
                self.check_next_amount()
        elif typ==self.UNIT_PAGE:
            self.amount_index = amount_index - 1
            self.check_next_amount()
        else:
            self.ing_index -= 1
            self.setup_next_ing()
        self.curpage = indx
        if self.curpage == 0:
            self.backButton.set_sensitive(False)

    def apply_cb (self, *args):
        page = self.notebook.get_current_page()
        if page == self.NUT_PAGE:
            self.apply_nut_equivalent()
            self.check_next_amount()
        elif page == self.UNIT_PAGE:
            self.apply_amt_convert()
            # if out of amounts, this will move to the next ingredient
            self.check_next_amount()
        elif page == self.CUSTOM_PAGE:
            if not self.custom_factor:
                de.show_message(_("To apply nutritional information, Gourmet needs a valid amount and unit."))
                return
            self.apply_custom()
            self.check_next_amount()
        self.path.append((page,self.ingkey,self.amount_index))
        self.curpage += 1
        #self.notebook.set_current_page(page + 1)
        self.backButton.set_sensitive(True)

    def ignore_cb (self, *args):
        page = self.notebook.get_current_page()
        self.path.append((page,self.ingkey,self.amount_index))
        self.curpage += 1
        self.backButton.set_sensitive(True)
        if page == self.NUT_PAGE:
            self.setup_next_ing()
        else:
            self.check_next_amount()

    def custom_cb (self, *args): self.goto_page_custom()

    def usda_cb (self, *args): self.goto_page_key_to_nut()
        
    def show (self):
        self.glade.get_widget('window1').show()

    #def notebook_page_changed_cb (self, *args):
    #    if self.notebook.get_current_page()==0: self.prevDruidButton.set_sensitive(False)
    
class PageableNutritionStore (PageableViewStore):
    def __init__ (self, view, columns=['ndbno','desc',],column_types=[int,str]):
        PageableViewStore.__init__(self,view,columns,column_types)
    
                   
if __name__ == '__main__':
    import nutrition
    from gourmet.recipeManager import RecipeManager,dbargs
    dbargs['file']='/tmp/foo/recipes.mk'
    rd=RecipeManager(**dbargs)
    import nutritionGrabberGui
    try:
        nutritionGrabberGui.check_for_db(rd)
    except nutritionGrabberGui.Terminated:
        pass
    rd.save()
    import gourmet.convert
    c=gourmet.convert.converter()
    nd=nutrition.NutritionData(rd,c)
    nid = NutritionInfoDruid(nd,{})
    #nid.set_ingkey('black pepper')
    #nid.autosearch_ingkey()
    #nid.set_from_unit('tsp.')
    nid.add_ingredients([('black pepper',[(1,'tsp.'),(2,'pinch')]),
                         ('tomato',[(1,''),(2,'cups'),(0.5,'lb.')]),
                         ('kiwi',[(1,''),(0.5,'c.')]),])
                         
    def quit (*args):
        rd.save()
        nid.glade.get_widget('window1').hide()
        gtk.main_quit()
    nid.glade.get_widget('window1').connect('delete-event',quit)
    nid.connect('finish',quit)
    gtk.main()
