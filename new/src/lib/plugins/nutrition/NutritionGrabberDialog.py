import gtk
import os, os.path, time
from gourmet.DatabaseGrabber import DatabaseGrabber
from gourmet.dialogs import extras as de
from gourmet.system.threads import Terminated
from gourmet.gglobals import datad
from gettext import gettext as _

class NutritionGrabberDialog (DatabaseGrabber):
    def __init__ (self, db):
        DatabaseGrabber.__init__(self,db,self.show_progress)
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
        self.progdialog = de.ProgressDialog(label=_('Loading Nutritional Data'),
                                            pause=self.pausecb,
                                            stop=self.stopcb)
        self.progdialog.show()
        self.grab_data(datad)
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
            raise Terminated("Terminated!")
        while gtk.events_pending():
            gtk.main_iteration()

    def get_zip_file (self):
        self.show_progress(0.01,_('Fetching nutritional database from zip archive %s')%self.USDA_ZIP_URL)
        return DatabaseGrabber.get_zip_file(self)

    def get_abbrev_from_url (self):
        self.show_progress(0.05,_('Extracting %s from zip archive.')%self.ABBREV_FILE_NAME)
        return DatabaseGrabber.get_abbrev_from_url(self)
