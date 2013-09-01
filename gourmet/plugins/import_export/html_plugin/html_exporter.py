import re, os.path, os, xml.sax.saxutils, time, shutil, urllib, textwrap
from gettext import gettext as _
from gourmet import convert,gglobals
from gourmet.gdebug import *
from gourmet.exporters.exporter import *


HTML_HEADER_START = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
  <head>
  """
HTML_HEADER_CLOSE = """<meta http-equiv="Content-Style-Stype" content="text/css">
     <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
     </head>"""


class html_exporter (exporter_mult):
    def __init__ (self, rd, r, out, conv=None,
                  css=os.path.join(gglobals.style_dir,"default.css"),
                  embed_css=True, start_html=True, end_html=True, imagedir="pics/", imgcount=1,
                  link_generator=None,
                  # exporter_mult args
                  mult=1,
                  change_units=True,
                  ):
        """We export web pages. We have a number of possible options
        here. css is a css file which will be embedded if embed_css is
        true or referenced if not. start_html and end_html specify
        whether or not to write header info (so we can be called in
        the midst of another script writing a page). imgcount allows
        an outside function to keep number exported images, handing
        us the imgcount at the start of our export. link_generator
        will be handed the ID referenced by any recipes called for
        as ingredients. It should return a URL for that recipe
        or None if it can't reference the recipe based on the ID."""
        self.start_html=start_html
        self.end_html=end_html
        self.embed_css=embed_css
        self.css=css
        self.link_generator=link_generator
        if imagedir and imagedir[-1] != os.path.sep: imagedir += os.path.sep #make sure we end w/ slash
        if not imagedir: imagedir = "" #make sure it's a string
        self.imagedir_absolute = os.path.join(os.path.split(out.name)[0],imagedir)
        self.imagedir = imagedir
        exporter_mult.__init__(self, rd, r, out,
                               conv=conv,
                               imgcount=imgcount,
                               mult=mult,
                               change_units=change_units,
                               do_markup=True,
                               use_ml=True)
        
    def htmlify (self, text):
        t=text.strip()
        #t=xml.sax.saxutils.escape(t)
        t="<p>%s</p>"%t
        t=re.sub('\n\n+','</p><p>',t)
        t=re.sub('\n','<br>',t)
        return t

    def write_head (self):
        title = self._grab_attr_(self.r,'title')
        if not title: title = _('Recipe')
        title=xml.sax.saxutils.escape(title)
        if self.start_html:
            self.out.write(HTML_HEADER_START)
            self.out.write("<title>%s</title>"%title)
            if self.css:
                if self.embed_css:
                    self.out.write("<style type='text/css'><!--\n")
                    f=open(self.css,'r')
                    for l in f.readlines():
                        self.out.write(l)
                    f.close()
                    self.out.write("--></style>")
                else:
                    self.out.write("<link rel='stylesheet' href='%s' type='text/css'>"%self.make_relative_link(self.css))
            self.out.write(HTML_HEADER_CLOSE)
            self.out.write('<body>')
        self.out.write('<div class="recipe" itemscope itemtype="http://schema.org/Recipe">')
        
    def write_image (self, image):
        imgout = os.path.join(self.imagedir_absolute,"%s.jpg"%self.imgcount)
        while os.path.isfile(imgout):
            self.imgcount += 1
            imgout = os.path.join(self.imagedir_absolute,"%s.jpg"%self.imgcount)
        if not os.path.isdir(self.imagedir_absolute):
            os.mkdir(self.imagedir_absolute)
        o = gglobals.open(imgout,'wb')
        o.write(image)
        o.close()
        # we use urllib here because os.path may fsck up slashes for urls.
        self.out.write('<img src="%s" itemprop="image">'%self.make_relative_link("%s%s.jpg"%(self.imagedir,
                                                                            self.imgcount)
                                                                )
                       )
        self.images.append(imgout)
        
    def write_inghead (self):
        self.out.write('<div class="ing"><h3>%s</h3><ul class="ing">'%_('Ingredients'))

    def write_text (self, label, text):
        attr = gglobals.NAME_TO_ATTR.get(label,label)
        if attr == 'instructions':
            self.out.write('<div class="%s"><h3 class="%s">%s</h3><div itemprop="recipeInstructions">%s</div></div>' % (attr,label,label,self.htmlify(text)))
        else:
            self.out.write('<div class="%s"><h3 class="%s">%s</h3>%s</div>' % (attr,label,label,self.htmlify(text)))

    def handle_italic (self, chunk): return "<em>" + chunk + "</em>"
    def handle_bold (self, chunk): return "<strong>" + chunk + "</strong>"
    def handle_underline (self, chunk): return "<u>" + chunk + "</u>"

    def write_attr_head (self):
        self.out.write("<div class='header'>")

    def write_attr (self, label, text):
        attr = gglobals.NAME_TO_ATTR.get(label,label)
        if attr=='link':
            webpage = text.strip('http://')
            webpage = webpage.split('/')[0]
            self.out.write('<a href="%s">'%text +
                           _('Original Page from %s')%webpage +
                           '</a>\n')
        elif attr == 'rating':
            rating, rest = text.split('/', 1)
            self.out.write('<p class="%s" itemprop="aggregateRating" itemscope itemtype="http://schema.org/AggregateRating"><span class="label">%s:</span> <span itemprop="ratingValue">%s</span><span>/%s</span></p>\n' % (attr, label.capitalize(), rating, rest))
        else:
            itemprop = None
            if attr == 'title':
                itemprop = 'name'
            elif attr == 'category':
                itemprop = 'recipeCategory'
            elif attr == 'cuisine':
                itemprop = 'recipeCuisine'
            elif attr == 'yields':
                itemprop = 'recipeYield'
            elif attr == 'preptime':
                itemprop = 'prepTime'
            elif attr == 'cooktime':
                itemprop = 'cookTime'
            elif attr == 'instructions':
                itemprop = 'recipeInstructions'
            if itemprop:
                self.out.write('<p class="%s"><span class="label">%s:</span> <span itemprop="%s">%s</span></p>\n' % (attr, label.capitalize(), itemprop, xml.sax.saxutils.escape(text)))
            else:
                self.out.write("<p class='%s'><span class='label'>%s:</span> %s</p>\n"%(attr, label.capitalize(), xml.sax.saxutils.escape(text)))
        
    def write_attr_foot (self):
        self.out.write("</div>")
    
    def write_grouphead (self, name):
        self.out.write("<li class='inggroup'>%s:<ul class='ing'>"%name)

    def write_groupfoot (self):
        self.out.write("</ul></li>")
                            
    def write_ingref (self, amount, unit, item, refid, optional):
        link=False
        if self.link_generator:
            link=self.link_generator(refid)
            if link:
                self.out.write("<a href='")
                self.out.write(
                    self.make_relative_link(link)
                    #xml.sax.saxutils.escape(link).replace(" ","%20")
                    #self.make_relative_link(link)
                    )
                self.out.write("'>")
        self.write_ing (amount, unit, item, optional=optional)
        if link: self.out.write("</a>")

    def write_ing (self, amount=1, unit=None,
                   item=None, key=None, optional=False):
        self.out.write('<li class="ing" itemprop="ingredients">')
        for o in [amount, unit, item]:
            if o: self.out.write(xml.sax.saxutils.escape("%s "%o))
        if optional:
            self.out.write("(%s)"%_('optional'))
        self.out.write("</li>\n")
    
    def write_ingfoot (self):
        self.out.write('</ul>\n</div>\n')

    def write_foot (self):
        self.out.write("</div>\n")
        if self.end_html:
            self.out.write('\n</body>\n</html>')

    def make_relative_link (self, filename):
        try:
            outdir = os.path.split(self.out.name)[0] + os.path.sep
            if filename.find(outdir)==0:
                filename=filename[len(outdir):]
        except:
            pass
        return linkify(filename)

class website_exporter (ExporterMultirec):
    def __init__ (self, rd, recipe_table, out, conv=None, ext='htm', copy_css=True,
                  css=os.path.join(gglobals.style_dir,'default.css'),
                  imagedir='pics' + os.path.sep,
                  index_rows=['title','category','cuisine','rating','yields'],
                  progress_func=None,
                  change_units=False,
                  mult=1):
        self.ext=ext
        self.css=css
        self.embed_css = False
        if copy_css:
            styleout = os.path.join(out,'style.css')
            if not os.path.isdir(out):
                gglobals.makedirs(out)
            to_copy = gglobals.open(self.css,'r')
            print 'writing css to ',styleout
            to_paste = gglobals.open(styleout,'w')
            to_paste.write(to_copy.read())
            to_copy.close(); to_paste.close()
            self.css = styleout
        self.imagedir=imagedir
        self.index_rows=index_rows
        self.imgcount=1
        self.added_dict={}
        self.exportargs={'embed_css': False,
                          'css': self.css,
                          'imgcount': self.imgcount,
                         'imagedir':self.imagedir,
                         'link_generator': self.generate_link,
                         'change_units':change_units,
                         'mult':mult}
        if conv:
            self.exportargs['conv']=conv
        ExporterMultirec.__init__(self, rd, recipe_table, out,
                                  one_file=False,
                                  ext=self.ext,
                                  progress_func=progress_func,
                                  exporter=html_exporter,
                                  exporter_kwargs=self.exportargs)
        
    def write_header (self):
        self.indexfn = os.path.join(self.outdir,'index%s%s'%(os.path.extsep,self.ext))
        self.indexf = gglobals.open(self.indexfn,'w')
        self.indexf.write(HTML_HEADER_START)
        self.indexf.write("<title>Recipe Index</title>")
        if self.embed_css:
            self.indexf.write("<style type='text/css'><!--\n")
            f=open(self.css,'r')
            for l in f.readlines():
                self.indexf.write(l)
            f.close()
            self.indexf.write("--></style>")
        else:
            self.indexf.write("<link rel='stylesheet' href='%s' type='text/css'>"%self.make_relative_link(self.css))
        self.indexf.write(HTML_HEADER_CLOSE)
        self.indexf.write('<body>')
        self.indexf.write('<div class="index"><table class="index">\n<tr>')
        for r in self.index_rows:
            self.indexf.write('<th class="%s">%s</th>'%(r,REC_ATTR_DIC[r]))
        self.indexf.write('</tr>\n')    

    def recipe_hook (self, rec, filename, exporter):
        """Add index entry"""
        # we link from the first row
        
        self.indexf.write(
            """<tr><td class="%s">
                     <a href="%s">%s</a>
                   </td>"""%(self.index_rows[0],
                             #xml.sax.saxutils.escape(filename).replace(" ","%20"),
                             self.make_relative_link(filename),
                             xml.sax.saxutils.escape(self._grab_attr_(rec,self.index_rows[0]))
                             ))
        for r in self.index_rows[1:]:
            self.indexf.write('<td class="%s">%s</td>'%(r,self._grab_attr_(rec,r)))
        self.indexf.write('</tr>')
        self.imgcount=exporter.imgcount
        self.added_dict[rec.id]=filename

    def write_footer (self):
        self.indexf.write('</table></div></body></html>')
        self.indexf.close()

    def generate_link (self, id):
        if self.added_dict.has_key(id):
            return self.added_dict[id]
        else:
            rec = self.rd.get_rec(id)
            if rec:
                return self.generate_filename(rec,self.ext,add_id=True)
            else:
                return None

    def make_relative_link (self, filename):
        if self.outdir[-1] != os.path.sep:
            outdir = self.outdir + os.path.sep
        else: outdir = self.outdir
        if filename.find(outdir)==0:
            filename=filename[len(outdir):]
        return linkify(filename)

def linkify (filename):
    ret = filename.replace('\\','/')
    ret = filename.replace(' ','%20')
    return xml.sax.saxutils.escape(filename)
    
