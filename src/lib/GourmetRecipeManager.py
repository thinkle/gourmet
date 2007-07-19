#!/usr/bin/env python
import os.path, time, os, sys, re, threading, StringIO, pango, string
import Image
import gtk.glade, gtk, gobject, gtk.gdk, traceback
import keyEditor, valueEditor, batchEditor
import recipeManager
import nutrition.nutrition, nutrition.nutritionGrabberGui
import exporters.printer as printer
import prefs, prefsGui, shopgui, reccard, convertGui, fnmatch, tempfile
import exporters, importers
import convert, WidgetSaver, version, ratingWidget
import importers.mastercook_importer as mastercook_importer
import dialog_extras as de
import treeview_extras as te
from ImageExtras import get_pixbuf_from_jpg
from gdebug import *
from gglobals import *
from recindex import RecIndex
import recipeMerger
import exporters.recipe_emailer as recipe_emailer
import locale, gettext
from timer import show_timer
_ = gettext.gettext
from defaults import lang as defaults

from zipfile import BadZipfile

if os.name == 'posix':
    # somewhat hackish -- we assume USR ==
    usr_share = os.path.join(os.path.split(datad)[0])
    if not os.path.exists(os.path.join(usr,'locale')):
        usr_share = os.path.join('/usr','share')
    DIR = os.path.join(usr_share,'locale')
else:
    DIR = os.path.join(datad,'i18n')

import gettext_setup

try:
    import rtf_exporter
    rtf=True
except ImportError:
    debug('No RTF support',0)
    rtf=False

def check_for_data_to_import (rm):
    if rm.fetch_len(rm.rview)==0:
        try:
            import legacy_db
        except ImportError:
            print "Not trying to update."
            print "We had an import error."
            import traceback; traceback.print_exc()
        else:
            pd = de.ProgressDialog(label=_('Importing old recipe data'),
                                   sublabel=_('Importing recipe data from a previous version of Gourmet into new database.'),
                                   )
            def set_prog (p,msg=None):
                p=float(p)
                pd.set_progress(p,msg)
                while gtk.events_pending():
                    gtk.main_iteration()
            legacy_db.backup_legacy_data(gourmetdir, pd, set_prog)
            backup_file = os.path.join(gourmetdir,'GOURMET_DATA_DUMP')
            if os.path.exists(backup_file):
                import upgradeHandler        
                pd.show()
                upgradeHandler.import_backup_file(
                    rm,backup_file,set_prog
                    )
                os.rename(backup_file,backup_file+'.ALREADY_LOADED')
                pd.hide()
                pd.destroy()
        
class RecGui (RecIndex):
    """This is the main application. We subclass RecIndex, which handles displaying a list of
    recipes and searching them (a functionality we need in a few other places, such as when
    calling a recipe as an ingredient or when looking through the "trash". """

    def __init__ (self,splash_label=None):
        # used on imports to make filtering wait until
        # we are all done.
        self.wait_to_filter=False
        try:
            import gnome
            # The following allows accessibility support to work for
            # some unknown reason
            # apparently some outdated GNOME bindings are
            # missing this.
            if hasattr(gnome,'program_init'):
                gnome.program_init(version.appname,version.version)
            else:
                debug(
                    'You appear to have an outdated version of python-gnome bindings: gnome.program_init does not exist.',
                    0)
        except ImportError:
            pass
        if debug_level > 0:
            debug("Debug level: %s"%debug_level, debug_level)
        # just make sure we were given a splash label to update
        self.splash_label = splash_label
        self.update_splash(_("Loading window preferences..."))
        self.prefs = prefs.Prefs()
        self.prefsGui = prefsGui.PreferencesGui(
            self.prefs,
            buttons={'clear_remembered_optional_button':lambda *args: self.forget_remembered_optional_ingredients()}
            )
        self.prefsGui.apply_prefs_dic['recipes_per_page'] = lambda p,v: getattr(getattr(self,'rmodel'),
                                                                               'change_items_per_page')(v)

        def toggleFractions (prefname,use):
            print 'toggleFractions->',use
            if use:
                convert.USE_FRACTIONS = convert.FRACTIONS_NORMAL
            else:
                convert.USE_FRACTIONS = convert.FRACTIONS_OFF
        self.prefsGui.apply_prefs_dic['useFractions'] = toggleFractions
        if self.prefs.get('useFractions',
                          defaults.LANG_PROPERTIES['useFractions']
                          ):
            convert.USE_FRACTIONS = convert.FRACTIONS_NORMAL
        else:
            convert.USE_FRACTIONS = convert.FRACTIONS_OFF
        
        self.update_splash(_("Loading graphical interface..."))        
        gtk.glade.bindtextdomain('gourmet',DIR)
        gtk.glade.textdomain('gourmet')
        debug("gladebase is: %s"%gladebase,1)
        self.glade = gtk.glade.XML(os.path.join(gladebase,'app.glade'))
        self.pop = self.glade.get_widget('rlmen')
        self.app = self.glade.get_widget('app')
        self.prog = self.glade.get_widget('progressbar')
        # configuration stuff
        # WidgetSaver is our way of remembering the state and position of
        # windows and widgets for the future.
        self.conf = []
        self.conf.append(WidgetSaver.WindowSaver(self.app,
                                                 self.prefs.get('app_window',
                                                                {}),
                                                 show=False))        
        # a thread lock for import/export threads
        self.lock = gt.get_lock()
        self._threads = []
        self.threads = 0
        self.selected = True
        # widgets that should be sensitive only when a row is selected
        self.act_on_row_widgets = [self.glade.get_widget('rlViewRecButton'),
                                   self.glade.get_widget('rlViewRecMenu'),
                                   self.glade.get_widget('rlShopRecButton'),
                                   self.glade.get_widget('rlShopRecMenu'),
                                   self.glade.get_widget('rlDelRecButton'),
                                   self.glade.get_widget('rlDelRecMenu'),
                                   self.glade.get_widget('rlBatchEditRecMenu'),
                                   self.glade.get_widget('export_menu_item'),
                                   self.glade.get_widget('email_menu_item'),
                                   self.glade.get_widget('print_menu_item'),
                                   ]
        
        self.rtcolsdic={}
        self.rtwidgdic={}
        for a,l,w in REC_ATTRS:
            self.rtcolsdic[a]=l
            self.rtwidgdic[a]=w
        self.rtcols = [r[0] for r in REC_ATTRS]
        self.update_splash(_("Loading recipe database..."))
        self.init_recipes()
        self.update_splash(_("Setting up recipe index..."))
        RecIndex.__init__(self,
                          #model=self.rmodel,
                          glade=self.glade,
                          rd=self.rd,
                          rg=self,
                          editable=False)

        # we need an "ID" to add/remove messages to/from the status bar
        self.pauseid = self.stat.get_context_id('pause')
        # setup call backs for e.g. right-clicking on the recipe tree to get a popup menu
        self.rectree.connect("popup-menu",self.popup_rmenu)#self.recTreeSelectRec)
        self.rectree.connect("button-press-event",self.rectree_click_cb)
        # connect the rest of our handlers
        self.glade.signal_autoconnect({
            'newRec' : self.newRecCard,
            'shopHide' : self.sl.hide,
            'showShop' : self.sl.show,
            'showList' : lambda *args: self.app.present(),            
            'new' : self.new,
            'defaultsave': self.save_default,
            'export' : self.export_selected_recs,
            'export_all': self.export_all_recs,
            'import' : self.importg,
            'import_webpage': self.import_webpageg,
            'quit' : self.quit,
            'about' : self.show_about,
            'show_help' : self.show_help,
            'rl_viewrec' : self.recTreeSelectRec,
            'rl_shoprec' : self.recTreeShopRec,
            'rl_delrec': self.recTreeDeleteRecCB,
            'colPrefs': self.show_preferences,
            'unitConverter': self.showConverter,
            'ingKeyEditor': self.showKeyEditor,
            'valueEditor': self.showValueEditor,
            'print':self.print_recs,
            'email':self.email_recs,
            #'email_prefs':self.email_prefs,
            'showDeletedRecipes':self.show_deleted_recs,
            'emptyTrash':self.empty_trash,
            'on_timer': lambda *args: show_timer(),
            'batch_edit':self.batch_edit_recs,
            'on_duplicate_finder':self.show_duplicate_editor,
#            'shopCatEditor': self.showShopEditor,            
            })
        # self.rc will be a list of open recipe cards.
        self.rc={}
        # updateViewMenu creates our view menu based on which cards are open
        self.updateViewMenu()
        self.register_col_dialog()
        ## make sure the focus is where it ought to be...
        self.app.present()
        self.srchentry.grab_focus()
        self.srchentry.connect('activate',self.search_entry_activate_cb)
        self.update_splash(_("Done!"))
        self.threads = 0

    def search_entry_activate_cb (self, *args):
        if self.rmodel._get_length_()==1:
            self.recTreeSelectRec()
        else:
            self.limit_search()
            
    def update_splash (self, text):
        """Update splash screen on startup."""
        debug("Setting splash text: %s"%text,3)
        if not self.splash_label: return
        self.splash_label.set_text(text)        
        while gtk.events_pending():
            gtk.main_iteration()
        
    def del_rc (self, id):
        """Forget about recipe card identified by id"""
        if self.rc.has_key(id):
            del self.rc[id]
        self.updateViewMenu()

    def update_reccards (self, rec):
        if self.rc.has_key(rec.id):
            rc=self.rc[rec.id]
            rc.updateRecipe(rec,show=False)
            self.updateViewMenu()
        
    def viewMenu (self):
        """Build a _View menu based on recipes currently
        opened in recipe cards."""
        m=gtk.Menu()
        ri=gtk.MenuItem(_('Recipe _Index'))
        sh=gtk.MenuItem(_('Shopping _List'))
        separator=gtk.MenuItem()
        ri.connect('activate',lambda *args: self.app.present())
        sh.connect('activate',self.sl.show)
        m.append(ri)
        ri.show()
        m.append(sh)
        sh.show()
        m.append(separator)
        separator.show()
        for rc in self.rc.values():
            i=gtk.MenuItem("_%s"%rc.current_rec.title)
            i.connect('activate',rc.show)
            m.append(i)
            i.show()
        return m

    def updateViewMenu (self):
        """Update view menus in all open windows."""
        glades=[self.glade, self.sl.glade]
        for r in self.rc.values():
            glades.append(r.glade)
        for glade in glades:
            menu=self.viewMenu()
            vmi=glade.get_widget('view_menu_item')
            if vmi:
                vmi.set_submenu(menu)
    
    def show_about (self, *args):
        """Show information about ourselves, using GNOME's
        nice interface if available."""
        debug("show_about (self, *args):",5)
        description=version.description
        copyright=version.copyright
        appname=version.appname
        myversion=version.version
        authors=version.authors
        website="http://grecipe-manager.sourceforge.net"
        documenters=None
        translator=_("translator-credits")
        # translator's should translate the string 'translator-credits'
        # If we're not using a translatino, then this isn't shown
        if translator == "translator-credits":
            translator = None
        # Grab CREDITS from our defaults_LANG file too!
        if hasattr(defaults,'CREDITS') and defaults.CREDITS:
            if translator and translator.find(defaults.CREDITS) > -1:
                translator += "\n%s"%defaults.CREDITS
            else:
                translator = defaults.CREDITS
        comments=None
        logo=gtk.gdk.pixbuf_new_from_file(os.path.join(imagedir,"gourmet_logo.png"))
        try:
            import gnome.ui
            # to test the non-GNOME hack on a GNOME system,
            # uncomment the following line
            # import asdflkjasdf
            args = [appname,
                    myversion,
                    copyright,
                    description,
                    authors,
                    comments,
                    translator,
                    logo]
            if not translator:
                args = args[0:5] + [None] + args[6:]
            about= gnome.ui.About(*args)
            try:
                about.set_website(website) #will be available in 2.6
            except AttributeError:
                debug('No website available in "about" with this version of gtk/gnome',2)
                c=about.get_property('comments')
                c += _("\nWebsite: %s")%website
                about.set_property('comments',c)
                pass
            about.show()
        except ImportError:
            sublabel = '%s\n%s'%(copyright,description)
            for a in authors:
                sublabel += '\n%s'%a
            if translator:
                sublabel += _('\nTranslated by: %s')%translator
            if website:
                sublabel += _('\nWebsite: %s')%website
            import xml.sax.saxutils
            de.show_message(label=xml.sax.saxutils.escape('%s %s'%(appname,myversion)),
                            sublabel=sublabel) #new line that leaves strings as they are.
            
    def show_help (self, *args):
        de.show_faq(HELP_FILE)

    def show_progress_dialog (self, thread, progress_dialog_kwargs={},message=_("Import paused"),
                           stop_message=_("Stop import")):
        """Show a progress dialog"""
        if hasattr(thread,'name'): name=thread.name
        else: name = ''
        for k,v in [('okay',True),
                    ('label',name),
                    ('parent',self.app),
                    ('pause',self.pause_cb),
                    ('stop',self.stop_cb),
                    ('modal',False),]:
            if not progress_dialog_kwargs.has_key(k):
                progress_dialog_kwargs[k]=v
        if not hasattr(self,'progress_dialog') or not self.progress_dialog:
            self.progress_dialog = de.ProgressDialog(**progress_dialog_kwargs)
            self.prog = self.progress_dialog.progress_bar
        else:
            self.progress_dialog.reassign_buttons(pausecb=progress_dialog_kwargs['pause'],
                                              stopcb=progress_dialog_kwargs['stop'])
            self.progress_dialog.reset_label(progress_dialog_kwargs['label'])
        self.pause_message = message
        self.stop_message = stop_message
        self.thread = thread        
        self.progress_dialog.show()
        self.progress_dialog.connect('close',lambda *args: setattr(self.progress_dialog,None))
        #self.pauseButton.show()
        #self.stopButton.show()
        
    def hide_progress_dialog (self):
        """Make the progress dialog go away."""
        if hasattr(self,'progress_dialog') and self.progress_dialog:
            self.progress_dialog.hide()
            self.progress_dialog.destroy()
            self.progress_dialog = None
            
    def quit (self, *args):
        """Close down shop, giving user option of saving changes and
        saving our window prefs for posterity."""
        debug("quit (self, *args):",5)
        for c in self.conf:
            c.save_properties()
        a=self.glade.get_widget('app')
        for r in self.rc.values():
            for c in r.conf:
                c.save_properties()
            if r.edited and de.getBoolean(parent=self.app,
                                             label=_("Save your edits to %s")%r.current_rec.title):
                r.saveEditsCB()
            else: r.edited=False # in case someone else checks this (e.g. reccard on close)
        for conf in self.sl.conf:
            conf.save_properties()
        self.prefs.save()
        threads=threading.enumerate()
        if len(threads) > 1 or (not use_threads and self.lock.locked_lock()):
            msg = "Another process is in progress"
            for t in threads:
                if "import" in t.getName(): msg = _("An import is in progress.")
                if "export" in t.getName(): msg = _("An export is in progress.")
                if "delete" in t.getName(): msg = _("A delete is in progress.")
            quit_anyway = de.getBoolean(label=msg,
                                        sublabel=_("Exit program anyway?"),
                                        custom_yes=gtk.STOCK_QUIT,
                                        custom_no=_("Don't exit!"),
                                        cancel=False)
            if quit_anyway:
                for t in threads:
                    if t.getName() !='MainThread':
                        try:
                            t.terminate()
                        except:
                            debug("Unable to terminate thread %s"%t,0)
                            return True
                if not use_threads:
                    for t in self._threads:
                        try:
                            t.terminate()
                            self.threads = self.threads - 1
                        except: return True
            else:
                return True
        self.save_default()
        for r in self.rc.values():
            r.widget.destroy()
        self.sl.widget.destroy()
        a.destroy()
        gtk.main_quit()
        #import sys
        #sys.exit()

    def new (self, *args):
        debug("new (self, *args):",5)
        self.init_recipes()

    def init_recipes (self):
        """Initialize recipe database.

        We load our recipe database from recipeManager. If there's any problem,
        we display the traceback to the user so they can send it out for debugging
        (or possibly make sense of it themselves!)."""
        try:
            self.rd = recipeManager.RecipeManager(**recipeManager.dbargs)
            check_for_data_to_import(self.rd)
            # initiate autosave stuff
            # autosave every 3 minutes (milliseconds * 1000 milliseconds/second * 60 seconds/minute)
            gobject.timeout_add(1000*60*3,lambda *args: self.rd.save() or True)
        except:
            self.prefs['db_backend'] = None
            self.prefs.save()
            from StringIO import StringIO
            f = StringIO()
            traceback.print_exc(file=f)
            error_mess = f.getvalue()
            de.show_message(label='Database Connection failed.',
                            sublabel='There was a problem with the database information you gave Gourmet',
                            expander=(_('_Details'),
                                      error_mess)
                            )
            raise
        # connect hooks to modify our view whenever and
        # whenceever our recipes are updated...
        self.rd.modify_hooks.append(self.update_rec_iter)
        self.rd.modify_hooks.append(self.updateAttributeModels)
        self.rd.add_hooks.append(self.updateAttributeModels)
        #self.rd.add_hooks.append(self.new_rec_iter)
        self.rd.delete_hooks.append(self.delete_rec_iter)
        self.rd.delete_hooks.append(self.updateAttributeModels)
        # a flag to make deleting multiple recs
        # more efficient...
        self.doing_multiple_deletions=False
        #self.conv = rmetakit.mkConverter(self.rd)
        self.conv = convert.converter()
        # initialize our nutritional database
        nutrition.nutritionGrabberGui.check_for_db(self.rd)
        self.nd = nutrition.nutrition.NutritionData(self.rd,self.conv)
        self.rd.nd = self.nd
        # initialize star-generator for use elsewhere
        self.star_generator = ratingWidget.StarGenerator()
        # we'll need to hand these to various other places
        # that want a list of units.
        self.umodel = convertGui.UnitModel(self.conv)
        self.attributeModels = []
        self.inginfo = reccard.IngInfo(self.rd)
        #self.create_rmodel(self.rd.rview)
        self.sl = shopgui.ShopGui(self, conv=self.conv)
        self.sl.hide()

    def selection_changed (self, selected=False):
        if selected != self.selected:
            if selected: self.selected=True
            else: self.selected=False
            for w in self.act_on_row_widgets:
                w.set_sensitive(self.selected)

    def rectree_click_cb (self, tv, event):
        """Display popup button for right-click on rectree."""
        debug("rectree_click_cb (self, event):",5)
        if event.button==3:
            self.popup_rmenu(event)
            return True
        #if event.button==1 and event.type ==gtk.gdk._2BUTTON_PRESS:
        #    self.recTreeSelectRec()

    def reset_rtree (self):
        """Re-create our recipe model."""
        debug("reset_rtree (self):",5)
        self.setup_search_views()
        self.rmodel.change_view(self.lsrchvw)
        self.rectree.set_model(self.rmodel)
        self.set_reccount()

    def new_rec_iter (self, rec):
        self.reset_rtree()

    def delete_rec_iter (self, rec):
        if self.doing_multiple_deletions: return
        self.redo_search()

    def update_rec_iter (self, rec): self.rmodel.update_recipe(rec)

    def recTreeDeleteRecCB (self, *args):
        """Make a watch show up (this can be slow
        if lots of recs are selected!"""
        #gtk.app.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        #gobject.idle_add(self.recTreeDeleteRec)
        # this seems broken
        sel=self.rectree.get_selection()
        if not sel: return
        mod,rr=sel.get_selected_rows()
        recs = [mod[path][0] for path in rr]
        self.recTreeDeleteRecs(recs)

    def delete_open_card_carefully (self, rec):
        """Delete any open card windows, confirming if the card is edited.

        We return True if the user cancels deletion.
        """
        if self.rc.has_key(rec.id):
            rc = self.rc[rec.id]            
            if rc.edited:
                rc.widget.present()
                if not de.getBoolean(
                    label=_('Delete %s?'),
                    sublabel=_('You have unsaved changes to %s. Are you sure you want to delete?'),
                    custom_yes=gtk.STOCK_DELETE,
                    custom_no=gtk.STOCK_CANCEL,
                    cancel=False):
                    return True
            rc.widget.hide()
            self.del_rc(rec.id)
            
    def recTreeDeleteRecs (self, recs):
        cancelled = []
        for rec in recs:
            if self.delete_open_card_carefully(rec): # returns True if user cancels
                cancelled.append(rec)
        if cancelled:
            for c in cancelled: recs.remove(c)
        self.rd.undoable_delete_recs(
            [self.rd.get_rec(r.id) for r in recs],
            self.history,
            make_visible=lambda *args: self.redo_search()
            )
        self.set_reccount()
        if hasattr(self,'recTrash'):
            self.recTrash.update_from_db()
        self.message(_("Deleted") + ' ' + string.join([(r.title or _('Untitled')) for r in recs],', '))

    def recTreePurge (self, recs, paths=None, model=None):
        if not use_threads and self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to delete recipes.')
                            )
            return
        if not recs:
            # Do nothing if there are no recipes to delete.
            return
        if not paths: paths=[]
        expander=None
        bigmsg = _("Permanently delete recipes?")
        if len(recs) == 1:
            bigmsg = _("Permanently delete recipe?")
            msg = _("Are you sure you want to delete the recipe <i>%s</i>")%recs[0].title
        elif len(recs) < 5:
            msg = _("Are you sure you want to delete the following recipes?")
            for r in recs:
                msg += "\n<i>%s</i>"%r.title
        else:
            msg = _("Are you sure you want to delete the %s selected recipes?")%len(recs)
            tree = te.QuickTree([r.title for r in recs])
            expander = [_("See recipes"),tree]
        if de.getBoolean(parent=self.app,label=bigmsg,sublabel=msg,expander=expander):
            self.redo_search() # update all

            def show_progress (t):
                gt.gtk_enter()
                self.show_progress_dialog(t,
                                          progress_dialog_kwargs={'label':'Deleting recipes'},
                                          message=_('Deletion paused'), stop_message=_("Stop deletion"))
                gt.gtk_leave()
            def save_delete_hooks (t):
                self.saved_delete_hooks = self.rd.delete_hooks[0:]
                self.rd.delete_hooks = []
            def restore_delete_hooks (t):
                self.rd.delete_hooks = self.saved_delete_hooks
            pre_hooks = [
                lambda *args: self.lock.acquire(),
                save_delete_hooks,
                show_progress,
                ]
            post_hooks = [
                restore_delete_hooks,
                lambda *args: self.lock.release()]
            t=gt.SuspendableThread(gt.SuspendableDeletions(self, recs),
                                name='delete',
                                pre_hooks = pre_hooks,
                                post_hooks = post_hooks)
            if self.lock.locked_lock():
                de.show_message(label=_('An import, export or deletion is running'),
                                sublabel=_('The recipes will be deleted once the other process is finished.')
                                )
            debug('PRE_HOOKS=%s'%t.pre_hooks,1)
            debug('POST_HOOKS=%s'%t.post_hooks,1)
            debug('rd.add_hooks=%s'%self.rd.add_hooks,1)
            gt.gtk_leave()
            t.start()
            gt.gtk_enter()
        else:
            return True

    def delete_rec (self, rec):
        debug("delete_rec (self, rec): %s"%rec,5)
        debug("does %s have %s"%(self.rc,rec.id),5)
        if self.rc.has_key(rec.id):
            debug("Getting rid of open recipe card window.",2)
            w=self.rc[rec.id].widget
            self.rc[rec.id].hide()
            w.destroy()
            self.updateViewMenu()
        if hasattr(rec,'id') and rec.id:
            if rec:
                titl = rec.title
                debug('deleting recipe %s'%rec.title,1)
                # try a workaround to segfaults -- grab rec anew from ID.
                dbrec = self.rd.get_rec(rec.id)
                if dbrec:
                    self.rd.delete_rec(dbrec)
                else:
                    print 'wtf?!?',rec,':',rec.id,' not real?'
            else: debug('no recipe to delete!?!',1)
            if not self.doing_multiple_deletions:
                gt.gtk_enter()
                self.message(_("Deleted recipe %s")%titl)
                self.doing_multiple_deletions=False
                gt.gtk_leave()
        else:
            debug("%s %s does not have an ID!"%(rec,rec.title),2)
        debug("returning None",2)
        return None

    def email_recs (self, *args):
        debug('email_recs called!',1)
        recs = self.recTreeSelectedRecs()
        d=recipe_emailer.EmailerDialog(recs, self.rd, self.prefs, self.conv)
        d.setup_dialog()
        d.email()

    #def email_prefs (self, *args):
    #    d = recipe_emailer.EmailerDialog([],None,self.prefs,self.conv)
    #    d.setup_dialog(force=True)

    def show_deleted_recs (self, *args):
        if not hasattr(self,'recTrash'):
            self.recTrash = RecTrash(self.rd,self.rg)
        else:
            self.recTrash.show()
            

    def empty_trash (self, *args):
        self.recTreePurge(
            self.rd.fetch_all(self.rd.rview,deleted=True)
            )

    def print_recs (self, *args):
        debug('printing recipes',3)
        recs = self.recTreeSelectedRecs()
        gt.gtk_leave()
        printer.RecRenderer(self.rd, recs,
                            dialog_title=gettext.ngettext('Print %s recipe',
                                                          'Print %s recipes',
                                                          len(recs))%len(recs),
                            dialog_parent = self.app,
                            change_units = self.prefs.get('readableUnits',True)
                            )
        gt.gtk_enter()

    def popup_rmenu (self, event):
        debug("popup_rmenu (self, *args):",5)
        if hasattr(event,'button') and hasattr(event,'time'):
            self.pop.popup(None,None,None,event.button,event.time)
        else:
            self.pop.popup(None,None,None,0,0)
            return True

    def newRecCard (self, *args):
        self.app.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        def show ():
            rc=reccard.RecCard(self)
            self.make_rec_visible(rc.current_rec)
            self.rc[rc.current_rec.id]=rc
            self.app.window.set_cursor(None)
        gobject.idle_add(show)

    def update_modified_recipe (self, rec, attribute, value):
        if self.rc.has_key(rec.id):
            self.rc[rec.id].updateAttribute(attribute,value)

    def openRecCard (self, rec):
        if self.rc.has_key(rec.id):
            self.rc[rec.id].show()
        else:
            def show ():
                w=reccard.RecCard(self, rec)
                self.rc[rec.id]=w
                self.updateViewMenu()
                self.app.window.set_cursor(None)
            self.app.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
            gobject.idle_add(show)

    def recTreeSelectRec (self, *args):
        debug("recTreeSelectRec (self, *args):",5)
        for rec in self.recTreeSelectedRecs():
            self.openRecCard(rec)

    def recTreeShopRec (self, *args):
        debug("recTreeShopRec (self, *args):",5)
        rr=self.recTreeSelectedRecs()
        #r = self.recTreeSelectedRec()
        for r in rr:
            if r.servings and r.servings != "None":
                debug("servings=%s"%r.servings,5)
                serv = de.getNumber(default=float(r.servings),
                                    label=_("Number of servings of %s to shop for")%r.title,
                                    parent=self.app.get_toplevel())
                if serv: mult = float(serv)/float(r.servings)
                else:
                    debug('getNumber cancelled',2)
                    return
            else:
                mult = de.getNumber(default=float(1),
                                    label=_("Multiply %s by:")%r.title,
                                    parent=self.app.get_toplevel(),
                                    digits=2)
                if not mult:
                    mult = float(1)
            d=shopgui.getOptionalIngDic(self.rd.get_ings(r),mult,self.prefs,self)
            self.sl.addRec(r,mult,d)
            self.sl.show()

    def saveg (self, *args):
        debug("saveg (self, *args):",5)
        self.save(de.select_file())

    def save_default (self, *args):
        debug("save_default (self, *args):",5)
        self.save()

    def save (self, file=None, db=None, xml=None):
        debug("save (self, file=None, db=None, xml=None):",5)
        if file and not xml and not db:
            if re.search(".xml$",file):
                xml=file
            else:
                db=file
        if xml:
            self.exportXML(file)
        else:
            self.rd.file=db
            self.rd.save()
            self.message(_("Saved!"))
            
    def message (self, msg):
        debug("message (self, msg): %s"%msg,5)
        self.stat.push(self.contid,msg)
        gobject.timeout_add(1500,self.flush_messages)

    def flush_messages (self, ret=False):
        debug("flush_messages (self):",5)
        self.stat.pop(self.contid)
        return ret

    def forget_remembered_optional_ingredients (self):
        sublabel=_('Forget previously saved choices for which optional ingredients to shop for. This action is not reversable.')
        sublabel+= '\n\n'
        sublabel+= _('This will affect all recipes. If you want to forget the settings for an individual recipe, you can do so from the <b>Tools</b> menu of an individual recipe card.')
        if de.getBoolean(
            parent=self.app.get_toplevel(),
            label=_('Forget which optional ingredients to shop for?'),
            sublabel=sublabel,
            custom_yes=gtk.STOCK_OK,
            custom_no=gtk.STOCK_CANCEL,
            cancel=False):
            self.rg.rd.clear_remembered_optional_ings() #without an arg, this clears all.

    def export_selected_recs (self, *args): self.exportg(export_all=False)
    def export_all_recs (self, *args): self.exportg(export_all=True)

    def exportg (self, export_all=False):
        """If all is false, export only selected recipes.

        If all is True, export all recipes.
        """
        if not use_threads and self.lock.locked_lock():
            de.show_message(
                parent=self.app.get_toplevel(),
                label=_('An import, export or deletion is running'),
                sublabel=_('Please wait until it is finished to start your export.')
                            )
            return
        saveas_filters = exporters.saveas_filters[0:]
        ext = self.prefs.get('save_recipes_as','%sxml'%os.path.extsep)
        exp_directory = self.prefs.get('rec_exp_directory','~')
        file,exp_type=de.saveas_file(_("Export recipes"),
                                     filename="%s/%s%s"%(exp_directory,_('recipes'),ext),
                                     parent=self.app.get_toplevel(),
                                     filters=saveas_filters)
        if file:
            self.prefs['rec_exp_directory']=os.path.split(file)[0]
            self.prefs['save_recipes_as']=os.path.splitext(file)[1]
            expClass=None
            post_hooks = [self.after_dialog_offer_url(exp_type,file)]
            if exporters.exporter_dict.has_key(exp_type):
                myexp = exporters.exporter_dict[exp_type]
                if myexp.has_key('extra_prefs_dialog'):
                    extra_prefs = myexp['extra_prefs_dialog']()
                else:
                    extra_prefs = {}
                pd_args={'label':myexp['label'],'sublabel':myexp['sublabel']%{'file':file}}
                if export_all: recs = self.rd.fetch_all(self.rd.rview,deleted=False,sort_by=[('title',1)])
                else: recs = self.recTreeSelectedRecs()
                expClass = myexp['mult_exporter']({'rd':self.rd,
                                                   'rv': recs,
                                                   'conv':self.conv,
                                                   'prog':self.set_progress_thr,
                                                   'file':file,
                                                   'extra_prefs':extra_prefs,
                                                   })
            if expClass:
                self.threads += 1
                def show_progress (t):
                    debug('showing pause button',1)
                    gt.gtk_enter()
                    self.show_progress_dialog(t,message=_('Export Paused'),stop_message=_("Stop export"),
                                              progress_dialog_kwargs=pd_args,
                                              )
                    gt.gtk_leave()
                pre_hooks = [show_progress]
                pre_hooks.insert(0, lambda *args: self.lock.acquire())
                #post_hooks.append(lambda *args: self.reset_prog_thr())
                post_hooks.append(lambda *args: self.lock.release())
                t=gt.SuspendableThread(expClass, name='export',
                                    pre_hooks=pre_hooks,
                                    post_hooks=post_hooks)
                if self.lock.locked_lock():
                    de.show_message(label=_('An import, export or deletion is running'),
                                    sublabel=_('Your export will start once the other process is finished.'))
                debug('PRE_HOOKS=%s'%t.pre_hooks,1)
                debug('POST_HOOKS=%s'%t.post_hooks,1)                
                t.start()
                if not use_threads:
                    if not hasattr(self,'_threads'): self._threads = []
                    self._threads.append(t)
            else:
                de.show_message(label=_('Gourmet cannot export file of type "%s"')%os.path.splitext(file)[1],
                                message_type=gtk.MESSAGE_ERROR)

    def import_pre_hook (self, *args):
        debug('import_pre_hook, gt.gtk_enter()',1)
        debug('about to run... %s'%self.rd.add_hooks[1:-1],1)
        gt.gtk_enter()

    def import_post_hook (self, *args):
        debug('import_post_hook,gt.gtk_leave()',5)
        gt.gtk_leave()

    def import_webpageg (self, *args):
        if not use_threads and self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to start your import.')
                            )
            return
        import importers.html_importer
        sublabel = _('Enter the URL of a recipe archive or recipe website.')
        url = de.getEntry(label=_('Enter website address.'),
                          sublabel=sublabel,
                          entryLabel=_('Enter URL:'),
                          entryTip=_('Enter the address of a website or recipe archive. The address should begin with http://'),
                          default_character_width=60,
                          )
        if not url: return
        if url.find('//')<0:
            url = 'http://'+url
        self.show_progress_dialog(None,
                                  progress_dialog_kwargs={'label':_('Importing recipe from %s')%url,
                                                      'stop':False,
                                                      'pause':False,})
        try:
            i=importers.html_importer.import_url(
                url,
                self.rd,
                progress=self.set_progress_thr,
                threaded=True)
            #self.rd,
            #    url,
            #    prog=self.set_progress_thr,
            #    threaded=True)
            if type(i)==list:
                impClass,cant_import = self.prepare_import_classes(i)
                if impClass:
                    self.run_import(impClass,url,display_errors=False)
                else:
                    raise NotImplementedError("Gourmet cannot import")
            else:
                self.run_import(i,url,display_errors=False)
        except NotImplementedError:
            sublabel=_('Gourmet does not know how to import site %s')%url
            sublabel += "\n"
            sublabel += _('Are you sure %(url)s points to a page with a recipe on it?')%locals()
            de.show_message(label=_('Unable to import'),
                            sublabel=sublabel,
                            message_type=gtk.MESSAGE_ERROR)
            self.hide_progress_dialog()
        except BadZipfile:
            de.show_message(label=_('Unable to unzip'),
                            sublabel=_('Gourmet is unable to unzip the file %s')%url,
                            message_type=gtk.MESSAGE_ERROR)
        except IOError:
            self.hide_progress_dialog()
            de.show_traceback(label=_('Unable to retrieve URL'),
                              sublabel=_("""Gourmet was unable to retrieve the site %s. Are you sure your internet connection is working?  If you can retrieve the site with a webbrowser but continue to get this error, please submit a bug report at %s.""")%(url,BUG_URL)
                              )
            raise
        except gt.Terminated:
            if self.threads > 0: self.threads = self.threads - 1
            self.lock.release()
        except:
            self.hide_progress_dialog()
            de.show_traceback(
                label=_('Error retrieving %(url)s.')%locals(),
                sublabel=_('Are you sure %(url)s points to a page with a recipe on it?')%locals()
                )
            raise
        self.make_rec_visible()
        
    def importg (self, *args):
        if not use_threads and self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to start your import.')
                            )
            return
        import_directory = "%s/"%self.prefs.get('rec_import_directory',None)
        debug('show import dialog',0)
        ifiles=de.select_file(
            _("Import Recipes"),
            filename=import_directory,
            filters=importers.FILTERS,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            select_multiple=True)
        if ifiles:
            self.prefs['rec_import_directory']=os.path.split(ifiles[0])[0]
            self.import_multiple_files(ifiles)
        self.make_rec_visible()
            
    def prepare_import_classes (self, files):
        """Handed multiple import files, prepare to import.

        We return a tuple (importerClasses,cant_import)

        importClass - an instance of importers.importer.MultipleImport
        which handles the actual import when their run methods are
        called.

        cant_import - a list of files we couldn't import.

        This does most of the work of import_multiple_files, but
        leaves it up to our caller to display our progress dialog,
        etc.
        """
        impClass = None            
        importerClasses = []
        cant_import = []
        # we're going to make a copy of the list and chew it up. We do
        # this rather than doing a for loop because zip files or other
        # archives can end up expanding our list
        imp_files = files[0:] 
        while files:
            fn = files.pop()
            if type(fn)==str and os.path.splitext(fn)[1] in ['.gz','.gzip','.zip','.tgz','.tar','.bz2']:
                try:
                    debug('trying to unzip %s'%fn,0)
                    from importers.zip_importer import archive_to_filelist
                    archive_files = archive_to_filelist(fn)
                    for a in archive_files:
                        if type(a) == str:
                            files += [a]
                        else:
                            # if we have file objects, we're going to write
                            # them out to real files, so we don't have to worry
                            # about details later (this is stupid, but I'm sick of
                            # tracking down places where I e.g. closed files regardless
                            # of whether I opened them)
                            finame=tempfile.mktemp(a.name)
                            tfi=open(finame,'w')
                            tfi.write(a.read())
                            tfi.close()
                            files += [finame]
                    continue
                except:
                    cant_import.append(fn)
                    raise
                    continue
            try:
                impfilt = importers.FILTER_INFO[importers.select_import_filter(fn)]
            except NotImplementedError:
                cant_import.append(fn)
                continue
            impClass = impfilt['import']({'file':fn,
                                          'rd':self.rd,
                                          'threaded':True,
                                          })
            if impfilt['get_source']:
                if type(fn)==str: fname = fn
                else: fname = "file"
                source=de.getEntry(label=_("Default source for recipes imported from %s")%fname,
                                   entryLabel=_('Source:'),
                                   default=os.path.split(fname)[1], parent=self.app)
                # the 'get_source' dict is the kwarg that gets
                # set to the source
                impClass[2][impfilt['get_source']]=source
            if impClass: importerClasses.append((impClass,fn))
            else:
                debug('GOURMET cannot import file %s'%fn)
        if importerClasses:
            impClass = importers.importer.MultipleImporter(self,
                                                           importerClasses)
            return impClass,cant_import
        else:
            return None,cant_import

    def import_multiple_files (self, files):
        """Import multiple files,  showing dialog."""
        # This should probably be moved to importer with a quiet/not quiet options
        # and all of the necessary connections handed as arguments.
        impClass,cant_import=self.prepare_import_classes(files)
        if impClass:
            filenames = filter(lambda x: isinstance(x,str), files)
            self.run_import(
                impClass,
                import_source=string.join([os.path.split(f)[1] for f in filenames],", ")
                )
        if cant_import:
            # if this is a file with a name...
            BUG_URL="http://sourceforge.net/tracker/?group_id=108118&atid=649652"
            sublabel = gettext.ngettext("Gourmet could not import the file %s",
                                            "Gourmet could not import the following files: %s",
                                            len(cant_import))%", ".join(cant_import)
            sublabel += "\n"
            sublabel += gettext.ngettext(
                "If you believe this file is in one of the formats Gourmet supports, please submit a bug report at %s and attach the file.",
                "If you believe these files are in a format Gourmet supports, please submit a bug report at %s and attach the file.",
                len(cant_import))%BUG_URL
            self.offer_url(
                label=gettext.ngettext("Cannot import file.",
                                       "Cannot import files.",
                                       len(cant_import)),
                sublabel=sublabel,
                url=BUG_URL)
            return

    def run_import (self, impClass, import_source="", display_errors=True):
        """Run our actual import and display progress dialog."""
        # we have to make sure we don't filter while we go (to avoid
        # slowing down the process too much).
        self.wait_to_filter=True
        self.last_impClass = impClass
        pre_hooks = [lambda *args: self.inginfo.disconnect_manually()]
        post_hooks = [lambda *args: self.inginfo.reconnect_manually()]
        pre_hooks.append(lambda *args: self.rd.add_hooks.insert(0,self.import_pre_hook))
        pre_hooks.append(lambda *args: self.rd.add_hooks.append(self.import_post_hook))
        self.threads += 1
        release = lambda *args: self.lock.release()
        post_hooks.extend([self.import_cleanup,
                           lambda *args: setattr(self,'last_impClass',None),
                           release])
        def show_progress_dialog (t):
            debug('showing progress dialog',3)
            gt.gtk_enter()
            if import_source:
                sublab = _('Importing recipes from %s')%import_source
            else: sublab = None
            self.rg.show_progress_dialog(
                t,
                {'label':_('Importing Recipes'),
                 'sublabel':sublab
                 })
            gt.gtk_leave()
        pre_hooks.insert(0,show_progress_dialog)
        pre_hooks.insert(0, lambda *args: self.lock.acquire())
        t=gt.SuspendableThread(impClass,name="import",
                               pre_hooks=pre_hooks, post_hooks=post_hooks,
                               display_errors=display_errors)
        if self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Your import will start once the other process is finished.'))
        debug('starting thread',2)
        debug('PRE_HOOKS=%s'%t.pre_hooks,1)
        debug('POST_HOOKS=%s'%t.post_hooks,1)
        t.start()

    def import_cleanup (self, *args):
        """Remove our threading hooks"""
        debug('import_cleanup!',1)
        self.rd.add_hooks.remove(self.import_pre_hook)
        self.rd.add_hooks.remove(self.import_post_hook)
        debug('hooks: %s'%self.rd.add_hooks,1)
        self.wait_to_filter=False
        gt.gtk_enter()
        # Check for duplicates
        if self.last_impClass and self.last_impClass.added_recs:
            rmd = recipeMerger.RecipeMergerDialog(
                self.rd,
                in_recipes=self.last_impClass.added_recs,
                on_close_callback=lambda *args: self.redo_search()
                )
            rmd.show_if_there_are_dups(
                label=_('Some of the imported recipes appear to be duplicates. You can merge them here, or close this dialog to leave them as they are.')
                )
        # Update our models for category, cuisine, etc.
        self.updateAttributeModels()
        # Reset our index view
        self.redo_search()
        gt.gtk_leave()

    def after_dialog_offer_url (self, linktype, file):
        url = "file:///%s"%file
        label = _("Export succeeded")
        if linktype == exporters.WEBPAGE:
            url += '/index.htm'
            linktype = _("webpage")
        sublabel = _("Exported %s to %s")%(linktype,file)
        def offerer (t):
            if t.completed:
                #self.idle_offer_url(label, sublabel, url, True)
                self.offer_url(label, sublabel, url, True)
        return offerer

    def idle_offer_url (self, label, sublabl, url, from_thread):
        if from_thread:
            gt.gtk_enter()
        gobject.idle_add(lambda *args: self.offer_url(label,sublabl,url,True))
        if from_thread:
            gt.gtk_leave()

    def offer_url (self, label, sublabel, url, from_thread=False):
        if from_thread:
            gt.gtk_enter()
        if hasattr(self,'progress_dialog'):
            self.hide_progress_dialog()            
        d=de.MessageDialog(label=label,
                           sublabel=sublabel,
                           cancel=False
                           )
        b = gtk.Button(stock=gtk.STOCK_JUMP_TO)
        b.connect('clicked',lambda *args: launch_url(url))
        d.vbox.pack_end(b,expand=False)
        b.show()
        d.run()
        if from_thread:
            gt.gtk_leave()

    def pause_cb (self, button, *args):
        if button.get_active():
            debug('Suspending thread from pause_cb',0)
            self.thread.suspend()
            self.stat.push(self.pauseid, self.pause_message)
            self.flusher = gobject.timeout_add(1000,lambda *args: self.flush_messages(True))
        else:
            self.stat.pop(self.pauseid)            
            gobject.source_remove(self.flusher)
            self.thread.resume()
            
    def stop_cb (self, *args):
        debug('Stop_cb called; pausing thread',1)
        self.thread.suspend()
        if de.getBoolean(label=self.stop_message):
            debug('Stopping thread from stop cb',0)
            self.thread.terminate()
            if self.threads > 0:
                self.threads = self.threads - 1
                try: self.lock.release()
                except: pass
            self.hide_progress_dialog()
        else:
            debug('Resuming thread: stop_cb cancelled',0)
            self.thread.resume()
            return True

    def reset_prog_thr (self,message=_("Done!")):
        debug('reset_prog_thr',0)
        #self.prog.set_fraction(1)
        self.set_progress_thr(1,message)
        gt.gtk_enter()
        self.set_reccount()
        gt.gtk_leave()

    def set_progress_thr (self, prog, message=_("Importing...")):
        debug("set_progress_thr (self, %s,%s)"%(prog,message),1)
        gt.gtk_enter()
        if hasattr(self,'progress_dialog'):
            self.progress_dialog.set_progress(prog,message)
        gt.gtk_leave()

    def register_col_dialog (self, *args):
        already_hidden=self.prefs.get('rectree_hidden_columns',DEFAULT_HIDDEN_COLUMNS)
        if not already_hidden: already_hidden=[]
        def mapper (i):
            if i in already_hidden: return [i, False]
            else: return [i, True]
        options=map(lambda i: self.rtcolsdic[i], self.rtcols)
        options=map(mapper, options)
        #pd = de.preferences_dialog(options=options, option_label=None, value_label=_("Show in Index View"),
        #                           apply_func=self.configure_columns, parent=self.app)
        self.prefsGui.add_pref_table(options,
                                     'indexViewVBox',
                                     self.configure_columns)        

    def show_preferences (self, *args):
        self.prefsGui.show_dialog(page=self.prefsGui.INDEX_PAGE)

    def configure_columns (self, retcolumns):
        hidden=[]
        for c,v in retcolumns:
            if not v: hidden.append(c)
        self.rectree_conf.hidden=self.prefs['rectree_hidden_columns']=hidden
        self.rectree_conf.apply_visibility()

    def showConverter (self, *args):
        cg=convertGui.ConvGui(converter=self.conv, unitModel=self.umodel)

    def showKeyEditor (self, *args):
        ke=keyEditor.KeyEditor(rd=self.rd, rg=self)

    def showValueEditor (self, *args):
        if not hasattr(self,'ve'):
            self.ve=valueEditor.ValueEditor(self.rd,self)
        self.ve.valueDialog.connect('response',lambda d,r: (r==gtk.RESPONSE_APPLY and self.updateAttributeModels))
        self.ve.show()


    def batch_edit_recs (self, *args):
        recs = self.recTreeSelectedRecs()
        if not hasattr(self,'batchEditor'):
            self.batchEditor =  batchEditor.BatchEditor(self)
        self.batchEditor.set_values_from_recipe(recs[0])
        self.batchEditor.dialog.run()
        # If we have values...
        if self.batchEditor.values:
            changes = self.batchEditor.values
            only_where_blank = self.batchEditor.setFieldWhereBlank
            attributes = ', '.join(changes.keys())
            msg = gettext.ngettext('Set %(attributes)s for %(num)s selected recipe?',
                                   'Set %(attributes)s for %(num)s selected recipes?',
                                   len(recs))%{'attributes':attributes,
                                               'num':len(recs),
                                               }
            msg += '\n'
            if only_where_blank:
                msg += _('Any previously existing values will not be changed.')+'\n'
            else:
                msg += _('The new values will overwrite any previously existing values.')+'\n'
            msg += '<i>'+_('This change cannot be undone.')+'</i>'
            if de.getBoolean(label=_('Set values for selected recipes'),sublabel=msg,cancel=False,
                             custom_yes=gtk.STOCK_OK,custom_no=gtk.STOCK_CANCEL,):
                for r in recs:
                    if only_where_blank:
                        changes = self.batchEditor.values.copy()
                        for attribute in changes.keys():
                            if hasattr(r,attribute) and getattr(r,attribute):
                                del changes[attribute]
                        if changes:
                            self.rd.modify_rec(r,changes)
                    else:
                        self.rd.modify_rec(r,self.batchEditor.values)
                    self.update_rec_iter(r)
            else:
                print 'Cancelled'
        self.batchEditor.dialog.hide()
        self.updateAttributeModels()

    def show_duplicate_editor (self, *args):
        rmd = recipeMerger.RecipeMergerDialog(
            self.rd,
            on_close_callback=lambda *args: self.redo_search()
            )
        rmd.populate_tree_if_possible()
        rmd.show()
                    
    def getAttributeModel (self, attribute):
        """Return a ListModel with a unique list of values for attribute.

        This is stored here so that all the different comboboxes that
        might need e.g. a list of categories can share 1 model and
        save memory.
        """
        if not hasattr(self,'%sModel'%attribute):
            slist = self.createAttributeList(attribute)
            m = gtk.ListStore(str)
            for i in slist: m.append([i])
            setattr(self,'%sModel'%attribute,m)
            self.attributeModels.append((attribute,getattr(self,'%sModel'%attribute)))
        return getattr(self,'%sModel'%attribute)

    def updateAttributeModels (self):
        print 'updateAttributeModels!'
        for attr,mod in self.attributeModels:
            self.updateAttributeModel(attr)
            
    def updateAttributeModel (self, attribute):
        slist = self.createAttributeList(attribute)
        model = getattr(self,'%sModel'%attribute)
        for n,item in enumerate(slist):
            if model[n][0] == item:
                continue
            else:
                # See if we match something later in the model -- if
                # we do, suck up the whole model
                additional = 1
                found_match = False
                while len(model) > (n+additional):
                    if model[n+additional][0] == item:
                        while additional > 0:
                            model.remove(model.get_iter(n))
                            additional -= 1
                            found_match = False
                        break
                    additional += 1
                if not found_match:
                    model.insert(n,[item])
        while len(model) > len(slist):
            last = model.get_iter(len(model) - 1)
            model.remove(last)
        return model

    def createAttributeList (self, attribute):
        """Create a ListModel with unique values of attribute.
        """
        if attribute=='category':
            slist = self.rg.rd.get_unique_values(attribute,self.rg.rd.catview)
        else:
            slist = self.rg.rd.get_unique_values(attribute,deleted=False)
        if not slist:
            slist = self.rg.rd.get_default_values(attribute)
        else:
            for default_value in self.rg.rd.get_default_values(attribute):
                if default_value not in slist: slist.append(default_value)
        slist.sort()
        return slist

    # END class RecGUI

class RecTrash (RecIndex):

    default_searches = [{'column':'deleted','operator':'=','search':True}]
    
    def __init__ (self, rd, rg):
        self.rg = rg
        self.rmodel = self.rg.rmodel
        self.glade = gtk.glade.XML(os.path.join(gladebase,'recSelector.glade'))
        self.glade.get_widget('selectActionBox').set_property('visible',False)
        tab=self.glade.get_widget('trashActionBox')
        tab.set_property('visible',True)
        #try:
        #    tab.set_visible(True)
        #except:
        #    print "Can't set trashActionBox visible"
        #    for c in tab.get_children(): c.set_visible(True)
        self.window = self.glade.get_widget('recDialog')
        self.window.connect('delete-event',self.dismiss)
        self.window.set_title('Wastebasket (Deleted Recipes)')
        self.glade.signal_autoconnect({
            'purgeRecs':self.recTreePurgeSelectedRecs,
            'undeleteRecs':self.recTreeUndeleteSelectedRecs,
            'ok':self.dismiss,
            })
        RecIndex.__init__(self, self.glade, self.rg.rd, self.rg)

    def dismiss (self, *args):
        self.window.hide()
        return True
    
    def show (self, *args, **kwargs):
        self.window.show(*args,**kwargs)

    def setup_search_views (self):
        self.last_search = ["",""]
        self.rvw = self.rd.fetch_all(self.rd.rview,deleted=True)
        self.searches = self.default_searches
        self.sort_by = []

    def update_from_db (self):
        print 'UDPATE TRASH FROM DB!'
        self.update_rmodel(self.rg.rd.fetch_all(
            self.rg.rd.rview,deleted=True
            )
                                  )

    def recTreeUndeleteSelectedRecs (self, *args):
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

    def recTreePurgeSelectedRecs (self, *args):
        if not use_threads and self.rg.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to delete recipes.')
                            )
            return
        debug("recTreeDeleteRec (self, *args):",5)
        sel = self.rectree.get_selection()
        if not sel: return
        mod,rr=sel.get_selected_rows()
        recs = map(lambda path: mod[path][0],rr)
        self.rg.recTreePurge(recs,rr,mod)
        self.update_from_db()

def set_accel_paths (glade, widgets, base='<main>'):
    """A convenience function. Hand us a function and set accel
    paths based on it."""
    for s in widgets:
        w=glade.get_widget(s)
        if type(w) == gtk.MenuItem: set_path_for_menuitem(w)
        else:
            for c in w.get_children():
                if type(c) == gtk.MenuItem:
                    set_path_for_menuitem(c,base)
                else:
                    debug("Can't handle %s"%c,1)

def set_path_for_menuitem (mi, base='<main>'):
    if mi.get_children():
        accelLab = mi.get_children()[0]
        l=accelLab.get_label().replace('_','')
        path = base + '/' + l
        mi.set_accel_path(path)
    sm = mi.get_submenu()
    if sm:
        sm.set_accel_path(path)
        for c in sm.get_children():
            set_path_for_menuitem(c,path)
    
def startGUI ():
    debug("startGUI ():",4)
    # show splash screen before we do anything...
    debug("showing splash screen...",1)    
    gt.gtk_threads_init()
    #gtk.threads_init()
    splash = gtk.Window()
    #splash.window_set_auto_startup_notification(False)
    splash.set_property('decorated',False)
    splash.set_position(gtk.WIN_POS_CENTER)
    splash.set_icon_from_file(os.path.join(imagedir,'recbox.png'))
    splash.set_title(_('Gourmet Recipe Manager starting up...'))
    pixbuf=gtk.gdk.pixbuf_new_from_file(os.path.join(imagedir,'splash.png'))
    pixmap, mask = pixbuf.render_pixmap_and_mask()
    width, height = pixmap.get_size()
    del pixbuf
    splash.set_app_paintable(True)
    splash.resize(width, height)
    splash.realize()
    splash.window.set_back_pixmap(pixmap, False)
    splash.label = gtk.Label(_("Starting gourmet..."))
    splash.label.set_alignment(0.5,1)
    splash.label.set_justify(gtk.JUSTIFY_CENTER)
    splash.label.set_line_wrap(True)
    #pal = pango.AttrList()
    #pal.insert(pango.AttrForeground(
    #    255,255,128
    #    ))
    #splash.label.set_property('attributes',pal)
    splash.label.show()
    splash.add(splash.label)    
    del pixmap
    splash.show()
    splash.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
    gt.gtk_enter()
    #gtk.threads_enter()
    while gtk.events_pending():
        # show our GUI
        gtk.main_iteration()
    try:
        r=RecGui(splash_label=splash.label)
    except:
        splash.hide()
        while gtk.events_pending():
            gtk.main_iteration()
        #gtk.main_quit()
        raise
    debug('hiding splash screen.',1)
    splash.hide()
    gtk.main()
    #gtk.threads_leave()
    gt.gtk_leave()
              
if __name__ == '__main__':
    if os.name!='nt':
        import profile, tempfile,os.path
        import hotshot, hotshot.stats
        #profi = os.path.join(tempfile.tempdir,'GOURMET_PROFILE')
        prof = hotshot.Profile(os.path.join(tempfile.tempdir,'GOURMET_HOTSHOT_PROFILE'))
        prof.runcall(startGUI)
        stats = hotshot.stats.load(os.path.join(tempfile.tempdir,'GOURMET_HOTSHOT_PROFILE'))
        stats.strip_dirs()
        stats.sort_stats('time','calls').print_stats()
        #profile.run('startGUI()',profi)
        #import pstats
        #p=pstats.Stats(profi)
        #p.strip_dirs().sort_stats('cumulative').print_stats()
    else:
        startGUI()
