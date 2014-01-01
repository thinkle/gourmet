Installation
===========
We'll assume you're reading this document because you want to install Gourmet manually. Please note that if you're using a Linux distribution, chances are that they're is a Gourmet package available in your system's software repository that lets you install Gourmet much easier than described below. For Windows, our installer (found at https://launchpad.net/gourmet/+download) is currently also outdated (version 0.15.4), so if you'd like to try out the up-to-date version without having to wait for us to release a new installer, also follow these steps.

Required Packages
===============
Linux
-----
Fortunately for Linux users, at least most of the software Gourmet requires comes packaged with most Linux distributions. The table at the bottom of this document lists the dependencies, and the corresponding packages' names for some of the more popular distros.

Windows
------
To run Gourmet from source on Windows takes a bit of doing, since Windows does not come with a lot of development tools by default. So first, you will need to download and install a few open-source development packages. Most of them are just usual *.msi or *.exe installers which should be easy to install; if multiple options are given, make sure to download the one that matches your architecture (32 vs 64 bits) and Python version.

In the more complicated cases, you need to download a .zip, .gz or .tar.gz file, which you will then have to extract.
If you have trouble extracting .gz or .tar.gz files (which may not be supported by e.g. WinZip), get [7-Zip](http://sourceforge.net/projects/sevenzip/) - an excellent open source compression utility that supports multiple formats.
Once extracted, open a command prompt (on Windows Vista and later: with administrator privileges, i.e. by right-clicking on the command prompt icon and picking "Run as Administrator"). Change into the directory you just extracted and run
```
python setup.py install
```

Requirements                               |Debian                |MacPorts          |Windows
-------------------------------------------|----------------------|------------------|---------------
Python 2.7                                 |python                |python27          |http://www.python.org/
PyGTK                                      |python-gtk2           |py27-gtk          |[all-in-one installer](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/). Make sure to install PyGTK, PyGObject, PyCairo, and intltool.
SQLAlchemy                                 |python-sqlalchemy     |py27-sqlalchemy   |http://www.sqlalchemy.org/download.html
Python Imaging Library (PIL)               |python-imaging        |py27-pil          |http://www.pythonware.com/products/pil/index.htm
elib.intl                                  |python-elib.intl      |*manually*        |http://github.com/dieterv/elib.intl/zipball/master
*Build Requirements*                       |                      |                  |
setuptools (*Windows only!*)               |                      |                  |
intltool                                   |intltool              |intltool          |*included in PyGTK installer*
python-distutils-extra                     |python-distutils-extra|*manually*        |https://launchpad.net/python-distutils-extra/
*Extra Requirements*                       |                      |
Python Reportlab (for printing/PDF export) |python-reportlab      |py27-reportlab    |
pypoppler (for printing and PDF export)    |python-poppler        |*manually*        | 
PyGTKSpell (for the spell checking plugin) |python-gtkspell       |py27-gtkspell     |(N/A)
python-gst0.10 (for sound)                 |python-gst0.10        |py27-gst-python   |*not required*
BeautifulSoup (for the Web import plugin)  |python-beautifulsoup  |py27-beautifulsoup|http://www.crummy.com/software/BeautifulSoup/#Download
IPython (for the interactive shell plugin) |ipython               |py27-ipython      |http://ipython.org/download.html
*Windows only*                             |                      |                  |
Perl (needed to run intltool)              |                      |                  |http://strawberryperl.com/

