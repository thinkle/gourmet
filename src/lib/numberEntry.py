import validatingEntry
import gtk, gobject
import convert
import re
from gettext import gettext as _

class NumberEntry (validatingEntry.ValidatingEntry):

    error_message = _('Invalid input.') + ' ' + _('Not a number.')

    in_progress_regexp = """
        ^ # start at
        %(NUMBER_START_REGEXP)s+ # a number
        %(NUMBER_END_NO_RANGE_REGEXP)s*
        $ # end
        """%convert.__dict__
    
    def __init__ (self):
        self.in_progress_matcher = re.compile(self.in_progress_regexp,
                                              re.VERBOSE|re.UNICODE)
        validatingEntry.ValidatingEntry.__init__(self)
        self.entry.get_value = self.get_value
        self.entry.set_value = self.get_value

    def find_errors_in_progress (self, txt):
        txt = txt.strip() # we don't care about leading/trailing space
        if not txt: return
        if not self.in_progress_matcher.match(txt):
            return self.error_message

    def find_completed_errors (self, txt):
        if txt and not convert.frac_to_float(txt):
            return self.error_message

    def set_value (self, n):
        self.set_text(convert.float_to_frac(n,fractions=convert.FRACTIONS_ASCII))

    def get_value (self):
        return convert.frac_to_float(self.get_text())

class RangeEntry (NumberEntry):
    in_progress_regexp = """
        ^ # start at
        %(NUMBER_START_REGEXP)s+ # a number
        %(NUMBER_END_REGEXP)s*
        (%(RANGE_REGEXP)s|[Tt][Oo]?)?
        %(NUMBER_START_REGEXP)s*
        %(NUMBER_END_REGEXP)s*
        $ # end
        """%convert.__dict__

    def find_completed_errors (self, txt):
        split =  convert.RANGE_MATCHER.split(txt)
        if len(split)==1:
            return NumberEntry.find_completed_errors(self,txt)
        elif len(split)>2:
            return "A range can only have 2 items."
        else:
            error1 = NumberEntry.find_completed_errors(self,split[0])
            if error1: return error1
            error2 = NumberEntry.find_completed_errors(self,split[1])
            if error2: return error2

    def set_value (self, n):
        if type(n)==tuple:
            if len(n)==1:
                n = n[0]
            if len(n)>2:
                raise ValueError
            else:
                self.set_text(
                    convert.float_to_frac(n[0],
                                          fractions=convert.FRACTIONS_ASCII)\
                    +' - '+\
                    convert.float_to_frac(n[1],
                                          fractions=convert.FRACTIONS_ASCII)
                    )
                return
        NumberEntry.set_value(self,n)

    def get_value (self):
        txt = gtk.get_text()
        split = convert.RANGE_MATCHER.split(txt)
        if len(split)==1: return NumberEntry.get_value(self)
        if len(split)>2: return None
        else:
            return tuple([convert.frac_to_float(t) for t in split])
        
if gtk.pygtk_version[1] < 8: gobject.type_register(NumberEntry)

if __name__ == '__main__':
    w = gtk.Window()
    hb = gtk.HBox()
    w.connect('delete-event',lambda *args: gtk.main_quit())
    vb = gtk.VBox(); vb.show()
    l = gtk.Label('Number Entry:')
    l.show()
    hb.pack_start(l)
    ne = NumberEntry(); ne.show()
    def foo (widget):
        print 'Changed!',widget,widget.get_value()
    ne.connect('changed',foo)
    hb.pack_start(ne)
    hb.show()
    hb2 = gtk.HBox()
    l = gtk.Label('Range Entry:'); l.show()
    hb2.pack_start(l)
    rent = RangeEntry(); rent.show()
    hb2.pack_start(rent)
    hb2.show()
    vb.pack_start(hb, fill=False, expand=False)
    vb.pack_start(hb2,fill=False,expand=False)
    qb = gtk.Button(stock=gtk.STOCK_QUIT); qb.show()
    qb.connect('clicked',lambda *args: w.hide() or gtk.main_quit())
    vb.pack_start(qb, fill=False, expand=False)
    w.add(vb)
    w.present()
    gtk.main()
