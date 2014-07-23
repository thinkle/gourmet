#!/usr/bin/env python
import urllib, StringIO, os.path
import exporter, html_exporter, pdf_exporter
from gourmet import gglobals
import gourmet.gtk_extras.dialog_extras as de
from gourmet.gdebug import debug

class StringIOfaker (StringIO.StringIO):
    def __init__ (self, *args, **kwargs):
        StringIO.StringIO.__init__(self, *args, **kwargs)

    def close (self, *args):
        pass

    def close_really (self):
        StringIO.StringIO.close(self)

class Emailer:
    def __init__ (self, emailaddress=None, subject=None, body=None, attachments=[]):
        self.emailaddress=None
        self.subject=subject
        self.body=body
        self.attachments=attachments
        self.connector_string = "?"

    def send_email (self):
        self.url = "mailto:"
        if self.emailaddress: self.url += self.emailaddress
        if self.subject:
            self.url_append('subject',self.subject)
        if self.body:
            self.url_append('body',self.body)
        for a in self.attachments:
            self.url_append('attachment',a)              
        debug('launching URL %s'%self.url,0)
        gglobals.launch_url(self.url)

    def url_append (self, attr, value):
        self.url += "%s%s=%s"%(self.connector(),attr,urllib.quote(value.encode('utf-8','replace')))
                                                                   
    def connector (self):
        retval = self.connector_string
        self.connector_string = "&"
        return retval

class RecipeEmailer (Emailer):
    def __init__ (self, recipes, rd, conv=None, change_units=True):
        Emailer.__init__(self)
        self.recipes = recipes
        self.rd = rd
        self.conv = conv
        self.change_units=change_units
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
                                    conv=self.conv,
                                    padding="\n\n-----\n")
        e.run()
        if not self.body: self.body=""
        self.body += s.getvalue()
        s.close_really()

    def write_email_html (self):
        for r in self.recipes:
            fi = os.path.join(gglobals.tmpdir,"%s.htm"%r.title)
            ofi = open(fi,'w')
            e=html_exporter.html_exporter(self.rd,
                                          r,
                                          ofi,
                                          conv=self.conv,
                                          embed_css=True,
                                          imagedir="")
            ofi.close()
            self.attachments.append(fi)
            for i in e.images:
                self.attachments.append(i)

    def write_email_pdf (self):
        prefs = pdf_exporter.get_pdf_prefs()
        for r in self.recipes:
            fi = os.path.join(gglobals.tmpdir,"%s.pdf"%r.title)
            ofi = open(fi,'w')
            e = pdf_exporter.PdfExporter(self.rd,
                                         r,
                                         ofi,
                                         conv=self.conv,
                                         change_units=self.change_units,
                                         pdf_args=prefs)
            ofi.close()
            self.attachments.append(fi)

    def send_email_html (self, emailaddress=None, include_plain_text=True):
        if include_plain_text: self.write_email_text()
        else: self.body = None
        if emailaddress: self.emailaddress=emailaddress
        self.write_email_html()
        self.send_email()

    def send_email_text (self, emailaddress=None):
        if emailaddress: self.emailaddress=emailaddress
        self.write_email_text()
        self.send_email()
            
class EmailerDialog (RecipeEmailer):
    def __init__ (self, recipes, rd, prefs, conv=None):
        RecipeEmailer.__init__(self, recipes, rd, conv=conv, change_units=prefs.get('readableUnits',True))
        self.prefs = prefs
        self.option_list = {'':''}
        self.options = {
            _('Include Recipe in Body of E-mail (A good idea no matter what)'):('email_include_body',True),
            _('E-mail Recipe as HTML Attachment'):('email_include_html',False),
            _('E-mail Recipe as PDF Attachment'):('email_include_pdf',True),
            }
        self.option_list = []
        self.email_options = {}
        for k,v in self.options.items():
            self.email_options[v[0]]=apply(self.prefs.get,v)
            self.option_list.append([k,self.email_options[v[0]]])

    def dont_ask_cb (self, widget, *args):
        if widget.get_active():
            self.prefs['emailer_dont_ask']=True
        else:
            self.prefs['emailer_dont_ask']=False

    def setup_dialog (self, force = False):
        if force or not self.prefs.get('emailer_dont_ask',False):
            d=de.PreferencesDialog(options=self.option_list,
                                   option_label=_("Email Options"),
                                   value_label="",
                                   dont_ask_cb=self.dont_ask_cb,
                                   dont_ask_custom_text=_("Don't ask before sending e-mail."))
            retlist = d.run()
            if retlist:
                for o in retlist:
                    k = o[0]
                    v = o[1]
                    pref = self.options[k][0]
                    self.email_options[pref]=v
                    self.prefs[pref]=v

    def email (self, address=None):
        if address: self.emailaddress=address
        if self.email_options['email_include_body']:
            self.write_email_text()
        if self.email_options['email_include_html']:
            self.write_email_html()
        if self.email_options['email_include_pdf']:
            self.write_email_pdf()
        if not self.email_options['email_include_body'] and not self.email_options['email_include_body']:
            de.show_message(_("E-mail not sent"),
                            sublabel=_("You have not chosen to include the recipe in the body of the message or as an attachment.")
                            )
        else:
            self.send_email()
            

if __name__ == '__main__':
    import gourmet.recipeManager
    rd = gourmet.recipeManager.default_rec_manager()
    rec = rd.fetch_one(rd.recipe_table)
    ed = EmailerDialog([rec],rd,{})
    ed.setup_dialog()
    ed.email()
    #ed.run()
    #e.write_email_text()
    #e.write_email_pdf()
    #e.write_email_html()
    #e.send_email()
    
