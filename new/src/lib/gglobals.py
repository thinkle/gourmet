import os
import tempfile
import gettext
from gettext import gettext as _

from gourmet.gdebug import debug
from gourmet.options import options

copyright = _("Copyright (c) 2004-2006 Thomas M. Hinkle. GNU GPL")
description = _("Gourmet Recipe Manager is an application to store, organize and search recipes.")
authors = ["Thomas M. Hinkle <Thomas_Hinkle@alumni.brown.edu>",
           _("Roland Duhaime (Windows porting assistance)"),
           _("Daniel Folkinshteyn <nanotube@gmail.com> (Windows installer)"),
           _("Richard Ferguson (improvements to Unit Converter interface)"),
           _("R.S. Born (improvements to Mealmaster export)"),
           _("ixat <ixat.deviantart.com> (logo and splash screen)"),
           _("Yula Zubritsky (nutrition and add-to-shopping list icons)"),
           _("Simon Darlington <simon.darlington@gmx.net> (improvements to internationalization, assorted bugfixes)"),
           ]
uidir = ""
tmpdir = tempfile.gettempdir()
BUG_URL = "http://sourceforge.net/tracker/?group_id=108118&atid=649652"

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
                APPDATA,datatype = _winreg.QueryValueEx(y, 'Personal')
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
                           'HOMEPATH',
                           'HOME']            
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

#use_threads = options.threads
# Uncomment the below to test FauxThreads
use_threads = True

# note: this os specific stuff is rather hackish and must be kept in sync with
# changes in setup.py

if os.name == 'posix':
    # grab the proper subdirectory, assuming we're in
    # lib/python/site-packages/gourmet/
    # special case our standard debian install, which puts
    # all the python libraries into /usr/share/gourmet
    __file__ = os.path.realpath(__file__)
    if __file__.find('src/lib/')>-1: # Facilitate testing from src/ dir...
        base = os.path.split(
            os.path.split(
            os.path.split(__file__)[0] #lib/
            )[0] #src/
            )[0] #./
        datad = os.path.join(base,'data')
        usr = '/usr'
    else:
        if __file__.find('/usr/share/gourmet')==0:
            usr='/usr'
        else:
            usr=os.path.split(os.path.split(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])[0])[0]
        # add share/gourmet
        # this assumes the user only specified a general build
        # prefix. If they specified data and lib prefixes, we're
        # screwed. See the following email for details:
        # http://mail.python.org/pipermail/python-list/2004-May/220700.html
        datad=os.path.join(usr,'share','gourmet')
    
    gladebase = os.path.join(datad,'glade')
    imagedir = os.path.join(datad,'images')

    import glob
    locale_dirs = [
        os.path.join(os.path.sep,'usr','share','locale'),
        os.path.join(os.path.sep,'usr','local','share','locale'),
        'locale',
        os.path.join(os.path.sep,'opt','locale')
        ]
    DIR = None
    for l in locale_dirs:
        if glob.glob(os.path.join(l,'*','*','gourmet.mo')):
            DIR = l
            break
elif os.name == 'nt': 
    #datad = os.path.join('Program Files','Gourmet Recipe Manager','data')
    # We're going to look in a number of places, starting with our current location
    if os.path.exists('app.glade'):
        print "we're in the data directory"
        datad = ''
    elif os.path.exists(os.path.join('data','app.glade')):
        print "data directory = data"
        datad = 'data'
    elif os.path.exists(os.path.join('..','data','app.glade')):
        print 'data directory = ..\data\  '
        datad = os.path.join('..','data')
    else:
        pybase = os.path.split(__file__)[0]
        if os.path.exists(os.path.join(pybase,'app.glade')):
            print 'found data in ',pybase
            datad = pybase
        elif os.path.exists(os.path.join(pybase,'data','app.glade')):
            # look in a "data" directory directly above the directory we are in
            print 'found data in ',pybase,'/data'
            datad = os.path.join(pybase,'data')
        else: # otherwise, backup a directory and look there...
            pybase = os.path.split(pybase)[0]
            if os.path.exists(os.path.join(pybase,'data','app.glade')):
                print 'found data in ',pybase,'\data'
                datad = os.path.join(pybase,'data')
            else:
                # assume we are in Python\Lib\site-packages\gourmet\
                # back up four direcotires and add gourmet\data\
                print "Couldn't find data... I hope it's in ../../../../gourmet/data/"
                pybase = os.path.split(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])[0]
                datad = os.path.join(pybase,'gourmet','data')
    # at this point, we'd better have a data directory...
    gladebase = os.path.join(datad,'glade')
    uidir = os.path.join(datad,'ui')
    imagedir = os.path.join(datad,'images')
    use_threads = False
    DIR = os.path.join(datad,'i18n')
    print "DATAD = ",datad
else:
    print "Gourmet isn't ready for operating system %s"%os.name
    import sys
    sys.exit()
    
# GETTEXT SETUP

gettext.bindtextdomain('gourmet',DIR)
gettext.textdomain('gourmet')
gettext.install('gourmet',DIR,unicode=1)

# GRAB EXPLICITLY STATED GLADE/IMAGE/DATA DIRECTORIES FROM OPTIONS
if options.datad:
    datad=options.datad
    gladebase = os.path.join(datad,'glade')
    imagedir = os.path.join(datad,'images')
    uidir = os.path.join(datad,'ui')

if options.imaged:
    imagedir=options.imaged

if options.gladed:
    gladebase=options.gladed

HELP_FILE = os.path.join(datad,'FAQ')

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

import locale, os
try:
    if os.name == 'posix':
        locale.setlocale(locale.LC_ALL,'')

    # Windows locales are named differently, e.g. German_Austria instead of de_AT
    # Fortunately, we can find the POSIX-like type using a different method
    # After that, we set the LC_ALL environment variable for use with gettext.
    elif os.name == 'nt': 
        import win32api
        locid = win32api.GetUserDefaultLangID()
        loc = locale.windows_locale[locid]
        os.environ["LC_ALL"] = loc

except locale.Error:
    print 'Unable to properly set locale %s.%s'%(locale.getdefaultlocale())

dbargs = {}
dbargs['file'] = os.path.join(gourmetdir,'recipes.db')

import gourmet.threads as gt
