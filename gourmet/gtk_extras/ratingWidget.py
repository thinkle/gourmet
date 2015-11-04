import gtk, gtk.gdk
import gobject
import gourmet.gglobals as gglobals
import os.path
from gettext import gettext as _
import tempfile

try:
    from PIL import Image
except ImportError:
    import Image

PLUS_ONE_KEYS = ['plus',
                 'greater',
                 #'Up',
                 #'Right',
                 ]
MINUS_ONE_KEYS = ['minus',
                  'less',
                  #'Down',
                  #'Left'
                  ]
PLUS_MAX_KEYS = ['Page_Up']
MINUS_MAX_KEYS = ['Page_Down']
ACTIVATE_KEYS = ['space']

# An implement a star box for rating something (as in 1 to 5 stars) a
# la rhythmbox


# StarGenerator handles efficient creation/fetching of Pixbufs for various
# numbers of stars

class StarGenerator:

    """A convenient class that will give us a gtk.Pixbuf representing stars
    for any number.

    set_image and unset_image must have the same width!""" 

    def __init__ (self,
                    set_image=os.path.join(gglobals.imagedir,'gold_star.png'),
                    unset_image=os.path.join(gglobals.imagedir,'no_star.png'),
                    half_image=os.path.join(gglobals.imagedir,'half_gold_star.png'),
                    #background=(0,0,0,0),
                    background=0,
                    size=None,
                    ):
        self.set_img   = Image.open(set_image)
        if size:
            self.set_img = self.set_img.resize(size)
        self.unset_img = Image.open(unset_image).resize(self.set_img.size)
        self.halfset_img = Image.open(half_image).resize(self.set_img.size)
        #convert to RGBA self.set_img = self.set_img.convert('RGBA')
        self.set_img = self.set_img.convert('RGBA')
        self.unset_img = self.unset_img.convert('RGBA')
        self.halfset_img = self.halfset_img.convert('RGBA')
        self.width,self.height = self.set_img.size
        self.set_region = self.set_img.crop((0,0,
                                             self.width,
                                             self.height))
        self.unset_region = self.unset_img.crop((0,0,
                                             self.width,
                                             self.height))
        self.halfset_region = self.halfset_img.crop((0,0,
                                                     self.width,
                                                     self.height))
        self.background = background
        self.pixbufs = {}
        self.image_files = {}

    def get_pixbuf (self,n,max=10):

        """Return a pixbuf with an image representing n/max stars"""

        if self.pixbufs.has_key((n,max)):
            return self.pixbufs[(n,max)]
        else:
            img = self.build_image(n,max)
            pb=self.get_pixbuf_from_image(img)
            self.pixbufs[(n,max)]=pb
            return pb

    def get_full_width (self, max=10):
        return self.width*max/2

    def get_image (self, *args, **kwargs):
        """Get an Image (PIL) object representing n/max stars
        """
        # Just an alias for semantic clarity...
        return self.build_image(*args,**kwargs)

    def get_file (self, n, max=10, ext='.jpg'):
        if (self.image_files.has_key((n,max,ext))
            and
            os.path.exists(self.image_files[(n,max,ext)])
            ):
            return self.image_files[(n,max,ext)]
        fi = tempfile.mktemp("%s_of_%s.%s"%(n,max,ext))
        i = self.get_image(n,max)
        i = i.convert('RGB')
        i.save(fi)
        self.image_files[(n,max,ext)]=fi
        return fi
        
    def build_image (self, n, max=10):
        """Build an image representing n/max stars."""
        img=Image.new('RGBA',
                      (self.get_full_width(max),
                       self.height),
                      self.background)
        for i in range(0,(max/2)):
            if i*2+2 <= n:
                to_paste = self.set_region
            elif (i*2)+1 <= n:
                to_paste = self.halfset_region
            else:
                to_paste = self.unset_region
            xbase = self.width*i
            img.paste(to_paste,
                (xbase,
                 0,
                 xbase+self.width,
                 self.height))
        return img

    def get_pixbuf_from_image (self, image, make_white_opaque=True):

        """Get a pixbuf from a PIL Image.

        By default, turn all white pixels transparent.
        """

        is_rgba = image.mode=='RGBA'
        if is_rgba: rowstride = 4
        else: rowstride = 3
        pb=gtk.gdk.pixbuf_new_from_data(
            image.tobytes(),
            gtk.gdk.COLORSPACE_RGB,
            is_rgba,
            8,
            image.size[0],
            image.size[1],
            (is_rgba and 4 or 3) * image.size[0] #rowstride
            )
        return pb
    
star_generator = StarGenerator()

# StarImage is a class that allows easy setting of an image from a value.

class StarImage (gtk.Image):
    __gtype_name__ = 'StarImage'

    def __init__ (self,
                  star_gen=star_generator,
                  value=0,
                  upper=10):
        """Create an Image widget with value/upper stars filled in.

        star_gen is an instance of the StarGenerator class which will do
        the work of creating the Pixbufs with the star images.

        The number can be changed via the get_value and set_value methods.

        If you want the user to be able to change the number of stars,
        use a StarButton.
        """
        gtk.Image.__init__(self)
        self.stars = star_gen
        self.upper = upper
        self.set_value(value)
        
    def set_value (self, value):

        """Set value. Silently floor value at 0 and cap it at self.upper"""

        if value > self.upper: value = self.upper
        if value < 0: value = 0
        self.set_from_pixbuf(
            self.stars.get_pixbuf(value,self.upper)
            )
        self.value=value

    def get_value (self): return self.value
        
    def set_upper (self, value):
        """Change the upper number of stars allowed.

        Update our image accordingly."""
        self.upper = upper
        self.set_value(self.value)

    def set_text (self, value): self.set_value(int(value))
    def get_text (self): return "%s"%self.get_value()
        
# Next is a Button type class that allows the user to set the value
# via the mouse or the keyboard

class StarButton (gtk.Button):
    __gtype_name__ = 'StarButton'

    """A StarButton, to allow the user to select a number using icons.

    'Stars' are one of the normal elements to select. So that a user
    could rate on a scale of one-to-four stars.
    """

    __custom_handler_names__ = ['changed']
    _custom_handlers_ = {}

    def __init__ (self,
                  star_gen=star_generator,
                  start_value = 0,
                  upper=10,
                  ):
        """Initiate a StarButton.

        star_gen is an instance of the StarGenerator class which will
        generate our actual images of stars or whatever else.

        Upper is the upper number of 'stars' the user can select.

        start_value is our initial value.

        if interactive is True, we will catch click and keyboard
        events and allow the user to change the value using the
        keyboard.

        """
        self.__gobject_init__()
        self.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event',
                     self.buttonpress_cb)
        self.connect('key-press-event',
                     self.keypress_cb)
        #self.connect('activate',
        #             self.activate_cb)
        self.connect('mnemonic-activate',
                     self.activate_cb)
        self.image = StarImage(star_gen, value=start_value, upper=upper)
        self.add(self.image)
        self.image.show()
        # set up convenience methods        
        self.get_value = self.image.get_value
        self.set_upper = self.image.set_upper

    def set_value (self, value):
        self.image.set_value(value)
        if self._custom_handlers_.has_key('changed'):
            for h in self._custom_handlers_['changed']:
                if h(self): break
        return True

    def set_text (self, value): self.set_value(int(value))
    def get_text (self): return "%s"%self.get_value()

    def connect (self, name, handler):
        """We do something very very bad."""
        if name in self.__custom_handler_names__:
            if self._custom_handlers_.has_key(name):
                self._custom_handlers_[name].append(handler)
            else:
                self._custom_handlers_[name]=[handler]
        else:
            gtk.Button.connect(self,name,handler)

    def activate_cb (self, *args):
        self.grab_focus()
        return True

    def buttonpress_cb (self, widget, event):
        x,y = event.get_coords()
        wx,wy = self.image.translate_coordinates(self.image,int(x),int(y))
        self.star_width =  self.image.get_pixbuf().get_width() / self.image.upper
        star = x / self.star_width + 1
        star = int(star)
        if self.image.value >= star:
            # if we're clicking on a set icon, we want it to go away
            self.set_value(star-1)
        else:
            # otherwise we want it to be filled            
            self.set_value(star)
        return True
        
    def keypress_cb (self, widget, event):
        name=gtk.gdk.keyval_name(event.keyval)
        if name in PLUS_ONE_KEYS:
            self.set_value(self.image.value+1)
            return True
        elif name in MINUS_ONE_KEYS:
            self.set_value(self.image.value-1)
            return True
        elif name in PLUS_MAX_KEYS:
            self.set_value(self.image.upper)
            return True
        elif name in MINUS_MAX_KEYS:
            self.set_value(0)
            return True
        elif name in ACTIVATE_KEYS:
            return True
        elif name in [str(x) for x in range(self.image.upper/2 + 1)]:
            self.set_value(int(name)*2)
            return True


class TreeWithStarMaker:
    """A class to automatically handle stars in trees.

    This is a little backasswards to be honest, but it's better than repeating
    code oodles of times.

    We implement our own "signal" handling of a sort, allowing users to connect
    to a change in value by calling connect_change_handler(handler).

    Handlers will take arguments like this and should return True to
    prevent us from setting the star value. (They will also prevent
    other handlers from doing their thing, as happens elsewhere in the
    gtk world).

    def handler (value, model, treeiter, colnum):
        '''This handler will just set the value in our model.
        Presumably you want to do something more with the data
        '''
        model.set_value(treeiter,colnum,value)
    """
    def __init__ (self,
                  tree,
                  star_generator,
                  col_title=_("Rating"),
                  col_position=-1,
                  data_col=0,
                  handlers=[],
                  upper=10,
                  editable=True,
                  properties={}
                  ):
        self.tree=tree
        self.star_generator=star_generator
        self.col_title=col_title
        self.col_position=col_position
        self.data_col=data_col
        self.handlers = handlers
        self.upper = upper
        self.editable=editable
        self.properties = properties
        # setup our column
        self.setup_column()
        self.setup_callbacks()
        
    def connect_change_handler (self, handler): self.handlers.append(handler)

    def call_handlers (self, *params):
        for handler in self.handlers:
            if handler(*params): break

    def setup_column (self):
        self.cellrenderer = gtk.CellRendererPixbuf()        
        tot_cols=self.tree.insert_column_with_data_func(
            self.col_position,
            self.col_title,
            self.cellrenderer,
            self.cell_data_func)
        if self.col_position == -1:
            self.col_position = tot_cols-1
        if self.editable:
            self.cellrenderer.set_property('mode',gtk.CELL_RENDERER_MODE_EDITABLE)
        self.cellrenderer.set_property('xalign',0)
        col=self.tree.get_column(self.col_position)
        col.set_sort_column_id(self.data_col)
        for p,v in self.properties.items():
            col.set_property(p,v)
        self.col = col        

    def setup_callbacks (self):
        self.tree.connect('button-press-event',self.tree_click_callback)
        self.tree.connect('key-press-event',self.tree_keypress_callback)

    def cell_data_func (self, tree_column, cell, model, tree_iter):
        """Populate our cell with a pixbuf based on an integer"""
        val = model.get_value(tree_iter,self.data_col)
        pb = self.star_generator.get_pixbuf(int(val),self.upper)
        cell.set_property('pixbuf',pb)

    def tree_click_callback (self, tv, event):
        x = int(event.x)
        y = int(event.y)
        try:
            path, col, cellx, celly = tv.get_path_at_pos(x,y)
        except:
            return
        if col.get_property('title')==self.col_title:
            # If we're changing rows, we assume our user doesn't want to
            # click this button yet. This may be bad behavior, but it seems
            # reasonable for the time being.
            if hasattr(self,'curpath') and path == self.curpath:
                mod=tv.get_model()
                itr=mod.get_iter(path)
                curval=mod.get_value(itr,0)
                self.star_width = self.cellrenderer.get_property('pixbuf').get_width()/self.upper
                starval = cellx / self.star_width + 1
                curval = mod.get_value(itr,self.data_col)
                if starval > curval:
                    self.call_handlers(starval, mod, itr, self.data_col)
                    #mod.set_value(itr,self.col_position,starval)
                else:
                    self.call_handlers(starval-1, mod, itr, self.data_col)
                    #mod.set_value(itr,self.col_position,starval-1)
            self.curpath = path

    def tree_keypress_callback (self, tv, event):
        path,col = tv.get_cursor()
        if not col: return
        if not path: return
        if col.get_property('title') == self.col_title:
            # go ahead and edit...
            name=gtk.gdk.keyval_name(event.keyval)
            mod = tv.get_model()
            itr = mod.get_iter(path)
            curval = mod.get_value(itr,self.data_col)
            if name in MINUS_ONE_KEYS:
                #mod.set_value(itr,self.col_position,curval - 1)
                self.call_handlers(curval - 1, mod, itr, self.data_col)
                return True
            if name in PLUS_ONE_KEYS:
                #mod.set_value(itr,self.col_position,curval + 1)
                self.call_handlers(curval + 1, mod, itr, self.data_col)
                return True
            elif name in [str(x) for x in range(self.upper/2 + 1)]:
                #mod.set_value(itr,self.col_position,int(name))
                self.call_handlers(int(name)*2, mod, itr, self.data_col)
                return True
        
    
# Next is a proof of concept making this work in a TreeView

class Tree(gtk.TreeView):
    def __init__(self,stars):
        self.stars = stars
        self.upper = 10
        self.store = gtk.ListStore(gobject.TYPE_STRING,
                                   gobject.TYPE_INT)
        for i in range(10):
            for n in range(6):
                self.store.append(['Test %s%s'%(i,n),n])
        gtk.TreeView.__init__(self)
        self.set_size_request(300, 200)
        self.set_model(self.store)
        self.set_headers_visible(True)
        rend = gtk.CellRendererText()
        column = gtk.TreeViewColumn('First', rend, text=0)
        column.set_sort_column_id(0)
        self.append_column(column)
        TreeWithStarMaker(self, self.stars, data_col=1, handlers=[self.rating_change_handler])
        column = gtk.TreeViewColumn('Second', rend, )
        self.append_column(column)

    def rating_change_handler (self, value, model, treeiter, colnum):
        model.set_value(treeiter,colnum,value)
        
if __name__ == '__main__':
    vb = gtk.VBox()
    s = StarGenerator()
    for i in range(10):
        hb = gtk.HBox()
        hb.pack_start(StarButton(s,start_value=i),fill=False,expand=False)
        vb.add(hb)
    w=gtk.Window()
    w.add(vb)
    b = gtk.Button(stock=gtk.STOCK_QUIT)
    b.connect('clicked',lambda *args: w.hide() or gtk.main_quit())
    vb.add(b)
    t = Tree(s)
    vb.add(t)
    vb.show_all()
    w.connect('delete-event',lambda *args: w.hide() or gtk.main_quit())
    w.show_all()
    gtk.main()
        
            
    
