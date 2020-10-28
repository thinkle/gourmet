# Installation
Gourmet is currently available in the form of Flatpak and Python wheel.
We recommend that you install it from the Flatpak.
In both cases, you will need an internet connection.

**We strongly recommend that you make a backup of your recipe database.**
As Gourmet is still in early stage of (re)development, make a backup of your
recipe database, typically found under `$HOME/.gourmet/recipe.db`:
```sh
cp $HOME/.gourmet/recipes.db $HOME/.gourmet/recipes.db.bak
```

## Flatpak
The Flatpak contains the full environment, but depends on other flatpak
packages, which will be installed automatically.

Install Flatpak if it's not on your system already:
```sh
sudo apt-get install flatpak
```

As Gourmet is still under active development, the flatpak is not available from
Flathub, and instead must be [downloaded and installed manually](https://github.com/kirienko/gourmet/releases/tag/v1-alpha2).

In a terminal, execute the following:
```sh
flatpak remote-add --if-not-exists --user flathub https://flathub.org/repo/flathub.flatpakrepo
sudo flatpak install gourmet-2db9db8f.flatpak
```

You will be prompted with a message regarding the runtime:
```sh
Required runtime for io.github.thinkle.Gourmet/x86_64/master (runtime/org.gnome.Platform/x86_64/3.36) found in remote flathub)
Do you want to install it? [Y/n]
```

Select `y`, and a list of dependencies will be displayed. Say `y` to install
them all.

At the end, you will be greeted with an `Installation complete.` message.

You can now launch the Flatpak either from your application menu or from the
command line so:
```sh
flatpak run io.github.thinkle.Gourmet
```

It can be uninstalled so:
```sh
flatpak remove io.github.thinkle.Gourmet
```


## Python Wheel
[Download the wheel](https://github.com/kirienko/gourmet/releases/tag/v1-alpha2)
Dependencies must be manually installed.

### Unbutu 20.04, Linux Mint 20
Install the following packages from `apt`:

```sh
sudo apt-get update

sudo apt-get install --no-install-recommends python3-argcomplete python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgirepository1.0-dev libcairo2-dev enchant python3-bs4 python3-ebooklib python3-keyring python3-lxml python3-pil python3-cairo python3-enchant python3-gi python3-gst-1.0 python3-gtkspellcheck python3-requests python3-reportlab python3-selenium python3-setuptools python3-sqlalchemy python3-pip python3-toml gir1.2-poppler-0.18 ```

Then, install dependencies from the Python repository:
```sh
sudo pip3 install scrape-schema-recipe
```

Finally, install Gourmet:

```sh
sudo pip3 install gourmet-2db9db8f-py3-none-any.whl
```

You can now launch Gourmet from a terminal:

```sh
$ gourmet
```
