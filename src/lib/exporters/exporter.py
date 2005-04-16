import re, Image, os.path, os, xml.sax.saxutils, time, shutil, urllib, textwrap
from gourmet import gglobals, convert
from gourmet.gdebug import *
from gettext import gettext as _

REC_ATTR_DIC={}
for attr,titl,widget in gglobals.REC_ATTRS:
    REC_ATTR_DIC[attr]=titl

class exporter:

    """Base class for all exporters.  Subclasses must implement basic write methods,
    which are handed attributes, text blobs, images, etc. and then expected to write
    them appropriately."""

#new variable contained here called attr_order
#This is so we can control the order the attributes are in
#Some exporter subclasses might care (like mealmaster)
    def __init__ (self, rd, r, out,
                  conv=None,
                  imgcount=1,
                  order=['image','attr','text','ings'],
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
                  ):
        """A base exporter class to be subclassed (or to be
        called for plain text export).

        do_markup: if True, we handle markup parsing internally, using
        the functions handle_italic, handle_bold and
        handle_underline. If not, marked up pango text (with <u>, <b>,
        and <i> is written to our exported directly.

        If use_ml is True, we leave pango-ified text properly escaped.
        if use_ml is False, we unescape pango text &amp;->&, etc.
        """
        tt = TimeAction('exporter.__init__()',0)
	self.attr_order=attr_order
        self.out = out
        self.r = r
        self.rd=rd
        self.do_markup=do_markup
        self.use_ml=use_ml
        if not conv: conv=convert.converter()
        self.conv=conv
        self.imgcount=imgcount
        self.write_head()
        self.images = []
        for task in order:
            t=TimeAction('exporter._write_attrs()',4)
            if task=='image':
                if self.grab_attr(self.r,'image'):
                    self.write_image(self.r.image)
            if task=='attr':
                self._write_attrs()
                t.end()
                t=TimeAction('exporter._write_text()',4)
            elif task=='text':
                self._write_text()
                t.end()
                t=TimeAction('exporter._write_ings()',4)            
            elif task=='ings': self._write_ings()
            t.end()
        self.write_foot()
        tt.end()
        
    def _write_attrs (self):        
        self.write_attr_head()
        for a in self.attr_order:
            gglobals.gt.gtk_update()
            txt=self.grab_attr(self.r,a)
            if txt and txt.strip():
                if (a=='preptime' or a=='cooktime') and a.find("0 ")==0: pass
                else: self.write_attr(REC_ATTR_DIC[a],txt)
        self.write_attr_foot()

    def _write_text (self):
        for a in ['instructions','modifications']:
            txt=self.grab_attr(self.r,a)
            if txt and txt.strip():
                if self.do_markup: txt=self.handle_markup(txt)
                if not self.use_ml: txt = xml.sax.saxutils.unescape(txt)
                self.write_text(a.capitalize(),txt)

    def _write_ings (self):
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
                amount=self.grab_attr(i,'amount')
                if amount: amount=convert.float_to_frac(amount)
                if self.grab_attr(i,'refid'):
                    self.write_ingref(amount=amount,
                                      unit=self.grab_attr(i,'unit'),
                                      item=self.grab_attr(i,'item'),
                                      refid=self.grab_attr(i,'refid'),
                                      optional=self.grab_attr(i,'optional')
                                      )
                else:
                    self.write_ing(amount=amount,
                                   unit=self.grab_attr(i,'unit'),
                                   item=self.grab_attr(i,'item'),
                                   key=self.grab_attr(i,'ingkey'),
                                   optional=self.grab_attr(i,'optional')
                                   )
            if g:
                self.write_groupfoot()
        self.write_ingfoot()


    def write_image (self, image):
        pass
    
    def grab_attr (self, obj, attr):
        try:
            return getattr(obj,attr)
        except:
            return None

    def write_head (self):
        pass

    def write_foot (self):
        pass

    def write_inghead(self):
        self.out.write("\n---\n%s\n---\n"%_("Ingredients"))

    def write_ingfoot(self):
        pass

    def write_attr_head (self):
        pass
    
    def write_attr_foot (self):
        pass

    def write_attr (self, label, text):
        self.out.write("%s: %s\n"%(label, text.strip()))

    def write_text (self, label, text):
        self.out.write("\n---\n%s\n---\n"%label)
        ll=text.split("\n")
        for l in ll:
            for wrapped_line in textwrap.wrap(l):
                self.out.write("\n%s"%wrapped_line)
        self.out.write('\n\n')

    def handle_markup (self, txt):
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

    def handle_italic (self,chunk): return "*"+chunk+"*"
    def handle_bold (self,chunk): return chunk.upper()
    def handle_underline (self,chunk): return "_" + chunk + "_"

    def write_grouphead (self, text):
        """The start of group of ingredients named TEXT"""
        self.out.write("\n%s:\n"%text.strip())

    def write_groupfoot (self):
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
    """An exporter subclass that allows multiplying of the exported recipe."""
    def __init__ (self, rd, r, out, conv=None,
                  mult=1, imgcount=1, order=['attr','text','ings'],
                  change_units=True, use_ml=False, do_markup=True):        
        self.mult = mult
        self.change_units = change_units
        exporter.__init__(self, rd, r, out, conv, imgcount, order, use_ml=use_ml, do_markup=do_markup)

    def write_attr (self, label, text):
        attr = gglobals.NAME_TO_ATTR[label]
        if attr=='servings':
            num = convert.frac_to_float(text) * self.mult
            if num:
                text = convert.float_to_frac(num)
        self.out.write("%s: %s\n"%(label, text))

    def multiply_amount (self, amount, unit):
        if self.mult==1 or not amount:
            return amount,unit
        amt = convert.frac_to_float(amount) * self.mult
        if self.change_units:
            amt,unit = self.conv.adjust_unit(amt,unit)
            return convert.float_to_frac(amt),unit
        else:
            return convert.float_to_frac(amt),unit
        
    def write_ing (self, amount=1, unit=None, item=None, key=None, optional=False):
        amount,unit = self.multiply_amount(amount,unit)
        if amount:
            self.out.write("%s"%amount)
        if unit:
            self.out.write(" %s"%unit)
        if item:
            self.out.write(" %s"%item)
        if optional:
            self.out.write(" (%s)"%_("optional"))
        self.out.write("\n")        
            

class mealmaster_exporter (exporter):
    def __init__ (self, rd, r, out, conv=None):
        import mealmaster_importer
        self.conv = conv
        mmf2mk =mealmaster_importer.mmf_constants()
        uc_orig=mmf2mk.unit_conv
        self.uc={}
        for k,v in uc_orig.items():
            self.uc[v]=k
        recattrs_orig=mmf2mk.recattrs
        self.recattrs={}
        for k,v in recattrs_orig.items():
            self.recattrs[v]=k
        self.categories = ""
        exporter.__init__(self, rd, r, out, conv,
                          order=['attr','ings','text'])

    def write_head (self):
        self.out.write("MMMMM----- Recipe via Meal-Master (tm)\n\n")

    def write_attr (self, label, text):
        #We must be getting the label already capitalized from an the exporter class
	#this line is just to correct that without making a mess of the exporter class
	label=label.lower()
	if label=='category' or label=='cuisine':
            if self.categories:
                self.categories="%s, %s"%(self.categories,text)
            else:
                self.categories=text
            self.out.write("%s: %s\n"%(self.pad("Categories",12),self.categories))
	#Mealmaster pukes at the preptime line so this removes it    
	elif label=='preparation time' or label=='rating' or label=='source':
	    pass
	else:
            if label and text:
                if self.recattrs.has_key(label):
                    label=self.recattrs[label]
                else:
                    label=label.capitalize()
                label=self.pad(label,12)
		self.out.write("%s: %s\n"%(label, text))

    def write_attr_foot (self):
        #Removed by rsborn as part of the MM export fix
	#self.out.write("%s: %s\n\n"%(self.pad("Categories",12),self.categories))
	pass

    def pad (self, text, chars):
        text=text.strip()
        fill = chars - len(text)
        return "%s%s"%(" "*fill,text)
    
    def write_text (self, label, text):
        ll=text.split("\n")
        for l in ll:
            for wrapped_line in textwrap.wrap(l):
                self.out.write("\n  %s"%wrapped_line)
            
    def write_inghead (self):
        self.master_ings=[] # our big list
        # self.ings is what we add to
        # this can change when we add groups
        self.ings = self.master_ings
        self.ulen=1
        # since the specs we found suggest it takes 7 blanks
        # to define an ingredient, our amtlen needs to be at
        # least 6 (there will be an extra space added
        self.amtlen=6
        self.out.write("\n")

    def write_grouphead (self, name):
        debug('write_grouphead called with %s'%name,0)
        group = (name, [])
        self.ings.append(group) # add to our master
        self.ings = group[1] # change current list to group list

    def write_groupfoot (self):
        self.ings = self.master_ings # back to master level

    def write_ing (self, amount="1", unit=None, item=None, key=None, optional=False):
        if type(amount)==type(1.0) or type(amount)==type(1):
  	    amount = convert.float_to_frac(amount)
  	if not amount: amount = ""        
        if self.conv.unit_dict.has_key(unit) and self.uc.has_key(self.conv.unit_dict[unit]):
            unit=self.uc[self.conv.unit_dict[unit]] or ""
        elif unit:
            # if we don't recognize the unit, we add it to
            # the item
            item="%s %s"%(unit,item)
            unit=""
        if len(unit)>self.ulen:
            self.ulen=len(unit)
        if len(amount)>self.amtlen:
            self.amtlen=len(amount)
            #print "DEBUG: %s length %s"%(amount,self.amtlen)
        # we hold off writing ings until we know the lengths
        # of strings since we need to write out neat columns
        if optional: item="%s (optional)"%item
        self.ings.append([amount,unit,item])

    def write_ingfoot (self):
        """Write all of the ingredients"""
        ## where we actually write the ingredients...
        for i in self.master_ings:
            # if we're a tuple, this is a group...
            if type(i)==type(()):
                # write the group title first...
                group = i[0]
                width = 70
                dashes = width - len(group)
                left_side = dashes/2 - 5
                right_side = dashes/2
                self.out.write("-----%s%s%s\n"%(left_side * "-",
                                           group.upper(),
                                           right_side * "-")
                          )
                map(self._write_ingredient,i[1])
                self.out.write("\n") # extra newline at end of groups
            else:
                self._write_ingredient(i)
        # we finish with an extra newline
        self.out.write("\n")
                        
    def _write_ingredient (self, ing):
        a,u,i = ing
        self.out.write("%s %s %s\n"%(self.pad(a,self.amtlen),
                                     self.pad(u,self.ulen),
                                     i))

    def write_foot (self):
        self.out.write("\n\n")
	self.out.write("MMMMM")
	self.out.write("\n\n")
    

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
            self.ofi=open(out,'w')
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
                self.ofi=open(fn,'w')
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
