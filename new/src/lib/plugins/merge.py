import gtk
from gettext import gettext as _
from gourmet import gglobals
from gourmet.ui.dialogs import GladeDialog
from gourmet import converter
from gourmet import identify

def attach_window(window):
    def test(*args):
        dialog = RecipeMergerDialog()
        dialog.show()
    ui = '<ui><menubar name="MenuBar"><menu name="ToolsMenu" action="ToolsMenu"><placeholder name="ToolsActions"><menuitem name="Merge" action="Merge" /></placeholder></menu></menubar></ui>' 
    
    actions = [
        ('Merge', None, '_Merge recipes', None, 'Merge duplicate recipes', test),
    ]
    ag = gtk.ActionGroup('merge')
    ag.add_actions(actions)

    manager = window.ui_manager
    manager.insert_action_group(ag, -1)
    manager.add_ui_from_string(ui)

class RecipeMergerDialog (GladeDialog):
    """
    A dialog to allow the user to merge recipes.
    """

    glade_file = 'recipeMerger.glade'

    # These line up to the position of the options in the search-type
    # combo box in glade...
    RECIPE_DUP_MODE = 0
    ING_DUP_MODE = 1
    COMPLETE_DUP_MODE = 2

    DUP_INDEX_PAGE = 0
    MERGE_PAGE = 1
    
    def __init__ (self):
        GladeDialog.__init__(self)
        self.to_merge = [] # Queue of recipes to be merged...
        self.widgets['searchTypeCombo'].set_active(self.COMPLETE_DUP_MODE)

    def setup_treeview (self):
        renderer = gtk.CellRendererText()
        col = gtk.TreeViewColumn('Recipe',renderer,text=2)
        self.duplicateRecipeTreeView.append_column(col)
        self.duplicateRecipeTreeView.insert_column_with_data_func(
            -1, # position
            'Last Modified', # title
            renderer, # renderer
            self.time_cell_data_func, # function
            3 # data column
            )
        self.duplicateRecipeTreeView.append_column(col)
        col = gtk.TreeViewColumn('Duplicates',renderer,text=4)
        self.duplicateRecipeTreeView.append_column(col)
        self.duplicateRecipeTreeView.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    def time_cell_data_func (self, tree_column, cell, model, titer, data_col):
        """Display time in treeview cell.
        """
        val = model.get_value(titer,data_col)
        curtime = time.time()
        # within 18 hours, return in form 4 hours 23 minutes ago or some such
        if val == 0:
            cell.set_property('text',_('Unknown'))
            return
        if curtime - val < 18 * 60 * 60:
            cell.set_property('text',
                              _("%s ago")%converter.seconds_to_timestring(curtime-val,round_at=1))
            return
        tupl=time.localtime(val)
        if curtime - val <  7 * 24 * 60 * 60:
            cell.set_property('text',
                              time.strftime('%A %T',tupl))
            return
        else:
            cell.set_property('text',
                              time.strftime('%D %T',tupl))
            return

    def populate_tree (self):
        """Populate treeview with duplicate recipes.
        """
        search_mode =self.searchTypeCombo.get_active()
        include_deleted = self.includeDeletedRecipesCheckButton.get_active()
        if search_mode == self.RECIPE_DUP_MODE:
            dups = self.rd.find_duplicates(by='recipe',
                                    recipes=self.in_recipes,
                                    include_deleted=include_deleted)
        elif search_mode == self.ING_DUP_MODE:
            dups = self.rd.find_duplicates(by='ingredient',
                                    recipes=self.in_recipes,
                                    include_deleted=include_deleted)
        else: # == self.COMPLETE_DUP_MODE
            dups = self.rd.find_complete_duplicates(include_deleted=include_deleted,
                                             recipes=self.in_recipes)
        self.setup_treemodel(dups)
        self.dups = dups
        self.duplicateRecipeTreeView.set_model(self.treeModel)

    def setup_treemodel (self, dups):
        self.treeModel = gtk.TreeStore(int,int,str,int,str) # dup_index, rec_id, rec_title, last_modified, number_of_duplicates
        for dup_index,duplicate_recipes in enumerate(dups):
            first = duplicate_recipes[0]
            others = duplicate_recipes[1:]
            nduplicates = len(duplicate_recipes)
            r = self.rd.get_rec(first)
            firstIter = self.treeModel.append(
                None,
                (dup_index, first, r.title, r.last_modified or 0, str(nduplicates))
                )
            for o in others:
                r = self.rd.get_rec(o)
                self.treeModel.append(firstIter,
                                      (dup_index,o,r.title,r.last_modified or 0,'')
                                      )
    def merge_next_recipe (self, ):
        if self.to_merge:
            self.current_dup_index = self.to_merge.pop(0)
            duplicate_recipes = self.dups[self.current_dup_index]
            #self.idt = IngDiffTable(self.rd,duplicate_recipes[0],duplicate_recipes[1])
            self.current_recs = [self.rd.get_rec(i) for i in duplicate_recipes]
            self.current_diff_data = recipeIdentifier.diff_recipes(self.rd,self.current_recs)
            self.diff_table = DiffTable(self.current_diff_data,self.current_recs[0],parent=self.recipeDiffScrolledWindow)
            self.diff_table.add_ingblocks(self.rd, self.current_recs)
            if not self.diff_table.idiffs and not self.current_diff_data:
                # If there are no differences, just merge the recipes...
                self.apply_merge()
                return
            if self.recipeDiffScrolledWindow.get_child():
                self.recipeDiffScrolledWindow.remove(self.recipeDiffScrolledWindow.get_child())
            self.diff_table.show()
            #self.idt.show()
            vb = gtk.VBox()
            vb.add(self.diff_table)
            #vb.add(self.idt)
            vb.show()
            #self.recipeDiffScrolledWindow.add_with_viewport(self.diff_table)
            self.recipeDiffScrolledWindow.add_with_viewport(vb)
            self.notebook.set_current_page(self.MERGE_PAGE)
        else:
            self.notebook.set_current_page(self.DUP_INDEX_PAGE)

    def do_merge (self, merge_dic, recs, to_keep=None):
        if not to_keep:
            to_keep = recs[0]
        if type(to_keep)==int:
            to_keep = self.rd.get_rec(to_keep)
        self.rd.modify_rec(to_keep,merge_dic)
        for r in recs:
            if r.id != to_keep.id:
                self.rd.delete_rec(r)
        
    def apply_merge (self, *args):
        #print "CALL: apply_merge"
        #print 'Apply ',self.diff_table.selected_dic,'on ',self.diff_table.rec
        self.do_merge(self.diff_table.selected_dic,
                      self.current_recs,
                      to_keep=self.diff_table.rec)
        self.merge_next_recipe()
        if not self.to_merge:
            self.populate_tree()
            
    def merge_selected (self, *args):
        """Merge currently selected row from treeview.
        """
        mod,rows = self.duplicateRecipeTreeView.get_selection().get_selected_rows()
        dup_indices = [mod[r][0] for r in rows]
        self.to_merge = []
        for d in dup_indices:
            if d not in self.to_merge:
                self.to_merge.append(d)
        self.merge_next_recipe()
        
    def merge_all (self, *args):
        """Merge all rows currently in treeview.
        """
        #print 'CALL: merge_all'
        self.to_merge = range(len(self.dups))
        self.merge_next_recipe()

    def cancel_merge (self, *args):
        self.merge_next_recipe()
        if not self.to_merge:
            self.populate_tree()

    def populate_tree_if_possible (self):
        self.populate_tree()
        if not self.dups:
            self.searchTypeCombo.set_active(self.RECIPE_DUP_MODE)
            self.populate_tree()
            if not self.dups:
                self.searchTypeCombo.set_active(self.ING_DUP_MODE)
                self.populate_tree()

    def show_if_there_are_dups (self, label=None):
        self.populate_tree_if_possible()
        if self.dups:
            self.show(label=label)
        else:
            self.glade.get_widget('window').destroy()
        
    def show (self, label=None):
        self.dialog.show()

    def close (self, *args):
        self.dialog.hide()
        self.dialog.destroy()
