from gi.repository import Gtk
import gourmet.gtk_extras.dialog_extras as de
from gourmet.plugin import RecDisplayModule, UIPlugin, MainPlugin, ToolPlugin
from .recipe_emailer import RecipeEmailer
from gettext import gettext as _

class EmailRecipePlugin (MainPlugin, UIPlugin):

    ui_string = '''
   <menubar name="RecipeIndexMenuBar">
         <menu name="Tools" action="Tools">
       <placeholder name="StandaloneTool">
           <menuitem action="EmailRecipes"/>
       </placeholder>
   </menu>
   </menubar>
    '''

    def setup_action_groups (self):
        self.actionGroup = Gtk.ActionGroup(name='RecipeEmailerActionGroup')
        self.actionGroup.add_actions([
                ('EmailRecipes',None,_('Email recipes'),
                 None,_('Email all selected recipes (or all recipes if no recipes are selected'),self.email_selected),
                ])
        self.action_groups.append(self.actionGroup)

    def activate (self, pluggable):
        self.rg = self.pluggable = pluggable
        self.add_to_uimanager(pluggable.ui_manager)

    def get_selected_recs (self):
        recs = self.rg.get_selected_recs_from_rec_tree()
        if not recs:
            recs = self.rd.fetch_all(self.rd.recipe_table, deleted=False, sort_by=[('title',1)])
        return recs

    def email_selected (self, *args):
        recs = self.get_selected_recs()
        l = len(recs)
        if l > 20:
            if not de.getBoolean(
                title=_('Email recipes'),
                # only called for l>20, so fancy gettext methods
                # shouldn't be necessary if my knowledge of
                # linguistics serves me
                sublabel=_('Do you really want to email all %s selected recipes?')%l,
                custom_yes=_('Yes, e_mail them'),
                cancel=False,
                ):
                return
        re = RecipeEmailer(recs)
        re.send_email_with_attachments()



