import io

from gi.repository import GdkPixbuf, Gio, GLib
from PIL import Image

from gourmet.gdebug import debug


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


def bytes_to_pixbuf(raw: bytes) -> GdkPixbuf.Pixbuf:
    """Create a GdkPixbuf.Pixbuf from bytes"""
    glib_bytes = GLib.Bytes.new(raw)
    stream = Gio.MemoryInputStream.new_from_bytes(glib_bytes)
    return GdkPixbuf.Pixbuf.new_from_stream(stream)


def bytes_to_image(raw: bytes) -> Image.Image:
    """Given raw image data (bytes), return an Image object."""
    sfi = io.BytesIO(raw)
    sfi.seek(0)
    return Image.open(sfi)


def image_to_bytes(image: Image.Image) -> bytes:
    ofi = io.BytesIO()
    image = image.convert('RGB')
    image.save(ofi, 'jpeg')
    return ofi.getvalue()
