import gtk
import os.path, tempfile
from gourmet.GourmetRecipeManager import get_application
from emailer import Emailer
import StringIO
import gourmet.exporters.exportManager as exportManager
import gourmet.exporters.exporter as exporter

class StringIOfaker (StringIO.StringIO):
    def __init__ (self, *args, **kwargs):
        StringIO.StringIO.__init__(self, *args, **kwargs)

    def close (self, *args):
        pass

    def close_really (self):
        StringIO.StringIO.close(self)

class RecipeEmailer (Emailer):
    def __init__ (self, recipes, attachment_types=["pdf"], do_text=True):
        Emailer.__init__(self)
        self.attachments_left = self.attachment_types = list(attachment_types)
        self.attached = []
        self.recipes = recipes
        self.rg = get_application()
        self.rd = self.rg.rd
        self.change_units=self.rg.prefs.get('readableUnits',True)
        if len(recipes) > 1:
            self.subject = _("Recipes")
        elif recipes:
            self.subject = recipes[0].title

    def write_email_text (self):
        s = StringIOfaker()
        first = True
        e=exporter.ExporterMultirec(self.rd,
                                    self.recipes,
                                    s,
                                    padding="\n\n-----\n")
        e.run()
        if not self.body: self.body=""
        self.body += s.getvalue()
        s.close_really()

    def write_attachments (self):
        em = exportManager.get_export_manager()
        for typ in self.attachment_types:
            name = _('Recipes')
            if len(self.recipes)==1:
                name = self.recipes[0].title.replace(':','-').replace('\\','-').replace('/','-')
            fn = os.path.join(tempfile.gettempdir(),"%s.%s"%(name,typ))
            self.attachments.append(fn)
            instance = em.do_multiple_export(self.recipes, fn)
            instance.connect('completed',self.attachment_complete,typ)
            print 'Start thread to create ',typ,'!','->',fn
    
    def attachment_complete (self, thread, typ):
        self.attachments_left.remove(typ)
        if not self.attachments_left:
            print 'Attachments complete! Send email!'
            self.send_email()
    
    def send_email_with_attachments (self, emailaddress=None):
        if emailaddress: self.emailaddress=emailaddress
        self.write_email_text()
        self.write_attachments()
        
    #def send_email_html (self, emailaddress=None, include_plain_text=True):
    #    if include_plain_text: self.write_email_text()
    #   else: self.body = None
    #   if emailaddress: self.emailaddress=emailaddress
    #     self.write_email_html()
    #   self.send_email()

    def send_email_text (self, emailaddress=None):
        if emailaddress: self.emailaddress=emailaddress 
        self.write_email_text()
        self.send_email()
        
