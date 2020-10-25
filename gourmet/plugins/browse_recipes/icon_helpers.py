import os.path

from gi.repository import GdkPixbuf, Gtk
from PIL import Image, ImageDraw

from gourmet.image_utils import bytes_to_pixbuf, image_to_pixbuf
from gourmet.gtk_extras.ratingWidget import star_generator

curdir = os.path.split(__file__)[0]
ICON_SIZE = 125


def scale_pb (pb, do_grow=True):
    w = pb.get_width()
    h = pb.get_height ()
    if not do_grow and (w < ICON_SIZE or h < ICON_SIZE):
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
    return pb.scale_simple(target_w,target_h,GdkPixbuf.InterpType.BILINEAR)


generic_recipe_image = scale_pb(GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','generic_recipe.png')))
preptime_image = GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','preptime.png'))
preptime_empty_image = GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','preptime_empty_clock.png'))
cooktime_image = GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','cooktime.png'))
cooktime_empty_image = GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','cooktime_empty_clock.png'))
cuisine_image = scale_pb(GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','cuisine.png')))
rating_image =  scale_pb(GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','rating.png')))
source_image =  scale_pb(GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','source.png')))
category_image =  scale_pb(GdkPixbuf.Pixbuf.new_from_file(os.path.join(curdir,'images','generic_category.png')))

attr_to_icon = {
    'category':category_image,
    'source':source_image,
    'rating':rating_image,
    'cuisine':cuisine_image,
    'cooktime':scale_pb(cooktime_image),
    'preptime':scale_pb(preptime_image),
    }

def get_recipe_image (rec):
    if rec.image:
        pb = scale_pb(bytes_to_pixbuf(rec.image))
    else:
        pb = generic_recipe_image.copy()
    big_side = ((pb.get_property('height') > pb.get_property('width') and pb.get_property('height')) or pb.get_property('width'))
    if rec.rating:
        #sg = get_star_generator()
        sg = star_generator
        ratingPB = sg.get_pixbuf(rec.rating)
        h = pb.get_height() - ratingPB.get_height() - 5
        w = pb.get_width() - ratingPB.get_width() - 5
        if h < 0: h = 0
        if w < 0: w = 0
        if ratingPB.get_property('width') > pb.get_property('width'):
            SCALE = float(pb.get_property('width'))/ratingPB.get_property('width')
        else:
            SCALE = 1
        ratingPB.composite(
            pb,
            w, #dest_x
            h, # dest_y
            int(ratingPB.get_width()*SCALE), # dest_width,
            int(ratingPB.get_height()*SCALE), #dest_height
            w, #offset_x,
            h, #offset_y
            SCALE,SCALE, #scale_x,scale_y
            GdkPixbuf.InterpType.BILINEAR,
            255 # overall_alpha
            )
    if rec.preptime:
        #prepPB = get_time_slice(rec.preptime)
        prepPB = make_preptime_icon(rec.preptime)
        prepPB = prepPB.scale_simple(int(big_side*0.4),int(big_side*0.4),GdkPixbuf.InterpType.BILINEAR)
        prepPB.composite(
            pb,
            pb.get_property('width')/2 + 5,5,
            prepPB.get_property('width'),prepPB.get_property('height'),
            pb.get_property('width')/2 + 5,5,
            1,1,GdkPixbuf.InterpType.BILINEAR,
            127 # alpha
            )
    if rec.cooktime:
        cookPB = make_cooktime_icon(rec.cooktime)
        cookPB = cookPB.scale_simple(int(big_side*0.4),int(big_side*0.4),GdkPixbuf.InterpType.BILINEAR)
        cookPB.composite(
            pb,
            pb.get_property('width')/2 + 5,pb.get_property('height')/2,
            cookPB.get_property('width'),cookPB.get_property('height'),
            pb.get_property('width')/2 + 5,pb.get_property('height')/2,
            1,1,GdkPixbuf.InterpType.BILINEAR,
            188 # alpha
            )
    return pb

class PiePixbufGenerator:

    '''Generate Pie-chart style pixbufs representing circles'''

    def __init__ (self):
        self.slices = {}

    def get_image (self, angle, color):
        angle = int(angle)
        if (angle,color) in self.slices: return self.slices[(angle,color)]
        img = Image.new('RGBA',
                        (ICON_SIZE,ICON_SIZE),
                        255 # background
                        )
        d = ImageDraw.Draw(img)
        d.pieslice((10,10,ICON_SIZE-10,ICON_SIZE-10),-90,-90 + angle, color)
        self.slices[(angle,color)] = image_to_pixbuf(img)
        return self.slices[(angle,color)]

    def get_time_image (self, time_in_seconds):
        if time_in_seconds <= 60:
            return self.get_image( (time_in_seconds/60.0) * 360, 'pink') # seconds (sweep hand)
        elif time_in_seconds <= 60 * 60:
            return self.get_image( (time_in_seconds/float(60*60)) * 360, 'red') # minutes (minute hand)
        elif time_in_seconds <= 60 * 60 * 60 * 12: # hours (12 hours)
            return self.get_image( (time_in_seconds/float(60*60*12) * 360), 'blue')
        else:
            return self.get_image(359, 'blue')


pie_generator = PiePixbufGenerator()
make_pie_slice = pie_generator.get_image
get_time_slice = pie_generator.get_time_image

def make_time_icon (text):
    img = Image.new('RGBA',
                    (ICON_SIZE,ICON_SIZE),
                    255 # background
                    )
    d = ImageDraw.Draw(img)
    #Thosed.text(

PREP = 1
COOK = 2

def make_preptime_icon (preptime):
    return make_time_icon(preptime,mode=PREP)

def make_cooktime_icon (cooktime):
    return make_time_icon(cooktime,mode=COOK)

def make_time_icon (time, mode):
    LEFT_CORNER = (31,103)
    W,H = 65,65
    if mode == PREP:
        icon_image = preptime_empty_image.copy()
    elif mode == COOK:
        icon_image = cooktime_empty_image.copy()
    slice_pb = get_time_slice(time)
    SCALE_X = W / float(slice_pb.get_property('width'))
    SCALE_Y = H / float(slice_pb.get_property('height'))
    args = (icon_image,
           LEFT_CORNER[0],
           LEFT_CORNER[1],
           W,H,
           LEFT_CORNER[0],
           LEFT_CORNER[1],
           SCALE_X, SCALE_Y, GdkPixbuf.InterpType.BILINEAR, 255)
    slice_pb.composite(*args)
    return icon_image

if __name__ == '__main__':
    t = 60*60*6
    hb = Gtk.HBox()
    pb = make_preptime_icon(t)
    w = Gtk.Window()
    i = Gtk.Image(); i.set_from_pixbuf(pb)
    hb.pack_start(i, True, True, 0)
    pb2 = get_time_slice(t)
    i2 = Gtk.Image(); i2.set_from_pixbuf(pb2)
    hb.pack_start(i2, True, True, 0)
    w.add(hb)
    w.show_all()
    w.connect('delete-event',lambda *args: Gtk.main_quit())
    Gtk.main()
