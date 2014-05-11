from gourmet.plugin_loader import Pluggable
from gourmet.plugin import ToolPlugin, RecDisplayPlugin
from gourmet import prefs
from gourmet.gglobals import imagedir, uibase
from gourmet.gtk_extras import fix_action_group_importance
from gourmet.gtk_extras.WidgetSaver import WindowSaver
from gourmet.gtk_extras.mnemonic_manager import MnemonicManager
import gourmet.ImageExtras as ie
from gourmet.gdebug import debug
from gourmet import convert

from editor import RecEditor
from gourmet.views.ingredient.display import IngredientDisplay

import gc
import gtk
import os.path
import xml.sax.saxutils

# RECIPE CARD DISPLAY

class RecCardDisplay (Pluggable):

    ui_string = '''
    <ui>
       <menubar name="RecipeDisplayMenuBar">
          <menu name="Recipe" action="Recipe">
            <menuitem action="Export"/>
            <menuitem action="ShopRec"/>
            <!-- <menuitem action="Email"/> -->
            <menuitem action="Print"/>
            <separator/>
            <menuitem action="Delete"/>
            <separator/>
            <menuitem action="Close"/>
          </menu>
          <menu name="Edit" action="Edit">
            <menuitem action="Preferences"/>
            <menuitem action="AllowUnitsToChange"/>
          </menu>
          <menu name="Go" action="Go"/>
          <menu name="Tools" action="Tools">
            <placeholder name="StandaloneTool">
            <menuitem action="Timer"/></placeholder>
            <separator/>
            <placeholder name="DataTool">
            </placeholder>
            <separator/>
            <menuitem action="ForgetRememberedOptionals"/>    
          </menu>
          <menu name="HelpMenu" action="HelpMenu">
            <menuitem name="Help" action="Help"/>
          </menu>
        </menubar>
    </ui>
    '''

    def __init__ (self, reccard, recGui, recipe=None):
        self.reccard = reccard; self.rg = recGui; self.current_rec = recipe
        self.mult = 1 # parameter
        self.conf = [] #reccard.conf
        self.prefs = prefs.get_prefs()
        self.setup_ui()
        self.setup_uimanager()
        self.setup_main_window()
        self.setup_notebook()
        self.ingredientDisplay = IngredientDisplay(self)
        self.modules = [self.ingredientDisplay]
        self.update_from_database()
        Pluggable.__init__(self, [ToolPlugin,RecDisplayPlugin])
        self.mm = MnemonicManager()
        self.mm.add_toplevel_widget(self.window)
        self.mm.fix_conflicts_peacefully()
        self.setup_style()

    def setup_uimanager (self):
        self.ui_manager = gtk.UIManager()
        self.ui_manager.add_ui_from_string(self.ui_string)
        self.setup_actions()
        for group in [
            self.recipeDisplayActionGroup,
#            self.rg.toolActionGroup,
#            self.rg.toolActionGroup
            ]:
            fix_action_group_importance(group)
        self.ui_manager.insert_action_group(self.recipeDisplayActionGroup,0)
        self.ui_manager.insert_action_group(self.recipeDisplayFuturePluginActionGroup,0)
#        self.ui_manager.insert_action_group(self.rg.toolActionGroup,0)
#        self.rg.add_uimanager_to_manage(self.current_rec.id,self.ui_manager,'RecipeDisplayMenuBar')

    def setup_actions (self):
        self.recipeDisplayActionGroup = gtk.ActionGroup('RecipeDisplayActions')
        self.recipeDisplayActionGroup.add_actions([
            ('Recipe',None,_('_Recipe')),
            ('Edit',None,_('_Edit')),
            ('Go',None,_('_Go')),
            ('HelpMenu',None,_('_Help')),
            ('Export',gtk.STOCK_SAVE,_('Export recipe'),
             None,_('Export selected recipe (save to file)'),
             self.export_cb),
#             ('Delete',gtk.STOCK_DELETE,_('_Delete recipe'),
#              None,_('Delete this recipe'),self.reccard.delete
#              ),
            ('Close',gtk.STOCK_CLOSE,None,
             None,None,self.hide),
            ('Preferences',gtk.STOCK_PREFERENCES,None,
             None,None,self.preferences_cb),
            ('Help',gtk.STOCK_HELP,_('_Help'),
             None,None,lambda *args: de.show_faq(os.path.join(doc_base,'FAQ'),jump_to='Entering and Editing recipes')),
            ]
                                                )
        self.recipeDisplayActionGroup.add_toggle_actions([
            ('AllowUnitsToChange',None,_('Adjust units when multiplying'),
             None,
             _('Change units to make them more readable where possible when multiplying.'),
             self.toggle_readable_units_cb),
            ]
                                                       )
        self.recipeDisplayFuturePluginActionGroup = gtk.ActionGroup('RecipeDisplayFuturePluginActions')
        self.recipeDisplayFuturePluginActionGroup.add_actions([
            #('Email',None,_('E-_mail recipe'),
            # None,None,self.email_cb),
            ('Print',gtk.STOCK_PRINT,_('Print recipe'),
             '<Control>P',None,self.print_cb),
            ('ShopRec','add-to-shopping-list',None,None,None,self.shop_for_recipe_cb),
            ('ForgetRememberedOptionals',None,_('Forget remembered optional ingredients'),
             None,_('Before adding to shopping list, ask about all optional ingredients, even ones you previously wanted remembered'),self.forget_remembered_optional_ingredients), 
            ])
        ('Export',None,_('Export Recipe'),
         None,None,self.export_cb)

    def setup_ui (self):
        self.ui = gtk.Builder()
        self.ui.add_from_file(os.path.join(uibase,'recCardDisplay.ui'))

        self.ui.connect_signals({
            'shop_for_recipe':self.shop_for_recipe_cb,
            'edit_details': lambda *args: self.reccard.show_edit(module='description'),
            'edit_ingredients': lambda *args: self.reccard.show_edit(module='ingredients'),
            'edit_instructions': lambda *args: self.reccard.show_edit(module='instructions'),
            'edit_modifications': lambda *args: self.reccard.show_edit(module='notes'),
            })
        self.setup_widgets_from_ui()

    def setup_widgets_from_ui (self):
        self.display_info = ['title','rating','preptime','link',
                             'yields','yield_unit','cooktime','source',
                             'cuisine','category','instructions',
                             'modifications',]
        for attr in self.display_info:
            setattr(self,'%sDisplay'%attr,self.ui.get_object('%sDisplay'%attr))
            setattr(self,'%sDisplayLabel'%attr,self.ui.get_object('%sDisplayLabel'%attr))
            try:
                assert(getattr(self,'%sDisplay'%attr))
                if attr not in ['title','yield_unit']: 
                    assert(getattr(self,'%sDisplayLabel'%attr))
            except:
                print 'Failed to load all widgets for ',attr
                print '%sDisplay'%attr,'->',getattr(self,'%sDisplay'%attr)
                print '%sDisplayLabel'%attr,'->',getattr(self,'%sDisplayLabel'%attr)
                raise
        # instructions & notes display
        for d in ['instructionsDisplay','modificationsDisplay']:
            disp = getattr(self,d)
            disp.set_wrap_mode(gtk.WRAP_WORD)
            disp.set_editable(False)
#             disp.connect('time-link-activated',
#                          timeScanner.show_timer_cb,
#                          self.rg.conv
#                          )
        # link button
        self.linkDisplayButton = self.ui.get_object('linkDisplayButton')
        self.linkDisplayButton.connect('clicked',self.link_cb)
        # multiplication spinners
        self.yieldsDisplaySpin = self.ui.get_object('yieldsDisplaySpin')
        self.yieldsDisplaySpin.connect('changed',self.yields_change_cb)
        self.yieldsMultiplyByLabel = self.ui.get_object('multiplyByLabel')
        self.multiplyDisplaySpin = self.ui.get_object('multiplyByDisplaySpin')
        self.multiplyDisplaySpin.connect('changed',self.multiplication_change_cb)
        self.multiplyDisplayLabel = self.ui.get_object('multiplyByDisplayLabel')
        # Image display widget
        self.imageDisplay = self.ui.get_object('imageDisplay')
        # end setup_widgets_from_ui
        self.reflow_on_resize = [(getattr(self,'%sDisplay'%s[0]),s[1]) for s in [
            ('title',0.9), # label and percentage of screen it can take up...
            ('cuisine',0.5),
            ('category',0.5),
            ('source',0.5),
            ]]
        sw = self.ui.get_object('recipeBodyDisplay')
        sw.connect('size-allocate',self.reflow_on_allocate_cb)
        sw.set_redraw_on_allocate(True)                
        
    def reflow_on_allocate_cb (self, sw, allocation):
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
        if not hasattr(self,'orig_pixbuf') or not self.orig_pixbuf: return
        pb = self.imageDisplay.get_pixbuf()
        iwidth = pb.get_width()
        origwidth = self.orig_pixbuf.get_width()
        new_pb = None
        if iwidth > image_width:
            scale = float(image_width)/iwidth
            width = iwidth * scale
            height = pb.get_height() * scale
            new_pb = self.orig_pixbuf.scale_simple(
                int(width),
                int(height),
                gtk.gdk.INTERP_BILINEAR
                )
        elif (origwidth > iwidth) and (image_width > iwidth):
            if image_width < origwidth:
                scale = float(image_width)/origwidth
                width = image_width
                height = self.orig_pixbuf.get_height() * scale
                new_pb = self.orig_pixbuf.scale_simple(
                    int(width),
                    int(height),
                    gtk.gdk.INTERP_BILINEAR
                    )
            else:
                new_pb = self.orig_pixbuf
        if new_pb:
            del pb
            self.imageDisplay.set_from_pixbuf(new_pb)
        gc.collect()
        
    def setup_style (self,main=None):
        """Modify style of widgets so we have a white background"""
        if not main: main = self.main
        new_style = main.get_style().copy()
        cmap = main.get_colormap()
        new_style.bg[gtk.STATE_NORMAL]= cmap.alloc_color('white')
        new_style.bg[gtk.STATE_INSENSITIVE] = cmap.alloc_color('white')
        new_style.fg[gtk.STATE_NORMAL]= cmap.alloc_color('black')
        new_style.fg[gtk.STATE_INSENSITIVE] = cmap.alloc_color('black')
        # define a function to walk our widgets recursively 
        def set_style (widg, styl):
            if (not isinstance(widg,gtk.Button) and
                not isinstance(widg,gtk.Entry) and
                not isinstance(widg,gtk.Notebook) and
                not isinstance(widg,gtk.Separator)
                ): widg.set_style(styl)
            if hasattr(widg,'get_children'):
                for c in widg.get_children():
                    set_style(c,styl)
        set_style(main,new_style)
    
    # Main GUI setup
    def setup_main_window (self):
        self.window = gtk.Window();
        self.window.set_icon_from_file(os.path.join(imagedir,'reccard.png'))        
        self.window.connect('delete-event',self.hide)
        self.conf.append(WindowSaver(self.window,
                                                 self.prefs.get('reccard_window_%s'%self.current_rec.id,
                                                                {'window_size':(700,600)})
                                                 )
                         )
        self.window.set_default_size(*self.prefs.get('reccard_window_%s'%self.current_rec.id)['window_size'])
        main_vb = gtk.VBox()
        menu = self.ui_manager.get_widget('/RecipeDisplayMenuBar')
        main_vb.pack_start(menu,fill=False,expand=False); menu.show()
        self.messagebox = gtk.HBox()
        main_vb.pack_start(self.messagebox,fill=False,expand=False)
        self.main = self.ui.get_object('recipeDisplayMain')
        self.main.unparent()
        main_vb.pack_start(self.main); self.main.show()
        self.window.add(main_vb); main_vb.show()
        # Main has a series of important boxes which we will add our interfaces to...
        self.left_notebook = self.ui.get_object('recipeDisplayLeftNotebook')
        self.window.add_accel_group(self.ui_manager.get_accel_group())
        self.window.show()

    def setup_notebook (self):
        def hackish_notebook_switcher_handler (*args):
            # because the switch page signal happens before switching...
            # we'll need to look for the switch with an idle call
            gobject.idle_add(self.left_notebook_change_cb)
        self._last_module = None
        self.left_notebook.connect('switch-page',hackish_notebook_switcher_handler)
        self.left_notebook_pages = {}
        self.left_notebook_pages[0] = self

    def shop_for_recipe_cb (self, *args):
        print self,'shop_for_recipe_cb'
        try:
            d = self.rg.sl.getOptionalIngDic(self.rg.rd.get_ings(self.current_rec),
                                             self.mult,
                                             self.prefs)
        except UserCancelledError:
            return
        self.rg.sl.addRec(self.current_rec,self.mult,d)
        self.rg.sl.show()

    def add_plugin_to_left_notebook (self, klass):
        instance = klass(self)
        tab_label = gtk.Label(instance.label)
        n = self.left_notebook.append_page(instance.main,tab_label=tab_label)
        self.left_notebook_pages[n] = instance
        instance.main.show(); tab_label.show()
        self.modules.append(instance)
        self.left_notebook.set_show_tabs(
            self.left_notebook.get_n_pages() > 1
            )

    def remove_plugin_from_left_notebook (self, klass):
        for mod in self.modules[:]:
            if isinstance(mod,klass):
                self.modules.remove(mod)
                page_num = self.left_notebook.page_num(mod.main)
                self.left_notebook.remove_page(
                    page_num
                    )
                del self.left_notebook_pages[page_num]
                del mod.main; del mod
        self.left_notebook.set_show_tabs(
            self.left_notebook.get_n_pages() > 1
            )

    def left_notebook_change_cb (self):
        page = self.left_notebook.get_current_page()
        module = self.left_notebook_pages.get(page,None)
        if (self._last_module and self._last_module != module
            and hasattr(self._last_module,'leave_page')
            ):
            self._last_module.leave_page()
        if module:
            if hasattr(module,'enter_page'): module.enter_page()
            self._last_module = module

    def update_from_database (self):
        # FIXME: remember to set sensitivity of remembered-optionals -
        # below is the old code to do so.  as long as we have the list
        # here, this is a good place to update the activity of our
        # menuitem for forgetting remembered optionals
        #remembered=False
        #for i in ings:
        #    if i.shopoptional==1 or i.shopoptional==2:
        #        remembered=True
        #        break
        #self.forget_remembered_optionals_menuitem = self.ui.get_object('forget_remembered_optionals_menuitem')
        #self.forget_remembered_optionals_menuitem.set_sensitive(remembered)
        for module in self.modules:
            # Protect ourselves from bad modules, since these could be
            # plugins
            try:
                module.update_from_database()
            except:
                print 'WARNING: Exception raised by %(module)s.update_from_database()'%locals()
                import traceback; traceback.print_exc()
        self.special_display_functions = {
            'yields':self.update_yields_display,
            'yield_unit':self.update_yield_unit_display,
            'title':self.update_title_display,
            'link':self.update_link_display,
            }
        self.update_image()
        for attr in self.display_info:
            if self.special_display_functions.has_key(attr):
                self.special_display_functions[attr]()
            else:
                widg=getattr(self,'%sDisplay'%attr)
                widgLab=getattr(self,'%sDisplayLabel'%attr)
                if not widg or not widgLab:
                    raise Exception("There is no widget or label for  %s=%s, %s=%s" % (attr, widg, "label", widgLab))
                if attr=='category':
                    attval = self.current_rec.categories_string # ', '.join(self.rg.rd.get_cats(self.current_rec))
                else:
                    attval = getattr(self.current_rec,attr)
                if attval:
                    debug('showing attribute %s = %s'%(attr,attval),0)
                    if attr=='rating':
                        widg.set_value(attval)
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

    def update_image (self):
        imagestring = self.current_rec.image
        if not imagestring:
            self.orig_pixbuf = None
            self.imageDisplay.hide()
        else:
            self.orig_pixbuf = ie.get_pixbuf_from_jpg(imagestring)
            self.imageDisplay.set_from_pixbuf(
                self.orig_pixbuf
                )
            self.imageDisplay.show()

    def update_yield_unit_display (self):
        self.yield_unitDisplay.set_text(self.current_rec.yield_unit or '')
            
    def update_yields_display (self):
        self.yields_orig=self.current_rec.yields
        try:
            self.yields_orig = float(self.yields_orig)
        except:
            self.yields_orig = None
        if self.yields_orig:
            # in this case, display yields spinbutton and update multiplier label as necessary
            self.yieldsDisplay.show()
            self.yieldsDisplayLabel.show()
            self.multiplyDisplaySpin.hide()
            self.multiplyDisplayLabel.hide()
            #if yields:
            #    self.mult = float(yields)/float(self.yields_orig)
            #else:
            self.mult = 1
            yields=float(self.yields_orig)
            self.yieldsDisplaySpin.set_value(yields)
        else:
            #otherwise, display multiplier label and checkbutton
            self.yieldsDisplay.hide()
            self.yieldsDisplayLabel.hide()
            self.multiplyDisplayLabel.show()
            self.multiplyDisplaySpin.show()

    def update_title_display (self):
        titl = self.current_rec.title
        if not titl: titl="Unitled"
        self.window.set_title(titl)
        titl = "<b><big>" + xml.sax.saxutils.escape(titl) + "</big></b>"
        self.titleDisplay.set_label(titl)

    def update_link_display (self):
        if self.current_rec.link:
            self.linkDisplayButton.show()
            self.linkDisplay.set_markup(
                '<span underline="single" color="blue">%s</span>'%self.current_rec.link
                )
            self.link = self.current_rec.link
        else:
            self.link = ''
            self.linkDisplayButton.hide()
            self.linkDisplayLabel.hide()

    def export_cb (self, *args):
        opt = self.prefs.get('save_recipe_as','html')
        fn = exporters.exportManager.get_export_manager().offer_single_export(self.current_rec,self.prefs,parent=self.window,
                                                                              mult=self.mult)
        

    def toggle_readable_units_cb (self, widget):
        if widget.get_active():
            self.prefs['readableUnits']=True
            self.ingredientDisplay.display_ingredients()
        else:
            self.prefs['readableUnits']=False
            self.ingredientDisplay.display_ingredients()

    def preferences_cb (self, *args):
        self.rg.prefsGui.show_dialog(page=self.rg.prefsGui.CARD_PAGE)

    def hide (self, *args):
        self.window.hide()
#        self.reccard.hide()
        return True

    # Future plugin callbacks
    # def email_cb (self, *args):
#         if self.reccard.edited:
#             if de.getBoolean(label=_("You have unsaved changes."),
#                              sublabel=_("Apply changes before e-mailing?")):
#                 self.saveEditsCB()
#         from exporters import recipe_emailer
#         d=recipe_emailer.EmailerDialog([self.current_rec],
#                                        self.rg.rd, self.prefs, self.rg.conv)
#         d.setup_dialog()
#         d.email()        

    def print_cb (self, *args):
        if self.reccard.edited:
            if de.getBoolean(label=_("You have unsaved changes."),
                             sublabel=_("Apply changes before printing?")):
                self.saveEditsCB()
        printManager = get_print_manager()
        printManager.print_recipes(
            self.rg.rd, [self.current_rec], mult=self.mult,
            parent=self.window,
            change_units=self.prefs.get('readableUnits',True)
           )

    def link_cb (self, *args): launch_url(self.link)

    def yields_change_cb (self, widg):
        self.update_yields_multiplier(widg.get_value())
        self.ingredientDisplay.display_ingredients() # re-update

    def multiplication_change_cb (self, widg):
        self.mult = widg.get_value()
        self.ingredientDisplay.display_ingredients() # re-update

    def update_yields_multiplier (self, val):
        yields = self.yieldsDisplaySpin.get_value()
        if yields == self.current_rec.yields:
            self.yield_unitDisplay.set_text(self.current_rec.yield_unit)
        if yields != self.current_rec.yields:
            # Consider pluralizing...
            plur_form = defaults.defaults.get_pluralized_form(self.current_rec.yield_unit,yields)
            if plur_form != self.yield_unitDisplay.get_text():
                # Change text!
                self.yield_unitDisplay.set_text(plur_form)
        if float(yields) != self.yields_orig:
            self.mult = float(yields)/self.yields_orig
        else:
            self.mult = 1
        if self.mult != 1:
            self.yieldsMultiplyByLabel.set_text("x %s"%convert.float_to_frac(self.mult))
        else:
            self.yieldsMultiplyByLabel.set_label('')

    def forget_remembered_optional_ingredients (self):
        pass
