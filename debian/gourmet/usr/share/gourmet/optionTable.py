#!/usr/bin/env python

import gtk

class OptionTable (gtk.Table):
    def __init__ (self, options=([]), option_label=None, value_label=None,
                  changedcb=None, xpadding=5, ypadding=5):
        self.options=options
        self.defaults = options[0:]
        self.xpadding = xpadding
        self.ypadding = ypadding
        self.option_label=option_label
        self.value_label=value_label
        # if pygtk let me emit a signal, I'd just emit a changed signal for any change.
        # but since it doesn't, I let you connect a function by binding changedcb
        self.changedcb=changedcb
        cols = 2
        rows = len(self.options)
        if self.option_label or self.value_label:
            rows += 1
        gtk.Table.__init__(self, rows=rows, columns=cols)
        self.widgets = []
        self.createOptionWidgets()
        
    def createOptionWidgets (self):
        n=0
        if self.option_label:
            n=1
            lab=gtk.Label()
            lab.set_text('<span weight="bold"><u>%s</u></span>'%self.option_label)
            lab.set_use_markup(True)
            lab.set_alignment(0.5,0.5)
            lab.set_justify(gtk.JUSTIFY_CENTER)            
            self.attach(lab, 0, 1, 0, 1, xpadding=self.xpadding, ypadding=self.ypadding)
            lab.show()
        if self.value_label:
            n=1
            lab=gtk.Label()
            lab.set_text('<span weight="bold"><u>%s</u></span>'%self.value_label)
            lab.set_use_markup(True)
            lab.set_alignment(0.5,0.5)
            lab.set_justify(gtk.JUSTIFY_CENTER)
            self.attach(lab, 1, 2, 0, 1, xpadding=self.xpadding, ypadding=self.ypadding)
            lab.show()
        for l,v in self.options:
            if type(v)==type(True):
                w=gtk.CheckButton()
                w.set_active(v)
                # widgets contains the widget, the get method and the set method
                self.widgets.append([w,'get_active','set_active'])
                if self.changedcb:
                    w.connect('toggled',self.changedcb)
            elif type(v)==type(""):
                w=gtk.Entry()
                w.set_text(v)
                self.widgets.append([w, 'get_text', 'set_text'])
                if self.changedcb:
                    w.connect('changed',self.changedcb)
            elif type(v)==type(1) or type(v)==type(float(1)):
                adj = gtk.Adjustment(value=0, lower=0, upper=100000, step_incr=1, page_incr=10)
                if type(v)==type(1):
                    # if an integer...
                    w=gtk.SpinButton(adj, digits=0)
                    self.widgets.append([w,'get_value_as_int','set_value'])
                else:
                    w=gtk.SpinButton(adj, digits=1)
                    self.widgets.append([w,'get_value','set_value'])
                w.set_value(v)
                if self.changedcb:
                    w.connect('changed',self.changedcb)
            else:
                raise "I don't know what to do with a value of type %s (%s)"%(type(v),v)
            # attach out label and our widget
            lab = gtk.Label(l)
            lab.set_justify(gtk.JUSTIFY_LEFT)
            lab.set_alignment(0,0)
            self.attach(lab, 0, 1, n, n+1, xpadding=self.xpadding, ypadding=self.ypadding)
            lab.show()
            self.attach(w, 1, 2, n, n+1, xpadding=self.xpadding, ypadding=self.ypadding)
            w.show()
            n += 1
            
    def revert (self):
        for n in range(len(self.options)):
            widget,get_method,set_method=self.widgets[n]
            default_val=self.default_options[n][1]
            self.options[n][1]=default_val
            getattr(widget,set_method)(default_val)

    def apply (self):
        for n in range(len(self.options)):
            widget,get_method,set_method=self.widgets[n]
            self.options[n][1]=getattr(widget,get_method)()

                
        


if __name__ == '__main__':
    w=gtk.Window()
    ot=OptionTable(options=(["Toggle Option",True],
                            ["String Option","Hello"],
                            ["Integer Option",1],
                            ["Float Option",float(3)]),
                   option_label="Option",
                   value_label="Value")
    w.add(ot)
    ot.show()
    w.show()
    w.connect('delete_event',gtk.main_quit)
    gtk.main()
    
