#!/usr/bin/env python
import gc
import gtk.glade, gtk, gobject, os.path, time, os, sys, re, threading, gtk.gdk, Image, StringIO, pango, string
import xml.sax.saxutils, pango
import exporters
import convert, TextBufferMarkup, types
from recindex import RecIndex
import prefs, WidgetSaver, timeEntry, Undo, ratingWidget
import keymanager
import dialog_extras as de
from dialog_extras import show_amount_error
import treeview_extras as te
import cb_extras as cb
import chooserNotebook
import exporters.printer as printer
from gdebug import *
from gglobals import *
from nutrition.nutritionLabel import NutritionLabel
from nutrition.nutrition import NutritionInfoList, NutritionVapor
from gettext import gettext as _
from gettext import ngettext
import ImageExtras as ie
from importers.importer import parse_range
from FauxActionGroups import ActionManager
import mnemonic_manager

import LinkedTextView, timeScanner
from timer import show_timer

class RecRef:
    def __init__ (self, id, title):
        self.refid = id
        self.item = title

class RecCard (WidgetSaver.WidgetPrefs,ActionManager):
    """Our basic recipe card."""

    HIDEABLE_WIDGETS = [
        ('handlebox','Toolbar'),
        #('imageFrame','Image'),
        #('ieHandlebox','Ingredient Editor'),
        #(['servingsLabel','servingsBox','rcMultCheck'],'Servings'),
        (['cuisineLabel','cuisineBox'],'Cuisine'),
        #(['categoryLabel','categoryBox'],'Category'),
        (['preptimeLabel','preptimeBox'],'Preparation Time'),
        (['cooktimeLabel','cooktimeBox'],'Cooking Time'),
        #(['ratingLabel','ratingBox'],'Rating'),
        #(['sourceLabel','sourceBox'],'Source'),
        #(['instrExp'],'Instructions'),
        #(['modExp'],'Modifications'),
        ]

    NOTEBOOK_ATTR_PAGE = 0
    NOTEBOOK_ING_PAGE = 1
    NOTEBOOK_INST_PAGE = 2
    NOTEBOOK_MOD_PAGE = 3

    notebook_pages = {
        NOTEBOOK_ATTR_PAGE:'attributes',
        NOTEBOOK_ING_PAGE:'ingredients',
        NOTEBOOK_INST_PAGE:'instructions',
        NOTEBOOK_MOD_PAGE:'modifications',
        }

    def __init__ (self, RecGui, recipe=None):
        debug("RecCard.__init__ (self, RecGui):",5)
        self.setup_defaults()
        t=TimeAction('RecCard.__init__ 1',0)
        self.mult=1
        self.nutritional_highlighting = False
        self.been_to_nutrition_tab = False
        self.rg = RecGui
        self.prefs = self.rg.prefs
        self.rd = self.rg.rd
        self.nd = self.rg.nd
        self.setup_glade()
        self.ie = IngredientEditor(self.rg, self)
        self.ingtree_ui = IngredientTreeUI(self)        
        self.setup_style()
        self.setup_action_manager()
        self.get_widgets()
        self.register_pref_dialog()
        self.widgets_changed_since_save = {}
        self.history = Undo.MultipleUndoLists(self.undo,self.redo,
                                              get_current_id=self.notebook.get_current_page
                                              )
        self.history.add_action_hook(self.undo_action_callback)
        # Setup notebook page switching...
        def hackish_notebook_switcher_handler (*args):
            # because the switch page signal happens before switching...
            # we'll need to look for the switch with an idle call
            gobject.idle_add(self.notebookChangeCB)
        self.notebook.connect('switch-page',hackish_notebook_switcher_handler)
        # Now set up nutrition notebook switching
        def hackish_notebook_switcher_handler_2 (*args):
            gobject.idle_add(self.nutritionNotebookChangeCB)
        self.nutrition_notebook.connect('switch-page',hackish_notebook_switcher_handler_2)
        self.page_specific_handlers = []
        self.notebookChangeCB()
        self.initRecipeWidgets()
        self.setEdited(False)
        self.images = []
        self.new = True
        if recipe:
            self.updateRecipe(recipe,show=False)
            self.new = False
        else:
            r=self.rg.rd.new_rec()
            self.new = True
            self.updateRecipe(r,show=False)
            # and set our page to the details page
            self.notebook.set_current_page(self.NOTEBOOK_ATTR_PAGE)

        t.end()
        t=TimeAction('RecCard.__init__ 4',0)
        self.pref_id = 'rc%s'%self.current_rec.id
        self.conf = []
        self.conf.append(WidgetSaver.WindowSaver(self.edit_window, self.prefs.get(self.pref_id+'_edit',{})))
        self.conf.append(WidgetSaver.WindowSaver(self.display_window, self.prefs.get(self.pref_id,{})))
        self.connect_signals()
        self.show()
        t.end()

    def setup_glade (self):
        self.makeTimeEntry = lambda *args: timeEntry.makeTimeEntry()
        self.makeStarButton = lambda *args: ratingWidget.make_star_button(self.rg.star_generator)
        self.makeStarImage = lambda *args: ratingWidget.make_star_image(self.rg.star_generator)
        self.makeLinkedTextView = lambda *args: LinkedTextView.LinkedTextView()
        self.makeLinkedTimeView = lambda *args: timeScanner.LinkedTimeView()
        self.makeNutritionLabel = lambda *args: NutritionLabel(self.prefs)
        def custom_handler (glade,func_name,
                            widg, s1,s2,i1,i2):
            f=getattr(self,func_name)
            w= f(s1,s2,i1,i2)
            return w
        gtk.glade.set_custom_handler(custom_handler)
        self.glade = gtk.glade.XML(os.path.join(gladebase,'recCard.glade'))
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.add_glade(self.glade)
        nlb=self.glade.get_widget('nutritionLabel').edit_missing_button.get_child().get_child().get_children()[1]
        self.mm.add_widget_mnemonic(nlb)
        self.mm.fix_conflicts_peacefully()
        # Manually fixing this particular mnemonic for English...
        if nlb.get_text()=='Edit':
            nlb.set_markup_with_mnemonic('Ed_it')

    def connect_signals (self):
        self.glade.signal_autoconnect({
            'rc2shop' : self.addToShopL,
            'rcDelete' : self.delete,
            'rcHide' : self.hide,
            'rcHideEdit' : self.hide_edit,
            'saveEdits': self.saveEditsCB,
            'newRec' : self.newRecipeCB,
            'rcToggleMult' : self.multTogCB,
            'toggleEdit' : self.saveEditsCB,
            'rcSave' : self.saveAs,
            'setRecImage' : self.ImageBox.set_from_fileCB,
            'delRecImage' : self.ImageBox.removeCB,
            'instrAddImage' : self.addInstrImageCB,
            'rcRevert' : self.revertCB,
            'recRef':lambda *args: RecSelector(self.rg,self),
            'unitConverter': self.rg.showConverter,
            'ingKeyEditor': self.rg.showKeyEditor,
            'print': self.print_rec,
            'email': self.email_rec,
            'preferences':self.show_pref_dialog,
            'forget_remembered_optionals':self.forget_remembered_optional_ingredients,
            'show_help': lambda *args: de.show_faq(HELP_FILE,jump_to='Entering and Editing recipes'),
            'edit_details': lambda *args: self.show_edit(tab=self.NOTEBOOK_ATTR_PAGE),
            'edit_ingredients': lambda *args: self.show_edit(tab=self.NOTEBOOK_ING_PAGE),
            'edit_instructions': lambda *args: self.show_edit(tab=self.NOTEBOOK_INST_PAGE),
            'edit_modifications': lambda *args: self.show_edit(tab=self.NOTEBOOK_MOD_PAGE),
            'on_timer': lambda *args: show_timer(),
            })

    def setup_style (self):
        # Do some funky style modifications...
        print 'setup style'
        display_toplevel_widget = self.glade.get_widget('displayPanes')
        new_style = display_toplevel_widget.get_style().copy()
        cmap = display_toplevel_widget.get_colormap()
        new_style.bg[gtk.STATE_NORMAL]= cmap.alloc_color('white')
        new_style.bg[gtk.STATE_INSENSITIVE] = cmap.alloc_color('white')
        new_style.fg[gtk.STATE_NORMAL]= cmap.alloc_color('black')
        new_style.fg[gtk.STATE_INSENSITIVE] = cmap.alloc_color('black')
        def set_style (widg, styl):
            if (not isinstance(widg,gtk.Button) and
                not isinstance(widg,gtk.Entry) and
                not isinstance(widg,gtk.Notebook) and
                not isinstance(widg,gtk.Separator)
                ): widg.set_style(styl)
            if hasattr(widg,'get_children'):
                for c in widg.get_children():
                    set_style(c,styl)
        set_style(display_toplevel_widget,new_style)

    def flow_my_text_on_allocate (self,sw,allocation):
        hadj = sw.get_hadjustment()
        xsize = hadj.page_size
        width = allocation.width
        for widget,perc in self.reflow_on_resize:
            widg_width = int(xsize * perc)
            widget.set_size_request(widg_width,-1)
            t = widget.get_label()
            widget.set_label(t)
        # Flow our image...
        image_width = int(xsize * 0.75)
        if not hasattr(self.ImageBox,'orig_pixbuf') or not self.ImageBox.orig_pixbuf: return
        pb = self.ImageBox.imageD.get_pixbuf()
        iwidth = pb.get_width()
        origwidth = self.ImageBox.orig_pixbuf.get_width()
        new_pb = None
        if iwidth > image_width:
            scale = float(image_width)/iwidth
            width = iwidth * scale
            height = pb.get_height() * scale
            new_pb = self.ImageBox.orig_pixbuf.scale_simple(
                int(width),
                int(height),
                gtk.gdk.INTERP_BILINEAR
                )
        elif (origwidth > iwidth) and (image_width > iwidth):
            if image_width < origwidth:
                scale = float(image_width)/origwidth
                width = image_width
                height = self.ImageBox.orig_pixbuf.get_height() * scale
                new_pb = self.ImageBox.orig_pixbuf.scale_simple(
                    int(width),
                    int(height),
                    gtk.gdk.INTERP_BILINEAR
                    )
            else:
                new_pb = self.ImageBox.orig_pixbuf
        if new_pb:
            del pb
            self.ImageBox.imageD.set_from_pixbuf(new_pb)
        gc.collect()

    def on_card_edit_size_allocate_cb (self,sw,allocation):
        width = allocation.width
        max_col_width = (width*3)/16
        for c in self.ingtree_ui.ingTree.get_columns():
            for rend in c.get_cell_renderers():
                try:
                    rend.get_property('wrap-width')
                except TypeError:
                    pass
                else:
                    rend.set_property('wrap-width',max_col_width)
        self.ingtree_ui.ingTree.queue_draw()
        gobject.timeout_add(100,self.ingtree_ui.ingTree.columns_autosize)

    def setup_defaults (self):
        self.mult = 1
        #self.serves = float(self.serveW.get_text())
        self.edit_title = _('Edit Recipe:')
        self.default_title = _('Recipe Card:')

    def get_widgets (self):
        t=TimeAction('RecCard.get_widgets 1',0)
        self.timeB = self.glade.get_widget('preptimeBox')
        self.nutritionLabel = self.glade.get_widget('nutritionLabel')
        self.nutritionLabel.connect('ingredients-changed',
                                    lambda *args: self.resetIngredients()
                                    )
        self.nutritionLabel.connect('label-changed',self.nutrition_highlighting_label_changed)
        self.display_info = ['title','rating','preptime','link',
                             'servings','cooktime','source',
                             'cuisine','category','instructions',
                             'modifications','ingredients']
        for attr in self.display_info:
            setattr(self,'%sDisplay'%attr,self.glade.get_widget('%sDisplay'%attr))
            setattr(self,'%sDisplayLabel'%attr,self.glade.get_widget('%sDisplayLabel'%attr))
        # Set up wrapping callbacks...
        self.reflow_on_resize = [(getattr(self,'%sDisplay'%s[0]),s[1]) for s in [
            ('title',0.9), # label and percentage of screen it can take up...
            ('cuisine',0.5),
            ('category',0.5),
            ('source',0.5),
            ]
                                 ]
        self.glade.get_widget(
            'recipeDetailsWindow'
            ).connect('size-allocate',self.flow_my_text_on_allocate)
        self.glade.get_widget('recCard').connect('size-allocate',self.on_card_edit_size_allocate_cb)
        self.glade.get_widget('recipeDetailsWindow').set_redraw_on_allocate(True)
        self.servingsDisplaySpin = self.glade.get_widget('servingsDisplaySpin')
        self.servingsDisplaySpin.connect('changed',self.servingsChangeCB)
        self.servingsMultiplyByLabel = self.glade.get_widget('multiplyByLabel')
        self.multiplyDisplaySpin = self.glade.get_widget('multiplyByDisplaySpin')
        self.multiplyDisplaySpin.connect('changed',self.multChangeCB)
        self.multiplyDisplayLabel = self.glade.get_widget('multiplyByDisplayLabel')
        self.ingredientsDisplay.connect('link-activated',
                                        self.show_recipe_link_cb)
        self.ingredientsDisplay.set_wrap_mode(gtk.WRAP_WORD)
        for d in ['instructionsDisplay','modificationsDisplay']:
            disp = getattr(self,d)
            disp.set_wrap_mode(gtk.WRAP_WORD)
            disp.set_editable(False)
            disp.connect('time-link-activated',
                         timeScanner.show_timer_cb,
                         self.rg.conv
                         )
        self.special_display_functions = {
            'servings':self.updateServingsDisplay,
            'ingredients':self.updateIngredientsDisplay,
            'title':self.updateTitleDisplay,
            'link':self.updateLinkDisplay,
            }
        WidgetSaver.WidgetPrefs.__init__(
            self,
            self.prefs,
            glade=self.glade,
            hideable_widgets=self.HIDEABLE_WIDGETS,
            basename='rc_hide_')
        self.ImageBox = ImageBox(self)
        self.rg.sl.sh.init_orgdic()        
        #self.serveW = self.glade.get_widget('servingsBox')
        #self.multCheckB = self.glade.get_widget('rcMultCheck')
        self.multLabel = self.glade.get_widget('multLabel')
        self.linkDisplayButton = self.glade.get_widget('linkDisplayButton')
        self.linkDisplayButton.connect('clicked',self.link_cb)
        self.edit_window = self.widget = self.glade.get_widget('recCard')
        self.display_window = self.glade.get_widget('recCardDisplay')
        self.edit_window.set_transient_for(self.display_window)
        self.stat = self.glade.get_widget('statusbar1')
        self.contid = self.stat.get_context_id('main')
        self.toggleReadableMenu = self.glade.get_widget('toggle_readable_units_menuitem')
        self.toggleReadableMenu.set_active(self.prefs.get('readableUnits',True))
        self.toggleReadableMenu.connect('toggled',self.readableUnitsCB)
        # this hook won't spark an infinite loop since the 'toggled' signal is only emitted
        # for a *change*
        def toggle_readable_hook (p,v):
            if p=='readableUnits': self.toggleReadableMenu.set_active(v)
        self.rg.prefs.set_hooks.append(toggle_readable_hook)
        self.notebook=self.glade.get_widget('editNotebook')
        self.tree_control = self.glade.get_widget('ChooserTreeView')
        cn = chooserNotebook.ChooserNotebook(self.tree_control,self.notebook)
        self.nutrition_notebook = self.glade.get_widget('nutritionNotebook')        
        t.end()
        
    def setup_action_manager(self):
        ActionManager.__init__(
            self,self.glade,
            # action groups
            {'ingredientGroup':[{'ingAdd':[{'label':_('Add _ingredient'),
                                            'stock-id':gtk.STOCK_ADD,
                                            'tooltip':_('Add new ingredient to the list.'),
                                            'separators':'ingSeparator'},
                                           ['ingAddMenu']]},
                                {'ingGroup':[{'tooltip':_('Create new subgroup of ingredients.'),},
                                             ['ingNewGroupButton','ingNewGroupMenu']]},
                                {'ingImport':[{'tooltip':_('Import list of ingredients from text file.'),
                                               'separators':'ingSeparator3'
                                               },
                                              ['ingImportListButton','ingImportListMenu'],
                                              ]
                                 },
                                {'ingPaste':[{'tooltip':_('Paste list of ingredients from clipboard.')},
                                             ['pasteIngredientButton','pasteIngredientMenu']]
                                 },
                                {'ingRecRef':[{'tooltip':_('Add another recipe as an "ingredient" in the current recipe.'),
                                               'separators':'ingSeparator3'
                                               },
                                              ['ingRecRefButton','ingRecRefMenu']]},
                                #{'ingSeparators':[{'label':None,'stock-id':None,'tooltip':None},['ingSeparator','ingSeparator2']]}
                                ],
             'selectedIngredientGroup':[{'ingDel':[{'tooltip':_('Delete selected ingredient')},
                                                   ['ingDelButton','ingDelMenu']]},
                                        {'ingUp':[{'tooltip':_('Move selected ingredient up.'),
                                                   'separators':'ingSeparator2'},
                                                  ['ingUpButton','ingUpMenu']]},
                                        {'ingDown':[{'tooltip':_('Move selected ingredient down.')},
                                                    ['ingDownButton','ingDownMenu']]},
                                        ],
             'editTextItems':[{p: [{'separators':'formatSeparator'},
                                   ['%sButton'%p,'%sButton2'%p,'%sMenu'%p]]} for p in 'bold','italic','underline'],
             'genericEdit':[{'copy':[{},['copyButton','copyButton2','copyMenu']]},
                            {'paste':[{'separators':'copySeparator'},['pasteButton','pasteButton2','pasteMenu',]]},
                            ],
             'undoButtons':[{'undo':[{},['undoButton','undoMenu']]},
                            {'redo':[{},['redoButton','redoMenu']]},
                            ],
             #'editButtons':[{'edit':[{'tooltip':_("Toggle whether we're editing the recipe card")},
             #                        ['editButton','editMenu']]},
             #               ],
             'viewRecipeCardButtons':[{'view':[{'tooltip':_('View recipe card for current recipe')},
                                               ['viewRecipeCardButton','view_recipe_card_menuitem']]},
                                      ],
             'saveButtons':[{'save':[{},['saveButton','saveMenu']]},
                            {'revert':[{},['revertButton','revertMenu'],]},]
             },
            # callbacks
            [('ingUp',self.ingtree_ui.ingUpCB),
             ('ingDown',self.ingtree_ui.ingDownCB),
             ('ingAdd',self.ie.new),
             ('ingDel',self.ie.delete_cb),
             ('ingGroup',self.ingtree_ui.ingNewGroupCB),
             ('ingImport',self.importIngredientsCB),
             ('ingPaste',self.pasteIngsCB),
             ('view',self.viewCB),
             #('edit',self.editCB),
             ]
            )
        self.notebook_page_actions = {'ingredients':['ingredientGroup','selectedIngredientGroup'],
                                      'instructions':['editTextItems'],
                                      'modifications':['editTextItems'],
                                      }
        # for editText stuff is not yet implemented!
        # it appears it will be quite a pain to implement as well, alas!
        # see bug 59390: http://bugzilla.gnome.org/show_bug.cgi?id=59390
        #self.editTextItems.set_visible(False)
        self.genericEdit.set_visible(False)
        import sets
        self.notebook_changeable_actions = sets.Set()
        for aa in self.notebook_page_actions.values():
            for a in aa:
                self.notebook_changeable_actions.add(a)

    def register_pref_dialog (self, *args):
        """Add our GUI prefs to the preference dialog."""
        options = self.make_option_list()
        if hasattr(self.rg,'rec_apply_list'):
            self.rg.rec_apply_list.append(self.apply_option)
        else:
            # make a list of open reccard's "apply" functions
            self.rg.rec_apply_list = [self.apply_option]
            # make a function to call these apply functions for each open item
            self.rg.apply_rec_options = lambda *args: [cb(*args) for cb in self.rg.rec_apply_list]
            self.rg.prefsGui.add_pref_table(options,
                                            'cardViewVBox',
                                            self.rg.apply_rec_options
                                            )
        
    def show_pref_dialog (self, *args):
        """Show our preference dialog for the recipe card."""
        self.rg.prefsGui.show_dialog(page=self.rg.prefsGui.CARD_PAGE)

    def notebookChangeCB (self, *args):
        page=self.notebook.get_current_page()
        self.history.switch_context(page)
        while self.page_specific_handlers:
            w,s = self.page_specific_handlers.pop()
            if w.handler_is_connected(s):
                w.disconnect(s)
        debug('notebook changed to page: %s'%page,3)
        if self.notebook_pages.has_key(page):
            page=self.notebook_pages[page]
        else:
            debug('WTF, %s not in %s'%(page,self.notebook_pages),1)
        debug('notebook on page: %s'%page,3)
        for actionGroup in self.notebook_changeable_actions:
            if self.notebook_page_actions.has_key(page):
                getattr(self,actionGroup).set_visible(actionGroup in self.notebook_page_actions[page])
                if not actionGroup in self.notebook_page_actions[page]: debug('hiding actionGroup %s'%actionGroup,3)
                if actionGroup in self.notebook_page_actions[page]: debug('showing actionGroup %s'%actionGroup,3)
            else:
                getattr(self,actionGroup).set_visible(False)
        if 'instructions'==page:
            buf = self.rw['instructions'].get_buffer()
            c1=buf.setup_widget_from_pango(self.bold, '<b>bold</b>')
            c2=buf.setup_widget_from_pango(self.italic, '<i>ital</i>')
            c3=buf.setup_widget_from_pango(self.underline, '<u>underline</u>')
            self.page_specific_handlers = [(buf,c1),(buf,c2),(buf,c3)]
        if 'modifications'==page:
            buf = self.rw['modifications'].get_buffer()
            c1=buf.setup_widget_from_pango(self.bold, '<b>bold</b>')
            c2=buf.setup_widget_from_pango(self.italic, '<i>ital</i>')
            c3=buf.setup_widget_from_pango(self.underline, '<u>underline</u>')
            self.page_specific_handlers = [(buf,c1),(buf,c2),(buf,c3)]

    def nutritionNotebookChangeCB (self):
        page = self.nutrition_notebook.get_current_page()
        current_state = self.nutritional_highlighting
        if page == 0: # page 0 = normal display page
            self.nutritional_highlighting = False
        else:
            self.nutritional_highlighting = True
        if not self.been_to_nutrition_tab:
            highlight = self.prefs.get('nutrition_to_highlight','kcal')
            if highlight:
                self.nutritionLabel.toggles[highlight].activate()
        if current_state != self.nutritional_highlighting:
            # If we've changed, redraw our ingredient info
            self.updateIngredientsDisplay()
        self.been_to_nutrition_tab = True

    def nutrition_highlighting_label_changed (self, nl):
        self.nutritional_highlighting = True
        self.prefs['nutrition_to_highlight'] = self.nutritionLabel.active_name
        self.updateIngredientsDisplay()

    def multTogCB (self, w, *args):
        debug("multTogCB (self, w, *args):",5)
        return
        if not self.multCheckB.get_active():
            old_mult = self.mult
            self.mult = 1
            self.multLabel.set_text("")
            if old_mult != self.mult:
                self.serveW.set_value(float(self.serves_orig))
        
    def modTogCB (self, w, *args):
        debug("modTogCB (self, w, *args):",5)
        if w.get_active():
            self.rw['modifications'].show()
        else:
            self.rw['modifications'].hide()

    def show_recipe_link_cb (self, widg, link):
        rid,rname = link.split(':')
        rec = self.rg.rd.get_rec(int(rid))
        if not rec:
            rec = self.rg.rd.fetch_one(
                self.rg.rd.rview,
                title=rname
                )
        if rec:
            self.rg.openRecCard(rec)
        else:
            de.show_message(parent=self.display_window,
                            label=_('Unable to find recipe %s in database.')%rname
                            )
            
    def instrTogCB (self, w, *args):
        debug("instrTogCB (self, w, *args):",5)
        if w.get_active():
            self.rw['instructions'].show()
        else:
            self.rw['instructions'].hide()

    def readableUnitsCB (self, widget):
        if widget.get_active():
            self.prefs['readableUnits']=True
            self.resetIngList()
        else:
            self.prefs['readableUnits']=False
            self.resetIngList()

    def addInstrImage (self, file):
        debug("addInstrImage (self, file):",5)
        w = self.rw['instructions']
        i = gtk.Image()
        i.set_from_file(file)
        pb=i.get_pixbuf()
        i=None
        b=w.get_buffer()
        iter=b.get_iter_at_offset(0)
        anchor = b.create_child_anchor(iter)
        self.images.append((anchor,pb))
        b.insert_pixbuf(iter,pb)

    def addInstrImageCB (self, *args):
        debug("addInstrImageCB (self, *args):",5)
        f = de.select_file(_("Choose an image to insert in instructions..."),action=gtk.FILE_CHOOSER_ACTION_OPEN)
        self.addInstrImage(f)

    def saveEditsCB (self, click=None, click2=None, click3=None):
        debug("saveEditsCB (self, click=None, click2=None, click3=None):",5)
        self.rg.message("Committing edits!")
        self.setEdited(False)
        self.widgets_changed_since_save =  {}
        self.view.set_sensitive(True)        
        self.new = False
        newdict = {'id': self.current_rec.id}
        for c in self.reccom:
            newdict[c]=self.rw[c].entry.get_text()
        for e in self.recent:
            if e in INT_REC_ATTRS: newdict[e]=self.rw[e].get_value()
            else: newdict[e]=self.rw[e].get_text()
        for t in self.rectexts:
            buf = self.rw[t].get_buffer()
            newdict[t]=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if self.ImageBox.edited:
            newdict['image'],newdict['thumb']=self.ImageBox.commit()
            self.ImageBox.edited=False
        debug("modify_rec, newdict=%s"%newdict,1)
        self.current_rec = self.rg.rd.modify_rec(self.current_rec,newdict)
        ## if our title has changed, we need to update menus
        self.updateRecDisplay()
        self.rg.rmodel.update_recipe(self.current_rec)
        self.ingtree_ui.ingController.commit_ingredients()
        self.resetIngredients()
        # Update hashes for tracking unique recipes...
        self.rg.rd.update_hashes(self.current_rec)
        # save DB for metakit
        self.rg.rd.save()
        if newdict.has_key('title'):
            self.edit_window.set_title("%s %s"%(self.edit_title,self.current_rec.title.strip()))
            self.display_window.set_title("%s %s"%(self.default_title,self.current_rec.title.strip()))
            self.rg.updateViewMenu()
        
    def delete (self, *args):
        debug("delete (self, *args):",2)
        self.rg.recTreeDeleteRecs([self.current_rec])
        debug("delete finished",2)
    
    def addToShopL (self, *args):
        debug("addToShopL (self, *args):",5)
        import shopgui
        d = shopgui.getOptionalIngDic(self.rg.rd.get_ings(self.current_rec),
                                      self.mult,
                                      self.prefs,
                                      self.rg)
        self.rg.sl.addRec(self.current_rec,self.mult,d)
        self.rg.sl.show()

    def servingsChangeCB (self, widg):
        val=widg.get_value()
        self.updateServingMultiplierLabel(val)
        self.updateIngredientsDisplay()

    def multChangeCB (self, widg):
        self.mult=widg.get_value()
        self.updateIngredientsDisplay()
        
    def initRecipeWidgets (self):
        debug("initRecipeWidgets (self):",5)
        self.rw = {}
        self.recent = []
        self.reccom = []        
        for a,l,w in REC_ATTRS:
            if w=='Entry': self.recent.append(a)
            elif w=='Combo': self.reccom.append(a)
            else: raise "REC_ATTRS widget type %s not recognized"%w
        self.rectexts = ['instructions', 'modifications']
        for a in self.reccom:
            self.rw[a]=self.glade.get_widget("%sBox"%a)
            self.rw[a].get_children()[0].connect('changed',self.changedCB)
        for a in self.recent:
            self.rw[a]=self.glade.get_widget("%sBox"%a)
            self.rw[a].connect('changed',self.changedCB)
        for t in self.rectexts:
            self.rw[t]=self.glade.get_widget("%sText"%t)
            buf = TextBufferMarkup.InteractivePangoBuffer()
            self.rw[t].set_buffer(buf)
            buf.connect('changed',self.changedCB)        

    def newRecipeCB (self, *args):
        debug("newRecipeCB (self, *args):",5)
        self.rg.newRecCard()

    def resetIngList (self):
        debug("resetIngList (self, rec=None):",0)
        self.ing_alist = None
        self.ingtree_ui.set_tree_for_rec(self.current_rec)
        self.updateIngredientsDisplay()

    def updateAttribute (self, attr, value):
        """Update our recipe card to reflect attribute:value.

        We assume the attribute has already been set for the recipe.
        This function is meant to make us properly reflect external
        changes."""
        if self.rw.has_key(attr):
            if attr in self.reccom: self.rw[attr].entry.set_text(value)
            elif attr in INT_REC_ATTRS: self.rw[attr].entry.set_value(value)
            elif attr in self.recent: self.rw[attr].set_text(value)
            elif attr in self.rectexts: self.rw[attr].get_buffer().set_text(value)
            # update title if necessary
            if attr=='title':
                self.edit_window.set_title(value)
        self.updateRecDisplay()
            
    def updateRecipe (self, rec, show=True):
        """Update our recipe."""
        # The real work is done in UpdateRec -- we just add a check
        # that allows us to properly handle recipes as integer IDs or
        # as objects and that asks the user if they want to abandon
        # edits before getting the new recipe
        debug("updateRecipe (self, rec):",0)
        if type(rec) == int:
            rec=self.rg.rd.fetch_one(self.rg.rd.rview,id=rec)
        if not self.edited or de.getBoolean(parent=self.edit_window,
                                            label=_("Abandon your edits to %s?")%self.current_rec.title):
            self.updateRec(rec)
            if show:
                import traceback; traceback.print_exc()
                self.show()

    def revertCB (self, *args):
        if de.getBoolean(parent=self.edit_window,
                         label=_("Are you sure you want to abandon your changes?"),
                         cancel=False):
            self.updateRec(self.current_rec)

    def updateRec (self, rec):
        debug("updateRec (self, rec):",5)
        """If handed an ID, we'll grab the rec"""
        if not hasattr(rec,'id'):
            rec=self.rg.rd.get_rec(rec)
        self.current_rec = rec
        try:
            self.serves_orig = float(self.current_rec.servings)
        except:
            self.serves_orig = None
            if hasattr(self.current_rec,'servings'):
                debug(_("Couldn't make sense of %s as number of servings")%self.current_rec.servings,0)        
        self.serves = self.serves_orig
        #self.servingsChange()
        self.resetIngredients()
        self.updateRecDisplay()
        for c in self.reccom:
            debug("Widget for %s"%c,5)
            if c=='category':
                slist = self.rg.rd.get_unique_values(c,self.rg.rd.catview)
            else:
                slist = self.rg.rd.get_unique_values(c,deleted=False)
            if not slist:
                slist = self.rg.rd.get_default_values(c)
            else:
                for default_value in self.rg.rd.get_default_values(c):
                    if default_value not in slist: slist.append(default_value)
            slist.sort()
            cb.set_model_from_list(self.rw[c],slist)
            cb.setup_completion(self.rw[c])
            if c=='category':
                val = ', '.join(self.rg.rd.get_cats(rec))
            else:
                val = getattr(rec,c)
            self.rw[c].entry.set_text(val or "")
            if isinstance(self.rw[c],gtk.ComboBoxEntry):
                Undo.UndoableEntry(self.rw[c].get_child(),self.history)
                cb.FocusFixer(self.rw[c])
            else:
                # we still have to implement undo for regular old comboBoxen!
                1
        for e in self.recent:
            if isinstance(self.rw[e],gtk.SpinButton):
                try:
                    self.rw[e].set_value(float(getattr(rec,e)))
                except:
                    debug('%s Value %s is not floatable!'%(e,getattr(rec,e)))
                    self.rw[e].set_text("")
                Undo.UndoableGenericWidget(self.rw[e],self.history)
            elif e in INT_REC_ATTRS:
                self.rw[e].set_value(int(getattr(rec,e) or 0))
                Undo.UndoableGenericWidget(self.rw[e],
                                           self.history)
            else:
                self.rw[e].set_text(getattr(rec,e) or "")
                Undo.UndoableEntry(self.rw[e],self.history)    
        for t in self.rectexts:
            w=self.rw[t]
            b=w.get_buffer()
            try:
                #txt=unicode(getattr(rec,t))
                txt = getattr(rec,t)
                if txt:
                    txt = txt.encode('utf8','ignore')
                else:
                    txt = "".encode('utf8')
                #txt = getattr(rec,t).decode()
            except UnicodeDecodeError:
                txt = getattr(rec,t)
                debug('UnicodeDecodeError... trying to force our way foreward',0)
                debug('We may fail to display this: %s'%txt,0)
                debug('Type = %s'%type(txt),0)
                raise
            b.set_text(txt)
            Undo.UndoableTextView(w,self.history)
        #self.servingsChange()
        self.ImageBox.get_image()
        self.ImageBox.edited=False
        self.setEdited(False)
                
    def undoableWidget (self, widget, signal='changed',
                        get_text_cb='get_text',set_text_cb='set_text'):
        if type(get_text_cb)==str: get_text_cb=getattr(widget,get_text_cb)
        if type(set_text_cb)==str: set_text_cb=getattr(widget,set_text_cb)
        txt=get_text_cb()
        utc = Undo.UndoableTextChange(set_text_cb,
                                      self.history,
                                      initial_text=txt,
                                      text=txt)
        def change_cb (*args):
            newtxt=get_text_cb()
            utc.add_text(newtxt)
        widget.connect(signal,change_cb)

    def updateRecDisplay (self):
        """Update the 'display' portion of the recipe card."""
        self.update_nutrition_info()
        for attr in self.display_info:
            if  self.special_display_functions.has_key(attr):
                debug('calling special_display_function for %s'%attr,0)
                self.special_display_functions[attr]()
            else:
                widg=getattr(self,'%sDisplay'%attr)
                widgLab=getattr(self,'%sDisplayLabel'%attr)
                if not widg or not widgLab:
                    raise 'There is no widget or label for  %s=%s, %s=%s'%(attr,widg,'label',widgLab)
                if attr=='category':
                    attval = ', '.join(self.rg.rd.get_cats(self.current_rec))
                else:
                    attval = getattr(self.current_rec,attr)
                if attval:
                    debug('showing attribute %s = %s'%(attr,attval),0)
                    if attr in INT_REC_ATTRS:
                        if attr=='rating': widg.set_value(attval)
                        elif attr in ['preptime','cooktime']:
                            widg.set_text(convert.seconds_to_timestring(attval))
                    else:
                        widg.set_text(attval)
                        #if attr in ['modifications',#'instructions'
                        #            ]:
                        #    widg.set_use_markup(True)
                        #    widg.set_size_request(600,-1)
                    widg.show()
                    widgLab.show()
                else:
                    debug('hiding attribute %s'%attr,0)
                    widg.hide()
                    widgLab.hide()

    def list_all_ings (self, rec):
        """Return a list of ingredients suitable for nutritional
        lookup, including all optional items and ingredients contained
        in recipe-as-ingredient items.
        """
        ings = self.rd.get_ings(rec)
        ret = []
        for i in ings:
            if hasattr(i,'refid') and i.refid:
                subrec = self.rd.get_referenced_rec(i)
                if not subrec:
                    raise "WTF! Can't find ",i.refid
                ret.extend(self.list_all_ings(subrec))
                continue
            else:
                ret.append(i)
        return ret

    def update_nutrition_info (self):
        """Update nutritional information for ingredient list."""
        if self.current_rec.servings:
            self.nutritionLabel.set_servings(
                convert.frac_to_float(self.current_rec.servings)
                )
        #ings = self.list_all_ings(self.current_rec)
        nutritional_info_list = []
        if not self.ing_alist:
            self.create_ing_alist()
        for g,ings in self.ing_alist:
            nutritional_info_list.append(
                self.rg.nd.get_nutinfo_for_inglist(ings,self.rd)
                )
        self.nutinfo = NutritionInfoList(nutritional_info_list)
        self.nutritionLabel.set_nutinfo(self.nutinfo)
        self.nutritionLabel.rec = self.current_rec

    def updateTitleDisplay (self):
        titl = self.current_rec.title
        if not titl: titl="Unitled"
        titl = "<b><big>" + xml.sax.saxutils.escape(titl) + "</big></b>"
        self.titleDisplay.set_label(titl)

    def updateServingsDisplay (self, serves=None):
        self.serves_orig=self.current_rec.servings
        try:
            self.serves_orig = float(self.serves_orig)
        except:
            self.serves_orig = None
        if self.serves_orig:
            # in this case, display servings spinbutton and update multiplier label as necessary
            self.servingsDisplay.show()
            self.servingsDisplayLabel.show()
            self.multiplyDisplaySpin.hide()
            self.multiplyDisplayLabel.hide()
            if serves:
                self.mult = float(serves)/float(self.serves_orig)
            else:
                self.mult = 1
                serves=float(self.serves_orig)
            self.servingsDisplaySpin.set_value(serves)
        else:
            #otherwise, display multiplier label and checkbutton
            self.servingsDisplay.hide()
            self.servingsDisplayLabel.hide()
            self.multiplyDisplayLabel.show()
            self.multiplyDisplaySpin.show()

    def updateLinkDisplay (self):
        if self.current_rec.link:
            self.linkDisplayButton.show()
            self.linkDisplay.set_markup(
                '<span underline="single" color="blue">%s</span>'%self.current_rec.link
                )
            self.link = self.current_rec.link
        else:
            self.link = ''
            self.linkDisplayButton.hide()

    def link_cb (self, *args): launch_url(self.link)

    def updateServingMultiplierLabel (self,*args):
        serves = self.servingsDisplaySpin.get_value()
        if float(serves) != self.serves_orig:
            self.mult = float(serves)/self.serves_orig
        else:
            self.mult = 1
        if self.mult != 1:
            self.servingsMultiplyByLabel.set_text("x %s"%convert.float_to_frac(self.mult))
        else:
            self.servingsMultiplyByLabel.set_label("")
    
    def create_ing_alist (self):
        """Create alist ing_alist based on ingredients in DB for current_rec"""
        ings=self.rg.rd.get_ings(self.current_rec)
        self.ing_alist = self.rg.rd.order_ings(ings)
        debug('self.ing_alist updated: %s'%self.ing_alist,1)

    def forget_remembered_optional_ingredients (self, *args):
        if de.getBoolean(parent=self.edit_window,
                         label=_('Forget which optional ingredients to shop for?'),
                         sublabel=_('Forget previously saved choices for which optional ingredients to shop for. This action is not reversable.'),
                         custom_yes=gtk.STOCK_OK,
                         custom_no=gtk.STOCK_CANCEL,
                         cancel=False):
            debug('Clearing remembered optional ingredients.',0)
            self.rg.rd.clear_remembered_optional_ings(self.current_rec)

    def resetIngredients (self):
        """Reset our display of ingredients based on what's in our database at present."""
        # Our basic ingredient list...
        self.create_ing_alist()
        self.update_nutrition_info()
        # Our ingredient card display
        self.updateIngredientsDisplay()
        # Reset our treeview in our editor window
        self.resetIngList()
        

    def updateIngredientsDisplay (self):
        """Update our display of ingredients, only reloading from DB if this is our first time.
        """
        if not self.ing_alist:
            self.create_ing_alist()
        group_strings = []
        group_index = 0
        nut_highlighted = False
        for g,ings in self.ing_alist:
            labels = []
            if g: labels.append("<u>%s</u>"%xml.sax.saxutils.escape(g))
            ing_index = 0
            for i in ings:
                ing_strs = []
                if self.nutritional_highlighting and self.serves_orig:
                    amt,unit = self.rg.rd.get_amount_and_unit(i,mult = 1.0/self.serves_orig)
                else:
                    amt,unit = self.rg.rd.get_amount_and_unit(i,
                                                              mult=self.mult,
                                                              conv=self.rg.conv
                                                              )
                if amt: ing_strs.append(amt)
                if unit: ing_strs.append(unit)
                if i.item: ing_strs.append(i.item)
                if (type(i.optional)!=str and i.optional) or i.optional=='yes': 
                    ing_strs.append(_('(Optional)'))
                color = None; weight = None
                if self.nutritional_highlighting and self.nutritionLabel.active_name:
                    props = self.nutritionLabel.active_properties
                    if type(props)==str:
                        nut_amt = getattr(self.nutinfo[group_index][ing_index],props)
                        tot_amt = getattr(self.nutinfo,props)
                    else:
                        nut_amt = sum([getattr(self.nutinfo[group_index][ing_index],p) or 0 for p in props])
                        tot_amt = sum([getattr(self.nutinfo,p) or 0 for p in props])
                    if nut_amt:
                        perc = float(nut_amt)/tot_amt
                        if self.serves_orig: nut_amt = nut_amt/self.serves_orig
                        label = self.nutritionLabel.active_unit
                        if not self.nutritionLabel.active_unit:
                            label = self.nutritionLabel.active_label.lower()
                        if int(nut_amt) or (nut_amt==int(nut_amt)):
                            nut_amt = "%i"%nut_amt
                        else:
                            nut_amt = "%.2f"%nut_amt
                        ing_strs.append('(%s %s)'%(nut_amt,label))
                        color = "#%02x%02x%02x"%(255,255,
                                                 180-int(180*perc)
                                                )
                        nut_highlighted = True
                        weight = int(pango.WEIGHT_NORMAL + ((pango.WEIGHT_HEAVY - pango.WEIGHT_NORMAL) * perc))
                istr = xml.sax.saxutils.escape(' '.join(ing_strs))
                if i.refid:
                    labels.append('<a href="%s:%s">'%(i.refid,
                                        xml.sax.saxutils.escape(i.item)
                                        )\
                                  +istr+'</a>')
                else:
                    labels.append(
                        xml.sax.saxutils.escape(istr)
                        )
                if color:
                    labels[-1] = '<span background="%s" foreground="black">'%color+labels[-1]+'</span>'
                if weight:
                    labels[-1] = '<span weight="%i">'%weight+labels[-1]+'</span>'
                if (self.nutritional_highlighting
                    and
                    isinstance(self.nutinfo[group_index][ing_index],
                               NutritionVapor)):
                    labels[-1] = '<span foreground="red">'+labels[-1]+'</span>'
                ing_index += 1
            group_strings.append('\n'.join(labels))
            group_index += 1
        label = '\n\n'.join(group_strings)
        if nut_highlighted:
            label = '<i>Highlighting amount of %s in each ingredient.</i>\n'%self.nutritionLabel.active_label+label
        if label:
            self.ingredientsDisplay.set_text(label)
            self.ingredientsDisplay.set_editable(False)
            self.ingredientsDisplay.show()
            self.ingredientsDisplayLabel.show()
        else:
            self.ingredientsDisplay.hide()
            self.ingredientsDisplayLabel.hide()        

    def showIngredientChange (self, ref, d):
        if not ref.valid():
            self.resetIngredients()
            return
        iter = ref.get_model().get_iter(ref.get_path())
        ## COLUMN NUMBER FOR Shopping Category==6
        d=d.copy()
        # we hackishly muck up the dictionary so that the 'amount' field
        # becomes the proper display amount.
        if d.has_key('amount'):
            d['amount']=convert.float_to_frac(d['amount'])
        if d.has_key('rangeamount'):
            if d['rangeamount']:
                d['amount']=d['amount']+'-'+convert.float_to_frac(d['rangeamount'])
            del d['rangeamount']
        #self.resetIngredients()
        if d.has_key('ingkey'):
            ## if the key has been changed and the shopping category is not set...
            shopval = self.imodel.get_value(iter,6)
            debug('Shopping Category value was %s'%shopval,4)
            if shopval:
                self.rg.sl.orgdic[d['ingkey']]=shopval
            else:
                if self.rg.sl.orgdic.has_key(d['ingkey']):
                    debug('Setting new shopping category!',2)
                    self.imodel.set_value(iter, 6, self.rg.sl.orgdic[d['ingkey']])
        for attr,v in d.items():
            if self.ingColsByAttr.has_key(attr):
                self.imodel.set_value(ref.get_model().get_iter(ref.get_path()),self.ingColsByAttr[attr],v)
        # Update everything but our treeview
        self.create_ing_alist()
        self.updateIngredientsDisplay()
        self.update_nutrition_info()

    def add_ingredient_from_line (self, line, group_iter=None, prev_iter=None):
        """Add an ingredient to our list from a line of plain text"""
        d=self.rg.rd.ingredient_parser(line, conv=self.rg.conv)
        if d:
            if d.has_key('rangeamount'):
                d['amount'] = self.rg.rd._format_amount_string_from_amount(
                    (d['amount'],d['rangeamount'])
                    )    
                del d['rangeamount']
            elif d.has_key('amount'):
                d['amount'] = convert.float_to_frac(d['amount'])
            return self.ingtree_ui.ingController.add_new_ingredient(prev_iter=prev_iter,group_iter=group_iter,**d)

    def importIngredientsCB (self, *args):
        debug('importIngredientsCB',5) #FIXME
        f=de.select_file(_("Choose a file containing your ingredient list."),action=gtk.FILE_CHOOSER_ACTION_OPEN)
        add_with_undo(self, lambda *args: self.importIngredients(f))

    def pasteIngsCB (self, *args):
        self.cb = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY)
        def add_ings_from_clippy (cb,txt,data):
            if txt:
                def do_add ():
                    for l in txt.split('\n'):
                        if l.strip(): self.add_ingredient_from_line(l)
                add_with_undo(self, lambda *args: do_add())
        self.cb.request_text(add_ings_from_clippy)

    def show_edit (self, tab=None):
        if not tab: tab = self.NOTEBOOK_ATTR_PAGE
        self.notebook.set_current_page(tab)
        self.edit_window.present()

    def viewCB (self, button):
        self.display_window.present()
            
    def setEditMode (self, edit_on):
        if edit_on:
            self.notebook.set_show_tabs(True)
            self.undoButtons.set_visible(True)
            self.saveButtons.set_visible(True)
            self.notebook.set_current_page(self.NOTEBOOK_ATTR_PAGE)
        else:
            #self.notebook.set_show_tabs(False)
            self.glade.get_widget('recCard').hide()
            self.glade.get_widget('recCardDisplay').show()
            #self.undoButtons.set_visible(False)
            #self.saveButtons.set_visible(False)            
            #self.notebook.set_current_page(self.NOTEBOOK_DISPLAY_PAGE)

    def importIngredients (self, file):
        ifi=file(file,'r')
        for line in ifi:
            self.ingtree_ui.add_ingredient_from_line(line)
        
    def saveAs (self, *args):
        debug("saveAs (self, *args):",5)
        opt = self.prefs.get('save_recipe_as','html')
        if opt and opt[0]=='.': opt = opt[1:] #strip off extra "." if necessary
        fn,exp_type=de.saveas_file(_("Save recipe as..."),
                                   filename="~/%s.%s"%(self.current_rec.title,opt),
                                   filters=exporters.saveas_single_filters[0:])
        if not fn: return
        if not exp_type or not exporters.exporter_dict.has_key(exp_type):
            de.show_message(_('Gourmet cannot export file of type "%s"')%os.path.splitext(fn)[1])
            return
        myexp = exporters.exporter_dict[exp_type]
        if myexp.get('extra_prefs_dialog',None):
            extra_prefs = myexp['extra_prefs_dialog']()
        else:
            extra_prefs = {}
        if myexp.get('mode',''):
            out=open(fn,'wb')
        else:
            out=open(fn,'w')

        try:
            myexp['exporter']({
                'rd':self.rg.rd,
                'rec':self.current_rec,
                'out':out,
                'conv':self.rg.conv,
                'change_units':self.prefs.get('readableUnits',True),
                'mult':self.mult,
                'extra_prefs':extra_prefs
                })
            self.message(myexp['single_completed']%{'file':fn})
        except:
            from StringIO import StringIO
            f = StringIO()
            import traceback; traceback.print_exc(file=f)
            error_mess = f.getvalue()
            de.show_message(
                label=_('Unable to save %s')%fn,
                sublabel=_('There was an error during export.'),
                expander=(_('_Details'),error_mess),
                message_type=gtk.MESSAGE_ERROR
                )
        else:
            # set prefs for next time
            out.close()
            ext=os.path.splitext(fn)[1]
            self.prefs['save_recipe_as']=ext
            self.rg.offer_url(
                label=_("Export succeeded"),
                sublabel=_("Exported %(filetype)s to %(filename)s")%{
                'filetype':exp_type,
                'filename':fn,},
                url='file:///%s'%fn
                )

    def changedCB (self, widget):
        ## This needs to keep track of undo history...
        pass

    def get_prop_for_widget (self, widget):
        if not widget: return
        for p,w in self.rw.items():
            if widget==w: return p
            # For comboboxes whose entries we've been handed...
            if hasattr(widget,'parent') and widget.parent==w and isinstance(widget,gtk.Entry): return p

    def undo_action_callback (self, undo_history, action, typ):
        # For all actions that go into the undo system, not just UNDO
        widget = action.widget
        prop = self.get_prop_for_widget(widget)
        if prop:
            # For all changes to simple recipe attributes (Title,
            # Cuisine, etc.), we look at every change and compare with
            # the original value. If it has, we delete the change from
            # our dictionary of changes. If all changes have been set
            # back to original value, we are no longer "Edited"            
            if hasattr(widget,'get_value'): val = widget.get_value()
            elif hasattr(widget,'get_text'): val = widget.get_text()
            elif hasattr(widget,'entry'): val = widget.entry.get_text()
            elif hasattr(widget,'get_buffer'): val = widget.get_buffer().get_text()
            else: raise TypeError("I don't know how to get the value from action %s widget %s"%(action,widget))
            # HAVE TO HANDLE CATEGORIES
            if prop=='category':
                orig_value = ', '.join(self.rg.rd.get_cats(self.current_rec))
            else:
                orig_value = getattr(self.current_rec,prop)
            if type(orig_value) in types.StringTypes:
                val = val.strip(); orig_value=orig_value.strip()
            else:
                if not val: val = 0
                if not orig_value: orig_value = 0
            if orig_value==val:
                if self.widgets_changed_since_save.has_key(prop):
                    del self.widgets_changed_since_save[prop]
            else:
                self.widgets_changed_since_save[prop]=val            
        else:
            # If we can't compare with original values, we keep a
            # dictionary of all changes made on a per-widget basis.
            if not widget:
                self.widgets_changed_since_save['UntrackableChange']=True
            else:
                # We store each change in our dictionary... if the
                # change has disappeared from the history list, then
                # we can surmise it has been "undone"
                if self.widgets_changed_since_save.has_key(widget):
                    old_change = self.widgets_changed_since_save[widget][-1]
                    if (old_change.is_undo != action.is_undo
                        and
                        old_change not in undo_history):
                        # If we are the inverse of the old action and
                        # the old action is no longer in history, then
                        # we can assume (safely?) that we have undone
                        # the old action
                        del self.widgets_changed_since_save[widget][-1]
                        if not self.widgets_changed_since_save[widget]:
                            del self.widgets_changed_since_save[widget]
                    else:
                        self.widgets_changed_since_save[widget].append(action)
                else:
                    self.widgets_changed_since_save[widget]=[action]
        if self.widgets_changed_since_save:
            self.setEdited(True)
        else:
            self.setEdited(False)
        
    def setEdited (self, boolean=True):
        debug("setEdited (self, boolean=True):",5)
        self.edited=boolean
        if boolean:
            self.save.set_sensitive(True)
            self.revert.set_sensitive(True)
            self.message(_("You have unsaved changes."))
        else:
            self.save.set_sensitive(False)
            self.revert.set_sensitive(False)
            self.message(_("There are no unsaved changes."))

    def hide (self, *args):
        debug("hide (self, *args):",5)
        for c in self.conf:
            c.save_properties()
        if not self.new and self.edit_window.get_property('visible'):
            self.hide_edit()
        self.display_window.hide()
        # delete it from main apps list of open windows
        self.rg.del_rc(self.current_rec.id)
        if not self.display_window.get_property('visible'):
            self.rg.del_rc(self.current_rec.id)
        return True

    def hide_edit (self, *args):
        for c in self.conf:
            c.save_properties()
        if self.edited:
            test=de.getBoolean(label=_("Save edits to %s before closing?")%self.current_rec.title,
                               cancel_returns='CANCEL')
            if test=='CANCEL':
                return True
            elif test:
                self.saveEditsCB()
            else:
                self.edited=False #to avoid multiple dialogs if this gets called twice somehow
                if self.new:
                    self.delete()
        self.edit_window.hide()
        return True
        
    def show (self, *args):
        debug("show (self, *args):",5)
        if self.new:
            self.edit_window.set_title("%s %s"%(self.edit_title,self.current_rec.title.strip()))
            self.display_window.hide()
            self.edit_window.present()
            self.view.set_visible(True)
            self.view.set_sensitive(False)
        else:
            self.edit_window.set_title("%s %s"%(self.edit_title,self.current_rec.title))
            self.display_window.set_title("%s %s"%(self.default_title,self.current_rec.title))
            self.display_window.present()
            self.edit_window.hide()

    def email_rec (self, *args):
        if self.edited:
            if de.getBoolean(label=_("You have unsaved changes."),
                             sublabel=_("Apply changes before e-mailing?")):
                self.saveEditsCB()
        from exporters import recipe_emailer
        d=recipe_emailer.EmailerDialog([self.current_rec],
                                       self.rg.rd, self.prefs, self.rg.conv)
        d.setup_dialog()
        d.email()

    def print_rec (self, *args):
        if self.edited:
            if de.getBoolean(label=_("You have unsaved changes."),
                             sublabel=_("Apply changes before printing?")):
                self.saveEditsCB()
        printer.RecRenderer(self.rg.rd, [self.current_rec], mult=self.mult,
                            dialog_title=_("Print Recipe %s"%(self.current_rec.title)),
                            dialog_parent=self.edit_window,
                            change_units=self.prefs.get('readableUnits',True)
                            )

    def message (self, msg):
        debug('message (self, msg): %s'%msg,5)
        self.stat.push(self.contid,msg)

class ImageBox:
    def __init__ (self, RecCard):
        debug("__init__ (self, RecCard):",5)
        self.rg = RecCard.rg
        self.rc = RecCard
        self.glade = self.rc.glade
        self.imageW = self.glade.get_widget('recImage')
        self.addW = self.glade.get_widget('addImage')
        self.delW = self.glade.get_widget('delImageButton')
        self.imageD = self.glade.get_widget('imageDisplay')
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
            return ie.get_string_from_image(self.image),ie.get_string_from_image(self.thumb)
        else:
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
        self.imageD.set_from_pixbuf(pb)
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
        if de.getBoolean(label="Are you sure you want to remove this image?",
                         parent=self.rc.widget):
            current_image = ie.get_string_from_image(self.image)
            Undo.UndoableObject(
                lambda *args: self.remove_image(),
                lambda *args: self.set_from_string(current_image),
                self.rc.history,
                widget=self.imageW).perform()

    def remove_image (self):
        self.rc.current_rec.image=''
        self.image=None
        self.orig_pixbuf = None
        self.draw_image()
        self.edited=True

class UndoableObjectWithInverseThatHandlesItsOwnUndo (Undo.UndoableObject):

    """A class for an UndoableObject whose Undo method already makes
    its own undo magic happen without need for our intervention.
    """
    # This is useful for making Undo's of "add"s -- we use the delete
    # methods for our Undoing nwhich already do a good job handling all
    # the Undo magic properly

    def inverse (self):
        self.history.remove(self)
        self.inverse_action()

def add_with_undo (rc,method):
    uts = UndoableTreeStuff(rc.ingtree_ui.ingController)
    def do_it ():
        uts.start_recording_additions()
        method()
        uts.stop_recording_additions()
    UndoableObjectWithInverseThatHandlesItsOwnUndo(
        do_it,
        uts.undo_recorded_additions,
        rc.history,
        widget=rc.ingtree_ui.ingController.imodel
        ).perform()

class UndoableTreeStuff:
    def __init__ (self, ic):
        self.ic = ic

    def start_recording_additions (self):
        debug('UndoableTreeStuff.start_recording_additiong',3)        
        self.added = []
        self.pre_ss = te.selectionSaver(self.ic.rc.ingtree_ui.ingTree)        
        self.connection = self.ic.imodel.connect('row-inserted',
                                                 self.row_inserted_cb)
        debug('UndoableTreeStuff.start_recording_additiong DONE',3)        
        
    def stop_recording_additions (self):
        debug('UndoableTreeStuff.stop_recording_additiong',3)                
        self.added = [
            # i.get_model().get_iter(i.get_path()) is how we get an
            # iter from a TreeRowReference
            self.ic.get_persistent_ref_from_iter(i.get_model().get_iter(i.get_path()))
            for i in self.added
            ]
        self.ic.imodel.disconnect(self.connection)
        debug('UndoableTreeStuff.stop_recording_additions DONE',3)        
        
    def undo_recorded_additions (self):
        debug('UndoableTreeStuff.undo_recorded_additions',3)
        self.ic.delete_iters(
            *[self.ic.get_iter_from_persistent_ref(a) for a in self.added],
            **{'is_undo':True}
            )
        debug('UndoableTreeStuff.undo_recorded_additions DONE',3)                

    def row_inserted_cb (self, tm, path, itr):
        self.added.append(gtk.TreeRowReference(tm,tm.get_path(itr)))

    def record_positions (self, iters):
        debug('UndoableTreeStuff.record_positions',3)                
        self.pre_ss = te.selectionSaver(self.ic.rc.ingtree_ui.ingTree)        
        self.positions = []
        for i in iters:
            path = self.ic.imodel.get_path(i)
            if path[-1]==0:
                parent = path[:-1] or None
                sibling = None
            else:
                parent = None
                sibling = path[:-1] + (path[-1]-1,)
            sib_ref = sibling and self.ic.get_persistent_ref_from_path(sibling)
            parent_ref = parent and self.ic.get_persistent_ref_from_path(parent)
            ref = self.ic.get_persistent_ref_from_iter(i)
            self.positions.append((ref,sib_ref,parent_ref))
        debug('UndoableTreeStuff.record_positions DONE',3)                

    def restore_positions (self):
        debug('UndoableTreeStuff.restore_positions',3)                        
        for ref,sib_ref,parent_ref in self.positions:
            te.move_iter(self.ic.imodel,
                         self.ic.get_iter_from_persistent_ref(ref),
                         sibling=sib_ref and self.ic.get_iter_from_persistent_ref(sib_ref),
                         parent=parent_ref and self.ic.get_iter_from_persistent_ref(parent_ref),
                         direction='after'
                         )
            self.pre_ss.restore_selections()
        debug('UndoableTreeStuff.restore_positions DONE',3)                        

class IngredientController:

    """Handle updates to our ingredient model.

    Changes are not reported as they happen; rather, we use the
    commit_ingredients method to do sync up our database with what
    we're showing as our database.
    """

    def __init__ (self, rc):
        self.rc = rc; self.rg = self.rc.rg; self.glade = self.rc.glade
        self.new_item_count = 0
        self.commited_items_converter = {}

    # Setup methods
    def create_imodel (self, rec):
        self.ingredient_objects = []        
        self.current_rec=rec
        ings=self.rg.rd.get_ings(rec)
        # as long as we have the list here, this is a good place to update
        # the activity of our menuitem for forgetting remembered optionals        
        remembered=False
        for i in ings:
            if i.shopoptional==1 or i.shopoptional==2:
                remembered=True
                break
        self.forget_remembered_optionals_menuitem = self.glade.get_widget('forget_remembered_optionals_menuitem')
        self.forget_remembered_optionals_menuitem.set_sensitive(remembered)
        ## now we continue with our regular business...
        debug("%s ings"%len(ings),3)
        self.ing_alist=self.rg.rd.order_ings(ings)
        self.imodel = gtk.TreeStore(gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_BOOLEAN,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)
        for g,ings in self.ing_alist:
            if g:
                g=self.add_group(g)
            for i in ings:
                debug('adding ingredient %s'%i.item,0)
                self.add_ingredient(i, group_iter=g)
        return self.imodel

    def _new_iter_ (self,
                    group_iter=None,
                    prev_iter=None,
                    fallback_on_append=True):
        iter = None
        if group_iter and not prev_iter:
            if type(self.imodel.get_value(group_iter, 0)) not in types.StringTypes:
                prev_iter = group_iter
                print 'fix this old code!'
                import traceback; traceback.print_stack()
                print '(not a real traceback, just a hint for fixing the old code)'
            else:
                iter = self.imodel.append(group_iter)
        if prev_iter:
            iter = self.imodel.insert_after(None, prev_iter, None)
        if not iter:
            if fallback_on_append: iter = self.imodel.append(None)
            else: iter = self.imodel.prepend(None)
        return iter
    
    # Add recipe info...
    def add_ingredient_from_kwargs (self, group_iter=None, prev_iter=None,
                                    fallback_on_append=True, undoable=False,
                                    placeholder=None, # An ingredient
                                                      # object count
                                                      # (number)
                                    **ingdict):
        iter = self._new_iter_(group_iter=group_iter,prev_iter=prev_iter,
                               fallback_on_append=fallback_on_append)
        if ingdict.has_key('refid') and ingdict['refid']:
            self.imodel.set_value(iter,0,
                                  RecRef(ingdict['refid'],ingdict.get('item',''))
                                  )
        elif placeholder is not None:
            self.imodel.set_value(iter,0,placeholder)
        else:
            self.imodel.set_value(iter,0,self.new_item_count)
            self.new_item_count+=1
        self.update_ingredient_row(
            iter,**ingdict
            )
        return iter

    def add_new_ingredient (self,                            
                            *args,
                            **kwargs
                            ):
        ret = self.add_ingredient_from_kwargs(*args,**kwargs)
        return ret

    def undoable_update_ingredient_row (self, ref, d):
        itr = self.rc.ingtree_ui.ingController.get_iter_from_persistent_ref(ref)
        orig = self.rc.ingtree_ui.ingController.get_rowdict(itr)
        Undo.UndoableObject(
            lambda *args: self.update_ingredient_row(itr,**d),
            lambda *args: self.update_ingredient_row(itr,**orig),
            self.rc.history,
            widget=self.imodel,
            ).perform()

    def update_ingredient_row (self,iter,
                               amount=None,
                               unit=None,
                               item=None,
                               optional=None,
                               ingkey=None,
                               shop_cat=None,
                               refid=None,
                               undoable=False
                               ):
        if amount is not None: self.imodel.set_value(iter,1,amount)
        if unit is not None: self.imodel.set_value(iter,2,unit)
        if item is not None: self.imodel.set_value(iter,3,item)
        if optional is not None: self.imodel.set_value(iter,4,optional)
        if ingkey is not None: self.imodel.set_value(iter,5,ingkey)
        if shop_cat:
            self.imodel.set_value(iter,6,shop_cat)
        elif ingkey and self.rc.rg.sl.orgdic.has_key(ingkey):
            self.imodel.set_value(iter,6,self.rc.rg.sl.orgdic[ingkey])
                
    def add_ingredient (self, ing, prev_iter=None, group_iter=None,
                        fallback_on_append=True, shop_cat=None,
                        is_undo=False):
        """add an ingredient to our model based on an ingredient
        object.

        group_iter is an iter to put our ingredient inside of.

        prev_iter is an ingredient after which we insert our ingredient

        fallback_on_append tells us whether to append or (if False)
        prepend when we have no group_iter.

        is_undo asks if this is part of an UNDO action. If it is, we
        don't add the object to our list of ingredient_objects (which
        is designed to reflect the current state of the database).
        """
        i = ing
        # Append our ingredient object to a list so that we will be able to notice if it has been deleted...
        if not is_undo: self.ingredient_objects.append(ing)
        iter = self._new_iter_(prev_iter=prev_iter,group_iter=group_iter,fallback_on_append=fallback_on_append)
        amt = self.rg.rd.get_amount_as_string(i)
        unit = i.unit
        self.imodel.set_value(iter, 0, i)
        self.imodel.set_value(iter, 1, amt)
        self.imodel.set_value(iter, 2, unit)
        self.imodel.set_value(iter, 3, i.item)
        if i.optional:
            opt=True
        else:
            opt=False
        self.imodel.set_value(iter, 4, opt)
        self.imodel.set_value(iter, 5, i.ingkey)
        if shop_cat:
            self.imodel.set_value(iter, 6, shop_cat)
        elif self.rg.sl.orgdic.has_key(i.ingkey):
            debug("Key %s has category %s"%(i.ingkey,self.rg.sl.orgdic[i.ingkey]),5)
            self.imodel.set_value(iter, 6, self.rg.sl.orgdic[i.ingkey])
        else:
            self.imodel.set_value(iter, 6, None)
        return iter

    def add_group (self, name, prev_iter=None, children_iters=[], fallback_on_append=True):
        if not prev_iter:
            if fallback_on_append: groupiter = self.imodel.append(None)
            else: groupiter = self.imodel.prepend(None)
        else:
            # ALLOW NO NESTING!
            while self.imodel.iter_parent(prev_iter):
                print 'Odd, ',prev_iter,'has parent','(inserting our group after parent)'
                prev_iter = self.imodel.iter_parent(prev_iter)
            groupiter = self.imodel.insert_after(None,prev_iter,None)
        self.imodel.set_value(groupiter, 0, "GROUP %s"%name)
        self.imodel.set_value(groupiter, 1, name)
        children_iters.reverse()
        for c in children_iters:
            te.move_iter(self.imodel,c,None,parent=groupiter,direction='after')
            #self.rg.rd.undoable_modify_ing(self.imodel.get_value(c,0),
            #                               {'inggroup':name},
            #                               self.history)
        debug('add_group returning %s'%groupiter,5)
        return groupiter

    #def change_group (self, name,
    def delete_iters (self, *iters, **kwargs):
        """kwargs can have is_undo"""
        is_undo = kwargs.get('is_undo',False)
        refs = []
        undo_info = []
        try:
            paths = [self.imodel.get_path(i) for i in iters]
        except TypeError:
            print 'Odd we are failing to get_paths for ',iters
            print 'Our undo stack looks like this...'
            print self.rc.history
            raise
        for itr in iters:
            orig_ref = self.get_persistent_ref_from_iter(itr)
            # We don't want to add children twice, once as a
            # consequent of their parents and once because they've
            # been selected in their own right.
            parent = self.imodel.iter_parent(itr)
            parent_path =  parent and self.imodel.get_path(parent)
            if parent_path in paths:
                # If our parent is in the iters to be deleted -- we
                # don't need to delete it individual
                continue
            refs.append(orig_ref)
            deleted_dic,prev_ref,ing_obj = self._get_undo_info_for_iter_(itr)
            child = self.imodel.iter_children(itr)
            children = []
            if child:
                expanded = self.rc.ingtree_ui.ingTree.row_expanded(
                    self.imodel.get_path(itr)
                    )
            else:
                expanded = False
            while child:
                children.append(self._get_undo_info_for_iter_(child))
                child = self.imodel.iter_next(child)
            undo_info.append((deleted_dic,prev_ref,ing_obj,children,expanded))
    
        u = Undo.UndoableObject(
            lambda *args: self.do_delete_iters(refs),
            lambda *args: self.do_undelete_iters(undo_info),
            self.rc.history,
            widget=self.imodel,
            is_undo=is_undo
            )
        debug('IngredientController.delete_iters Performing deletion of %s'%refs,2)
        u.perform()

    def _get_prev_path_ (self, path):
        if path[-1]==0:
            if len(path)==1:
                prev_path = None
            else:
                prev_path = tuple(path[:-1])
        else:
            prev_path = te.path_next(path,-1)
        return prev_path

    def _get_undo_info_for_iter_ (self, iter):
        deleted_dic = self.get_rowdict(iter)
        path = self.imodel.get_path(iter)
        prev_path = self._get_prev_path_(path)
        if prev_path:
            prev_ref = self.get_persistent_ref_from_path(prev_path)
        else:
            prev_ref = None
        ing_obj = self.imodel.get_value(iter,0)
        return deleted_dic,prev_ref,ing_obj

    def do_delete_iters (self, iters):
        for ref in iters:
            i = self.get_iter_from_persistent_ref(ref)
            if not i: print 'Failed to get reference from',i
            else: self.imodel.remove(i)

    def do_undelete_iters (self, rowdicts_and_iters):
        for rowdic,prev_iter,ing_obj,children,expanded in rowdicts_and_iters:
            prev_iter = self.get_iter_from_persistent_ref(prev_iter)
            # If ing_obj is a string, then we are a group
            if ing_obj and type(ing_obj) in types.StringTypes:
                itr = self.add_group(rowdic['amount'],prev_iter,fallback_on_append=False)
            elif type(ing_obj) == int or not ing_obj:        
                itr = self.add_ingredient_from_kwargs(prev_iter=prev_iter,
                                                      fallback_on_append=False,
                                                      placeholder=ing_obj,
                                                      **rowdic)
            #elif ing_obj not in self.ingredient_objects:
            #    # If we have an ingredient object, but it's not one we
            #    # recall, then we must be recalling the object from
            #    # before a deletion -- we'll 
            else:
                # Otherwise, we must have an ingredient object
                itr = iter = self.add_ingredient(ing_obj,prev_iter,
                                                 fallback_on_append=False,
                                                 is_undo=True)
                self.update_ingredient_row(iter,**rowdic)
            if children:
                first = True
                for rd,pi,io in children:
                    pi = self.get_iter_from_persistent_ref(pi)
                    if first:
                        gi = itr
                        pi = None
                        first = False
                    else:
                        gi = None    
                    if io and type(io) not in [str,unicode,int] and not isinstance(io,RecRef):
                        itr = self.add_ingredient(io,
                                                  group_iter=gi,
                                                  prev_iter=pi,
                                                  fallback_on_append=False,
                                                  is_undo = True)
                        self.update_ingredient_row(itr,**rd)
                    else:
                        itr = self.add_ingredient_from_kwargs(group_iter=gi,
                                                              prev_iter=pi,
                                                              fallback_on_append=False,
                                                              **rd)
                        self.imodel.set_value(itr,0,io)
            if expanded:
                self.rc.ingtree_ui.ingTree.expand_row(self.imodel.get_path(itr),True)

    # Get a dictionary describing our current row
    def get_rowdict (self, iter):
        d = {}
        for k,n in [('amount',1),
                    ('unit',2),
                    ('item',3),
                    ('optional',4),
                    ('ingkey',5),
                    ('shop_cat',6)]:
            d[k] = self.imodel.get_value(iter,n)
        return d

    # Get persistent references to items easily

    def get_persistent_ref_from_path (self, path):
        return self.get_persistent_ref_from_iter(
            self.imodel.get_iter(path)
            )

    def get_persistent_ref_from_iter (self, iter):
        uid = self.imodel.get_value(iter,0)
        return uid

    def get_path_from_persistent_ref (self, ref):
        return self.imodel.get_path(
            self.get_iter_from_persistent_ref(ref)
            )

    def get_iter_from_persistent_ref (self, ref):
        try:
            if self.commited_items_converter.has_key(ref):
                ref = self.commited_items_converter[ref]
        except TypeError:
            # If ref is unhashable, we don't care
            pass
        itr = self.imodel.get_iter_first()
        while itr:
            v = self.imodel.get_value(itr,0)
            if v == ref or self.rg.rd.row_equal(v,ref):
                return itr
            child = self.imodel.iter_children(itr)
            if child:
                itr = child
            else:
                next = self.imodel.iter_next(itr)
                if next:
                    itr = next
                else:
                    parent = self.imodel.iter_parent(itr)
                    if parent:
                        itr = self.imodel.iter_next(parent)
                    else:
                        itr = None
        itr = self.imodel.get_iter_first()
        while itr:
            child = self.imodel.iter_children(itr)
            if child: itr = child
            else:
                next = self.imodel.iter_next(itr)
                if next:
                    itr = next
                else:
                    parent = self.imodel.iter_parent(itr)
                    if parent:
                        itr = self.imodel.iter_next(parent)
                    else:
                        itr = None

    def commit_ingredients (self):
        """Commit ingredients as they appear in tree to database."""
        iter = self.imodel.get_iter_first()
        n = 0
        # Start with a list of all ingredient object - we'll eliminate
        # each object as we come to it in our tree -- any items not
        # eliminated have been deleted.
        deleted = self.ingredient_objects[:]

        # We use an embedded function rather than a simple loop so we
        # can recursively crawl our tree -- so think of commit_iter as
        # the inside of the loop, only better

        def commit_iter (iter, pos, group=None):
            ing = self.imodel.get_value(iter,0)
            # If ingredient is a string, than this is a group
            if type(ing) in [str,unicode]:
                group = self.imodel.get_value(iter,1)
                i = self.imodel.iter_children(iter)
                while i:
                    pos = commit_iter(i,pos,group)
                    i = self.imodel.iter_next(i)
                return pos
            # Otherwise, this is an ingredient...
            else:
                d = self.get_rowdict(iter)
                # Get the amount as amount and rangeamount
                if d['amount']:
                    amt,rangeamount = parse_range(d['amount'])
                    d['amount']=amt
                    if rangeamount: d['rangeamount']=rangeamount
                # Get category info as necessary
                if d.has_key('shop_cat'):
                    self.rg.sl.orgdic[d['ingkey']] = d['shop_cat']
                    del d['shop_cat']
                d['position']=pos
                d['inggroup']=group
                # If we are a recref...
                if isinstance(ing,RecRef):
                    d['refid'] = ing.refid
                # If we are a real, old ingredient
                if type(ing) != int and not isinstance(ing,RecRef):
                    for att in ['amount','unit','item','ingkey','position','inggroup','optional']:
                        if getattr(ing,att)==d[att]: del d[att]
                    if ing in deleted:
                        # We have not been deleted...
                        deleted.remove(ing)
                    else:
                        # In this case, we have an ingredient object
                        # that is not reflected in our
                        # ingredient_object list. This means the user
                        # Deleted us, saved, and then clicked undo,
                        # resulting in the trace object. In this case,
                        # we need to set ing.deleted to False
                        d['deleted'] = False
                    if ing.deleted: # If somehow our object is
                                    # deleted... (shouldn't be
                                    # possible, but why not check!)
                        d['deleted']=False
                    if d:
                        self.rc.rg.rd.modify_ing_and_update_keydic(ing,d)
                else:
                    d['id'] = self.rc.current_rec.id
                    self.commited_items_converter[ing] = self.rg.rd.add_ing_and_update_keydic(d)
                    # Add ourself to the list of ingredient objects so
                    # we will notice subsequent deletions.
                    self.ingredient_objects.append(self.commited_items_converter[ing])
                return pos+1
        # end commit iter

        while iter:
            n = commit_iter(iter,n)
            iter = self.imodel.iter_next(iter)
        # Now delete all deleted ings...  (We're not *really* deleting
        # them -- we're just setting a handy flag to delete=True. This
        # makes Undo faster. It also would allow us to allow users to
        # go back through their "ingredient Trash" if we wanted to put
        # in a user interface for them to do so.
        for i in deleted: self.ingredient_objects.remove(i)
        self.rg.rd.modify_ings(deleted,{'deleted':True})


class IngredientTreeUI:

    """Handle our ingredient treeview display, drag-n-drop, etc.
    """

    head_to_att = {_('Amt'):'amount',
                   _('Unit'):'unit',
                   _('Item'):'item',
                   _('Key'):'ingkey',
                   _('Optional'):'optional',
                   _('Shopping Category'):'shop_cat',
                   }

    def __init__ (self, rc):
        self.rc =rc; self.glade = self.rc.glade; self.rg = self.rc.rg
        self.ingController = IngredientController(self.rc)
        self.ingTree = self.glade.get_widget('ingTree')
        self.ingTree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)                
        self.setup_columns()
        self.ingTree.connect("row-activated",self.ingtree_row_activated_cb)
        self.ingTree.connect("button-press-event",self.ingtree_click_cb)
        self.selected=True
        #self.selection_changed()
        self.ingTree.get_selection().connect("changed",self.selection_changed_cb)
        self.setup_drag_and_drop()
        self.ingTree.show()
        
    # Basic setup methods

    def setup_columns (self):
        self.ingColsByName = {}
        self.ingColsByAttr = {}
        self.shopmodel = gtk.ListStore(str) # We need a model for
                                            # shopping-cat dropdown
        for c in self.rc.ie.shopcats:
            self.shopmodel.append([c])
        for n,head,tog,model,style in [[1,_('Amt'),False,None,None],
                                 [2,_('Unit'),False,self.rg.umodel,None],
                                 [3,_('Item'),False,None,None],
                                 [4,_('Optional'),True,None,None],
                                 [5,_('Key'),False,self.rg.inginfo.key_model,pango.STYLE_ITALIC],
                                 [6,_('Shopping Category'),False,self.shopmodel,pango.STYLE_ITALIC],
                                 ]:        
            # Toggle setup
            if tog:
                renderer = gtk.CellRendererToggle()
                renderer.set_property('activatable',True)
                renderer.connect('toggled',self.ingtree_toggled_cb,n,'Optional')
                col=gtk.TreeViewColumn(head, renderer, active=n)
            # Non-Toggle setup
            else:
                # Work around to support older pygtk
                if CRC_AVAILABLE and model:
                    debug('Using CellRendererCombo, n=%s'%n,0)
                    renderer = gtk.CellRendererCombo()
                    renderer.set_property('model',model)
                    renderer.set_property('text-column',0)
                else:
                    debug('Using CellRendererText, n=%s'%n,0)
                    renderer = gtk.CellRendererText()
                renderer.set_property('editable',True)
                renderer.connect('edited',self.ingtree_edited_cb,n,head)
                # If we have gtk > 2.8, set up text-wrapping
                try:
                    renderer.get_property('wrap-width')
                except TypeError:
                    pass
                else:
                    renderer.set_property('wrap-mode',gtk.WRAP_WORD)
                    renderer.set_property('wrap-width',150)
                if head==_('Key'):
                    try:
                        renderer.connect('editing-started',
                                         self.ingtree_start_keyedit_cb)
                    except:
                        debug('Editing-started connect failed. Upgrade GTK for this functionality.',0)
                if style:
                    renderer.set_property('style',style)
                # Create Column
                col=gtk.TreeViewColumn(head, renderer, text=n)
            # Register ourselves...
            self.ingColsByName[head]=col
            if self.head_to_att.has_key(head):
                self.ingColsByAttr[self.head_to_att[head]]=n
            # All columns are reorderable and resizeable
            col.set_reorderable(True)
            col.set_resizable(True)
            col.set_alignment(0)
            col.set_min_width(45) 
            #if n==2:     #unit
            #    col.set_min_width(80) 
            if n==3:     #item
                col.set_min_width(130) 
            if n==5:     #key
                col.set_min_width(130)
            self.ingTree.append_column(col)
        # Hackish menu for old GTK setups...
        self.setupShopPopupMenu()

    def setup_drag_and_drop (self):
        ## add drag and drop support
        targets=[('GOURMET_INTERNAL', gtk.TARGET_SAME_WIDGET, 0),
                 ('text/plain',0,1),
                 ('STRING',0,2),
                 ('STRING',0,3),
                 ('COMPOUND_TEXT',0,4),
                 ('text/unicode',0,5),]
        self.ingTree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                              targets,
                                              gtk.gdk.ACTION_DEFAULT |
                                              gtk.gdk.ACTION_COPY |
                                              gtk.gdk.ACTION_MOVE)
        self.ingTree.enable_model_drag_dest(targets,
                                            gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.ingTree.connect("drag_data_received",self.dragIngsRecCB)
        self.ingTree.connect("drag_data_get",self.dragIngsGetCB)
        self.ingTree.connect('drag-begin',
                             lambda *args: setattr(self,'ss',te.selectionSaver(self.ingTree,0))
                             )
        self.ingTree.connect('drag-end',
                             lambda *args: self.ss.restore_selections()
                             )

    def setupShopPopupMenu (self):
        if CRC_AVAILABLE: return #if we have the new cellrenderercombo, we don't need this
        self.shoppop = gtk.Menu()
        new = gtk.MenuItem(_('New Category'))
        self.shoppop.append(new)
        new.connect('activate',self.shop_popup_callback,False)
        new.show()
        sep = gtk.MenuItem()
        self.shoppop.append(sep)
        sep.show()
        for i in self.rg.sl.sh.get_orgcats():
            itm = gtk.MenuItem(i)
            self.shoppop.append(itm)
            itm.connect('activate',self.shop_popup_callback,i)
            itm.show()

    # End of setup methods

    # Callbacks and the like

    def my_isearch (self, mod, col, key, iter, data=None):
        # we ignore column info and search by item
        val = mod.get_value(iter,3)
        # and by key
        if val:
            val += mod.get_value(iter,5)
            if val.lower().find(key.lower()) != -1:
                return False
            else:
                return True
        else:
            val = mod.get_value(iter,1)
            if val and val.lower().find(key.lower())!=-1:
                return False
            else:
                return True
        
    def ingtree_click_cb (self, tv, event):
        debug("ingtree_click_cb",5)
        if CRC_AVAILABLE: return False # in this case, popups are handled already!
        x = int(event.x)
        y = int(event.y)
        time = event.time
        try:
            path, col, cellx, celly = tv.get_path_at_pos(x,y)
        except: return
        debug("ingtree_click_cb: path=%s, col=%s, cellx=%s, celly=%s"%(path,
                                                     col,
                                                     cellx,
                                                     celly),
              5)
        if col.get_title()==_('Shopping Category'):
            tv.grab_focus()
            tv.set_cursor(path,col,0)
            self.shoppop_iter=tv.get_model().get_iter(path)
            self.shoppop.popup(None,None,None,event.button,event.time)
            return True
        
    def ingtree_row_activated_cb (self, tv, path, col, p=None):
        debug("ingtree_row_activated_cb (self, tv, path, col, p=None):",5)
        itr=self.get_selected_ing()
        i = self.ingController.imodel.get_value(itr,0)
        if isinstance(i,RecRef) or (hasattr(i,'refid') and i.refid):
            rec=self.rg.rd.get_referenced_rec(i)
            if rec:
                self.rg.openRecCard(rec)
            else:
                de.show_message(parent=self.edit_window,
                                label=_("The recipe %s (ID %s) is not in our database.")%(i.item,
                                                                                          i.refid)
                                )
        else:
            d = self.ingController.get_rowdict(itr)
            self.rc.ie.show(i,d)
            self.rc.ie.ieExpander.set_expanded(True)

    def shop_popup_callback (self, menuitem, i):
        """i is our new category. If i==False, we prompt for
        a category."""
        regenerate_menu=False
        #colnum for key=5
        mod=self.ingTree.get_model()
        key=mod.get_value(self.shoppop_iter,5)
        debug('shop_pop_callback with key %s'%key,5)
        if not i:
            i=de.getEntry(label=_("Category to add %s to")%key,
                       parent=self.edit_window)
            if not i:
                return
            regenerate_menu=True
        self.rg.sl.orgdic[key]=i
        mod.set_value(self.shoppop_iter,6,i)
        if regenerate_menu:
            self.setupShopPopupMenu()

    def selection_changed_cb (self, *args):
        model,rows=self.ingTree.get_selection().get_selected_rows()
        self.selection_changed(rows and True)
        if self.rc.ie.ieExpander.get_expanded():
            itr = self.get_selected_ing()
            if itr:
                i = self.ingController.imodel.get_value(itr,0)
                d = self.ingController.get_rowdict(itr)
                if i: self.rc.ie.show(i,d)
                else: self.rc.ie.new()
        return True
    
    def selection_changed (self, selected=False):
        if selected != self.selected:
            if selected: self.selected=True
            else: self.selected=False
            self.rc.selectedIngredientGroup.set_sensitive(self.selected)

    def ingtree_toggled_cb (self, cellrenderer, path, colnum, head):
        debug("ingtree_toggled_cb (self, cellrenderer, path, colnum, head):",5)
        store=self.ingTree.get_model()
        iter=store.get_iter(path)
        val = store.get_value(iter,colnum)
        newval = not val
        ref = self.ingController.get_persistent_ref_from_iter(iter)
        u = Undo.UndoableObject(
            lambda *args: store.set_value(self.ingController.get_iter_from_persistent_ref(ref),
                                          colnum,newval),
            lambda *args: store.set_value(self.ingController.get_iter_from_persistent_ref(ref),
                                          colnum,val),
            self.rc.history,
            widget=self.ingController.imodel
            )
        u.perform()
        
    def ingtree_start_keyedit_cb (self, renderer, cbe, path_string):
        debug('ingtree_start_keyedit_cb',0)
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.ingTree.get_model()
        iter = store.get_iter(path)
        itm=store.get_value(iter,self.ingColsByAttr['item'])
        mod = renderer.get_property('model')
        myfilter=mod.filter_new()
        cbe.set_model(myfilter)
        myKeys = self.rg.rd.key_search(itm)
        vis = lambda m, iter: m.get_value(iter,0) and (m.get_value(iter,0) in myKeys or m.get_value(iter,0).find(itm) > -1)
        myfilter.set_visible_func(vis)
        myfilter.refilter()

    def ingtree_edited_cb (self, renderer, path_string, text, colnum, head):
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.ingTree.get_model()
        iter = store.get_iter(path)
        ing=store.get_value(iter,0)
        d = {}
        if type(ing) in [str,unicode]:
            debug('Changing group to %s'%text,2)
            self.change_group(iter, text)
            return
        else:       
            attr=self.head_to_att[head]
            d[attr]=text
            if attr=='amount':
                try:
                    parse_range(text)
                except:
                    show_amount_error(text)
                    raise
            elif attr=='unit':
                amt,msg=self.changeUnit(text,self.ingController.get_rowdict(iter))
                if amt:
                    d['amount']=amt
                if msg:
                    self.rc.message(msg)
            elif attr=='item':
                d['ingkey']=self.rg.rd.km.get_key(text)
            ref = self.ingController.get_persistent_ref_from_iter(iter)
            self.ingController.undoable_update_ingredient_row(ref,d)

    # Drag-n-Drop Callbacks
    
    def dragIngsRecCB (self, widget, context, x, y, selection, targetType,
                         time):
        debug("dragIngsRecCB (self=%s, widget=%s, context=%s, x=%s, y=%s, selection=%s, targetType=%s, time=%s)"%(self, widget, context, x, y, selection, targetType, time),3)
        drop_info=self.ingTree.get_dest_row_at_pos(x,y)
        mod=self.ingTree.get_model()
        if drop_info:
            path, position = drop_info
            dref = self.ingController.get_persistent_ref_from_path(path)
            dest_ing=mod.get_value(mod.get_iter(path),0)
            if type(dest_ing) in [str,unicode]: group=True
            else: group=False
        else:
            dref = None
            group = False
            position = None
        if str(selection.target) == 'GOURMET_INTERNAL':
            # if this is ours, we move it
            uts = UndoableTreeStuff(self.ingController)
            selected_iter_refs = [
                self.ingController.get_persistent_ref_from_iter(i) for i in self.selected_iter
                ]
            def do_move ():
                debug('do_move - inside dragIngsRecCB ',3)
                debug('do_move - get selected_iters from - %s '%selected_iter_refs,3)
                if dref:
                    diter = self.ingController.get_iter_from_persistent_ref(dref)
                else:
                    diter = None
                selected_iters = [
                    self.ingController.get_iter_from_persistent_ref(r) for r in selected_iter_refs
                    ]
                uts.record_positions(selected_iters)                
                debug('do_move - we have selected_iters - %s '%selected_iters,3)
                selected_iters.reverse()
                if (group and
                    (position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                     or
                     position==gtk.TREE_VIEW_DROP_INTO_OR_AFTER)
                    ):
                    for i in selected_iters:
                        te.move_iter(mod,i,direction="before",parent=diter)
                elif (position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                      or
                      position==gtk.TREE_VIEW_DROP_BEFORE):
                    for i in selected_iters:
                        te.move_iter(mod,i,sibling=diter,direction="before")
                else:
                    for i in selected_iters:
                        te.move_iter(mod,i,sibling=diter,direction="after")
                debug('do_move - inside dragIngsRecCB - move selections',3)
                self.ingTree.get_selection().unselect_all()
                for r in selected_iter_refs:
                    i = self.ingController.get_iter_from_persistent_ref(r)
                    if not i:
                        print 'Odd - I get no iter for ref',r
                        import traceback; traceback.print_stack()
                        print 'Strange indeed! carry on...'                        
                    else:
                        self.ingTree.get_selection().select_iter(i)
                debug('do_move - inside dragIngsRecCB - DONE',3)
            Undo.UndoableObject(
                do_move,
                uts.restore_positions,
                self.rc.history,
                widget=self.ingController.imodel).perform()
               #self.ingTree.get_selection().select_iter(new_iter)
        else:
            # if this is external, we copy
            debug('external drag!',2)
            lines = selection.data.split("\n")
            lines.reverse()
            if (position==gtk.TREE_VIEW_DROP_BEFORE or
                position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE and not group):
                pre_path = te.path_next(self.ingController.get_path_from_persistent_ref(dref),-1)
                if pre_path:
                    itr_ref = self.ingController.get_persistent_ref_from_path(pre_path)
                else:
                    itr_ref = None
            else:
                itr_ref = dref
            def do_add ():
                for l in lines:
                    if group: 
                        self.rc.add_ingredient_from_line(
                            l,
                            group_iter=self.ingController.get_iter_from_persistent_ref(itr_ref)
                            )
                    else:
                        self.rc.add_ingredient_from_line(
                            l,
                            prev_iter=self.ingController.get_iter_from_persistent_ref(itr_ref)
                            )
            add_with_undo(self.rc,do_add)
        #self.commit_positions()
        debug("restoring selections.")
        debug("done restoring selections.")        

    def dragIngsGetCB (self, tv, context, selection, info, timestamp):
        def grab_selection (model, path, iter, args):
            strings, iters = args            
            str = ""
            amt = model.get_value(iter,1)
            if amt:
                str="%s "%amt
            unit = model.get_value(iter,2)
            if unit:
                str="%s%s "%(str,unit)
            item = model.get_value(iter,3)
            if item:
                str="%s%s"%(str,item)
            debug("Dragged string: %s, iter: %s"%(str,iter),3)
            iters.append(iter)
            strings.append(str)
        strings=[]
        iters=[]
        tv.get_selection().selected_foreach(grab_selection,(strings,iters))
        str=string.join(strings,"\n")
        selection.set('text/plain',0,str)
        selection.set('STRING',0,str)
        selection.set('GOURMET_INTERNAL',8,'blarg')
        self.selected_iter=iters

    # Move-item callbacks

    def get_selected_refs (self):
        ts,paths = self.ingTree.get_selection().get_selected_rows()
        return [self.ingController.get_persistent_ref_from_path(p) for p in paths]
    
    def ingUpCB (self, *args):
        refs = self.get_selected_refs()
        u=Undo.UndoableObject(lambda *args: self.ingUpMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              lambda *args: self.ingDownMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              self.rc.history,
                              widget=self.ingController.imodel,
                              )
        u.perform()

    def ingDownCB (self, *args):
        refs = self.get_selected_refs()
        u=Undo.UndoableObject(lambda *args: self.ingDownMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              lambda *args: self.ingUpMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              self.rc.history)
        u.perform()

    def ingUpMover (self, paths):
        ts = self.ingController.imodel
        def moveup (ts, path, itera):
            if itera:
                prev=te.path_next(path,-1)
                prev_iter=ts.get_iter(prev)
                te.move_iter(ts,itera,sibling=prev_iter,direction="before")
                #self.ingTree.get_selection().unselect_path(path)
                #self.ingTree.get_selection().select_path(prev)
        paths.reverse()
        tt = te.selectionSaver(self.ingTree)        
        for p in paths:
            itera = ts.get_iter(p)
            moveup(ts,p,itera)
        tt.restore_selections()
        
    def ingDownMover (self, paths):
        ts = self.ingController.imodel
        def movedown (ts, path, itera):
            if itera:
                next = ts.iter_next(itera)
                te.move_iter(ts,itera,sibling=next,direction="after")
                #if next:
                #    next_path=ts.get_path(next)
                #else:
                #    next_path=path
        paths.reverse()
        tt = te.selectionSaver(self.ingTree)
        for p in paths:
            itera = ts.get_iter(p)
            movedown(ts,p,itera)
        tt.restore_selections()

    # Edit Callbacks
    def changeUnit (self, new_unit, ingdict):
        """Handed a new unit and an ingredient, we decide whether to convert and return:
        None (don't convert) or Amount (new amount)
        Message (message for our user) or None (no message for our user)"""
        key=ingdict['ingkey']
        old_unit=ingdict['unit']
        old_amt=ingdict['amount']
        if type(old_amt)==str:
            old_amt = convert.frac_to_float(old_amt)
        density=None
        conversion = self.rg.conv.converter(old_unit,new_unit,key)
        if conversion and conversion != 1:
            new_amt = old_amt*conversion
            opt1 = _("Converted: %(amt)s %(unit)s")%{'amt':convert.float_to_frac(new_amt),
                                                     'unit':new_unit}
            opt2 = _("Not Converted: %(amt)s %(unit)s")%{'amt':convert.float_to_frac(old_amt),
                                                         'unit':new_unit}
            CONVERT = 1
            DONT_CONVERT = 2
            choice = de.getRadio(label=_('Changed unit.'),
                                 sublabel=_('You have changed the unit for %(item)s from %(old)s to %(new)s. Would you like the amount converted or not?')%{
                'item':ingdict['item'],
                'old':old_unit,
                'new':new_unit},
                                 options=[(opt1,CONVERT),
                                          (opt2,DONT_CONVERT),]
                                 )
            if not choice:
                raise "User cancelled"
            if choice==CONVERT:
                return (new_amt,
                        _("Converted %(old_amt)s %(old_unit)s to %(new_amt)s %(new_unit)s"%{
                    'old_amt':old_amt,
                    'old_unit':old_unit,
                    'new_amt':new_amt,
                    'new_unit':new_unit,})
                        )
            else:
                return (None,
                        None)
        if conversion:
            return (None,None)
        return (None,
                _("Unable to convert from %(old_unit)s to %(new_unit)s"%{'old_unit':old_unit,
                                                                         'new_unit':new_unit}
                  ))


    # End Callbacks

    # Convenience methods / Access to the Tree

    # Accessing the selection

    def getSelectedIters (self):
        if len(self.ingController.imodel)==0:
            return None
        ts,paths = self.ingTree.get_selection().get_selected_rows()
        return [ts.get_iter(p) for p in paths]

    def getSelectedIter (self):
        debug("getSelectedIter",4)
        if len(self.ingController.imodel)==0:
            return None
        try:
            ts,paths=self.ingTree.get_selection().get_selected_rows()
            lpath=paths[-1]
            group=ts.get_iter(lpath)
        except:
            debug("getSelectedIter: there was an exception",0)            
            group=None
        return group

    def get_selected_ing (self):
        """get selected ingredient"""
        debug("get_selected_ing (self):",5)
        path, col = self.ingTree.get_cursor()
        if path:
            itera = self.ingTree.get_model().get_iter(path)
        else:
            tv,rows = self.ingTree.get_selection().get_selected_rows()
            if len(rows) > 0:
                itera = rows[0]
            else:
                itera=None
        return itera
        #if itera:
        #    return self.ingTree.get_model().get_value(itera,0)
        #else: return None

    def set_tree_for_rec (self, rec):        
        self.ingTree.set_model(
            self.ingController.create_imodel(rec)
            )
        self.selection_changed()
        self.ingTree.expand_all()

    def ingNewGroupCB (self, *args):
        group_name = de.getEntry(label=_('Adding Ingredient Group'),
                                 sublabel=_('Enter a name for new subgroup of ingredients'),
                                 entryLabel=_('Name of group:'),
                                 )
        selected_iters=self.getSelectedIters() or []
        undo_info = []
        for i in selected_iters:
            deleted_dic,prev_ref,ing_obj = self.ingController._get_undo_info_for_iter_(i)
            undo_info.append((deleted_dic,prev_ref,ing_obj,[],False))
        selected_iter_refs = [self.ingController.get_persistent_ref_from_iter(i)\
                              for i in selected_iters]
        pitr=self.getSelectedIter()
        if pitr:
            prev_iter_ref = self.ingController.get_persistent_ref_from_iter(pitr)
        else:
            prev_iter_ref = None
        def do_add_group ():
            itr = self.ingController.add_group(
                group_name,
                children_iters=[
                self.ingController.get_iter_from_persistent_ref(r) for r in selected_iter_refs
                ],
                prev_iter=(prev_iter_ref and self.ingController.get_iter_from_persistent_ref(prev_iter_ref))
                )
            gi = self.ingController.get_persistent_ref_from_iter(itr)
            self.ingTree.expand_row(self.ingController.imodel.get_path(itr),True)
        def do_unadd_group ():
            gi = 'GROUP '+group_name  #HACK HACK HACK
            self.ingController.imodel.remove(
                self.ingController.get_iter_from_persistent_ref(gi)
                )
            self.ingController.do_undelete_iters(undo_info)
        u = Undo.UndoableObject(do_add_group,
                           do_unadd_group,
                           self.rc.history)
        u.perform()

    def change_group (self, iter, text):
        debug('Undoable group change: %s %s'%(iter,text),3)
        model = self.ingController.imodel
        oldgroup0 = model.get_value(iter,0)
        oldgroup1 = model.get_value(iter,1)
        def change_my_group ():
            model.set_value(iter,0,"GROUP %s"%text)
            model.set_value(iter,1,text)
        def unchange_my_group ():
            model.set_value(iter,0,oldgroup0)
            model.set_value(iter,1,oldgroup1)
        obj = Undo.UndoableObject(change_my_group,unchange_my_group,self.history)
        obj.perform()    

class IngredientEditor:
    def __init__ (self, RecGui, rc):
        debug("IngredientEditor.__init__ (self, RecGui):",5)
        self.ing = None
        self.user_set_key=False
        self.user_set_shopper=False
        self.rc=rc
        self.rg = RecGui
        self.init_dics()
        self.myLastKeys = None
        self.setup_glade()
        self.setup_comboboxen()
        self.setup_signals()
        self.last_ing = ""
        self.keySetEventInhibit = False

    def init_dics (self):
        self.orgdic = self.rg.sl.sh.orgdic
        self.shopcats = self.rg.sl.sh.get_orgcats()        
        
    def setup_keybox (self, model):
        # setup combo box for keybox
        self.keyBox.set_model(model.filter_new()) 
        if self.keyBox.get_text_column() == -1:       # ie is not set
            self.keyBox.set_text_column(0)
        if len(model) > 5:
            self.keyBox.set_wrap_width(3)
                
    def setup_comboboxen (self):
        # setup combo box for unitbox
        debug('start setup_comboboxen()',3)
        self.unitBox.set_model(self.rg.umodel)        
        if len(self.rg.umodel) > 6:
            self.unitBox.set_wrap_width(2)
            if len(self.rg.umodel) > 10:
                self.unitBox.set_wrap_width(3)
        self.unitBox.set_text_column(0)
        cb.FocusFixer(self.unitBox)
        # remove this temporarily because of annoying gtk bug
        # http://bugzilla.gnome.org/show_bug.cgi?id=312528
        self.unitBox.entry = self.unitBox.get_children()[0]
        #cb.setup_completion(self.unitBox) # add autocompletion
        self.setup_keybox(self.rg.inginfo.key_model)
        self.rg.inginfo.disconnect_calls.append(lambda *args: self.keyBox.set_model(empty_model))
        self.rg.inginfo.key_connect_calls.append(self.setup_keybox)
        cb.setup_completion(self.keyBox) #add autocompletion
        cb.FocusFixer(self.keyBox)
        # add autocompletion for items
        if hasattr(self,'ingBox'):
            cb.make_completion(self.ingBox, self.rg.inginfo.item_model)
            self.rg.inginfo.disconnect_calls.append(self.ingBox.get_completion().set_model(empty_model))
            self.rg.inginfo.item_connect_calls.append(lambda m: self.ingBox.get_completion().set_model(m))
        cb.set_model_from_list(self.shopBox,self.shopcats)
        cb.setup_completion(self.shopBox)
        cb.FocusFixer(self.shopBox)
        if len(self.shopBox.get_model()) > 5:
            self.shopBox.set_wrap_width(2)
            if len (self.shopBox.get_model()) > 10:
                self.shopBox.set_wrap_width(3)
        self.new()

    def setup_glade (self):
        self.glade = self.rc.glade
        #self.glade.signal_connect('ieKeySet', self.keySet)
        #self.glade.signal_connect('ieShopSet', self.shopSet)
        #self.glade.signal_connect('ieApply', self.apply)
        self.ieBox = self.glade.get_widget('ieBox')
        self.ieExpander = self.glade.get_widget('ieExpander')
        self.ieAdd = self.glade.get_widget('ieAdd')
        #self.ieBox.hide()
        self.amountBox = self.glade.get_widget('ieAmount')
        self.unitBox = self.glade.get_widget('ieUnit')
        self.keyBox = self.glade.get_widget('ieKey')
        self.ingBox = self.glade.get_widget('ieIng')
        self.shopBox = self.glade.get_widget('ieShopCat')
        self.optCheck = self.glade.get_widget('ieOptional')
        self.togWidget = self.glade.get_widget('ieTogButton')
        self.quickEntry = self.glade.get_widget('quickIngredientEntry')
        
    def setup_signals (self):
        self.glade.signal_connect('ieAdd', self.add)
        self.glade.signal_connect('ieNew', self.new)
        self.glade.signal_connect('addQuickIngredient',self.quick_add)
        #self.glade.signal_connect('ieDel', self.delete_cb)        
        if hasattr(self,'ingBox') and self.ingBox:
            self.ingBox.connect('focus_out_event',self.setKey)
            self.ingBox.connect('editing_done',self.setKey)
        if hasattr(self,'keyBox') and self.keyBox:
            self.keyBox.connect('changed',self.keySet)
            self.keyBox.get_children()[0].connect('changed',self.keySet)
        if hasattr(self,'shopBox'):            
            self.shopBox.connect('changed',self.shopSet)
        # now we connect the activate signal manually that makes
        # hitting "return" add the ingredient. This way if we think
        # we were trying to autocomplete, we can block this signal.
        for w in ['ingBox','shopBox','keyBox']:
            if hasattr(self,w) and getattr(self,w):
                widg = getattr(self,w)
                if type(widg) == gtk.ComboBoxEntry:
                    widg = widg.get_children()[0]
                if type(widg) == gtk.Entry:
                    widg.connect('activate',self.returned)

    def keySet (self, *args):
        # Handler for a change in the 'Key' combo box.
        # Firstly, this could be caused by a user, or by the program. We can disable the effects
        # of the latter by using the keySetEventInhibit function/flag.
        # Then, the user could be working from ingredient to shopping category (with our automated help)
        # Here the ingredient box is filled.
        # Otherwise, we are going backwards, from a shopping category to an ingredient. 
        # Here the ingredient box is empty

        if self.keySetEventInhibit:
            pass
        else:
            debug("keySet (self, *args):",0)
            if hasattr(self,'ingBox') and self.ingBox.get_text():
                debug("keySet: ingredient box had data:",3)
                if not re.match("^\s*$",self.keyBox.entry.get_text()):
                    debug('user set key',0)
                    self.user_set_key=True
                    self.setShopper()
                else:
                    debug('user unset key',0)
                    #if user blanks key, we do our automagic again            
                    self.user_set_key=False 
            else:
                debug("keySet:  ingredient box was empty:",3)
                thisKey=self.keyBox.entry.get_text()
                ing = self.rg.rd.fetch_one(self.rg.rd.ikview, ingkey=thisKey)
                if hasattr(self,'ingBox'):
                    if ing:
                        self.ingBox.set_text( ing.item )
                    else:
                        self.ingBox.set_text('')

    def shopSet (self, eventObject):
        # Handler for a change to the shop category combo box

        if (
            (hasattr(self,'ingBox') and self.ingBox.get_text())
            or
            self.keyBox.entry.get_text()
            ):
            # User has already filled in the ingredient box, so assume they are
            # setting this manually, or it's being filled in a result of that entry
            if not re.match("^\s*$",self.shopBox.entry.get_text()):
                self.user_set_shopper=True
            else:
                #if user blanks key, we do our automagic again
                self.user_set_key=False
        else:
            #No entry in ingredient box, so assume the user is working back from shop entry
            # to find their desired ingredient
            chosenCategory=self.shopBox.entry.get_text()    
            self.rg.inginfo.make_key_model(chosenCategory)
            self.setup_keybox(self.rg.inginfo.key_model)
           # we *could* insert the first entry of the model into the keybox (but we won't)

    def addKey (self,key,item):
        debug("addKey (self,key,item):",5)
        pass
        # this stuff is no longer necessary
        # with our new key dictionary class
        #
        #if self.keydic.has_key(item):
        #    self.keydic[item].append(key)
        #else:
        #    self.keydic[item]=[key]
    
    def getKey (self):
        debug("getKey (self):        ",5)
        kk=self.keyBox.entry.get_text()
        if kk:
            return kk
        else:
            #return self.myKeys[0]
            return ""
        
    def getKeyList (self, ing=None):
        debug("getKeyList (self):",5)
        if not ing:
            ing = self.ingBox.get_text()
        return self.rg.rd.key_search(ing)

    def setKey (self, *args):
        #Handler for finishing edits to ingredient box, or lost focus
        debug("setKeyList (self, *args):        ",5)
        ing =  self.ingBox.get_text()
        if ing == self.last_ing:
            return
        myKeys = self.getKeyList(ing)
        if myKeys and not self.user_set_key:
            self.keySetEventInhibit = True
            self.keyBox.entry.set_text(myKeys[0])
            self.keySetEventInhibit = False
            self.user_set_key=False
        # and while we're at it...
        self.setKeyList()
        self.setShopper()
        self.last_ing = ing

    def setKeyList (self, *args):
        debug('setKeyList called!',0)
        t=TimeAction('getKeyList()',0)
        self.myKeys = self.getKeyList()
        t.end()
        self.itxt = self.ingBox.get_text()
        t=TimeAction('keybox - rebuild model',0)
        model = gtk.ListStore(str)
        for k in self.myKeys: model.append([k])
        self.keyBox.set_model(model)
        #self.keyBox.get_model().refilter()
        t.end()
        if len(self.keyBox.get_model()) > 6:
            self.keyBox.set_wrap_width(2)
            if len(self.keyBox.get_model()) > 10:
                self.keyBox.set_wrap_width(3)
        else: self.keyBox.set_wrap_width(1)
        self.myLastKeys=self.myKeys

    def setShopper (self):
        debug("setShopper (self):",5)
        if not self.user_set_shopper:
            sh = self.getShopper()
            if sh:
                self.shopBox.entry.set_text(sh)
                self.user_set_shopper=False
                
    def getShopper (self):
        debug("getShopper (self):",5)
        key = self.getKey()
        if self.orgdic.has_key(key):
            return self.orgdic[key]
        else:
            return None

    def show (self, ref, d):
        debug("show (self, ing):",5)
        self.ing = ref
        if d.has_key('item'):
            self.ingBox.set_text(d['item'])
        else:
            self.ingBox.set_text('')
        if d.has_key('ingkey') and d['ingkey']:
            self.keyBox.entry.set_text(d['ingkey'])
            self.keyBox.entry.user_set_key=True
        else:
            self.keyBox.entry.set_text('')
            self.user_set_key=False            
        if d.has_key('amount'):
            self.amountBox.set_text(
                d['amount']
                )
        else:
            self.amountBox.set_text('')
        if d.has_key('unit') and d['unit']:
            self.unitBox.entry.set_text(d['unit'])
        else:
            self.unitBox.entry.set_text('')
        if d.has_key('optional') and d['optional']:
            self.optCheck.set_active(True)
        else:
            self.optCheck.set_active(False)
        if d.has_key('shop_cat') and d['shop_cat']:
            self.shopBox.entry.set_text(d['shop_cat'])
        else:
            self.shopBox.entry.set_text('')
        self.user_set_shopper=False
        self.getShopper()

    def new (self, *args):
        # Handler for "New" Button
        debug("new (self, *args):",5)
        self.ing = None
        self.unitBox.entry.set_text("")
        self.shopBox.entry.set_text("")
        self.amountBox.set_text("")
        if hasattr(self,'ingBox') and self.ingBox:
            self.ingBox.set_text("")
        self.keyBox.entry.set_text("")
        self.user_set_key=False
        self.user_set_shopper=False
        if hasattr(self,'optCheck') and self.optCheck:
            self.optCheck.set_active(False)
        #self.amountBox.grab_focus()

    def get_previous_iter_and_group_iter (self):
        """Return prev_iter,group_iter"""
        # If there is a selected iter, we treat it as a group to put
        # our entry into or after
        selected_iter = self.rc.ingtree_ui.getSelectedIter()
        if not selected_iter:
            # default behavior (put last)
            group_iter = None
            prev_iter = None
        elif self.rc.ingtree_ui.ingController.imodel.get_value(selected_iter,0) in types.StringTypes:
            # if we are a group
            group_iter = selected_iter
            prev_iter = None
        else:
            # then we are a previous iter...
            group_iter = None
            prev_iter = selected_iter
        return prev_iter,group_iter

    def quick_add (self, *args):
        txt = self.quickEntry.get_text()
        prev_iter,group_iter = self.get_previous_iter_and_group_iter()
        add_with_undo(self.rc,
                      lambda *args: self.rc.add_ingredient_from_line(txt,
                                                                     prev_iter=prev_iter,
                                                                     group_iter=group_iter)
                      )
        self.quickEntry.set_text('')

    def returned(self, *args):
        # Handler when the user hits the return button in one of the comboboxes
        # don't add the item immediately in case our guess of key etc was a bit wrong of the mark
        # (with python's poor handling of accent characters, this could easily be the case!)
        # Let the user do the add...
        self.ieAdd.grab_focus()

    def add (self, *args):
        # Handler for click of the "Add" button.
        # means probably that user has entered something in the ingredient field...?
        debug("add (self, *args):",5)
        d = {}        
        d['ingkey']=self.getKey()
        d['item']=self.ingBox.get_text()
        d['unit']=self.unitBox.entry.get_text()
        amt=self.amountBox.get_text()
        if amt:
            try:
                parse_range(amt)
            except:
                show_amount_error(amt)
                raise
            else:
                d['amount']=amt
        if not d['item'] :
            # if there's no item but there is a key, we assume that the user
            # wanted the item to be the same as the key
            if d['ingkey']:
                d['item']=d['item']
                self.rc.message(_('Assuming you wanted item equal to key %s')%d['ingkey'])
            # if there's not an item or a key, we check if our user
            # made a typing error and meant the unit as an item
            elif d['unit'] and not d['unit'] in self.rg.conv.units:
                itm = d['unit']
                d['item']=d['unit']
                d['unit']=""
                self.rc.message(_('You forgot an item. Assuming you meant "%s" as an item and not a unit.')%itm)
            else:
                self.rc.message(_('An ingredient must have an item!'))
                return
        if self.optCheck.get_active(): d['optional']=True
        else: d['optional']=False
        if not d['ingkey']:
            d['ingkey']=self.rg.rd.km.get_key(d['item'])
        sh = self.shopBox.entry.get_text()
        if sh: d['shop_cat']=sh
        if self.ing is not None:
            self.rc.ingtree_ui.ingController.undoable_update_ingredient_row(self.ing,d)
        else:
            d['prev_iter'],d['group_iter'] = self.get_previous_iter_and_group_iter()
            add_with_undo(self.rc,
                          lambda *args: self.rc.ingtree_ui.ingController.add_new_ingredient(**d)
                          )
        debug('blank selves/new',5)
        self.new()
        debug('done!',5)

    def delete_cb (self, *args):
        debug("delete_cb (self, *args):",5)
        mod,rows = self.rc.ingtree_ui.ingTree.get_selection().get_selected_rows()
        rows.reverse()
        self.rc.ingtree_ui.ingController.delete_iters(*[mod.get_iter(p) for p in rows])
                                      
class IngInfo:
    """Keep models for autocompletion, comboboxes, and other
    functions that might want to access a complete list of keys,
    items and the like"""

    def __init__ (self, rd):
        self.rd = rd
        self.make_item_model()
        self.make_key_model('')
        # this is a little bit silly... but, because of recent bugginess...
        # we'll have to do it. disable and enable calls are methods that
        # get called to disable and enable our models while adding to them
        # en masse. disable calls get no arguments passed, enable get args.
        self.disconnect_calls = []
        self.key_connect_calls = []
        self.item_connect_calls = []
        self.manually = False
        self.rd.add_ing_hooks.append(self.add_ing)

    def make_item_model(self):
        #unique_item_vw = self.rd.iview_not_deleted.counts(self.rd.iview_not_deleted.item, 'count')
        self.item_model = gtk.ListStore(str)
        for i in self.rd.get_unique_values('item',table=self.rd.iview,deleted=False):
            self.item_model.append([i])
        if len(self.item_model)==0:
            import defaults
            for i,k,c in defaults.lang.INGREDIENT_DATA:
                self.item_model.append([i])
        
    def make_key_model (self, myShopCategory):
        # make up the model for the combo box for the ingredient keys
        if myShopCategory:
            unique_key_vw = self.rd.get_unique_values('ingkey',table=self.rd.sview, shopcategory=myShopCategory)
        else:
            unique_key_vw = self.rd.get_unique_values('ingkey',table=self.rd.ikview)

        # the key model by default stores a string and a list.
        self.key_model = gtk.ListStore(str)
        keys=[]
        for k in unique_key_vw:
            keys.append(k)

        keys.sort()
        for k in keys:
            self.key_model.append([k])

    def change_key (self, old_key, new_key):
        """One of our keys has changed."""
        keys = map(lambda x: x[0], self.key_model)
        index = keys.index(old_key)
        if old_key in keys:
            if new_key in keys:
                del self.key_model[index]
            else:
                self.key_model[index]=[new_key]
        modindx = self.rd.normalizations['ingkey'].find(old_key)
        if modindx>=0:
            self.rd.normalizations['ingkey'][modindx].ingkey=new_key

    def disconnect_models (self):
        for c in self.disconnect_calls:
            if c: c()

    def connect_models (self):
        for c in self.key_connect_calls: c(self.key_model)
        for c in self.item_connect_calls: c(self.item_model)

    def disconnect_manually (self):
        self.manually = True
        self.disconnect_models()

    def reconnect_manually (self):
        self.manually=False
        self.connect_models()

    def add_ing (self, ing):
        # This is really inefficient... we're going to disable temporarily
        pass
        # if not self.manually: self.disconnect_models()
#         if hasattr(ing,'item'):
#             debug('checking for item',3)
#             if not [ing.item] in self.item_model:
#                 debug('adding item',3)                
#                 self.item_model.append([ing.item])
#                 debug('appended %s to item model'%ing.item,3)
#         if hasattr(ing,'ingkey'):
#             debug('checking for key',3)
#             if not [ing.ingkey] in self.key_model:
#                 debug('adding key',3)
#                 self.key_model.append([ing.ingkey])
#                 debug('appended %s to key model'%ing.ingkey,3)
#         debug('add ing completed',3)
#         if not self.manually: self.connect_models()

class RecSelector (RecIndex):
    """Select a recipe and add it to RecCard's ingredient list"""
    def __init__(self, RecGui, RecCard):
        self.glade=gtk.glade.XML(os.path.join(gladebase,'recSelector.glade'))
        self.glade.signal_connect('cancel',self.cancel)
        self.glade.signal_connect('ok',self.ok)        
        self.rg=RecGui
        self.reccard=RecCard
        self.dialog = self.glade.get_widget('recDialog')
        RecIndex.__init__(self,
                          self.glade,
                          self.rg.rd,
                          self.rg,
                          editable=False
                          )

    def quit (self):
        self.dialog.destroy()

    def cancel (self,*args):
        debug('cancel',0)
        self.quit()

    def recTreeSelectRec (self, *args):
        self.ok()

    def ok (self,*args):
        debug('ok',0)
        pre_iter=self.reccard.ingtree_ui.get_selected_ing()
        try:
            for rec in self.recTreeSelectedRecs():
                if rec.id == self.reccard.current_rec.id:
                    de.show_message(label=_("Recipe cannot call itself as an ingredient!"),
                                    sublabel=_('Infinite recursion is not allowed in recipes!')
                                    )
                    continue
                ingdic={'amount':1,
                        'unit':'recipe',
                        'item':rec.title,
                        'refid':rec.id,
                        }
                debug('adding ing: %s'%ingdic,5)
                iter=self.reccard.ingtree_ui.ingController.add_ingredient_from_kwargs(
                    group_iter=pre_iter,
                    **ingdic
                    )
                #path=self.reccard.imodel.get_path(iter)
                #self.reccard.ss.add_selection(iter)
            self.quit()
        except:
            de.show_message(label=_("You haven't selected any recipes!"))
            raise
        
if __name__ == '__main__':

    def test_ing_editing (rc):
        rc.show_edit(tab=rc.NOTEBOOK_ING_PAGE)        
        g = rc.ingtree_ui.ingController.add_group('Foo bar')
        for l in ('''1 c. sugar
        1 c. silly; chopped and sorted
        1 lb. very silly
        1 tbs. extraordinarily silly'''.split('\n')):
            rc.add_ingredient_from_line(l,group_iter=g)
        rc.ingtree_ui.ingController.delete_iters(g)
        rc.undo.emit('activate')
    import GourmetRecipeManager
    rg = GourmetRecipeManager.RecGui()
    rg.app.hide()
    try:
        rc = RecCard(rg,rg.rd.fetch_one(rg.rd.rview))
        rc.display_window.connect('delete-event',
                                  lambda *args: gtk.main_quit()
                                  )
        rc.edit_window.connect('delete-event',lambda *args: gtk.main_quit())
        #rc.show_edit()
        #rc.rw['title'].set_text('Foo')
        
        #test_ing_editing(rc)
    except:
        rg.app.hide()
        raise
    else:
        gtk.main()
