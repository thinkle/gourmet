import os, os.path, gobject, re, gtk
from gettext import gettext as _
import tempfile
from gdebug import debug
from OptionParser import options

tmpdir = tempfile.gettempdir()

if options.gourmetdir:
    gourmetdir = options.gourmetdir
    debug("User specified gourmetdir %s"%gourmetdir,0)
else:
    if os.name =='nt':
        gourmetdir = os.path.join(os.path.expanduser('~'),'Application Data','gourmet')
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

# note: this os specific stuff is rather hackish and must be kept in sync with
# changes in setup.py

use_threads = True
#use_threads = False

if os.name == 'posix':
    # grab the proper subdirectory, assuming we're in
    # lib/python/site-packages/gourmet/
    # special case our standard debian install, which puts
    # all the python libraries into /usr/share/gourmet
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
    gladebase=datad
    imagedir=datad


elif os.name == 'nt':
    #datad = os.path.join('Program Files','Gourmet Recipe Manager','data')
    # assume we are in Python\Lib\site-packages\gourmet\
    pybase = os.path.split(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])[0]
    # back up four direcotires and add gourmet\data\
    datad = os.path.join(pybase,'gourmet','data')
    gladebase = datad
    imagedir = datad
    use_threads = False
else:
    print "Gourmet isn't ready for operating system %s"%os.name
    import sys
    sys.exit()


# GRAB EXPLICITLY STATED GLADE/IMAGE/DATA DIRECTORIES FROM OPTIONS
if options.datad:
    datad=options.datad
    gladebase=datad
    imagedir=datad

if options.imaged:
    imagedir=options.imaged

if options.gladed:
    gladebase=options.gladed

# UNCOMMENT BELOW TO TEST
#use_threads=False
import recipeManager
#myprefs=prefs.Prefs()
if recipeManager.db != 'metakit':
    print 'Not using metakit; threads disabled to avoid bugginess.'
    use_threads = False
else:
    print 'Using metakit'
    
if use_threads:
    debug('using GourmetThreads',0)
    import GourmetThreads as gt
else:
    debug('using GourmetFauxThreads',0)    
    import GourmetFauxThreads as gt



REC_ATTRS = [('title',_('Title'),'Entry'),
             ('category',_('Category'),'Combo'),
             ('cuisine',_('Cuisine'),'Combo'),
             ('rating',_('Rating'),'Combo'),
             ('source',_('Source'),'Combo'),
             ('servings',_('Servings'),'Entry'),
             ('preptime',_('Preparation Time'),'Entry'),
             ('cooktime',_('Cooking Time'),'Entry'),
             ]

NAME_TO_ATTR = {_('Instructions'):'instructions',
                _('Notes'):'modifications'
                }

for attr, name, widget in REC_ATTRS:
    NAME_TO_ATTR[name]=attr
    
try:
    import gnomeprint.ui, gnomeprint
    gnome_printing = True
except:
    gnome_printing = False

launchers = [['.*',['gnome-open']],
             ['rtf',['openoffice','abiword','ted','kword']],
             ['txt',['gedit','kedit',]],
             ['html?',['firefox','mozilla',]]
             ]


def is_on_system (app):
    p=os.popen('which %s'%app)
    if p.read():
        return app
    
import dialog_extras

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
                dialog_extras.show_message("Unable to open",sublabel="Failed to launch URL: %s"%url)
        except gobject.GError, err:
            print dir(err)
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
