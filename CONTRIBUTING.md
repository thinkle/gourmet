If you'd like to contribute, it's best to follow established GitHub practices by

1. [forking](https://github.com/thinkle/gourmet/fork) the repository
2. picking an [issue](https://github.com/thinkle/gourmet/issues) to work on
3. posting a little comment expressing your intent to make sure nobody else is already working on it
4. hacking the code, and when ready
5. pushing to your forked repo, and filing a pull request.

You're also welcome to join our [Gourmet team on Launchpad](https://launchpad.net/~gourmet) and particularly to subscribe to our mailing list there. We'd kindly ask you to stick to a *one issue = one commit = one pull request* policy whenever possible, with an expressive commit message mentioning the issue it's supposed to fix on the last line (like so: "Fixes #123."). (That way, the corresponding issue gets closed automatically when merging the commit.)

Our introductory material to the source code is currently rather sparse, but you still might want to check out the [Development](Development) wiki article and [CODING.md](CODING.md) file for starters.

To get started, why not check out our list of [list of bugs tagged 'easy'](https://github.com/thinkle/gourmet/issues?labels=easy&page=1&state=open)?

Currently, our most pressing issues are:
* [Windows Printing](https://github.com/thinkle/gourmet/issues/708).
* [Release a mac version](https://github.com/thinkle/gourmet/issues/704).
* Code cleanup.
 * This includes using [SQLAlchemy's ORM](https://github.com/thinkle/gourmet/issues/712), which is an ongoing effort in the `develop` branch, and scheduled for release woth version 0.18.0.
 * Parts of Gourmet's source code are about ten years old, and technologies have evolved since development started. Hence, there are some things that were implemented differently back then and could be greatly simplified by using modern technologies available in the present-day versions of the toolkits used by Gourmet (such as Gtk components as in [gourmet/gtk_extras/dialog_extras.py](../blob/master/gourmet/gtk_extras/dialog_extras.py), database backends, etc).
 * Also, there are still large portions of commented-out code where something already got replaced by something else, 
 * or python modules that aren't actually imported anywhere else anymore (example: [3daaba2db](../commit/3daaba2dbb865272cb5b1b96d14eca3fe5deeaf7)).
 * Remove old logo images, file duplicates, obsolete plugins, etc.
 * Clean up files names which currently are a mixture of camelCaps and under\_scores, plus some rather obscure abbreviations.
 * Use pyflakes, pylint or pychecker etc. to detect unnecessary imports etc. I find it _very_ useful to use e.g. the Eclipse IDE with PyDev which features inline pylint checks!
 * Stick to [PEP 8](http://www.python.org/dev/peps/pep-0008/) conventions, e.g. by running [autopep8](https://pypi.python.org/pypi/autopep8/) on existing code.
 * Use [CloneDigger](http://clonedigger.sourceforge.net/) to find duplicate code and remove redundancies.
* Write tests. Being the recognized cure for regressions, we could really use some automated testing. There seem to be have been some related efforts spread across the code, but the goal should really be tests that cover pretty much all functionality, and that are run regularly (particularly before releasing) to check if anything is broken (see the [TESTS](../blob/master/TESTS) file). We should use some standard Python (and PyGTK) unit test framework to implement this.
  * One of the main issues with the current code is that a lot of it is very intertwined (circular imports, lots of classes constructed with the entired recipe database as an argument, etc). I've tried to implement a couple of unit tests to test single features (which, as the name says, are supposed to act on "units of work") -- e.g. some website importers. That's currently not easy at all, as I need to initialize and pass either a dummy database, or replace some classes they would normally depend on with dummy classes. So we need more "atomic" classes before being able to write proper tests.
* We could also use some more documentation, both for users and for developers (i.e. by adding comments to the source code).
* We'd like to turn our current [web page](http://thinkle.github.com/gourmet/) into an actual web _site_. To work on the web site, just fork our repo and check out the gh-pages branch.
 * It should retain most of the current visual elements (icon, color scheme, Lobster font)
 * but use [Jekyll](https://help.github.com/articles/using-jekyll-with-pages) (or maybe the [Octopress](http://octopress.org/) framwork for Jekyll; and maybe [Disqus](http://disqus.com/) for comments) to provide a news blog into which we'll then feed our old news items back from sourceforge times, and that we're going to use for future announcements (e.g. for releases).
 * What about a download with e.g. a [Download for Ubuntu](https://wiki.ubuntu.com/SoftwareCenter/AppPromotion) button?
 * A "Star on GitHub" button (like http://docs.python-requests.org/en/latest/ has) would be nice.
 * Some way to donate would be also nice (PayPal, gittip.com, Flattr,...?)
* Bug triaging. We have about [200 open issues](https://github.com/thinkle/gourmet/issues), and some of them are a couple of years old and have already been fixed. Some help in tagging, commenting, and ideally closing bugs is very welcome! (Note that to close a bug, you should really be sure it's okay to do so because you have tested Gourmet to work under the same conditions the bug reporter did.)

Make sure to also check out our upcoming [milestones](https://github.com/thinkle/gourmet/milestones).

More nifty ideas can be found via the [gsoc-idea label](https://github.com/thinkle/gourmet/issues?labels=gsoc-idea&page=1&state=open).
