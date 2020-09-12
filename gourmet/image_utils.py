from typing import Optional
import io

from gi.repository import Gio, GLib
from gi.repository.GdkPixbuf import Pixbuf
from PIL import Image, ImageFile


def shrink_image(original: ImageFile.ImageFile,
                 width: Optional[int] = None,
                 height: Optional[int] = None):
    """Shrink an image to have a maximum given width or height.

    This function is only called when creating a new recipe, and generating its
    thumbnail and recipe card image, both of which will be stored in the
    database.
    """
    iwidth, iheight = original.size
    resized = False

    # Shrink based on width
    if width is not None and iwidth > width:
        new_height = int(width/iwidth * iheight)
        if height is None or new_height < height:
            shrunk = original.resize((width, new_height))
            resized = True

    # Shrink base on height
    if not resized and height is not None and iheight > height:
        new_width = int(height/iheight * iwidth)
        shrunk = original.resize((new_width, height))
        resized = True
        
    return shrunk if resized else original


def bytes_to_pixbuf(raw: bytes) -> Pixbuf:
    glib_bytes = GLib.Bytes.new(raw)
    stream = Gio.MemoryInputStream.new_from_bytes(glib_bytes)
    return Pixbuf.new_from_stream(stream)


def bytes_to_image(raw: bytes) -> Image.Image:
    sfi = io.BytesIO(raw)
    sfi.seek(0)
    return Image.open(sfi)


def image_to_bytes(image: Image.Image) -> bytes:
    ofi = io.BytesIO()
    image = image.convert('RGB')
    image.save(ofi, 'jpeg')
    return ofi.getvalue()
