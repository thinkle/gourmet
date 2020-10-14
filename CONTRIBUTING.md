# Getting Started
Install Gourmet's dependencies:

    pip3 install -r requirements.txt
    pip3 install -r development.txt

`requirements.txt` contains the dependencies needed for Gourmet itself,
`development.txt` contains the packages required for testing.

Before you start development, you should first build localized *.mo and
*.gourmet-plugin files within a build/ subdirectory of the source tree by
running

    python3 setup.py build_i18n -m

You can then install Gourmet in edit mode so:

    pip3 install --user -e .

By doing so, you will be able to test your changes when launching Gourmet.

# Style
New code follows the [PEP 8](http://www.python.org/dev/peps/pep-0008/) standard.  

The following conventions are not strictly followed in Gourmet, old code
should be reformatted only when modifying it.

# Getting the Source
Gourmet's source code is hosted on [GitHub](https://github.com/thinkle/gourmet).
You can clone it by opening a command prompt and typing:

    git clone https://github.com/thinkle/gourmet.git

If you don't have any previous experience with Git, you might want to take a
look at the [official Git tutorial](http://www.kernel.org/pub/software/scm/git/docs/gittutorial.html),
or the [GitHub Help pages](http://help.github.com/).

# Contributing
## Development
If you'd like to contribute,

1. [fork](https://github.com/thinkle/gourmet/fork) and clone the repository
2. pick an [issue](https://github.com/thinkle/gourmet/issues) to work on
3. post a little comment expressing your intent to make sure nobody else is
   already working on it
4. hack the code, and when ready
5. push to your forked repo, and create a pull request.

Make sure to also check out our upcoming [milestones](https://github.com/thinkle/gourmet/milestones).

## Issues and Suggestions
We welcome feedback and issue reporting. You can do so by browsing existing
issues and commenting on them, or creating a new one.

When reporting an issue, please fill in the provided template.

For feedback or requests of features, please explain with details, and
screenshots if possible, what you would like.
