from __future__ import print_function

import settings
from gettext import gettext as _
# To have strings from .ui files (gtk.Builder) translated on all platforms,
# we need the following module to enable localization on all platforms.
try:
    import elib.intl
    elib.intl.install('gourmet', settings.locale_base)
except ImportError:
    print('elib.intl failed to load.')
    print('IF YOU HAVE TROUBLE WITH TRANSLATIONS, MAKE SURE YOU HAVE THIS '
          'LIBRARY INSTALLED.')

name= 'gourmet'
appname = _("Gourmet Recipe Manager")
copyright = _("Copyright (c) 2004-2014 Thomas M. Hinkle. GNU GPL v2")
version = "0.17.5"
website = "http://thinkle.github.io/gourmet/"
description = "Recipe Organizer and Shopping List Generator"
long_description = _("""\
Gourmet Recipe Manager is an application to store, organize and search recipes.

Features:
* Makes it easy to create shopping lists from recipes.
* Imports recipes from a number of sources, including MealMaster and MasterCook
  archives and several popular websites.
* Exports recipes as PDF files, plain text, MealMaster files, HTML web pages,
  and a custom XML format for exchange with other Gourmet users.
* Supports linking images with recipes.
* Can calculate nutritional information for recipes based on the ingredients.
""")
author = 'Thomas Mills Hinkle'
author_email = 'Thomas_Hinkle@alumni.brown.edu'
maintainer = 'Bernhard Reiter'
maintainer_email = 'ockham@raz.or.at'
authors = ["Thomas M. Hinkle <Thomas_Hinkle@alumni.brown.edu>",
           _("Roland Duhaime (Windows porting assistance)"),
           _("Daniel Folkinshteyn <nanotube@gmail.com> (Windows installer)"),
           _("Richard Ferguson (improvements to Unit Converter interface)"),
           _("R.S. Born (improvements to Mealmaster export)"),
           _("ixat <ixat.deviantart.com> (logo and splash screen)"),
           _("Yula Zubritsky (nutrition and add-to-shopping list icons)"),
           _("Simon Darlington <simon.darlington@gmx.net> (improvements to internationalization, assorted bugfixes)"),
           _("Bernhard Reiter <ockham@raz.or.at> (maintenance since 0.16.0, website re-design)"),
           ]
artists = [_("Nyall Dawson (cookie icon)"),
           _("Kati Pregartner (splash screen image)")]
license = 'GPL'
