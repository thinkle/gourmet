from gourmet.gglobals import FLOAT_REC_ATTRS, INT_REC_ATTRS, REC_ATTR_DIC, REC_ATTRS, doc_base, uibase, imagedir
from gourmet.gdebug import debug
from gourmet.plugin_loader import Pluggable
from gourmet.plugin import RecEditorModule, RecEditorPlugin, ToolPlugin
from gourmet import prefs
from gourmet import Undo
from gourmet.gtk_extras import cb_extras as cb
from gourmet.gtk_extras import dialog_extras as de
from gourmet.gtk_extras.WidgetSaver import WidgetPrefs, WindowSaver
from gourmet.gtk_extras import fix_action_group_importance
from gourmet.gtk_extras import TextBufferMarkup, timeEntry
from gourmet.gtk_extras.mnemonic_manager import MnemonicManager
from gourmet import ImageExtras as ie
from gourmet.models import Ingredient
from gourmet.views.ingredient.tree_ui import IngredientTreeUI, UndoableTreeStuff, add_with_undo
from gourmet.controllers.ingredient import IngredientController
from gourmet import convert, Undo

from index import RecIndex

import gobject
import gtk
import os.path

try:
    from PIL import Image
except ImportError:
    import Image

def find_entry (w):
    if isinstance(w,gtk.Entry):
        return w
    else:
        if not hasattr(w,'get_children'):
            return None
        for child in w.get_children():
            e = find_entry(child)
            if e: return e

# Dialog for adding a recipe as an ingredient
class RecSelector (RecIndex):
    """Select a recipe and add it to RecCard's ingredient list"""
    def __init__(self, recGui, ingEditor):
        self.prefs = prefs.get_prefs()
        self.ui=gtk.Builder()
        self.ui.add_from_file(os.path.join(uibase,'recipe_index.ui'))
        self.rg=recGui
        self.ingEditor = ingEditor
        self.re = self.ingEditor.re
        self.setup_main_window()
        RecIndex.__init__(self,
                          self.ui,
                          self.rg.rd,
                          self.rg,
                          editable=False
                          )
        self.dialog.run()

    def setup_main_window (self):
        d = gtk.Dialog(_("Choose recipe"),
                       self.re.window,
                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.re.conf.append(
            WidgetSaver.WindowSaver(d,
                                    self.prefs.get('recselector',
                                                   {'window_size':(800,600)})
                                    )
            )
        d.set_default_size(*self.prefs.get('recselector')['window_size'])
        self.recipe_index_interface = self.ui.get_object('recipeIndexBox')
        self.recipe_index_interface.unparent()
        d.vbox.add(self.recipe_index_interface)
        d.connect('response',self.response_cb)
        self.recipe_index_interface.show()
        self.dialog = d

    def response_cb (self, dialog, resp):
        if resp==gtk.RESPONSE_ACCEPT:
            self.ok()
        else:
            self.quit()

    def quit (self):
        self.dialog.destroy()

    def rec_tree_select_rec (self, *args):
        self.ok()

    def ok (self,*args):
        debug('ok',0)
        pre_iter=self.ingEditor.ingtree_ui.get_selected_ing()
        try:
            for rec in self.get_selected_recs_from_rec_tree():
                if rec.id == self.re.current_rec.id:
                    de.show_message(label=_("Recipe cannot call itself as an ingredient!"),
                                    sublabel=_('Infinite recursion is not allowed in recipes!')
                                    )
                    continue
                if rec.yields:
                    amount = getYieldSelection(rec,self.re.window)
                else:
                    amount = 1
                ingdic={'amount':amount,
                        'unit':'recipe',
                        'item':rec.title,
                        'refid':rec.id,
                        }
                debug('adding ing: %s'%ingdic,5)
                iter=self.ingEditor.ingtree_ui.ingController.add_ingredient_from_kwargs(
                    group_iter=pre_iter,
                    **ingdic
                    )
                #path=self.reccard.imodel.get_path(iter)
                #self.reccard.ss.add_selection(iter)
            self.quit()
        except:
            de.show_message(label=_("You haven't selected any recipes!"))
            raise

class YieldSelector (de.ModalDialog):

    def __init__ (self, rec, parent=None):
        self.__in_update_from_yield = False
        self.__in_update_from_rec = False
        de.ModalDialog.__init__(
            self,
            okay=True,
            default=1,parent=parent,
            label=_('How much of %(title)s does your recipe call for?')%{'title':rec.title},
            cancel=False
                  )
        self.rec = rec
        table = gtk.Table()
        self.vbox.add(table);
        self.recButton,self.recAdj = self.make_spinny(val=1,lower=0,
                                                      step_incr=0.5,page_incr=5)
        recLabel = gtk.Label(_('Recipes') + ': ')
        self.recAdj.connect('value_changed',self.update_from_rec)
        self.recAdj.connect('changed',self.update_from_rec)
        table.attach(recLabel,0,1,0,1); recLabel.show()
        table.attach(self.recButton,1,2,0,1); self.recButton.show()
        if rec.yields:
            self.yieldsButton,self.yieldsAdj = self.make_spinny(val=self.rec.yields)
            self.yieldsAdj.connect('value_changed',self.update_from_yield)
            self.yieldsAdj.connect('changed',self.update_from_yield)
            yieldsLabel = gtk.Label(rec.yield_unit.title() + ': ')
            table.attach(yieldsLabel,0,1,1,2); yieldsLabel.show()
            table.attach(self.yieldsButton,1,2,1,2);  self.yieldsButton.show()
        table.show()

    def make_spinny (self, val=1, lower=0, upper=10000, step_incr=1, page_incr=10,
                     digits=2):
        '''return adjustment, spinner widget
        '''
        adj = gtk.Adjustment(val,
                             lower=lower,upper=upper,
                             step_incr=step_incr,page_incr=page_incr,
                             )
        sb = gtk.SpinButton(adj)
        sb.set_digits(digits)
        return sb,adj

    def update_from_yield (self, *args):
        if self.__in_update_from_rec: return
        self._in_update_from_yield = True
        yield_val = self.yieldsAdj.get_value()
        factor = yield_val / float(self.rec.yields)
        self.recAdj.set_value(factor)
        self.ret = factor
        self._in_update_from_yield = False

    def update_from_rec (self, *args):
        if self.__in_update_from_yield: return
        self.__in_update_from_rec = True
        factor = self.recAdj.get_value()
        if hasattr(self,'yieldsAdj'):
            self.yieldsAdj.set_value(self.rec.yields * factor)
        self.ret = factor
        self.__in_update_from_rec = False

def getYieldSelection (rec, parent=None):
    '''Given a recipe, return how much of that recipe we want.

    We offer the user the choice to multiply the recipe or change the
    yield amount. We return the factor to multiply the recipe by.

    '''
    yd = YieldSelector(rec,parent)
    try:
        return yd.run()
    except:
        return 1


class RecEditor (WidgetPrefs, Pluggable):

    ui_string = '''
    <ui>
      <menubar name="RecipeEditorMenuBar">
        <menu name="Recipe" action="Recipe">
          <menuitem action="ShowRecipeCard"/>
          <separator/>
          <menuitem action="DeleteRecipe"/>
          <menuitem action="Revert"/>
          <menuitem action="Save"/>
          <separator/>
          <menuitem action="Close"/>
        </menu>
        <menu name="Edit" action="Edit">
          <placeholder name="EditActions"/>
          <separator/>
          <menuitem action="Preferences"/>
        </menu>
        <!--<menu name="Go" action="Go"/>-->
        <menu name="Tools" action="Tools">
        <placeholder name="StandaloneTool">
          <menuitem action="UnitConverter"/>
          </placeholder>
          <separator/>
          <placeholder name="DataTool">          
          </placeholder>
        </menu>
        <menu name="HelpMenu" action="HelpMenu">
          <menuitem action="Help"/>
        </menu>
      </menubar>
      <toolbar name="RecipeEditorToolBar">
        <toolitem action="Save"/>
        <toolitem action="Revert"/>
        <separator/>
        <toolitem action="Undo"/>
        <toolitem action="Redo"/>
        <separator/>
        <toolitem action="ShowRecipeCard"/>
      </toolbar>
      <toolbar name="RecipeEditorEditToolBar"/>
    </ui>
    '''    

    def __init__ (self, reccard, rg, recipe=None, recipe_display=None, new=False):
        self.edited = False
        self.editor_module_classes = [
            DescriptionEditorModule,
            IngredientEditorModule,
            InstructionsEditorModule,
            NotesEditorModule,
            ]
        self.reccard= reccard; self.rg = rg; self.recipe_display = recipe_display
        if self.recipe_display and not recipe:
            recipe = self.recipe_display.current_rec
        self.current_rec = recipe
        self.setup_defaults()
        self.conf = reccard.conf
        self.setup_ui_manager()
        #self.setup_undo()        
        self.setup_main_interface()
        self.setup_modules()
        self.setup_notebook()
        self.page_specific_handlers = []
        #self.setEdited(False)
        # parameters for tracking what has changed
        self.widgets_changed_since_save = {}
        self.new = True
        if recipe and not new:
            #self.updateRecipe(recipe,show=False)
            self.new = False
        elif not recipe:
            recipe = Recipe(title=_('New Recipe'))
        self.set_edited(False)
        Pluggable.__init__(self,[ToolPlugin,RecEditorPlugin])
        self.mm = MnemonicManager()
        self.mm.add_toplevel_widget(self.window)
        self.mm.fix_conflicts_peacefully()        
        self.show()
        self.modules[0].grab_focus()

    def present (self):
        self.window.present()
        self.modules[0].grab_focus()
        
    def setup_defaults (self):
        self.edit_title = _('Edit Recipe:')

    def setup_ui_manager (self):
        self.ui_manager = gtk.UIManager()
        self.ui_manager.add_ui_from_string(self.ui_string)
        self.setup_action_groups()
        fix_action_group_importance(self.mainRecEditActionGroup)
        self.ui_manager.insert_action_group(self.mainRecEditActionGroup,0)
        fix_action_group_importance(self.rg.toolActionGroup)
        self.ui_manager.insert_action_group(self.rg.toolActionGroup,1)

    def setup_action_groups (self):
        self.mainRecEditActionGroup = gtk.ActionGroup('RecEditMain')

        self.mainRecEditActionGroup.add_actions([
            # menus
            ('Recipe',None,_('_Recipe')), 
            ('Edit',None,_('_Edit')),
            ('Help',gtk.STOCK_HELP,None),
            ('HelpMenu',None,_('_Help')),
            ('Save',gtk.STOCK_SAVE,None,
             '<Control>s',_('Save edits to database'),self.save_cb), #saveEdits
            ('DeleteRecipe',gtk.STOCK_DELETE,_('_Delete Recipe'),
             None,None,self.delete_cb),
            ('Revert',gtk.STOCK_REVERT_TO_SAVED,None,
             None,None,self.revert_cb), # revertCB
            ('Close',gtk.STOCK_CLOSE,None,
             None,None,self.close_cb), 
            ('Preferences',gtk.STOCK_PREFERENCES,None,
             None,None,self.preferences_cb), # show_pref_dialog
            ('ShowRecipeCard','recipe-card',_('View Recipe Card'),
             None,None,self.show_recipe_display_cb), #view_recipe_card
            ])

    def setup_modules (self):
        self.modules = []
        self.module_tab_by_name = {}
        for klass in self.editor_module_classes:
            instance = klass(self)
            tab_label = gtk.Label(instance.label)
            n = self.notebook.append_page(
                instance.main,
                tab_label=tab_label)
            self.module_tab_by_name[instance.name] = n
            instance.main.show(); tab_label.show()
            instance.connect('toggle-edited',self.module_edited_cb)
            self.modules.append(instance)

    def add_plugin (self, klass, position=None):
        """Register any external plugins"""
        instance = klass(self)
        if instance.__class__ in self.editor_module_classes: return # these are handled in setup_modules...
        tab_label = gtk.Label(instance.label)
        if not position:
            n = self.notebook.append_page(instance.main,tab_label=tab_label)
        else:
            n = self.notebook.insert_page(instance.main,tab_label=tab_label,position=position)
            # We'll need to reset the other plugin's positions if we shoved one in the middle
            for mod in self.modules[position:]:
                self.module_tab_by_name[mod.name] = self.notebook.page_num(mod.main)
        self.module_tab_by_name[instance.name] = n
        #self.plugins.append(instance)
        if not position:
            self.modules.append(instance)
        else:
            self.modules = self.modules[:position] + [instance] + self.modules[position:]
        instance.main.show(); tab_label.show()
        instance.connect('toggle-edited',self.module_edited_cb)

    def module_edited_cb (self, module, val):
        if val:
            self.set_edited(True)
        else:
            for m in self.modules:
                if m.edited:
                    #print 'Strange,',module,'told us we are not edited, but ',m,'tells us we are...'
                    self.set_edited(True)
                    return
            self.set_edited(False)

    def show_module (self, module_name):
        """Show the part of our interface corresponding with module
        named module_name."""
        if not self.module_tab_by_name.has_key(module_name):
            raise ValueError('RecEditor has no module named %s'%module_name)
        self.notebook.set_current_page(
            self.module_tab_by_name[module_name]
            )

    def setup_main_interface (self):
        self.window = gtk.Window()
        self.window.set_icon_from_file(os.path.join(imagedir,'reccard_edit.png'))
        title = ((self.current_rec and self.current_rec.title) or _('New Recipe')) + ' (%s)'%_('Edit')
        self.window.set_title(title)
        self.window.connect('delete-event',
                            self.close_cb)
        self.conf.append(WindowSaver(self.window,
                                                 self.rg.prefs.get('rec_editor_window',
                                                                   {'window_size':(700,600)})
                                                 )
                         )
        self.window.set_default_size(*prefs.get_prefs().get('rec_editor_window')['window_size'])
        main_vb = gtk.VBox()
        main_vb.pack_start(self.ui_manager.get_widget('/RecipeEditorMenuBar'),expand=False,fill=False)
        main_vb.pack_start(self.ui_manager.get_widget('/RecipeEditorToolBar'),expand=False,fill=False)
        main_vb.pack_start(self.ui_manager.get_widget('/RecipeEditorEditToolBar'),expand=False,fill=False)
        self.notebook = gtk.Notebook(); self.notebook.show()
        main_vb.pack_start(self.notebook)
        self.window.add(main_vb)
        self.window.add_accel_group(self.ui_manager.get_accel_group())
        main_vb.show()

    def show (self):
        self.window.present()

    def setup_notebook (self):
        def hackish_notebook_switcher_handler (*args):
            # because the switch page signal happens before switching...
            # we'll need to look for the switch with an idle call
            gobject.idle_add(self.notebook_change_cb)
        self.notebook.connect('switch-page',hackish_notebook_switcher_handler)
        ## The following workaround was necessary on Windows as long as
        ## https://bugzilla.gnome.org/show_bug.cgi?id=552681
        ## was not fixed, which it is with versions of Gtk+ that ship
        ## with PyGTK 2.24.8
        #if os.name == 'nt' or os.name == 'dos':
        #    self.notebook.set_tab_pos(gtk.POS_TOP)
        #else:
        self.notebook.set_tab_pos(gtk.POS_LEFT)
        self._last_module = None
        self.last_merged_ui = None
        self.last_merged_action_groups = None
        self.notebook_change_cb()

    def set_edited (self, edited):
        self.edited = edited
        if edited:
            self.mainRecEditActionGroup.get_action('Save').set_sensitive(True)
            self.mainRecEditActionGroup.get_action('Revert').set_sensitive(True)            
        else:
            self.mainRecEditActionGroup.get_action('Save').set_sensitive(False)
            self.mainRecEditActionGroup.get_action('Revert').set_sensitive(False)

    def update_from_database (self):
        for mod in self.modules:
            mod.update_from_database()
            mod.__edited = False
            
    def notebook_change_cb (self, *args):
        """Update menus and toolbars"""
        page=self.notebook.get_current_page()
        #self.history.switch_context(page)
        if self.last_merged_ui is not None:
            self.ui_manager.remove_ui(self.last_merged_ui)
            for ag in self.last_merged_action_groups:
                self.ui_manager.remove_action_group(ag)
        self.last_merged_ui = self.ui_manager.add_ui_from_string(self.modules[page].ui_string)
        for ag in self.modules[page].action_groups:
            fix_action_group_importance(ag)
            self.ui_manager.insert_action_group(ag,0)
        self.last_merged_action_groups = self.modules[page].action_groups
        module = self.modules[page]
        if (self._last_module and self._last_module!=module
            and hasattr(self._last_module,'leave_page')
            ):
            self._last_module.leave_page()
        if module:
            if hasattr(module,'enter_page'): module.enter_page()
            self._last_module = module

    def save_cb (self, *args):
        self.widgets_changed_since_save = {}
        self.mainRecEditActionGroup.get_action('ShowRecipeCard').set_sensitive(True)
        self.new = False
        for m in self.modules:
            self.current_rec = m.save(self.current_rec)

        self.reccard.session.commit()
        if self.current_rec.title:
            self.window.set_title("%s %s"%(self.edit_title,self.current_rec.title.strip()))
        self.set_edited(False)
        self.reccard.new = False
        self.reccard.update_recipe(self.current_rec) # update display (if any)
        self.rg.update_go_menu()
        self.rg.rd.save()        

    def revert_cb (self, *args):
        self.update_from_database()
        self.set_edited(False)

    def delete_cb (self, *args):
        self.rg.rec_tree_delete_recs([self.current_rec])

    def close_cb (self, *args):
        if self.edited:
            try:
                save_me = de.getBoolean(
                    title=_("Save changes to %s")%self.current_rec.title,                    
                    label=_("Save changes to %s")%self.current_rec.title,
                    custom_yes=gtk.STOCK_SAVE,
                    )
            except de.UserCancelledError:
                return
            if save_me:
                self.save_cb()
        self.window.hide()
        self.reccard.hide()
        if self.new:
            # If we are new and unedited, delete...
            self.rg.rd.delete_rec(self.current_rec)
            self.rg.redo_search()
        return True

    def preferences_cb (self, *args):
        """Show our preference dialog for the recipe card."""
        self.rg.prefsGui.show_dialog(page=self.rg.prefsGui.CARD_PAGE)        

    def show_recipe_display_cb (self, *args):
        """Show recipe card display (not editor)."""
        self.reccard.show_display()


class IngredientEditorModule (RecEditorModule):

    name = 'ingredients'
    label = _('Ingredients')
    ui_string = '''
      <menubar name="RecipeEditorMenuBar">
        <menu name="Edit" action="Edit">
          <placeholder name="EditActions">
          <menuitem action="AddIngredient"/>
          <menuitem action="DeleteIngredient"/>
          <menuitem action="AddIngredientGroup"/>
          <menuitem action="PasteIngredient"/>
          <separator/>
          <menuitem action="MoveIngredientUp"/>
          <menuitem action="MoveIngredientDown"/>
          <separator/>
          <menuitem action="AddRecipeAsIngredient"/>
          <menuitem action="ImportIngredients"/>
          </placeholder>
        </menu>
      </menubar>
      <toolbar name="RecipeEditorEditToolBar">
        <toolitem action="MoveIngredientUp"/>
        <toolitem action="MoveIngredientDown"/>
        <toolitem action="DeleteIngredient"/>
        <separator/>
        <toolitem  action="AddIngredientGroup"/>
        <toolitem action="AddRecipeAsIngredient"/>
        <separator/>
        <toolitem action="ImportIngredients"/>
        <toolitem action="PasteIngredient"/>
        <separator/>
      </toolbar>
    '''

    def setup (self):
        pass

    def setup_main_interface (self):
        self.ui = gtk.Builder()
        self.ui.add_from_file(os.path.join(uibase,'recCardIngredientsEditor.ui'))
        self.main = self.ui.get_object('ingredientsNotebook')
        self.main.unparent()
        self.ingtree_ui = IngredientTreeUI(self, self.ui.get_object('ingTree'))
        self.setup_action_groups()
        self.update_from_database()
        self.quickEntry = self.ui.get_object('quickIngredientEntry')
        self.ui.connect_signals({'addQuickIngredient':self.quick_add})

    def quick_add (self, *args):
        txt = unicode(self.quickEntry.get_text())
        prev_iter,group_iter = self.ingtree_ui.get_previous_iter_and_group_iter()
        add_with_undo(self,
                      lambda *args: self.add_ingredient_from_line(txt,
                                                                  prev_iter=prev_iter,
                                                                  group_iter=group_iter)
                      )
        self.quickEntry.set_text('')

    def update_from_database (self):
        self.ingtree_ui.set_tree_for_rec(self.current_rec)

    def setup_action_groups (self):
        self.ingredientEditorActionGroup = gtk.ActionGroup('IngredientEditorActionGroup')
        self.ingredientEditorOnRowActionGroup = gtk.ActionGroup('IngredientEditorOnRowActionGroup')        
        self.ingredientEditorActionGroup.add_actions([
            ('AddIngredient',gtk.STOCK_ADD,_('Add ingredient'),
             None,None),
            ('AddIngredientGroup',None,_('Add group'),
             '<Control>G',None,self.ingtree_ui.ingNewGroupCB),
            ('PasteIngredient',gtk.STOCK_PASTE,_('Paste ingredients'),
             '<Control>V',None,self.paste_ingredients_cb),
            ('ImportIngredients',None,_('Import from file'),
             '<Control>O',None,self.import_ingredients_cb),
            ('AddRecipeAsIngredient',None,_('Add _recipe'),
             '<Control>R',_('Add another recipe as an ingredient in this recipe'),
             lambda *args: RecSelector(self.rg, self)),
            ])
        self.ingredientEditorOnRowActionGroup.add_actions([
            ('DeleteIngredient',gtk.STOCK_DELETE,_('Delete'),
             #'Delete', # Binding to the delete key meant delete
             #pressed anywhere would do this, icnluding in a text
             #field
             None, 
             None,self.delete_cb),            
            ('MoveIngredientUp',gtk.STOCK_GO_UP,_('Up'),
             '<Control>Up',None,self.ingtree_ui.ingUpCB),
            ('MoveIngredientDown',gtk.STOCK_GO_DOWN,_('Down'),
             '<Control>Down',None,self.ingtree_ui.ingDownCB),
            ])
        for group in [self.ingredientEditorActionGroup,
                      self.ingredientEditorOnRowActionGroup,
                      ]:
            fix_action_group_importance(group)
        self.action_groups.append(self.ingredientEditorActionGroup)
        self.action_groups.append(self.ingredientEditorOnRowActionGroup)

    def add_ingredient_from_line (self, line, group_iter=None, prev_iter=None):
        """Add an ingredient to our list from a line of plain text"""
        d=self.rg.rd.parse_ingredient(line, conv=self.rg.conv)
        if d == Ingredient():
            d.item = line
            d.amount = None
            d.unit = None
        itr = self.ingtree_ui.ingController.add_ingredient_from_kwargs(prev_iter=prev_iter,group_iter=group_iter,ingredient=d)
        # If there is just one row selected...
        sel = self.ingtree_ui.ingTree.get_selection()
        if sel.count_selected_rows()==1:
            # Then we move our selection down to our current ingredient...
            sel.unselect_all()
            sel.select_iter(itr)
        # Make sure our newly added ingredient is visible...
        self.ingtree_ui.ingTree.scroll_to_cell(
            self.ingtree_ui.ingController.imodel.get_path(itr)
            )
        return itr

    def importIngredients (self, file):
        ifi=file(file,'r')
        for line in ifi:
            self.ingtree_ui.add_ingredient_from_line(line)

    def import_ingredients_cb (self, *args):
        debug('importIngredientsCB',5) #FIXME
        f=de.select_file(_("Choose a file containing your ingredient list."),action=gtk.FILE_CHOOSER_ACTION_OPEN)
        add_with_undo(self, lambda *args: self.importIngredients(f))

    def paste_ingredients_cb (self, *args):
        self.cb = gtk.clipboard_get()
        def add_ings_from_clippy (cb,txt,data):
            if txt:
                def do_add ():
                    for l in txt.split('\n'):
                        if l.strip(): self.add_ingredient_from_line(l)
                add_with_undo(self, lambda *args: do_add())
        self.cb.request_text(add_ings_from_clippy)

    def delete_cb (self, *args):
        debug("delete_cb (self, *args):",5)
        mod,rows = self.ingtree_ui.ingTree.get_selection().get_selected_rows()
        rows.reverse()
        self.ingtree_ui.ingController.delete_iters(*[mod.get_iter(p) for p in rows])


    def save (self, recdic):
        # Save ingredients...
        self.ingtree_ui.ingController.commit_ingredients()
        self.emit('saved')
        return recdic

class TextEditor:

    def setup (self):
        self.edit_widgets = [] # for keeping track of editable widgets
        self.edit_textviews = [] # for keeping track of editable
                                 # textviews

    def setup_action_groups (self):
        self.copyPasteActionGroup = gtk.ActionGroup('CopyPasteActionGroup')
        self.copyPasteActionGroup.add_actions([
            ('Copy',gtk.STOCK_COPY,None,None,None,self.do_copy),
            ('Paste',gtk.STOCK_PASTE,None,None,None,self.do_paste),
            ('Cut',gtk.STOCK_CUT,None,None,None,self.do_cut),            
            ])
        self.cb = gtk.Clipboard()
        gobject.timeout_add(500,self.do_sensitize)
        self.action_groups.append(self.copyPasteActionGroup)

    def do_sensitize (self):
        for w in self.edit_widgets:
            if w.has_focus():
                self.copyPasteActionGroup.get_action('Copy').set_sensitive(
                    w.get_selection_bounds() and True or False
                    )
                self.copyPasteActionGroup.get_action('Cut').set_sensitive(
                    w.get_selection_bounds() and True or False
                    )
                self.copyPasteActionGroup.get_action('Paste').set_sensitive(
                    self.cb.wait_is_text_available() or False
                    )
                return True
        for tv in self.edit_textviews:
            tb = tv.get_buffer()
            self.copyPasteActionGroup.get_action('Copy').set_sensitive(
                tb.get_selection_bounds() and True or False
                )
            self.copyPasteActionGroup.get_action('Cut').set_sensitive(
                tb.get_selection_bounds() and True or False
                )
            self.copyPasteActionGroup.get_action('Paste').set_sensitive(
                self.cb.wait_is_text_available() or False
                )
        return True
        
    def do_copy (self, *args):
        for w in self.edit_widgets:        
            if w.has_focus():
                w.copy_clipboard()
                return
        for tv in self.edit_textviews:
            tv.get_buffer().copy_clipboard(self.cb)

    def do_cut (self, *args):
        for w in self.edit_widgets:        
            if w.has_focus():
                w.cut_clipboard()
        for tv in self.edit_textviews:
            buf  = tv.get_buffer()
            buf.cut_clipboard(self.cb,tv.get_editable())

    def do_paste (self, *args):
        text = self.cb.wait_for_text()
        if self.edit_widgets:
            widget = self.edit_widgets[0]
        else:
            widget = self.edit_textviews[0]
        parent = widget.parent
        while parent and not hasattr(parent,'focus_widget') :
            parent = parent.parent
        widget = parent.focus_widget
        if isinstance(widget,gtk.TextView):
            buf = widget.get_buffer()
            buf.paste_clipboard(self.cb,None,widget.get_editable())
        elif isinstance(widget,gtk.Editable):
            widget.paste_clipboard()
        else:
            print 'What has focus?',widget
        
class DescriptionEditorModule (TextEditor, RecEditorModule):
    name = 'description'
    label = _('Description')
    ui_string = '''
      <menubar name="RecipeEditorMenuBar">
        <menu name="Edit" action="Edit">
          <placeholder name="EditActions">
            <menuitem action="Undo"/>
            <menuitem action="Redo"/>
            <separator/>
            <menuitem action="Cut"/>
            <menuitem action="Copy"/>
            <menuitem action="Paste"/>
          </placeholder>
        </menu>
      </menubar>
      <toolbar name="RecipeEditorToolBar">
        <toolitem action="Cut"/>
        <toolitem action="Copy"/>
        <toolitem action="Paste"/>
      </toolbar>
    '''

    def __init__ (self, *args):
        RecEditorModule.__init__(self, *args)

    def setup_main_interface (self):
        self.ui = gtk.Builder()
        self.ui.add_from_file(os.path.join(uibase,'recCardDescriptionEditor.ui'))
        self.imageBox = ImageBox(self)
        self.init_recipe_widgets()
        # Set up wrapping callbacks...
        self.ui.connect_signals({
            'setRecImage' : self.imageBox.set_from_fileCB,
            'delRecImage' : self.imageBox.removeCB,            
            })
        self.main = self.ui.get_object('descriptionMainWidget')
        self.main.unparent()

    def init_recipe_widgets (self):
        self.rw = {}
        self.entries = []
        self.combos = []

        for a,l,w in REC_ATTRS:
            if w=='Entry': self.entries.append(a)
            elif w=='Combo': self.combos.append(a)
            else: raise Exception("REC_ATTRS widget type %s not recognized" % w)

        for a in self.combos + self.entries:
            self.rw[a]=self.ui.get_object("%sBox"%a)
            try:
                assert(self.rw[a])
            except:
                print 'No recipe editing widget for',a
                raise
            self.edit_widgets.append(self.rw[a])
            self.rw[a].db_prop = a
            # Set up accessibility
            atk = (find_entry(self.rw[a]) or self.rw[a]).get_accessible()
            atk.set_name(REC_ATTR_DIC[a]+' Entry')

        self.update_from_database()

    def update_from_database (self):
        try:
            self.yields = float(self.current_rec.yields)
        except:
            self.yields = None
            if hasattr(self.current_rec,'yields'):
                debug(_("Couldn't make sense of %s as number of yields")%self.current_rec.yields,0)
        for c in self.combos:
            debug("Widget for %s"%c,5)
            model = self.rg.get_attribute_model(c)
            self.rw[c].set_model(model)
            self.rw[c].set_text_column(0)
            cb.setup_completion(self.rw[c])
            val = getattr(self.current_rec,c)
            self.rw[c].entry.set_text(val or "")
            if isinstance(self.rw[c],gtk.ComboBoxEntry):
                Undo.UndoableEntry(self.rw[c].get_child(),self.history)
                cb.FocusFixer(self.rw[c])
            else:
                # we still have to implement undo for regular old comboBoxen!
                1
        for e in self.entries:
            if isinstance(self.rw[e],gtk.SpinButton):
                try:
                    self.rw[e].set_value(float(getattr(self.current_rec,e)))
                except:
                    debug('%s Value %s is not floatable!'%(e,getattr(self.current_rec,e)))
                    self.rw[e].set_text("")
                Undo.UndoableGenericWidget(self.rw[e],self.history, signal='value-changed')
            elif e in INT_REC_ATTRS:
                self.rw[e].set_value(int(getattr(self.current_rec,e) or 0))
                Undo.UndoableGenericWidget(self.rw[e],
                                           self.history)
            else:
                self.rw[e].set_text(getattr(self.current_rec,e) or "")
                Undo.UndoableEntry(self.rw[e],self.history)
        self.imageBox.get_image()

    def grab_focus (self):
        self.ui.get_object('titleBox').grab_focus()
        
    def save (self, recipe):
        for c in self.combos:
            setattr(recipe, c, unicode(self.rw[c].entry.get_text()))
        for e in self.entries:
            if e in INT_REC_ATTRS + FLOAT_REC_ATTRS:
                setattr(recipe, e, self.rw[e].get_value())
            else:
                setattr(recipe, e, unicode(self.rw[e].get_text()))
        if self.imageBox.edited:
            recipe.image, recipe.thumb = self.imageBox.commit()
            self.imageBox.edited=False
        self.emit('saved')
        return recipe

class ImageBox: # used in DescriptionEditor for recipe image.
    def __init__ (self, RecCard):
        debug("__init__ (self, RecCard):",5)
        self.edited = False
        self.rg = RecCard.rg
        self.rc = RecCard
        self.ui = self.rc.ui
        self.imageW = self.ui.get_object('recImage')
        self.addW = self.ui.get_object('addImage')
        self.delW = self.ui.get_object('delImageButton')
        self.image = None

    def get_image (self, rec=None):
        """Set image based on current recipe."""
        debug("get_image (self, rec=None):",5)
        if not rec:
            rec=self.rc.current_rec
        if rec.image:
            try:
                self.set_from_string(rec.image)
            except:
                print 'Problem with image from recipe.'
                print 'Moving ahead anyway.'
                print 'Here is the traceback'
                import traceback; traceback.print_exc()
                print "And for your debugging convenience, I'm dumping"
                print "a copy of the faulty image in /tmp/bad_image.jpg"
                import tempfile
                try:
                    dumpto = os.path.join(tempfile.tempdir,'bad_image.jpg')
                    ofi = file(dumpto,'w')
                    ofi.write(rec.image)
                    ofi.close()
                except:
                    print 'Nevermind -- I had a problem dumping the file.'
                    traceback.print_exc()
                    print '(Ignoring this traceback...)'
        else:
            self.image=None
            self.hide()

    def hide (self):
        debug("hide (self):",5)
        self.imageW.hide()
        self.delW.hide()
        self.addW.show()
        return True

    def commit (self):
        debug("commit (self):",5)
        """Return image and thumbnail data suitable for storage in the database"""
        if self.image:
            self.imageW.show()
            return ie.get_string_from_image(self.image),ie.get_string_from_image(self.thumb)
        else:
            self.imageW.hide()
            return '',''
    
    def draw_image (self):
        debug("draw_image (self):",5)
        """Put image onto widget"""
        if self.image:
            self.win = self.imageW.get_parent_window()
            if self.win:
                wwidth,wheight=self.win.get_size()
                wwidth=int(float(wwidth)/3)
                wheight=int(float(wheight)/3)
            else:
                wwidth,wheight=100,100
            self.image=ie.resize_image(self.image,wwidth,wheight)
            self.thumb=ie.resize_image(self.image,40,40)
            self.set_from_string(ie.get_string_from_image(self.image))
        else:
            self.hide()

    def show_image (self):
        debug("show_image (self):",5)
        """Show widget and switch around buttons sensibly"""
        self.addW.hide()
        self.imageW.show()
        self.delW.show()

    def set_from_string (self, string):
        debug("set_from_string (self, string):",5)
        pb=ie.get_pixbuf_from_jpg(string)
        self.imageW.set_from_pixbuf(pb)
        self.orig_pixbuf = pb
        self.show_image()

    def set_from_file (self, file):
        debug("set_from_file (self, file):",5)
        self.image = Image.open(file)
        self.draw_image()
        
    def set_from_fileCB (self, *args):
        debug("set_from_fileCB (self, *args):",5)
        f=de.select_image("Select Image",action=gtk.FILE_CHOOSER_ACTION_OPEN)
        if f:
            Undo.UndoableObject(
                lambda *args: self.set_from_file(f),
                lambda *args: self.remove_image(),
                self.rc.history,
                widget=self.imageW).perform()
            self.edited=True

    def removeCB (self, *args):
        debug("removeCB (self, *args):",5)
        #if de.getBoolean(label="Are you sure you want to remove this image?",
        #                 parent=self.rc.widget):
        if self.image:
            current_image = ie.get_string_from_image(self.image)
        else:
            current_image = ie.get_string_from_pixbuf(self.orig_pixbuf)
        Undo.UndoableObject(
            lambda *args: self.remove_image(),
            lambda *args: self.set_from_string(current_image),
            self.rc.history,
            widget=self.imageW).perform()

    def remove_image (self):
        self.image=None
        self.orig_pixbuf = None
        self.draw_image()
        self.edited=True


class TextFieldEditor (TextEditor):
    ui_string = '''
      <menubar name="RecipeEditorMenuBar">
        <menu name="Edit" action="Edit">
          <placeholder name="EditActions">
            <menuitem action="Undo"/>
            <menuitem action="Redo"/>
            <separator/>
            <menuitem action="Cut"/>            
            <menuitem action="Copy"/>
            <menuitem action="Paste"/>
            <separator/>
            <menuitem action="Underline"/>
            <menuitem action="Bold"/>
            <menuitem action="Italic"/>
          </placeholder>
        </menu>
      </menubar>
      <toolbar name="RecipeEditorEditToolBar">
        <toolitem action="Underline"/>
        <toolitem action="Bold"/>
        <toolitem action="Italic"/>
        <separator/>
        <toolitem action="Cut"/>        
        <toolitem action="Copy"/>
        <toolitem action="Paste"/>
        <separator/>
      </toolbar>
    '''
    prop = None

    def setup (self): # Text Field Editor
        self.images = [] # For inline images in text fields (future)
        TextEditor.setup(self)

    def setup_action_groups (self):
        TextEditor.setup_action_groups(self)
        self.richTextActionGroup = gtk.ActionGroup('RichTextActionGroup')
        self.richTextActionGroup.add_toggle_actions([
            ('Bold',gtk.STOCK_BOLD,None,'<Control>B',None,None),
            ('Italic',gtk.STOCK_ITALIC,None,'<Control>I',None,None),
            ('Underline',gtk.STOCK_UNDERLINE,None,'<Control>U',None,None),            
            ])
        for action,markup in [('Bold','<b>b</b>'),
                              ('Italic','<i>i</i>'),
                              ('Underline','<u>u</u>')]:
            self.tv.get_buffer().setup_widget_from_pango(
                self.richTextActionGroup.get_action(action),
                markup
                )
        self.action_groups.append(self.richTextActionGroup)

    def setup_main_interface (self):
        self.main = gtk.ScrolledWindow()
        self.main.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.tv = gtk.TextView()
        self.main.add(self.tv)
        buf = TextBufferMarkup.InteractivePangoBuffer()
        self.tv.set_wrap_mode(gtk.WRAP_WORD)
        self.tv.set_buffer(buf)
        self.tv.show()
        self.tv.db_prop = self.prop
        if not self.label:
            print 'Odd,',self,'has no label'
        else:
            atk = self.tv.get_accessible()
            atk.set_name(self.label + ' Text')
        self.update_from_database()
        Undo.UndoableTextView(self.tv,self.history)
        self.setup_action_groups()
        self.edit_textviews = [self.tv]

    def update_from_database (self):
        txt = getattr(self.re.current_rec,self.prop)
        if txt:
            txt = txt.encode('utf8','ignore')
        else:
            txt = "".encode('utf8')
        self.tv.get_buffer().set_text(txt)

    def save (self, recipe):
        setattr(recipe, self.prop, self.tv.get_buffer().get_text())
        self.emit('saved')
        return recipe

class InstructionsEditorModule (TextFieldEditor,RecEditorModule):
    name = 'instructions'
    label = _('Instructions')
    prop = 'instructions'

class NotesEditorModule (TextFieldEditor,RecEditorModule):
    name = 'notes'
    prop = 'modifications'
    label = _('Notes')
