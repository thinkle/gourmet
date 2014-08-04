import re, os.path, os, xml.sax.saxutils, time, textwrap
from gourmet import convert
from gourmet.models.recipe import REC_ATTR_DIC, DEFAULT_ATTR_ORDER, \
                                  DEFAULT_OUTPUT_ATTR_ORDER, \
                                  DEFAULT_TEXT_ATTR_ORDER, TEXT_ATTR_DIC
from gourmet.gglobals import use_threads
from gourmet.gdebug import TimeAction, debug, print_timer_info
from gourmet.plugin_loader import Pluggable, pluggable_method
from gourmet.plugin import BaseExporterPlugin, BaseExporterMultiRecPlugin
from gourmet.threadManager import SuspendableThread
from gourmet.models.ingredient import order_ings
from gourmet.models.meta import session_factory
from gourmet.util.yields import Yield
from gourmet.exporters.exporter import exporter, ExporterMultirec

from sqlalchemy.orm import scoped_session

class PlainTextExporter (exporter):
    """A base exporter class.

    All Gourmet exporters should subclass this class or one of its
    derivatives.

    This class can also be used directly for plain text export.
    """
    DEFAULT_ENCODING = 'utf-8'

    name='exporter'
    ALLOW_PLUGINS_TO_WRITE_NEW_FIELDS = True
    
    def __init__ (self, r, out,
                  change_units=True,
                  imgcount=1,
                  order=['image','attr','ings','text'],
                  attr_order=DEFAULT_OUTPUT_ATTR_ORDER,
                  text_attr_order = DEFAULT_TEXT_ATTR_ORDER,
                  do_markup=True,
                  use_ml=False,
                  convert_attnames=True,
                  fractions=convert.FRACTIONS_ASCII,
                  ):
        """Instantiate our exporter.

        change_units is a flag; if true, change units to keep them readable.
        imgcount is a number we use to start counting our exported images.
        order is a list of our core elements in order: 'image','attr','text' and 'ings'
        attr_order is a list of our attributes in the order we should export them:
                   title, category, cuisine, servings, source, rating, preptime, cooktime
        text_attr_order is a list of our text attributes.
        do_markup is a flag; if true, we interpret tags in text blocks by calling
                  self.handle_markup to e.g. to simple plaintext renderings of tags.
        use_ml is a flag; if true, we escape strings we output to be valid *ml
        convert_attnames is a flag; if true, we hand write_attr a translated attribute name
                         suitable for printing or display. If not, we just hand it the standard
                         attribute name (this is a good idea if a subclass needs to rely on the
                         attribute name staying consistent for processing, since converting attnames
                         will produce locale specific strings.
        """
        exporter.__init__(self, r, out,
                          imgcount=imgcount,
                          change_units=change_units,
                          do_markup=True,
                          use_ml=True)

    @pluggable_method
    def write_attr (self, label, item):
        """Write an attribute with label and text.

        If we've been initialized with convert_attnames=True, the
        label will already be translated to our current
        locale. Otherwise, the label will be the same as it used
        internally in our database.

        So if your method needs to do something special based on the
        attribute name, we need to set convert_attnames to False (and
        do any necessary i18n of the label name ourselves.
        """
        if isinstance(item, Yield):
            item=format(item, "{'fractions': %s}"%self.fractions)
        self.out.write("%s: %s\n"%(label, item))

    @pluggable_method
    def write_text (self, label, text):
        """Write a text chunk.

        This could include markup if we've been initialized with
        do_markup=False.  Otherwise, markup will be handled by the
        handle_markup methods (handle_italic, handle_bold,
        handle_underline).
        """
        self.out.write("\n---\n%s\n---\n"%label)
        ll=text.split("\n")
        for l in ll:
            for wrapped_line in textwrap.wrap(l):
                self.out.write("\n%s"%wrapped_line)
        self.out.write('\n\n')

    def handle_italic (self,chunk):
        """Make chunk italic, or the equivalent."""
        return "*"+chunk+"*"
    
    def handle_bold (self,chunk):
        """Make chunk bold, or the equivalent."""
        return chunk.upper()
    
    def handle_underline (self,chunk):
        """Make chunk underlined, or the equivalent of"""
        return "_" + chunk + "_"

    @pluggable_method
    def write_grouphead (self, text):
        """The start of group of ingredients named TEXT"""
        self.out.write("\n%s:\n"%text.strip())

    @pluggable_method
    def write_groupfoot (self):
        """Mark the end of a group of ingredients.
        """
        pass
    
    @pluggable_method
    def write_ingref (self, ingredient):
        """By default, we don't handle ingredients as recipes, but
        someone subclassing us may wish to do so..."""
        self.write_ing(ingredient)

    @pluggable_method
    def write_ing (self, ingredient):
        """Write ingredient."""
        ingstr = format(ingredient, "{'fractions': %s}"%self.fractions)
        if ingstr:
            self.out.write(ingstr)
        self.out.write("\n")


class PlainTextExporterMultirec (ExporterMultirec):

    name = 'Exporter'

    def __init__ (self, recipes, out,
                  imgcount=1,
                  exporter=exporter,
                  exporter_kwargs={},
                  padding=None):
        self.padding=padding
        
        ExporterMultirec.__init__(
            self,
            recipes, out,
            one_file=True, ext='txt',
            exporter=PlainTextExporter,
            exporter_kwargs=exporter_kwargs,
            padding=padding
            )
