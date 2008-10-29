#!/usr/bin/env python
import gtk.glade, gtk, gobject, os.path, time, os, sys, re, threading, gtk.gdk, Image, StringIO, pango, string
import rxml_to_metakit, rmetakit, convert, exporter, shopgui, GourmetRecipeManager
from recindex import RecIndex
import prefs, WidgetSaver
import keymanager
import dialog_extras as de
import treeview_extras as te
import cb_extras as cb
from get_pixbuf_from_file import get_pixbuf_from_jpg
import printer
from gdebug import *
from gglobals import *
from gettext import gettext as _


class RecCard (WidgetSaver.WidgetPrefs):
    def __init__ (self, RecGui, recipe=None):
        debug("RecCard.__init__ (self, RecGui):",5)
        from timeEntry import makeTimeEntry
        gtk.glade.set_custom_widget_callbacks(locals())
        self.glade = gtk.glade.XML(os.path.join(gladebase,'recCard.glade'))
        self.timeB = self.glade.get_widget('preptimeBox')
        self.timeB.connect('changed',self.setEdited)
        self.rg = RecGui
        self.prefs = self.rg.prefs
        WidgetSaver.WidgetPrefs.__init__(
            self,
            self.prefs,
            glade=self.glade,
            hideable_widgets=[
            ('handlebox','Toolbar'),
            ('imageFrame','Image'),
            ('ieHandlebox','Ingredient Editor'),
            (['servingsLabel','servingsBox','rcMultCheck'],'Servings'),
            (['cuisineLabel','cuisineBox'],'Cuisine'),
            (['categoryLabel','categoryBox'],'Category'),
            (['preptimeLabel','preptimeBox'],'Preperation Time'),
            (['ratingLabel','ratingBox'],'Rating'),
            (['sourceLabel','sourceBox'],'Source'),
            (['instrExp'],'Instructions'),
            (['modExp'],'Modifications'),
            ],
            basename='rc_hide_')
        self.ImageBox = ImageBox(self)        
        self.rg.sl.sh.init_orgdic()
        self.selected=gtk.TRUE
        self.ie = IngredientEditor(self.rg, self)
        self.serveW = self.glade.get_widget('servingsBox')
        self.multCheckB = self.glade.get_widget('rcMultCheck')
        self.multLabel = self.glade.get_widget('multLabel')
        self.applyB = self.glade.get_widget('saveButton')
        self.revertB = self.glade.get_widget('revertButton')
        self.mult = 1
        self.serveW.connect('changed',self.servingsChange)
        self.serves = float(self.serveW.get_text())
        self.widget = self.glade.get_widget('recCard')
        self.stat = self.glade.get_widget('statusbar1')
        self.contid = self.stat.get_context_id('main')
        self.delButton = self.glade.get_widget('ingDelButton')
        self.toggleReadableMenu = self.glade.get_widget('toggle_readable_units_menuitem')
        self.toggleReadableMenu.set_active(self.prefs.get('readableUnits',True))
        self.toggleReadableMenu.connect('toggled',self.readableUnitsCB)
        self.default_title = _("Recipe Card: ")
        self.create_ingTree()
        self.selection=gtk.TRUE
        self.selection_changed()
        self.initRecipeWidgets()
        self.setEdited(False)
        self.images = []
        if recipe:
            self.updateRecipe(recipe)
        else:
            r=self.rg.rd.new_rec()
            #if not self.ie.visible:
            #    self.ie.visible=True
            #    self.ie.toggleVisible()
            if self.multCheckB.get_active():
                self.multCheckB.set_active(False)
            self.updateRecipe(r)
        self.pref_id = 'rc%s'%self.current_rec.id
        self.conf = []
        self.conf.append(WidgetSaver.WindowSaver(self.widget, self.prefs.get(self.pref_id,{})))
        for name,widget in self.expanders.items():
            self.conf.append(
                WidgetSaver.WidgetSaver(widget,
                                        self.prefs.get('%s%s'%(self.pref_id,
                                                               name),
                                                       {'expanded':widget.get_expanded()}),
                                        signals=['activate'])
                )
        self.glade.signal_autoconnect({
            'rc2shop' : self.addToShopL,
            'rcDelete' : self.delete,
            'rcHide' : self.hide,
            'saveEdits': self.saveEditsCB,
            'addIng' : self.newIngCB,
            'newRec' : self.newRecipeCB,
            'rcToggleMult' : self.multTogCB,
            'toggleEdit' : self.saveEditsCB,
            'rcSave' : self.saveAs,
            'rcEdited' : self.setEdited,
            'setRecImage' : self.ImageBox.set_from_fileCB,
            'delRecImage' : self.ImageBox.removeCB,
            'instrAddImage' : self.addInstrImageCB,
            'rcRevert' : self.revertCB,
            'ieUp' : self.ingUpCB,
            'ieDown' : self.ingDownCB,
            'ieNewGroup' : self.ingNewGroupCB,
            'recRef':lambda *args: RecSelector(self.rg,self),
            'importIngs': self.importIngredientsCB,
            'unitConverter': self.rg.showConverter,
            'ingKeyEditor': self.rg.showKeyEditor,
            'print': self.print_rec,
            'email': self.email_rec,
            'preferences':self.show_pref_dialog,
            })
        self.show()
        # hackish, but focus was acting funny        
        self.rw['title'].grab_focus()

    def multTogCB (self, w, *args):
        debug("multTogCB (self, w, *args):",5)
        if not self.multCheckB.get_active():
            old_mult = self.mult
            self.mult = 1
            self.multLabel.set_text("")
            if old_mult != self.mult:
                self.imodel = self.create_imodel(self.current_rec,mult=self.mult)
                self.ingTree.set_model(self.imodel)
                self.selection_changed()
                self.ingTree.expand_all()
                self.serveW.set_value(float(self.serves_orig))
        
    def modTogCB (self, w, *args):
        debug("modTogCB (self, w, *args):",5)
        if w.get_active():
            self.rw['modifications'].show()
        else:
            self.rw['modifications'].hide()

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
        f = de.select_file(_("Choose an image to insert in instructions... "),action=gtk.FILE_CHOOSER_ACTION_OPEN)
        self.addInstrImage(f)

    def saveEditsCB (self, click=None, click2=None, click3=None):
        debug("saveEditsCB (self, click=None, click2=None, click3=None):",5)
        self.rg.message("Committing edits! (You still need to save changes to make these changes permanent)")
        newdict = {'id': self.current_rec.id}
        for c in self.reccom:
            newdict[c]=self.rw[c].entry.get_text()
        for e in self.recent:
            if e=='servings':
                newdict[e]=self.serves_orig
            else:
                newdict[e]=self.rw[e].get_text()
        for t in self.rectexts:
            buf = self.rw[t].get_buffer()
            newdict[t]=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if self.ImageBox.edited:
            self.ImageBox.commit()
            self.ImageBox.edited=False
            newdict['thumb']=self.current_rec.thumb
            newdict['image']=self.current_rec.image
        debug("modify_rec, newdict=%s"%newdict,5)            
        self.rg.rd.modify_rec(self.current_rec,newdict)
        ## then, we remove the duplicate item
        self.rg.rd.rview.remove(self.rg.rd.rview.filter(lambda row: self.are_equal(self.current_rec,row)))
        self.setEdited(False)
        ## if our title has changed, we need to update menus
        if newdict.has_key('title'):
            self.widget.set_title("%s %s"%(self.default_title,self.current_rec.title))
            self.rg.updateViewMenu()
            
    def delete (self, *args):
        debug("delete (self, *args):",2)
        self.rg.delete_rec(self.current_rec)
        debug("delete finished",2)
    
    def are_equal (self, obj1, obj2):
        debug("are_equal (self, obj1, obj2):",5)
        """A lambda-syntax-necessitated hack"""
        if obj1 == obj2:
            return True
        else:
            return False

    def addToShopL (self, *args):
        debug("addToShopL (self, *args):",5)
        d = shopgui.getOptionalIngDic(self.rg.rd.get_ings(self.current_rec),self.mult)
        self.rg.sl.addRec(self.current_rec,self.mult,d)
        self.rg.sl.show()

    def getServes (self):
        debug("getServes (self):",5)
        txt = self.serveW.get_text()
        if txt != "":
            self.serves = float(self.serveW.get_text())
        return self.serves

    def servingsChange (self, *args):
        debug("servingsChange (self, *args):",5)
        self.getServes()
        if self.multCheckB.get_active():
            if self.serves_orig == 0 or not self.serves_orig:
                ## a hack to avoid a divide-by-zero error
                ## in case someone has nonsensically created
                ## a recipe of 0 servings
                self.serves_orig = 1
            self.mult = self.serves / self.serves_orig
            if self.mult==1:
                self.multLabel.set_text("")
            else:
                self.multLabel.set_text("x%s"%convert.float_to_frac(self.mult))
            self.imodel = self.create_imodel(self.current_rec,mult=self.mult)
            self.ingTree.set_model(self.imodel)
            self.ingTree.expand_all()
            self.selection_changed()
        else:
            if (self.serves != self.serves_orig) and not (self.serves == 1 and not self.serves_orig):
                self.serves_orig=self.serves
                self.setEdited(True)

    def initRecipeWidgets (self):
        debug("initRecipeWidgets (self):",5)
        self.expanders = {'instructions':self.glade.get_widget('instrExp'),
                           'modifications':self.glade.get_widget('modExp'),
                          'attributes':self.glade.get_widget('detExp'),
                          'ingredients':self.glade.get_widget('ingExp'),
                          'ieExpander':self.glade.get_widget('ieExpander')}
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
            self.rw[a].get_children()[0].connect('changed',self.setEdited)
        for a in self.recent:
            self.rw[a]=self.glade.get_widget("%sBox"%a)            
        for t in self.rectexts:
            self.rw[t]=self.glade.get_widget("%sText"%t)
            self.rw[t].get_buffer().connect('changed',self.setEdited)

    def newRecipeCB (self, *args):
        debug("newRecipeCB (self, *args):",5)
        self.rg.newRecCard()

    def getSelectedIter (self):
        debug("getSelectedIter",4)
        if len(self.imodel)==0:
            return None
        try:
            ts,paths=self.ingTree.get_selection().get_selected_rows()
            lpath=paths[-1]
            group=ts.get_iter(lpath)
        except:
            debug("getSelectedIter: there was an exception",0)            
            group=None
        return group

    def newIngCB (self, *args):
        d={'id':self.current_rec.id}
        ing=self.rg.rd.add_ing(d)
        group=self.getSelectedIter()
        debug("group=%s"%group,5)
        iter=self.add_ingredient(self.imodel,ing,self.mult,group) #we return iter
        path=self.imodel.get_path(iter)
        # open up (in case we're in a group)
        self.ingTree.expand_to_path(path)
        self.ingTree.set_cursor(path,self.ingColsByName[_('Amt')])
        #self.ingTree.get_selection().select_iter(iter)
        self.ingTree.grab_focus()

    def ingUpCB (self, *args):
        def moveup (ts, path, itera):            
            if itera:
                prev=self.path_next(path,-1)
                prev_iter=ts.get_iter(prev)
                te.move_iter(ts,itera,sibling=prev_iter,direction="before")
                self.ingTree.get_selection().unselect_path(path)
                self.ingTree.get_selection().select_path(prev)
        ts,paths = self.ingTree.get_selection().get_selected_rows()
        self.pre_modify_tree()        
        paths.reverse()
        for p in paths:
            itera = ts.get_iter(p)
            moveup(ts,p,itera)
        self.commit_positions()
        self.post_modify_tree()
        
    def ingDownCB (self, *args):
        #ts, itera = self.ingTree.get_selection().get_selected()
        def movedown (ts, path, itera):
            if itera:
                next = ts.iter_next(itera)
                te.move_iter(ts,itera,sibling=next,direction="after")
                if next:
                    next_path=ts.get_path(next)
                else:
                    next_path=path
                self.ingTree.get_selection().unselect_path(path)
                self.ingTree.get_selection().select_path(self.path_next(next_path,1))
        ts,paths = self.ingTree.get_selection().get_selected_rows()
        self.pre_modify_tree()
        paths.reverse()        
        for p in paths:
            itera = ts.get_iter(p)
            movedown(ts,p,itera)
            #selected_foreach(movedown)
        self.commit_positions()
        self.post_modify_tree()
        
    def path_next (self, path, inc=1):
        """Return the path NEXT rows after PATH. Next can be negative, in
        which case we get previous paths."""
        next=list(path[0:-1])
        last=path[-1]
        last += inc
        if last < 0:
            last=0
        next.append(last)
        next=tuple(next)
        return next

    def ingNewGroupCB (self, *args):
        self.add_group(_('New Group'),self.imodel,prev_iter=self.getSelectedIter())

    def resetIngList (self, rec=None):
        debug("resetIngList (self, rec=None):",5)
        if not rec:
            rec=self.current_rec
        self.imodel = self.create_imodel(rec,mult=self.mult)
        self.ingTree.set_model(self.imodel)
        self.selection_changed()
        self.ingTree.expand_all()

    def updateRecipe (self, rec, show=True):
        debug("updateRecipe (self, rec):",5)
        if not self.edited or de.getBoolean(parent=self.widget,
                                         label=_("Abandon your edits to %s?")%self.current_rec.title):
            self.updateRec(rec)
            if show:
                self.show()

    def revertCB (self, *args):
        if de.getBoolean(parent=self.widget,
                      label=_("Are you sure you want to abandon your changes?"),
                         cancel=False):
            self.updateRec(self.current_rec)

    def updateRec (self, rec):
        debug("updateRec (self, rec):",5)
        """If handed an ID, we'll grab the rec"""
        if type(rec) == type(""):
            rec=self.rg.rd.get_rec(rec)
        self.current_rec = rec
        try:
            self.serves_orig = float(self.current_rec.servings)
            self.serveW.set_value(float(self.serves_orig))
        except:
            self.serves_orig = None
            self.multCheckB.set_active(False)
            if hasattr(self.current_rec,'servings'):
                debug(_("Couldn't make sense of %s as number of servings")%self.current_rec.servings,0)
        self.serves = self.serves_orig
        self.servingsChange()
        self.resetIngList(rec)
        for c in self.reccom:
            debug("Widget for %s"%c,5)
            slist = self.rg.rd.get_unique_values(c)
            if not slist:
                self.rg.rd.get_default_values(c)
            cb.set_model_from_list(self.rw[c],slist)
            cb.setup_completion(self.rw[c])
            self.rw[c].entry.set_text(getattr(rec,c))            
        for e in self.recent:
            self.rw[e].set_text(getattr(rec,e))
        for t in self.rectexts:
            w=self.rw[t]
            b=w.get_buffer()
            try:
                #txt=unicode(getattr(rec,t))
                txt = getattr(rec,t).encode('utf8','ignore')
                #txt = getattr(rec,t).decode()
            except UnicodeDecodeError:
                txt = getattr(rec,t)
                debug('UnicodeDecodeError... trying to force our way foreward',0)
                debug('We may fail to display this: %s'%txt,0)
                debug('Type = %s'%type(txt),0)
                raise
            b.set_text(txt)
            if re.match('^\s*$',getattr(rec,t)):
                #self.expanders[t].set_expanded(gtk.FALSE)
                self.expanders[t].set_property('expanded',gtk.FALSE)
                #self.togButtons[t].set_active(gtk.FALSE)
            else:
                #nself.expanders[t].set_expanded(gtk.TRUE)
                self.expanders[t].set_property('expanded',gtk.TRUE)                
                #self.togButtons[t].set_active(gtk.TRUE)
        self.servingsChange()
        self.ImageBox.get_image()
        self.ImageBox.edited=False
        self.setEdited(False)
                
    def create_ingTree (self, rec=None, mult=1):
        debug("create_ingTree (self, rec=None, mult=1):        ",5)
        self.ingTree = self.glade.get_widget('ingTree')
        self.ingTree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.ingTree.expand_all()
        self.ingColsByName = {}
        for n,head,tog,style in [[1,_('Amt'),False,None],
                                 [2,_('Unit'),False,None],
                                 [3,_('Item'),False,None],
                                 [4,_('Optional'),True,None],
                                 [5,_('Key'),False,pango.STYLE_ITALIC],
                                 [6,_('Shopping Category'),False,pango.STYLE_ITALIC],
                                 ]:
            if tog:
                renderer = gtk.CellRendererToggle()
                renderer.set_property('activatable',gtk.TRUE)
                renderer.connect('toggled',self.ingtree_toggled_cb,4,'Optional')
                col=gtk.TreeViewColumn(head, renderer, active=n)
            else:
                renderer = gtk.CellRendererText()
                renderer.set_property('editable',gtk.TRUE)
                renderer.connect('edited',self.ingtree_edited_cb,n,head)
                if style:
                    renderer.set_property('style',style)
                col=gtk.TreeViewColumn(head, renderer, text=n)
            self.ingColsByName[head]=col
            col.set_reorderable(gtk.TRUE)
            col.set_resizable(gtk.TRUE)
            self.ingTree.append_column(col)
        self.setupShopPopupMenu()
        self.ingTree.connect("row-activated",self.ingTreeClickCB)
        self.ingTree.connect("button-press-event",self.ingtree_click_cb)
        self.ingTree.get_selection().connect("changed",self.selection_changedCB)
        self.ingTree.show()
        ## add drag and drop support
        #self.ingTree.drag_dest_set(gtk.DEST_DEFAULT_ALL,
        #                           [("text/plain",0,0)],
        #                           gtk.gdk.ACTION_COPY)
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
        if len(self.rg.rd.rview) > 1:
            if not rec:
                rec = self.rg.rd.rview[1]
            self.imodel = self.create_imodel(rec, mult=1)
            self.ingTree.set_model(self.imodel)
            self.selection_changed()
            self.ingTree.expand_all()
            #self.ingTree.set_search_column(self.ingTreeSearchColumn)
            self.ingTree.set_search_equal_func(self.my_isearch)

    def my_isearch (self, mod, col, key, iter, data=None):
        # we ignore column info and search by item
        val = mod.get_value(iter,3)
        # and by key
        val += mod.get_value(iter,5)
        if val.lower().find(key.lower()) != -1:
            return False
        else:
            return True
        
    def ingtree_click_cb (self, tv, event):
        debug("ingtree_click_cb",5)
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
            self.shoppop.popup(None,None,None,0,0)
            return True

    def setupShopPopupMenu (self):
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
                       parent=self.widget)
            if not i:
                return
            regenerate_menu=True
        self.rg.sl.orgdic[key]=i
        mod.set_value(self.shoppop_iter,6,i)
        if regenerate_menu:
            self.setupShopPopupMenu()

    def selection_changedCB (self, *args):
        v=self.ingTree.get_selection().get_selected_rows()[1]
        if v: selected=gtk.TRUE
        else: selected=gtk.FALSE
        self.selection_changed(v)
        return gtk.TRUE
    
    def selection_changed (self, selected=gtk.FALSE):
        if selected != self.selected:
            if selected: self.selected=gtk.TRUE
            else: self.selected=gtk.FALSE
            if self.delButton:
                self.delButton.set_sensitive(self.selected)
            else: debug("No delButton!",2)

    def ingtree_toggled_cb (self, cellrenderer, path, colnum, head):
        debug("ingtree_toggled_cb (self, cellrenderer, path, colnum, head):",5)
        store=self.ingTree.get_model()
        iter=store.get_iter(path)
        val = store.get_value(iter,colnum)
        newval = not val
        store.set_value(iter,colnum,newval)
        ing=store.get_value(iter,0)
        if head==_('Optional'):
            if newval:
                self.rg.rd.modify_ing(ing, {'optional':'yes'})
            else:
                self.rg.rd.modify_ing(ing, {'optional':'no'})
        
            
    def ingtree_edited_cb (self, renderer, path_string, text, colnum, head):
        debug("ingtree_edited_cb (self, renderer, path_string, text, colnum, head):",5)
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.ingTree.get_model()
        iter = store.get_iter(path)
        ing=self.selectedIng()
        if head==_('Shopping Category'):
            self.rg.sl.orgdic[ing.key]=text
            store.set_value(iter, colnum, text)            
        else:
            head_to_att = {_('Amt'):'amount',
                           _('Unit'):'unit',
                           _('Item'):'item',
                           _('Key'):'key'}
            attr=head_to_att[head]
            if attr=='amount':
                if type(store.get_value(iter,0)) != type(""):
                    # if we're not a group
                    ntext=convert.frac_to_float(text)
                    if not ntext:
                        show_amount_error(text)
                        raise "Amount is not a number!"
                    text = ntext
            d={attr:text}
            if attr=='item':
                d['key']=self.rg.rd.km.get_key(text)
                store.set_value(iter,5,d['key'])
            self.rg.rd.modify_ing(ing,d)
            if d.has_key('key'):
                ## if the key has been changed and the shopping category is not set...
                ## COLUMN NUMBER FOR Shopping Category==6
                shopval=store.get_value(iter, 6)
                debug('Shopping Category value was %s'%shopval,4)
                if shopval:
                    self.rg.sl.orgdic[d['key']]=shopval
                else:
                    if self.rg.sl.orgdic.has_key(text):
                        debug('Setting new shopping category!',2)
                        store.set_value(iter, 6, self.rg.sl.orgdic[text])
            store.set_value(iter, colnum, text)
                    
    def dragIngsRecCB (self, widget, context, x, y, selection, targetType,
                         time):
        debug("dragIngsRecCB (self=%s, widget=%s, context=%s, x=%s, y=%s, selection=%s, targetType=%s, time=%s)"%(self, widget, context, x, y, selection, targetType, time),3)
        drop_info=self.ingTree.get_dest_row_at_pos(x,y)
        mod=self.ingTree.get_model()
        if drop_info:
            path, position = drop_info
            diter = mod.get_iter(path)
            dest_ing=mod.get_value(diter,0)
            if type(dest_ing)==type(""): group=True
            else: group=False
            debug('drop_info good, GROUP=%s'%group,5)
            #new_iter=mod.append(None)
            #path=mod.get_path(new_iter)
        else:
            diter = None
            group = False
            position = None
        #self.pre_modify_tree()            
        if str(selection.target) == 'GOURMET_INTERNAL':
               # if this is ours, we move it
               self.selected_iter.reverse() # all things must go backwards in treeView land...
               if (group and
                   (position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                    or
                    position==gtk.TREE_VIEW_DROP_INTO_OR_AFTER)
                   ):
                   self.pre_modify_tree()
                   for i in self.selected_iter:
                       te.move_iter(mod,i,sibling=diter,direction="before",parent=diter)
                   self.post_modify_tree()
               elif (position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                     or
                     position==gtk.TREE_VIEW_DROP_BEFORE):
                   self.pre_modify_tree()
                   for i in self.selected_iter:
                       te.move_iter(mod,i,sibling=diter,direction="before")
                   self.post_modify_tree()                       
               else:
                   self.pre_modify_tree()
                   for i in self.selected_iter:
                       te.move_iter(mod,i,sibling=diter,direction="after")
                   self.post_modify_tree()                       
               #self.ingTree.get_selection().select_iter(new_iter)
        else:
            # if this is external, we copy
            debug('external drag!',2)
            for l in selection.data.split("\n"):
                self.add_ingredient_from_line(l)
        self.commit_positions()
        debug("restoring selections.")
        #self.post_modify_tree()
        debug("done restoring selections.")        

    def add_ingredient_from_line (self, line):
        """Add an ingredient to our list from a line of plain text"""
        d=self.rg.rd.ingredient_parser(line, conv=self.rg.conv)
        self.pre_modify_tree()
        if d:
            d['id']=self.current_rec.id
            i=self.rg.rd.add_ing(d)
            iter=self.add_ingredient(self.imodel,i,self.mult)
            self.ss.add_selection(iter)
        self.post_modify_tree()

    def pre_modify_tree (self):
        """This shouldn't really be necessary, but I'm getting
        a lot of bizarre behavior and segfaults from modifying
        the tree while connected.
        So, this should be called before adding, deleting or
        moving rows in our model"""
        debug('pre_modify_tree called',5)
        self.ss = te.selectionSaver(self.ingTree)
        debug('disconnecting tree')
        self.ingTree.set_model(empty_model)
        debug('pre_modify_tree done')

    def post_modify_tree (self):
        """And this must be called after adding, deleting or
        moving rows in our model."""
        debug('post_modify_tree called')
        self.ingTree.set_model(self.imodel)
        debug('expanding all')        
        self.ingTree.expand_all()
        debug('restoring selections')                
        self.ss.restore_selections()
        debug('post_modify_tree done')
        
    def commit_positions (self):
        debug("Committing positions",4)
        iter=self.imodel.get_iter_first()
        self.edited=True
        n=0
        def commit_iter(iter,pos,group=None):
            debug("iter=%s,pos=%s,group=%s"%(iter,pos,group),5)
            ing=self.imodel.get_value(iter,0)
            if type(ing)==type(""):
                group=self.imodel.get_value(iter,1)
                i=self.imodel.iter_children(iter)
                while i:
                    pos=commit_iter(i,pos,group)
                    i=self.imodel.iter_next(i)
            else:
                ing.position=pos
                if group: ing.group=group
                pos+=1
            return pos
        while iter:
            n=commit_iter(iter,n)
            iter=self.imodel.iter_next(iter)
            debug("Next iter = %s"%iter)
        debug("Done committing positions",4)

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
        

    def selectedIng (self):
        debug("selectedIng (self):",5)
        path, col = self.ingTree.get_cursor()
        if path:
            itera = self.ingTree.get_model().get_iter(path)
        else:
            tv,rows = self.ingTree.get_selection().get_selected_rows()
            if len(rows) > 0:
                itera = rows[0]
            else:
                itera=None
        if itera: return self.ingTree.get_model().get_value(itera,0)
        else: return None
    
    def ingTreeClickCB (self, tv, path, col, p=None):
        debug("ingTreeClickCB (self, tv, path, col, p=None):",5)
        i=self.selectedIng()
        if hasattr(i,'refid') and i.refid:
            rec=self.rg.rd.get_rec(i.refid)
            if rec:
                self.rg.openRecCard(rec)
            else:
                de.show_message(parent=self.widget, label=_("The recipe %s (ID %s) is not in our database.")%(i.item,
                                                                                                           i.refid))
        else: self.ie.show(self.selectedIng())

    def create_imodel (self, rec, mult=1):
        debug("create_imodel (self, rec, mult=1):",5)
        ings=self.rg.rd.get_ings(rec)
        debug("%s ings"%len(ings),3)
        ing_alist=self.rg.rd.order_ings(ings)
        model = gtk.TreeStore(gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_BOOLEAN,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)
        for g,ings in ing_alist:
            if g:
                g=self.add_group(g,model)
            for i in ings:
                debug('adding ingredient %s'%i.item,4)
                self.add_ingredient(model, i, mult, g)
        return model

    def add_group (self, name, model, prev_iter=None):
        debug('add_group',5)
        if not prev_iter:
            groupiter = model.append(None)
        else:
            groupiter = model.insert_after(None,prev_iter,None)
        model.set_value(groupiter, 0, "GROUP %s"%name)
        model.set_value(groupiter, 1, name)
        debug('add_group returning %s'%groupiter,5)
        return groupiter

    def add_ingredient (self, model, ing, mult, group_iter=None):
        """group_iter is an iter to put our ingredient inside of.
        If group_iter is not a group but an ingredient, we'll insert our
        ingredient after it"""
        debug("add_ingredient (self=%s, model=%s, ing=%s, mult=%s, group_iter=%s):"%(self, model, ing, mult, group_iter),5)
        i = ing
        if group_iter:
            if type(model.get_value(group_iter, 0))==type(""):
                debug("Adding to group",4)
                iter = model.append(group_iter)
            else:
                iter = model.insert_after(None, group_iter, None)
                debug("Adding after iter",5)            
        else:
            iter = model.insert_before(None, None, None)
        conv = self.rg.conv
        if self.prefs.get('readableUnits',True):
            amt,unit = conv.adjust_unit(float(i.amount)*mult,i.unit)
        else:
            amt,unit = float(i.amount)*mult,i.unit
        amt = convert.float_to_frac(amt)
        if unit != i.unit:
            debug('Automagically adjusting unit: %s->%s'%(i.unit,unit),0)
        model.set_value(iter, 0, i)
        model.set_value(iter, 1, amt)
        model.set_value(iter, 2, unit)
        model.set_value(iter, 3, i.item)
        if i.optional=='yes':
            opt=gtk.TRUE
        else:
            opt=gtk.FALSE
        model.set_value(iter, 4, opt)
        model.set_value(iter, 5, i.key)
        if self.rg.sl.orgdic.has_key(i.key):
            debug("Key %s has category %s"%(i.key,self.rg.sl.orgdic[i.key]),5)
            model.set_value(iter, 6, self.rg.sl.orgdic[i.key])
        else:
            model.set_value(iter, 6, None)
        return iter

    def importIngredientsCB (self, *args):
        debug('importIngredientsCB',0) #FIXME
        f=de.select_file(_("Choose a file containing your ingredient list."),action=gtk.FILE_CHOOSER_ACTION_OPEN)
        self.importIngredients(f)
        
    def importIngredients (self, file):
        ifi=open(file,'r')
        for line in ifi:
            self.add_ingredient_from_line(line)

    def saveAs (self, *args):
        debug("saveAs (self, *args):",5)
        #opt = de.getOption(label=_("Export recipe as..."),options=[[_("Mealmaster"),"mmf"],[_("HTML"),"htm"],[_("Plain Text"),"txt"],[_("Rich Text Format"),"rtf"]])
        opt = self.prefs.get('save_recipe_as','html')
        saveas_filters = [[_('RTF'),['application/rtf'],['*.rtf','*.RTF']],
                                   [_('Plain Text'),['text/plain'],['*.txt','*.TXT']],
                                   [_('HTML Web Page'),['text/html'],['*.html','*.htm','*.HTM','*.HTML']],
                                   [_('Mealmaster file'),['text/mmf'],['*.mmf','*.MMF']],
                                   ]
        fn,exp_type=de.saveas_file(_("Save recipe as..."),
                          filename="~/%s.%s"%(self.current_rec.title,opt),
                          filters=saveas_filters)
        if not fn: return
        if not exp_type:
            de.show_message(_('Gourmet cannot export file of type "%s"')%ext)
            return
        out=open(fn,'w')
        if exp_type==_('HTML Web Page'):
            exporter.html_exporter(self.rg.rd,self.current_rec,out,conv=self.rg.conv)
        elif exp_type==_('Plain Text'):
            try:
                exporter.exporter(self.rg.rd,self.current_rec,out,conv=self.rg.conv)
                self.message(_('Recipe saved as Plain Text file %s')%fn)
            except:
                de.show_message(_('Unable to save %s')%fn)
                raise
        elif exp_type==_('Mealmaster file'):
            try:
                exporter.mealmaster_exporter(self.rg.rd,self.current_rec,out,conv=self.rg.conv)
                self.message(_('Recipe saved as Mealmaster file %s')%fn)
            except:
                self.message(_('Unable to save %s')%fn)
                raise
        elif exp_type==_('RTF'):
            try:
                import rtf_exporter
                rtf_exporter.rtf_exporter(self.rg.rd,self.current_rec,out,conv=self.rg.conv)
            except ImportError:
                de.show_message(message=_('Gourmet is currently unable to export RTF'), submessage=_('You need to install PyRTF to export RTF.\nGo to http://pyrtf.sourceforge.net if you wish to download it.'))
            except:
                de.show_message(_('Unable to save %s'%fn))
                raise
        out.close()
        # set prefs for next time
        ext=os.path.splitext(fn)[1]
        self.prefs['save_recipe_as']=ext

    def setEdited (self, boolean=True):
        debug("setEdited (self, boolean=True):",5)
        self.edited=boolean
        if boolean:
            self.applyB.set_sensitive(gtk.TRUE)
            self.revertB.set_sensitive(gtk.TRUE)
            self.message(_("You have unsaved changes."))
        else:
            self.applyB.set_sensitive(gtk.FALSE)
            self.revertB.set_sensitive(gtk.FALSE)
            self.message(_("There are no unsaved changes."))

    def hide (self, *args):
        debug("hide (self, *args):",5)
        if self.edited:
            test=de.getBoolean(label=_("Save edits to %s before closing?")%self.current_rec.title,cancel_returns='CANCEL')
            if test=='CANCEL': return True
            elif test:
                self.saveEditsCB()
            else: self.edited=False #to avoid multiple dialogs if this gets called twice somehow
        # save our position
        for c in self.conf:
            c.save_properties()
        self.widget.hide()
        # delete it from main apps list of open windows
        self.rg.del_rc(self.current_rec.id)
        #return True
        # now we destroy old recipe cards
        
    def show (self, *args):
        debug("show (self, *args):",5)
        self.widget.show()
        try:
            self.widget.set_title("%s %s"%(self.default_title,self.current_rec.title))
            self.widget.present()
        except:
            self.widget.grab_focus()

    def email_rec (self, *args):
        if self.edited:
            if de.getBoolean(label=_("You have unsaved changes."),
                             sublabel=_("Apply changes before e-mailing?")):
                self.saveEditsCB()
        import recipe_emailer
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
                            dialog_parent=self.widget,
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
        self.image = None
        changed=False

    def get_image (self, rec=None):
        debug("get_image (self, rec=None):",5)
        if not rec:
            rec=self.rc.current_rec
        if rec.image:
            self.set_from_string(rec.image)
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
        """Put current image in database"""
        if self.image:
            file = StringIO.StringIO()
            self.image.save(file,"JPEG")
            self.rc.current_rec.image=file.getvalue()
            file = StringIO.StringIO()
            self.thumb.save(file,"JPEG")
            self.rc.current_rec.thumb=file.getvalue()
            
        else:
            self.rc.current_rec.image=""
            self.rc.current_rec.thumb=""

    def resize_image (self, image, width=None, height=None):
        debug("resize_image (self, image, width=None, height=None):",5)
        """Resize an image to have a maximum width=width or height=height.
        We only shrink, we don't grow."""
        iwidth,iheight=image.size
        resized=False
        if width and iwidth > width:
            newheight=int((float(width)/float(iwidth)) * iheight)
            if not height or newheight < height:
                retimage=image.resize((width, newheight))
                resised=True
        if not resized and height and iheight > height:
            newwidth = int((float(height)/float(iheight)) * iwidth)
            retimage = image.resize((newwidth,height))
            resized=True
        if resized:
            return retimage
        else:
            return image

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
            self.image=self.resize_image(self.image,wwidth,wheight)
            self.thumb=self.resize_image(self.image,40,40)
            file = StringIO.StringIO()            
            self.image.save(file,'JPEG')
            self.set_from_string(file.getvalue())
            file.close()
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
        pb=get_pixbuf_from_jpg(string)
        self.imageW.set_from_pixbuf(pb)
        self.show_image()

    def set_from_file (self, file):
        debug("set_from_file (self, file):",5)
        self.image = Image.open(file)
        self.draw_image()        
        
    def set_from_fileCB (self, *args):
        debug("set_from_fileCB (self, *args):",5)
        f=de.select_image("Select Image",action=gtk.FILE_CHOOSER_ACTION_OPEN)
        if f:
            self.set_from_file(f)
            self.rc.setEdited(True)
            self.edited=True

    def removeCB (self, *args):
        debug("removeCB (self, *args):",5)
        if de.getBoolean(label="Are you sure you want to remove this image?",
                      parent=self.rc.widget):
            self.rc.current_rec.image=''
            self.image=None
            self.draw_image()
            self.edited=True
            self.rc.setEdited(True)
            
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

    def init_dics (self):
        self.orgdic = self.rg.sl.sh.orgdic
        # setup shopbox
        self.shopcats = self.rg.sl.sh.get_orgcats()        
        
    def setup_comboboxen (self):
        # setup combo box for unitbox
        debug('start setup_comboboxen()',3)
        self.unitBox.set_model(self.rg.umodel)        
        if len(self.rg.umodel) > 6:
            self.unitBox.set_wrap_width(2)
            if len(self.rg.umodel) > 10:
                self.unitBox.set_wrap_width(3)
        self.unitBox.set_text_column(0)
        cb.setup_completion(self.unitBox) # add autocompletion
        # setup combo box for keybox

        def setup_keybox (model):
            self.keyBox.set_model(model.filter_new())        
            self.keyBox.set_text_column(0)
            if len(model) > 5:
                self.keyBox.set_wrap_width(3)
                
        setup_keybox(self.rg.inginfo.key_model)
        self.rg.inginfo.disconnect_calls.append(lambda *args: self.keyBox.set_model(empty_model))
        self.rg.inginfo.key_connect_calls.append(setup_keybox)
        cb.setup_completion(self.keyBox) #add autocompletion
        # add autocompletion for items
        if hasattr(self,'ingBox'):
            cb.make_completion(self.ingBox, self.rg.inginfo.item_model)
            self.rg.inginfo.disconnect_calls.append(self.ingBox.get_completion().set_model(empty_model))
            self.rg.inginfo.item_connect_calls.append(lambda m: self.ingBox.get_completion().set_model(m))
        cb.set_model_from_list(self.shopBox,self.shopcats)
        cb.setup_completion(self.shopBox)
        if len(self.shopBox.get_model()) > 5:
            self.shopBox.set_wrap_width(2)
            if len (self.shopBox.get_model()) > 10:
                self.shopBox.set_wrap_width(3)
        self.new()
        
    def setup_glade (self):
        self.glade=self.rc.glade
        #self.glade.signal_connect('ieKeySet', self.keySet)
        #self.glade.signal_connect('ieShopSet', self.shopSet)
        #self.glade.signal_connect('ieApply', self.apply)
        self.ieBox = self.glade.get_widget('ieBox')
        self.ieExpander = self.glade.get_widget('ieExpander')
        #self.ieBox.hide()
        self.amountBox = self.glade.get_widget('ieAmount')
        self.unitBox = self.glade.get_widget('ieUnit')
        self.keyBox = self.glade.get_widget('ieKey')
        self.ingBox = self.glade.get_widget('ieIng')
        self.shopBox = self.glade.get_widget('ieShopCat')
        self.optCheck = self.glade.get_widget('ieOptional')
        self.togWidget = self.glade.get_widget('ieTogButton')

    def setup_signals (self):
        self.glade.signal_connect('ieAdd', self.add)
        self.glade.signal_connect('ieNew', self.new)
        self.glade.signal_connect('ieDel', self.delete_cb)        
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
                    widg.connect('activate',self.add)

    def keySet (self, *args):
        debug("keySet (self, *args):",0)
        if not re.match("^\s*$",self.keyBox.entry.get_text()):
            debug('user set key',0)
            self.user_set_key=True
            self.setShopper()
        else:
            debug('user unset key',0)
            #if user blanks key, we do our automagic again            
            self.user_set_key=False 

    def shopSet (self, *args):
        if not re.match("^\s*$",self.shopBox.entry.get_text()):
            self.user_set_shopper=True
        else:
            #if user blanks key, we do our automagic again
            self.user_set_key=False

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
            ""
        
    def getKeyList (self, ing=None):
        debug("getKeyList (self):",5)
        if not ing:
            ing = self.ingBox.get_text()
        return self.rg.rd.key_search(ing)

    def setKey (self, *args):
        debug("setKeyList (self, *args):        ",5)
        ing =  self.ingBox.get_text()
        if ing == self.last_ing:
            return
        myKeys = self.getKeyList(ing)
        if myKeys and not self.user_set_key:
            self.keyBox.entry.set_text(myKeys[0])
            self.user_set_key=False
        # and while we're at it...
        self.setKeyList()
        self.setShopper()
        self.last_ing = ing

    def setKeyList (self, *args):
        debug('setKeyList called!',0)
        self.myKeys = self.getKeyList()
        self.itxt = self.ingBox.get_text()
        if self.myKeys and self.myKeys != self.myLastKeys:
            def vis (m, iter):
                x = m.get_value(iter,0)
                if x and (x in self.myKeys or x.find(self.itxt) > -1):
                    return True
                else: return False
            debug('set visibility func to look for %s'%self.myKeys,0)
            self.keyBox.get_model().set_visible_func(vis)
        else:
            self.keyBox.get_model().set_visible_func(lambda *args: True)
        self.keyBox.get_model().refilter()
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
                         
    def show (self, ing):
        debug("show (self, ing):",5)
        self.ing = ing
        if hasattr(ing,'item'):
            self.ingBox.set_text(ing.item)
        if hasattr(ing,'key'):
            self.keyBox.entry.set_text(ing.key)
            self.keyBox.entry.user_set_key=True
        else:
            self.user_set_key=False            
        if hasattr(ing,'amount'):
            self.amountBox.set_text(convert.float_to_frac(float(ing.amount) * self.rc.mult))
        if hasattr(ing,'unit'):
            self.unitBox.entry.set_text(ing.unit)
        if hasattr(ing,'optional') and ing.optional=='yes':
            self.optCheck.set_active(gtk.TRUE)
        else:
            self.optCheck.set_active(gtk.FALSE)
        self.user_set_shopper=False
        self.getShopper()

    def new (self, *args):
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
            self.optCheck.set_active(gtk.FALSE)
        self.amountBox.grab_focus()

    def add (self, *args):
        debug("add (self, *args):",5)
        d = {}
        d['id']=self.rc.current_rec.id
        d['key']=self.getKey()
        d['item']=self.ingBox.get_text()
        d['unit']=self.unitBox.entry.get_text()
        amt=self.amountBox.get_text()
        if amt:
            try:
                d['amount']= convert.frac_to_float(amt)/self.rc.mult
            except:
                show_amount_error(amt)
                raise
        if not d['item'] :
            # if there's no item but there is a key, we assume that the user
            # wanted the item to be the same as the key
            if d['key']:
                d['item']=d['item']
                self.rc.message(_('Assuming you wanted item equal to key %s')%d['key'])
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
        if self.optCheck.get_active(): d['optional']='yes'
        else:
            d['optional']='no'
        if d['key']:
            self.addKey(d['key'],d['item'])
        else:
            d['key']=self.rg.rd.key_search(d['item'])[0]
        sh = self.shopBox.entry.get_text()
        if sh:
            self.rg.sl.sh.add_org_itm(d['key'],sh)
        if self.ing:
            i=self.rg.rd.modify_ing(self.ing,d)
            self.rc.resetIngList()
        else:
            i=self.rg.rd.add_ing(d)
            iter=self.rc.add_ingredient(self.rc.imodel,i,self.rc.mult,
                                   group_iter=self.rc.getSelectedIter())
            path=self.rc.imodel.get_path(iter)
            self.rc.ingTree.expand_to_path(path)
            self.rc.ingTree.get_selection().select_iter(iter)
        self.new()
        #self.rc.resetIngList()
        #self.new()

    def delete_cb (self, *args):
        debug("delete_cb (self, *args):",5)
        mod,rows = self.rc.ingTree.get_selection().get_selected_rows()
        rows.reverse()
        for p in rows:
            i=mod.get_iter(p)
            ing = mod.get_value(i,0)
            if type(ing) == type(""):
                ## then we're a group
                self.remove_group(i)
            elif de.getBoolean(label=_("Are you sure you want to delete %s?")%ing.item):
                self.rc.pre_modify_tree()
                mod.remove(i)
                self.rc.post_modify_tree()                
                debug('deleting ingredient')
                self.rg.rd.delete_ing(ing)
                
        self.new()

    def remove_group (self, iter):
        nchildren = self.rc.imodel.iter_n_children(iter)
        if type(nchildren) != type(1):
            # if there are no children
            # we just remove the group
            # heading without asking
            # for confirmation
            self.rc.imodel.remove(iter)
            return
        # otherwise, we'll need to be more thorough...
        group = self.rc.imodel.get_value(iter,1)
        if de.getBoolean(label=_("Are you sure you want to delete %s")%group):
            # collect our childrenp
            children = []
            ings = []
            for n in range(nchildren):
                child=self.rc.imodel.iter_nth_child(iter,n)
                children.append(child)
                i=self.rc.imodel.get_value(child,0)
                ings.append([i.amount,i.unit,i.item])
            if children:
                children.reverse()
                question=_("Shall I delete the items contained in %s or just move them out of the group?")%group
                tree = te.QuickTree(ings, [_("Amount"),_("Unit"),_("Item")])
                debug("de.getBoolean called with:")
                debug("label=%s"%question)
                debug("expander=['See ingredients',%s]"%tree)
                delete=de.getBoolean(label=question,
                                     custom_yes=_("Delete them."),
                                     custom_no=_("Move them."),
                                     expander=[_("See ingredients"),tree])
                    # then we're deleting them, this is easy!
                children.reverse()
                self.rc.pre_modify_tree()
                for c in children:
                    ing = self.rc.imodel.get_value(c,0)
                    if delete:
                        self.rc.imodel.remove(c)
                        self.rg.rd.delete_ing(ing)
                    else:
                        ing.group = None
                        te.move_iter(self.rc.imodel, c,
                                     sibling=iter, direction="after")
            else: self.rc.pre_modify_tree()
            self.rc.imodel.remove(iter)
            self.rc.post_modify_tree()


class IngInfo:
    """Keep models for autocompletion, comboboxes, and other
    functions that might want to access a complete list of keys,
    items and the like"""

    def __init__ (self, rd):
        self.rd = rd
        self.make_item_model()
        self.make_key_model()
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
        unique_item_vw = self.rd.iview.counts(self.rd.iview.item, 'count')
        self.item_model = gtk.ListStore(str)
        for i in unique_item_vw:
            self.item_model.append([i.item])
        if not unique_item_vw:
            import defaults
            for i,k,c in defaults.lang.INGREDIENT_DATA:
                self.item_model.append([i])
        
    def make_key_model (self):
        unique_key_vw = self.rd.iview.groupby(self.rd.iview.key, 'groupvw')
        # the key model by default stores a string and a list.
        self.key_model = gtk.ListStore(str)
        for k in unique_key_vw:
            lst = []
            self.key_model.append([k.key])
        if not unique_key_vw:
            import defaults
            for i,k,v in defaults.lang.INGREDIENT_DATA:
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
        if not self.manually: self.disconnect_models()
        if hasattr(ing,'item'):
            debug('checking for item',3)
            if not [ing.item] in self.item_model:
                debug('adding item',3)                
                self.item_model.append([ing.item])
                debug('appended %s to item model'%ing.item,3)
        if hasattr(ing,'key'):
            debug('checking for key',3)
            if not [ing.key] in self.key_model:
                debug('adding key',3)
                self.key_model.append([ing.key])
                debug('appended %s to key model'%ing.key,3)
        debug('add ing completed',3)
        if not self.manually: self.connect_models()

class RecSelector (RecIndex):
    """Select a recipe and add it to RecCard's ingredient list"""
    def __init__(self, RecGui, RecCard):
        self.glade=gtk.glade.XML(os.path.join(gladebase,'recSelector.glade'))
        self.glade.signal_connect('cancel',self.cancel)
        self.glade.signal_connect('ok',self.ok)        
        self.rg=RecGui
        self.rc=RecCard
        self.dialog = self.glade.get_widget('recDialog')
        RecIndex.__init__(self, self.rg.rmodel, self.glade, self.rg.rd,
                          self.rg, visible=2)

    def quit (self):
        self.dialog.destroy()

    def cancel (self,*args):
        debug('cancel',0)
        self.quit()

    def ok (self,*args):
        debug('ok',0)
        pre_iter=self.rc.getSelectedIter()
        try:
            self.rc.pre_modify_tree()
            for rec in self.recTreeSelectedRecs():
                if rec.id == self.rc.current_rec.id:
                    de.show_message(label=_("Recipe cannot call itself as an ingredient!"),
                                    sublabel=_('Infinite recursion is not allowed in recipes!')
                                    )
                    continue
                ingdic={'amount':1,
                        'unit':'recipe',
                        'item':rec.title,
                        'refid':rec.id,
                        'id':self.rc.current_rec.id,}
                debug('adding ing: %s'%ingdic,5)
                i=self.rg.rd.add_ing(ingdic)
                iter=self.rc.add_ingredient(self.rc.imodel,i,
                                            mult=self.rc.mult,
                                            group_iter=pre_iter)
                path=self.rc.imodel.get_path(iter)
                self.rc.ss.add_selection(iter)
            self.rc.post_modify_tree()
            self.rc.commit_positions()
            self.quit()
        except:
            de.show_message(label=_("You haven't selected any recipes!"))
            raise
        
def show_amount_error (txt):
    """Show an error that explains how numeric amounts work."""
    de.show_message(label=_("""I'm sorry, I can't understand
the amount "%s".""")%txt,
                    sublabel=_("Amounts must be numbers (fractions or decimals) or blank."),
                    expander=[_("Details"),
                              _("""
The "unit" must be in the "unit" field by itself.
For example, if you want to enter one and a half cups,
the amount field could contain "1.5" or "1 1/2". "cups"
should go in the separate "unit" field.
""")])
