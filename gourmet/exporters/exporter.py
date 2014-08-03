import re, os.path, os, xml.sax.saxutils, time, shutil, urllib, textwrap, types
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

from sqlalchemy.orm import scoped_session

class exporter (SuspendableThread, Pluggable):
    """A base exporter class.

    All Gourmet exporters should subclass this class or one of its
    derivatives.

    This class can also be used directly for plain text export.
    """
    DEFAULT_ENCODING = 'utf-8'

    name='exporter'
    ALLOW_PLUGINS_TO_WRITE_NEW_FIELDS = True
    
    def __init__ (self, r, out,
                  conv=None,
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
        self.attr_order=attr_order
        self.text_attr_order = text_attr_order
        self.out = out
        self.Session = scoped_session(session_factory)
        self.session = self.Session()
        self.r = self.session.merge(r)
        self.do_markup=do_markup
        self.fractions=fractions
        self.use_ml=use_ml
        self.convert_attnames = convert_attnames
        if not conv: conv=convert.get_converter()
        self.conv=conv
        self.imgcount=imgcount
        self.images = []
        self.order = order
        Pluggable.__init__(self,[BaseExporterPlugin])
        SuspendableThread.__init__(self,self.name)

    def do_run (self):
        self.write_head()
        for task in self.order:
            if task=='image':
                if getattr(self.r,'image'):
                    self.write_image(self.r.image)
            if task=='attr':
                self._write_attrs_()

            elif task=='text':
                self._write_text_()
            elif task=='ings': self._write_ings_()
        self.write_foot()
        self.Session.remove()


    # Internal methods -- ideally, subclasses should have no reason to
    # override any of these methods.
    @pluggable_method
    def _write_attrs_ (self):
        self.write_attr_head()
        for a in self.attr_order:
            txt=getattr(self.r,a)
            debug('_write_attrs_ writing %s=%s'%(a,txt),1)
            if txt and (
                (type(txt) not in [str,unicode])
                or
                txt.strip()
                ):
                if (a=='preptime' or a=='cooktime') and a.find("0 ")==0: pass
                else:
                    if self.convert_attnames:
                        self.write_attr(REC_ATTR_DIC.get(a,a),txt)
                    else:
                        self.write_attr(a,txt)
        self.write_attr_foot()

    @pluggable_method
    def _write_text_ (self):
        #print 'exporter._write_text_',self.text_attr_order,'!'
        for a in self.text_attr_order:
            txt=getattr(self.r,a)
            if txt and txt.strip():
                if self.do_markup:  txt=self.handle_markup(txt)
                #else: print 'exporter: do_markup=False'
                if not self.use_ml: txt = xml.sax.saxutils.unescape(txt)
                if self.convert_attnames:
                    self.write_text(TEXT_ATTR_DIC.get(a,a),txt)
                else:
                    self.write_text(a,txt)

    @pluggable_method
    def _write_ings_ (self):
        """Write all of our ingredients.
        """
        if not self.r.ingredients:
            return
        self.write_inghead()
        for g,ings in order_ings(self.r.ingredients):
            if g:
                self.write_grouphead(g)            
            for i in ings:
                if getattr(i,'refid'):
                    self.write_ingref(i)
                else:
                    self.write_ing(i)
            if g:
                self.write_groupfoot()
        self.write_ingfoot()

    # Below are the images inherited exporters should
    # subclass. Subclasses overriding methods should make these
    # pluggable so that plugins can fiddle about with things as they
    # see fit.

    def write_image (self, image):
        """Write image based on binary data for an image file (jpeg format)."""
        pass


    def write_head (self):
        """Write any necessary header material at recipe start."""
        pass

    def write_foot (self):
        """Write any necessary footer material at recipe end."""
        pass

    @pluggable_method
    def write_inghead(self):
        """Write any necessary markup before ingredients."""
        self.out.write("\n---\n%s\n---\n"%_("Ingredients"))

    @pluggable_method
    def write_ingfoot(self):
        """Write any necessary markup after ingredients."""
        pass

    @pluggable_method
    def write_attr_head (self):
        """Write any necessary markup before attributes."""
        pass

    @pluggable_method
    def write_attr_foot (self):
        """Write any necessary markup after attributes."""
        pass

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
            text=format(item, "{'fractions': %s}"%self.fractions)
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

    def handle_markup (self, txt):
        """Handle markup inside of txt."""
        if txt == None:
            print 'Warning, handle_markup handed None'
            return ''
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

class exporter_mult (exporter):
    """A basic exporter class that can handle a multiplied recipe."""
    def __init__ (self, r, out,
                  conv=None, 
                  change_units=True,
                  mult=1,
                  imgcount=1,
                  order=['image','attr','ings','text'],
                  attr_order=DEFAULT_OUTPUT_ATTR_ORDER,
                  text_attr_order=DEFAULT_TEXT_ATTR_ORDER,
                  do_markup=True,
                  use_ml=False,
                  convert_attnames=True,
                  fractions=convert.FRACTIONS_ASCII,
                    ):
        """Initiate an exporter class capable of multiplying the recipe.

        We allow the same arguments as the base exporter class plus
        the following

        mult = number (multiply by this number)

        change_units = True|False (whether to change units to keep
        them readable when multiplying).
        """
        self.mult = mult
        self.change_units = change_units
        exporter.__init__(self, r, out, conv, imgcount, order,
                          attr_order=attr_order,
                          text_attr_order=text_attr_order,
                          use_ml=use_ml, do_markup=do_markup,
                          convert_attnames=convert_attnames,
                          fractions=fractions,
                          )

    @pluggable_method
    def write_attr (self, label, text):
        if isinstance(text, Yield):
            text=format(text, "{'fractions': %s}"%self.fractions)
        self.out.write("%s: %s\n"%(label, text))

    @pluggable_method
    def write_ing (self, ingredient=None):
        """Write ingredient."""
        ingstr = format(ingredient, "{'fractions': %s}"%self.fractions)
        if ingstr:
            self.out.write(ingstr)
        self.out.write("\n")

class ExporterMultirec (SuspendableThread, Pluggable):

    name = 'Exporter'

    def __init__ (self, recipes, out, one_file=True,
                  ext='txt',
                  conv=None,
                  imgcount=1,
                  exporter=exporter,
                  exporter_kwargs={},
                  padding=None):
        """Output all recipes in recipes into a document or multiple
        documents. if one_file, then everything is in one
        file. Otherwise, we treat 'out' as a directory and put
        individual recipe files within it."""
        self.timer=TimeAction('exporterMultirec.__init__()')
        self.recipes = recipes
        self.out = out
        self.padding=padding
        self.one_file = one_file
        Pluggable.__init__(self,[BaseExporterMultiRecPlugin])
        SuspendableThread.__init__(self,self.name)
        self.ext = ext
        self.exporter = exporter
        self.exporter_kwargs = exporter_kwargs
        self.fractions = self.exporter_kwargs.get('fractions',
                                                  convert.FRACTIONS_ASCII)
        self.DEFAULT_ENCODING = self.exporter.DEFAULT_ENCODING
        self.one_file = one_file

    def append_referenced_recipes (self):
        for r in self.recipes[:]:
            for i in r.ingredients:
                if i.recipe_ref and not i.recipe_ref in self.recipes:
                    print 'Appending recipe ',rec.title,'referenced in ',r.title
                    self.recipes.append(rec)
        
    @pluggable_method
    def do_run (self):
        self.rcount = 0
        self.rlen = len(self.recipes)        
        if not self.one_file:
            self.outdir=self.out
            if os.path.exists(self.outdir):
                if not os.path.isdir(self.outdir):
                    self.outdir=self.unique_name(self.outdir)
                    os.makedirs(self.outdir)
            else: os.makedirs(self.outdir)
        if self.one_file and type(self.out)==str:
            self.ofi=open(self.out,'wb')
        else: self.ofi = self.out
        self.write_header()
        self.suspended = False
        self.terminated = False
        first = True
        self.append_referenced_recipes()
        for r in self.recipes:
            self.check_for_sleep()
            msg = _("Exported %(number)s of %(total)s recipes")%{'number':self.rcount,'total':self.rlen}
            self.emit('progress',float(self.rcount)/float(self.rlen), msg)
            fn=None
            if not self.one_file:
                fn=self.generate_filename(r,self.ext,add_id=True)
                self.ofi=open(fn,'wb')
            if self.padding and not first:
                self.ofi.write(self.padding)
            e=self.exporter(out=self.ofi, r=r, **self.exporter_kwargs)
            self.connect_subthread(e)
            e.do_run()
            self.recipe_hook(r,fn,e)
            if not self.one_file:
                self.ofi.close()
            self.rcount += 1
            first = False
        self.write_footer()
        if self.one_file:
            self.ofi.close()
        self.timer.end()
        self.emit('progress',1,_("Export complete."))
        print_timer_info()

    @pluggable_method
    def write_header (self):
        pass

    @pluggable_method
    def write_footer (self):
        pass

    def generate_filename (self, rec, ext, add_id=False):
        title=rec.title
        # get rid of potentially confusing characters in the filename
        # Windows doesn't like a number of special characters, so for
        # the time being, we'll just get rid of all non alpha-numeric
        # characters
        ntitle = ""
        for c in title:
            if re.match("[A-Za-z0-9 ]",c):
                ntitle += c
        title = ntitle
        # truncate long filenames
        max_filename_length = 252
        if len(title) > (max_filename_length - 4):
            title = title[0:max_filename_length-4]
        # make sure there is a title
        if not title:
            title = _("Recipe")
        title=title.replace("/"," ")
        title=title.replace("\\"," ")
        # Add ID #
        if add_id:
            title = title + str(rec.id)
        file_w_ext="%s%s%s"%(self.unique_name(title),os.path.extsep,ext)
        return os.path.join(self.outdir,file_w_ext)

    def recipe_hook (self, rec, filename=None, exporter=None):
        """Intended to be subclassed by functions that want a chance
        to act on each recipe, possibly knowing the name of the file
        the rec is going to. This makes it trivial, for example, to build
        an index (written to a file specified in write_header."""
        pass
    
    def unique_name (self, filename):
        if os.path.exists(filename):
            n=1
            fn,ext=os.path.splitext(filename)
            if ext: dot=os.path.extsep
            else: dot=""
            while os.path.exists("%s%s%s%s"%(fn,n,dot,ext)):
                n += 1
            return "%s%s%s%s"%(fn,n,dot,ext)
        else:
            return filename

    def check_for_sleep (self):
        if self.terminated:
            raise Exception("Exporter Terminated!")
        while self.suspended:
            if self.terminated:
                debug('Thread Terminated!',0)
                raise Exception("Exporter Terminated!")
            if use_threads:
                time.sleep(1)
            else:
                time.sleep(0.1)

    def terminate (self):
        self.terminated = True

    def suspend (self):
        self.suspended = True

    def resume (self):
        self.suspended = False
