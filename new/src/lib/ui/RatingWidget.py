import gtk
import gtk.gdk as gdk
import gobject
import os.path
import Image
import tempfile
from gettext import gettext as _
import gourmet.gglobals as gglobals

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

MAX_SCORE = 5

class StarGenerator:

    """A convenient class that will give us a gtk.Pixbuf representing stars
    for any number.

    set_image and unset_image must have the same width!""" 

    def __init__ (self):
        self.width,self.height = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        set_image=os.path.join(gglobals.imagedir,'set-star.png')
        unset_image=os.path.join(gglobals.imagedir,'no-star.png')
        self.set_img   = Image.open(set_image)
        self.unset_img = Image.open(unset_image).resize(self.set_img.size)
        #convert to RGBA
        self.set_img = self.set_img.convert('RGBA')
        self.unset_img = self.unset_img.convert('RGBA')
        self.width,self.height = self.set_img.size
        self.set_region = self.set_img.crop((0,0,
                                             self.width,
                                             self.height))
        self.unset_region = self.unset_img.crop((0,0,
                                             self.width,
                                             self.height))
        self.pixbufs = {}
        self.image_files = {}

        self.set_buf = gdk.pixbuf_new_from_file_at_size(set_image, self.width, self.height)
        self.unset_buf = gdk.pixbuf_new_from_file_at_size(unset_image, self.width, self.height)

    def get_pixbuf (self,n):

        """Return a pixbuf with an image representing n/max stars"""

        if self.pixbufs.has_key((n, MAX_SCORE)):
            return self.pixbufs[(n, MAX_SCORE)]
        else:
            img = self.build_image(n)
            pb=self.get_pixbuf_from_image(img)
            self.pixbufs[(n, MAX_SCORE)]=pb
            return pb

    def get_full_width (self):
        return self.width*MAX_SCORE

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
        
    def build_image (self, n):
        """Build an image representing n/max stars."""
        img=Image.new('RGBA',
                      (self.get_full_width(),
                       self.height),
                      None)
        for i in range(0,(MAX_SCORE)):
            if i < n:
                to_paste = self.set_region
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
            image.tostring(),
            gtk.gdk.COLORSPACE_RGB,
            is_rgba,
            8,
            image.size[0],
            image.size[1],
            (is_rgba and 4 or 3) * image.size[0] #rowstride
            )
        return pb
        
    def render_stars (self, widget, window, x, y, x_offset, y_offset, rating, selected):
        rtl = (widget.get_direction() == gtk.TEXT_DIR_RTL)
        icon_width,icon_height = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        for i in range(MAX_SCORE):
            offset = 0
            state = None
            if selected:
                if widget.props.has_focus:
                    state = gtk.STATE_SELECTED
                else:
                    state = gtk.STATE_ACTIVE
            else:
                offset = 120
                if widget.state == gtk.STATE_INSENSITIVE:
                    state = gtk.STATE_INSENSITIVE
                else:
                    state = gtk.STATE_NORMAL
                
            if i < rating:
                buf = star_generator.set_buf
            else:
                buf = star_generator.unset_buf
            if buf is None: return False
            star_offset = 0
            if rtl:
                star_offset = (MAX_SCORE - i - 1) * icon_width
            else:
                star_offset = i * icon_width
            window.draw_pixbuf(
                None, buf, x, y, x_offset + star_offset, y_offset, 
                icon_width, icon_height, gdk.RGB_DITHER_NORMAL, 0, 0
            )
        return True
    
    def get_rating_from_widget (self, widget, x, y, width):
        return 0
    
    
star_generator = StarGenerator()

# RatingImage is a class that allows easy setting of an image from a value.

class RatingImage (gtk.Image):
    def __init__ (self,
                  value=0):
        """Create an Image widget with value/upper stars filled in.

        star_generator is an instance of the StarGenerator class which will do
        the work of creating the Pixbufs with the star images.

        The number can be changed via the get_value and set_value methods.

        If you want the user to be able to change the number of stars,
        use a StarButton.
        """
        gtk.Image.__init__(self)
        self.set_value(value)
        
    def set_value (self, value):
        """Set value. Silently floor value at 0 and cap it at MAX_SCORE"""
        if value > MAX_SCORE: value = MAX_SCORE
        if value < 0: value = 0
        self.set_from_pixbuf(star_generator.get_pixbuf(value))
        self.value=value

    def get_value (self): return self.value

    def set_text (self, value): self.set_value(int(value))
    def get_text (self): return "%s"%self.get_value()
        
# Next is a Button type class that allows the user to set the value
# via the mouse or the keyboard

class RatingButton (gtk.Button):
    """
    A StarButton, to allow the user to select a number using icons.

    'Stars' are one of the normal elements to select. So that a user
    could rate on a scale of one-to-four stars.
    """

    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_STRING,
                    []),
    }

    def __init__ (self):
        self.__gobject_init__()
        self.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.buttonpress_cb)
        self.connect('key-press-event', self.keypress_cb)
        self.connect('mnemonic-activate', self.activate_cb)
        self.image = RatingImage()
        self.add(self.image)
        self.image.show()
        # set up convenience methods        
        self.get_value = self.image.get_value
        self.show()

    def set_value (self, value):
        self.image.set_value(value)
        self.emit('changed')
        return True

    def set_text (self, value): self.set_value(int(value))
    def get_text (self): return "%s"%self.get_value()

    def activate_cb (self, *args):
        self.grab_focus()
        return True

    def buttonpress_cb (self, widget, event):
        x,y = event.get_coords()
        wx,wy = self.image.translate_coordinates(self.image,int(x),int(y))
        self.star_width =  self.image.get_pixbuf().get_width() / MAX_SCORE
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
        elif name in [str(x) for x in range(MAX_SCORE + 1)]:
            self.set_value(int(name))
            return True

class CellRendererRating (gtk.GenericCellRenderer):

    rating = gobject.property(type=int)

    def __init__ (self):
        gtk.GenericCellRenderer.__init__(self)
        
    def on_get_size (self, widget, cell_area):
        icon_width,icon_height = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        width = self.get_property('xpad') * 2 + icon_width * MAX_SCORE
        height = self.get_property('ypad') * 2 + icon_height
        return 0,0,width,height
        
    def on_activate (self, event, widget, path, bg_area, cell_area, flags):
        x,y = widget.get_pointer()
        x,y = widget.widget_to_tree_coords(x, y)
        self.rating = star_generator.get_rating_from_widget(
            widget, x - cell_area.x, y - cell_area.y, cell_area.width
        )
        
    def on_render (self, window, widget, bg_area, cell_area, expose_area, flags):
        x,y,width,height = self.get_size(widget, cell_area)
        x += cell_area.x
        y += cell_area.y
        width -= self.get_property('xpad') * 2
        height -= self.get_property('ypad') * 2
        
        draw_rect = cell_area.intersect(gdk.Rectangle(x,y,width,height))
        if draw_rect is None: return
        selected = flags & gtk.CELL_RENDERER_SELECTED
        star_generator.render_stars(
            widget, window,
            draw_rect.x - x, draw_rect.y - y, 
            draw_rect.x, draw_rect.y, 
            self.rating, selected
        )
        
    def on_start_editing (event, widget, path, background_area, cell_area, flags):
        pass

