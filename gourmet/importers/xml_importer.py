import xml.sax, xml.sax.saxutils, re, sys
import importer
from gourmet.gdebug import TimeAction
from gourmet.recipeManager import get_recipe_manager # for getting out database...
from gourmet.threadManager import SuspendableThread

def unquoteattr (str):
    return xml.sax.saxutils.unescape(str).replace("_"," ")

class RecHandler (xml.sax.ContentHandler, importer.Importer):
    def __init__ (self, total=None, conv=None, parent_thread=None):
        self.elbuf = ""
        xml.sax.ContentHandler.__init__(self)
        importer.Importer.__init__(self,total=total,
                                   do_markup=False, conv=conv)
        self.parent_thread = parent_thread
        self.check_for_sleep = parent_thread.check_for_sleep
        self.terminate = parent_thread.terminate
        self.resume = parent_thread.resume
        self.suspend = parent_thread.suspend
        self.emit = parent_thread.emit
        
    def characters (self, ch):
        self.elbuf += ch

class Converter (importer.Importer):
    def __init__ (self, filename, recHandler, recMarker=None,
                  conv=None, name='XML Importer'):

        """Initialize an XML converter which will use recHandler to parse data.
        
        filename - our file to parse (or the name of the file).

        rd - our recdata object.

        recHandler - our recHandler class.

        recMarker - a string that identifies a recipe, so we can
        quickly count total recipes and update users as to progress)
        and our recHandler class.

        We expect subclasses effectively to call as as we are with
        their own recHandlers.
        """

        self.recMarker=recMarker
        self.fn = filename
        self.rh = recHandler(conv=conv,parent_thread=self)
        self.added_ings = self.rh.added_ings
        self.added_recs = self.rh.added_recs
        self.terminate = self.rh.terminate
        self.suspend = self.rh.suspend
        self.resume = self.rh.resume
        importer.Importer.__init__(self,name=name)

    def do_run (self):
        # count the recipes in the file        
        t = TimeAction("rxml_to_metakit.run counting lines",0)
        if isinstance(self.fn, basestring):
            f=file(self.fn,'rb')
        else:
            f=self.fn
        recs = 0
        for l in f.readlines():
            if l.find(self.recMarker) >= 0: recs += 1
            if recs % 5 == 0: self.check_for_sleep()
        f.close()
        t.end()
        self.rh.total=recs
        self.parse = xml.sax.parse(self.fn, self.rh)
        self.added_ings = self.rh.added_ings
        self.added_recs = self.rh.added_recs
        importer.Importer._run_cleanup_(self.rh)

        
        
