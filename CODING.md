Getting Started
===============
Make sure you have all the dependencies as listed in [INSTALL.md](INSTALL.md)
installed.

Before you start coding, you should first build localized *.mo and
*.gourmet-plugin files within a build/ subdirectory of the source tree by
running

    python setup.py build_i18n -m

Afterwards, you can just launch `bin/gourmet` from the source directory to
test the program and see how changes to the source code affect it.

Style
=====
The style used in Gourmet can be rather varied. However, new code
should adhere to style guidelines, and old code should be updated to meet
them. Generally, we try to follow the python style guidelines set out
by Mr. Guido Van Russom, as formalized by
[PEP 8](http://www.python.org/dev/peps/pep-0008/).

The following conventions are not strictly followed in Gourmet, but
I'd like to follow them from here on out for greater consistency.

* Class names are capitalized, using CamelCase.
* method names begin with verbs and use underscores for multiple words
* attributes should be lower cased and use camel caps for multiple words.

Development tools
=================
If you want to work from within an IDE, you might want to use [Eclipse](http://www.eclipse.org) with some useful plugins, which you install by entering their download locations into Eclipse's Help > Install new Software... dialog:

* EGit and GitHub Mylyn Connector
 * are for working with Git repositories, and GitHub issues integration into Eclipse, see http://eclipse.github.com; download locations: http://download.eclipse.org/egit/updates and http://download.eclipse.org/egit/github/updates
* PyDev
 * is for Python development; its download location is http://pydev.org/updates
* EclipseNSIS
 * if you want to produce a windows installer package; download location: http://eclipsensis.sourceforge.net/update

With EGit installed, go to File > Import... > Git > Git repository and enter the URI found in the "Getting the Source" section. The rest of the importing process should be fairly intuitive.

As a supplement or an alternative to Eclipse and the plugins listed above,
we can recommend [GitHub for Windows](http://windows.github.com/) as the
Windows Git client; it features both command-line tools (and a dedicated prompt
called Git Shell) and a nifty GUI.

Getting the Source
==================

Gourmet's source code is hosted at [GitHub](https://github.com/thinkle/gourmet).
You can clone it by opening a command prompt and typing
```
git clone https://github.com/thinkle/gourmet.git
```

If you don't have any previous experience with Git, you might want to take a
look at the [official Git tutorial](http://www.kernel.org/pub/software/scm/git/docs/gittutorial.html),
or the [GitHub Help pages](http://help.github.com/).
