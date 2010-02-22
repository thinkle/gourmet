# A very simple setup script to create an executable.
#
# Run the build process by entering 'setup_win.py py2exe' or
# 'python setup_win.py py2exe' in a console prompt.
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them hello.exe and test_wx.exe.


from distutils.core import setup
import py2exe

#do the following imports to get the version number
import sys, os, glob
sys.path.append(os.path.join('.', 'src', 'lib'))
import version

includes = ["atk",
            "gourmet.backends.*",
            "gourmet.defaults.*",
            "gourmet.defaults",
            "gourmet.exporters.*",
            "gourmet.gtk_extras.*",
            "gourmet.importers.*",
            "tarfile",
            ]

dll_excludes = ["libpangocairo-1.0-0.dll",
                "libpangowin32-1.0-0.dll",
                "libcairo-2.dll","libfontconfig-1.dll",
                "libpango-1.0-0.dll",
                "libpangoft2-1.0-0.dll",
                "libgtk-win32-2.0-0.dll",
                "iconv.dll",
                "libglib-2.0-0.dll",
                "intl.dll",
                "libatk-1.0-0.dll",
                "libgdk-win32-2.0-0.dll",
                "libgobject-2.0-0.dll",
                "libxml2.dll",
                "libgmodule-2.0-0.dll",
                "libgthread-2.0-0.dll",
                "libgdk_pixbuf-2.0-0.dll",
                "zlib1.dll",
                "libglade-2.0-0.dll",
                "libpango-1.0-0.dll",
                # see http://stackoverflow.com/questions/1979486/py2exe-win32api-pyc-importerror-dll-load-failed
                "mswsock.dll",
                "powrprof.dll"
                ]

packages = ["xml.dom","cairo","pangocairo","sqlalchemy",
            "reportlab", # for PDF and Printing export
            #"enchant", # for the spellcheck plugin; crashes gourmet
            #"gtkspell", # for the spellcheck plugin; cannot find libenchant.dll
            #"IPython", # for the python shell plugin; crashes gourmet
            "PIL.ImageDraw" # for the browse_recipes plugin; PIL alone crashes gourmet
            ]

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = version.version,
    description = "Recipe Organizer and Shopping List Generator for Gnome",
    name = "Gourmet Recipe Manager",
    author = "Thomas Mills Hinkle",
    author_email = 'Thomas_Hinkle@alumni.brown.edu',
    url = 'http://grecipe-manager.sourceforge.net',
    license = "GPL",


    options = {"py2exe": {
                          # create a compressed zip archive
                          "compressed": 1,
                          "optimize": 2,
                          "bundle_files": 1,
                          "dist_dir": os.path.join(sys.exec_prefix, 'dist'),
#choose another target for the dist dir instead of ./dist.
                          "includes": includes,
                          "dll_excludes": dll_excludes,
                          "packages" : packages
                        }
                },


    # targets to build
    console = [
        {
            "script": os.path.join(sys.exec_prefix, 'Scripts','GourmetDebug.pyw'),
            "dest_base": "Gourmet_debug"
        }
    ],

    windows = [
       {
           "script": os.path.join(sys.exec_prefix, 'Scripts','Gourmet.pyw'),
           "dest_base": "Gourmet"
       }
    ],
    
    # Maybe some time in the fututre we can use the following instead of including
    # plugin files via NSIS - dito for data and i18n dirs. But that will need some
    # recursive magic, and as I'm lazy, I'll stick with NSIS for the job for now. --Bernhard
    #data_files=[ ("data/plugins",glob.glob(os.path.join(sys.exec_prefix,"Lib/site-packages/gourmet/plugins/*.gourmet-plugin")))]
    
    #data_files = enchant.utils.win32_data_files() #required for enchant
    
    #data_files = [('.', "c:/windows/system32/msvcp71.dll")] #probably needed for xp
    )

