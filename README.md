Gourmet Recipe Manager
===================
Try it. It's good!
----------------

Windows Version Warning
=======================

**Note that this is an alpha version!**

While the Windows version is basically identical to the Linux version, 
it has not been tested as thouroughly. Also, as some of the components Gourmet relies on
are not available for Windows, some features (mainly plugins) are not (yet) available.
Specifically, the

* Printing & PDF Export,
* Spell Checking, and
* Python Shell 

plugins are currently not working.

Furthermore, there seem to be some errors related to the

* Nutritional Information and
* Unit Display Preferences
plugins, in particular when deactivating them again, and to the
* Browse Recipes plugin.

We're currently working on resolving these issues.
If you experience any other issues, please report them at Gourmet's bug tracking system 
at https://github.com/thinkle/gourmet/issues -- by doing so, you can help us improve Gourmet!

Introduction
============

Gourmet Recipe Manager is a manager, editor, and organizer for
recipes. It has a plugin architecture which allows you to enable
extensions to Gourmet's base functionality. For example, there is a
nutritional plugin that allows Gourmet to help you calculate
nutritional information for any recipe. There are also a wide variety
of import and export plugins that let Gourmet read and write recipes
in various formats.

This program aspires to meet the GNOME Human Interface
Guidelines. Please let me know if you see any ways the interface could
become more GNOME HIG compliant (or just improve in general).

Requirements
============

Minimum Requirements
--------------------

1. Python 2.6
2. PyGTK (>=2.16)
3. SQLalchemy (>= 0.7)
4. Python Imaging Libraries (PIL)
5. elib.intl

Build Requirements
------------------

1. intltool
2. python-distutils-extra

Extra Requirements
------------------

1. Python Reportlab (python-reportlab) - for PDF export.
2. For RTF support, you will need the PyRTF library available
   at http://pyrtf.sourceforge.net
3. PyGTKSpell
4. pypoppler
5. python-gst0.10
6. BeautifulSoup (for the Web import plugin)

Install
=======

Under Linux and Unix systems, running `sudo python setup.py install` will
install gourmet to your current python environment's default location
(i.e. subdirectories of /usr/local for most Linux distributions. For
information on how to customize these locations, run
`sudo python setup.py --help`).

That should be all you need, and will create an entry in your launcher menu.
Alternatively, you can now run gourmet by issuing

`gourmet`

from the commandline.

Gourmet also has commandline options, most of which should not be
needed by an average user. Issuing `gourmet --help` will get you help
for those options.

Warning
=======

No warantee, etc. Please inform me of bugs/problems/feature
requests and I'll respond as quickly as I can. I can be reached
at Thomas_Hinkle@alumni.brown.edu

----

If you find this program useful, or have any comments or questions,
please e-mail to let me know at Thomas_Hinkle@alumni.brown.edu
