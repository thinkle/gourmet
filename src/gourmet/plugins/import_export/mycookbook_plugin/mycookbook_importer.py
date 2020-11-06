import re
import gourmet.image_utils
from gourmet.gdebug import *
from gourmet.gglobals import *
from gourmet.importers import xml_importer
from PIL import Image


class RecHandler(xml_importer.RecHandler):
    ADD = 1
    IS = 2
    # mapping: 'mcb tag':('gourmet tag',method import),
    RECTAGS = {'title': ('title', IS),
               'url': ('link', ADD),
               'category': ('category', ADD),
               'serving': ('servings', IS),
               'cooktime': ('cooktime', IS),
               'preptime': ('preptime', IS),
               'quantity': ('yields', IS),
               'rating': ('rating', IS),
               'source': ('source', IS),
               }
    RECIPE_TAG = 'recipe'
    ING_TAG = 'ingredient'
    INSTR_TAG = 'recipetext'
    COMMENT_TAG = 'comments'

    current_section = ''

    def __init__(self, total=None, conv=None, parent_thread=None):
        self.in_mixed = 0
        self.rec = {}
        self.ing = {}
        xml_importer.RecHandler.__init__(self, total, conv=conv,
                                         parent_thread=parent_thread)

    def startElement(self, name, attrs):
        self.elbuf = ""
        if name == self.RECIPE_TAG:
            self.start_rec()
        if name == self.ING_TAG:
            self.current_section = 'ingredient'
        if name == self.INSTR_TAG:
            self.current_section = 'instruction'
        if name == self.COMMENT_TAG:
            self.current_section = 'comments'

    def endElement(self, name):
        key, method = None, None
        if name == self.RECIPE_TAG:
            self.commit_rec()
            return
        if name == 'li' and self.current_section == 'ingredient':
            if not hasattr(self, 'db'):
                import gourmet.backends.db as db
                self.db = db.get_database()
            ingdic = self.rd.parse_ingredient(self.elbuf.strip())
            self.start_ing(**ingdic)
            self.commit_ing()
        if name == 'li' and self.current_section == 'instruction':
            key = 'instructions'
            method = self.ADD
            obj = self.rec
        if name == 'li' and self.current_section == 'comments':
            key = 'modifications'
            method = self.ADD
            obj = self.rec
        if name == 'imagepath':
            obj = self.rec
            # get the temp directory and build the image path
            (dirname, filename) = os.path.split(self.parent_thread.fn)
            (pic_dirname, pic_filename) = os.path.split(self.elbuf.strip())
            pic_fullpath = os.path.join(dirname, 'images', pic_filename)

            # try to import the image
            if os.path.isfile(pic_fullpath):
                try:
                    im = Image.open(pic_fullpath)
                    obj['image'] = gourmet.image_utils.image_to_bytes(im)
                except Exception as e:
                    print('Issue loading: ' + pic_fullpath)
                    print(str(e))

        # times fixing
        if name == 'cooktime' or name == 'preptime':
            self.elbuf = self.elbuf.replace('mn', 'min')
            if re.match('([0-9]*)min', self.elbuf):
                self.elbuf = self.elbuf.replace('min', ' min')

        # other tags
        if name == self.ING_TAG:
            self.current_section = ''
        elif name == self.INSTR_TAG:
            self.current_section = ''
        elif name == self.COMMENT_TAG:
            self.current_section = ''
        elif name in self.RECTAGS:
            obj = self.rec
            key, method = self.RECTAGS[name]

        value = self.elbuf.strip()
        if key and value:
            if key == 'rating':
                # MyCookbook's rating range is integers from 1 to 5, while
                # ours is from 1 to 10, so we have to multiply by 2 when
                # importing.
                obj['rating'] = int(value) * 2
            elif method == self.ADD and key in obj:
                obj[key] = f'{obj[key]}\n {value}'
            else:
                obj[key] = value


class Converter(xml_importer.Converter):
    def __init__(self, filename, conv=None):
        xml_importer.Converter.__init__(self, filename, RecHandler,
                                        recMarker="</recipe>",
                                        conv=conv,
                                        name='MCB Importer')
