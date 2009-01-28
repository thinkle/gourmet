#!/bin/env python
#
# setup.py for Gourmet

import imp
import sys
import glob
import os.path
import os

for desktop_file in ['gourmet.desktop.in'] + glob.glob('src/lib/plugins/*plugin.in')  + glob.glob('src/lib/plugins/*/*plugin.in'):
    #print 'intltool-merge -d i18n/ %s %s'%(desktop_file,
    #                                           desktop_file[:-3])
    os.system('intltool-merge -d i18n/ %s %s'%(desktop_file,
                                               desktop_file[:-3])
              )

#from distutils.core import setup
from tools.gourmet_distutils import setup
from distutils.command.install_data import install_data

# grab the version from our new "version" module
# first we have to extend our path to include src/lib/
sys.path.append(os.path.join(os.path.split(__file__)[0],'src','lib'))
#print sys.path
try:
    from version import version
except:
    #print 'Version info may be out of date.'
    version = "0.11.0"

name= 'gourmet'

if sys.version < '2.2':
    sys.exit('Error: Python-2.2 or newer is required. Current version:\n %s'
             % sys.version)

def modules_check():
    '''Check if necessary modules is installed.
    The function is executed by distutils (by the install command).'''
    try:
        try:
            import gtk
            import gtk.glade
        except RuntimeError:
            print 'Error importing GTK - is there no windowing environment available?'
            print "We're going to ignore this error and live dangerously. Please make"
            print 'sure you have pygtk > 2.3.93 and gtk.glade available!'
    except ImportError:
        raise
    mod_list = [#'metakit',
        'Image',
        'reportlab',
        ('pysqlite2','sqlite3')
        ]
    ok = 1
    for m in mod_list:
        if type(m)==tuple:
            have_mod = False
            for mod in m:
                try:
                    exec('import %s'%mod)
                except ImportError:
                    pass
                else:
                    have_mod = True
            if not have_mod:
                ok = False
                print 'Error: %s is Python module is required to install %s'%(
                    ' or '.join(m), name.title()
                    )
        else:
            try:
                exec('import %s' % m)
            except ImportError:
                ok = False
                print 'Error: %s Python module is required to install %s' \
                  % (m, name.title())
    recommended_mod_list = ['PyRTF']
    for m in recommended_mod_list:
        try:
            exec('import %s' % m)
        except ImportError:
            print '%s Python module is recommended for use with %s' \
                  % (m, name.title())
    if not ok:
        sys.exit(1)

def data_files():
    '''Build list of data files to be installed'''
    images = glob.glob(os.path.join('images','*.png'))
    icons = glob.glob(os.path.join('images','*.ico'))
    style = glob.glob(os.path.join('style','*.css'))
    glade = glob.glob(os.path.join('glade','*.glade'))
    sounds = glob.glob(os.path.join('data','*.wav'))
    i18n = glob.glob(os.path.join('i18n','*/*/*.mo'))
    txts = glob.glob(os.path.join('data','*.txt'))
    dtds = glob.glob(os.path.join('data','*.dtd'))        
    images.extend(icons)
    images.extend(style)
    images.extend(glade)
    images.extend(sounds)
    images.extend(txts)
    images.extend(dtds)    
    #print "data_files: ",images,style
    # Note that this os specific stuff must be kept in sync with gglobals.py
    if os.name == 'nt' or os.name == 'dos':
        base = 'gourmet'
        i18n_base = os.path.join(base,'i18n')
        files = [(os.path.join(base),[os.path.join('src','gourmet')])]
        base = os.path.join(base,'data')
    else:
        # elif os.name == posix
        base = 'share'
        i18n_base = os.path.join('share','locale')
        # files in /usr/share/X/ (not gourmet)
        files = [
            (os.path.join(base,'pixmaps'),
             [os.path.join('images','recbox.png')]
             ),
            (os.path.join(base,'applications'),
             ['gourmet.desktop']
             ),]
        base = os.path.join(base,'gourmet')

    for f in i18n:
        pth,fn=os.path.split(f)
        pthfiles = pth.split(os.path.sep)
        pthfiles=pthfiles[1:] # strip off i18n
        pth = os.path.sep.join(pthfiles)
        #print pth,fn
        pth = os.path.join(i18n_base,pth)
        files.append((pth,[f]))           
    files.extend([(base, images + ['FAQ'])])
    #print 'DATA FILES:',files
    return files

class my_install_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'))
        install_data.finalize_options(self)
        #print 'install_data has: ',dir(install_data)

if os.name == 'nt':
    script = [os.path.join('windows','Gourmet.pyw'),
              os.path.join('windows','GourmetDebug.pyw')]
else:
    script = [os.path.join('src','gourmet')]
    # Run upgrade pre script
    # Importing runs the actual script...
    #import tools.upgrade_pre_script
    #tools.upgrade_pre_script.dump_old_data()

plugins = []
import os, os.path

def crawl (base, basename):
    bdir = base
    subdirs = filter(lambda x: x != 'CVS' and os.path.isdir(os.path.join(bdir,x)), os.listdir(bdir))
    for subd in subdirs:
        name = basename + '.' + subd
        plugins.append(name)
        crawl(os.path.join(bdir,subd),name)

crawl('src/lib/plugins', 'gourmet.plugins')

result = setup(
    name = name,
    version = version,
    #windows = [ {'script':os.path.join('src','gourmet'),
    #             }],
    description = 'Recipe Organizer and Shopping List Generator for Gnome',
    author = 'Thomas Mills Hinkle',
    author_email = 'Thomas_Hinkle@alumni.brown.edu',
    url = 'http://grecipe-manager.sourceforge.net',
    license = 'GPL',
    data_files = data_files(),
    packages = ['gourmet',
                'gourmet.backends',
                'gourmet.defaults',
                'gourmet.gtk_extras',
                'gourmet.importers',
                'gourmet.exporters',
                'gourmet.legacy_db',
                'gourmet.legacy_db.db_085',
                'gourmet.legacy_db.db_09',
                'gourmet.plugins',
                ] + plugins,
    package_data = {'gourmet': ['plugins/*.gourmet-plugin','plugins/*/*.gourmet-plugin','plugins/*.glade','plugins/*/*.glade', 'plugins/*/images/*.png','plugins/*/*/images/*.png']},
    package_dir = {'gourmet' : os.path.join('src','lib')},
    scripts = script,
    cmdclass={'install_data' : my_install_data},
    )

