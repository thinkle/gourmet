import os
import os.path
import re
from pkgutil import get_data

from gi.repository import GObject, Gtk

import gourmet.convert as convert
import gourmet.gglobals as gglobals
import gourmet.gtk_extras.cb_extras as cb
import gourmet.gtk_extras.dialog_extras as de
import gourmet.gtk_extras.WidgetSaver as WidgetSaver
from gourmet.defaults import lang as defaults
from gourmet.gtk_extras.mnemonic_manager import MnemonicManager
from gourmet.gtk_extras.pageable_store import PageableViewStore
from gourmet.gtk_extras.validation import NumberEntry
from gourmet.i18n import _

from .nutritionInfoEditor import MockObject, NutritionInfoIndex
from .nutritionLabel import NUT_LAYOUT, RECOMMENDED_INTAKE, SEP

try:
    current_path = os.path.split(os.path.join(os.getcwd(),__file__))[0]
except:
    current_path = ''

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
        if self.initially_hidden is True:
            for w in self.highlight_widgets:
                w.hide()
        if isinstance(self.initially_hidden, list):
            for w in self.initially_hidden:
                w.hide()
        for c in self.hide_on_highlight:
            c.show()

class NutritionUSDAIndex:

    '''This class handles the view for searching the USDA database.
    '''

    __last_group__ = None
    group = None

    PACKAGED_FOODS = ['Soups, Sauces, and Gravies',
                      'Baked Products',
                      'Meals, Entrees, and Sidedishes',
                      'Fast Foods',
                      'Baby Foods']

    ALL_GROUPS = _('Any food group')

    def __init__ (self, rd, prefs, widgets):
        self.rd = rd; self.prefs = prefs
        for name,w in widgets: setattr(self,name,w)
        self._setup_nuttree_()
        self.__last_search__ = ''
        self.__override_search__ = False
        # TODO: Fixing saving usdaSearchAsYouTypeToggle state
        # Button state is not being saved across sessions and always starts off
        # inactive. Of note, this problem seemed to also exist in the last
        # release (0.17.4), but the button always started off active.
        WidgetSaver.WidgetSaver(
            self.usdaSearchAsYouTypeToggle,
            self.prefs.get('sautTog',
                           {'active':True}),
            ['toggled'])
        # Ensure usdaFindButton is shown if usdaSearchAsYouTypeToggle is
        # inactive
        self.toggle_saut()
        # search
        self.usdaSearchEntry.connect('changed',self.search_type_cb)
        self.usdaFindButton.connect('clicked',self.search_cb)
        self.usdaSearchAsYouTypeToggle.connect('toggled',self.toggle_saut)
        cb.set_model_from_list(self.foodGroupComboBox,
                               [self.ALL_GROUPS]+self.rd.get_unique_values('foodgroup',self.rd.nutrition_table)
                               )
        cb.cb_set_active_text(self.foodGroupComboBox,self.ALL_GROUPS)

    def set_search (self, txt):
        """Set the search to txt, ensuring there are results.

        If there are no results for the search, we'll try a partial
        search for only some of the words in txt. If that fails, we'll
        set the search to blank.
        """
        words = re.split(r'\W+',txt)
        # always search raw if possible... (it gets us the real thing
        # vs. canned/frozen/soup/babyfood, etc.)
        if 'raw' not in words:
            words += ['raw']
        search_terms = []
        search_in = self.rd.nutrition_table
        srch = []
        searchvw = None
        for w in words:
            if w in [',',' ',';','.']: continue
            result = self.rd.search_nutrition(srch+[w])
            if result:
                srch += [w]
                searchvw = result
        groups = self.rd.fetch_food_groups_for_search(srch)
        cur_active = cb.cb_get_active_text(self.foodGroupComboBox)
        groups = [self.ALL_GROUPS] + groups
        cb.set_model_from_list(self.foodGroupComboBox,groups)
        cb.cb_set_active_text(self.foodGroupComboBox,cur_active)
        self.__override_search__ = True # turn off any handling of text insertion
        search_text = ' '.join(srch)
        self.usdaSearchEntry.set_text(search_text)
        self.searchvw = searchvw or self.rd.fetch_all(self.rd.nutrition_table)
        self.nutrition_store.change_view(self.searchvw)
        self.__last_search__ = search_text
        self.__override_search__ = False # turn back on search handling!

    def get_selected_usda_item (self):
        if len(self.searchvw)==1:
            nut = self.searchvw[0].ndbno
        else:
            mod,itr = self.usdaTreeview.get_selection().get_selected()
            nut = mod.get_value(itr,0)
        return nut

    def _setup_nuttree_ (self):
        """Set up our treeview with USDA nutritional equivalents"""
        self.nutrition_store = PageableNutritionStore(self.rd.fetch_all(self.rd.nutrition_table))
        self.usdaFirstButton.connect('clicked', lambda *args: self.nutrition_store.goto_first_page())
        self.usdaLastButton.connect('clicked', lambda *args: self.nutrition_store.goto_last_page())
        self.usdaForwardButton.connect('clicked', lambda *args: self.nutrition_store.next_page())
        self.usdaBackButton.connect('clicked', lambda *args: self.nutrition_store.prev_page())
        self.nutrition_store.connect('page-changed',self.update_nuttree_showing)
        self.nutrition_store.connect('view-changed',self.update_nuttree_showing)
        self.update_nuttree_showing()
        self.searchvw = self.rd.nutrition_table
        self.usdaTreeview.set_model(self.nutrition_store)
        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn('Item',renderer,text=1)
        self.usdaTreeview.append_column(col)

    def update_nuttree_showing (self,*args):
        self.usdaShowingLabel.set_text('Showing results %s to %s of %s'%self.nutrition_store.showing())
        # update buttons too
        cp = self.nutrition_store.page
        lp = self.nutrition_store.get_last_page()
        if cp == 0:
            self.usdaFirstButton.set_sensitive(False)
            self.usdaBackButton.set_sensitive(False)
        else:
            self.usdaFirstButton.set_sensitive(True)
            self.usdaBackButton.set_sensitive(True)
        if cp == lp:
            self.usdaLastButton.set_sensitive(False)
            self.usdaForwardButton.set_sensitive(False)
        else:
            self.usdaLastButton.set_sensitive(True)
            self.usdaForwardButton.set_sensitive(True)

    # search callbacks &c.
    def toggle_saut (self, *args):
        if self.usdaSearchAsYouTypeToggle.get_active():
            self.usdaFindButton.hide()
        else:
            self.usdaFindButton.show()

    def search_type_cb (self, *args):
        if self.usdaSearchAsYouTypeToggle.get_active(): self.search_cb()

    def search_cb (self, *args):
        if self.__override_search__: return
        GObject.idle_add(self.search)

    def search (self):
        txt = self.usdaSearchEntry.get_text()
        if self.__last_search__ == txt and self.group == self.__last_group__:
            return
        words = re.split(r'\W+',txt)
        groups = self.rd.fetch_food_groups_for_search(words)
        cur_active = cb.cb_get_active_text(self.foodGroupComboBox)
        groups = [self.ALL_GROUPS] + groups
        if cur_active not in groups:
            groups += [cur_active]
        cb.set_model_from_list(self.foodGroupComboBox,groups)
        cb.cb_set_active_text(self.foodGroupComboBox,cur_active)
        self.searchvw = self.rd.search_nutrition(words,group=self.group)
        self.__last_search__ = txt
        self.__last_group__ = self.group
        self.nutrition_store.change_view(self.searchvw)
        self.nutrition_store.set_page(0)

    def food_group_filter_changed_cb (self, fgcb):
        food_group = cb.cb_get_active_text(fgcb)
        if food_group==self.ALL_GROUPS:
            self.group = None
        else:
            self.group = food_group
        GObject.idle_add(self.search)

class NutritionInfoDruid (GObject.GObject):

    """A druid (or "wizard") to guide a user through helping Gourmet
    calculate nutritional information for an ingredient.

    This consists in finding a USDA equivalent of the ingredient in
    question and possibly of converting a unit.
    """

    NUT_PAGE = 0
    UNIT_PAGE = 1
    CUSTOM_PAGE = 2
    DENSITY_PAGE = 3
    INFO_PAGE = 4
    INDEX_PAGE = 5

    DEFAULT_AMOUNT = 8
    DEFAULT_UNIT = 'oz.'

    __gsignals__ = {
        # The key callback will return a tuple (old_key,new_key)
        'key-changed':(GObject.SignalFlags.RUN_LAST,GObject.TYPE_PYOBJECT,(GObject.TYPE_PYOBJECT,)),
        # The unit callback will return a tuple ((old_unit,old_key),(new_unit,new_key))
        'unit-changed':(GObject.SignalFlags.RUN_LAST,GObject.TYPE_PYOBJECT,(GObject.TYPE_PYOBJECT,)),
        'finish':(GObject.SignalFlags.RUN_LAST,None,())
        }

    def __init__ (self, nd, prefs, rec=None, in_string=''):
        self.ui = Gtk.Builder()
        self.ui.add_from_string(get_data('gourmet', 'ui/nutritionDruid.ui').decode())
        self.mm = MnemonicManager()
        self.mm.add_builder(self.ui)
        self.mm.fix_conflicts_peacefully()
        self.prefs = prefs
        self.nd = nd
        self.rec = rec
        self.in_string = in_string or (rec and _('recipe') or _('selection'))
        self.rd = self.nd.db
        self.def_ingredient_amounts = {} # For default amounts for nutritional label...
        self.amounts = {} # List amounts by ingredient
        self.ing_to_index = {} # A way to keep track of the order of our ingredients...
        self._setup_widgets_()
        # keep track of pages/setups we've been on
        self.path = []
        self.curpage = 0
        self.prevDruidButton.set_sensitive(False)
        # Initiate our gobject-ness so we can emit signals.
        GObject.GObject.__init__(self)
        # Save our position with our widget saver...
        WidgetSaver.WindowSaver(self.ui.get_object('window'),
                                self.prefs.get('nutritionDruid',{})
                                )


    def _setup_widgets_ (self):
        self.controls = []
        self.widgets =  ['notebook',
                         # ingKey Changing Stuff
                         'ingKeyLabel','ingKeyEntry','changeKeyButton','applyKeyButton',
                         'ingKeyLabel2',
                         # Search stuff
                         'usdaSearchEntry','usdaSearchAsYouTypeToggle','usdaFindButton',
                         'usdaFirstButton','usdaBackButton','usdaForwardButton',
                         'usdaLastButton','usdaShowingLabel',
                         'usdaTreeview','foodGroupComboBox',
                         'customBox','customButton',
                         # Unit adjusting stuff
                         'convertUnitLabel','fromUnitComboBoxEntry','fromUnitLabel',
                         'changeUnitButton','cancelUnitButton','saveUnitButton',
                         'fromAmountEntry','toUnitCombo','toAmountEntry',
                         # Wizard buttons
                         'prevDruidButton','ignoreButton','applyButton',
                         # Custom nutritional information screen
                         'massUnitComboBox','customNutritionAmountEntry',
                         # Density-Choosing page
                         'densityLabel','densityBox',
                         # Index page...
                         'editButton',
                         # INFO PAGE
                         'infoIngredientKeyLabel','infoUSDALabel','nutritionLabelBox',
                         'infoDensityLabel','infoOtherEquivalentsLabel',
                         'infoCustomEquivalentsTable',
                         ]
        for widget_name in self.widgets:
            setattr(self,widget_name,self.ui.get_object(widget_name))
            if not getattr(self,widget_name): print("WIDGET: ",widget_name,"NOT FOUND.")
            # make a list of all core control widgets
            if widget_name!='notebook': self.controls.append(getattr(self,widget_name))
        self.usdaIndex = NutritionUSDAIndex(self.rd,
                                            prefs=self.prefs,
                                            widgets=[(w,getattr(self,w)) for w in self.widgets])
        self.ui.connect_signals(
            {'previousPage':self.previous_page_cb,
             'applyPage':self.apply_cb,
             'ignorePage':self.ignore_cb,
             'customPage':self.custom_cb,
             'usdaPage':self.usda_cb,
             'close':self.close,
             'on_foodGroupComboBox_changed':self.usdaIndex.food_group_filter_changed_cb,
             'edit':self.view_nutritional_info,
             'infoEditUSDAAssociation':self.info_edit_usda_association,
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
        # Nutrition box...
        self.custom_box=self.ui.get_object('customBox')
        self.customNutritionAmountEntry.connect('changed',self.custom_unit_changed)
        self.massUnitComboBox.connect('changed',self.custom_unit_changed)
        self._setup_custom_box()

    ### BEGIN METHODS FOR NUTRITIONAL INFORMATION INDEX

    def setup_nutrition_index (self):
        if not hasattr(self,'full_inglist'):
            self.add_ingredients([])
        if not hasattr(self,'nutInfoIndex'):
            self.nutInfoIndex = NutritionInfoIndex(
                self.rd, prefs=self.prefs, ui=self.ui,
                ingredients=self.full_inglist,
                in_string=self.in_string,
                )
        self.path.append((self.goto_page_index,[]))
        self.goto_page_index()

    ### END METHODS FOR NUTRITIONAL INFORMATION INDEX

    ### BEGIN METHODS FOR DISPLAYING CURRENT NUTRITIONAL INFO
    def view_nutritional_info (self, *args):
        nutalias = self.nutInfoIndex.get_selected_ingredient()
        if nutalias.ndbno == 0:
            # Then this is not really an item... we better edit it!
            self.add_ingredients(
                [(
                nutalias.ingkey,
                self.get_amounts_and_units_for_ingkey(nutalias.ingkey)
                  )]
                )
        else:
            self.show_info_page(nutalias)
            self.path.append(
                (self.show_info_page,[nutalias])
                )

    def show_info_page (self, nutalias):
        self.infoIngredientKeyLabel.set_text(nutalias.ingkey)
        self.infoUSDALabel.set_text(nutalias.desc)
        self.goto_page_info()
        self.prevDruidButton.set_sensitive(True)
        self.set_nutritional_label(nutalias)
        self.set_density_info(nutalias)
        self.info_nutalias = nutalias

    def set_density_info (self, nutalias):
        densities,extra_units = self.nd.get_conversions(nutalias.ingkey)
        density_texts = []
        for k,v in list(densities.items()):
            if not k:
                density_texts = ['%.2f'%v] + density_texts
            else:
                density_texts.append('%s: %.2f'%(k,v))
        self.infoDensityLabel.set_text('\n'.join(density_texts) or 'None')
        eutexts = ['%s: %s g'%(k,v) for k,v in list(extra_units.items()) ]
        eutexts.sort()
        extra_units_text = '\n'.join(eutexts)
        self.infoOtherEquivalentsLabel.set_text(
            extra_units_text or 'None'
            )
        others = self.rd.fetch_all(self.rd.nutritionconversions_table,ingkey=nutalias.ingkey)
        other_label = '\n'.join(['%s: %.1f g'%(
            conv.unit or '100 %s'%_('ml'),1.0/conv.factor
            ) for conv in others])
        if others:
            self.populate_custom_equivalents_table(others)
        else:
            self.infoCustomEquivalentsTable.hide()

    def populate_custom_equivalents_table (self, equivalents):
        # Remove previous children...
        for c in self.infoCustomEquivalentsTable.get_children():
            self.infoCustomEquivalentsTable.remove(c); c.unparent()
        for n,eq in enumerate(equivalents):
            lab = Gtk.Label("%s: %.1f g"%(
                eq.unit or 'No unit', 1.0/eq.factor)
                            )
            rembut = Gtk.Button('C_hange'); rembut.set_use_underline(True)
            rembut.connect('clicked',
                           self.info_edit_equivalent,
                           eq)
            self.infoCustomEquivalentsTable.attach(lab,
                                                   0,1,n,n+1)
            self.infoCustomEquivalentsTable.attach(rembut,
                                                   1,2,n,n+1)
        self.infoCustomEquivalentsTable.show_all()

    def set_nutritional_label (self, nutalias):
        if not hasattr(self,'nutritionLabel'):
            from .nutritionLabel import NutritionLabel
            self.nutritionAmountLabel = Gtk.Label()
            self.nutritionLabel = NutritionLabel(self.prefs, custom_label=' ')
            self.nutritionLabelBox.pack_start(self.nutritionAmountLabel,
                                              fill=0,
                                              expand=0)
            self.nutritionLabelBox.pack_start(self.nutritionLabel,
                                              fill=0,
                                              expand=0,
                                              )
            self.nutritionAmountLabel.set_alignment(0.0,0.0)
            self.nutritionAmountLabel.show()
            self.nutritionLabel.show()
        amount,unit = self.def_ingredient_amounts.get(nutalias.ingkey,
                                                  (self.DEFAULT_AMOUNT,
                                                   self.DEFAULT_UNIT)
                                                  )
        nutinfo = self.nd.get_nutinfo_for_inglist([
            MockObject(amount=amount,
                       unit=unit,
                       ingkey=nutalias.ingkey)
            ],
                                                  self.rd
                                                  )
        if nutinfo._get_vapor():
            amount = self.DEFAULT_AMOUNT; unit = self.DEFAULT_UNIT
            nutinfo = self.nd.get_nutinfo_for_inglist([
            MockObject(amount=amount,
                       unit=unit,
                       ingkey=nutalias.ingkey)
            ],
                                                      self.rd
                                                      )

        self.nutritionLabel.set_nutinfo(
            nutinfo
            )
        self.nutritionAmountLabel.set_markup(
            '<i>Nutritional information for %(amount)s %(unit)s</i>'%{
            'amount':amount,
            'unit':unit,
            })

    def get_amounts_and_units_for_ingkey (self, ingkey):
        """Return a list of amounts and units present in database for ingkey"""
        amounts_and_units = []
        ings = self.rd.fetch_all(self.rd.ingredients_table,ingkey=ingkey)
        for i in ings:
            a,u = i.amount,i.unit
            if (a,u) not in amounts_and_units:
                amounts_and_units.append((a,u))
        return amounts_and_units

    # start nutritional-info callbacks
    def info_edit_usda_association (self, *args):
        """Edit the USDA association for the item on the information page."""
        self.edit_nutinfo(ingkey=self.info_nutalias.ingkey,
                          desc=self.info_nutalias.desc)
        self.path.append(
            (self.edit_nutinfo,
             [self.info_nutalias.ingkey,
              self.info_nutalias.desc])
            )

    def info_edit_equivalent (self, button, eq):
        """Edit equivalents callback. eq is a nutalias DB object.
        """
        self.amounts[self.ingkey] = {}
        self.amount = 1
        self.ingkey = self.info_nutalias.ingkey
        self.set_from_unit(eq.unit)
        self.fromAmountEntry.set_text('1')
        conv = self.nd.get_conversion_for_amt(1,eq.unit,self.info_nutalias.ingkey)
        amt_in_grams = conv * 100
        self.setup_to_units()
        to_unit = cb.cb_set_active_text(self.toUnitCombo,'g')
        self.toAmountEntry.set_text(convert.float_to_frac(amt_in_grams,
                                                          fractions=convert.FRACTIONS_ASCII
                                                          ))

        # Hack to avoid adding ourselves to the path on a "back" event
        # -- if button is None, then we know we were called
        # artificially from previous_page_cb (not from a button press
        # event)
        if button:
            self.path.append(
                (self.info_edit_equivalent,
                 [None,eq])
                )
        self.goto_page_unit_convert()

    # end nutritional-info callbacks

    ### END METHODS FOR DISPLAYING CURRENT NUTRITIONAL INFO

    ### BEGIN  METHODS FOR CUSTOM NUTRITIONAL INTERFACE
    def _setup_custom_box (self):
        """Setup the interface for entering custom nutritional information.
        """
        t = Gtk.Table()
        masses = [i[0] for i in defaults.UNIT_GROUPS['metric mass']\
                  + defaults.UNIT_GROUPS['imperial weight']]
        cb.set_model_from_list(
            self.massUnitComboBox,
            masses)
        cb.cb_set_active_text(self.massUnitComboBox,'g')
        self.customNutritionAmountEntry.set_value(100)
        self.nutrition_info = {}
        self.custom_box.add(t)
        self.changing_percent_internally = False
        self.changing_number_internally = False
        l=Gtk.Label(label='%RDA'); l.show()
        t.attach(l,2,3,0,1)
        for n,nutstuff in enumerate(NUT_LAYOUT):
            if nutstuff == SEP:
                hs = Gtk.HSeparator()
                t.attach(hs,0,2,n+1,n+2,xoptions=Gtk.AttachOptions.FILL)
                hs.show()
                continue
            label_txt,typ,name,properties,show_percent,unit = nutstuff
            if unit: label_txt += " (" + unit + ")"
            label = Gtk.Label(label=label_txt); label.show()
            label.set_alignment(0,0.5)
            t.attach(label,0,1,n+1,n+2,xoptions=Gtk.AttachOptions.FILL)
            entry = NumberEntry(default_to_fractions=False)
            entry.show()
            t.attach(entry,1,2,n+1,n+2,xoptions=Gtk.AttachOptions.FILL)
            if show_percent:
                percent_entry = NumberEntry(default_to_fractions=False,
                                            decimals=0)
                percent_entry.entry.set_width_chars(4)
                percent_entry.show()
                percent_label = Gtk.Label(label='%'); percent_label.show()
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
            base_convert = self.nd.conv.converter(unit,'g')/float(100)
            self.custom_factor = 1/(base_convert * amount)

    def apply_custom (self, *args):
        nutinfo = self.nutrition_info.copy()
        for k,v in list(nutinfo.items()):
            if isinstance(v, (int, float)):
                nutinfo[k] = v*self.custom_factor
            # Special case fat, which is listed as one item but is in
            # fact a combination of 3. We'll have to fudge the info
            # about mono- v. poly- unsaturated fats.
            if k=='fat':
                totfat = v * self.custom_factor
                unsatfat = totfat - nutinfo.get('fasat',0)
                del nutinfo['fat']
                nutinfo['fapoly']=unsatfat # Fudge
        nutinfo['desc']=self.ingkey
        ndbno = self.nd.add_custom_nutrition_info(nutinfo)

    ### END METHODS FOR CUSTOM NUTRITIONAL INTERFACE

    ### METHODS TO SET CURRENT ITEM AND UNIT INFO
    def set_ingkey (self, txt):
        self.ingKeyEntry.set_text(txt)
        self.ingKeyLabel.set_markup('<i><b>'+txt+'</b></i>') # USDA Page
        self.ingKeyLabel2.set_markup('<i><b>'+txt+'</b></i>') # Custom Page
        self.nutrition_info['desc']=txt
        self.ingkey = txt

    ### BEGIN METHODS FOR SETTING UNIT EQUIVALENTS

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
        self.convertUnitLabel.set_markup(
            '<span weight="bold" size="larger">' + \
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
        self.densities,self.extra_units = self.nd.get_conversions(self.ingkey)
        for d in list(self.densities.keys()):
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

    def apply_amt_convert (self,*args):
        to_unit = cb.cb_get_active_text(self.toUnitCombo)
        base_convert = self.nd.conv.converter('g',to_unit)
        if not base_convert:
            self.densities,self.extra_units = self.nd.get_conversions(self.ingkey)
            if to_unit in self.extra_units:
                base_convert = 1/self.extra_units[to_unit]
            else:
                # this is a density, we hope...
                if to_unit.find(' (')>0:
                    to_unit,describer = to_unit.split(' (')
                    describer = describer[0:-1]
                    density = self.densities[describer]
                else:
                    if None not in self.densities:
                        raise RuntimeError("Unable to make sense of conversion from %s %s"%(to_unit,self.ingkey))
                    density = self.densities[None]
                base_convert = self.nd.conv.converter('g',to_unit,density=density)
        to_amount = convert.frac_to_float(self.toAmountEntry.get_text())
        from_amount = convert.frac_to_float(self.fromAmountEntry.get_text())
        ratio = from_amount / to_amount
        factor = base_convert * ratio
        from_unit = self.fromUnit
        self.nd.set_conversion(self.ingkey,from_unit,factor)

    ### END METHODS FOR SETTING UNIT EQUIVALENTS

    ### BEGIN METHODS FOR SEARCHING USDA INDEX

    def autosearch_ingkey (self):
        """Automatically do a search for our current ingkey.

        We're pretty smart about this: in other words, we won't do a
        search that doesn't have results.
        """
        self.usdaIndex.set_search(self.ingkey)

    def apply_nut_equivalent (self,*args):
        nut = self.usdaIndex.get_selected_usda_item()
        self.nd.set_key_from_ndbno(self.ingkey,nut)
        # Now see if we need to do any conversion or not
        self.setup_to_units()

    ### END METHODS FOR SEARCHING USDA INDEX

    ### BEGIN CALLBACKS FOR QUICK-CHANGES OF INGREDIENT KEY / UNIT

    def apply_ingkey (self,*args):
        key = self.ingKeyEntry.get_text()
        if key==self.ingkey:
            self.changeIngKeyAction.dehighlight_action()
            return
        #ings = self.rd.fetch_all(self.rd.ingredients_table,ingkey=self.ingkey)
        #self.rd.modify_ings(ings,{'ingkey':key})
        if self.rec:
            try:
                user_says_yes = de.getBoolean(
                    label=_('Change ingredient key'),
                    sublabel=_(
                    'Change ingredient key from %(old_key)s to %(new_key)s everywhere or just in the recipe %(title)s?'
                    )%{'old_key':self.ingkey,
                       'new_key':key,
                       'title':self.rec.title
                       },
                    custom_no=_('Change _everywhere'),
                    custom_yes=_('_Just in recipe %s')%self.rec.title
                    )
            except de.UserCancelledError:
                self.changeIngKeyAction.dehighlight_action()
                return
        else:
            if not de.getBoolean(label=_('Change ingredient key'),
                                 sublabel=_('Change ingredient key from %(old_key)s to %(new_key)s everywhere?'
                                            )%{'old_key':self.ingkey,
                                               'new_key':key,
                                               },
                                 cancel=False,
                                 ):
                self.changeIngKeyAction.dehighlight_action()
                return
        if self.rec and user_says_yes:
            self.rd.update_by_criteria(self.rd.ingredients_table,
                           {'ingkey':self.ingkey,
                            'recipe_id':self.rec.id},
                           {'ingkey':key}
                           )
        else:
            self.rd.update_by_criteria(self.rd.ingredients_table,
                          {'ingkey':self.ingkey},
                          {'ingkey':key}
                          )
        old_key = self.ingkey
        self.set_ingkey(key)
        # Update amounts dictionary...
        self.amounts[key] = self.amounts[old_key]
        del self.amounts[old_key]
        self.autosearch_ingkey()
        self.changeIngKeyAction.dehighlight_action()
        if self.nd.get_nutinfo(key):
            self.setup_to_units()
            self.check_next_amount()
        self.emit('key-changed',(old_key,key))

    def save_unit_cb (self,*args):
        from_unit = self.fromUnitComboBoxEntry.get_children()[0].get_text()
        old_from_unit = self.fromUnit
        #ings = self.rd.fetch_all(self.rd.ingredients_table,ingkey=self.ingkey,unit=old_from_unit)
        #self.rd.modify_ings(ings,{'unit':from_unit})
        if self.rec and de.getBoolean(
            label=_('Change unit'),
            sublabel=_(
            'Change unit from %(old_unit)s to %(new_unit)s for all ingredients %(ingkey)s or just in the recipe %(title)s?'
            )%{'old_unit':old_from_unit,
               'new_unit':from_unit,
               'ingkey':self.ingkey,
               'title':self.rec.title
               },
            custom_no=_('Change _everywhere'),
            custom_yes=_('_Just in recipe %s')%self.rec.title
            ):
            self.rd.update_by_criteria(self.rd.ingredients_table,
                           {'ingkey':self.ingkey,
                            'unit':old_from_unit,
                            'recipe_id':self.rec.id},
                           {'unit':from_unit}
                           )
        else:
            self.rd.update_by_criteria(self.rd.ingredients_table,
                          {'ingkey':self.ingkey,
                           'unit':old_from_unit},
                          {'unit':from_unit}
                          )
        self.set_from_unit(self.fromUnitComboBoxEntry.get_children()[0].get_text())
        self.changeUnitAction.dehighlight_action()
        self.emit('unit-changed',((old_from_unit,self.ingkey),(from_unit,self.ingkey)))

    ### END CALLBACKS FOR QUICK-CHANGES OF INGREDIENT KEY / UNIT

    ### BEGIN METHODS FOR DENSITY-CHOOSING INTERFACE

    def get_density (self,amount,unit):
        self.densityLabel.set_text(
            _("""In order to calculate nutritional information for "%(amount)s %(unit)s %(ingkey)s", Gourmet needs to know its density. Our nutritional database has several descriptions of this food with different densities. Please select the correct one below.""")%({'amount':amount,'unit':unit,'ingkey':self.ingkey})
            )
        for c in self.densityBox.get_children():
            self.densityBox.remove(c)
            c.unparent()
        group = None
        def density_callback (rb, name):
            self.custom_density = name
        for d in list(self.densities.keys()):
            group = Gtk.RadioButton(group,str(d)+' '+'(%.2f)'%self.densities[d])
            group.connect('toggled',density_callback,d)
            self.densityBox.pack_start(group,expand=False,fill=False)
            group.show()
        group.set_active(True)
        self.custom_density = d
        self.goto_page_density()

    def apply_density (self):
        self.nd.set_density_for_key(
            self.ingkey,
            self.custom_density
            )
        for c in self.densityBox.get_children(): c.hide()

    ### END METHODS FOR DENSITY CHANGING INTERFACE

    ### BEGIN CALLBACKS TO WALK THROUGH INGREDIENTS

    def add_ingredients (self, inglist, full_inglist=[]):
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
        if not full_inglist:
            if self.rec:
                self.full_inglist = []
                for i in self.rd.get_ings(self.rec):
                    self.full_inglist.append(i.ingkey)
                    self.def_ingredient_amounts[i.ingkey] = (i.amount,i.unit)
            else:
                self.full_inglist = []
                for ingkey,amounts_and_units in self.inglist:
                    self.full_inglist.append(ingkey)
                    if amounts_and_units:
                        self.def_ingredient_amounts[ingkey] = amounts_and_units[0]
        self.ing_index = 0
        self.setup_next_ing()

    def setup_next_ing (self):
        """Move to next ingredient."""
        if self.ing_index >= len(self.inglist):
            self.finish()
            return
        ing = self.inglist[self.ing_index]
        self.ing_index+=1
        if not ing:
            return
        ingkey,amounts = ing
        self.ing_to_index[ingkey] = self.ing_index
        self.amounts[ingkey] = amounts
        self.amount_index = 0
        self.set_ingkey(ingkey)
        if not self.nd.get_nutinfo(ingkey):
            self.edit_nutinfo()
            self.path.append((self.edit_nutinfo,[ingkey]))
        else:
            self.setup_to_units()
            self.check_next_amount()

    def edit_nutinfo (self, ingkey=None, desc=None):
        self.amounts[ingkey or desc] = self.get_amounts_and_units_for_ingkey(ingkey)
        self.amount_index = 0
        if ingkey:
            self.set_ingkey(ingkey)
        if desc:
            self.usdaIndex.set_search(desc)
        else:
            self.autosearch_ingkey()
        self.goto_page_key_to_nut()
        ing_index = self.ing_to_index.get(ingkey,None)
        if ing_index: self.ing_index = ing_index

    def check_next_amount (self):
        """Check the next amount on our amounts list.

        If the amount is already convertible, we don't do anything.
        If the amount is not convertible, we ask our user for help!
        """
        if self.amount_index >= len(self.amounts[self.ingkey]):
            self.setup_next_ing()
            return
        amount,unit = self.amounts[self.ingkey][self.amount_index]
        if not amount: amount=1
        self.amount = amount
        self.amount_index += 1
        existing_conversion = self.nd.get_conversion_for_amt(amount,unit,self.ingkey,fudge=True)
        existing_conversion_fudged = (existing_conversion
                                      and
                                      (not self.nd.get_conversion_for_amt(amount,unit,self.ingkey,fudge=False)
                                       ))
        if existing_conversion_fudged:
            self.get_density(amount,unit)
        elif existing_conversion:
            self.check_next_amount()
        else:
            self.edit_units(amount, unit, self.ingkey)
            self.path.append((self.edit_units,
                              [amount,unit,self.ingkey,self.amount_index])
                             )

    def edit_units (self, amount, unit, ingkey, indx=None):
        self.set_ingkey(ingkey)
        self.set_from_unit(unit)
        if indx is not None: self.amount_index = indx
        self.fromAmountEntry.set_text(convert.float_to_frac(amount,
                                                            fractions=convert.FRACTIONS_ASCII)
                                      )
        self.toAmountEntry.set_text(convert.float_to_frac(amount,
                                                          fractions=convert.FRACTIONS_ASCII)
                                    )
        self.goto_page_unit_convert()

    def previous_page_cb (self, *args):
        """Move to the previous item in self.path


        PATH ITEMS are in the form:

        (CUSTOM_METHOD,ARGS)

        We'll call CUSTOM_METHOD(ARGS)
        """
        self.path.pop() # pop off current page...
        method,args = self.path[-1]
        if callable(method):
            method(*args)
        else:
            # for convenience, if the method isn't callable, we take
            # it to be a page
            self.notebook.set_current_page(method)
        if len(self.path) <= 1:
            self.prevDruidButton.set_sensitive(False)
        return

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
        elif page == self.DENSITY_PAGE:
            self.apply_density()
            self.check_next_amount()
        self.curpage += 1
        self.prevDruidButton.set_sensitive(True)

    def ignore_cb (self, *args):
        page = self.notebook.get_current_page()
        self.curpage += 1
        self.prevDruidButton.set_sensitive(True)
        if page == self.NUT_PAGE:
            self.setup_next_ing()
        else:
            self.check_next_amount()

    ### END CALLBACKS TO WALK THROUGH INGREDIENTS

    ### BEGIN CONVENIENCE METHODS FOR SWITCHING PAGES
    def goto_page_key_to_nut (self):
        for b in [self.applyButton,self.ignoreButton]: b.show()
        for b in [self.editButton]: b.hide()
        self.notebook.set_current_page(self.NUT_PAGE)

    def goto_page_unit_convert(self):
        for b in [self.applyButton,self.ignoreButton]: b.show()
        for b in [self.editButton]: b.hide()
        self.notebook.set_current_page(self.UNIT_PAGE)

    def goto_page_custom (self):
        for b in [self.applyButton,self.ignoreButton]: b.show()
        for b in [self.editButton]: b.hide()
        self.notebook.set_current_page(self.CUSTOM_PAGE)

    def goto_page_density (self):
        for b in [self.applyButton,self.ignoreButton]: b.show()
        for b in [self.editButton]: b.hide()
        self.notebook.set_current_page(self.DENSITY_PAGE)

    def goto_page_index (self):
        for b in [self.editButton]: b.show()
        for b in [self.applyButton,self.ignoreButton]: b.hide()
        self.notebook.set_current_page(self.INDEX_PAGE)

    def goto_page_info (self):
        for b in [self.editButton,self.applyButton,self.ignoreButton]: b.hide()
        self.notebook.set_current_page(self.INFO_PAGE)

    ### END CONVENIENCE METHODS FOR SWITCHING PAGES

    def custom_cb (self, *args): self.goto_page_custom()

    def usda_cb (self, *args): self.goto_page_key_to_nut()

    ### BEGIN METHODS FOR STARTING AND FINISHING

    def show (self):
        self.ui.get_object('window').show()

    def finish (self):
        # When done -- goto nutritional index page...
        if not hasattr(self,'nutInfoIndex'):
            self.setup_nutrition_index()
        else:
            self.nutInfoIndex.reset()
            self.goto_page_index()

    def close (self, *args):
        self.ui.get_object('window').hide()
        self.emit('finish')
        #self.ui.get_object('window').hide()

    ### END METHODS FOR STARTING AND FINISHING

    ### END NutritionInfoDruid

class PageableNutritionStore (PageableViewStore):
    def __init__ (self, view, columns=['ndbno','desc',],column_types=[int,str]):
        PageableViewStore.__init__(self,view,columns,column_types)


if __name__ == '__main__':
    from . import nutrition
    from gourmet.recipeManager import RecipeManager,dbargs
    dbargs['file']='/tmp/boofoo.db'
    rd=RecipeManager(**dbargs)
    rd.add_ing(dict(ingkey='1% milk',
               amount=1.0,
               unit='c.'))
    rd.add_ing(dict(ingkey='1% milk',
               amount=10,
               unit='oz.'))
    rd.add_ing(dict(ingkey='1% milk',
               amount=1,
               unit='splash'))
    from . import nutritionGrabberGui
    try:
        nutritionGrabberGui.check_for_db(rd)
    except nutritionGrabberGui.Terminated:
        pass
    rd.save()
    import gourmet.convert
    c=gourmet.convert.converter()
    nd=nutrition.NutritionData(rd,c)
    nid = NutritionInfoDruid(nd,{})
    def unit_handler (*args):
        print('CHANGE UNIT CALLBACK:',args)
    def key_handler (*args):
        print('CHANGE KEY CALLBACK:',args)
    nid.connect('unit-changed',unit_handler)
    nid.connect('key-changed',key_handler)
    #nid.set_ingkey('black pepper')
    #nid.autosearch_ingkey()
    #nid.set_from_unit('tsp.')
    nid.add_ingredients([
        ('white sugar',[(1,'c.')]),
        ('black pepper',[(1,'tsp.'),(2,'pinch')]),
        ('tomato',[(1,''),(2,'cups'),(0.5,'lb.')]),
        ('kiwi',[(1,''),(0.5,'c.')]),
        ('raw onion',[(1,'c.')]),
        ('sugar, powdered',[(1,'c.')]),
        ('garlic',[(1,'clove')]),
        ('cauliflower',[(1,'head'),(3,'chunks')]),
        ('salt',[(3,'tsp'),]),
        ('1% milk',[(1,'c.')])

        ])

    def quit (*args):
        rd.save()
        nid.ui.get_object('window').hide()
        Gtk.main_quit()
    nid.ui.get_object('window').connect('delete-event',quit)
    nid.connect('finish',quit)
    Gtk.main()
    del rd
    del nid
