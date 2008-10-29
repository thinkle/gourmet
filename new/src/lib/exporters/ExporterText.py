import re, Image, os.path, os, xml.sax.saxutils, time, shutil, urllib, textwrap, types
from gourmet import gglobals
from gourmet.gdebug import *
from gettext import gettext as _

from gourmet.recipe import converter

REC_ATTR_DIC = gglobals.REC_ATTR_DIC
DEFAULT_ATTR_ORDER = gglobals.DEFAULT_ATTR_ORDER
DEFAULT_TEXT_ATTR_ORDER = gglobals.DEFAULT_TEXT_ATTR_ORDER

class ExporterText(Export):

    def write_attr (self, label, text):
        self.out.write("%s: %s\n"%(label, text.strip()))

    def write_text (self, label, text):
        self.out.write("\n---\n%s\n---\n"%label)
        ll=text.split("\n")
        for l in ll:
            for wrapped_line in textwrap.wrap(l):
                self.out.write("\n%s"%wrapped_line)
        self.out.write('\n\n')

    def write_grouphead (self, text):
        self.out.write("\n%s:\n"%text.strip())

    def handle_italic (self, chunk):
        return "*"+chunk+"*"
    
    def handle_bold (self, chunk):
        return chunk.upper()
    
    def handle_underline (self, chunk):
        return "_" + chunk + "_"

    def write_grouphead (self, text):
        self.out.write("\n%s:\n"%text.strip())
        
    def write_ing (self, ingredient=None):
        if ingredient.amount:
            self.out.write("%s"%ingredient.amount)
        if ingredient.unit:
            self.out.write(" %s"%ingredient.unit)
        if ingredient.item:
            self.out.write(" %s"%ingredient.item)
        if ingredient.optional:
            self.out.write(" (%s)"%_("optional"))
        self.out.write("\n")
