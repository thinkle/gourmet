from gourmet.plugin import MainPlugin
import gtk
import browser

class TestPlugin (MainPlugin):

    def activate (self, pluggable):
        MainPlugin.activate(self,pluggable)
        self.browser = browser.RecipeBrowser(pluggable.rd)
        self.browser.view.connect('recipe-selected',self.recipe_selected_cb)
        self.add_tab(self.browser,'Browse Recipes')

    def recipe_selected_cb (self, browser, rid):
        self.main.open_rec_card(self.main.rd.get_rec(rid))

plugins = [TestPlugin,]
