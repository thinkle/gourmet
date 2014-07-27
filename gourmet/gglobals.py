import os, os.path, gobject, re, gtk
import tempfile
from gdebug import debug
from OptionParser import args
from models.recipe import REC_ATTRS, INT_REC_ATTRS, FLOAT_REC_ATTRS, \
                          TEXT_ATTR_DIC, DEFAULT_ATTR_ORDER, REC_ATTR_DIC, \
                          NAME_TO_ATTR, DEFAULT_TEXT_ATTR_ORDER

tmpdir = tempfile.gettempdir()

if args.gourmetdir:
    gourmetdir = args.gourmetdir
    debug("User specified gourmetdir %s"%gourmetdir,0)
else:
    if os.name =='nt':
        APPDATA = os.environ.get('APPDATA',None)
        gourmetdir = os.path.join(APPDATA,'gourmet')
    else:
        gourmetdir = os.path.join(os.path.expanduser('~'),'.gourmet')
try:
    if not os.path.exists(gourmetdir):
        debug('Creating %s'%gourmetdir,0)
        os.makedirs(gourmetdir)
except OSError:
    try:
        debug("Unable to create standard config directory in home directory. Looking for .gourmet in working directory instead.",0)
        gourmetdir = '.gourmet'
        if not os.path.exists(gourmetdir):
            debug("Creating .gourmet in working directory",0)
            os.makedirs(gourmetdir)
    except OSError:
        print "Unable to create gourmet directory."
        raise
        import sys
        sys.exit()


if not os.access(gourmetdir,os.W_OK):
    debug('Cannot write to configuration directory, %s'%gourmetdir,-1)
    import sys
    sys.exit()        
    
debug('gourmetdir=%s'%gourmetdir,2)

use_threads = args.threads
# Uncomment the below to test FauxThreads
#use_threads = False

# note: this stuff must be kept in sync with changes in setup.py
import settings
uibase = os.path.join(settings.ui_base)
lib_dir = os.path.join(settings.lib_dir,'gourmet')

# To have strings from .ui files (gtk.Builder) translated on all platforms,
# we need the following module to enable localization on all platforms.
try:
    import elib.intl
    elib.intl.install('gourmet', settings.locale_base)
except ImportError:
    print 'elib.intl failed to load.'
    print 'IF YOU HAVE TROUBLE WITH TRANSLATIONS, MAKE SURE YOU HAVE THIS LIBRARY INSTALLED.'
    import gettext
    gettext.install('gourmet', settings.locale_base, unicode=True)

data_dir = settings.data_dir
imagedir = os.path.join(settings.data_dir,'images')
style_dir = os.path.join(settings.data_dir,'style')

icondir = os.path.join(settings.icon_base,"48x48","apps")
doc_base = settings.doc_base
plugin_base = settings.plugin_base

# GRAB PLUGIN DIR FOR HTML IMPORT
if args.html_plugin_dir:
    html_plugin_dir = args.html_plugin_dir
else:
    html_plugin_dir = os.path.join(gourmetdir,'html_plugins')
    if not os.path.exists(html_plugin_dir):
        os.makedirs(html_plugin_dir)
        template_file = os.path.join(settings.data_dir,'RULES_TEMPLATE')
        if os.path.exists(template_file):
            import shutil
            shutil.copy(template_file,
                        os.path.join(html_plugin_dir,'RULES_TEMPLATE')
                        )

DEFAULT_HIDDEN_COLUMNS = [REC_ATTR_DIC[attr] for attr in
                          ['link','yields','yield_unit','preptime','cooktime']
                          ]
    
from gtk_extras import dialog_extras

def launch_url (url, ext=""):
    if os.name == 'nt':
        os.startfile(url)
    elif os.name == 'posix':
        try:
            gtk.show_uri(gtk.gdk.Screen(),url,0L)
        except gobject.GError, err:
            #print dir(err)
            label = _('Unable to open URL')
            for reg, msg in [('mailto:',_('Unable to launch mail reader.')),
                             ('http:',_('Unable to open website.')),
                             ('file:',_('Unable to open file.'))]:
                if re.match(reg,url.lower()): label = msg
            dialog_extras.show_message(
                label=label,
                sublabel=err.message,
                expander=[_('_Details'),
                          _("There was an error launching the url: %s"%url)]
                )

# Set up custom STOCK items and ICONS!
icon_factory = gtk.IconFactory()
    
def add_icon (file_name, stock_id, label=None, modifier=0, keyval=0):
    pb = gtk.gdk.pixbuf_new_from_file(file_name)
    iconset = gtk.IconSet(pb)
    icon_factory.add(stock_id,iconset)
    icon_factory.add_default()
    gtk.stock_add([(stock_id,
                    label,
                    modifier,
                    keyval,
                    "")])

for filename,stock_id,label,modifier,keyval in [    
    ('AddToShoppingList.png','add-to-shopping-list',_('Add to _Shopping List'),gtk.gdk.CONTROL_MASK,gtk.gdk.keyval_from_name('l')),
    ('reccard.png','recipe-card',None,0,0),
    ('reccard_edit.png','edit-recipe-card',None,0,0),    
    ]:
    add_icon(os.path.join(imagedir,filename),stock_id,label,modifier,keyval)


import models
models.initialize_connection(os.path.join(gourmetdir,'recipes.db'), args.db_url)
