import gtk, gobject
from gettext import gettext as _

class NutritionModel (gtk.TreeStore):
    """Handed ingredients and a nutritional database, display
    our nutritional information thus far."""
    AMOUNT_COL_HEAD = _("Amount")
    UNIT_COL_HEAD = _("Unit")
    ING_COL_HEAD = _("Ingredient")
    USDA_COL_HEAD = _("USDA Database Equivalent")
    UNKNOWN = _("Unknown")
    AMT_COL = 1
    UNIT_COL = 2
    ING_COL = 3
    USDA_COL = 4
    def __init__ (self, ings, nd):
        gtk.TreeStore.__init__(self,gobject.TYPE_PYOBJECT,str,str,str,str)
        self.nd = nd
        self.ings = ings
        map(self.add_ingredient,self.ings)
        
    def add_ingredient (self, ing):
        r=self.nd.get_key(ing.ingkey)
        if r: desc=r.desc
        else: desc = self.UNKNOWN
        self.append(None,[ing,str(ing.amount),ing.unit,str(ing.item),desc])        
