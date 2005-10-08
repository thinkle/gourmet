import re, Image, os.path, os, xml.sax.saxutils, time, shutil, urllib, textwrap
from gourmet import gglobals, convert
from gourmet.gdebug import *
from gettext import gettext as _

REC_ATTR_DIC = gglobals.REC_ATTR_DIC

class exporter:
    """A base exporter class.

    All Gourmet exporters should subclass this class or one of its
    derivatives.

    This class can also be used directly for plain text export.
    """
    DEFAULT_ENCODING = 'utf-8'

    def __init__ (self, rd, r, out,
                  conv=None,
                  imgcount=1,
                  order=['image','attr','ings','text'],
		  attr_order=['title',
                              'category',
                              'cuisine',
                              'servings',
                              'source',
                              'rating',
                              'preptime',
                              'cooktime'],
                  text_attr_order = ['instructions',
                                     'modifications'],
                  do_markup=True,
                  use_ml=False,
                  convert_attnames=True,
                  fractions=convert.FRACTIONS_ASCII
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
	self.attr_order=attr_order
        self.text_attr_order = text_attr_order
        self.out = out
        self.r = r
        self.rd=rd
        self.do_markup=do_markup
        self.fractions=fractions
        self.use_ml=use_ml
        self.convert_attnames = convert_attnames
        if not conv: conv=convert.converter()
        self.conv=conv
        self.imgcount=imgcount
        self.write_head()
        self.images = []
        for task in order:
            t=TimeAction('exporter._write_attrs_()',4)
            if task=='image':
                if self._grab_attr_(self.r,'image'):
                    self.write_image(self.r.image)
            if task=='attr':
                self._write_attrs_()
                t.end()
                t=TimeAction('exporter._write_text_()',4)
            elif task=='text':
                self._write_text_()
                t.end()
                t=TimeAction('exporter._write_ings_()',4)            
            elif task=='ings': self._write_ings_()
            t.end()
        self.write_foot()
        tt.end()

    # Internal methods -- ideally, subclasses should have no reason to
    # override any of these methods.
        
    def _write_attrs_ (self):        
        self.write_attr_head()
        for a in self.attr_order:
            gglobals.gt.gtk_update()
            txt=self._grab_attr_(self.r,a)
            if txt and txt.strip():
                if (a=='preptime' or a=='cooktime') and a.find("0 ")==0: pass
                else:
                    if self.convert_attnames:
                        self.write_attr(REC_ATTR_DIC[a],txt)
                    else:
                        self.write_attr(a,txt)
        self.write_attr_foot()

    def _write_text_ (self):
        for a in self.text_attr_order:
            txt=self._grab_attr_(self.r,a)
            if txt and txt.strip():
                if self.do_markup: txt=self.handle_markup(txt)
                if not self.use_ml: txt = xml.sax.saxutils.unescape(txt)
                if self.convert_attnames:
                    self.write_text(gglobals.TEXT_ATTR_DIC[a],txt)
                else:
                    self.write_text(a,txt)

    def _write_ings_ (self):
        """Write all of our ingredients.
        """
        ingredients = self.rd.get_ings(self.r)
        if not ingredients:
            return
        gglobals.gt.gtk_update()
        self.write_inghead()
        for g,ings in self.rd.order_ings(ingredients):
            gglobals.gt.gtk_update()
            if g:
                self.write_grouphead(g)            
            for i in ings:
                amount,unit = self._get_amount_and_unit_(i)
                if self._grab_attr_(i,'refid'):
                    self.write_ingref(amount=amount,
                                      unit=unit,
                                      item=self._grab_attr_(i,'item'),
                                      refid=self._grab_attr_(i,'refid'),
                                      optional=self._grab_attr_(i,'optional')
                                      )
                else:
                    self.write_ing(amount=amount,
                                   unit=unit,
                                   item=self._grab_attr_(i,'item'),
                                   key=self._grab_attr_(i,'ingkey'),
                                   optional=self._grab_attr_(i,'optional')
                                   )
            if g:
                self.write_groupfoot()
        self.write_ingfoot()

    def _grab_attr_ (self, obj, attr):
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
                    ret = convert.seconds_to_timestring(ret,fractions=self.fractions)
            elif attr=='rating' and ret and type(ret)!=str:
                if ret/2==ret/2.0:
                    ret = "%s/5 %s"%(ret/2,_('stars'))
                else:
                    ret = "%s/5 %s"%(ret/2.0,_('stars'))
            if type(ret) in [str,unicode] and attr not in ['thumb','image']:
                try:
                    ret = ret.encode(self.DEFAULT_ENCODING)
                except:
                    print "wtf:",ret,"doesn't look like unicode."
                    raise
            return ret

    def _get_amount_and_unit_ (self, ing):
        return self.rd.get_amount_and_unit(ing,fractions=self.fractions)

    # Below are the images inherited exporters should subclass.

    def write_image (self, image):
        """Write image based on binary data for an image file (jpeg format)."""
        pass


    def write_head (self):
        """Write any necessary header material at recipe start."""
        pass

    def write_foot (self):
        """Write any necessary footer material at recipe end."""
        pass

    def write_inghead(self):
        """Write any necessary markup before ingredients."""
        self.out.write("\n---\n%s\n---\n"%_("Ingredients"))

    def write_ingfoot(self):
        """Write any necessary markup after ingredients."""
        pass

    def write_attr_head (self):
        """Write any necessary markup before attributes."""
        pass
    
    def write_attr_foot (self):
        """Write any necessary markup after attributes."""
        pass

    def write_attr (self, label, text):
        """Write an attribute with label and text.

        If we've been initialized with convert_attnames=True, the
        label will already be translated to our current
        locale. Otherwise, the label will be the same as it used
        internally in our database.

        So if your method needs to do something special based on the
        attribute name, we need to set convert_attnames to False (and
        do any necessary i18n of the label name ourselves.
        """
        self.out.write("%s: %s\n"%(label, text.strip()))

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
            fields=fd.get_set_fields()
            if fields != 0: #if there are fields
                if 'style' in fields.value_nicks and fd.get_style()==pango.STYLE_ITALIC:
                    chunk=self.handle_italic(chunk)
                if 'weight' in fields.value_nicks and fd.get_weight()==pango.WEIGHT_BOLD:
                    chunk=self.handle_bold(chunk)
            for att in atts:
                if att.type==pango.ATTR_UNDERLINE and att.value==pango.UNDERLINE_SINGLE:
                    chunk=self.handle_underline(chunk)
            outtxt += chunk
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

    def write_grouphead (self, text):
        """The start of group of ingredients named TEXT"""
        self.out.write("\n%s:\n"%text.strip())

    def write_groupfoot (self):
        """Mark the end of a group of ingredients.
        """
        pass
    
    def write_ingref (self, amount=1, unit=None,
                      item=None, optional=False,
                      refid=None):
        """By default, we don't handle ingredients as recipes, but
        someone subclassing us may wish to do so..."""
        self.write_ing(amount=amount,
                       unit=unit, item=item,
                       key=None, optional=optional)

    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        """Write ingredient."""
        if amount:
            self.out.write("%s"%amount)
        if unit:
            self.out.write(" %s"%unit)
        if item:
            self.out.write(" %s"%item)
        if optional:
            self.out.write(" (%s)"%_("optional"))
        self.out.write("\n")

class exporter_mult (exporter):
    """A basic exporter class that can handle a multiplied recipe."""
    def __init__ (self, rd, r, out,
                  conv=None, 
                  change_units=True,
                  mult=1,
                  imgcount=1,
                  order=['image','attr','ings','text'],
                  attr_order=['title',
                              'category',
                              'cuisine',
                              'servings',
                              'source',
                              'rating',
                              'preptime',
                              'cooktime'],
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
        exporter.__init__(self, rd, r, out, conv, imgcount, order, use_ml=use_ml, do_markup=do_markup,
                          fractions=fractions)

    def write_attr (self, label, text):
        #attr = gglobals.NAME_TO_ATTR[label]
        self.out.write("%s: %s\n"%(label, text))

    def _grab_attr_ (self, obj, attr):
        """Grab attribute attr of obj obj.

        Possibly manipulate the attribute we get to hand out export
        something readable.
        """
        ret = getattr(obj,attr)
        if attr=='servings' and self.mult:
            fl_ret = convert.frac_to_float(ret)
            if fl_ret:
                return convert.float_to_frac(fl_ret * self.mult,
                                             fractions=self.fractions)
        else:
            return exporter._grab_attr_(self,obj,attr)

    def get_amount_and_unit (self, ing):
         if self.mult != 1 and self.change_units:
             return self.rd.get_amount_and_unit(ing,mult=self.mult,conv=self.conv,
                                                fractions=self.fractions)
         else:
             return self.rd.get_amount_and_unit(ing,mult=self.mult,


    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        if amount:
            self.out.write("%s"%amount)
        if unit:
            self.out.write(" %s"%unit)
        if item:
            self.out.write(" %s"%item)
        if optional:
            self.out.write(" (%s)"%_("optional"))
        self.out.write("\n")        

class ExporterMultirec:
    def __init__ (self, rd, rview, out, one_file=True,
                  ext='txt',
                  conv=None,
                  imgcount=1,
                  progress_func=None,
                  exporter=exporter,
                  exporter_kwargs={},
                  padding=None):
        """Output all recipes in rview into a document or multiple
        documents. if one_file, then everything is in one
        file. Otherwise, we treat 'out' as a directory and put
        individual recipe files within it."""        
        self.timer=TimeAction('exporterMultirec.__init__()')
        self.rd = rd
        self.rview = rview
        self.out = out
        self.padding=padding
        if not one_file:
            self.outdir=out
            if os.path.exists(self.outdir):
                if not os.path.isdir(self.outdir):
                    self.outdir=self.unique_name(self.outdir)
                    os.makedirs(self.outdir)
            else: os.makedirs(self.outdir)
        if one_file and type(out)==str:
            self.ofi=open(out,'wb')
        else: self.ofi = out
        self.write_header()
        self.rcount = 0
        self.rlen = len(self.rview)
        self.suspended = False
        self.terminated = False
        self.pf = progress_func
        self.ext = ext
        self.exporter = exporter
        self.exporter_kwargs = exporter_kwargs
        self.one_file = one_file
        self.rd = rd
        
    def run (self):
        first = True
        for r in self.rview:
            self.check_for_sleep()
            if self.pf:
                msg = _("Exported %(number)s of %(total)s recipes")%{'number':self.rcount,'total':self.rlen}
                self.pf(float(self.rcount)/float(self.rlen), msg)
            fn=None
            if not self.one_file:
                fn=self.generate_filename(r,self.ext)
                self.ofi=open(fn,'wb')
            if self.padding and not first:
                self.ofi.write(self.padding)
            e=self.exporter(out=self.ofi, r=r, rd=self.rd, **self.exporter_kwargs)
            self.recipe_hook(r,fn,e)
            if not self.one_file:
                self.ofi.close()
            self.rcount += 1
            first = False
        self.write_footer()
        if self.one_file:
            self.ofi.close()
        self.timer.end()
        if self.pf: self.pf(1,_("Export complete."))
        print_timer_info()

    def write_header (self):
        pass

    def write_footer (self):
        pass

    def generate_filename (self, rec, ext):
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
        max_filename_length = 255
        if len(title) > (max_filename_length - 4):
            title = title[0:max_filename_length-4]
        # make sure there is a title
        if not title:
            title = _("Recipe")
        title=title.replace("/"," ")
        title=title.replace("\\"," ")
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
        gglobals.gt.gtk_update()
        if self.terminated:
            raise "Exporter Terminated!"
        while self.suspended:
            gglobals.gt.gtk_update()
            if self.terminated:
                debug('Thread Terminated!',0)
                raise "Exporter Terminated!"
            if gglobals.use_threads:
                time.sleep(1)
            else:
                time.sleep(0.1)

    def terminate (self):
        self.terminated = True

    def suspend (self):
        self.suspended = True

    def resume (self):
        self.suspended = False
