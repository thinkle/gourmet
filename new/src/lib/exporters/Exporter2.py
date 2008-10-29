import re, Image, os.path, os, xml.sax.saxutils, time, shutil, urllib, textwrap, types
from gourmet import gglobals
from gourmet.gdebug import *
from gettext import gettext as _

from gourmet.recipe import converter

REC_ATTR_DIC = gglobals.REC_ATTR_DIC
DEFAULT_ATTR_ORDER = gglobals.DEFAULT_ATTR_ORDER
DEFAULT_TEXT_ATTR_ORDER = gglobals.DEFAULT_TEXT_ATTR_ORDER

class exporter:
    """
    A base exporter class.

    All Gourmet exporters should subclass this class or one of its
    derivatives.

    This class can also be used directly for plain text export.
    """
    DEFAULT_ENCODING = 'utf-8'

    def __init__ (self, rd, r, out,
                  conv=None,
                  imgcount=1,
                  order=['image','attr','ings','text'],
		  attr_order=DEFAULT_ATTR_ORDER,
                  text_attr_order = DEFAULT_TEXT_ATTR_ORDER,
                  do_markup=True,
                  use_ml=False,
                  convert_attnames=True,
                  fractions=converter.FRACTIONS_ASCII
                  ):
        """Instantiate our exporter.

        conv is a preexisting convert.converter() class
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
        tt = TimeAction('exporter.__init__()',0)
	    self.attr_order = attr_order
        self.text_attr_order = text_attr_order
        self.out = out
        self.r = r
        self.rd = rd
        self.do_markup = do_markup
        self.fractions = fractions
        self.use_ml = use_ml
        self.convert_attnames = convert_attnames
        self.conv = converter.conv
        self.imgcount = imgcount
        self.write_head()
        self.images = []
        for task in order:
            if task == 'image':
                if self._grab_attr_(self.r,'image'):
                    self.write_image(self.r.image)
            if task=='attr':
                self._write_attrs_()
            elif task=='text':
                self._write_text_()
            elif task=='ings': 
                self._write_ings_()
        self.write_foot()
        tt.end()

    # Internal methods -- ideally, subclasses should have no reason to
    # override any of these methods.
        
    def _write_attrs_ (self):
        self.write_attr_head()
        for a in self.attr_order:
            gglobals.gt.gtk_update()
            txt=self._grab_attr_(self.r,a)
            debug('_write_attrs_ writing %s=%s'%(a,txt),5)
            if txt and (
                (type(txt) not in [str,unicode])
                or
                txt.strip()
                ):
                if (a=='preptime' or a=='cooktime') and a.find("0 ")==0: pass
                else:
                    if self.convert_attnames:
                        self.write_attr(REC_ATTR_DIC[a],txt)
                    else:
                        self.write_attr(a,txt)
        self.write_attr_foot()

    def _write_text_ (self):
            # End of non-Gourmet code
            txt=self._grab_attr_(self.r,a)
            if txt and txt.strip():
                if self.do_markup:  txt=self.handle_markup(txt)
                #else: print 'exporter: do_markup=False'
                if not self.use_ml: txt = xml.sax.saxutils.unescape(txt)
                if self.convert_attnames:
                    self.write_text(gglobals.TEXT_ATTR_DIC[a],txt)
                else:
                    self.write_text(a,txt)

    def _write_ings_ (self):
        """Write all of our ingredients.
        """
        ingredients = self.r.ingredients
        if not ingredients: return
        self.write_inghead()
        for ing in ingredients:
            pass
        self.write_ingfoot()

    def _grab_attr_ (self, obj, attr):
        # This is a bit ugly -- we allow exporting categories as if
        # they were a single attribute even though we in fact allow
        # multiple categories.
        if attr=='category':
            return ', '.join(obj.categories)
        try:
            ret = getattr(obj,attr)
        except:
            return None
        else:
            if attr in ['preptime','cooktime']:
                # this 'if' ought to be unnecessary, but is kept around
                # for db converting purposes -- e.g. so we can properly
                # export an old DB
                if ret and type(ret)!=str: 
                    ret = converter.seconds_to_timestring(ret,fractions=self.fractions)
            elif attr=='rating' and ret and type(ret)!=str:
                if ret/2==ret/2.0:
                    ret = "%s/5 %s"%(ret/2,_('stars'))
                else:
                    ret = "%s/5 %s"%(ret/2.0,_('stars'))
            elif attr=='servings' and type(ret)!=str:
                ret = converter.float_to_frac(ret,fractions=self.fractions)
            if type(ret) in [str,unicode] and attr not in ['thumb','image']:
                try:
                    ret = ret.encode(self.DEFAULT_ENCODING)
                except:
                    print "oops:",ret,"doesn't look like unicode."
                    raise
            return ret

    # Below are the images inherited exporters should subclass.

    def write_image (self, image):
        """Write image based on binary data for an image file (jpeg format)."""
        raise NotImplementedError

    def write_head (self):
        """Write any necessary header material at recipe start."""
        raise NotImplementedError

    def write_foot (self):
        """Write any necessary footer material at recipe end."""
        raise NotImplementedError

    def write_inghead(self):
        """Write any necessary markup before ingredients."""
        raise NotImplementedError

    def write_ingfoot(self):
        """Write any necessary markup after ingredients."""
        raise NotImplementedError

    def write_attr_head (self):
        """Write any necessary markup before attributes."""
        raise NotImplementedError
    
    def write_attr_foot (self):
        """Write any necessary markup after attributes."""
        raise NotImplementedError

    def write_attr (self, label, text):
        """
        Write an attribute with label and text.

        If we've been initialized with convert_attnames=True, the
        label will already be translated to our current
        locale. Otherwise, the label will be the same as it used
        internally in our database.

        So if your method needs to do something special based on the
        attribute name, we need to set convert_attnames to False (and
        do any necessary i18n of the label name ourselves.
        """
        raise NotImplementedError

    def write_text (self, label, text):
        """
        Write a text chunk.

        This could include markup if we've been initialized with
        do_markup=False.  Otherwise, markup will be handled by the
        handle_markup methods (handle_italic, handle_bold,
        handle_underline).
        """
        raise NotImplementedError

    def handle_markup (self, txt):
        """Handle markup inside of txt."""
        import pango
        outtxt = ""
        try:
            al,txt,sep = pango.parse_markup(txt,u'\x00')
        except:
            al,txt,sep = pango.parse_markup(xml.sax.saxutils.escape(txt),u'\x00')
        ai = al.get_iterator()
        more = True
        while more:
            fd,lang,atts=ai.get_font()
            chunk = xml.sax.saxutils.escape(txt.__getslice__(*ai.range()))
            trailing_newline = ''
            fields=fd.get_set_fields()
            if fields != 0: #if there are fields
                # Sometimes we get trailing newlines, which is ugly
                # because we end up with e.g. <b>Foo\n</b>
                #
                # So we define trailing_newline as a variable
                if chunk and chunk[-1]=='\n':
                    trailing_newline = '\n'; chunk = chunk[:-1]
                if 'style' in fields.value_nicks and fd.get_style()==pango.STYLE_ITALIC:
                    chunk=self.handle_italic(chunk)
                if 'weight' in fields.value_nicks and fd.get_weight()==pango.WEIGHT_BOLD:
                    chunk=self.handle_bold(chunk)
            for att in atts:
                if att.type==pango.ATTR_UNDERLINE and att.value==pango.UNDERLINE_SINGLE:
                    chunk=self.handle_underline(chunk)
            outtxt += chunk + trailing_newline
            more=ai.next()
        return outtxt

    def handle_italic (self,chunk):
        """Make chunk italic, or the equivalent."""
        raise NotImplementedError
    
    def handle_bold (self,chunk):
        """Make chunk bold, or the equivalent."""
        raise NotImplementedError
    
    def handle_underline (self,chunk):
        """Make chunk underlined, or the equivalent of"""
        raise NotImplementedError

    def write_grouphead (self, text):
        """The start of group of ingredients named TEXT"""
        raise NotImplementedError

    def write_groupfoot (self):
        """Mark the end of a group of ingredients.
        """
        raise NotImplementedError
    
    def write_ingref (self, reference=None):
        """By default, we don't handle ingredients as recipes, but
        someone subclassing us may wish to do so..."""
        self.write_ing(reference)

    def write_ing (self, ingredient=None):
        """Write ingredient."""
        raise NotImplementedError
