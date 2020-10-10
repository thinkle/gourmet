from collections import defaultdict
from enum import Enum
import io
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import unquote, urlparse

from gi.repository import Gio, GLib
from gi.repository.GdkPixbuf import Pixbuf
from PIL import Image, UnidentifiedImageError
import requests

MAX_THUMBSIZE = 10000000  # The maximum size, in bytes, of thumbnails we allow


class ThumbnailSize(Enum):
    SMALL = (128, 128)
    LARGE = (256, 256)


def cached(func):
    """A decorator to keep previously created thumbnails.

    This may be memory intensive. If it impedes usability, due to increased
    memory usage, it should be removed.
    """
    thumbnails: Dict[str, Dict[ThumbnailSize, Image.Image]] = defaultdict(dict)

    def wrapper(path, size=ThumbnailSize.LARGE):
        if path in thumbnails and size in thumbnails[path]:
            return thumbnails[path][size]

        image = func(path, size)

        thumbnails[path][size] = image
        return image

    return wrapper


@cached
def make_thumbnail(path: str, size=ThumbnailSize.LARGE) -> Optional[Pixbuf]:
    """Create an in-memory thumbnail from the given uri path.

    This function is used when browsing images to add to a recipe: thumbnails
    are displayed in the file chooser.
    Aspect ratios are kept, thus thumbnails won't necessarily be squared.

    The provided `path` is a str, provided by a Gtk.FileChooserDialog. As such,
    it is first converted to a Path object.
    """

    if path.startswith('http'):
        response = requests.get(path)
        path = io.BytesIO(response.content)

    else:
        path = Path(urlparse(unquote(path)).path)
        if not path.is_file():
            return

    try:
        image = Image.open(path)
    except (UnidentifiedImageError, ValueError):
        return

    image.thumbnail(size.value)
    return bytes_to_pixbuf(image_to_bytes(image))


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
