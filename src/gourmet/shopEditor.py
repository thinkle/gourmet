import pickle
import re
from pkgutil import get_data

from gi.repository import GObject, Gtk

from .backends import db
from .gtk_extras import WidgetSaver
from .gtk_extras import cb_extras as cb
from .gtk_extras import dialog_extras as de


class ShopEditor:

    """ShopEditor sets up a GUI to allow editing which shopping
    categories correspond to which items throughout the recipe
    database. It is useful for corrections or changes to category info
    en masse and for reordering shopping categories."""

    def __init__ (self, rd=db.recipeManager(), rg=None):
        self.ui = Gtk.Builder()
        self.ui.add_from_string(get_data('gourmet', 'ui/shopCatEditor.ui').decode())
        self.rd = rd
        self.rg = rg
        self.prefs = self.rg.prefs
        self.widget_names = ['treeview', 'searchByBox', 'searchEntry', 'searchButton', 'window',
                             'searchAsYouTypeToggle', 'regexpTog', 'deleteCatButton', 'addCatEntry',
                             'addCatButton']
        for w in self.widget_names:
            setattr(self,w,self.ui.get_object(w))
        # setup entry callback to sensitize/desensitize apply
        self.addCatButton.set_sensitive(False)
        self.addCatEntry.connect('changed',self.addCatEntryChangedCB)
        self.makeTreeModel()
        self.search_string=""
        self.treeModel.set_default_sort_func(self.sort_model_fun)
        self.treeModel.set_sort_column_id(-1,Gtk.SortType.ASCENDING)
        self.filteredModel = self.treeModel.filter_new()
        self.filteredModel.set_visible_func(self.filter_visibility_fun)
        self.setupTreeView()
        self.treeview.set_model(self.filteredModel)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        #self.treeview.set_model(self.treeModel)
        self.ui.connect_signals({
            'iSearch':self.isearchCB,
            'search':self.searchCB,
            'search_as_you_type_toggle':self.search_as_you_typeCB,
            'close_window': lambda *args: self.window.hide() and self.window.destroy(),
            'catUp':self.catUpCB,
            'catDown':self.catDownCB,
            'catTop':self.catTopCB,
            'catBottom':self.catTopCB,
            })
        # to set our regexp_toggled variable
        self.searchByBox.set_active(0)
        self.dont_ask = False
        # setup WidgetSavers
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.searchAsYouTypeToggle,
            self.prefs.get('sautTog',
                           {'active':self.searchAsYouTypeToggle.get_active()}),
            ['toggled']))
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.regexpTog,
            self.prefs.get('regexpTog',
                           {'active':self.regexpTog.get_active()}),
            ['toggled']))

    def dont_ask_cb (self, widget, *args):
        self.dont_ask=widget.get_active()

    def sort_model_fun (model, iter1, iter2, data):
        c1 = model.get_value(iter1, self.CAT_COL)
        if c1 in self.rg.sl.sh.catorder_dic:
            c1_order = self.rg.sl.sh.catorder_dic[c1]
        else:
            c1_order = None
        c2 = model.get_value(iter2, self.CAT_COL)
        if c1 in self.rg.sl.sh.catorder_dic:
            c2_order = self.rg.sl.sh.catorder_dic[c2]
        else:
            c2_order = None
        if c1_order and c2_order:
            compare = c1_order > c2_order
        elif c1 and c2:
            compare = c1 > c2
        else:
            k1 = model.get_value(iter1, self.KEY_COL)
            k2 = model.get_value(iter2, self.KEY_COL)
            if k1 and k2:
                compare = k1 > k2
            else:
                compare = 0
        # iter1 and iter2 are equal
        if compare==0: return 0
        # iter1 precedes iter2
        if compare: return 1
        # iter2 precedes iter1
        else: return 1

    def filter_visibility_fun (self, mod, iter):
        if not self.search_string:
            return True
        str = mod.get_value(iter,self.search_by)
        if not str and self.search_by==self.KEY_COL:
            # then we need to make sure we show key header rows
            # whose items include an item w/ the proper title...
            cat = mod.get_value(iter,self.CAT_COL)
            if cat in self.cat_to_key:
                for itm in self.cat_to_key[cat]:
                    if self.use_regexp:
                        if re.search(self.search_string, itm): return True
                    elif itm.find(self.search_string) >= 0: return True
        if self.use_regexp:
            if re.search(self.search_string, str): return True
        else:
            if str.find(self.search_string) >= 0:
                return True

    def setupTreeView (self):
        self.CAT_COL = 1
        self.KEY_COL = 2
        for n,head in [[self.CAT_COL,'Category'],
                       [self.KEY_COL,'Key'],
                       ]:
            renderer = Gtk.CellRendererText()
            renderer.set_property('editable',True)
            renderer.connect('edited',self.tree_edited,n,head)
            col = Gtk.TreeViewColumn(head, renderer, text=n)
            col.set_resizable(True)
            self.treeview.append_column(col)
            self.treeview.connect('row-expanded',self.populateChild)

    def tree_edited (self, renderer, path_string, text, n, head):
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        iter = self.filteredModel.convert_iter_to_child_iter(self.filteredModel.get_iter(path))
        key = self.treeModel.get_value(iter, self.KEY_COL)
        item = self.treeModel.get_value(iter, self.ITEM_COL)
        children = self.treeModel.iter_children(iter)
        if n==self.KEY_COL and key==text: return
        if n==self.ITEM_COL and item==text: return
        ## make sure they want to make this change
        if not self.dont_ask:
            msg = "Are you sure you want to change the "
            if n==self.KEY_COL: msg += 'key'
            if n==self.ITEM_COL: msg += 'item'
            if item:
                msg += "for \"%s from \"%s\""%(item,key)
            else:
                msg += " from \"%s\" "%key
            msg += " to \"%s\""%text
            if not de.getBoolean(label=msg,
                                 dont_ask_cb=self.dont_ask_cb,
                                 dont_ask_custom_text="Don't ask me before changing keys and items."):
                return
        if children and n==self.KEY_COL:
            self.change_children(key, text, iter)
        else:
            if n==self.KEY_COL:
                self.changeItem(key, item, new_key=text)
            elif n==self.ITEM_COL:
                self.changeItem(key, item, new_item=text)
        self.treeModel.set_value(iter, n, text)

    def change_children (self, key, new_key, iter):
        # if it's children, it means we're changing a key for
        # all cases... and then we just have to change the model
        # so our user knows it worked
        self.changeItem(key, new_key=new_key)
        nn = 0
        child = self.treeModel.iter_nth_child(iter,nn)
        while child:
            self.treeModel.set_value(child, self.KEY_COL, new_key)
            nn += 1
            child = self.treeModel.iter_nth_child(iter,nn)

    def changeItem (self, key, item=None, new_key=None, new_item=None):
        if item:
            vw=self.rd.ingredients_table.select(key=key,item=item)
        else:
            vw=self.rd.ingredients_table.select(key=key)
        for i in vw:
            if new_key:
                i.ingkey=new_key
                self.rd.changed=True
            if new_item:
                i.item=new_item
                self.rd.changed=True

    def makeTreeModel (self):
        self.treeModel = Gtk.TreeStore(GObject.TYPE_PYOBJECT, str, str)
        unique_cat_vw = self.rd.shopcats_table.groupby(self.rd.shopcats_table.category, 'groupvw')
        self.cat_to_key={}
        for c in unique_cat_vw:
            iter=self.treeModel.append(None,[c, pickle.loads(c.category), ""])
            self.cat_to_key[pickle.loads(c.category)]=[]
            for i in c.groupvw:
                #self.treeModel.append(iter,[i,pickle.loads(c.category),i.ingkey])
                self.treeModel.append(iter,[i,pickle.loads(c.category),i.ingkey])
                self.cat_to_key[pickle.loads(c.category)].append(i.ingkey)

    def populateChild (self, tv, iter, path):
        iter = self.filteredModel.convert_iter_to_child_iter(iter)
        n = 0
        child = self.treeModel.iter_nth_child(iter,n)
        while child:
            i = self.treeModel.get_value(child,0)
            recipes = ""
            for ii in i.itemgroup:
                id = ii.id
                r = self.rd.get_rec(ii.id)
                if r: recipes += ", %s"%r.title
            recipes = recipes[2:] # strip the first space
            self.treeModel.set_value(child, 4, recipes)
            n += 1
            child = self.treeModel.iter_nth_child(iter,n)

    def doSearch (self):
        """Do the actual searching."""
        self.search_string = self.searchEntry.get_text()
        search_by_str = cb.cb_get_active_text(self.searchByBox)
        self.use_regexp = self.regexpTog.get_active()
        if search_by_str == 'Key':
            self.search_by = self.KEY_COL
        else:
            #print self.treeModel[-1][self.ITEM_COL]
            self.search_by = self.CAT_COL
        self.filteredModel.refilter()

    def isearchCB (self, *args):
        if self.searchAsYouTypeToggle.get_active():
            self.doSearch()

    def searchCB (self, *args):
        self.doSearch()

    def search_as_you_typeCB (self, *args):
        if self.searchAsYouTypeToggle.get_active():
            self.searchButton.hide()
        else: self.searchButton.show()

    def addCatEntryChangedCB (self, *args):
        if self.addCatEntry.get_text():
            self.addCatButton.set_sensitive(True)
        else: self.addCatButton.set_sensitive(False)


    def catUpCB (self, *args):
        pass

    def catDownCB (self, *args):
        pass

    def catTopCB (self, *args):
        pass

    def catBottomCB (self, *args):
        pass


if __name__ == '__main__':
    ke=ShopEditor()
    Gtk.main()
