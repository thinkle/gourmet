"""recipeMerger.py

This module contains code for handling the 'merging' of duplicate
recipes.
"""
import gtk, os.path, time
import recipeIdentifier
import ratingWidget, convert
import mnemonic_manager
import gglobals
import convert
from gettext import gettext as _

class ConflictError (ValueError):
    def __init__ (self, conflicts):
        self.conflicts = conflicts

class RecipeMergerDialog:

    """A dialog to allow the user to merge recipes.
    """

    # These line up to the position of the options in the search-type
    # combo box in glade...
    RECIPE_DUP_MODE = 0
    ING_DUP_MODE = 1
    COMPLETE_DUP_MODE = 2

    DUP_INDEX_PAGE = 0
    MERGE_PAGE = 1
    
    def __init__ (self, rd, in_recipes=None, on_close_callback=None):
        self.rd = rd
        self.in_recipes = in_recipes
        self.on_close_callback = on_close_callback
        self.to_merge = [] # Queue of recipes to be merged...
        self.glade = gtk.glade.XML(os.path.join(gglobals.gladebase,'recipeMerger.glade'))
        self.get_widgets()
        self.searchTypeCombo.set_active(self.COMPLETE_DUP_MODE)
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.add_glade(self.glade)
        self.mm.fix_conflicts_peacefully()
        self.glade.signal_autoconnect(
            {
            'on_searchTypeCombo_changed':lambda *args: self.populate_tree(),
            'on_includeDeletedRecipesCheckButton_toggled':lambda *args: self.populate_tree(),
            'on_mergeAllButton_clicked':self.merge_all,
            'on_cancelMergeButton_clicked':self.cancel_merge,
            'on_mergeSelectedButton_clicked':self.merge_selected,
            'on_applyButton_clicked':self.apply_merge,
            'close':self.close,
            }
            )
        
    def get_widgets (self):
        for w in [
            'recipeDiffScrolledWindow',
            'duplicateRecipeTreeView',
            'mergeAllButton','mergeSelectedButton', # buttons on list-dups page (minus close button)
            'applyMergeButton','cancelMergeButton', # buttons on merge-recs page
            'searchTypeCombo','includeDeletedRecipesCheckButton','notebook'
            ]:
            setattr(self,w,self.glade.get_widget(w))
        self.setup_treeview()

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
                              _("%s ago")%convert.seconds_to_timestring(curtime-val,round_at=1))
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
        #print 'CALL: populate_tree'
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
        #print "CALL: merge_selected"
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
            self.glade.get_widget('window1').destroy()
        
    def show (self, label=None):
        if label:
            l = self.glade.get_widget('infoLabel')
            l.set_markup('<span background="yellow" foreground="black"><b><i>%s</i></b></span>'%label)
            l.show()
        self.glade.get_widget('window1').show()

    def close (self, *args):
        #print "CALL: close"
        w = self.glade.get_widget('window1')
        w.hide()
        w.destroy()
        if self.on_close_callback:
            self.on_close_callback(self)
        
class RecipeMerger:

    """A class to handle recipe merging.
    """
    
    def __init__ (self, rd):
        self.rd = rd

    def autoMergeRecipes (self, recs):
        to_fill,conflicts = recipeIdentifier.merge_recipes(self.rd,
                                                           recs)
        if conflicts:
            raise ConflictError(conflicts)
        else:
            to_keep = recs[0]
            # Update a single recipe with our information...
            self.rd.modify_rec(to_keep,to_fill)
            # Delete the other recipes...
            for r in recs[1:]:
                self.rd.delete_rec(r)

    def uiMergeRecipes (self, recs):
        diffs = recipeIdentifier.diff_recipes(self.rd,
                                              recs)
        idiffs = recipeIdentifier.diff_ings(self.rd,r1,r2)
        if diffs:
            return DiffTable(diffs,recs[0])
        else:
            return None

class DiffTable (gtk.Table):

    """A Table displaying differences in a recipe.

    diff_dic is a dictionary with the differences.
    {'attribute':(VAL1,VAL2,...)}

    recipe_object is a recipe object representing one of our duplicate
    recs, from which we can grab attributes that are not different.
    """

    def __init__ (self, diff_dic, recipe_object=None, parent=None):
        self.idiffs = []
        self.diff_dic = diff_dic
        gtk.Table.__init__(self)
        self.selected_dic = {}
        self.set_col_spacings(6)
        self.set_row_spacings(6)        
        self.row = 0
        self.max_cols = 1
        for attr,name,typ in gglobals.REC_ATTRS \
                + [('image','Image',None)] \
                + [(attr,gglobals.TEXT_ATTR_DIC[attr],None) for attr in gglobals.DEFAULT_TEXT_ATTR_ORDER]:
            if diff_dic.has_key(attr):
                buttons = self.build_options(attr,self.diff_dic[attr])
                label = gtk.Label('_'+name+':')
                label.set_alignment(0.0,0.5)
                label.set_use_underline(True)
                label.show()
                self.attach(label,0,1,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
                target = None
                for col,b in enumerate(buttons):
                    self.setup_widget_size(b,in_col=True)
                    b.show()
                    if not target:
                        target = b
                        label.set_mnemonic_widget(target)
                    self.attach(b,col+1,col+2,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
                    if col > self.max_cols: self.max_cols = col
                self.row += 1
            elif recipe_object and hasattr(recipe_object,attr) and getattr(recipe_object,attr):
                att_label = gtk.Label(name+':')
                att_label.set_use_underline(True)
                att_label.set_alignment(0,0.5)
                att_label.show()
                constructor = get_display_constructor(attr)
                val = getattr(recipe_object,attr)
                val_label = constructor(getattr(recipe_object,attr))
                val_label.show()
                self.setup_widget_size(val_label,False)
                if hasattr(val_label,'set_alignment'): val_label.set_alignment(0,0.5)
                self.attach(att_label,0,1,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
                self.attach(val_label,1,5,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)                
                self.row += 1
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.add_toplevel_widget(self)
        self.mm.fix_conflicts_peacefully()
        self.rec = recipe_object.id
        
    def setup_widget_size (self, w, in_col=True):
        if in_col:
            w.set_size_request(230,-1)
        else:
            w.set_size_request(650,-1)

    def build_options (self, attribute, values):
        buttons = []
        group_rb = None
        make_widget = get_display_constructor(attribute)
        for v in values:
            rb = gtk.RadioButton(group=group_rb)
            if not group_rb: group_rb = rb
            if v is not None:
                rb.add(make_widget(v))
            else:
                rb.add(gtk.Label(_("None")))
            rb.show_all()
            buttons.append(rb)
            rb.connect('toggled',self.value_toggled,attribute,v)
        self.selected_dic[attribute] = values[0]
        for n,v in enumerate(values):
            if v:
                buttons[n].set_active(True)
                break
        return buttons

    def value_toggled (self, rb, attribute, v):
        self.selected_dic[attribute] = v

    def add_ingblocks (self, rd, recs):
        #print 'add_ingblocks for ',[r.id for r in recs]
        self.rd = rd
        self.iblock_dic = {}
        if len(recs) == 1:
            blocks = recipeIdentifier.format_ingdiff_line(
                recipeIdentifier.format_ings(recs[0],self.rd)
                )
            self.iblock_dic[blocks[0]] = recs[0]
        else:
            blocks = []
            rec_0 = recs[0]
            for r in recs[1:]:
                chunks = self.get_ing_text_blobs(rec_0,r)
                if not chunks and not blocks:
                    # If there is no diff, in other words, and we
                    # don't yet have any block...
                    chunks = [recipeIdentifier.format_ings(recs[0],self.rd)]
                elif not chunks:
                    # Otherwise if there are no diffs we just continue
                    # our loop...
                    continue
                if not blocks:
                    blocks = [chunks[0]]
                    self.iblock_dic[blocks[0]] = rec_0
                if chunks and len(chunks) > 1:
                    new_block = chunks[1]
                    if new_block not in blocks:
                        blocks.append(new_block)
                        self.iblock_dic[new_block] = r
        group_rb = None
        name = _('Ingredients')
        if len(blocks) > 1:
            lab = gtk.Label('_'+_("Ingredients")); lab.set_use_underline(True)
            for col,block in enumerate(blocks):
                rb = gtk.RadioButton(
                    label=_("Recipe")+ ' ' +'%i'%(col+1),
                    group=group_rb
                    )
                if not group_rb:
                    group_rb = rb
                    lab.set_mnemonic_widget(rb)
                if not block:
                    rb.add(gtk.Label(_("None")))                    
                else:
                    for n,txt in enumerate(block):
                        l = gtk.Label(txt)
                        l.set_alignment(0.0,0.0)                    
                        l.set_use_markup(True)
                        l.set_line_wrap(True); l.set_line_wrap_mode(gtk.WRAP_WORD)
                        l.show()
                        self.setup_widget_size(l,in_col=True)
                        self.attach(l,col+1,col+2,self.row+1+n,self.row+2+n,
                                    xoptions=gtk.SHRINK|gtk.FILL,
                                    yoptions=gtk.SHRINK|gtk.FILL)
                    #rb.add(l)
                rb.connect('toggled',self.ing_value_toggled,block)
                self.setup_widget_size(rb,in_col=True)                
                rb.show()
                self.attach(rb,col+1,col+2,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
        else:
            lab = gtk.Label(_("Ingredients")); lab.show()
            l = gtk.Label(blocks[0])
            l.set_alignment(0.0,0.0)
            l.set_use_markup(True)
            l.set_line_wrap(True); l.set_line_wrap_mode(gtk.WRAP_WORD)
            l.show()
            self.attach(l,1,5,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
        lab.set_alignment(0.0,0.0); lab.show()
        self.attach(lab,0,1,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)

    def ing_value_toggled (self, rb, block):
        if rb.get_active():
            #print 'RB clicked',rb,'for block',block
            #print 'ING TOGGLED - REC = ',
            self.rec = self.iblock_dic[block]
            #print self.rec

    def get_ing_text_blobs (self, r1, r2):
        """Return an ing-blurb for r1 and r2 suitable for display."""
        idiff = recipeIdentifier.diff_ings(self.rd,r1,r2)
        if idiff: self.idiffs.append(idiff)
        def is_line (l):
            return not (l == '<diff/>')
        if idiff:
            return [
                tuple([recipeIdentifier.format_ingdiff_line(i)
                 for i in filter(is_line,igroup)
                 ])
                for igroup in idiff
                ]
        else:
            return None
            
def put_text_in_scrolled_window (text):
    sw = gtk.ScrolledWindow()
    tv = gtk.TextView()
    sw.add(tv)
    tv.get_buffer().set_text(text)
    tv.set_editable(False)
    tv.set_wrap_mode(gtk.WRAP_WORD)
    sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    tv.show()
    return sw

def make_text_label (t, use_markup=False):
    if not t:
        return gtk.Label(_('None'))
    elif len(t) < 30:
        return gtk.Label(t)
    elif len(t) < 250:
        l = gtk.Label(t)
        if use_markup: l.set_use_markup(use_markup)
        l.set_line_wrap_mode(gtk.WRAP_WORD)
        return l
    else:
        return put_text_in_scrolled_window(t)

def get_display_constructor (attribute):
    if attribute == 'rating':
        return lambda v: ratingWidget.make_star_image(
            ratingWidget.star_generator,
            value=v,
            upper=10)
    elif attribute in ['preptime','cooktime']:
        return lambda v: gtk.Label(convert.seconds_to_timestring(v))
    elif attribute=='image':
        return lambda v: (v and gtk.Label("An Image") or gtk.Label("No Image"))
    elif attribute in gglobals.DEFAULT_TEXT_ATTR_ORDER:        
        return make_text_label
    else:
        return lambda v: v and gtk.Label(v) or gtk.Label(_('None'))

if __name__ == '__main__':

    def test_in_window (widget):
        """Put widget in window and show it"""
        w = gtk.Window()
        w.add(widget)
        w.connect('delete-event',gtk.main_quit)
        w.show()
        gtk.main()
        
    def test_difftable ():
        class FakeRec:
            pass
        test_rec = FakeRec()
        test_rec.title = 'Shloppidy Recipe'
        test_data = {'rating':[4,7],
                     'category':['Dessert','Dessert, Cake'],
                     'cuisine':['American','All-American'],
                     'preptime':[6000,12000],
                     'cooktime':[6543,None]}
        
        t = DiffTable(test_data,test_rec)
        t.show()
        test_in_window(t)
        print t.selected_dic

    def test_merger (rd, conflicts):
        recs = [rd.get_rec(i) for i in conflicts]
        rmerger = RecipeMerger(rd)
        to_fill,conflict_dic = recipeIdentifier.merge_recipes(rd,recs)
        if conflict_dic:
            dt = rmerger.uiMergeRecipes(recs)
            dt.show()
            test_in_window(dt)
            print dt.selected_dic
        elif to_fill:
            print 'Differences in ',conflicts,'can be auto-filled with',to_fill
        else:
            print 'No differences in ',conflicts
    import recipeManager
    rd = recipeManager.default_rec_manager()
    rmd = RecipeMergerDialog(rd)
    rmd.populate_tree()
    rmd.show()
    rmd.glade.get_widget('window1').connect('delete-event',gtk.main_quit)
    gtk.main()
    #dups = rd.find_complete_duplicates()
    #for d in dups[5:]:
    #    test_merger(rd,d)
    
    
        
