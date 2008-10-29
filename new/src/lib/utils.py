import gtk, os, gobject, re

def is_on_system (app):
    p = os.popen('which %s'%app)
    if p.read():
        return app

from gourmet.ui import dialogs

def launch_url (url, ext=""):
    if os.name == 'nt':
        os.startfile(url)
    elif os.name == 'posix':
        try:
            import gnome
            gnome.url_show(url)
        except ImportError:
            print 'gnome libraries not available, trying builtins'
            if not ext: ext=os.path.splitext(url)
            for regexp,l in launchers:
                if regexp.match('\.?%s'%regexp, ext):
                    if is_on_system(app):
                        os.popen(app + " " + url)
                        return
            # if that fails...
            print 'builtins failing, using python webbrowser functions'
            try:
                import webbrowser
                webbrowser.open(url)
            except ImportError:
                dialogs.show_message("Unable to open",sublabel="Failed to launch URL: %s"%url)
        except gobject.GError, err:
            #print dir(err)
            label = _('Unable to open URL')
            for reg, msg in [('mailto:',_('Unable to launch mail reader.')),
                             ('http:',_('Unable to open website.')),
                             ('file:',_('Unable to open file.'))]:
                if re.match(reg,url.lower()): label = msg
            dialogs.show_message(
                label=label,
                sublabel=err.message,
                expander=[_('_Details'),
                          _("There was an error launching the url: %s"%url)]
                )
                
def about_url_cb (dialog, url):
    launch_url(url)
    
gtk.about_dialog_set_url_hook(about_url_cb)
