# A very simple setup script to create an executable.
#
# Run the build process by entering 'setup.py py2exe' or
# 'python setup.py py2exe' in a console prompt.
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them hello.exe and test_wx.exe.


from distutils.core import setup
import py2exe

includes = ["atk", 
        #    "gourmet.importers.html_plugins.allrecipes", 
            "gourmet.importers.html_plugins.html_helpers", 
        #    "gourmet.importers.html_plugins.eating_well",
            "gourmet.importers.html_plugins.epicurious",
        #    "gourmet.importers.html_plugins.recipebookonline",
        #    "gourmet.importers.html_plugins.recipezaar",
        #    "gourmet.importers.html_importer",
        #    "gtk._gtk" 
            ]

dll_excludes = ["libpangowin32-1.0-0.dll",
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
                "libpango-1.0-0.dll"
                ]

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.8.5.12",
    description = "Gourmet Recipe Manager",
    name = "Gourmet Recipe Manager",
    author = "Thomas Mills Hinkle",
    license = "GPL",


    options = {"py2exe": {
                          # create a compressed zip archive
                          "compressed": 0,
                          "optimize": 2,
                          "includes": includes,
                          "dll_excludes": dll_excludes
                        }
                },


    # targets to build
    console = [
        {
            "script": "C:\Python24\Scripts\Gourmet.pyw",
            "dest_base": "Gourmet_debug"
        }
    ],
    

    windows = [
       {
           "script": "C:\Python24\Scripts\Gourmet.pyw",
           "dest_base": "Gourmet"
       }
    ],
    )

