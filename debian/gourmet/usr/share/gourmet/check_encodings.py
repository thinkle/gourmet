import gtk
from gdebug import debug
import dialog_extras as de
from gettext import gettext as _

class CheckEncoding:
    def __init__ (self, file, encodings=None):
        if encodings: self.encodings = encodings
        else:
            self.encodings = ['utf-8','ascii','cp850','latin_1','cp1252']
        self.all_encodings= ['ascii','cp037','cp424',
                        'cp437','cp500','cp737','cp775','cp850','cp852',
                        'cp855','cp856','cp857','cp860','cp861','cp862',
                        'cp863','cp864','cp865','cp869','cp874','cp875',
                        'cp1006','cp1026','cp1140','cp1250','cp1251',
                        'cp1252','cp1253','cp1254','cp1255','cp1256',
                        'cp1258','latin_1','iso8859_2','iso8859_3',
                        'iso8859_4','iso8859_5','iso8859_6','iso8859_7',
                        'iso8859_8','iso8859_9','iso8859_10','iso8859_13',
                        'iso8859_14','iso8859_15','koi8_r','koi8_u',
                        'mac_cyrillic','mac_greek','mac_iceland','mac_latin2',
                        'mac_roman','mac_turkish','utf_16','utf_16_be',
                        'utf_16_le','utf_7','utf_8']
        f = open(file,'r')
        self.txt = f.read()
        f.close()

    def test_encodings (self):
        for e in self.encodings:
            try:
                t=self.txt.decode(e)
                return (e,t)
            except UnicodeDecodeError:
                pass

    def test_all_encodings (self):
        self.possible_encodings = {}
        for e in self.all_encodings:
            try:
                d=self.txt.decode(e)
                self.possible_encodings[e]=d.encode('utf8')
            except UnicodeDecodeError:
                pass
        return self.possible_encodings

class GetFile (CheckEncoding):
    """Handed a filename, return a list of lines."""
    def __init__ (self,file,encodings=None):

        CheckEncoding.__init__(self,file,encodings)
        enc=self.test_encodings()
        if enc:
            self.enc,txt = enc
            self.lines = txt.split('\n')
        else:
            encodings=self.test_all_encodings()
            encoding = self.getEncoding(encodings=encodings)
            self.enc = encoding
            self.lines = encodings[encoding].split('\n')
        debug('reading file %s as encoding %s'%(file, self.enc))
        self.lines = map(lambda l: l.encode(),self.lines)
                                        
def get_file (file, encodings=None):
    gf = GetFile(file, encodings)
    debug('returning lines %s,%s,%s'%(gf.lines[0],gf.lines[1],gf.lines[2]),0)
    return gf.lines

class EncodingDialog (de.optionDialog):
    def __init__ (self, default=None, label=_("Select encoding"),
                  sublabel=_("Cannot determine proper encoding. Please select the correct encoding from the following list."),
                  expander_label=_("See _file with encoding"),
                  encodings=[],
                 ):
        self.expander_label=expander_label
        self.encodings = encodings
        options = self.create_options()
        expander=self.create_expander()
        de.optionDialog.__init__(self, default=default,label=label, sublabel=sublabel,
                                 options=options, expander=expander)
        self.optionMenu.connect('activate',self.change_encoding)

    def get_option (self,widget):
        de.optionDialog.get_option(self,widget)
        self.change_encoding()

    def create_options (self):
        return self.encodings.keys()

    def create_expander (self):
        self.sw = gtk.ScrolledWindow()
        self.tv = gtk.TextView()
        self.buffer = self.tv.get_buffer()
        self.sw.add(self.tv)
        self.sw.show_all()
        return self.expander_label,self.sw

    def change_encoding (self):
        self.buffer.set_text(self.encodings[self.ret])
        debug('changed text to encoding %s'%self.ret,0)
        
def getEncoding (*args,**kwargs):
    d=EncodingDialog(*args,**kwargs)
    return d.run()
