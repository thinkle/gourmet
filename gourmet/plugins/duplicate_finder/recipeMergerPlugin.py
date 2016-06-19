from __future__ import print_function

from gourmet.plugin import ToolPlugin, ImportManagerPlugin
import gtk
import recipeMerger
from gettext import gettext as _
#from gourmet.gglobals import gt # for threading protection on import
#                                # hooks
from gourmet.plugin_loader import PRE,POST

class RecipeMergerImportManagerPlugin (ImportManagerPlugin):

    def activate (self, pluggable):
        pluggable.add_hook(PRE,'follow_up',self.follow_up_pre_hook)

    def follow_up_pre_hook (self, importManager, threadmanager, importer):
        print('Running recipeMergerPlugin follow up post hook!')
        if importer.added_recs:
            print('There are ', len(importer.added_recs), 'added recs!')
            rmd = recipeMerger.RecipeMergerDialog(
                in_recipes=importer.added_recs,
                )
            rmd.show_if_there_are_dups(
                label=_('Some of the imported recipes appear to be duplicates. You can merge them here, or close this dialog to leave them as they are.')
                )
        return [threadmanager,importer],{}

class RecipeMergerPlugin (ToolPlugin):

    menu_items = '''
    <placeholder name="DataTool">
      <menuitem action="DuplicateMerger"/>
    </placeholder>'''

    menu_bars = ['RecipeIndexMenuBar']

    def activate (self, pluggable):
        ToolPlugin.activate(self,pluggable)
        pluggable.add_hook(PRE,'import_cleanup',self.import_cleanup_hook)

    def deactivate (self, pluggable):
        if hasattr(self,'pluggable'):
            pluggable.remove_hook(PRE,'import_cleanup',self.import_cleanup_hook)

    def remove (self):
        if hasattr(self,'pluggable'):
            self.pluggable.remove_hook(PRE,'import_cleanup',self.import_cleanup_hook)
        ToolPlugin.remove(self)                                     

    def import_cleanup_hook (self, rg, retval, *args, **kwargs):
        # Check for duplicates
        #gt.gtk_enter()
        if rg.last_impClass and rg.last_impClass.added_recs:
            rmd = recipeMerger.RecipeMergerDialog(
                rg.rd,
                in_recipes=rg.last_impClass.added_recs,
                on_close_callback=lambda *args: rg.redo_search()
                )
            rmd.show_if_there_are_dups(
                label=_('Some of the imported recipes appear to be duplicates. You can merge them here, or close this dialog to leave them as they are.')
                )
        #gt.gtk_leave()
    
    def setup_action_groups (self):
        self.action_group = gtk.ActionGroup('RecipeMergerPluginActionGroup')
        self.action_group.add_actions([
            ('DuplicateMerger',None,_('Find _duplicate recipes'),
             None,_('Find and remove duplicate recipes'),self.show_duplicate_merger)
            ]
                                      )
        self.action_groups.append(self.action_group)

    def show_duplicate_merger (self, *args):
        rmd = recipeMerger.RecipeMergerDialog(
            self.pluggable.rg.rd,
            on_close_callback=lambda *args: self.pluggable.rg.redo_search()
            )
        rmd.populate_tree_if_possible()
        rmd.show()
     
