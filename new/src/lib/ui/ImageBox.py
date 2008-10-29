import system.ImageExtras as ie
from dialogs import extras as de

class ImageBox:
    def __init__ (self, RecCard):
        debug("__init__ (self, RecCard):",5)
        self.rc = RecCard
        self.glade = self.rc.glade
        self.imageW = self.glade.get_widget('recImage')
        self.addW = self.glade.get_widget('addImage')
        self.imageD = self.glade.get_widget('imageDisplay')
        self.image = None

    def get_image (self, rec=None):
        """Set image based on current recipe."""
        debug("get_image (self, rec=None):",5)
        if not rec:
            rec = self.rc.recipe
        if rec.image:
            try:
                self.set_from_string(rec.image)
            except:
                debug('Problem with image from recipe.', 0)
                import traceback; traceback.print_exc()
        else:
            self.image = None
        
    def commit (self):
        debug("commit (self):",5)
        """Return image and thumbnail data suitable for storage in the database"""
        if self.image:
            self.imageD.show()
            return ie.get_string_from_image(self.image),ie.get_string_from_image(self.thumb)
        else:
            self.imageD.hide()
            return '',''
        
    
    def draw_image (self):
        debug("draw_image (self):",5)
        """Put image onto widget"""
        if self.image:
            self.win = self.imageW.get_parent_window()
            if self.win:
                wwidth,wheight=self.win.get_size()
                wwidth=int(float(wwidth)/3)
                wheight=int(float(wheight)/3)
            else:
                wwidth,wheight=100,100
            self.image=ie.resize_image(self.image,wwidth,wheight)
            self.thumb=ie.resize_image(self.image,40,40)
            self.set_from_string(ie.get_string_from_image(self.image))

    def set_from_string (self, string):
        debug("set_from_string (self, string):",5)
        pb=ie.get_pixbuf_from_jpg(string)
        self.imageW.set_from_pixbuf(pb)
        self.orig_pixbuf = pb
        self.imageD.set_from_pixbuf(pb)

    def set_from_file (self, file):
        debug("set_from_file (self, file):",5)
        self.image = Image.open(file)
        self.draw_image()
        
    def set_from_fileCB (self, *args):
        debug("set_from_fileCB (self, *args):",5)
        buttons=(_("No image"), 0, gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK)
        f=de.select_image(_("Select Image"),action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=buttons)
        if f:
            Undo.UndoableObject(
                lambda *args: self.set_from_file(f),
                lambda *args: self.remove_image(),
                self.rc.history,
                widget=self.imageW).perform()
            self.edited=True

    def removeCB (self, *args):
        debug("removeCB (self, *args):",5)
        if self.image:
            current_image = ie.get_string_from_image(self.image)
        else:
            current_image = ie.get_string_from_pixbuf(self.orig_pixbuf)
        Undo.UndoableObject(
            lambda *args: self.remove_image(),
            lambda *args: self.set_from_string(current_image),
            self.rc.history,
            widget=self.imageW).perform()

    def remove_image (self):
        self.image=None
        self.orig_pixbuf = None
        self.draw_image()
        self.edited=True
