import Image, ImageDraw, gtk.gdk, os.path
from gourmet.ImageExtras import get_pixbuf_from_jpg
from gourmet.ratingWidget import star_generator

curdir = os.path.split(__file__)[0]

ICON_SIZE=125

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
    return pb.scale_simple(target_w,target_h,gtk.gdk.INTERP_BILINEAR)

def get_pixbuf_from_image (image):

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


generic_recipe_image = scale_pb(gtk.gdk.pixbuf_new_from_file(os.path.join(curdir,'images','generic_recipe.png')))

def get_recipe_image (rec):
    if rec.image:
        pb = scale_pb(get_pixbuf_from_jpg(rec.image))
    else:
        pb = generic_recipe_image.copy()
    big_side = ((pb.props.height > pb.props.width and pb.props.height) or pb.props.width)
    if rec.rating:
        #sg = get_star_generator()
        sg = star_generator        
        ratingPB = sg.get_pixbuf(rec.rating)
        h = pb.get_height() - ratingPB.get_height() - 5
        w = pb.get_width() - ratingPB.get_width() - 5
        if h < 0: h = 0
        if w < 0: w = 0
        if ratingPB.props.width > pb.props.width:
            SCALE = float(pb.props.width)/ratingPB.props.width
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
            gtk.gdk.INTERP_BILINEAR,
            255 # overall_alpha
            )
    if rec.preptime:
        prepPB = get_time_slice(rec.preptime)
        prepPB = prepPB.scale_simple(int(big_side*0.3),int(big_side*0.3),gtk.gdk.INTERP_BILINEAR)
        prepPB.composite(
            pb,
            pb.props.width/2 + 5,5,
            prepPB.props.width,prepPB.props.height,
            pb.props.width/2 + 5,5,
            1,1,gtk.gdk.INTERP_BILINEAR,
            188 # alpha
            )
    if rec.cooktime:
        cookPB = get_time_slice(rec.cooktime)
        cookPB = cookPB.scale_simple(int(big_side*0.3),int(big_side*0.3),gtk.gdk.INTERP_BILINEAR)
        cookPB.composite(
            pb,
            pb.props.width/2 + 5,pb.props.height/2,
            cookPB.props.width,cookPB.props.height,
            pb.props.width/2 + 5,pb.props.height/2,
            1,1,gtk.gdk.INTERP_BILINEAR,
            188 # alpha
            )
    return pb

class PiePixbufGenerator:

    '''Generate Pie-chart style pixbufs representing circles'''

    def __init__ (self):
        self.slices = {}

    def get_image (self, angle, color):
        angle = int(angle)
        if self.slices.has_key((angle,color)): return self.slices[(angle,color)]
        img = Image.new('RGBA',
                        (ICON_SIZE,ICON_SIZE),
                        255 # background
                        )
        d = ImageDraw.Draw(img)
        d.pieslice((10,10,ICON_SIZE-10,ICON_SIZE-10),-90,-90 + angle, color)
        self.slices[(angle,color)] = get_pixbuf_from_image(img)
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

