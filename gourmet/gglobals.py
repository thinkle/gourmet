import os, os.path, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import tempfile
from .gdebug import debug
from .OptionParser import args
from .util import windows

tmpdir = tempfile.gettempdir()

if args.gourmetdir:
    gourmetdir = args.gourmetdir
    debug("User specified gourmetdir %s"%gourmetdir,0)
else:
    if os.name =='nt':
        # Under Windows, we cannot unfortunately just use os.environ, see
        # http://stackoverflow.com/questions/2608200/problems-with-umlauts-in-python-appdata-environvent-variable
        # We might drop this workaround with Python 3 (all strings are unicode)
        # and/or GTK+ 3 (use Glib.get_home_dir()).
        APPDATA = windows.getenv('APPDATA').decode('utf-8')
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
        print("Unable to create gourmet directory.")
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
from . import settings
uibase = os.path.join(settings.ui_base)
lib_dir = os.path.join(settings.lib_dir)

# To have strings from .ui files (Gtk.Builder) translated on all platforms,
# we need the following module to enable localization on all platforms.
# FIXME: `elib.entl` is no longer maintained and is no available via pip
try:
    import elib.intl
    elib.intl.install('gourmet', settings.locale_base)
except ImportError:
    print('elib.intl failed to load.')
    print('IF YOU HAVE TROUBLE WITH TRANSLATIONS, MAKE SURE YOU HAVE THIS LIBRARY INSTALLED.')
from gettext import gettext as _

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

REC_ATTRS = [('title',_('Title'),'Entry'),
             ('category',_('Category'),'Combo'),
             ('cuisine',_('Cuisine'),'Combo'),
             ('rating',_('Rating'),'Entry'),
             ('source',_('Source'),'Combo'),
             ('link',_('Website'),'Entry'),
             ('yields',_('Yield'),'Entry'),
             ('yield_unit',_('Yield Unit'),'Combo'),
             ('preptime',_('Preparation Time'),'Entry'),
             ('cooktime',_('Cooking Time'),'Entry'),
             ]

INT_REC_ATTRS = ['rating','preptime','cooktime']
FLOAT_REC_ATTRS = ['yields']
TEXT_ATTR_DIC = {'instructions':_('Instructions'),
                 'modifications':_('Notes'),
                 }

REC_ATTR_DIC={}
NAME_TO_ATTR = {_('Instructions'):'instructions',
                _('Notes'):'modifications',
                _('Modifications'):'modifications',
                }

DEFAULT_ATTR_ORDER = ['title',
                      #'servings',
                      'yields',
                      'cooktime',
                      'preptime',
                      'category',
                      'cuisine',
                      'rating',
                      'source',
                      'link',
                      ]

DEFAULT_TEXT_ATTR_ORDER = ['instructions',
                           'modifications',]

def build_rec_attr_dic ():
    for attr, name, widget in REC_ATTRS:
        REC_ATTR_DIC[attr]=name
        NAME_TO_ATTR[name]=attr

build_rec_attr_dic()

DEFAULT_HIDDEN_COLUMNS = [REC_ATTR_DIC[attr] for attr in
                          ['link','yields','yield_unit','preptime','cooktime']
                          ]

from .gtk_extras import dialog_extras

def launch_url (url, ext=""):
    if os.name == 'nt':
        os.startfile(url)
    elif os.name == 'posix':
        try:
            Gtk.show_uri(Gdk.Screen(),url,0)
        except GObject.GError as err:
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
icon_factory = Gtk.IconFactory()

def add_icon (file_name, stock_id, label=None, modifier=0, keyval=0):
    pb = GdkPixbuf.Pixbuf.new_from_file(file_name)
    iconset = Gtk.IconSet(pb)
    icon_factory.add(stock_id,iconset)
    icon_factory.add_default()
    # TODO: fix adding icons
    return
    Gtk.stock_add([(stock_id,
                    label,
                    modifier,
                    keyval,
                    "")])

for filename,stock_id,label,modifier,keyval in [
    ('AddToShoppingList.png','add-to-shopping-list',_('Add to _Shopping List'),Gdk.ModifierType.CONTROL_MASK,Gdk.keyval_from_name('l')),
    ('reccard.png','recipe-card',None,0,0),
    ('reccard_edit.png','edit-recipe-card',None,0,0),
    ]:
    add_icon(os.path.join(imagedir,filename),stock_id,label,modifier,keyval)
