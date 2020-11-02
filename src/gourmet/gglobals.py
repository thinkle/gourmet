import os
import os.path
from gettext import gettext as _
from pathlib import Path

from gi.repository import Gdk, GdkPixbuf, Gtk

from . import settings
from .optionparser import args

uibase = os.path.join(settings.ui_base)
lib_dir = os.path.join(settings.lib_dir)

gourmetdir: Path = Path(os.environ['HOME']).absolute() / '.gourmet'
if os.name == 'nt':
    gourmetdir = Path(os.environ['APPDATA']).absolute() / 'gourmet'

if args.gourmetdir:
    gourmetdir = Path(args.gourmetdir).absolute()
    print(f'User specified gourmetdir {gourmetdir}')

gourmetdir.mkdir(exist_ok=True)

use_threads = args.threads
# Uncomment the below to test FauxThreads
# use_threads = False

# note: this stuff must be kept in sync with changes in setup.py
data_dir = settings.data_dir
imagedir = os.path.join(settings.data_dir, 'images')

plugin_base = settings.plugin_base

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


def add_icon(file_name, stock_id, label=None, modifier=0, keyval=0):
    pb = GdkPixbuf.Pixbuf.new_from_file(file_name)
    iconset = Gtk.IconSet.new_from_pixbuf(pb)
    icon_factory.add(stock_id, iconset)
    icon_factory.add_default()
    # TODO: fix adding icons
    return
    Gtk.stock_add([(stock_id,
                    label,
                    modifier,
                    keyval,
                    "")])


for filename, stock_id, label, modifier, keyval in [
    ('AddToShoppingList.png',
     'add-to-shopping-list',
     _('Add to _Shopping List'),
     Gdk.ModifierType.CONTROL_MASK,
     Gdk.keyval_from_name('l')),

    ('reccard.png', 'recipe-card', None, 0, 0),

    ('reccard_edit.png', 'edit-recipe-card', None, 0, 0),
     ]:
    add_icon(os.path.join(imagedir, filename), stock_id,
             label, modifier, keyval)


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
