* Introduction *

Gourmet Recipe Manager is a manager, editor, and organizer for
recipes. It currently has support for MealMaster(tm) and
MasterCook(tm) import, including 1 and 2 column MealMaster recipes and
plain text and XML MasterCook(tm). It can also export and import an XML
format of its own (the DTD is included here for your interest) which I
developed for an earlier recipe program in emacs-lisp. It also allows
you to export recipes as MealMaster(tm), HTML, RTF or Plain Text.

Furthermore, to facilitate copying recipes off the web, you can drag a
list of ingredients from another application (i.e. your web browser)
to the ingredient list on the Recipe Card view and they will
automatically be imported (the program will do the best it can parsing
amounts, units and ingredients -- you can quickly see and correct any
problems). This can also be done with a list of ingredients in the
clipboard or in a text file.

In addition to allowing you to edit, import, search and categorize
recipes, Gourmet generates shopping lists sorted by category. It has a
simple mechanism for allowing you to designate "pantry" items that you
already have and don't need to buy, which will gourmet will remember
between sessions.

Gourmet also includes a handy unit converter to quickly allow you to
convert any measurement (it even knows the densities of a number of
common foods!).

The default and best supported backend for Gourmet is metakit -- a
all-in-a-file database that you don't need to know anything
about. Gourmet can also be used with sqlite or with MySQL. Support for
these databases is experimental at present.

This program aspires to meet the GNOME Human Interface
Guidelines. Please let me know if you see any ways the interface could
become more GNOME HIG compliant (or just improve in general).

* Minimum Requirements *

1. Python 2.2
2. PyGTK>2.3.9 and PyGNOME 
   (Note: with pygtk > 2.5, pygnome bindings have been split up.
    To print, you'll need e.g. the python-gnome2-extras package as
    well as the the python-gnome2 package).
3. libglade
4. Metakit & Python Metakit bindings (on debian, this is the
libmetakit-python package). Note: Gourmet can be run without
metakit if you use the SQLite or MySQL backends, but these are experimental
at present.
5. distutils (to install). Provided by python-dev package.
6. Python Imaging Libraries (PIL)

* Extra Requirements *

1. For RTF support, you will need the PyRTF library available
   at http://pyrtf.sourceforge.net

2. Gnomeprint bindings, for nice python printing. This is packaged
   differently in different places and versions, but will likely be in
   something called "python-gnome" or "pygtk-extras".

* Install *

As root, issue a python setup.py install.

That should be all you need. You can now simply issue

gourmet

from the commandline. Alternatively, use the nifty launcher
installed in /usr/share/applications/

Gourmet also has commandline options, most of which should not be
needed by an average user. Issuing gourmet --help will get you help
for those options.

* Warning *

No warantee, etc. Please inform me of bugs/problems/feature
requests and I'll respond as quickly as I can. I can be reached
at Thomas_Hinkle@alumni.brown.edu

* Brief manual *

Gourmet is intended to be intuitive to use. If anything is completely
non-obvious, I'll consider that a bug: let me know and I'll try to fix
it.

To use Gourmet, the first thing you'll need are some recipes in your
database. You can get recipes by importing MealMaster(tm) files or by
entering recipes manually (click "New Recipe"). Or you could write a
new importer module for whatever file format you have recipes in
*grin*.

There is somewhat out-of-date and incomplete documentation available
in the documentation folder. On a GNOME system, type yelp
documentation/documentation.xml (from the gourmet source folder) and
you can read what's done so far. This isn't yet properly installed by
setup.py.

The Gourmet program has three kinds of windows.

The first is a index view for looking at your collection. It has a
search-as-you-type search box that is meant to let you quickly find
your recipes. You can also create complex searches by using the add
button next to the search box to combine searches. From this view, you
can click the "View Recipe" button to see a recipe card view of your
recipe. Note that currently, the search box excepts regular
expressions.

The Card View shows you a recipe at a time, and doubles as an editor,
allowing you to conveniently edit old recipes and input new ones. The
recipe card window has multiple tabs -- the first tab is simply a
display of the recipe; the other tabs allow you to edit details of
your recipe: title and details, instructions, ratings, notes, an
image, and, of course, an ingredient list. To edit ingredients in a
typing-efficient way, use the ingredient editor at the bottom of the
cardView. This is set up to allow you to quickly type "amount TAB unit
TAB item TAB alt-A (for Add)"

Ingredients use a key system, so that when Gourmet generates shopping
lists, it will know that, for example, "aubergine", "eggplant" and
"eggplant, halved" are all the same thing. The program will learn keys
as you go, so that if you tell it once that "flour" should be keyed as
"flour, all purpose", then every time you type "flour" it will
automatically set the key to "flour, all purpose". It will also try to
guess keys as best it can, which is usually helpful but may
occasionally lead to incorrect results.

You can also drag and drop a list of ingredients from another program
onto the ingredient list and they will be imported -- the program does
the best it can to parse out units and amounts, but you will probably
have to correct some mistakes by hand.

In addition to having keys for ingredients, Gourmet keeps track of
shopping categories so that your shopping lists are sorted. If you're
going to use Gourmet for shopping lists and you like your shopping
lists sorted, then you should enter categories when it's
convenient. Any time you tell Gourmet what category something is in,
it will remember for the future.

The Shopping List View contains your shopping list. You can add
recipes to the shopping list from the index (where you can select
multiple recipes at a time to add) or from recipe cards. This view has
both a shopping list and a "pantry list" (ingredients called for in
your recipe that you don't need to buy). You can move ingredients
between the lists by dragging and dropping between the two lists, by
right clicking and selecting "move to pantry." You can also change the
categories for items in your lists by right-clicking and selecting a
new category or by using drag-and-drop.

Finally, you can add arbitrary items to the shopping list by clicking
on the "Add" button at the bottom of the screen.

From the shopping list, you can export a simple text file or you can
print. Printing will use the nice gnomeprint interface if available,
offering a print preview and relatively attractive layout. If not
available, printing will allow you to pipe the recipe in plain text to
lpr or another print command of your choosing.

----

If you find this program useful, or have any comments or questions,
please e-mail to let me know at Thomas_Hinkle@alumni.brown.edu