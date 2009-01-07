import gtk, gobject
from gourmet.gglobals import DEFAULT_ATTR_ORDER, REC_ATTR_DIC
from gourmet.ImageExtras import get_pixbuf_from_jpg
import gourmet.convert as convert
from gourmet.ratingWidget import star_generator
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import func
from gettext import gettext as _

ICON_SIZE=175

def scale_pb (pb):
    w = pb.get_width()
    h = pb.get_height ()
    if w < ICON_SIZE or h < ICON_SIZE:
        if w < h: target = w
        else: target = h
    else:
        target = ICON_SIZE
    if w > h:
        target_w = target
        target_h = int(target * (float(h)/w))
    else:
        target_h = target
        target_w = int(target * (float(w)/h))
    return pb.scale_simple(target_w,target_h,gtk.gdk.INTERP_BILINEAR)

def get_recipe_image (rec):
    pb = scale_pb(get_pixbuf_from_jpg(rec.image))
    if rec.rating:
        #sg = get_star_generator()
        sg = star_generator        
        ratingPB = sg.get_pixbuf(rec.rating)
        print 'Compositing!',rec.title
        h = pb.get_height() - ratingPB.get_height() - 5
        w = pb.get_width() - ratingPB.get_width() - 5
        if h < 0: h = 0
        if w < 0: w = 0
        if ratingPB.props.width > pb.props.width:
            SCALE = float(pb.props.width)/ratingPB.props.width
        else:
            SCALE = 1
        new_pb = ratingPB.composite(
            pb,
            w, #dest_x
            h, # dest_y
            int(ratingPB.get_width()*SCALE), # dest_width,
            int(ratingPB.get_height()*SCALE), #dest_height
            w, #offset_x,
            h, #offset_y
            SCALE,SCALE, #scale_x,scale_y
            gtk.gdk.INTERP_BILINEAR,
            255 # overall_alpha
            )
        return pb
    return pb

class RecipeBrowserView (gtk.IconView):

    __gsignals__ = {
        'recipe-selected':(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_INT,[gobject.TYPE_INT]),
        'path-selected':(gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_STRING,[gobject.TYPE_STRING])
        }

    def __init__ (self, rd):
        self.rd = rd
        gobject.GObject.__init__(self)
        gtk.IconView.__init__(self)
        self.models = {}
        self.set_model()
        self.set_text_column(1)
        self.set_pixbuf_column(2)
        self.connect('item-activated',self.item_activated_cb)
        self.switch_model('base')
        self.path = ['base']

    def new_model (self): return gtk.ListStore(str, # path
                                               str, # text
                                               gtk.gdk.Pixbuf, # image
                                               gobject.TYPE_PYOBJECT,
                                               )

    def switch_model (self, path, val=None):
        if not self.models.has_key(path):
            self.build_model(path,val)
        self.set_model(self.models[path])

    def build_model (self, path,val):
        if path == 'base':
            self.build_base_model()
        elif not '>' in path:
            self.build_first_level_model(path)
        else:
            self.build_recipe_model(path,val)

    def build_base_model (self):
        m = self.models['base'] = self.new_model()
        self.set_model(m)
        for itm in DEFAULT_ATTR_ORDER:
            if itm == 'title': continue
            m.append((itm,(REC_ATTR_DIC[itm]),None,None))

    def get_pixbuf (self, attr,val):
        if attr=='category':            
            tbl = self.rd.recipe_table.join(self.rd.categories_table)
            col = self.rd.categories_table.c.category
            if hasattr(self,'category_images'):
                stment = and_(col==val,self.rd.recipe_table.c.image!=None,
                              self.rd.recipe_table.c.image!='',
                              not_(self.rd.recipe_table.c.title.in_(self.category_images))
                              )
            else:
                stment = and_(col==val,self.rd.recipe_table.c.image!=None,self.rd.recipe_table.c.image!='')
            result = tbl.select(stment,limit=1).execute().fetchone()
            if not hasattr(self,'category_images'): self.category_images = []
            if result: self.category_images.append(result.title)
        elif attr=='rating':
            return star_generator.get_pixbuf(val)
        else:
            tbl = self.rd.recipe_table
            col = getattr(self.rd.recipe_table.c,attr)
            stment = and_(col==val,self.rd.recipe_table.c.image!=None,self.rd.recipe_table.c.image!='')
            result = tbl.select(stment,limit=1).execute().fetchone()
        if result and result.thumb:
            return scale_pb(get_pixbuf_from_jpg(result.image))
        else:
            return None

    def convert_val (self, attr, val):
        if attr in ['preptime','cooktime']:
            if val:
                return convert.seconds_to_timestring(val)
            else:
                return 'None'
        elif attr=='rating':
            if not val: return 'Unrated'
            else:
                val = int(val)
                txt = str(int(val) / 2)
                if val % 2:
                    txt += ' 1/2'
                txt += ' ' + _('Stars')
                return txt
        else:
            return str(val)

    def build_first_level_model (self, attribute):
        m = self.models[attribute] = self.new_model()
        if attribute == 'category':
            for n,val in self.rd.fetch_count(self.rd.categories_table,'category'):
                m.append((attribute+'>'+str(val),str(val)+' (%s)'%n,self.get_pixbuf(attribute,val),val))
        else:
            
                
            for n,val in self.rd.fetch_count(self.rd.recipe_table,attribute):
                if n == 0: continue
                m.append((attribute+'>'+str(val),self.convert_val(attribute,val)+' (%s)'%n,
                          self.get_pixbuf(attribute,val),val))
                          
    def build_recipe_model (self, path, val):
        m = self.models[path] = self.new_model()
        print 'build_recipe_model',path,val
        searches = [{'column':'deleted','operator':'=','search':False}]
        path = path.split('>')
        while path:
            textval = path.pop()
            attr = path.pop()
            if val is None:
                val = None
                searches.append({'column':attr,'search':val,'operator':'='})
            else:
                searches.append({'column':attr,'search':val})
        print 'Search=',searches
        for recipe in self.rd.search_recipes(searches):
            if recipe.image:
                pb = get_recipe_image(recipe)
                m.append((recipe.id,recipe.title,pb,None))
            else:
                m.append((recipe.id,recipe.title,None,None))

    def set_path (self, path):
        self.path = ['base']
        for level in path.split('>'):
            self.path.append(level)
        self.switch_model(path)

    def item_activated_cb (self, iv, path):
        row = self.get_model()[path]
        step = row[0]; val = row[3]
        try:
            rid = int(step)
        except ValueError:
            self.switch_model(step,val)
            self.path.append(step)
            self.emit('path-selected',step)
        else:
            self.emit('recipe-selected',rid)

    def back (self):
        if len(self.path) > 1:
            self.ahead = self.path.pop()
            self.switch_model(self.path[-1])

class RecipeBrowser (gtk.VBox):

    def __init__ (self, rd):
        gtk.VBox.__init__(self)
        self.view = RecipeBrowserView(rd)
        self.buttons = []
        self.button_bar = gtk.HBox()
        self.button_bar.set_spacing(6)
        self.pack_start(self.button_bar,expand=False)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        sw.add(self.view)
        self.pack_start(sw)
        home_button = gtk.Button(stock=gtk.STOCK_HOME)
        self.button_bar.pack_start(home_button,expand=False,fill=False)
        home_button.connect('clicked',self.home); home_button.show()
        self.view.connect('path-selected',self.path_selected_cb)
        self.view.show(); sw.show()

    def home (self, *args):
        self.view.set_path('base')

    def path_selected_cb (self, view, path):
        self.button_bar.show()
        for b in self.buttons: self.button_bar.remove(b)
        so_far = ''
        for step in path.split('>'):
            self.append_button(so_far + step)
            so_far += step + '>'
        
    def append_button (self, path):
        if '>' in path:
            txt = self.view.convert_val(*path.split('>'))
        else:
            txt = path
        self.buttons.append(gtk.Button(txt))
        self.buttons[-1].connect('clicked',lambda *args: self.view.set_path(path))
        self.button_bar.pack_start(self.buttons[-1],expand=False,fill=False)
        self.buttons[-1].show()
        
if __name__ == '__main__':
    import gourmet.recipeManager
    rb = RecipeBrowser(gourmet.recipeManager.get_recipe_manager())
    vb = gtk.VBox()
    vb.pack_start(rb)
    rb.show()
    w = gtk.Window()
    w.add(vb)
    w.show(); vb.show()
    w.set_size_request(800,500)
    w.connect('delete-event',gtk.main_quit)
    gtk.main()
    
