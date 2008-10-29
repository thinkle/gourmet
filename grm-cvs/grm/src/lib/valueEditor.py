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

    def __init__ (self, rd, rg):
        self.field = None; self.other_field = None
        self.rd = rd; self.rg = rg
        self.glade = gtk.glade.XML(os.path.join(gglobals.gladebase,'valueEditor.glade'))
        self.__setup_widgets__()
        self.__setup_treeview__()
        self.glade.signal_autoconnect({
            'on_changeValueButton_toggled':self.changeValueButtonToggledCB,
            'on_fieldToEditCombo_changed':self.fieldChangedCB,
            'on_otherChangeCheckButton_toggled':self.otherChangeToggleCB,
            'on_otherExpander_activate':self.otherChangeToggleCB,
            'on_otherFieldCombo_changed':self.otherFieldComboChangedCB,
            })
        
    def __setup_widgets__ (self):
        for w in [
            'valueDialog',
            'treeview',
            'fieldToEditCombo','newValueComboBoxEntry',
            'newValueEntry','changeValueButton',
            'deleteValueButton','forEachLabel',
            'otherExpander','otherFieldCombo',
            'otherNewValueEntry','otherNewValueComboBoxEntry',
            'otherValueBlurbLabel','otherChangeCheckButton',
            'leaveValueButton'
            ]:
            setattr(self,w,self.glade.get_widget(w))
        self.act_on_selection_widgets = [
            self.deleteValueButton, self.changeValueButton,
            self.newValueEntry,self.otherChangeCheckButton,
            self.leaveValueButton
            ]
        # Set up the combo-widget at the top with the 
        self.fields = [gglobals.REC_ATTR_DIC[v] for v in self.values]
        cb.set_model_from_list(
            self.fieldToEditCombo,
            self.fields
            )
        cb.set_model_from_list(
            self.otherFieldCombo,
            self.fields
            )
        self.newValueComboBoxEntry.set_sensitive(False)
        self.otherValueBlurbLabel.hide()
        self.newValueEntryCompletion = gtk.EntryCompletion()
        self.newValueEntry.set_completion(self.newValueEntryCompletion)
        self.otherNewValueEntryCompletion = gtk.EntryCompletion()
        self.otherNewValueEntry.set_completion(
            self.otherNewValueEntryCompletion
            )
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
        other_fields = self.fields[:]
        if self.field != 'category':
            other_fields.remove(gglobals.REC_ATTR_DIC[self.field])
        cb.set_model_from_list(
            self.otherFieldCombo,
            other_fields
            )

    def otherFieldComboChangedCB (self, combobox):
        name = cb.cb_get_active_text(combobox)
        self.other_field = gglobals.NAME_TO_ATTR[name]
        if self.other_field == 'category':
            self.otherValueBlurbLabel.hide()
        else:
            self.otherValueBlurbLabel.show()
        mod = self.make_model_for_field(self.other_field)
        self.otherNewValueComboBoxEntry.set_model(mod)
        if self.otherNewValueComboBoxEntry.get_text_column()==-1:
            self.otherNewValueComboBoxEntry.set_text_column(0)
        self.otherNewValueEntryCompletion.set_model(mod)
        self.otherNewValueEntryCompletion.set_text_column(0)
        

    def populate_treeview (self):
        """Assume that self.field is set"""
        mod = self.make_model_for_field(self.field)
        self.treeview.set_model(mod)
        self.newValueComboBoxEntry.set_model(mod)
        if self.newValueComboBoxEntry.get_text_column()==-1:
            self.newValueComboBoxEntry.set_text_column(0)
        self.newValueEntryCompletion.set_model(mod)
        self.newValueEntryCompletion.set_text_column(0)

    def make_model_for_field (self, field):
        vals = self.rd.get_unique_values(field)
        mod = gtk.ListStore(str)
        for v in vals: mod.append((v,))
        return mod
        
    def run (self): return self.valueDialog.run()
    def show (self): return self.valueDialog.show()
    def hide (self): return self.valueDialog.hide()    

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

    def otherChangeToggleCB (self, widg):
        if widg!=self.otherChangeCheckButton:
            self.otherChangeCheckButton.activate()
        if self.otherChangeCheckButton.get_active():
            self.otherExpander.set_expanded(True)
        else:
            self.otherExpander.set_expanded(False)

    def get_changes (self):
        if self.deleteValueButton.get_active():
            value = None
        elif self.changeValueButton.get_active():
            value = self.newValueEntry.get_text()
        return {self.field:value}

    def get_other_changes (self):
        if self.otherChangeCheckButton.get_active():
            return {self.other_field:self.otherNewValueEntry.get_text()}
        else:
            return {}

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
        other_changes = self.get_other_changes()
        if self.field != 'category' and self.other_field != 'category':
            changes.update(other_changes)
        elif other_changes:
            if self.other_field == 'category':
                # Inefficient, but works with our current backend
                # interface... and shouldn't be called often, so we'll
                # deal with the ugliness for now
                for r in self.rd.fetch_all(self.rd.rview,**criteria):
                    if not self.rd.fetch_one(self.rd.catview,{'id':r.id}):
                        self.rd.do_add_cat({'id':r.id,'category':other_changes['category']})
            else:
                if self.field=='category':
                    IDs = [r.id for r in self.rd.fetch_all(self.rd.catview,**criteria)]
                    new_criteria = {'id':('==',('or',IDs))}
                    self.rd.update_by_criteria(
                        self.rd.rview,
                        new_criteria,
                        other_changes
                        )
                else:
                    self.rd.update_by_criteria(
                        self.rd.rview,
                        criteria,
                        other_changes
                        )
        if self.field=='category' and not changes['category']:
            self.rd.delete_by_criteria(table,criteria)
        else:
            if self.field=='category':
                table = self.rd.catview
            else:
                table = self.rd.rview
            self.rd.update_by_criteria(table,criteria,changes)
        self.rg.reset_search()

if __name__ == '__main__':
    import recipeManager
    rm = recipeManager.default_rec_manager()
    class DummyRG:
        def reset_search (): pass
    w = gtk.Window()
    b = gtk.Button('edit me now')
    w.add(b); w.show_all()
    ve = ValueEditor(rm,DummyRG())
    b.connect('clicked',lambda *args: ve.run())
    w.connect('delete-event',gtk.main_quit)
    gtk.main()
