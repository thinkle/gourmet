# Gourmet Recipe Manager
## Try it. It's good!
![Tests](https://github.com/thinkle/gourmet/workflows/Tests/badge.svg) ![Build](https://github.com/thinkle/gourmet/workflows/Build/badge.svg)

# Introduction
Gourmet Recipe Manager is a manager, editor, and organizer for recipes.  
It has a plugin architecture which allows you to enable extensions to
Gourmet's base functionality.   
For example, there is a nutritional plugin that allows Gourmet to help you
calculate nutritional information for any recipe. There are also a wide variety
of import and export plugins that let Gourmet read and write recipes in various
formats.

# Requirements and Installation
**We strongly recommend that you make a backup of your recipe database.**  
As Gourmet is still in early stage of (re)development, make a backup of your
recipe database, typically found under `$HOME/.gourmet/recipe.db`:
```sh
cp $HOME/.gourmet/recipes.db $HOME/.gourmet/recipes.db.bak
```

Installation instruction are found in [INSTALL.md](INSTALL.md).

*Note: pdf support is not enabled in Flatpak. PDF and Print exports are thus
not available.*

# Issues and Contributions
See the [contribution guide](CONTRIBUTING.md).
