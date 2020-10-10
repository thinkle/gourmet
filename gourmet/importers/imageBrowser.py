from typing import List
from gi.repository import GdkPixbuf, Gtk

from gourmet.image_utils import (bytes_to_pixbuf, image_to_bytes, make_thumbnail,
                                 pixbuf_to_image, ThumbnailSize)


class ImageBrowser(Gtk.Dialog):
    def __init__(self, parent: Gtk.Window, uris: List[str]):
        Gtk.Dialog.__init__(self, title="Choose an image",
                            transient_for=parent, flags=0)
        self.set_default_size(600, 600)

        self.pixbuf: GdkPixbuf.Pixbuf = None

        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf)
        iconview = Gtk.IconView.new()
        iconview.set_model(self.liststore)
        iconview.set_pixbuf_column(0)

        for uri in uris:
            image = make_thumbnail(uri, ThumbnailSize.SMALL)
            pixbuf = bytes_to_pixbuf(image_to_bytes(image))
            self.liststore.append([pixbuf])

        iconview.connect('selection-changed', self.on_selection)

        box = self.get_content_area()
        box.pack_end(iconview, True, True, 0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.show_all()

    def on_selection(self, iconview: Gtk.IconView):
        item = iconview.get_selected_items()
        if item:
            itr = self.liststore.get_iter(item[0])
            self.image = pixbuf_to_image(self.liststore.get_value(itr, 0))