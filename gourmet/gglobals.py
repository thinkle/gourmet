#try:
#    import gnomevfs
#    import AASOIUQWE
#    # Okay, actually gnomevfs sucks so we'll put this off for
#    # now. Among other problems, gnomevfs Handlers don't really behave
#    # like proper file objects.
#except ImportError:
vfs_available = False
open = open
import os.path; os
exists = os.path.exists
makedirs = os.makedirs
#else:
#    vfs_available = True
#    def exists (fn):
#        return gnomevfs.exists(fn)
#    def open (fn, mode='r'):
#        if mode and mode[0]=='w':
#            if not exists(fn):
#                return gnomevfs.create(fn,gnomevfs.OPEN_WRITE)
#            else:
#                return gnomevfs.open(fn,gnomevfs.OPEN_WRITE)
#        else:
#            if mode != 'r':
#                print 'WARNING, treating open mode %s as gnomevfs OPEN_READ'%mode
#            return gnomevfs.open(fn,gnomevfs.OPEN_READ)
#    def makedirs (path):
#        gnomevfs.make_directory(path,gnomevfs.PERM_USER_ALL)
    
import os, os.path, gobject, re, gtk
import tempfile
from gdebug import debug
from OptionParser import options

tmpdir = tempfile.gettempdir()
BUG_URL = "http://sourceforge.net/tracker/?group_id=108118&atid=649652"

CRC_AVAILABLE = hasattr(gtk,'CellRendererCombo') # is this wonderful feature available?

if options.gourmetdir:
    gourmetdir = options.gourmetdir
    debug("User specified gourmetdir %s"%gourmetdir,0)
else:
    if os.name =='nt':
        # default to APPDATA, if available. If not, use ~/Application Data/gourmet/
        # Try APPDATA environmental variable, falling back to whatever python does with ~
        APPDATA = os.environ.get('APPDATA',None)
        if not APPDATA:
            # On win98, reading the registry should give us the proper dir...
            # (this code is from Dan F.)
            import _winreg
            try:
                x=_winreg.ConnectRegistry(None,_winreg.HKEY_CURRENT_USER)
                y= _winreg.OpenKey(
                    x,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
                    )
                #we dont need to use datatype, but it returns it
                APPDATA,datatype=_winreg.QueryValueEx(y,
                                                      'Personal')
                _winreg.CloseKey(y)
            except EnvironmentError:
                # maybe key doesn't exist... anyway, we have other fallback...
                pass
        # If we still haven't found where to put things, we'll try
        # some more environmental variables and fallback to C:\My
        # Documents\ if necessary... don't you love windows?
        if not APPDATA:
            # More attempts to figure out where to put things if our
            # previous efforts have failed us
            VARS_TO_TRY = ['USERPROFILE',
                           'HOMEPATH',]            
            for v in VARS_TO_TRY:
                if os.environ.has_key(v):
                    APPDATA = os.environ[v]
                    break
            if not APPDATA:
                WINDIR = os.environ.get('windir',None)
                if WINDIR:
                    FALLBACK_DRIVE = os.path.split(WINDIR)[0]
                else:
                    FALLBACK_DRIVE = "C:"
                APPDATA = os.path.join(FALLBACK_DRIVE,'My Documents')
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

use_threads = options.threads
# Uncomment the below to test FauxThreads
#use_threads = False

# note: this stuff must be kept in sync with changes in setup.py
import settings
base = settings.base

# To have strings from .ui files (gtk.Builder) translated on all platforms,
# we need the following module to enable localization on all platforms.
try:
    import elib.intl
    elib.intl.install('gourmet', settings.locale_base)
except ImportError:
    print 'elib.intl failed to load.'
    print 'IF YOU HAVE TROUBLE WITH TRANSLATIONS, MAKE SURE YOU HAVE THIS LIBRARY INSTALLED.'
from gettext import gettext as _

datad = os.path.join(base,'data')
uibase = os.path.join(base,'ui')
imagedir = os.path.join(base,'images')

# GRAB PLUGIN DIR FOR HTML IMPORT
if options.html_plugin_dir:
    html_plugin_dir = options.html_plugin_dir
else:
    html_plugin_dir = os.path.join(gourmetdir,'html_plugins')
    if not os.path.exists(html_plugin_dir):
        os.makedirs(html_plugin_dir)
        template_file = os.path.join(datad,'RULES_TEMPLATE')
        if os.path.exists(template_file):
            import shutil
            shutil.copy(template_file,
                        os.path.join(html_plugin_dir,'RULES_TEMPLATE')
                        )

#import OptionParser
#use_threads = False
#if use_threads:
#    debug('using GourmetThreads',0)
#    import GourmetThreads as gt
#else:
#    debug('using GourmetFauxThreads',0)    
#    import GourmetFauxThreads as gt

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

launchers = [['.*',['xdg-open']],
             ['rtf',['openoffice','abiword','ted','kword']],
             ['txt',['gedit','kedit',]],
             ['html?',['firefox','mozilla',]]
             ]


def is_on_system (app):
    p=os.popen('which %s'%app)
    if p.read():
        return app
    
from gtk_extras import dialog_extras

def launch_url (url, ext=""):
    if os.name == 'nt':
        os.startfile(url)
    elif os.name == 'posix':
        try:
            gtk.show_uri(gtk.gdk.Screen(),url,0L)
        except ImportError:
            print 'gtk libraries not available, trying builtins'
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
                dialog_extras.show_message("Unable to open",sublabel="Failed to launch URL: %s"%url)
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

empty_model = gtk.ListStore(str)

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
    ('gourmet.png','gourmet-logo',None,0,0),
    ('reccard.png','recipe-card',None,0,0),
    ('reccard_edit.png','edit-recipe-card',None,0,0),    
    ]:
    add_icon(os.path.join(imagedir,filename),stock_id,label,modifier,keyval)
