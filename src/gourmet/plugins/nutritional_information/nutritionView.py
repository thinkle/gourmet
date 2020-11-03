import re
import string

from gi.repository import GObject, Gtk

import gourmet.cb_extras as cb
import gourmet.convert as convert
import gourmet.dialog_extras as de
import gourmet.gglobals as gglobals
from gourmet.defaults import lang as defaults

from . import parser_data
from .nutritionModel import NutritionModel


class NutritionTable:
    """Handed a table (so we can steal it from glade), we pack it full
    of nutritional information."""
    def __init__ (self, table, prefs, default_editable=True):
        self.prefs = prefs
        self.table = table
        self.fields = prefs.get('nutritionFields',
                                # default nutritional fields
                                ['kcal','protein','carb','fiber',
                                 'calcium','iron','sodium',
                                 'fasat','famono','fapoly','cholestrl'])
        self.mnemonics=[]
        self.cells = {}
        self.pack_table()
        self.set_editable(default_editable)
        self.table.show_all()

    def set_nutrition_object (self, obj, multiply_by=None):
        # we want an object that has nutritionFields as attributes.
        # In our metakit-ish world, that means we really are going to
        # be getting a row of our nutrition database as an object, whose
        # attributes represent fields.
        for attr,widgets in list(self.cells.items()):
            val=getattr(obj,attr)
            # if we're multiplying and this is an attribute that needs to be multiplied...
            if multiply_by and attr in parser_data.PER_100_GRAMS:
                val = val * multiply_by
            for w in widgets: w.set_text("%s"%val)

    def set_editable (self, value):
        if value:
            for widgets in list(self.cells.values()):
                widgets[0].show()
                widgets[1].hide()
        else:
            for widgets in list(self.cells.values()):
                widgets[1].show()
                widgets[0].hide()

    def pack_table (self):
        for n,f in enumerate(self.fields):
            lname = parser_data.NUT_FIELDNAME_DICT[f]
            label = Gtk.Label()
            # we somewhat hackishly attempt to create a mnemonic
            lab = self.create_mnemonic(lname)
            label.set_text_with_mnemonic(lab+":")
            # We might eventually want to make this into SpinButtons, since they
            # are numbers, but I find too many SpinButtons annoying :)
            entr = Gtk.Entry()
            label.set_mnemonic_widget(entr)
            lab2 = Gtk.Label()
            self.cells[f]=(entr,lab2) # so we can get back at this widget
            self.table.attach(label,0,1,n,n+1)
            self.table.attach(entr,1,2,n,n+1)
            self.table.attach(lab2,2,3,n,n+1)

    def create_mnemonic (self, txt):
        """Create a mnemonic for txt, trying not to use the same
        mnemonic twice."""
        for n,char in enumerate(txt):
            if char.strip() and not char in self.mnemonics:
                self.mnemonics.append(char)
                return txt[0:n]+"_"+txt[n:]
        else:
            # if we must, go ahead and use the same mnemonic twice
            return "_" + txt


class NutritionItemView:
    def __init__ (self,
                  nd,
                  usdaChoiceWidget,
                  ingredientWidget,
                  amountWidget,
                  unitChoiceWidget,
                  descChoiceWidget,
                  currentAmountWidget,
                  infoTable,
                  amountLabel=None,
                  unitChoiceLabel=None,
                  descChoiceLabel=None,
                  ):
        self.nd = nd
        self.choices = {}
        self.usdaChoiceWidget=usdaChoiceWidget
        self.ingredientWidget=ingredientWidget
        self.amountWidget = amountWidget
        self.amountLabel = amountLabel
        self.unitChoiceWidget=unitChoiceWidget
        self.descChoiceWidget=descChoiceWidget
        self.currentAmountWidget = currentAmountWidget
        self.unitChoiceLabel=unitChoiceLabel
        self.descChoiceLabel=descChoiceLabel
        #self.ingredientWidget.connect('changed',self.set_ingredient_from_keybox)
        self.usdaChoiceWidget.connect('changed',self.usdaChangedCB)
        self.unitChoiceWidget.connect('changed',self.amountChangedCB)
        self.amountWidget.connect('changed',self.amountChangedCB)
        self.descChoiceWidget.connect('changed',self.amountChangedCB)
        self.infoTable = infoTable
        self.amount=100
        self.unit = 'g.'

    def set_unit_visibility (self, visible):
        if visible:
            self.amountWidget.show()
            self.unitChoiceWidget.show()
            if self.unitChoiceLabel: self.unitChoiceLabel.show()
            if self.amountLabel: self.amountLabel.show()
        else:
            self.unitChoiceWidget.hide()
            self.amountWidget.hide()
            if self.unitChoiceLabel: self.unitChoiceLabel.hide()
            if self.amountLabel: self.amountLabel.hide()
            self.set_desc_visibility(False)

    def set_desc_visibility (self, visible):
        if visible:
            self.descChoiceWidget.show()
            if self.descChoiceLabel: self.descChoiceLabel.show()
        else:
            self.descChoiceWidget.hide()
            if self.descChoiceLabel: self.descChoiceLabel.hide()

    #def set_ingredient_from_keybox (self,*args):
    #    ing = self.ingredientWidget.get_text()
    #    self.set_ingredient(ing)

    def set_nutref (self, nutrow):
        nutchoices = self.choices.get(self.usdaChoiceWidget) or []
        if nutrow.desc in nutchoices:
            self.set_choice(self.usdaChoiceWidget,nutrow.desc)
        else:
            self.setup_chocies([nutrow.desc]+nutchoices, self.usdaChoiceWidget)
            self.set_choice(nutrow.desc)

    def set_ingredient (self, ing):
        """Handed an ingredient object, we set up our other widgets
        to let the user choose nutritional information."""
        self.ingkey=ing
        self.currentAmountWidget.set_text("%s %s"%(self.amount,self.unit))
        self.setup_usda_choices(ing)
        self.setup_unit_boxes(ing)

    def setup_unit_boxes (self, ing=None, nutrow=None):
        self.densities,self.extra_units = self.nd.get_conversions(row=nutrow,key=ing)
        self.setup_choices(list(self.densities.keys()),self.descChoiceWidget)
        units = defaults.WEIGHTS[0:]
        if self.densities: units += defaults.VOLUMES[0:]
        if self.extra_units: units = list(self.extra_units.keys()) + units
        self.setup_choices(units,self.unitChoiceWidget)
        for k in list(self.densities.keys()):
            if k:
                # if we have a key that's not none, then we actually need a descChoiceWidget
                self.setup_choices(list(self.densities.keys()),self.descChoiceWidget)
                if None in self.densities:
                    self.set_choice(self.descChoiceWidget,None)
                else:
                    self.set_choice(self.descChoiceWidget,k)
                self.set_desc_visibility(True)
                return
        # if we didn't find any density choices, then we don't need our description widget
        self.set_desc_visibility(False)
        self.setup_choices(None,self.descChoiceWidget)

    def setup_usda_choices (self, ing):
        self.ingkey=ing
        nutrow = self.nd.get_nutinfo(self.ingkey)
        if nutrow:
            self.choices[self.usdaChoiceWidget]=[nutrow]
            self.setup_choices([nutrow],self.usdaChoiceWidget)
            self.set_choice(self.usdaChoiceWidget,nutrow)
            return
        lst = self.nd.get_usda_list_for_string(ing)
        self.usdaDict={}
        for l in lst: self.usdaDict[l[0]]=l[1]
        self.choices[self.usdaChoiceWidget]=[x[0] for x in lst]
        self.setup_choices(self.choices[self.usdaChoiceWidget],self.usdaChoiceWidget)

    def get_active_usda (self):
        return cb.cb_get_active_text(self.usdaChoiceWidget)

    def get_multiplier (self, *args):
        d=None
        # Grab our density (either the default density for the food, or the density for the
        # user-selected description, such as chopped, sliced, etc).
        if None in self.densities or self.densities and self.get_choice(self.descChoiceWidget):
            d=self.densities[self.get_choice(self.descChoiceWidget) or None]
        multiplier=self.nut and self.nd.convert_amount(self.amount,
                                                       self.unit,
                                                       d)
        if multiplier:
            self.set_unit_visibility(False) # if we don't need unit info, don't show it
            return multiplier
        elif self.nut: #if we just need the right unit, see if the user has entered an equivalent...
            # otherwise, we do need unit info, keep it visible
            self.set_unit_visibility(True)
            try:
                amt = convert.frac_to_float(self.amountWidget.get_text())
            except:
                # if there's not a number in Amt, we want to grab it
                self.amountWidget.grab_focus()
                return
            else:
                unit = self.get_choice(self.unitChoiceWidget)
                if unit in self.extra_units:
                    return self.nd.convert_amount(amt*self.extra_units[unit],'g.')
                else:
                    return self.nd.convert_amount(amt,unit,d)

    def usdaChangedCB (self, *args):
        usda_choice = self.get_active_usda()
        ndbno = self.usdaDict[usda_choice]
        self.nut = self.nd.db.nutrition_table.select({'ndbno':ndbno})[0]
        self.setup_unit_boxes(nutrow=self.nut)
        self.set_amount()

    def amountChangedCB (self, *args):
        self.set_amount()

    def set_amount (self):
        multiplier = self.get_multiplier()
        if not multiplier:
            #self.unitLabel="%s %s = "%(self.amount,self.unit)
            #self.unitEntry="?"
            self.currentAmountWidget.set_text("%s %s (? grams)"%(self.amount,self.unit))
        else:
            self.currentAmountWidget.set_text("%s %s (%s grams)"%(self.amount,self.unit,
                                                                  multiplier*100))
        self.infoTable.set_nutrition_object(self.nut,multiplier)

    def get_new_conversion (self, *args):
        unit=self.get_choice(self.unitChoiceWidget)
        amt = self.amountWidget.get_text()
        try:
            amt = float(amt)
        except:
            de.show_message(label='Invalid Amount',sublabel='Amount %s is not a number.'%amt)
            self.amountWidget.grab_focus()
        self.amount=amt
        self.unit = unit
        self.usdaChangedCB()

    def setup_choices (self, choices, choiceWidget):
        """Given a list of choices, we setup widget choiceWidget
        to offer those choices to user. By subclassing and overriding
        this method, we can let subclasses use any method they like
        to offer choices

        This function can also be handed None instead of choices, in which
        case there is no meaningful choice for the user to make"""
        # make sure there's no current model
        self.choices[choiceWidget]=choices
        choiceWidget.set_model(None)
        if choices:
            cb.set_model_from_list(choiceWidget,choices,expand=False)
        else:
            cb.set_model_from_list(choiceWidget,[None])

    def get_choice (self, choiceWidget):
        """Return the user's current choice from choiceWidget"""
        return cb.cb_get_active_text(choiceWidget)

    def set_choice (self, choiceWidget, choice):
        return cb.cb_set_active_text(choiceWidget,choice)


class NutritionCardView:
    def __init__ (self, recCard):
        self.rc = recCard
        from . import nutritionGrabberGui
        nutritionGrabberGui.check_for_db(self.rc.rg.rd)
        self.nmodel = NutritionTreeModel(
            self.get_nd(),
            nutrition_fields=self.rc.prefs.get('nutritionFields',
                                               # default nutritional fields
                                               ['kcal','protein','carb','fiber',
                                                'calcium','iron','sodium',
                                                'fasat','famono','fapoly','cholestrl'])
            )
        self.nmodel.attach_treeview(self.rc.ui.get_object('nutTreeView'))
        self.ings = self.rc.rg.rd.get_ings(self.rc.current_rec)
        for i in self.ings: self.nmodel.add_ingredient(i)
        NutritionCardViewOld(recCard) # initialize our old interface as well...

    def get_nd (self):
        if hasattr(self.rc.rg,'nutritionData'): return self.rc.rg.nutritionData
        else:
            from . import nutrition
            self.rc.rg.nutritionData = nutrition.NutritionData(self.rc.rg.rd,self.rc.rg.conv)
            return self.rc.rg.nutritionData

class NutritionCardViewOld:

    """We handle the nutritional portion of our recipe card interface."""

    ING_COL = 0
    NUT_COL = 1
    STR_COL = 2

    def __init__ (self, recCard):
        from . import nutritionGrabberGui
        self.rc = recCard
        self.ings = self.rc.rg.rd.get_ings(self.rc.current_rec)
        nutritionGrabberGui.check_for_db(self.rc.rg.rd)
        # grab our widgets
        self.treeview = self.rc.ui.get_object('nutritionTreeView')
        self.treeview.set_property('headers-visible',False)
        self.treeview.set_property('search-column',self.STR_COL)
        #self.expander = self.rc.ui.get_object('nutritionExpander')
        nutTable = self.rc.ui.get_object('nutritionTable')
        self.usdaExpander = self.rc.ui.get_object('usdaExpander')
        self.nutTable = NutritionTable(nutTable,self.rc.prefs)
        self.keyBox = self.rc.ui.get_object('nutritionKeyBox')
        self.keyBox.entry = self.keyBox.get_children()[0]
        self.usdaCombo = self.rc.ui.get_object('nutritionUSDACombo')
        self.UnitLabel = self.rc.ui.get_object('nutUnitLabel')
        self.UnitEntry = self.rc.ui.get_object('nutUnitEntry')
        self.UnitCombo = self.rc.ui.get_object('nutUnitCombo')
        self.applyButton = self.rc.ui.get_object('nutritionApplyButton')
        self.applyButton.connect('clicked',self.applyCB)
        self.customizeButton = self.rc.ui.get_object('nutritionCustomizeButton')
        self.radioManual = self.rc.ui.get_object('nutMethod')
        self.radioCalc = self.rc.ui.get_object('nutMethodCalcButton')
        self.radioUSDA = self.rc.ui.get_object('nutMethodLookupButton')
        self.radioManual.connect('toggled',self.nutMethodCB)
        self.niv = NutritionItemView(
            self.get_nd(),
            self.usdaCombo,
            self.keyBox.entry,
            self.rc.ui.get_object('nutAmountEntry'),
            self.UnitCombo,
            self.rc.ui.get_object('nutDescBox'),
            self.rc.ui.get_object('nutCurrentUnitLabel'),
            self.nutTable,
            amountLabel=self.rc.ui.get_object('nutAmountLabel'),
            unitChoiceLabel=self.rc.ui.get_object('nutUnitLabel'),
            descChoiceLabel=self.rc.ui.get_object('nutDescLabel'),
            )
        # self.nmodel = NutritionModel(self.rc.ings,self.get_nd()) # no longer use this
        # build our ingredient/nutrition model for our treeview
        self.setup_nmodel()
        self.setup_treeview_columns()
        self.treeview.set_model(self.nmodel)
        # setup treeview callback for selection change
        self.treeviewsel = self.treeview.get_selection()
        self.treeviewsel.set_mode(Gtk.SelectionMode.SINGLE)
        self.treeviewsel.connect('changed',self.selectionChangedCB)
        self.multiplier = None
        self.nutcombo_set = None

    def setup_nmodel (self):
        # make sure we have an ingredient list
        if not hasattr(self.rc,'ings'):
            self.rc.create_ing_alist()
        self.nmodel = Gtk.ListStore(GObject.TYPE_PYOBJECT,
                                    GObject.TYPE_PYOBJECT,
                                    str)
        self.nmodel.append([None,None,"Recipe"])
        for i in self.rc.ings:
            aliasrow=self.get_nd().get_key(i.ingkey)
            if aliasrow:
                nut_row = self.rc.rg.rd.nutrition_table.select({'ndbno':aliasrow.ndbno})
            else:
                nut_row = None
            self.nmodel.append([i,nut_row,i.ingkey])


    def setup_treeview_columns (self):
        for n in [self.STR_COL]:
            rend = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn("",rend,text=n)
            col.set_reorderable(True)
            col.set_resizable(True)
            self.treeview.append_column(col)

    def get_nd (self):
        if hasattr(self.rc.rg,'nutritionData'): return self.rc.rg.nutritionData
        else:
            from . import nutrition
            self.rc.rg.nutritionData = nutrition.NutritionData(self.rc.rg.rd,self.rc.rg.conv)
            return self.rc.rg.nutritionData

    def selectionChangedCB (self, *args):
        mod,itr = self.treeviewsel.get_selected()
        self.ing=mod.get_value(itr,self.ING_COL)
        self.nut = mod.get_value(itr,self.NUT_COL)
        if not self.ing or self.nut:
            # then this is the recipe that's been selected!
            self.radioCalc.show()
            self.radioUSDA.hide()
            self.usdaExpander.hide()
            return
        else:
            self.radioCalc.hide()
            self.radioUSDA.show()
            #if not self.nutcombo_set==self.ing:
            #    self.niv.setup_usda_choices(self.ing.ingkey)
            #    self.nutcombo_set=self.ing
            self.usdaExpander.set_expanded(True)
        if self.nut:
            self.setup_usda_box()
            self.radioUSDA.set_active(True)
        else:
            self.radioManual.set_active(True)
        self.keyBox.entry.set_text(self.ing.ingkey)

    def setup_usda_box (self):
        self.niv.amount=self.ing.amount
        self.niv.unit=self.ing.unit
        self.niv.set_ingredient(self.ing.ingkey)
        if self.nut:
            self.niv.set_nutref(nutrow)

    def setup_keybox (self, ing):
        self.keyBox.set_model(self.rc.rg.inginfo.key_model.filter_new())
        self.keyBox.set_text_column(0)
        curkey = self.keyBox.entry.get_text()
        keys = self.rc.rg.rd.key_search(ing.item)
        mod=self.keyBox.get_model()
        if keys:
            def vis (m, iter):
                x = m.get_value(iter,0)
                if x and x in keys: return True
            mod.set_visible_func(vis)
        else:
            mod=set_visible_func(lambda *args: True)
        mod.refilter()
        if len(self.keyBox.get_model()) > 6:
            self.keyBox.set_wrap_width(2)
            if len(self.keyBox.get_model()) > 10:
                self.keyBox.set_wrap_width(3)
        cb.setup_completion(self.keyBox)


    def nutMethodCB (self, widget, *args):
        # our widget is the "manual" widget
        if widget.get_active():
            self.usdaExpander.set_expanded(False)
            self.usdaExpander.set_sensitive(False)
            self.nutTable.set_editable(True)
        else:
            self.usdaExpander.set_sensitive(True)
            self.setup_usda_box()
            self.usdaExpander.set_expanded(True)
            self.nutTable.set_editable(False)


    def applyCB (self,*args):
        # ADD SOMETHING HERE TO CALL A "SAVE" type method on our NIV
        # now update our model
        # grab our new conversion
        self.niv.get_new_conversion()
        nmod,itr = self.treeviewsel.get_selected()
        # set our new key
        ing=nmod.get_value(itr,self.ING_COL)
        # (make undoable!)
        #self.rc.rg.rd.undoable_modify_ing(ing,{'ingkey':key},self.rc.history)
        row = self.rc.rg.rd.nutrition_table.select({'ndbno':ndbno})[0]
        nmod.set_value(itr,self.NUT_COL,row)
        #nmod.set_value(itr,self.STR_COL,key)

class NutritionTreeModel (Gtk.TreeStore):
    """Display our nutritional information in a simple tree model.

    > Ingredient-Name | Ingredient-Key | USDA-NAME | AMT | UNIT | Grams |
       > NUTINFO | VALUE
       > NUTINFO | VALUE
       > ...

       """

    ING_OBJECT_COLUMN = 0

    def __init__ (self,
                  nutritionData,
                  ingredient_info=['ingkey','amount','unit'],
                  nutrition_fields=['kcal','protein','carb','fasat','famono','fapoly','cholestrl'],
                  ):
        self.nd = nutritionData
        self.columns = ingredient_info + ['USDA','grams']
        self.numerics = ['amount','grams']
        self.build_store()
        self.nutrition_fields = nutrition_fields

    def build_store (self):
        n = self.ING_OBJECT_COLUMN
        self.ts_col_dic = {}
        self.coltypes = [GObject.TYPE_PYOBJECT] # for our ingobject
        for c in self.columns:
            n += 1
            if c in self.numerics: self.coltypes += [str] # everything's a string
            else: self.coltypes += [str]
            self.ts_col_dic[c]=n
        self.ts = GObject.GObject.__init__(self,*self.coltypes)

    def attach_treeview (self, treeview):
        self.tv = treeview
        self.tv.set_model(self)
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_property('editable',True)
        for col in self.columns:
            # not yet i18n'd
            if col=='USDA':
                rend = Gtk.CellRendererCombo()
                self.usda_model = Gtk.ListStore(str,str)
                rend.set_property('model',self.usda_model)
                rend.set_property('text-column',0)
                rend.set_property('editable',True)
                rend.connect('editing-started',self.usda_editing_started_cb)
                rend.connect('edited',self.usda_edited_cb)
                col=Gtk.TreeViewColumn(col,rend,text=self.ts_col_dic[col])
            else:
                col=Gtk.TreeViewColumn(col,text_renderer,text=self.ts_col_dic[col])
            col.set_reorderable(True)
            col.set_resizable(True)
            self.tv.append_column(col)
        self.tv.connect('row-expanded',self.populateChild)

    def add_ingredient (self, ing):
        base_list = [self.grab_attr(ing,name) for name in self.columns]
        itr=self.append(None,[ing]+base_list)
        self.append(itr)

    def populateChild (self, tv, iter, path):
        child = self.iter_children(iter)
        if self.get_value(child, 0)==None:
            self.remove(child) # remove the blank...
            self.append_nutritional_info(iter)

    def append_nutritional_info (self,iter):
        """Handed an treestore iter, append nutritional information."""
        ing = self.get_value(iter,self.ING_OBJECT_COLUMN)
        nut = self.nd.get_nutinfo(ing.ingkey)
        for fld in self.nutrition_fields:
            append_vals = [None] * (len(self.columns) + 1)
            append_vals[1]=fld
            if nut: append_vals[2]=getattr(nut,fld)
            self.append(iter,append_vals)

    def grab_attr (self, ing, name):
        if name in list(gglobals.ING_ATTRS.keys()):
            attval =  getattr(ing,name)
            if name in self.numerics:
                return convert.float_to_frac(attval)
            else:
                return attval
        elif name=='USDA':
            nutrow=self.nd.get_nutinfo(ing.ingkey)
            if nutrow: return nutrow.desc
            else: return None
        elif name=='grams':
            #nutrow=self.nd.get_nutinfo(ing.ingkey)
            #densities,extra_units=self.nd.get_conversions(nutrow)
            amt = self.nd.get_conversion_for_amt(ing.amount,
                                                 ing.unit,
                                                 ing.ingkey

                                                 )
            if amt: return 100 * amt
            else:
                return 0

    def usda_editing_started_cb (self,renderer,editable,path_string):
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        itr = self.get_iter(path)
        ing = self.get_value(itr,self.ING_OBJECT_COLUMN)
        if isinstance(editable,Gtk.ComboBoxEntry):
            while len(self.usda_model)>0: del self.usda_model[0] # empty our liststore...
            usda_list=self.nd.get_usda_list_for_string(ing.ingkey)
            self.usdaDict={}
            for l in usda_list:
                self.usdaDict[l[0]]=l[1]
                self.usda_model.append(l)

    def usda_edited_cb (self,renderer,path_string,text):
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        itr = self.get_iter(path)
        ing = self.get_value(itr,self.ING_OBJECT_COLUMN)
        self.nd.set_key_from_ndbno(ing.ingkey,self.usdaDict[text])
        self.set_value(itr,self.ts_col_dic['USDA'],text)



if __name__ == '__main__':
    w = Gtk.Window()
    f = Gtk.Entry()
    b = Gtk.Button(stock=Gtk.STOCK_ADD)
    hb = Gtk.HBox()
    hb.add(f)
    hb.add(b)
    vb = Gtk.VBox()
    vb.add(hb)
    t = Gtk.Table()
    nt = Gtk.NutritionTable(t, {}, True)
