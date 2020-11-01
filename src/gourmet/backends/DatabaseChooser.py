from gi.repository import Gtk
import os.path
from gourmet import gglobals
from gourmet import cb_extras as cb
from gourmet import dialog_extras as de
from gourmet.gdebug import debug
from gettext import gettext as _

class DatabaseChooser:
    """This is a simple interface for getting database information from the user."""
    def __init__ (self, okcb=lambda x: debug(x,0), modal=True):
        self._okcb = okcb
        self.modal = modal
        self.possible_dbs = ['sqlite','mysql']
        self.need_connection_info = ['mysql']
        self.need_file_info = ['sqlite']
        self.default_file_directory = gglobals.gourmetdir
        self.default_files = {'sqlite':'recipes.db'
                              }
        uifile = os.path.join(gglobals.uibase,'databaseChooser.ui')
        self.ui = Gtk.Builder()
        self.ui.add_from_file(uifile)
        self.connection_widgets = ['hostEntry','userEntry','pwEntry','dbEntry',
                                   'hostLabel','userLabel','pwLabel','dbLabel',
                                   'pwCheckButton']
        self.file_widgets = ['fileEntry','fileButton','fileLabel']
        self.widgets = self.file_widgets + self.connection_widgets + ['dbComboBox',
                                                                      'connectionExpander',
                                                                      'window']
        for w in self.widgets:
            setattr(self,w,self.ui.get_object(w))
        self.ui.connect_signals(
            {'ok_clicked':self.ok_cb,
             'cancel_clicked':self.cancel_cb,
             'dbChanged':self.change_db_cb,
             'browse_clicked':self.browse_cb}
            )
        self.pwEntry.set_visibility(False)
        self.dbComboBox.set_active(0)
        self.connectionExpander.set_expanded(False)
        self.change_db_cb()
        self.window.show()
        if self.modal:
            self.window.set_modal(True)

    def run (self):
        if self.modal:
            Gtk.mainloop()
            return self.retdic

    def ok_cb (self, *args):
        if not self.current_db:
            de.show_message(label='No database selected.',
                            sublabel='You need to select a database system.')
        else:
            self.retdic = {'db_backend':self.current_db}
            if self.current_db in self.need_connection_info:
                for e in self.connection_widgets:
                    if e.find('Entry') >= 0:
                        self.retdic[e[0:e.find('Entry')]]=getattr(self,e).get_text()
                self.retdic['store_pw']=self.pwCheckButton.get_active()
            if self.current_db in self.need_file_info:
                fi = self.fileEntry.get_text()
                if fi and fi.find(os.path.sep) < 0:
                    fi = os.path.join(self.default_file_directory,fi)
                self.retdic['file']=fi
            self.window.hide()
            self.window.destroy()
            if self._okcb: self._okcb(self.retdic)
            if self.modal:
                Gtk.mainquit()
            return self.retdic

    def cancel_cb (self, *args):
        self.window.hide()
        self.window.destroy()
        if self.modal: Gtk.mainquit()


    def change_db_cb (self, *args):
        self.current_db = None
        text = cb.cb_get_active_text(self.dbComboBox)
        if not text:
            return
        for db in self.possible_dbs:
            if text.lower().find(db.lower()) >= 0:
                self.current_db = db
                break
        if self.current_db in self.need_connection_info:
            self.connectionExpander.set_expanded(True)
            for w in self.connection_widgets:
                getattr(self,w).show()
        else:
            for w in self.connection_widgets:
                getattr(self,w).hide()
        for w in self.file_widgets:
            if self.current_db in self.need_file_info:
                getattr(self,w).show()
            else:
                getattr(self,w).hide()
        if self.current_db in self.default_files:
            self.fileEntry.set_text(self.default_files[self.current_db])

    def browse_cb (self,*args):
        fi = de.select_file(_("Choose Database File"),
                            filename=self.default_file_directory,
                            action=Gtk.FileChooserAction.OPEN)
        if fi:
            self.fileEntry.set_text(fi)


if __name__ == '__main__':
    d = DatabaseChooser(None,modal=True)
    print(d.run())
