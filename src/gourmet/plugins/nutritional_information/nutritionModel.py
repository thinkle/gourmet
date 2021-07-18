from gi.repository import GObject, Gtk

from gourmet.i18n import _


class NutritionModel (Gtk.TreeStore):
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
        Gtk.TreeStore.__init__(self,GObject.TYPE_PYOBJECT,str,str,str,str)
        self.nd = nd
        self.ings = ings
        list(map(self.add_ingredient,self.ings))

    def add_ingredient (self, ing):
        r=self.nd.get_key(ing.ingkey)
        if r: desc=r.desc
        else: desc = self.UNKNOWN
        self.append(None,[ing,str(ing.amount),ing.unit,str(ing.item),desc])
