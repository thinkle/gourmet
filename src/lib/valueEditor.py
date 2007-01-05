import gtk, gtk.glade, gobject
import gglobals, convert, os.path
import cb_extras as cb
import dialog_extras as de
from gettext import ngettext
from gettext import gettext as _


class ValueEditor:
    """A generic "value" editor for mucking about with the database.
    """

    values = 'category','cuisine','source','link'

    def __init__ (self, rd):
        self.rd = rd
        self.glade = gtk.glade.XML(os.path.join(gglobals.gladebase,'valueEditor.glade'))
        self.__setup_widgets__()
        self.__setup_treeview__()
        self.glade.signal_autoconnect({
            'on_changeValueButton_toggled':self.changeValueButtonToggledCB,
            'on_fieldToEditCombo_changed':self.fieldChangedCB,
            })
        
        
    def __setup_widgets__ (self):
        for w in [
            'valueDialog',
            'treeview',
            'fieldToEditCombo','newValueComboBoxEntry',
            'newValueEntry','changeValueButton',
            'deleteValueButton','forEachLabel',
            ]:
            setattr(self,w,self.glade.get_widget(w))
        self.act_on_selection_widgets = [
            self.deleteValueButton, self.changeValueButton,
            self.newValueEntry
            ]
        # Set up the combo-widget at the top with the 
        cb.set_model_from_list(
            self.fieldToEditCombo,
            [gglobals.REC_ATTR_DIC[v] for v in self.values]
            )
        self.newValueComboBoxEntry.set_sensitive(False)
        self.newValueEntryCompletion = gtk.EntryCompletion()
        self.newValueEntry.set_completion(self.newValueEntryCompletion)
        self.valueDialog.connect('response',self.dialog_response_cb)
        self.valueDialog.set_response_sensitive(gtk.RESPONSE_APPLY,False)
        

    def __setup_treeview__ (self):
        renderer = gtk.CellRendererText()
        # If we have gtk > 2.8, set up text-wrapping
        try:
            renderer.get_property('wrap-width')
        except TypeError:
            pass
        else:
            renderer.set_property('wrap-mode',gtk.WRAP_WORD)
            renderer.set_property('wrap-width',400)
        col = gtk.TreeViewColumn('Value',
                           renderer,
                           text=0)
        self.treeview.append_column(col)
        self.treeview.get_selection().connect('changed',self.treeViewSelectionChanged)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    def changeValueButtonToggledCB (self, tb):
        if tb.get_active():
            self.newValueComboBoxEntry.set_sensitive(True)
        else:
            self.newValueComboBoxEntry.set_sensitive(False)

    def treeViewSelectionChanged (self, tvSelection):
        vals = self.get_selected_values(tvSelection)
        if len(vals) == 1: val_string = vals[0]
        elif len(vals) == 2: val_string = ' or '.join(vals)
        elif len(vals) > 0:
            val_string = ' or '.join([', '.join(vals[:-1]),vals[-1]])
        else: # len(vals)==0
            self.forEachLabel.set_text(_('For each selected value'))
        if vals:
            self.val_string = val_string
            self.forEachLabel.set_text(
                _('Where %(field)s is %(value)s')%{'value':val_string,
                                                      'field':self.field}
                )
        self.valueDialog.set_response_sensitive(gtk.RESPONSE_APPLY,(vals and True or False))
        
    def fieldChangedCB (self, combobox):
        name = cb.cb_get_active_text(combobox)
        self.field = gglobals.NAME_TO_ATTR[name]
        self.populate_treeview()

    def populate_treeview (self):
        """Assume that self.field is set"""
        vals = self.rd.get_unique_values(self.field)
        mod = gtk.ListStore(str)
        for v in vals: mod.append((v,))
        self.treeview.set_model(mod)
        self.newValueComboBoxEntry.set_model(mod)
        self.newValueComboBoxEntry.set_text_column(0)
        self.newValueEntryCompletion.set_model(mod)
        self.newValueEntryCompletion.set_text_column(0)
        
    def run (self): return self.valueDialog.run()

    def dialog_response_cb (self, dialog, response_id):
        if response_id == gtk.RESPONSE_CLOSE:
            self.valueDialog.hide()
        if response_id == gtk.RESPONSE_APPLY:
            criteria,table = self.get_criteria_and_table()
            count = self.rd.fetch_len(table,**criteria)
            count_text = ngettext('Change will affect %s recipe',
                                  'Change will affect %s recipes',
                                  count)%count
            if self.deleteValueButton.get_active():
                label = _('Delete %s where it is %s?')%(self.field,self.val_string)
                yes = gtk.STOCK_DELETE
            else:
                label = _('Change %s from %s to "%s"?')%(self.field,self.val_string,
                                                                                self.newValueEntry.get_text())
                yes = '_Change'
            if de.getBoolean(label=label,
                             sublabel='\n\n'.join([
                count_text,
                _('<i>This change is not reversable.</i>')
                ]),
                             custom_yes=yes,
                             custom_no=gtk.STOCK_CANCEL,
                             cancel=False):

                self.apply_changes(criteria,table)
                self.populate_treeview()

    def get_changes (self):
        if self.deleteValueButton.get_active():
            value = None
        elif self.changeValueButton.get_active():
            value = self.newValueEntry.get_text()
        return {self.field:value}

    def get_selected_values (self, ts=None):
        if not ts:
            ts = self.treeview.get_selection()
        mod,paths = ts.get_selected_rows()
        values = []
        for p in paths:
            values.append(
                mod.get_value(mod.get_iter(p),0)
                )
        return values

    def get_criteria_and_table (self):
        values = self.get_selected_values()
        if len(values) > 1:
            criteria = {self.field:('==',('or',values))}
        elif len(values)==1:
            criteria = {self.field:values[0]}
        if self.field == 'category':
            table = self.rd.catview
        else:
            table = self.rd.rview
        return criteria,table

    def apply_changes (self, criteria, table):
        changes = self.get_changes()
        if self.field=='category' and not changes['category']:
            print 'self.rd.delete_by_criteria(',table,criteria,')'
            self.rd.delete_by_criteria(table,criteria)
            return
        else:
            table = self.rd.rview
        print 'self.rd.update_by_criteria(',table,criteria,changes,')'
        self.rd.update_by_criteria(table,criteria,changes)
        

if __name__ == '__main__':
    import recipeManager
    rm = recipeManager.default_rec_manager()
    w = gtk.Window()
    b = gtk.Button('edit me now')
    w.add(b); w.show_all()
    ve = ValueEditor(rm)
    b.connect('clicked',lambda *args: ve.run())
    w.connect('delete-event',gtk.main_quit)
    gtk.main()
