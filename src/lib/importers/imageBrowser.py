import gtk, gtk.gdk, gobject
from gourmet.ImageExtras import get_pixbuf_from_jpg
from gourmet.thumbnail import check_for_thumbnail,fetched_uris
from gourmet.dialog_extras import ModalDialog
import unittest
from gourmet.gdebug import debug,TimeAction
import threading, Queue

def grab_thumbnail (uri, type, iqueue, pqueue):
    def reporthook (block, blocksize, total):
        try:
            perc = (float(total)/(block*blocksize))
        except:
            perc = -1
        pqueue.put(('Getting %s'%uri,perc))
    pqueue.put_nowait(('Getting %s'%uri,0))
    import time
    t=time.time()
    fi = check_for_thumbnail(uri,type,reporthook)
    #fi = check_for_thumbnail(uri,type)
    iqueue.put((fi,uri))
    
class ImageBrowser (gtk.IconView):
    def __init__ (self,*args,**kwargs):
        gtk.IconView.__init__(self,*args,**kwargs)
        self.model = gtk.ListStore(gtk.gdk.Pixbuf,str)
        self.set_selection_mode(gtk.SELECTION_SINGLE)
        self.set_model(self.model)
        self.set_pixbuf_column(0)
        self.image_queue = Queue.Queue()
        self.progress_queue = Queue.Queue()
        self.updating = False
        self.adding = []
        gobject.timeout_add(100,self.update_progress)
        gobject.timeout_add(100,self.add_image_from_queue)
        
    def add_image_from_uri (self, u):
        self.adding.append(u)
        t=threading.Thread(target=lambda *args: grab_thumbnail(
            u,
            'small',
            self.image_queue,
            self.progress_queue)
                           )
        t.run()

    def add_image_from_queue (self):
        try:
            fi,u = self.image_queue.get_nowait()
            if fi:
                pb = gtk.gdk.pixbuf_new_from_file(fi)
                self.model.append([pb,u])
                self.adding.remove(u)
        except Queue.Empty:
            pass
        return True

    def update_progress (self):
        try:
            progress,text = self.progress_queue.get_nowait()
            self.set_progress(progress,text)            
        except:
            if not self.adding and hasattr(self,'progressbar'):
                self.progressbar.hide()
            else:
                self.progressbar.pulse()
        return True

    def set_progress (self, progress, text):
        if hasattr(self,'progressbar'):
            self.progressbar.show()
            self.progressbar.set_percentage(prog)
            self.progressbar.set_text(text)

class ImageBrowserDialog (ModalDialog):
    def __init__ (self, default=None, title="Select Image",okay=True,
                  label="Select an image", sublabel=None,parent=None, cancel=True, modal=True, expander=None):
        ModalDialog.__init__(self,default=default, title=title,
                             okay=okay,label=label,sublabel=sublabel,
                             parent=parent, cancel=cancel, modal=modal,
                             expander=expander)
        self.set_default_size(600,600)

    def setup_dialog (self, *args, **kwargs):
        ModalDialog.setup_dialog(self,*args,**kwargs)
        self.ib = ImageBrowser()
        self.ib.connect('selection-changed',self.selection_changed_cb)
        self.ib.connect('item-activated',self.okcb)
        self.sw = gtk.ScrolledWindow()
        self.pb = gtk.ProgressBar()
        self.vbox.pack_end(self.sw)
        self.vbox.pack_end(self.pb,expand=False)
        self.ib.progressbar = self.pb
        self.sw.add(self.ib)
        self.sw.show_all()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

    def okcb (self, *args,**kwargs):
        ModalDialog.okcb(self,*args,**kwargs)

    def selection_changed_cb (self, iv):
        selected_paths = iv.get_selected_items()
        if selected_paths:
            itr = self.ib.model.get_iter(selected_paths[0])
            val = self.ib.model.get_value(itr,1)
            self.ret = val
        else:
            self.ret = None

    def add_images_from_uris_w_progress (self, uris):
        self.image_queue = Queue.Queue()
        self.progress_queue = Queue.Queue()        

    def add_image_from_uri (self, u):
        self.ib.add_image_from_uri(u)

class ImageBrowserTest (unittest.TestCase):

    def setUp (self):
        self.ib = ImageBrowser()
        self.w = gtk.Window()
        self.sw = gtk.ScrolledWindow()
        self.sw.add(self.ib)
        self.sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.w.add(self.sw)
        
    #def testWindow (self):
    #    self.w.show_all()
    #    self.ib.show_all()
    #    for image in ['Caneel beach.JPG','Cinnamon beach.JPG','dsc00258.jpg']:
    #        self.ib.add_image_from_uri('file:///home/tom/pictures/'+image)
    #    self.ib.add_image_from_uri('http://wikipes.com/wikipes-logo.gif')
    #    self.w.connect('delete-event',lambda *args: gtk.main_quit())
    #    gtk.main()

    def testDialog (self):
        self.ibd = ImageBrowserDialog()
        self.ibd.add_image_from_uri('http://wikipes.com/wikipes-logo.gif')
        for image in ['Caneel beach.JPG','Cinnamon beach.JPG','dsc00258.jpg']:
            self.ibd.add_image_from_uri('file:///home/tom/pictures/'+image)        
        self.ibd.run()

def get_image_file (uri):
    return fetched_uris[uri]

if __name__ == '__main__':
    unittest.main()
    
