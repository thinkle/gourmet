import os.path, tempfile, gtk, Image, StringIO
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
    sfi=StringIO.StringIO()
    sfi.write(raw)
    sfi.seek(0)
    return Image.open(sfi)

def get_pixbuf_from_jpg (raw):
    """Given raw data of a jpeg file, we return a gtk.gdk.Pixbuf"""
    #o=open('/tmp/recimage.jpg','w')
    fn=os.path.join(tempfile.gettempdir(),'gourmet_temporary_img.jpg')
    o=open(fn,'w')
    o.write(raw)
    o.close()
    i=gtk.Image()
    i.set_from_file(fn)
    o.close()
    return i.get_pixbuf()
