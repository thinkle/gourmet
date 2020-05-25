#!/usr/bin/env python
from gi.repository import Gtk
from . import cb_extras
from gi.repository import GObject

class CustomOption (Gtk.HBox):

    __gsignals__ = {
        'changed':(GObject.SignalFlags.RUN_LAST,
                   None,
                   []),
        }

    def __init__ (self):
        # GObject.GObject.__init__(self)
        Gtk.HBox.__init__(self)
        raise NotImplementedError

    def get_value (self):
        raise NotImplementedError

    def set_value (self, val):
        raise NotImplementedError

class OptionTable (Gtk.Table):

    __gsignals__ = {
        'changed':(GObject.SignalFlags.RUN_LAST,
                   None,
                   []),
        }

    def __init__ (self, options=([]), option_label=None, value_label=None,
                  changedcb=None, xpadding=5, ypadding=5):
        Gtk.Table.__init__(self)
        self.options=options
        self.defaults = options[0:]
        self.xpadding = xpadding
        self.ypadding = ypadding
        self.option_label=option_label
        self.value_label=value_label
        self.changedcb=changedcb
        cols = 2
        rows = len(self.options)
        if self.option_label or self.value_label:
            rows += 1
        GObject.GObject.__init__(self, rows=rows, columns=cols)
        self.widgets = []
        self.createOptionWidgets()

    def createOptionWidgets (self):
        n=0
        if self.option_label:
            n=1
            lab=Gtk.Label()
            lab.set_text('<span weight="bold"><u>%s</u></span>'%self.option_label)
            lab.set_use_markup(True)
            lab.set_alignment(0.0,0.5)
            lab.set_justify(Gtk.Justification.LEFT)
            self.attach(lab, 0, 1, 0, 1, xpadding=self.xpadding, ypadding=self.ypadding)
                        #xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK)
            lab.show()
        if self.value_label:
            n=1
            lab=Gtk.Label()
            lab.set_markup('<span weight="bold"><u>%s</u></span>'%self.value_label)
            lab.set_alignment(0,0.5)
            lab.set_justify(Gtk.Justification.CENTER)
            self.attach(lab, 1, 2, 0, 1, xpadding=self.xpadding, ypadding=self.ypadding,
                        xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK)
            lab.show()
        for l,v in self.options:
            if isinstance(v,CustomOption):
                w = v
                self.widgets.append([v,'get_value','set_value'])
                v.connect('changed',lambda * args: self.emit('changed'))
            elif isinstance(v, bool):
                w=Gtk.CheckButton()
                w.set_active(v)
                # widgets contains the widget, the get method and the set method
                self.widgets.append([w,'get_active','set_active'])
                w.connect('toggled',lambda *args: self.emit('changed'))
                if self.changedcb:
                    w.connect('toggled',self.changedcb)
            elif isinstance(v, str):
                w=Gtk.Entry()
                w.set_text(v)
                self.widgets.append([w, 'get_text', 'set_text'])
                w.connect('changed',lambda *args: self.emit('changed'))
                if self.changedcb:
                    w.connect('changed',self.changedcb)
            elif isinstance(v, (int, float)):
                adj = Gtk.Adjustment(value=0, lower=0, upper=100*(v or 1), step_incr=(v or 1)*0.1, page_incr=(v or 1)*0.5)
                if isinstance(v, int):
                    # if an integer...
                    w=Gtk.SpinButton(adj, digits=0)
                    self.widgets.append([w,'get_value_as_int','set_value'])
                else:
                    w=Gtk.SpinButton(adj, digits=2)
                    self.widgets.append([w,'get_value','set_value'])
                w.set_value(v)
                w.connect('changed',lambda *args: self.emit('changed'))
                if self.changedcb:
                    w.connect('changed',self.changedcb)
            elif isinstance(v, (list, tuple)):
                default,value_list = v
                w = Gtk.ComboBoxText()
                for itm in value_list:
                    w.append_text(itm)
                cb_extras.cb_set_active_text(w,default)
                cb_extras.setup_typeahead(w)
                self.widgets.append([w,'get_active_text',cb_extras.cb_set_active_text])
                w.connect('changed',lambda *args: self.emit('changed'))
                if self.changedcb: w.connect('changed',self.changedcb)
            else:
                raise Exception("I don't know what to do with a value of type %s (%s)" % (type(v),v))
            # attach out label and our widget
            lab = Gtk.Label()
            lab.set_text_with_mnemonic(l)
            lab.set_mnemonic_widget(w)
            lab.set_justify(Gtk.Justification.LEFT)
            lab.set_alignment(0,0)
            self.attach(lab, 0, 1, n, n+1, xpadding=self.xpadding, ypadding=self.ypadding,
                        xoptions=Gtk.AttachOptions.FILL,yoptions=Gtk.AttachOptions.SHRINK)
            lab.show()
            self.attach(w, 1, 2, n, n+1, xpadding=self.xpadding, ypadding=self.ypadding,
                        xoptions=Gtk.AttachOptions.FILL,yoptions=Gtk.AttachOptions.SHRINK)
            w.show()
            n += 1

    def set_option (self, n, val):
        widget,get_method,set_method=self.widgets[n]
        self.options[n][1]=val
        if isinstance(set_method, str):
            getattr(widget,set_method)(val)
        else:
            set_method(widget,val)

    def revert (self):
        for n in range(len(self.options)):
            default_val=self.default_options[n][1]
            self.set_option(n,default_val)

    def apply (self):
        for n in range(len(self.options)):
            widget,get_method,set_method=self.widgets[n]
            self.options[n][1]=getattr(widget,get_method)()

if __name__ == '__main__':
    w=Gtk.Window()
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
    w.connect('delete_event',Gtk.main_quit)
    Gtk.main()
