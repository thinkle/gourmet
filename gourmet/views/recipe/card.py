from gourmet.models import Session

from display import RecCardDisplay
from editor import RecEditor

# OVERARCHING RECIPE CARD CLASS - PROVIDES GLUE BETWEEN EDITING AND DISPLAY

class RecCard (object):
    
    def __init__ (self, rg=None, recipe=None, manual_show=False, session=Session()):
        if not rg:
            from GourmetRecipeManager import get_application
            rg = get_application()
        self.rg = rg
        self.session = session
        self.conf = []
        self.new = False
        if not recipe:
            recipe = Recipe(title=_('New Recipe'))
            self.new = True
        self.current_rec = recipe
        if not manual_show:
            self.show()

    def set_current_rec (self, rec):
        self.__current_rec = rec
        if hasattr(self,'recipe_editor'):
            self.recipe_editor.current_rec = rec
        if hasattr(self,'recipe_display'):
            self.recipe_display.current_rec = rec

    def get_current_rec (self):
        return self.__current_rec
    
    current_rec = property(get_current_rec,
                           set_current_rec,
                           None,
                           "Recipe in the recipe card")
    def get_edited (self):
        if hasattr(self,'recipe_editor') and self.recipe_editor.edited: return True
        else: return False

    def set_edited (self, val):
        if hasattr(self,'recipe_editor') and self.recipe_editor.edited:
            self.recipe_editor.edited = bool(val)
    edited = property(get_edited,set_edited)

    def show_display (self):
        if not hasattr(self,'recipe_display'):
            self.recipe_display = RecCardDisplay(self, self.rg,self.current_rec)
        self.recipe_display.window.present()

    def show_edit (self, module=None):
        if not hasattr(self,'recipe_editor'):
            self.recipe_editor = RecEditor(self, self.rg,self.current_rec,new=self.new)
        if module:
            self.recipe_editor.show_module(module)
        self.recipe_editor.present()
        

    def delete (self, *args):
        self.rg.rec_tree_delete_recs([self.current_rec])

    def update_recipe (self, recipe):
        self.current_rec = recipe
        if hasattr(self,'recipe_display'):
            self.recipe_display.update_from_database()
        if hasattr(self,'recipe_editor') and not self.recipe_editor.window.get_property('visible'):
            delattr(self,'recipe_editor')

    def show (self):
        if self.new:
            self.show_edit()
        else:
            self.show_display()

    def hide (self):
        if ((not (hasattr(self,'recipe_display') and self.recipe_display.window.get_property('visible')))
             and
            (not (hasattr(self,'recipe_editor') and self.recipe_editor.window.get_property('visible')))):
            self.rg.del_rc(self.current_rec.id)

    # end RecCard
