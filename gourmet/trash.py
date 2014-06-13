from models import Recipe
from views.recipe import RecIndex
from gglobals import uibase
from gtk_extras import WidgetSaver
from gdebug import debug

import gtk
import os.path

class RecTrash (RecIndex):

    default_searches = [{'column':'deleted','operator':'=','search':True}]
    RESPONSE_DELETE_PERMANENTLY = 1
    RESPONSE_UNDELETE = 2
    RESPONSE_EMPTY_TRASH = 3    
    
    def __init__ (self, rg):
        self.rg = rg
        #self.rmodel = self.rg.rmodel
        self.ui=gtk.Builder()
        self.ui.add_from_file(os.path.join(uibase,'recipe_index.ui'))
        RecIndex.__init__(self, self.ui, self.rg.rd, self.rg)
        self.rvw = self.session.query(Recipe).all()
        self.deleted_recipes = self.really_all_recipes.filter_new()
        self.deleted_recipes.set_visible_func(lambda mod, it: not mod.get_value(it, self.really_all_recipes.get_column_index('deleted')))

        self.create_rmodel(self.rvw)
        self.setup_main_window()

    def setup_main_window (self):
        self.window = gtk.Dialog(_("Trash"),
                                 self.rg.window,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 ("_Empty trash",self.RESPONSE_EMPTY_TRASH,
                                  "_Delete permanently",self.RESPONSE_DELETE_PERMANENTLY,
                                  "_Undelete",self.RESPONSE_UNDELETE,
                                  gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE))
        self.window.set_default_response(gtk.RESPONSE_CLOSE)
        #a = gtk.Alignment(); a.set_padding(12,12,12,12)
        box = gtk.VBox(); box.show()
        box.set_border_width(12)
        #a.add(box); a.show(); 
        #self.window.vbox.add(a)
        self.window.vbox.add(box)
        top_label = gtk.Label(); top_label.set_alignment(0.0,0.5)
        top_label.set_markup('<span weight="bold" size="large">'+_('Trash')+'</span>\n<i>'+_('Browse, permanently delete or undelete deleted recipes')+'</i>')
        box.pack_start(top_label,expand=False,fill=False);top_label.show()
        self.recipe_index_interface = self.ui.get_object('recipeIndexBox')
        self.recipe_index_interface.unparent()
        box.pack_start(self.recipe_index_interface,fill=True,expand=True)
        self.recipe_index_interface.show()
        self.rg.conf.append(WidgetSaver.WindowSaver(self.window,
                                                    self.prefs.get('trash_window',
                                                                   {'size':(600,800)}),
                                                    show=False))
        self.window.connect('response',self.response_cb)
        # So we can let delete key delete recipe when treeview is focused

    def response_cb (self, dialog, response):
        if response==self.RESPONSE_DELETE_PERMANENTLY:
            self.purge_selected_recs()
        elif response==self.RESPONSE_UNDELETE:
            self.undelete_selected_recs()
        elif response==self.RESPONSE_EMPTY_TRASH:
            self.purge_all()
        else:
            self.dismiss()
        self.all_recipes.refilter()

    def dismiss (self, *args):
        self.window.hide()
        return True

    def show (self, *args, **kwargs):
        self.window.show(*args,**kwargs)
        self.srchentry.grab_focus()

    #def setup_search_views (self):
    #    self.last_search = ["",""]
    #    self.rvw = self.rd.fetch_all(self.rd.recipe_table,deleted=True)
    #    self.searches = self.default_searches
    #    self.sort_by = []

    def create_rmodel (self, vw):
        self.really_all_recipes = self.load_recipes(self.rvw)
        self.all_recipes = self.really_all_recipes.filter_new()
        self.all_recipes.set_visible_column(self.really_all_recipes.get_column_index('deleted'))
        self.count = self.all_recipes.iter_n_children(None)
        self.update_page()

    def update_from_db (self):
        self.update_rmodel(self.rg.rd.fetch_all(
            self.rg.rd.recipe_table,deleted=True
            ))

    def undelete_selected_recs (self, *args):
        mod,rr = self.rectree.get_selection().get_selected_rows()
        recs = [mod[path][0] for path in rr]
        msg = ''
        for r in recs:
            msg += r.title + ', '
            self.rg.rd.modify_rec(r,{'deleted':False})
        if msg: msg = msg[0:-2] # cut off the last comma
        self.update_from_db()
        self.rg.redo_search()
        self.rg.message(_('Undeleted recipes ') + msg)

    def purge_selected_recs (self, *args):
        debug("recTreeDeleteRec (self, *args):",5)
        sel = self.rectree.get_selection()
        if not sel: return
        mod,rr=sel.get_selected_rows()
        recs = map(lambda path: mod[path][0],rr)
        self.rg.purge_rec_tree(recs,rr,mod)
        self.update_from_db()

    def purge_all (self, *args):
        self.rg.purge_rec_tree(self.rvw)
        self.update_from_db()

