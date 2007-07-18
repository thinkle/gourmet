import os, os.path, tempfile, gtk, Image, StringIO
from gdebug import *

def resize_image (image, width=None, height=None):
    debug("resize_image (self, image, width=None, height=None):",5)
    """Resize an image to have a maximum width=width or height=height.
    We only shrink, we don't grow."""
    iwidth,iheight=image.size
    resized=False
    if width and iwidth > width:
	newheight=int((float(width)/float(iwidth)) * iheight)
	if not height or newheight < height:
	    retimage=image.resize((width, newheight))
	    resised=True
    if not resized and height and iheight > height:
	newwidth = int((float(height)/float(iheight)) * iwidth)
	retimage = image.resize((newwidth,height))
	resized=True
    if resized:
	return retimage
    else:
	return image

def get_image_from_string (raw):
    """Given raw image data, return an Image object."""
    if os.name =='posix':
        sfi=StringIO.StringIO()
        sfi.write(raw)
        sfi.seek(0)
    else:
        sfi = write_image_tempfile(raw)
    try:
        return Image.open(sfi)
    except:
        print 'Trouble in image land.'
        print 'We dumped the offending string here:'
        print sfi
        print "But we can't seem to load it..."

def get_string_from_image (image):
    """Convert an image into a string representing its JPEG self"""
    ofi = StringIO.StringIO()
    image = image.convert('RGB')
    image.save(ofi,"JPEG")
    ret = ofi.getvalue()
    ofi.close()
    return ret

def get_string_from_pixbuf (pb):
    fn = tempfile.mktemp('jpg')
    pb.save(fn,'jpeg')
    s = file(fn,'r').read()
    return s
    
def get_pixbuf_from_jpg (raw):
    """Given raw data of a jpeg file, we return a gtk.gdk.Pixbuf"""
    #o=open('/tmp/recimage.jpg','w')
    fn=write_image_tempfile(raw,name='gourmet_tempfile')
    i=gtk.Image()
    i.set_from_file(fn)
    return i.get_pixbuf()

def write_image_tempfile (raw, name=None, ext=".jpg"):
    """Write a temporary image file.

    If not given a name, generate one.
    """
    if name:
        fn = os.path.join(tempfile.gettempdir(),
                            name + ext)
    else:
        fn = tempfile.mktemp(ext)
    o=open(fn,'wb')
    o.write(raw)
    o.close()
    return fn
    
