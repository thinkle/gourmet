#!/usr/bin/env python
import gtk, gobject
from gourmet.widgets import cb_extras

class OptionTable (gtk.Table):

    __gsignals__ = {
        'changed':(gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_OBJECT,)),
        }
    
    # widgets contains the widget, the get method and the set method
    widgets = []
    
    def __init__ (self, options=([]), option_label=None, value_label=None,
                  changedcb=None, xpadding=4, ypadding=4):
        gobject.GObject.__init__(self)
        self.options=options
        self.defaults = options[0:]
        self.xpadding = xpadding
        self.ypadding = ypadding
        self.option_label = option_label
        self.value_label = value_label
        self.connect('changed', changedcb)
        self.set_table()
        self.createOptionLabels()
        self.createOptionWidgets()
       
    def set_table (self):
        self.active_column = 0
        cols = 2
        rows = len(self.options)
        self.all_bools = True
        for l,v in self.options:
            if type(v) is not bool: self.all_bools = False
        if self.all_bools:
            rows = (rows+(rows%2))/2
        if self.option_label or self.value_label:
            rows += 1
        self.rows = rows
        gtk.Table.__init__(self, rows=rows, columns=cols)
       
    def createOptionLabels (self):
        self.option_label = 0
        if self.option_label:
            lab = gtk.Label()
            lab.set_markup('<span weight="bold"><u>%s</u></span>'%self.option_label)
            lab.set_alignment(0.0,0.5)   
            self.attach(lab, 0, 1, 0, 1, xpadding=self.xpadding, ypadding=self.ypadding)
            lab.show()
            self.option_label = 1
        elif self.value_label:
            lab = gtk.Label()
            lab.set_markup('<span weight="bold"><u>%s</u></span>'%self.value_label)
            lab.set_alignment(0.0,0.5)
            lab.set_justify(gtk.JUSTIFY_CENTER)
            self.attach(lab, 1, 2, 0, 1, xpadding=self.xpadding, ypadding=self.ypadding,
                        xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
            lab.show()
            self.option_label = 1

    def createOptionWidgets (self):
        n = self.option_label
        for l,v in self.options:
            if type(v) is bool:
                w = gtk.CheckButton()
                w.set_active(v)
                self.widgets.append([w, 'toggled', 'get_active', 'set_active'])
            elif type(v) is str:
                w = gtk.Entry()
                w.set_text(v)
                self.widgets.append([w, 'changed', 'get_text', 'set_text'])
            elif type(v) in (int,float):
                adj = gtk.Adjustment(value=0, lower=0, upper=100*v, step_incr=v*0.1, page_incr=v*0.5)
                if v is int:
                    w = gtk.SpinButton(adj, digits=0)
                    self.widgets.append([w,'changed', 'get_value_as_int', 'set_value'])
                else:
                    w = gtk.SpinButton(adj, digits=2)
                    self.widgets.append([w, 'changed', 'get_value', 'set_value'])
            elif type(v) in (list,tuple):
                default,value_list = v
                w = gtk.combo_box_new_text()
                for itm in value_list:
                    w.append_text(itm)
                cb_extras.cb_set_active_text(w, default)
                cb_extras.setup_typeahead(w)
                self.widgets.append([w,'changed', 'get_active_text', cb_extras.cb_set_active_text])
            else:
                raise "I don't know what to do with a value of type %s (%s)"%(type(v),v)
            
            # connect changed signal
            w.connect(self.widgets[-1][1],lambda *args: self.emit('changed', w))
                
            # attach our label and our widget
            lab = gtk.Label()
            lab.set_text_with_mnemonic(l)
            lab.set_mnemonic_widget(w)      
            if type(v) is bool:
                col = self.active_column
                w.add(lab)
            else:
                col = 1
                self.attach(lab, 0, 1, n, n+1, xpadding=self.xpadding, ypadding=self.ypadding,
                            xoptions=gtk.FILL,yoptions=gtk.SHRINK)
            lab.show()
            self.attach(w, col, col+1, n, n+1, xpadding=self.xpadding, ypadding=self.ypadding,
                        xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.SHRINK)
            w.show()
            if self.all_bools:
                if n == self.rows - 1:
                    self.active_column += 1
                    n = -1
            n += 1
            
    def set_option (self, n, val):
        widget,signal,get_method,set_method = self.widgets[n]
        self.options[n][1] = val
        if type(set_method) == str:
            getattr(widget,set_method)(val)
        else:
            set_method(widget,val)
        
    def revert (self):
        for n in range(len(self.options)):
            default_val=self.default_options[n][1]
            self.set_option(n,default_val)

    def apply (self):
        for n in range(len(self.options)):
            widget,signal,get_method,set_method = self.widgets[n]
            self.options[n][1]=getattr(widget,get_method)()

if gtk.pygtk_version[1] < 8:
    gobject.type_register(OptionTable)

if __name__ == '__main__':
    w=gtk.Window()
    ot=OptionTable(options=(["_Toggle Option",True],
                            ["_String Option","Hello"],
                            ["_Integer Option",1],
                            ["_Float Option",float(3)],
                            ["_List Option",("C",["A","B","C","D"])],
                             ),
                   option_label="Option",
                   value_label="Value")
    w.add(ot)
    ot.show()
    w.show()
    w.connect('delete_event',gtk.main_quit)
    gtk.main()
    
