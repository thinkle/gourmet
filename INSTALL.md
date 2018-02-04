Installation
===========
We'll assume you're reading this document because you want to install Gourmet manually. 

 * Please note that for *Windows*, we provide an up-to-date installer at our [Releases](https://github.com/thinkle/gourmet/releases) web page which allows you to install Gourmet much easier than described below. 
 * Also, if you're using a *Linux* or *Unix* distribution, chances are that there is a Gourmet package available in your system's software repository that lets you install Gourmet easily.
 * For *Mac OS X*, you can use [MacPorts](https://www.macports.org/) or [Fink](http://www.finkproject.org/index.php?phpLang=en) which provide up-to-date packages to automatically install Gourmet.
 
If you're still sure about installing Gourmet manually anyway, keep reading.

Required Packages
===============
Linux/Unix
----------
Fortunately for Linux and Unix users, at least most of the software Gourmet requires comes packaged with most Linux (and some Unix) distributions. The table at the bottom of this document lists the dependencies, and the corresponding packages' names for some of the more popular distros.

To install Gourmet from source -- i.e. from the tarball found at our [Releases](https://github.com/thinkle/gourmet/releases) web page -- just uncompress that tarball, cd into the resulting directory, and run `sudo python setup.py install`, which will
install gourmet to your current python environment's default location (i.e. subdirectories of `/usr/local` for most Linux distributions. For information on how to customize these locations, run
`sudo python setup.py --help`).

That should be all you need, and will create an entry in your launcher menu.
Alternatively, you can now run gourmet by issuing

`gourmet`

from the command line.

Gourmet also has command line options, most of which should not be
needed by an average user. Issuing `gourmet --help` will get you help
for those options.

Mac OS X
--------
### Using MacPorts

To build gourmet from source, install the required dependencies as listed in the MacPorts column of the table below by running `sudo port install <dependencies>`. 

Then, get gourmet's source, `cd` to its directory, and run

    sudo /opt/local/bin/python setup.py install
    sudo ln -s /opt/local/Library/Frameworks/Python.framework/Versions/2.7/share/gourmet/ gourmet

You should then be able to launch gourmet by running

    /opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin/gourmet

### Using Fink

The following instructions all assume you have fink installed and that you have a terminal set up with the proper paths to run executables in the fink directories (/sw/bin/, etc.).

To create the fink package, you need a gourmet.info file. As a starting point, you can download the current one from the fink repository at http://pdb.finkproject.org/pdb/package.php/gourmet

You then want to save that file to `/sw/fink/dists/local/main/finkinfo/gourmet.info`.

Now, you can run:

    $ fink validate
    $ fink fetch gourmet
    ...
    $ fink -m --build-as-nobody rebuild gourmet
    ...
    Reading Package Lists... Done
    Building Dependency Tree... Done
    $

Now you can install gourmet and run it to make sure it worked!

    $ fink install gourmet
    ...
    Setting up gourmet (0.15.9-1) ...
    $ gourmet
    No gnome player
    No windows player
    Player is  gourmet.sound.Player
    ...

Further resources:
* http://finkproject.org/doc/packaging/index.php
* http://finkproject.org/doc/quick-start-pkg/index.php

Windows
-------
To run Gourmet from source on Windows takes a bit of doing, since Windows does not come with a lot of development tools by default. So first, you will need to download and install a few open-source development packages. Most of them are just usual *.msi or *.exe installers which should be easy to install; if multiple options are given, make sure to download the one that matches your architecture (32 vs 64 bits) and Python version.

In the more complicated cases, you need to download a .zip, .gz or .tar.gz file, which you will then have to extract.
If you have trouble extracting .gz or .tar.gz files (which may not be supported by e.g. WinZip), get [7-Zip](http://sourceforge.net/projects/sevenzip/) - an excellent open source compression utility that supports multiple formats.
Once extracted, open a command prompt (on Windows Vista and later: with administrator privileges, i.e. by right-clicking on the command prompt icon and picking "Run as Administrator"). Change into the directory you just extracted and run
```
python setup.py install
```

After installing all dependencies, open a (non-administrator) command prompt, cd to the directory to which you extracted (or git-cloned) Gourmet's source code,
and run gourmet by entering
```
python bin/gourmet
```

You might also want to build localization files as described in the CODING file so you can run Gourmet in your language.

Finally, you can freeze Gourmet for deployment by running
```
python setup.py bdist_msi
```
which will create an .msi installer file in the dist/ subdirectory of Gourmet's source code folder.

If you intend to put your installer online for others to download, you should sign it. To that end, you need to have Microsoft's [SignTool.exe](http://msdn.microsoft.com/en-us/library/8s9b9yaz.aspx) program installed (which comes as part of their Windows platform SDKs) and have a code signing certificate.
For instance, polish certification authority certum.eu offers [free code signing certificates](http://www.certum.eu/certum/cert,offer_en_open_source_cs.xml) to open source developers (limited to one year).
To sign your installer, run

```& 'C:\path\to\signtool.exe' sign /f C:\path\to\your\certificate.p12 /p yourpassword /t http://time.certum.pl /d "Gourmet Recipe Manager" '.\dist\Gourmet-x.y.z-win32.msi'```

from the source directory.

Requirements                               |Debian                |MacPorts            |Windows
-------------------------------------------|----------------------|--------------------|---------------
Python 2.7                                 |python                |python27            |http://www.python.org/
PyGTK                                      |python-gtk2           |py27-pygtk          |[all-in-one installer](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/). Make sure to install PyGTK, PyGObject, PyCairo, and intltool.
SQLAlchemy                                 |python-sqlalchemy     |py27-sqlalchemy     |http://www.sqlalchemy.org/download.html
Pillow 2.x (Python Imaging Library Fork)   |python-imaging        |py27-Pillow         |https://pypi.python.org/pypi/Pillow/
elib.intl                                  |python-elib.intl      |py27-elib.intl      |http://github.com/dieterv/elib.intl/zipball/master
*Build Requirements*                       |                      |                    |
setuptools (*Windows only!*)               |                      |                    |
intltool                                   |intltool              |intltool            |*included in PyGTK installer*
python-distutils-extra                     |python-distutils-extra|py27-distutils-extra|https://launchpad.net/python-distutils-extra/
*Extra Requirements*                       |                      |
Python Reportlab (for printing/PDF export) |python-reportlab      |py27-reportlab      |http://www.reportlab.com/ftp/
pypoppler (for printing and PDF export)    |python-poppler        |py27-poppler        |
PyGTKSpell (for the spell checking plugin) |python-gtkspell       |py27-gtkspell       |(N/A)
python-gst0.10 (for sound)                 |python-gst0.10        |py27-gst-python     |*not required*
BeautifulSoup (for the Web import plugin)  |python-beautifulsoup  |py27-beautifulsoup  |http://www.crummy.com/software/BeautifulSoup/#Download
IPython 0.12.1 (interactive shell plugin)  |ipython               |py27-ipython        |https://pypi.python.org/pypi/ipython/0.12.1#downloads
*Windows only*                             |                      |                    |
Perl (needed to run intltool)              |                      |                    |http://strawberryperl.com/
cx_Freeze (only needed to build installer) |                      |                    |http://cx-freeze.sourceforge.net/

