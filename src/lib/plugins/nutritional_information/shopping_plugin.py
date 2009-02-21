from gourmet.plugin import ShoppingListPlugin
import gtk
import gourmet.recipeManager, gourmet.GourmetRecipeManager
from gourmet.prefs import get_prefs
from nutritionLabel import NutritionLabel
import os.path
from gettext import gettext as _

class ShoppingNutritionalInfoPlugin (ShoppingListPlugin):

    ui = '''<ui>
    <menubar name="ShoppingListMenuBar">
      <menu name="Tools" action="Tools">
          <menuitem action="ShoppingNutritionalInfo"/>
      </menu>
    </menubar>
    <toolbar name="ShoppingListTopToolBar">
      <separator/>
      <toolitem action="ShoppingNutritionalInfo"/>
    </toolbar>
    </ui>
    '''
    name = 'shopping_nutritional_info'

    def setup_action_groups (self):
        self.nutritionShoppingActionGroup = gtk.ActionGroup('NutritionShoppingActionGroup')
        self.nutritionShoppingActionGroup.add_actions([
            ('Tools',None,_('Tools')),
            ('ShoppingNutritionalInfo', # name
             'nutritional-info', # stock
             _('Nutritional Information'), # label
             '<Ctrl><Shift>N', #key-command
             _('Get nutritional information for current list'),
             self.show_nutinfo # callback
             )
            ])
        self.action_groups.append(self.nutritionShoppingActionGroup)

    def show_nutinfo (self, *args):
        sg = self.pluggable
        rr = sg.recs
        rd = gourmet.recipeManager.get_recipe_manager()
        rg = gourmet.GourmetRecipeManager.get_application()
        if not hasattr(self,'nutrition_window'):
            self.create_nutrition_window()
        nutinfo = None
        # Add recipes...
        for rec in rr:
            ings = rd.get_ings(rec)
            ni = rd.nd.get_nutinfo_for_inglist(rd.get_ings(rec),
                                               rd)
            if nutinfo:
                nutinfo = nutinfo + ni
            else:
                nutinfo = ni
        # Add extras...
        for amt,unit,item in sg.extras:
            ni = rd.nd.get_nutinfo_for_item(item,amt,unit)
            if nutinfo:
                nutinfo = nutinfo + ni
            else:
                nutinfo = ni
        self.nl.set_nutinfo(nutinfo)
        self.nutrition_window.present()

    def create_nutrition_window (self):
        self.nutrition_window = gtk.Dialog(_('Nutritional Information'),
                            self.pluggable.w,
                            buttons=(gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE)
                            )
        self.nutrition_window.set_default_size(400,550)
        self.nutrition_window.set_icon(
            self.nutrition_window.render_icon('nutritional-info',
                                              gtk.ICON_SIZE_MENU)
            )
        self.nl = NutritionLabel(get_prefs())
        self.sw = gtk.ScrolledWindow(); self.sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.sw.add_with_viewport(self.nl); self.sw.show()
        self.nutrition_window.vbox.pack_start(self.sw)
        self.nutrition_window.connect('response',self.response_cb)
        self.nutrition_window.connect('close',self.response_cb)
        self.nl.servingLabel.set_markup('<b>'+_('Amount for Shopping List')+'</b>')
        self.nl.show()

    def response_cb (self, *args):
        # We only allow one response -- closing the window!
        self.nutrition_window.hide()
        
        

        
             
