#!/usr/bin/env python
import os.path, tempfile, gtk
from gdebug import *

def get_pixbuf_from_jpg (raw):
    debug("get_pixbuf_from_jpg (raw):",5)
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
