from __future__ import print_function

import gtk
import databaseGrabber
import os, os.path, time
import gourmet.gtk_extras.dialog_extras as de
from gourmet.gglobals import data_dir
from gettext import gettext as _

class DatabaseGrabberGui (databaseGrabber.DatabaseGrabber):
    def __init__ (self, db):
        databaseGrabber.DatabaseGrabber.__init__(self,db,self.show_progress)
        self.paused=False
        self.terminated=False

    def pausecb (self,button,*args):
        if button.get_active():
            self.paused=True
        else:
            self.paused=False

    def stopcb (self,*args):
        self.terminated=True
        
    def load_db (self):
        #filename=None
        #if de.getBoolean(
        #    label=_('Load nutritional database.'),
        #    sublabel=_("It looks like you haven\'t yet initialized your nutritional database. To do so, you'll need to download the USDA nutritional database for use with your program. If you are not currently online, but have already downloaded the USDA sr17 database, you can point Gourmet to the ABBREV.txt file now. If you are online, Gourmet can download the file automatically."),
        #    custom_yes=_('Browse for ABBREV.txt file'),
        #    custom_no=_('Download file automatically')):
        #    filename=de.select_file(
        #        'Find ABBREV.txt file',
        #        filters=[['Plain Text',['text/plain'],['*txt']]]
        #        )
        self.progdialog = de.ProgressDialog(label=_('Loading Nutritional Data'),
                                            pause=self.pausecb,
                                            stop=self.stopcb)
        self.progdialog.show()
        self.grab_data(data_dir)
        self.show_progress(1,_('Nutritonal database import complete!'))
        self.progdialog.set_response_sensitive(gtk.RESPONSE_OK,True)
        self.progdialog.hide()

    def show_progress (self,fract,msg):
        self.progdialog.progress_bar.set_fraction(fract)
        self.progdialog.progress_bar.set_text(msg)
        while self.paused:
            time.sleep(0.1)
            self.gui_update()
        self.gui_update()
        
    def gui_update (self):
        if self.terminated:
            raise Exception("Terminated!")
        while gtk.events_pending():
            gtk.main_iteration()

    def get_zip_file (self):
        self.show_progress(0.01,_('Fetching nutritional database from zip archive %s')%self.USDA_ZIP_URL)
        return databaseGrabber.DatabaseGrabber.get_zip_file(self)

    def get_abbrev_from_url (self):
        self.show_progress(0.05,_('Extracting %s from zip archive.')%self.ABBREV_FILE_NAME)
        return databaseGrabber.DatabaseGrabber.get_abbrev_from_url(self)
    
def check_for_db (db):
    if db.fetch_len(db.nutrition_table) < 10:
        print('Grabbing nutrition database!')
        dgg = DatabaseGrabberGui(db)        
        dgg.load_db()
    # Check if we have choline in our DB... butter (1123) has choline...
    elif not db.fetch_one(db.nutrition_table,ndbno=1123).choline:
        dgg = DatabaseGrabberGui(db)
        dgg.load_db()
        
if __name__=='__main__':
    import gourmet.recipeManager
    print('loading db')
    db = gourmet.recipeManager.RecipeManager(**gourmet.recipeManager.dbargs)
    print('checking for nutrition_table')
    check_for_db(db)
