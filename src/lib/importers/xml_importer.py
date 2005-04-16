import xml.sax, re, sys
import importer
from gourmet.gdebug import *
from gourmet.gglobals import *

class RecHandler (xml.sax.ContentHandler, importer.importer):
    def __init__ (self, recData, total=None, prog=None):
        self.elbuf = ""
        xml.sax.ContentHandler.__init__(self)
        importer.importer.__init__(self,rd=recData,total=total,prog=prog,threaded=True,
                                   do_markup=False)

    def characters (self, ch):
        self.elbuf += ch

class converter:
    def __init__ (self, filename, rd, recHandler, recMarker=None, threaded=False, progress=None):

        """filename is our file to parse.  rd is our recdata object.
        recHandler is our recHandler class.  We expect subclasses
        effectively to call as as we are, but provide recMarker (a
        string that identifies a recipe, so we can quickly count total
        recipes and update users as to progress) and our recHandler class."""

        self.rd = rd
        self.recMarker=recMarker
        self.fn = filename
        self.threaded = threaded
        self.progress = progress
        self.rh = recHandler(recData=self.rd,prog=self.progress)
        self.terminate = self.rh.terminate
        self.suspend = self.rh.suspend
        self.resume = self.rh.resume
        if not self.threaded: self.run()

    def run (self):
        # count the recipes in the file        
        t = TimeAction("rxml_to_metakit.run counting lines",0)
        f=open(self.fn)
        recs = 0
        for l in f.readlines():
            if l.find(self.recMarker) >= 0: recs += 1
        f.close()
        t.end()
        self.rh.total=recs
        self.parse = xml.sax.parse(self.fn, self.rh)

