# Contributing

Thank you for taking an interest in contributing to Gourmet! We appreciate that
you're thinking about offering your time to improving the project, and it's our
goal to respect your contribution accordingly.

Although this document focuses on code contributions, you can contribute in
several ways:
- File a bug report.
- Add or improve documentation.
- Promote the project to others.


## Contributing Code

In general, the process for contributing code is:

1. Pick or open an [issue](https://github.com/thinkle/gourmet/issues) to work
   on
2. Post a comment expressing your intent to make sure nobody else is already
   working on it
3. Set up a development environment, as described below
4. Hack the code, and when ready
5. Push your changes to your forked repo and create a pull request.

Make sure to also check out our upcoming [milestones](https://github.com/thinkle/gourmet/milestones).


## Setting Up a Development Environment

You'll want to clone Gourmet to your computer and probably
[fork](https://github.com/thinkle/gourmet/fork) it as well.

Ensure your system has the necessary prerequisites installed:
- [Python](https://www.python.org/), which is what Gourmet is written in.
- [PyGObject](https://pygobject.readthedocs.io/en/latest/) for GTK+ 3 and
  other GNOME libraries. You may either install your system's `pygobject`
  package(s) or install the necessary system requirements to install
  `pygobject` from PyPI with `pip`. The latter method is recommended if you
  plan on doing development within a Python virtual environment.
- [intltool](https://freedesktop.org/wiki/Software/intltool/) for
  internationalization.
- (optional) [Enchant](https://abiword.github.io/enchant/) for spell-checking.
  At least one of the backends must be installed as well.
- (optional) [GStreamer](https://gstreamer.freedesktop.org/) for sound. The
  GStreamer library itself and gst-plugins-base are required. Python bindings
  are provided through PyGObject, so GObject introspection data is also needed.
- (optional) [poppler](https://poppler.freedesktop.org/) for exporting PDFs.
  Python bindings are provided through PyGObject, so install the GLIB bindings
  and associated GObject introspection data.

**Note:** Although some prerequisites are optional, the development install of
Gourmet enables all plugins and features, so you probably want to install all
prerequisites to avoid any issues.

You may want to setup a [Python virtual
environment](https://docs.python.org/3/library/venv.html). This is optional but
highly recommended:
```bash
$ python -m venv --prompt gourmet env
$ source env/bin/activate
(gourmet) $ pip install -U pip setuptools wheel
```

Then install Gourmet itself:
```bash
(gourmet) $ pip install -r development.in
```
This installs the remaining Python dependencies and Gourmet itself in editable
mode, which allows you to run Gourmet and see your changes without having to
reinstall it.

**Note:** If you encounter an error during the installation of
`pygtkspellcheck`, first install `pyenchant` and `pygobject` on their own:
```bash
(gourmet) $ pip install pyenchant pygobject
(gourmet) $ pip install -r development.in
```

You should now be able to launch and run Gourmet:
```bash
(gourmet) $ gourmet
```


## Style

Gourmet is an old code base, consequently its style is not always consistent or
conformant to contemporary tastes. We are not interested in bikeshedding, but
please follow [PEP 8](http://www.python.org/dev/peps/pep-0008/) when writing new
code, and when working on old code, please tidy up as you go.


## Issues and Suggestions

We welcome feedback and issue reporting. You can do so by browsing existing
issues and commenting on them, or creating a new one.

When reporting an issue, please fill in the provided template.

For feedback or requests of features, please explain with details, and
screenshots if possible, what you would like.
