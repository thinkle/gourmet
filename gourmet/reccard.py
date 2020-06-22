#!/usr/bin/env python
import gc
import webbrowser

from gi.repository import Gdk, GdkPixbuf, GObject, Gtk
import os.path
try:
    from PIL import Image
except ImportError:
    import Image
import types
import xml.sax.saxutils
from gi.repository import Pango
from .exporters import exportManager
from . import convert
from .recindex import RecIndex
from . import prefs
from . import Undo
from .gtk_extras import WidgetSaver, timeEntry, ratingWidget, TextBufferMarkup
from .gtk_extras import dialog_extras as de
from .gtk_extras.dialog_extras import show_amount_error
from .gtk_extras import treeview_extras as te
from .gtk_extras import cb_extras as cb
from .exporters.printer import get_print_manager
from .gdebug import debug
from .gglobals import FLOAT_REC_ATTRS, INT_REC_ATTRS, REC_ATTR_DIC, REC_ATTRS, doc_base, uibase, imagedir
from gettext import gettext as _
from . import ImageExtras as ie
from .importers.importer import parse_range
from .gtk_extras import mnemonic_manager
from .gtk_extras import fix_action_group_importance
from .gtk_extras.dialog_extras import UserCancelledError
from .plugin import RecEditorModule, ToolPlugin, RecDisplayPlugin, RecEditorPlugin, IngredientControllerPlugin
from . import plugin_loader
from . import timeScanner
from . import defaults

# TODO
#
# Redo white-coloring of widgets
# Redo autowrapping of text fields

def find_entry (w):
    if isinstance(w,Gtk.Entry):
        return w
    else:
        if not hasattr(w,'get_children'):
            return None
        for child in w.get_children():
            e = find_entry(child)
            if e: return e

class RecRef:
    def __init__ (self, refid, title):
        self.refid = refid
        self.item = title
        self.amount = 1

# OVERARCHING RECIPE CARD CLASS - PROVIDES GLUE BETWEEN EDITING AND DISPLAY

class RecCard (object):

    def __init__ (self, rg=None, recipe=None, manual_show=False):
        if not rg:
            from .GourmetRecipeManager import get_application
            rg = get_application()
        self.rg = rg
        self.conf = []
        self.new = False
        if not recipe:
            recipe = self.rg.rd.new_rec()
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

# RECIPE CARD DISPLAY

class RecCardDisplay (plugin_loader.Pluggable):

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
        self.conf = reccard.conf
        self.prefs = prefs.get_prefs()
        self.setup_ui()
        self.setup_uimanager()
        self.setup_main_window()
        self.setup_notebook()
        self.ingredientDisplay = IngredientDisplay(self)
        self.modules = [self.ingredientDisplay]
        self.update_from_database()
        plugin_loader.Pluggable.__init__(self,
                                         [ToolPlugin,RecDisplayPlugin])
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.add_toplevel_widget(self.window)
        self.mm.fix_conflicts_peacefully()

    def setup_uimanager (self):
        self.ui_manager = Gtk.UIManager()
        self.ui_manager.add_ui_from_string(self.ui_string)
        self.setup_actions()
        for group in [
            self.recipeDisplayActionGroup,
            self.rg.toolActionGroup,
            self.rg.toolActionGroup
            ]:
            fix_action_group_importance(group)
        self.ui_manager.insert_action_group(self.recipeDisplayActionGroup,0)
        self.ui_manager.insert_action_group(self.recipeDisplayFuturePluginActionGroup,0)
        self.ui_manager.insert_action_group(self.rg.toolActionGroup,0)
        self.rg.add_uimanager_to_manage(self.current_rec.id,self.ui_manager,'RecipeDisplayMenuBar')

    def setup_actions (self):
        self.recipeDisplayActionGroup = Gtk.ActionGroup('RecipeDisplayActions')
        self.recipeDisplayActionGroup.add_actions([
            ('Recipe',None,_('_Recipe')),
            ('Edit',None,_('_Edit')),
            ('Go',None,_('_Go')),
            ('HelpMenu',None,_('_Help')),
            ('Export',Gtk.STOCK_SAVE,_('Export recipe'),
             None,_('Export selected recipe (save to file)'),
             self.export_cb),
            ('Delete',Gtk.STOCK_DELETE,_('_Delete recipe'),
             None,_('Delete this recipe'),self.reccard.delete
             ),
            ('Close',Gtk.STOCK_CLOSE,None,
             None,None,self.hide),
            ('Preferences',Gtk.STOCK_PREFERENCES,None,
             None,None,self.preferences_cb),
            ('Help',Gtk.STOCK_HELP,_('_Help'),
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
        self.recipeDisplayFuturePluginActionGroup = Gtk.ActionGroup('RecipeDisplayFuturePluginActions')
        self.recipeDisplayFuturePluginActionGroup.add_actions([
            #('Email',None,_('E-_mail recipe'),
            # None,None,self.email_cb),
            ('Print',Gtk.STOCK_PRINT,_('Print recipe'),
             '<Control>P',None,self.print_cb),
            ('ShopRec','add-to-shopping-list',None,None,None,self.shop_for_recipe_cb),
            ('ForgetRememberedOptionals',None,_('Forget remembered optional ingredients'),
             None,_('Before adding to shopping list, ask about all optional ingredients, even ones you previously wanted remembered'),self.forget_remembered_optional_ingredients),
            ])
        ('Export',None,_('Export Recipe'),
         None,None,self.export_cb)

    def setup_ui (self):
        self.ui = Gtk.Builder()
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
                print('Failed to load all widgets for ',attr)
                print('%sDisplay'%attr,'->',getattr(self,'%sDisplay'%attr))
                print('%sDisplayLabel'%attr,'->',getattr(self,'%sDisplayLabel'%attr))
                raise
        # instructions & notes display
        for d in ['instructionsDisplay','modificationsDisplay']:
            disp = getattr(self,d)
            disp.set_wrap_mode(Gtk.WrapMode.WORD)
            disp.set_editable(False)
            disp.connect('time-link-activated',
                         timeScanner.show_timer_cb,
                         self.rg.conv
                         )
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
        xsize = hadj.get_page_size()
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
                GdkPixbuf.InterpType.BILINEAR
                )
        elif (origwidth > iwidth) and (image_width > iwidth):
            if image_width < origwidth:
                scale = float(image_width)/origwidth
                width = image_width
                height = self.orig_pixbuf.get_height() * scale
                new_pb = self.orig_pixbuf.scale_simple(
                    int(width),
                    int(height),
                    GdkPixbuf.InterpType.BILINEAR
                    )
            else:
                new_pb = self.orig_pixbuf
        if new_pb:
            del pb
            self.imageDisplay.set_from_pixbuf(new_pb)
        gc.collect()

    # Main GUI setup
    def setup_main_window (self):
        self.window = Gtk.Window();
        self.window.set_icon_from_file(os.path.join(imagedir,'reccard.png'))
        self.window.connect('delete-event',self.hide)
        self.conf.append(WidgetSaver.WindowSaver(self.window,
                                                 self.prefs.get('reccard_window_%s'%self.current_rec.id,
                                                                {'window_size':(700,600)})
                                                 )
                         )
        self.window.set_default_size(*self.prefs.get('reccard_window_%s'%self.current_rec.id)['window_size'])
        main_vb = Gtk.VBox()
        menu = self.ui_manager.get_widget('/RecipeDisplayMenuBar')
        main_vb.pack_start(menu, fill=False, expand=False, padding=0)
        menu.show()
        self.messagebox = Gtk.HBox()
        main_vb.pack_start(self.messagebox, fill=False,
                           expand=False, padding=0)
        self.main = self.ui.get_object('recipeDisplayMain')
        self.main.unparent()
        main_vb.pack_start(self.main, True, True, 0); self.main.show()
        self.window.add(main_vb); main_vb.show()
        # Main has a series of important boxes which we will add our interfaces to...
        self.left_notebook = self.ui.get_object('recipeDisplayLeftNotebook')
        self.window.add_accel_group(self.ui_manager.get_accel_group())
        self.window.show()

    def setup_notebook (self):
        def hackish_notebook_switcher_handler (*args):
            # because the switch page signal happens before switching...
            # we'll need to look for the switch with an idle call
            GObject.idle_add(self.left_notebook_change_cb)
        self._last_module = None
        self.left_notebook.connect('switch-page',hackish_notebook_switcher_handler)
        self.left_notebook_pages = {}
        self.left_notebook_pages[0] = self

    def shop_for_recipe_cb (self, *args):
        print(self,'shop_for_recipe_cb')
        from . import shopgui
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
        tab_label = Gtk.Label(label=instance.label)
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

    def update_from_database(self):
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
                print('WARNING: Exception raised by %(module)s.update_from_database()'%locals())
                import traceback; traceback.print_exc()
        self.special_display_functions = {
            'yields':self.update_yields_display,
            'yield_unit':self.update_yield_unit_display,
            'title':self.update_title_display,
            'link':self.update_link_display,
            }
        self.update_image()
        for attr in self.display_info:
            if attr in self.special_display_functions:
                self.special_display_functions[attr]()
            else:
                widg=getattr(self,'%sDisplay'%attr)
                widgLab=getattr(self,'%sDisplayLabel'%attr)
                if not widg or not widgLab:
                    raise Exception("There is no widget or label for  %s=%s, %s=%s" % (attr, widg, "label", widgLab))
                if attr=='category':
                    attval = ', '.join(self.rg.rd.get_cats(self.current_rec))
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
        fn = exportManager.get_export_manager().offer_single_export(self.current_rec,self.prefs,parent=self.window,
                                                                    mult=self.mult)
        if fn:
            self.offer_url(_('Recipe successfully exported to '
                             '<a href="file:///%s">%s</a>')%(fn,fn),
                             url='file:///%s'%fn)


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
        self.reccard.hide()
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

    def link_cb (self, *args):
        webbrowser.open_new_tab(self.link)

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

    def offer_url (self, label, url, from_thread=False):
        if from_thread:
            gt.gtk_enter()
        if hasattr(self,'progress_dialog'):
            self.hide_progress_dialog()
        # Clear existing messages...
        for child in self.messagebox.get_children():
            self.messagebox.remove(child)
        # Add new message
        l = Gtk.Label()
        l.set_markup(label)
        l.connect('activate-link',lambda lbl, uri: webbrowser.open_new_tab(uri))
        infobar = Gtk.InfoBar()
        infobar.set_message_type(Gtk.MessageType.INFO)
        infobar.get_content_area().add(l)
        infobar.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        infobar.connect('response', lambda ib, response_id: self.messagebox.hide())
        self.messagebox.pack_start(infobar, True, True, 0)
        self.messagebox.show_all()
        if from_thread:
            gt.gtk_leave()


class IngredientDisplay:

    """The ingredient portion of our recipe display card.
    """

    def __init__ (self, recipe_display):
        self.recipe_display = recipe_display
        self.prefs = prefs.get_prefs()
        self.setup_widgets()
        self.rg = self.recipe_display.rg
        self.markup_ingredient_hooks = []

    def setup_widgets (self):
        self.ui = self.recipe_display.ui
        self.ingredientsDisplay = self.ui.get_object('ingredientsDisplay1')
        self.ingredientsDisplayLabel = self.ui.get_object('ingredientsDisplayLabel')
        self.ingredientsDisplay.connect('link-activated',
                                        self.show_recipe_link_cb)
        self.ingredientsDisplay.set_wrap_mode(Gtk.WrapMode.WORD)

    def update_from_database (self):
        self.ing_alist = self.rg.rd.order_ings(
            self.rg.rd.get_ings(self.recipe_display.current_rec)
            )
        self.display_ingredients()

    def display_ingredients (self):
        group_strings = []
        group_index = 0
        nut_highlighted = False
        for g,ings in self.ing_alist:
            labels = []
            if g: labels.append("<u>%s</u>"%xml.sax.saxutils.escape(g))
            ing_index = 0
            for i in ings:
                ing_strs = []
                amt,unit = self.rg.rd.get_amount_and_unit(i,
                                                          mult=self.recipe_display.mult,
                                                          conv=(self.prefs.get('readableUnits',True) and self.rg.conv or None)
                                                          )
                #if self.nutritional_highlighting and self.yields_orig:
                #    amt,unit = self.rg.rd.get_amount_and_unit(i,
                #                                              mult = 1.0/self.yields_orig,
                #                                              conv=(self.prefs.get('readableUnits',True) and self.rg.conv or None)
                #                                              )
                if amt: ing_strs.append(amt)
                if unit: ing_strs.append(unit)
                if i.item: ing_strs.append(i.item)
                if i.optional:
                    ing_strs.append(_('(Optional)'))
                istr = xml.sax.saxutils.escape(' '.join(ing_strs))
                if i.refid:
                    istr = ('<a href="%s:%s">'%(i.refid,
                                                xml.sax.saxutils.escape(i.item))
                             + istr
                            + '</a>')
                istr = self.run_markup_ingredient_hooks(istr,i,
                                                        ing_index,
                                                        group_index)
                labels.append(
                    istr
                    )
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

    def run_markup_ingredient_hooks (self, ing_string, ing_obj, ing_index, group_index):
        for hook in self.markup_ingredient_hooks:
            # each hook gets the following args:
            # ingredient string, ingredient object, ingredient index, group index
            ing_string = hook(ing_string, ing_obj, ing_index, group_index)
        return ing_string

    def create_ing_alist (self):
        """Create alist ing_alist based on ingredients in DB for current_rec"""
        ings=self.rg.rd.get_ings(self.get_current_rec())
        self.ing_alist = self.rg.rd.order_ings(ings)
        debug('self.ing_alist updated: %s'%self.ing_alist,1)

    # Callbacks

    def show_recipe_link_cb (self, widg, link):
        rid,rname = link.split(':',1)
        rec = self.rg.rd.get_rec(int(rid))
        if not rec:
            rec = self.rg.rd.fetch_one(
                self.rg.rd.recipe_table,
                title=rname
                )
        if rec:
            self.rg.open_rec_card(rec)
        else:
            de.show_message(parent=self.display_window,
                            label=_('Unable to find recipe %s in database.')%rname
                            )

# RECIPE EDITOR MODULES

class RecEditor (WidgetSaver.WidgetPrefs, plugin_loader.Pluggable):

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
            recipe=self.rg.rd.new_rec()
        self.set_edited(False)
        plugin_loader.Pluggable.__init__(self,[ToolPlugin,RecEditorPlugin])
        self.mm = mnemonic_manager.MnemonicManager()
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
        self.ui_manager = Gtk.UIManager()
        self.ui_manager.add_ui_from_string(self.ui_string)
        self.setup_action_groups()
        fix_action_group_importance(self.mainRecEditActionGroup)
        self.ui_manager.insert_action_group(self.mainRecEditActionGroup,0)
        fix_action_group_importance(self.rg.toolActionGroup)
        self.ui_manager.insert_action_group(self.rg.toolActionGroup,1)

    def setup_action_groups (self):
        self.mainRecEditActionGroup = Gtk.ActionGroup('RecEditMain')

        self.mainRecEditActionGroup.add_actions([
            # menus
            ('Recipe',None,_('_Recipe')),
            ('Edit',None,_('_Edit')),
            ('Help',Gtk.STOCK_HELP,None),
            ('HelpMenu',None,_('_Help')),
            ('Save',Gtk.STOCK_SAVE,None,
             '<Control>s',_('Save edits to database'),self.save_cb), #saveEdits
            ('DeleteRecipe',Gtk.STOCK_DELETE,_('_Delete Recipe'),
             None,None,self.delete_cb),
            ('Revert',Gtk.STOCK_REVERT_TO_SAVED,None,
             None,None,self.revert_cb), # revertCB
            ('Close',Gtk.STOCK_CLOSE,None,
             None,None,self.close_cb),
            ('Preferences',Gtk.STOCK_PREFERENCES,None,
             None,None,self.preferences_cb), # show_pref_dialog
            ('ShowRecipeCard','recipe-card',_('View Recipe Card'),
             None,None,self.show_recipe_display_cb), #view_recipe_card
            ])

    def setup_modules (self):
        self.modules = []
        self.module_tab_by_name = {}
        for klass in self.editor_module_classes:
            instance = klass(self)
            tab_label = Gtk.Label(label=instance.label)
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
        tab_label = Gtk.Label(label=instance.label)
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
        if module_name not in self.module_tab_by_name:
            raise ValueError('RecEditor has no module named %s'%module_name)
        self.notebook.set_current_page(
            self.module_tab_by_name[module_name]
            )

    def setup_main_interface (self):
        self.window = Gtk.Window()
        self.window.set_icon_from_file(os.path.join(imagedir,'reccard_edit.png'))
        title = ((self.current_rec and self.current_rec.title) or _('New Recipe')) + ' (%s)'%_('Edit')
        self.window.set_title(title)
        self.window.connect('delete-event',
                            self.close_cb)
        self.conf.append(WidgetSaver.WindowSaver(self.window,
                                                 self.rg.prefs.get('rec_editor_window',
                                                                   {'window_size':(700,600)})
                                                 )
                         )
        self.window.set_default_size(*prefs.get_prefs().get('rec_editor_window')['window_size'])
        main_vb = Gtk.VBox()
        main_vb.pack_start(self.ui_manager.get_widget('/RecipeEditorMenuBar'),expand=False,fill=False, padding=0)
        main_vb.pack_start(self.ui_manager.get_widget('/RecipeEditorToolBar'),expand=False,fill=False, padding=0)
        main_vb.pack_start(self.ui_manager.get_widget('/RecipeEditorEditToolBar'),expand=False,fill=False, padding=0)
        self.notebook = Gtk.Notebook(); self.notebook.show()
        main_vb.pack_start(self.notebook, True, True, 0)
        self.window.add(main_vb)
        self.window.add_accel_group(self.ui_manager.get_accel_group())
        main_vb.show()

    def show (self):
        self.window.present()

    def setup_notebook (self):
        def hackish_notebook_switcher_handler (*args):
            # because the switch page signal happens before switching...
            # we'll need to look for the switch with an idle call
            GObject.idle_add(self.notebook_change_cb)
        self.notebook.connect('switch-page',hackish_notebook_switcher_handler)
        ## The following workaround was necessary on Windows as long as
        ## https://bugzilla.gnome.org/show_bug.cgi?id=552681
        ## was not fixed, which it is with versions of Gtk+ that ship
        ## with PyGTK 2.24.8
        #if os.name == 'nt' or os.name == 'dos':
        #    self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        #else:
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
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
        newdict = {'id': self.current_rec.id}
        for m in self.modules:
            newdict = m.save(newdict)
        self.current_rec = self.rg.rd.modify_rec(self.current_rec,newdict)
        self.rg.rd.update_hashes(self.current_rec)
        self.rg.rmodel.update_recipe(self.current_rec)
        if 'title' in newdict:
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
                    custom_yes=Gtk.STOCK_SAVE,
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
        self.ui = Gtk.Builder()
        self.ui.add_from_file(os.path.join(uibase,'recCardIngredientsEditor.ui'))
        self.main = self.ui.get_object('ingredientsNotebook')
        self.main.unparent()
        self.ingtree_ui = IngredientTreeUI(self, self.ui.get_object('ingTree'))
        self.setup_action_groups()
        self.update_from_database()
        self.quickEntry = self.ui.get_object('quickIngredientEntry')
        self.ui.connect_signals({'addQuickIngredient':self.quick_add})

    def quick_add (self, *args):
        txt = str(self.quickEntry.get_text())
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
        self.ingredientEditorActionGroup = Gtk.ActionGroup('IngredientEditorActionGroup')
        self.ingredientEditorOnRowActionGroup = Gtk.ActionGroup('IngredientEditorOnRowActionGroup')
        self.ingredientEditorActionGroup.add_actions([
            ('AddIngredient',Gtk.STOCK_ADD,_('Add ingredient'),
             None,None),
            ('AddIngredientGroup',None,_('Add group'),
             '<Control>G',None,self.ingtree_ui.ingNewGroupCB),
            ('PasteIngredient',Gtk.STOCK_PASTE,_('Paste ingredients'),
             '<Control>V',None,self.paste_ingredients_cb),
            ('ImportIngredients',None,_('Import from file'),
             '<Control>O',None,self.import_ingredients_cb),
            ('AddRecipeAsIngredient',None,_('Add _recipe'),
             '<Control>R',_('Add another recipe as an ingredient in this recipe'),
             lambda *args: RecSelector(self.rg, self)),
            ])
        self.ingredientEditorOnRowActionGroup.add_actions([
            ('DeleteIngredient',Gtk.STOCK_DELETE,_('Delete'),
             #'Delete', # Binding to the delete key meant delete
             #pressed anywhere would do this, icnluding in a text
             #field
             None,
             None,self.delete_cb),
            ('MoveIngredientUp',Gtk.STOCK_GO_UP,_('Up'),
             '<Control>Up',None,self.ingtree_ui.ingUpCB),
            ('MoveIngredientDown',Gtk.STOCK_GO_DOWN,_('Down'),
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
        if d:
            if 'rangeamount' in d:
                d['amount'] = self.rg.rd._format_amount_string_from_amount(
                    (d['amount'],d['rangeamount'])
                    )
                del d['rangeamount']
            elif 'amount' in d:
                d['amount'] = convert.float_to_frac(d['amount'])
        else:
            d = {}
            d['item'] = line
            d['amount'] = None
            d['unit'] = None
        itr = self.ingtree_ui.ingController.add_new_ingredient(prev_iter=prev_iter,group_iter=group_iter,**d)
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
        with open(file, 'r') as ifi:
            for line in ifi:
                self.ingtree_ui.add_ingredient_from_line(line)

    def import_ingredients_cb (self, *args):
        debug('importIngredientsCB',5) #FIXME
        f=de.select_file(_("Choose a file containing your ingredient list."),action=Gtk.FileChooserAction.OPEN)
        add_with_undo(self, lambda *args: self.importIngredients(f))

    def paste_ingredients_cb (self, *args):
        self.cb = Gtk.Clipboard()
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
        self.copyPasteActionGroup = Gtk.ActionGroup('CopyPasteActionGroup')
        self.copyPasteActionGroup.add_actions([
            ('Copy',Gtk.STOCK_COPY,None,None,None,self.do_copy),
            ('Paste',Gtk.STOCK_PASTE,None,None,None,self.do_paste),
            ('Cut',Gtk.STOCK_CUT,None,None,None,self.do_cut),
            ])
        self.cb = Gtk.Clipboard()
        GObject.timeout_add(500,self.do_sensitize)
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
        if isinstance(widget,Gtk.TextView):
            buf = widget.get_buffer()
            buf.paste_clipboard(self.cb,None,widget.get_editable())
        elif isinstance(widget,Gtk.Editable):
            widget.paste_clipboard()
        else:
            print('What has focus?',widget)

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
        self.ui = Gtk.Builder()
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
        self.recent = []
        self.reccom = []
        for a,l,w in REC_ATTRS:
            if w=='Entry': self.recent.append(a)
            elif w=='Combo': self.reccom.append(a)
            else: raise Exception("REC_ATTRS widget type %s not recognized" % w)
        for a in self.reccom:
            self.rw[a]=self.ui.get_object("%sBox"%a)
            try:
                assert(self.rw[a])
            except:
                print('No recipe editing widget for',a)
                raise
            self.edit_widgets.append(self.rw[a])
            self.rw[a].db_prop = a
            # Set up accessibility
            atk = (find_entry(self.rw[a]) or self.rw[a]).get_accessible()
            atk.set_name(REC_ATTR_DIC[a]+' Entry')
            #self.rw[a].get_children()[0].connect('changed',self.changed_cb)
        for a in self.recent:
            self.rw[a]=self.ui.get_object("%sBox"%a)
            try:
                assert(self.rw[a])
            except:
                print('No recipe editing widget for',a)
                raise
            self.edit_widgets.append(self.rw[a])
            self.rw[a].db_prop = a
            # Set up accessibility
            atk = (find_entry(self.rw[a]) or self.rw[a]).get_accessible()
            atk.set_name(REC_ATTR_DIC[a]+' Entry')
            #self.rw[a].connect('changed',self.changed_cb)
        self.update_from_database()

    def update_from_database (self):
        try:
            self.yields = float(self.current_rec.yields)
        except:
            self.yields = None
            if hasattr(self.current_rec,'yields'):
                debug(_("Couldn't make sense of %s as number of yields")%self.current_rec.yields,0)
        for c in self.reccom:
            debug("Widget for %s"%c,5)
            model = self.rg.get_attribute_model(c)
            self.rw[c].set_model(model)
            self.rw[c].set_entry_text_column(0)
            cb.setup_completion(self.rw[c])
            if c=='category':
                val = ', '.join(self.rg.rd.get_cats(self.current_rec))
            else:
                val = getattr(self.current_rec,c)
            self.rw[c].insert_text(0, val or "")
            if isinstance(self.rw[c],Gtk.ComboBoxText):
                Undo.UndoableEntry(self.rw[c], self.history)
                cb.FocusFixer(self.rw[c])
            else:
                # we still have to implement undo for regular old comboBoxen!
                1
        for e in self.recent:
            if isinstance(self.rw[e],Gtk.SpinButton):
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

    def save (self, recdic):
        for c in self.reccom:
            recdic[c]=str(self.rw[c].get_active_text())
        for e in self.recent:
            if e in INT_REC_ATTRS +  FLOAT_REC_ATTRS:
                recdic[e]=self.rw[e].get_value()
            else:
                recdic[e]=str(self.rw[e].get_text())
        if self.imageBox.edited:
            recdic['image'],recdic['thumb']=self.imageBox.commit()
            self.imageBox.edited=False
        self.emit('saved')
        return recdic

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
                print('Problem with image from recipe.')
                print('Moving ahead anyway.')
                print('Here is the traceback')
                import traceback; traceback.print_exc()
                print("And for your debugging convenience, I'm dumping")
                print("a copy of the faulty image in /tmp/bad_image.jpg")
                import tempfile
                try:
                    dumpto = os.path.join(tempfile.tempdir,'bad_image.jpg')
                    with open(dumpto, 'wb') as ofi:
                        ofi.write(rec.image)
                except:
                    print('Nevermind -- I had a problem dumping the file.')
                    traceback.print_exc()
                    print('(Ignoring this traceback...)')
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
                wwidth = self.win.get_width()
                wheight = self.win.get_height()
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
        filenames = de.select_image("Select Image",action=Gtk.FileChooserAction.OPEN)
        qty = len(filenames)
        if qty == 1:
            fname, = filenames  # unpack the filename
            Undo.UndoableObject(
                lambda *args: self.set_from_file(fname),
                lambda *args: self.remove_image(),
                self.rc.history,
                widget=self.imageW).perform()
            self.edited=True
        else:
            raise ValueError(f"Expected 1 filename, but got {qty}", qty)

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
        self.richTextActionGroup = Gtk.ActionGroup('RichTextActionGroup')
        self.richTextActionGroup.add_toggle_actions([
            ('Bold',Gtk.STOCK_BOLD,None,'<Control>B',None,None),
            ('Italic',Gtk.STOCK_ITALIC,None,'<Control>I',None,None),
            ('Underline',Gtk.STOCK_UNDERLINE,None,'<Control>U',None,None),
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
        self.main = Gtk.ScrolledWindow()
        self.main.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        self.tv = Gtk.TextView()
        self.main.add(self.tv)
        buf = TextBufferMarkup.InteractivePangoBuffer()
        self.tv.set_wrap_mode(Gtk.WrapMode.WORD)
        self.tv.set_buffer(buf)
        self.tv.show()
        self.tv.db_prop = self.prop
        if not self.label:
            print('Odd,',self,'has no label')
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

    def save (self, recdic):
        recdic[self.prop] = self.tv.get_buffer().get_text()
        self.emit('saved')
        return recdic

class InstructionsEditorModule (TextFieldEditor,RecEditorModule):
    name = 'instructions'
    label = _('Instructions')
    prop = 'instructions'

class NotesEditorModule (TextFieldEditor,RecEditorModule):
    name = 'notes'
    prop = 'modifications'
    label = _('Notes')

# Various sub-classes to handle our ingredient treeview

class IngredientController (plugin_loader.Pluggable):

    """Handle updates to our ingredient model.

    Changes are not reported as they happen; rather, we use the
    commit_ingredients method to do sync up our database with what
    we're showing as our database.
    """

    ING_COL = 0
    AMT_COL = 1
    UNIT_COL = 2
    ITEM_COL = 3
    OPTIONAL_COL = 4

    def __init__ (self, ingredient_editor_module):
        self.ingredient_editor_module = ingredient_editor_module;
        self.rg = self.ingredient_editor_module.rg
        self.re = self.ingredient_editor_module.re
        self.new_item_count = 0
        self.commited_items_converter = {}
        plugin_loader.Pluggable.__init__(self,
                                         [IngredientControllerPlugin])

    # Setup methods
    def create_imodel (self, rec):
        self.ingredient_objects = []
        self.current_rec=rec
        ings=self.rg.rd.get_ings(rec)
        ## now we continue with our regular business...
        debug("%s ings"%len(ings),3)
        self.ing_alist=self.rg.rd.order_ings(ings)
        self.imodel = Gtk.TreeStore(GObject.TYPE_PYOBJECT,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_BOOLEAN,
                                    #GObject.TYPE_STRING,
                                    #GObject.TYPE_STRING
                                    )
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
            if not isinstance(self.imodel.get_value(group_iter, 0), str):
                prev_iter = group_iter
                print('fix this old code!')
                import traceback; traceback.print_stack()
                print('(not a real traceback, just a hint for fixing the old code)')
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
        if 'refid' in ingdict and ingdict['refid']:
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
        itr = self.ingredient_editor_module.ingtree_ui.ingController.get_iter_from_persistent_ref(ref)
        orig = self.ingredient_editor_module.ingtree_ui.ingController.get_rowdict(itr)
        Undo.UndoableObject(
            lambda *args: self.update_ingredient_row(itr,**d),
            lambda *args: self.update_ingredient_row(itr,**orig),
            self.ingredient_editor_module.history,
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
        #if ingkey is not None: self.imodel.set_value(iter,5,ingkey)
        #if shop_cat:
        #    self.imodel.set_value(iter,6,shop_cat)
        #elif ingkey and self.re.rg.sl.orgdic.has_key(ingkey):
        #    self.imodel.set_value(iter,6,self.re.rg.sl.orgdic[ingkey])

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
        #self.imodel.set_value(iter, 5, i.ingkey)
        #if shop_cat:
        #    self.imodel.set_value(iter, 6, shop_cat)
        #elif self.rg.sl.orgdic.has_key(i.ingkey):
        #    debug("Key %s has category %s"%(i.ingkey,self.rg.sl.orgdic[i.ingkey]),5)
        #    self.imodel.set_value(iter, 6, self.rg.sl.orgdic[i.ingkey])
        #else:
        #    self.imodel.set_value(iter, 6, None)
        return iter

    def add_group (self, name, prev_iter=None, children_iters=[], fallback_on_append=True):
        if not prev_iter:
            if fallback_on_append: groupiter = self.imodel.append(None)
            else: groupiter = self.imodel.prepend(None)
        else:
            # ALLOW NO NESTING!
            while self.imodel.iter_parent(prev_iter):
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
            print('Odd we are failing to get_paths for ',iters)
            print('Our undo stack looks like this...')
            print(self.ingredient_editor_module.history)
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
                expanded = self.ingredient_editor_module.ingtree_ui.ingTree.row_expanded(
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
            self.ingredient_editor_module.history,
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
            if not i: print('Failed to get reference from',i)
            else: self.imodel.remove(i)

    def do_undelete_iters (self, rowdicts_and_iters):
        for rowdic,prev_iter,ing_obj,children,expanded in rowdicts_and_iters:
            prev_iter = self.get_iter_from_persistent_ref(prev_iter)
            # If ing_obj is a string, then we are a group
            if ing_obj and isinstance(ing_obj, str):
                itr = self.add_group(rowdic['amount'],prev_iter,fallback_on_append=False)
            elif isinstance(ing_obj, int) or not ing_obj:
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
                    if io and not isinstance(io, (str, int, RecRef)):
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
                self.ingredient_editor_module.ingtree_ui.ingTree.expand_row(self.imodel.get_path(itr),True)

    # Get a dictionary describing our current row
    def get_rowdict (self, iter):
        d = {}
        for k,n in [('amount',1),
                    ('unit',2),
                    ('item',3),
                    ('optional',4),
                    ]:
            d[k] = self.imodel.get_value(iter,n)
        ing_obj = self.imodel.get_value(iter,0)
        self.get_extra_ingredient_attributes(
            ing_obj,
            d)
        return d

    @plugin_loader.pluggable_method
    def get_extra_ingredient_attributes (self, ing_obj, ingdict):
        if not hasattr(ing_obj,'ingkey') or not ing_obj.ingkey:
            if ingdict['item']:
                ingdict['ingkey'] = ingdict['item'].split(';')[0]
        else:
            ingdict['ingkey'] = ing_obj.ingkey

    # Get persistent references to items easily

    def get_persistent_ref_from_path (self, path):
        return self.get_persistent_ref_from_iter(
            self.imodel.get_iter(path)
            )

    def get_persistent_ref_from_iter (self, iter):
        uid = self.imodel.get_value(iter,0)
        return uid

    def get_path_from_persistent_ref (self, ref):
        itr = self.get_iter_from_persistent_ref(ref)
        if itr:
            return self.imodel.get_path(
                itr
                )

    #@debug_decorator
    def get_iter_from_persistent_ref (self, ref):
        try:
            if ref in self.commited_items_converter:
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
            if isinstance(ing, str):
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
                else:
                    d['amount']=None
                # Get category info as necessary
                if 'shop_cat' in d:
                    self.rg.sl.orgdic[d['ingkey']] = d['shop_cat']
                    del d['shop_cat']
                d['position']=pos
                d['inggroup']=group
                # If we are a recref...
                if isinstance(ing,RecRef):
                    d['refid'] = ing.refid
                # If we are a real, old ingredient
                if not isinstance(ing, (int, RecRef)):
                    for att in ['amount','unit','item','ingkey','position','inggroup','optional']:
                        # Remove all unchanged attrs from dict...
                        if hasattr(d,att):
                            if getattr(ing,att)==d[att]:
                                del d[att]
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
                        self.ingredient_editor_module.rg.rd.modify_ing_and_update_keydic(ing,d)
                else:
                    d['recipe_id'] = self.ingredient_editor_module.current_rec.id
                    self.commited_items_converter[ing] = self.rg.rd.add_ing_and_update_keydic(d)
                    self.imodel.set_value(iter,0,self.commited_items_converter[ing])
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
                   #_('Shopping Category'):'shop_cat',
                   }

    def __init__ (self, ie, tree):
        self.ingredient_editor_module =ie; self.rg = self.ingredient_editor_module.rg
        self.ingController = IngredientController(self.ingredient_editor_module)
        self.ingTree = tree
        self.ingTree.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.setup_columns()
        self.ingTree.connect("row-activated",self.ingtree_row_activated_cb)
        self.ingTree.connect("key-press-event",self.ingtree_keypress_cb)
        self.selected=True
        #self.selection_changed()
        self.ingTree.get_selection().connect("changed",self.selection_changed_cb)
        self.setup_drag_and_drop()
        self.ingTree.show()

    # Basic setup methods

    def setup_columns (self):
        self.ingColsByName = {}
        self.ingColsByAttr = {}
        for n,head,tog,model,style,expand in [[1,_('Amt'),False,None,None,False],
                                 [2,_('Unit'),False,self.rg.umodel,None,False],
                                 [3,_('Item'),False,None,None,True],
                                 [4,_('Optional'),True,None,None,False],
                                 #[5,_('Key'),False,self.rg.inginfo.key_model,Pango.Style.ITALIC],
                                 #[6,_('Shopping Category'),False,self.shopmodel,Pango.Style.ITALIC],
                                 ]:
            # Toggle setup
            if tog:
                renderer = Gtk.CellRendererToggle()
                renderer.set_property('activatable',True)
                renderer.connect('toggled',self.ingtree_toggled_cb,n,'Optional')
                col=Gtk.TreeViewColumn(head, renderer, active=n)
            # Non-Toggle setup
            else:
                if model:
                    debug('Using CellRendererCombo, n=%s'%n,0)
                    renderer = Gtk.CellRendererCombo()
                    renderer.set_property('model',model)
                    renderer.set_property('text-column',0)
                else:
                    debug('Using CellRendererText, n=%s'%n,0)
                    renderer = Gtk.CellRendererText()
                renderer.set_property('editable',True)
                renderer.connect('edited',self.ingtree_edited_cb,n,head)
                # If we have gtk > 2.8, set up text-wrapping
                try:
                    renderer.get_property('wrap-width')
                except TypeError:
                    pass
                else:
                    renderer.set_property('wrap-mode',Pango.WrapMode.WORD)
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
                col=Gtk.TreeViewColumn(head, renderer, text=n)
            if expand: col.set_expand(expand)
            # Register ourselves...
            self.ingColsByName[head]=col
            if head in self.head_to_att:
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

    def setup_drag_and_drop (self):
        ## add drag and drop support
        targets=[('GOURMET_INTERNAL', Gtk.TargetFlags.SAME_WIDGET, 0),
                 ('text/plain',0,1),
                 ('STRING',0,2),
                 ('STRING',0,3),
                 ('COMPOUND_TEXT',0,4),
                 ('text/unicode',0,5),]
        self.ingTree.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                              targets,
                                              Gdk.DragAction.DEFAULT |
                                              Gdk.DragAction.COPY |
                                              Gdk.DragAction.MOVE)
        self.ingTree.enable_model_drag_dest(targets,
                                            Gdk.DragAction.DEFAULT | Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
        self.ingTree.connect("drag_data_received",self.dragIngsRecCB)
        self.ingTree.connect("drag_data_get",self.dragIngsGetCB)
        self.ingTree.connect('drag-begin',
                             lambda *args: setattr(self,'ss',te.selectionSaver(self.ingTree,0))
                             )
        self.ingTree.connect('drag-end',
                             lambda *args: self.ss.restore_selections()
                             )
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

    def ingtree_row_activated_cb (self, tv, path, col, p=None):
        debug("ingtree_row_activated_cb (self, tv, path, col, p=None):",5)
        itr=self.get_selected_ing()
        i = self.ingController.imodel.get_value(itr,0)
        if isinstance(i,RecRef) or (hasattr(i,'refid') and i.refid):
            rec=self.rg.rd.get_referenced_rec(i)
            if rec:
                self.rg.open_rec_card(rec)
            else:
                de.show_message(parent=self.edit_window,
                                label=_("The recipe %s (ID %s) is not in our database.")%(i.item,
                                                                                          i.refid)
                                )
        else:
            d = self.ingController.get_rowdict(itr)
            #self.re.ie.show(i,d)
            #self.re.ie.ieExpander.set_expanded(True)

    def ingtree_keypress_cb (self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Delete' or keyname == 'BackSpace':
            self.ingredient_editor_module.delete_cb()
            return True


    def selection_changed_cb (self, *args):
        model,rows=self.ingTree.get_selection().get_selected_rows()
        self.selection_changed(rows and True)
        #if self.re.ie.ieExpander.get_expanded():
        #    itr = self.get_selected_ing()
        #    if itr:
        #        i = self.ingController.imodel.get_value(itr,0)
        #        d = self.ingController.get_rowdict(itr)
        #        if i: self.re.ie.show(i,d)
        #        else: self.re.ie.new()
        return True

    def selection_changed (self, selected=False):
        if selected != self.selected:
            if selected: self.selected=True
            else: self.selected=False
            if hasattr(self.ingredient_editor_module,'ingredientEditorOnRowActionGroup'):
                self.ingredient_editor_module.ingredientEditorOnRowActionGroup.set_sensitive(self.selected)

    def ingtree_toggled_cb (self, cellrenderer, path, colnum, head):
        debug("ingtree_toggled_cb (self, cellrenderer, path, colnum, head):",5)
        store=self.ingTree.get_model()
        iter=store.get_iter(path)
        val = store.get_value(iter,colnum)
        obj = store.get_value(iter,0)
        if isinstance(obj, str) and obj.find('GROUP')==0:
            print('Sorry, whole groups cannot be toggled to "optional"')
            return
        newval = not val
        ref = self.ingController.get_persistent_ref_from_iter(iter)
        u = Undo.UndoableObject(
            lambda *args: store.set_value(self.ingController.get_iter_from_persistent_ref(ref),
                                          colnum,newval),
            lambda *args: store.set_value(self.ingController.get_iter_from_persistent_ref(ref),
                                          colnum,val),
            self.ingredient_editor_module.history,
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
        if isinstance(ing, str):
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
                #if msg:
                #    self.re.message(msg)
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
            group = isinstance(dest_ing, str)
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
                    (position==Gtk.TreeViewDropPosition.INTO_OR_BEFORE
                     or
                     position==Gtk.TreeViewDropPosition.INTO_OR_AFTER)
                    ):
                    for i in selected_iters:
                        te.move_iter(mod,i,direction="before",parent=diter)
                elif (position==Gtk.TreeViewDropPosition.INTO_OR_BEFORE
                      or
                      position==Gtk.TreeViewDropPosition.BEFORE):
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
                        print('Odd - I get no iter for ref',r)
                        import traceback; traceback.print_stack()
                        print('Strange indeed! carry on...')
                    else:
                        self.ingTree.get_selection().select_iter(i)
                debug('do_move - inside dragIngsRecCB - DONE',3)
            Undo.UndoableObject(
                do_move,
                uts.restore_positions,
                self.ingredient_editor_module.history,
                widget=self.ingController.imodel).perform()
               #self.ingTree.get_selection().select_iter(new_iter)
        else:
            # if this is external, we copy
            debug('external drag!',2)
            lines = selection.data.split("\n")
            lines.reverse()
            if (position==Gtk.TreeViewDropPosition.BEFORE or
                position==Gtk.TreeViewDropPosition.INTO_OR_BEFORE and not group):
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
                        self.ingredient_editor_module.add_ingredient_from_line(
                            l,
                            group_iter=self.ingController.get_iter_from_persistent_ref(itr_ref)
                            )
                    else:
                        self.ingredient_editor_module.add_ingredient_from_line(
                            l,
                            prev_iter=self.ingController.get_iter_from_persistent_ref(itr_ref)
                            )
            add_with_undo(self.ingredient_editor_module,do_add)
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
        ingredients="\n".join(strings)
        selection.set('text/plain',0,ingredients)
        selection.set('STRING',0,ingredients)
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
                              self.ingredient_editor_module.history,
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
                              self.ingredient_editor_module.history)
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

    def get_previous_iter_and_group_iter (self):
        """Return prev_iter,group_iter"""
        # If there is a selected iter, we treat it as a group to put
        # our entry into or after
        selected_iter = self.getSelectedIter()
        if not selected_iter:
            # default behavior (put last)
            group_iter = None
            prev_iter = None
        elif isinstance(self.ingController.imodel.get_value(selected_iter,0), str):
            # if we are a group
            group_iter = selected_iter
            prev_iter = None
        else:
            # then we are a previous iter...
            group_iter = None
            prev_iter = selected_iter
        return prev_iter,group_iter

    # Edit Callbacks
    def changeUnit (self, new_unit, ingdict):
        """Handed a new unit and an ingredient, we decide whether to convert and return:
        None (don't convert) or Amount (new amount)
        Message (message for our user) or None (no message for our user)"""
        key=ingdict.get('ingkey',None)
        old_unit=ingdict.get('unit',None)
        old_amt=ingdict.get('amount',None)
        if isinstance(old_amt, str):
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
                raise Exception("User cancelled")
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
                           self.ingredient_editor_module.history)
        u.perform()

    def change_group (self, itr, text):
        debug('Undoable group change: %s %s'%(itr,text),3)
        model = self.ingController.imodel
        oldgroup0 = model.get_value(itr,0)
        oldgroup1 = model.get_value(itr,1)
        def get_group_iter (old_value):
            # Somewhat hacky -- our persistent references are stored in
            # the "0" column, which is simply "GROUP text". This means
            # that we can't properly "persist" groups since this chunk of
            # text changes when the group's name changes. In order to
            # remedy, we're relying on the hackish "GROUP name" value +
            # knowing what the previous group value was to make the
            # "persistent" reference work.
            return self.ingController.get_iter_from_persistent_ref("GROUP %s"%old_value)
        def change_my_group ():
            itr = get_group_iter(oldgroup1)
            self.ingController.imodel.set_value(itr,0,"GROUP %s"%text)
            self.ingController.imodel.set_value(itr,1,text)
        def unchange_my_group ():
            itr = get_group_iter(text)
            self.ingController.imodel.set_value(itr,0,oldgroup0)
            self.ingController.imodel.set_value(itr,1,oldgroup1)
        obj = Undo.UndoableObject(change_my_group,unchange_my_group,self.ingredient_editor_module.history)
        obj.perform()


class UndoableTreeStuff:
    def __init__ (self, ic):
        self.ic = ic

    def start_recording_additions (self):
        debug('UndoableTreeStuff.start_recording_additiong',3)
        self.added = []
        self.pre_ss = te.selectionSaver(self.ic.ingredient_editor_module.ingtree_ui.ingTree)
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
        self.added.append(Gtk.TreeRowReference(tm,tm.get_path(itr)))

    def record_positions (self, iters):
        debug('UndoableTreeStuff.record_positions',3)
        self.pre_ss = te.selectionSaver(self.ic.ingredient_editor_module.ingtree_ui.ingTree)
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
    idx = rc.re.module_tab_by_name["ingredients"]
    ing_controller = rc.re.modules[idx].ingtree_ui.ingController
    uts = UndoableTreeStuff(ing_controller)

    def do_it ():
        uts.start_recording_additions()
        method()
        uts.stop_recording_additions()

    UndoableObjectWithInverseThatHandlesItsOwnUndo(
        do_it,
        uts.undo_recorded_additions,
        ing_controller.ingredient_editor_module.history,
        widget=ing_controller.imodel
        ).perform()

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
        #unique_item_vw = self.rd.ingredients_table_not_deleted.counts(self.rd.ingredients_table_not_deleted.item, 'count')
        self.item_model = Gtk.ListStore(str)
        for i in self.rd.get_unique_values('item',table=self.rd.ingredients_table,deleted=False):
            self.item_model.append([i])
        if len(self.item_model)==0:
            from .defaults import defaults
            for i,k,c in defaults.lang.INGREDIENT_DATA:
                self.item_model.append([i])

    def make_key_model (self, myShopCategory):
        # make up the model for the combo box for the ingredient keys
        if myShopCategory:
            unique_key_vw = self.rd.get_unique_values('ingkey',table=self.rd.shopcats_table, shopcategory=myShopCategory)
        else:
            #unique_key_vw = self.rd.get_unique_values('ingkey',table=self.rd.keylookup_table)
            unique_key_vw = self.rd.get_unique_values('ingkey',table=self.rd.ingredients_table)
        # the key model by default stores a string and a list.
        self.key_model = Gtk.ListStore(str)
        keys=[]
        for k in unique_key_vw:
            keys.append(k)

        keys.sort()
        for k in keys:
            self.key_model.append([k])

    def change_key (self, old_key, new_key):
        """One of our keys has changed."""
        keys = [x[0] for x in self.key_model]
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

# Dialog for adding a recipe as an ingredient
class RecSelector (RecIndex):
    """Select a recipe and add it to RecCard's ingredient list"""
    def __init__(self, recGui, ingEditor):
        self.prefs = prefs.get_prefs()
        self.ui=Gtk.Builder()
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
        d = Gtk.Dialog(_("Choose recipe"),
                       self.re.window,
                       Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                        Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
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
        if resp==Gtk.ResponseType.ACCEPT:
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
        table = Gtk.Table()
        self.vbox.add(table);
        self.recButton,self.recAdj = self.make_spinny(val=1,lower=0,
                                                      step_incr=0.5,page_incr=5)
        recLabel = Gtk.Label(label=_('Recipes') + ': ')
        self.recAdj.connect('value_changed',self.update_from_rec)
        self.recAdj.connect('changed',self.update_from_rec)
        table.attach(recLabel,0,1,0,1); recLabel.show()
        table.attach(self.recButton,1,2,0,1); self.recButton.show()
        if rec.yields:
            self.yieldsButton,self.yieldsAdj = self.make_spinny(val=self.rec.yields)
            self.yieldsAdj.connect('value_changed',self.update_from_yield)
            self.yieldsAdj.connect('changed',self.update_from_yield)
            yieldsLabel = Gtk.Label(label=rec.yield_unit.title() + ': ')
            table.attach(yieldsLabel,0,1,1,2); yieldsLabel.show()
            table.attach(self.yieldsButton,1,2,1,2);  self.yieldsButton.show()
        table.show()

    def make_spinny (self, val=1, lower=0, upper=10000, step_incr=1, page_incr=10,
                     digits=2):
        '''return adjustment, spinner widget
        '''
        adj = Gtk.Adjustment(val,
                             lower=lower,upper=upper,
                             step_incr=step_incr,page_incr=page_incr,
                             )
        sb = Gtk.SpinButton(adj)
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

if __name__ == '__main__':
    from . import GourmetRecipeManager
    rg = GourmetRecipeManager.RecGui()
    import pdb
    rc = RecCard(rg,recipe=rg.rd.fetch_one(rg.rd.recipe_table,title='Asparagus Custard Tart'))
    #import pdb
    #pdb.runcall(rc.show_edit)
    #rc.show()
    #rc.show_display()
    #re = RecEditor(rg,recipe=rg.rd.fetch_one(rg.rd.recipe_table))
    #re.show()
    Gtk.main()

if __name__ == '__main__' and False:

    def test_ing_editing (rc):
        rc.show_edit(module=rc.NOTEBOOK_ING_PAGE)
        g = rc.ingtree_ui.ingController.add_group('Foo bar')
        for l in ('''1 c. sugar
        1 c. silly; chopped and sorted
        1 lb. very silly
        1 tbs. extraordinarily silly'''.split('\n')):
            rc.add_ingredient_from_line(l,group_iter=g)
        rc.ingtree_ui.ingController.delete_iters(g)
        rc.undo.emit('activate')

    from . import GourmetRecipeManager
    rg = GourmetRecipeManager.RecGui()
    Gtk.main()
    rg.app.hide()
    try:
        rc = RecCard(rg,rg.rd.fetch_one(rg.rd.recipe_table,title='Black and White Cookies'))
        rc.display_window.connect('delete-event',
                                  lambda *args: Gtk.main_quit()
                                  )
        rc.edit_window.connect('delete-event',lambda *args: Gtk.main_quit())
        #rc.show_edit()
        #rc.rw['title'].set_text('Foo')

        test_ing_editing(rc)
    except:
        rg.app.hide()
        raise
    else:
        Gtk.main()
