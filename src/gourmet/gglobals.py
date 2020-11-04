import os
import os.path
from gettext import gettext as _
from pathlib import Path

from gi.repository import Gdk, GdkPixbuf, Gtk

from . import settings
from .image_utils import load_pixbuf_from_resource as _load_pixbuf_from_resource
from .optionparser import args


lib_dir = os.path.join(settings.lib_dir)

# TODO: remove the gourmetdir global variable
# Instead of making this a global, it should be passed as an argument to
# interested parties.
# TODO: use standard platform directories to store user-specific data
# On linux, the "~/.gourmet" directory should go into the appropriate XDG user
# directory (or directories). This should also be audited on other platforms.
if args.gourmetdir:
    gourmetdir = Path(args.gourmetdir).absolute()
    print(f'User specified gourmetdir {gourmetdir}')
elif os.name == 'nt':
    gourmetdir = Path(os.environ['APPDATA']).absolute() / 'gourmet'
else:
    gourmetdir = Path(os.environ['HOME']).absolute() / '.gourmet'
gourmetdir.mkdir(exist_ok=True)

use_threads = args.threads
# Uncomment the below to test FauxThreads
# use_threads = False


REC_ATTRS = [('title', _('Title'), 'Entry'),
             ('category', _('Category'), 'Combo'),
             ('cuisine', _('Cuisine'), 'Combo'),
             ('rating', _('Rating'), 'Entry'),
             ('source', _('Source'), 'Combo'),
             ('link', _('Website'), 'Entry'),
             ('yields', _('Yield'), 'Entry'),
             ('yield_unit', _('Yield Unit'), 'Combo'),
             ('preptime', _('Preparation Time'), 'Entry'),
             ('cooktime', _('Cooking Time'), 'Entry'),
             ]

INT_REC_ATTRS = ['rating', 'preptime', 'cooktime']
FLOAT_REC_ATTRS = ['yields']
TEXT_ATTR_DIC = {'instructions': _('Instructions'),
                 'modifications': _('Notes'),
                 }

REC_ATTR_DIC = {}
NAME_TO_ATTR = {_('Instructions'): 'instructions',
                _('Notes'): 'modifications',
                _('Modifications'): 'modifications',
                }

DEFAULT_ATTR_ORDER = ['title',
                      # 'servings',
                      'yields',
                      'cooktime',
                      'preptime',
                      'category',
                      'cuisine',
                      'rating',
                      'source',
                      'link',
                      ]

DEFAULT_TEXT_ATTR_ORDER = ['instructions',
                           'modifications',
                           ]


def build_rec_attr_dic():
    for attr, name, widget in REC_ATTRS:
        REC_ATTR_DIC[attr] = name
        NAME_TO_ATTR[name] = attr


build_rec_attr_dic()

DEFAULT_HIDDEN_COLUMNS = [REC_ATTR_DIC[attr] for attr in
                          ('link', 'yields', 'yield_unit', 'preptime', 'cooktime')]  # noqa

# Set up custom STOCK items and ICONS!
icon_factory = Gtk.IconFactory()


# TODO: Move this into GTK-specific code
# TODO: Update/remove potentially-deprecated code?
# GTK 3 has deprecated the use of stock icons, so this may need to be rewritten
# (or removed altogether) to ensure this works in the future
def add_icon(
        pixbuf: GdkPixbuf.Pixbuf,
        stock_id: str,
        label: str = None,
        modifier: Gdk.ModifierType = 0,
        keyval: int = 0) -> None:
    iconset = Gtk.IconSet.new_from_pixbuf(pixbuf)
    icon_factory.add(stock_id, iconset)
    icon_factory.add_default()
    # TODO: fix adding icons
    return
    Gtk.stock_add([(stock_id, label, modifier, keyval, "")])


for filename, stock_id, label, modifier, keyval in [
    ('AddToShoppingList.png',
     'add-to-shopping-list',
     _('Add to _Shopping List'),
     Gdk.ModifierType.CONTROL_MASK,
     Gdk.keyval_from_name('l')),

    ('reccard.png', 'recipe-card', None, 0, 0),

    ('reccard_edit.png', 'edit-recipe-card', None, 0, 0),
     ]:
    add_icon(_load_pixbuf_from_resource(filename), stock_id, label, modifier, keyval)


# Color scheme preference
LINK_COLOR = 'blue'
star_color = 'blue'

style = Gtk.StyleContext.new()
_, bg_color = style.lookup_color('bg_color')
_, fg_color = style.lookup_color('fg_color')

if sum(fg_color) > sum(bg_color):  # background is darker
    LINK_COLOR = 'deeppink'
    star_color = 'gold'

NO_STAR = Path(__file__).parent / 'data' / 'images' / 'no_star.png'
HALF_STAR = Path(__file__).parent / 'data' / 'images' / f'half_{star_color}_star.png'  # noqa
FULL_STAR = Path(__file__).parent / 'data' / 'images' / f'{star_color}_star.png'  # noqa
