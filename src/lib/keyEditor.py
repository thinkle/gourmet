import gtk, gtk.glade, gobject, re
from gglobals import *
import WidgetSaver
import cb_extras as cb
import dialog_extras as de
from gettext import gettext as _

class KeyEditor:
    """KeyEditor sets up a GUI to allow editing which keys correspond to which items throughout
    the recipe database. It is useful for corrections or changes to keys en masse."""
    def __init__ (self, rd=None, rg=None):
        self.glade = gtk.glade.XML(os.path.join(gladebase,'keyeditor.glade'))
        self.rd = rd
        self.rg = rg
        self.widget_names = ['treeview', 'searchByBox', 'searchEntry', 'searchButton', 'window',
                             'searchAsYouTypeToggle', 'regexpTog', 'changeKeyEntry', 'changeKeyButton' ]
        for w in self.widget_names:
            setattr(self,w,self.glade.get_widget(w))
        # setup entry callback to sensitize/desensitize apply
        self.changeKeyButton.set_sensitive(False)
        self.changeKeyEntry.connect('changed',self.changeKeyEntryChangedCB)
        # setup completion in entry
        cb.make_completion(self.changeKeyEntry,self.rg.inginfo.key_model)
        self.makeTreeModel()
        self.search_string=""
        self.filteredModel = self.treeModel.filter_new()
        self.filteredModel.set_visible_func(self.filter_visibility_fun)
        self.setupTreeView()
        self.treeview.set_model(self.filteredModel)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        #self.treeview.set_model(self.treeModel)
        self.glade.signal_autoconnect({
            'iSearch':self.isearchCB,
            'search':self.searchCB,
            'search_as_you_type_toggle':self.search_as_you_typeCB,
            'changeKey':self.change_keyCB,
            'close_window': lambda *args: self.window.hide() and self.window.destroy()
            })
        # to set our regexp_toggled variable
        self.searchByBox.set_active(0)
        self.dont_ask = self.rg.prefs.get('dontAskDeleteKey',False)
        # setup WidgetSavers
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.searchAsYouTypeToggle,
            self.rg.prefs.get('sautTog',
                           {'active':self.searchAsYouTypeToggle.get_active()}),
            ['toggled']))
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.regexpTog,
            self.rg.prefs.get('regexpTog',
                           {'active':self.regexpTog.get_active()}),
            ['toggled']))
                
    def dont_ask_cb (self, widget, *args):
        self.dont_ask=widget.get_active()
        self.rg.prefs['dontAskDeleteKey']=self.dont_ask
    
    def filter_visibility_fun (self, mod, iter):
        if not self.search_string:
            return True
        str = mod.get_value(iter,self.search_by)
        if not str and self.search_by==self.ITEM_COL:
            # then we need to make sure we show key header rows
            # whose items include an item w/ the proper title...
            key = mod.get_value(iter,self.KEY_COL)
            if self.key_to_item.has_key(key):
                for itm in self.key_to_item[key]:
                    if self.use_regexp:
                        if re.search(self.search_string, itm): return True
                    elif itm.find(self.search_string) >= 0: return True
        if self.use_regexp:
            if re.search(self.search_string, str): return True
        else:
            if str.find(self.search_string) >= 0:
                return True
        
    def setupTreeView (self):
        self.KEY_COL = 1
        self.ITEM_COL = 2
        self.COUNT_COL = 3
        self.REC_COL = 4
        for n,head in [[self.KEY_COL,_('Key')],
                       [self.ITEM_COL,_('Item')],
                       [self.COUNT_COL,_('Count')],
                       [self.REC_COL, _('Recipes')]]:
            renderer = gtk.CellRendererText()
            if n==self.KEY_COL or n==self.ITEM_COL:
                renderer.set_property('editable',True)
                renderer.connect('edited',self.tree_edited,n,head)
            col = gtk.TreeViewColumn(head, renderer, text=n)
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
            msg = _("Are you sure you want to change the ")
            if n==self.KEY_COL: msg += _('key')
            if n==self.ITEM_COL: msg += _('item')
            if item:
                msg += _("for \"%s from \"%s\"")%(item,key)
            else:
                msg += _(" from \"%s\" ")%key
            msg += _(" to \"%s\"")%text
            if not de.getBoolean(label=msg,
                                 dont_ask_cb=self.dont_ask_cb,
                                 dont_ask_custom_text=_("Don't ask me before changing keys and items.")
                                 ):
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
        # and if we're changing it in all cases, we need to update our
        # inginfo class to get rid of the old key and add the new.
        self.rg.inginfo.change_key(key, new_key)
        
    def changeItem (self, key, item=None, new_key=None, new_item=None):
        if item:
            vw=self.rd.iview.select(key=key,item=item)
        else:
            vw=self.rd.iview.select(key=key)
        for i in vw:
            if new_key:
                i.ingkey=new_key
                self.rd.changed=True                
            if new_item:
                i.item=new_item
                self.rd.changed=True                
        
    def makeTreeModel (self):
        self.treeModel = gtk.TreeStore(gobject.TYPE_PYOBJECT, str, str, int, str)
        unique_key_vw = self.rd.iview.groupby(self.rd.iview.ingkey, 'groupvw')
        self.key_to_item={}
        for k in unique_key_vw:
            if k.ingkey:
                iter=self.treeModel.append(None,[k, k.ingkey, "",len(k.groupvw),""])
                self.unique_item_vw = k.groupvw.groupby(k.groupvw.item, 'itemgroup')
                cnt = 0
                if not self.key_to_item.has_key(k.ingkey): self.key_to_item[k.ingkey]=[]
                for i in self.unique_item_vw:
                    self.key_to_item[k.ingkey].append(i.item)
                    self.treeModel.append(iter,[i,
                                                k.ingkey,
                                                i.item,
                                                len(i.itemgroup),
                                                ""
                                                #recipes
                                                ])
                    
        
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
            self.search_by = self.ITEM_COL
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

    def change_keyCB (self, *args):
        new_key = self.changeKeyEntry.get_text()
        mod,rows = self.treeview.get_selection().get_selected_rows()
        if not new_key:
            de.show_message(_("You haven't entered a key!"))
            return
        if not de.getBoolean(label=_("Are you sure you want the keys\n for all %s selections set to\n \"%s\"")%(len(rows),new_key)):
            return
        for path in rows:
            iter=self.filteredModel.convert_iter_to_child_iter(self.filteredModel.get_iter(path))
            key = self.treeModel.get_value(iter, self.KEY_COL)
            item = self.treeModel.get_value(iter, self.ITEM_COL)
            self.changeItem(key,item,new_key=new_key)
            self.change_children(key, new_key, iter)
            self.treeModel.set_value(iter, self.KEY_COL, new_key)
            
    def changeKeyEntryChangedCB (self, *args):
        if self.changeKeyEntry.get_text():
            self.changeKeyButton.set_sensitive(True)
        else: self.changeKeyButton.set_sensitive(False)
        

            
if __name__ == '__main__':
    ke=KeyEditor()
    gtk.main()
