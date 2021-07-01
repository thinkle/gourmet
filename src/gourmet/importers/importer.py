import gettext
import os
import re
import time
import unittest
import xml.sax.saxutils

import gourmet.gglobals
import gourmet.gtk_extras.dialog_extras as de
from gourmet import convert, image_utils
from gourmet.gdebug import TimeAction, debug, print_timer_info
from gourmet.i18n import _
from gourmet.keymanager import KeyManager
from gourmet.recipeManager import get_recipe_manager  # Get hold of database
from gourmet.threadManager import SuspendableThread, Terminated

# Convenience functions

def string_to_rating (s):
    m = simple_matcher.match(s)
    if m:
        top=float(convert.frac_to_float(m.groups()[0]))
        bottom = float(convert.frac_to_float(m.groups()[2]))
        return int(top/bottom * 10)

def add_to_fn (fn):
    '''Add 1 to a filename.'''
    f,e=os.path.splitext(fn)
    try:
        f,n=os.path.splitext(f)
        n = int(n[1:])
        n += 1
        return f + "%s%s"%(os.path.extsep,n) + e
    except:
        return f + "%s1"%os.path.extsep + e

class Importer (SuspendableThread):

    """Base class for all importers. We provide an interface to the recipe database
    for importers to use. Basically, the importer builds up a dictionary of properties inside of
    self.rec and then commits that dictionary with commit_rec(). Similarly, ingredients are built
    as self.ing and then committed with commit_ing()."""

    def __init__ (self,
                  rd = None, # OBSOLETE
                  total=0,
                  prog=None, # OBSOLETE
                  do_markup=True,conv=None,rating_converter=None,
                  name='importer'):
        """rd is our recipeData instance.

        Total is used to keep track of progress.

        do_markup should be True if instructions and modifications
        come to us unmarked up (i.e. if we need to escape < and &,
        etc. -- this might be False if importing e.g. XML).
        """

        timeaction = TimeAction('importer.__init__',10)
        if not conv: self.conv = convert.get_converter()
        self.id_converter = {} # a dictionary for tracking named IDs
        self.total = total
        if prog or rd:
            import traceback; traceback.print_stack()
            if prog:
                print('WARNING: ',self,'handed obsolete parameter prog=',prog)
            if rd:
                print('WARNING: ',self,'handed obsolete parameter rd=',rd)
        self.do_markup=do_markup
        self.count = 0
        self.rd = get_recipe_manager()
        self.rd_orig_ing_hooks = self.rd.add_ing_hooks
        self.added_recs=[]
        self.added_ings=[]
        #self.rd_orig_hooks = self.rd.add_hooks
        self.rd.add_ing_hooks = []
        #self.rd.add_hooks = []
        self.position=0
        self.group=None
        # allow threaded calls to pause
        self.suspended = False
        # allow threaded calls to be terminated (this
        # has to be implemented in subclasses).
        self.terminated = False
        # Our rating converter -- if we've been handed a class, we
        # assume our caller will handle doing the
        # conversion. Otherwise we do it ourselves.
        if rating_converter:
            self.rating_converter = rating_converter
            self.do_conversion = False
        else:
            self.rating_converter = RatingConverter()
            self.do_conversion = True
        self.km = KeyManager.instance()
        timeaction.end()
        SuspendableThread.__init__(self,
                                   name=name)
    # end __init__

    def do_run (self):
        debug('Running ing hooks',0)
        for i in self.added_ings:
            for h in self.rd_orig_ing_hooks:
                h(i)
        #debug('Running rec hooks',0)
        #for r in self._added_recs:
        #    for h in self.rd_orig_hooks:
        #        h(r)
        self.rd.add_ing_hooks = self.rd_orig_ing_hooks
        #self.rd.add_hooks = self.rd_orig_hooks
        #print_timer_info()

    def _run_cleanup_ (self):
        if self.do_conversion:
            # if we have something to convert
            if self.rating_converter.to_convert:
                self.rating_converter.do_conversions(self.rd)

    def check_for_sleep (self):
        timeaction = TimeAction('importer.check_for_sleep',10)
        #gt.gtk_update()
        if self.terminated:
            raise Terminated("Importer Terminated!")
        while self.suspended:
            #gt.gtk_update()
            if self.terminated:
                raise Terminated("Importer Terminated!")
            else:
                time.sleep(1)
        timeaction.end()

    def start_rec (self, dict=None):
        self.rec_timer = TimeAction('importer RECIPE IMPORT',10)
        timeaction = TimeAction('importer.start_rec',10)
        self.check_for_sleep()
        if hasattr(self,'added_ings') and self.added_ings:
            print('WARNING: starting new rec, but we have ingredients that we never added!')
            print('Unadded ingredients: ',self.added_ings)
        self.added_ings=[]
        self.group = None
        if dict:
            self.rec=dict
        else:
            self.rec = {}
        #if not self.rec.has_key('id'):
        #else:
        #    self.rec['id']=self.rd.new_id()
        #debug('New Import\'s ID=%s'%self.rec['id'],0)
        timeaction.end()

    def _move_to_instructions (self, recdic, attr):
        """A convenience method to shift information from an attribute
        to instructions.

        This is frequently a fallback for bad input -- we try to make
        sure we don't lose data this way."""
        # We add e.g. "Servings: lots" to instructions -- REC_ATTR_DIC
        # gets us the properly i18n'd name
        text_to_add = gourmet.gglobals.REC_ATTR_DIC['yields' if attr=='servings'
                                                    else attr] \
                      +': '+recdic[attr]
        if 'instructions' not in recdic:
            recdic['instructions']=text_to_add
        else:
            recdic['instructions']=recdic['instructions']+'\n'+text_to_add
        del recdic[attr]

    def commit_rec (self):
        timeaction = TimeAction('importer.commit_rec',10)
        for key in ['cuisine','category','title']:
            if key in self.rec:
                self.rec[key]=str(re.sub(r'\s+',' ',self.rec[key]).strip())
        # if yields/servings can't be recognized as a number, add them
        # to the instructions.
        if 'yields' in self.rec:
            try:
                self.rec['yields'] = float(self.rec['yields'])
            except:
                yields,yield_unit = self.parse_yields(self.rec['yields'])
                if not yields:
                    print('Moving yields to instructions!')
                    self._move_to_instructions(self.rec,'yields')
                else:
                    self.rec['yields'] = yields
                    self.rec['yield_unit'] = yield_unit
        if 'servings' in self.rec:
            servs=self.convert_str_to_num(self.rec['servings'])
            if servs != None:
                self.rec['yields'] = float(servs)
                self.rec['yield_unit'] = gettext.ngettext('serving',
                                                          'servings',
                                                          servs)
                del self.rec['servings']
            else:
                self._move_to_instructions(self.rec,'servings')
        # Check preptime and cooktime
        for t in ['preptime','cooktime']:
            if t in self.rec and not isinstance(self.rec[t], int):
                secs = self.conv.timestring_to_seconds(self.rec[t])
                if secs != None:
                    self.rec[t]=secs
                else:
                    self._move_to_instructions(self.rec,t)
        # Markup instructions and mods as necessary
        if self.do_markup:
            for k in ['instructions','modifications']:
                if k in self.rec: self.rec[k] = xml.sax.saxutils.escape(self.rec[k])
        # A little strange, this is, but for UI reasons, we want to
        # keep track of any ratings that are not integers so that we
        # can ask the user how to convert them when we're all done
        # with importing.
        remembered_rating = None
        if 'rating' in self.rec and not isinstance(self.rec['rating'], (int, float)):
            if string_to_rating(self.rec['rating']):
                self.rec['rating']=string_to_rating(self.rec['rating'])
            else:
                remembered_rating = self.rec['rating']
                del self.rec['rating']
        tt=TimeAction('importer.commit_rec - rd.add_rec',5)
        debug('commiting recipe %s'%self.rec,0)
        # Check for images without thumbnails
        if self.rec.get('image',None) and not self.rec.get('thumb',None):
            if not self.rec['image']: del self.rec['image']
            else:
                img = image_utils.bytes_to_image(self.rec['image'])
                if img:
                    thumb = img.copy()
                    thumb.thumbnail((40, 40))
                    self.rec['thumb'] = image_utils.image_to_bytes(thumb)
                    # Make sure our image is properly formatted...
                    self.rec['image'] = image_utils.image_to_bytes(img)
                else:
                    print("ODD: we got no image from ",self.rec['image'][:100])
                    print('Deleting "image"')
                    del self.rec['image']
                    del self.rec['thumb']
        ## if we have an ID, we need to remember it for the converter
        if 'id' in self.rec:
            id_to_convert = self.rec['id']
        else:
            id_to_convert = None
        if id_to_convert:
            if self.rec['id'] in self.id_converter:
                self.rec['id']=self.id_converter[self.rec['id']]
                r = self.rd.add_rec(self.rec,accept_ids=True) # See doc on add_rec
            else:
                del self.rec['id']
                r =  self.rd.add_rec(self.rec)
                self.id_converter[id_to_convert] = r.id
        else:
            r = self.rd.add_rec(self.rec)
        # Add ingredients...
        for i in self.added_ings:
            if 'id' in i:
                print('WARNING: Ingredient has ID set -- ignoring value')
                del i['id']
            i['recipe_id'] = r.id
        self.rd.add_ings(self.added_ings)
        self.added_ings = []
        # Update hash-keys...
        self.rd.update_hashes(r)
        tt.end()
        self.added_recs.append(r)
        if remembered_rating: self.rating_converter.add(r.id,remembered_rating)
        self.check_for_sleep()
        timeaction.end()
        self.rec_timer.end()
        self.count += 1
        if self.total:
            self.emit(
                'progress',
                float(self.count)/self.total,
                _("Imported %s of %s recipes.")%(self.count,self.total)
                )

    def parse_yields (self, str):
        '''Parse number and field.'''
        m = re.match(r"(?P<prefix>\w+\s+)?(?P<num>[0-9/. ]+)(?P<unit>\s*\w+)?",str)
        if m:
            num = m.group('num')
            num = convert.frac_to_float(num)
            unit = (m.group('unit') or '').strip()
            prefix = (m.group('prefix') or '').strip()
            if not unit:
                if prefix in ['Serves','Feeds']:
                    unit = 'servings'
            elif prefix:
                if prefix not in ['Makes','Yields']:
                    print('Warning: parse_yields ignoring prefix, "%(prefix)s" in "%(str)s"'%locals())
            if not unit: unit='servings' # default/fallback
            return num,unit
        else:
            return None,None

    def convert_str_to_num (self, str):
        """Return a numerical servings value"""
        timeaction = TimeAction('importer.convert_str_to_num',10)
        debug('converting servings for %s'%str,5)
        try:
            return float(str)
        except:
            conv = convert.frac_to_float(str)
            if conv: return conv
            m=re.match("([0-9/. ]+)",str)
            if m:
                num=m.groups()[0]
                try:
                    return float(num)
                except:
                    return convert.frac_to_float(num)
        timeaction.end()

    def start_ing (self, **kwargs):
        timeaction = TimeAction('importer.start_ing',10)
        #gt.gtk_update()
        self.ing=kwargs
        #if self.ing.has_key('id'):
        #    self.ing['recipe_id']=self.ing['id']
        #    del self.ing['id']
        #    print 'WARNING: setting ingredients ID is deprecated. Assuming you mean to set recipe_id'
        #elif self.rec.has_key('id'):
        #    self.ing['recipe_id']=self.rec['id']
        #debug('ing ID %s, recipe ID %s'%(self.ing['recipe_id'],self.rec['id']),0)
        timeaction.end()

    def finish_ing (self):
        timeaction = TimeAction('importer.finish_ing 1',10)
        # Strip whitespace...
        for key in ['item','ingkey','unit']:
            if key in self.ing:
                self.ing[key]=re.sub(r'\s+',' ',self.ing[key]).strip()
        if not (
            ('refid' in self.ing and
             self.ing['refid'])
            or
            ('ingkey' in self.ing and
             self.ing['ingkey'])
            ):
            #self.ing['ingkey']=self.km.get_key(self.ing['item'],0.9)
            if 'item' in self.ing:
                self.ing['ingkey']=self.km.get_key_fast(self.ing['item'])
            else:
                debug('Ingredient has no item! %s'%self.ing,-1)
        timeaction.end()
        # if we have an amount (and it's not None), let's convert it
        # to a number
        if 'amount' in self.ing and self.ing['amount']\
               and 'rangeamount' not in self.ing:
            if convert.RANGE_MATCHER.search(str(self.ing['amount'])):
                self.ing['amount'],self.ing['rangeamount']=parse_range(self.ing['amount'])
        if 'amount' in self.ing:
            self.ing['amount']=convert.frac_to_float(
                self.ing['amount']
                )
        if 'rangeamount' in self.ing:
            self.ing['rangeamount']=convert.frac_to_float(
                self.ing['rangeamount']
                )
        timeaction = TimeAction('importer.commit_ing 2',10)
        if not ('position' in self.ing and self.ing['position']):
            self.ing['position']=self.position
            self.position+=1
        timeaction.end()
        timeaction = TimeAction('importer.commit_ing 3',10)
        if self.group:
            self.ing['inggroup']=self.group
        timeaction.end()
        timeaction = TimeAction('importer.commit_ing 4',10)
        self.added_ings.append(self.ing); self.ing = {}
        timeaction.end()

    commit_ing = finish_ing

    def add_amt (self, amount):
        timeaction = TimeAction('importer.add_amt',10)
        """We should NEVER get non-numeric amounts.
        Amounts must contain [/.0-9 ] e.g. 1.2 or 1 1/5
        or 1/3 etc."""
        #gt.gtk_update()
        self.ing['amount'],self.ing['rangeamount']=parse_range(amount)
        timeaction.end()

    def add_ref (self, id):
        timeaction = TimeAction('importer.add_ref',10)
        if id not in self.id_converter:
            self.id_converter[id]=self.rd.new_id()
        self.ing['refid']=self.id_converter[id]
        self.ing['unit']='recipe'
        timeaction.end()

    def add_item (self, item):
        timeaction = TimeAction('importer.add_item',10)
        itm=str(item.strip())
        itm=itm.replace("\n"," ")
        self.ing['item']=itm
        timeaction.end()

    def add_unit (self, unit):
        timeaction = TimeAction('importer.add_unit',10)
        self.ing['unit']=str(unit.strip())
        timeaction.end()

    def add_key (self, key):
        timeaction = TimeAction('importer.add_key',10)
        self.ing['ingkey']=str(key.strip())
        timeaction.end()

    def terminate (self):
        timeaction = TimeAction('importer.terminate',10)
        debug('Terminate!',0)
        self.terminated = True
        timeaction.end()

    def suspend (self):
        timeaction = TimeAction('importer.suspend',10)
        debug('Suspend!',0)
        self.suspended = True
        timeaction.end()
        print_timer_info()

    def resume (self):
        debug('Resume!',0)
        self.suspended = False

NUMBER_REGEXP = convert.NUMBER_REGEXP
simple_matcher = re.compile(
    r'(%(NUMBER_REGEXP)s+)\s*/\s*([\d]+)'%locals()
    )

def parse_range (number_string):
    """Parse a range and return a tuple with a low and high number as floats.

    We will also parse regular numbers, in which case the tuple will
    only have one item.
    """
    if isinstance(number_string, (int, float)):
        return (float(number_string),None)
    nums=convert.RANGE_MATCHER.split(number_string.strip())
    if len(nums) > 2:
        debug('WARNING: String %s does not appear to be a normal range.'%number_string,0)
        retval = list(map(convert.frac_to_float,nums))
        # filter any non-numbers before we take 1 and 3
        retval = [x for x in retval if x]
        if len(retval) > 2:
            debug('Parsing range as %s-%s'%(retval[0],retval[-1]),0)
            retval = retval[0],retval[-1]
    else:
        retval = list(map(convert.frac_to_float,nums))
    if len(retval)==2: return tuple(retval)
    elif len(retval)==1: return tuple(retval+[None])
    else: return (None,None)

class Tester:
    def __init__ (self, regexp):
        self.regexp = regexp

    def test (self, filename):
        if not hasattr(self,'matcher'):
            # only compile our regexp when necessary
            self.matcher = re.compile(self.regexp)
        CLOSE=False
        if isinstance(filename, str):
            # Latin-1 can decode any bytes, letting us open ASCII-compatible
            # text files and sniff their contents - e.g. for XML tags -
            # without worrying too much about their real text encoding.
            ofi = open(filename, 'r', encoding='latin1')
            CLOSE=True
        else:
            ofi = filename

        try:
            for l in ofi:
                if self.matcher.match(l):
                    return True
        finally:
            if CLOSE:
                ofi.close()
            else:
                ofi.seek(0)

class RatingConverter:

    """A class to handle converting ratings from strings to integers.

    This is here since many of our imports will grab ratings for us in
    the form of 'excellent' or some such, and we'll want to let our
    user convert those to stars as they see fit.
    """

    conversions = {'excellent':10,
                   'great':8,
                   'good':6,
                   'fair':4,
                   'okay':4,
                   'poor':2,
                   _('excellent').lower():10,
                   _('great').lower():8,
                   _('good').lower():6,
                   _('fair').lower():4,
                   _('okay').lower():4,
                   _('poor').lower():2,
                   }

    def __init__ (self):
        self.to_convert = {}
        self.got_conversions = False

    def add (self, id, rating):
        if isinstance(rating, int):
            raise Exception("Why do you need me? id: %(id)s rating: %(rating)s" % locals())
        self.to_convert[id]=rating

    def get_conversions (self, star_generator=None):
        """Get our conversions.

        If necessary, ask user to convert for us.
        """
        self.got_conversions=True
        if not star_generator:
            from gourmet.gtk_extras.ratingWidget import star_generator
        ratings = []
        need_conversions = False
        for v in list(self.to_convert.values()):
            if not need_conversions and v.lower() not in self.conversions:
                need_conversions = True
            if v not in ratings:
                ratings.append(v)
                conv = string_to_rating(v)
                if conv: self.conversions[v] = conv
        if need_conversions:
            self.conversions = de.get_ratings_conversion(ratings,star_generator,defaults=self.conversions)

    def do_conversions (self, db):
        if not self.got_conversions:
            self.get_conversions()
        for id,rating in list(self.to_convert.items()):
            try:
                if rating not in self.conversions and hasattr(rating,'lower') and rating.lower() in self.conversions:
                    rating = rating.lower()
                db.modify_rec(db.get_rec(id),{'rating':self.conversions[rating]})
            except:
                print('wtf... problem with rating ',rating,'for recipe',id)
                raise


class RatingConverterTest (unittest.TestCase):

    def setUp (self):

        class FakeDB:

            recs = dict([(n,{}) for n in range(20)])

            def get_rec (self, n): return n
            def modify_rec (self, n, d):
                for attr,val in list(d.items()): self.recs[n][attr]=val

        self.db = FakeDB()

    def testAutomaticConverter (self):
        rc = RatingConverter()
        tests = ['good','Great','Excellent','poor','okay']
        for n,rating in enumerate(tests):
            rc.add(n,rating)
            self.db.recs[n]['rating']=rating
        total = n
        rc.do_conversions(self.db)
        print('Conversions: ')
        for n,rating in enumerate(tests):
            print('Converted',rating,'->',self.db.recs[n]['rating'])

    def testInteractiveConverter (self):
        rc = RatingConverter()
        tests = ['alright','pretty good','funny tasting',
                 'okeydokey','not bad','damn good.']
        for n,rating in enumerate(tests):
            rc.add(n,rating)
            self.db.recs[n]['rating']=rating
        total = n
        rc.do_conversions(self.db)
        #print 'Conversions: '
        #for n,rating in enumerate(tests):
        #    print 'Converted',rating,'->',self.db.recs[n]['rating']

    def testStringToRatingConverter (self):
        assert(string_to_rating('4/5 stars')==8)
        assert(string_to_rating('3 1/2 / 5 stars')==7)
        assert(string_to_rating('4/10 stars')==4)

class ImporterTest (unittest.TestCase):

    def setUp (self):
        self.importer = Importer()

    def testParseSimpleYields (self):
        assert(self.importer.parse_yields('3 cups')==(3, 'cups'))
        assert(self.importer.parse_yields('7 servings')==(7,'servings'))
        assert(self.importer.parse_yields('12 muffins')==(12,'muffins'))
        assert(self.importer.parse_yields('10 loaves')==(10,'loaves'))

    def testParseComplexYields (self):
        assert(self.importer.parse_yields('Makes 12 muffins')==(12,'muffins'))
        assert(self.importer.parse_yields('Makes 4 servings')==(4,'servings'))
        assert(self.importer.parse_yields('Serves 7')==(7,'servings'))


if __name__ == '__main__':
    unittest.main()
