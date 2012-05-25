from gourmet.plugin import MainPlugin
import gtk
import browser
from gourmet.plugin_loader import PRE, POST

class BrowserPlugin (MainPlugin):

    def activate (self, pluggable):
        MainPlugin.activate(self,pluggable)
        self.browser = browser.RecipeBrowser(pluggable.rd)
        self.browser.view.connect('recipe-selected',self.recipe_activated_cb)
        self.browser.view.connect('selection-changed',self.selection_changed_cb)
        self.add_tab(self.browser,'Browse Recipes')
        pluggable.add_hook(POST, 'get_selected_recs_from_rec_tree',self.get_selected_post_hook)
        pluggable.add_hook(PRE, 'redo_search',self.reset_view)
        pluggable.add_hook(PRE, 'update_recipe',self.update_recipe)

    def selection_changed_cb (self, iconview):
        paths = iconview.get_selected_items()
        if not paths:
            self.recipes_unselected()
            return 
        model = iconview.get_model()
        rid = model[paths[0]][0]
        try:
            int(rid)
        except ValueError:
            self.recipes_unselected()
        else:
            # If we have an integer ID, we are selecting recipes!
            self.recipes_selected()

    def recipes_unselected (self):
        """Toggle our action items etc. for no recipes selected"""
        self.main.selection_changed(False)

    def recipes_selected (self):
        """Toggle our action items etc. for recipes selected"""
        self.main.selection_changed(True)

    def recipe_activated_cb (self, browser, rid):
        self.main.open_rec_card(self.main.rd.get_rec(rid))

    def reset_view (self, *args):
        self.browser.view.reset_model()

    def update_recipe (recipe):
        self.reset_view()

    def get_selected_post_hook (self, recs_from_recindex, pluggable):
        if self.main.main_notebook.get_current_page() in self.added_tabs:
            # then get recipes from iconview...
            retval = self.browser.view.get_selected_recipes()
            return retval
        else:
            return recs_from_recindex

plugins = [BrowserPlugin,]
