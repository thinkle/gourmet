#!/bin/env python
#
# setup.py for Gourmet

import imp
import sys
import glob
import os.path
import os
from stat import ST_MTIME

def maybe_intltool (fname):
    '''Check whether the file at fname has been updated since
    intltool-merge was last used on it. If it has, then use
    intltool-merge to update the output file.

    '''
    to_name = fname[:-3]
    if (
        (not os.path.exists(to_name))
        or
        os.stat(to_name)[ST_MTIME] < os.stat(fname)[ST_MTIME]
        ):
        if os.name == 'nt' or os.name == 'dos':
            os.system('perl intltool-merge -d po/ %s %s'%(fname, to_name))
        else:
            os.system('intltool-merge -d po/ %s %s'%(fname, to_name))

for f in ['gourmet.desktop.in'] + \
        glob.glob('gourmet/plugins/*plugin.in')  + \
        glob.glob('gourmet/plugins/*/*plugin.in'):
    maybe_intltool(f)
    
#from distutils.core import setup
from tools.gourmet_distutils import setup
from distutils.command.install_data import install_data

# grab the version from our new "version" module
# first we have to extend our path to include gourmet/
sys.path.append(os.path.join(os.path.split(__file__)[0],'gourmet'))
#print sys.path
try:
    from version import version, website
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
        except RuntimeError:
            print 'Error importing GTK - is there no windowing environment available?'
            print "We're going to ignore this error and live dangerously. Please make"
            print 'sure you have pygtk > 2.3.93 available!'
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
    data_files = []

    ddirs = [
        'data',
        'images',
        'sound',
        'style',
        'ui',
        ]
    for d in ddirs:
        for root, dirs, files in os.walk(d):
            if files:
                files = [os.path.join(root, f) for f in files]
                data_files.append((os.path.join('share','gourmet', root), files))
    print "data_files: ",data_files

    base = 'share'
    locale_base = os.path.join('share','locale')
    # if os.name == 'posix':
    # files in /usr/share/X/ (not gourmet)
    files = [
        (os.path.join(base,'pixmaps'),
         [os.path.join('images','gourmet.png')]
         ),
        (os.path.join(base,'applications'),
         ['gourmet.desktop']
         ),]
    base = os.path.join(base,'gourmet')

    for f in glob.glob(os.path.join('po','*/*/*.mo')):
        pth,fn=os.path.split(f)
        pthfiles = pth.split(os.path.sep)
        pthfiles=pthfiles[1:] # strip off po
        pth = os.path.sep.join(pthfiles)
        #print pth,fn
        pth = os.path.join(locale_base,pth)
        files.append((pth,[f]))           
    files.extend(data_files)
    files.extend([(os.path.join(base,'ui'), glob.glob(os.path.join('ui','*.ui')))])
    files.extend([(base, ['FAQ', 'LICENSE'])])
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
    script = [os.path.join('bin','gourmet')]
    # Run upgrade pre script
    # Importing runs the actual script...
    #import tools.upgrade_pre_script
    #tools.upgrade_pre_script.dump_old_data()

plugins = []

def crawl (base, basename):
    bdir = base
    subdirs = filter(lambda x: x != 'CVS' and os.path.isdir(os.path.join(bdir,x)), os.listdir(bdir))
    for subd in subdirs:
        name = basename + '.' + subd
        plugins.append(name)
        crawl(os.path.join(bdir,subd),name)

crawl('gourmet/plugins', 'gourmet.plugins')

result = setup(
    name = name,
    version = version,
    #windows = [ {'script':os.path.join('bin','gourmet'),
    #             }],
    description = 'Recipe Organizer and Shopping List Generator',
    author = 'Thomas Mills Hinkle',
    author_email = 'Thomas_Hinkle@alumni.brown.edu',
    url = website,
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
    package_data = {'gourmet': ['plugins/*.gourmet-plugin','plugins/*/*.gourmet-plugin','plugins/*/*.ui', 'plugins/*/images/*.png','plugins/*/*/images/*.png']},
    package_dir = {'gourmet' : os.path.join('gourmet')},
    scripts = script,
    cmdclass={'install_data' : my_install_data},
    )

