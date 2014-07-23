from nutritionLabel import NutritionLabel
from nutrition import NutritionInfoList, NutritionVapor
#from gourmet.gglobals import gladeCustomHandlers
from gourmet.plugin import RecDisplayModule, RecDisplayPlugin
import gtk, pango
import os.path

try:
    current_path = os.path.split(os.path.join(os.getcwd(),__file__))[0]
except:
    current_path = ''

class NutritionDisplayModule (RecDisplayModule):
    label = _('Nutrition')
    name = 'nutrition_display'
    #_custom_handlers_setup = False

    def __init__ (self, recipe_display):
        self.recipe_display = recipe_display
        self.nutritional_highlighting = True
        self.prefs = self.recipe_display.rg.prefs
        self.setup_ui()
        self.setup_ingredient_display_hooks()
        self.update_from_database()
        
    def update_from_database (self):
        self.nutinfo = self.recipe_display.rg.rd.nd.get_nutinfo_for_inglist(self.recipe_display.current_rec.ingredients)
        #print 'Set servings',self.recipe_display.current_rec.servings,type(self.recipe_display.current_rec.servings)
        self.nutritionLabel.set_yields(
            self.recipe_display.current_rec.yields,
            self.recipe_display.current_rec.yield_unit
                                       )
        self.nutritionLabel.set_nutinfo(self.nutinfo)
        self.nutritionLabel.rec = self.recipe_display.current_rec
        
    def setup_ui (self):
        #if not NutritionDisplayModule._custom_handlers_setup:
        #    gladeCustomHandlers.add_custom_handler('makeNutritionLabel',
        #                                           lambda *args: NutritionLabel(self.prefs)
        #                                           )
        #    NutritionDisplayModule._custom_handlers_setup = True
        self.ui = gtk.Builder()
        self.ui.add_from_file(os.path.join(current_path,'nut_recipe_card_display.ui'))
        self.ui.connect_signals(
            {'edit_nutrition': lambda *args: self.nutritionLabel.show_druid(nd=self.recipe_display.rg.rd.nd)}
            )
        self.nutritionLabel = self.ui.get_object('nutritionLabel')
        self.nutritionLabel.set_prefs(self.prefs)
        self.nutritionLabel.connect('ingredients-changed', self.ingredients_changed_cb)
        self.nutritionLabel.connect('label-changed',self.nutrition_highlighting_label_changed)
        self.main = self.ui.get_object('nutritionDisplay')
        self.main.unparent()

    def ingredients_changed_cb (self, *args):
        self.recipe_display.reccard.update_recipe(self.recipe_display.current_rec)
        
    def nutrition_highlighting_label_changed (self, *args):
        self.nutritional_highlighting = True
        self.recipe_display.prefs['nutrition_to_highlight'] = self.nutritionLabel.active_name
        self.recipe_display.ingredientDisplay.display_ingredients()
        
    def leave_page (self):
        self.nutritional_highlighting = False
        self.recipe_display.mult = self.mult_orig
        self.recipe_display.ingredientDisplay.display_ingredients()

    def enter_page (self):
        self.nutritional_highlighting = True
        if not self.nutritionLabel.active_name:
            if self.prefs.get('nutrition_to_highlight','kcal') in self.nutritionLabel.toggles:
                self.nutritionLabel.toggles[
                    self.prefs.get(
                        'nutrition_to_highlight','kcal')
                    ].activate()
        # Save what servings were and set them to "1" so that the
        # ingredient amounts display how much goes into each servings
        # (assuming there is a yield value)
        self.mult_orig = self.recipe_display.mult
        if self.recipe_display.current_rec.yields:
            self.recipe_display.mult = 1.0/self.recipe_display.current_rec.yields
        self.recipe_display.ingredientDisplay.display_ingredients()

    def setup_ingredient_display_hooks (self):
        self.ingredientDisplay = self.recipe_display.ingredientDisplay
        self.ingredientDisplay.markup_ingredient_hooks.append(self.nutritional_markup_hook)

    def nutritional_markup_hook (self, istr, ing, ing_index, group_index):
        if self.nutritional_highlighting and self.nutritionLabel.active_name:
            props = self.nutritionLabel.active_properties
            nutinfo_for_ing = None
            for ni in self.nutinfo:
                if ni.__ingobject__.id==ing.id:
                    nutinfo_for_ing = ni
                    break
            if nutinfo_for_ing is None: # if something is wrong...
                print 'Did not find nutritional info object for ingredient',ing
                print 'We did have...'
                for ni in self.nutinfo:
                    print ni.__ingobject__
                return istr
            if type(props)==str:
                nut_amt = getattr(nutinfo_for_ing,props)
                tot_amt = getattr(self.nutinfo,props)
            else:
                nut_amt = sum([getattr(nutinfo_for_ing,p) or 0 for p in props])
                tot_amt = sum([getattr(self.nutinfo,p) or 0 for p in props])
            if nut_amt:
                perc = float(nut_amt)/tot_amt
                if self.recipe_display.yields_orig: nut_amt = nut_amt/self.recipe_display.yields_orig
                label = self.nutritionLabel.active_unit
                if not self.nutritionLabel.active_unit:
                    label = self.nutritionLabel.active_label.lower()
                if int(nut_amt) or (nut_amt==int(nut_amt)):
                    nut_amt = "%i"%nut_amt
                else:
                    nut_amt = "%.2f"%nut_amt
                istr = istr + ' (%s %s)'%(nut_amt,label)
                faintest_yellow = 200
                color = "#%02x%02x%02x"%(255,255,
                                         faintest_yellow-int(faintest_yellow*(perc**2))
                                        )
                nut_highlighted = True
                weight = int(pango.WEIGHT_NORMAL + ((pango.WEIGHT_HEAVY - pango.WEIGHT_NORMAL) * perc))
                if color:
                    istr = '<span background="%s" foreground="black">'%color + istr + '</span>'
                if weight:
                    istr = '<span weight="%i">'%weight + istr + '</span>'
            if isinstance(nutinfo_for_ing,
                          NutritionVapor):
                istr = '<span foreground="red">'+istr+'</span>'
        return istr
        

class NutritionDisplayPlugin (RecDisplayPlugin):

    moduleKlass = NutritionDisplayModule



