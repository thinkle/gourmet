import convert
import gtk, gtk.glade
from gglobals import *
from gdebug import *
from gtk_extras.cb_extras import *
from gettext import gettext as _

class ConvGui:
    """This is a simple interface for the converter."""
    def __init__ (self, converter=None,
                  unitModel=None,
                  amt1=None, unit1=None, item=None,
                  okcb=None
                  ):
        self.possible_conversions = None
        self.glade = gtk.glade.XML(os.path.join(gladebase,'converter.glade'))
        self.conv = convert.get_converter()
        self.changing_item = False
        self.okcb = okcb
        self.widget_names = ['window','amt1Entry', 'amt2Label', 'unit1ComboBox', 'unit2ComboBox',
                   'itemComboBox', 'densitySpinButton', 'useDensityCheckButton', 'statusbar','expander1','messageLabel']
        # grab all our widgets
        for w in self.widget_names:
            setattr(self,w,self.glade.get_widget(w))
        # HACK FOR READABILITY w/o glade change
        self.resultLabel = self.amt2Label
        self.resultLabel.set_use_markup(True)
        self.resultLabel.set_line_wrap(True)
        if unitModel: self.unitModel=unitModel
        else: self.unitModel=UnitModel(self.conv)
        #self.unit2Model = self.unitModel.filter_new()
        self.unit1ComboBox.set_model(self.unitModel)
        self.unit1ComboBox.set_wrap_width(3)
        self.unit2ComboBox.set_wrap_width(3)        
        #self.unit2Model.set_visible_func(self.unit_filter)
        #self.unit2ComboBox.set_model(self.unit2Model)
        self.unit2ComboBox.set_model(self.unitModel)
        for combobox in [self.unit1ComboBox, self.unit2ComboBox]:
            cell = gtk.CellRendererText()            
            combobox.pack_start(cell, True)
            combobox.add_attribute(cell, 'text', 1)
            setup_typeahead(combobox)
        #self.itemComboBox.append_text('None')
        ikeys = self.conv.density_table.keys()
        ikeys.sort()
        for itm in ikeys:
            self.itemComboBox.append_text(itm)
        if len(self.conv.density_table.keys()) > 8:
            self.itemComboBox.set_wrap_width(3)
        setup_typeahead(self.itemComboBox)
        if amt1:
            self.amt1Entry=self.conv.float_to_frac(amt1)
        self.glade.signal_autoconnect({
            'amt1changed':self.changed,
            'unit1changed':self.changed,
            'unit2changed':self.changed,
            'itemChanged':self.density_itm_changed,
            'densitySpinChanged':self.density_spin_changed,
            'densityChecked':self.density_toggled,
            'close':self.close,
            })
        self.last_amt1 = None
        self.last_amt2 = None
        self.last_unit1 = None
        self.last_unit2 = None
        if unit1 and self.conv.unit_dict.has_key[unit1]:
            u = self.conv.unit_dict[unit1]
            cb_set_active_text(self.unit1ComboBox,u)
        if amt1: self.amt1Entry.set_text("%s"%amt1)
        if item: cb_set_active_text(self.itemComboBox,item)

    def changed (self, *args):
        amt1 = convert.frac_to_float(self.amt1Entry.get_text())
        #amt2 = convert.frac_to_float(self.resultLabel.get_text())
        #amt2 = self.amt2
        unit1 = cb_get_active_text(self.unit1ComboBox)
        unit2 = cb_get_active_text(self.unit2ComboBox)
        if unit1 != self.last_unit1:
            self.get_possible_conversions()
        #self.unit2Model.refilter()
        if amt1 and unit2:
            self.convert(amt1, unit1, unit2)
        self.last_amt1 = amt1
        #self.last_amt2 = amt2
        self.last_unit1 = unit1
        self.last_unit2 = unit2

    def convert (self, amt1, unit1, unit2):
        density=None
        #if self.useDensityCheckButton.get_active():
        density=self.densitySpinButton.get_value()
        if density <= 0 or not self.expander1.get_expanded(): density = None
        conversion = self.conv.convert_fancy(unit1, unit2, density=density)
        message = ""
        if conversion:
            amt2 = amt1 * conversion
            if amt2 < (0.05):
                retAmt = "%1.3e"%amt2
            else:
                retAmt = convert.float_to_frac(amt2)
            result = "%s %s = <b>%s</b> %s"%(convert.float_to_frac(amt1),
                                             unit1,
                                             retAmt,
                                             unit2)
        else:
            result = _("Cannot convert %s to %s")%(unit1,unit2)
            if not density:
                message=  _("Need density information.")
                if not self.expander1.get_expanded():
                    self.expander1.set_expanded(True)
                    self.changed()
                    self.itemComboBox.activate()
        self.resultLabel.set_text(result)
        self.resultLabel.set_use_markup(True)
        self.resultLabel.set_line_wrap(True)
        self.messageLabel.set_text("<i>%s</i>"%message)
        self.messageLabel.set_use_markup(True)
        
        

    def message (self, msg):
        id=self.statusbar.get_context_id('main')
        self.statusbar.push(id,msg)
        
    def unit_filter (self, mod, iter):
        u = mod.get_value(iter,0)
        if not self.possible_conversions:
            self.get_possible_conversions()
        if u in self.possible_conversions:
            return True
        else:
            return False

    def get_possible_conversions (self):
        density=self.densitySpinButton.get_value()
        #if self.useDensityCheckButton.get_active():
        #    density=self.densitySpinButton.get_value()
        if density <= 0 or not self.expander1.get_expanded(): density = None
        u1 = cb_get_active_text(self.unit1ComboBox)
        self.possible_conversions = self.conv.get_all_conversions(u1,density=density)
        
    def density_toggled (self, *args):
        sens =  self.useDensityCheckButton.get_active()
        self.densitySpinButton.set_sensitive(sens)
        self.itemComboBox.set_sensitive(sens)
        self.changed()

    def density_itm_changed (self, *args):
        debug('density_itm_changed',5)
        self.changing_item=True
        itm=cb_get_active_text(self.itemComboBox)
        if itm != _('None'):
            self.densitySpinButton.set_value(self.conv.density_table[itm])
        else:
            self.densitySpinButton.set_value(0)
        self.changed()
        self.changing_item=False

    def density_spin_changed (self, *args):
        debug('density_spin_changed',5)
        if not self.changing_item:
            self.itemComboBox.set_active(0)
            self.changed()

    def close (self, *args):
        self.window.hide()
        if self.okcb:
            self.okcb(cb_get_active_text(self.unit2ComboBox),resultLabel.get_text())
        if __name__ == '__main__':
            gtk.main_quit()

class UnitModel (gtk.ListStore):
    def __init__ (self, converter):
        debug('UnitModel.__init__',5)
        self.conv = converter
        gtk.ListStore.__init__(self, str, str)
        # the first item of each conv.units
        lst = map(lambda a: (a[1][0],a[0]), filter(lambda x: not (converter.unit_to_seconds.has_key(x[1][0])
                                                                  or
                                                                  converter.unit_to_seconds.has_key(x[0])
                                                                  )
                                                   ,
                                                   self.conv.units)
                  )
        lst.sort()
        for ulong,ushort in lst:
            iter=self.append()
            self.set_value(iter,0,ushort)
            if ulong != ushort:
                ulong = "%s (%s)"%(ulong,ushort)
            self.set_value(iter,1,"%s"%ulong)

if __name__ == '__main__':
    gladebase="/home/tom/Projects/gourmet/glade/"
    cg=ConvGui()
    gtk.main()
    
