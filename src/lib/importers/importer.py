#!/usr/bin/python
import os,stat,re,time,StringIO
from gourmet import keymanager, convert, ImageExtras
from gourmet.gdebug import debug, TimeAction, print_timer_info
from gourmet.gglobals import gt, use_threads
import xml.sax.saxutils
from gettext import gettext as _
import gourmet.dialog_extras as de
import re

class importer:

    """Base class for all importers. We provide an interface to the recipe database
    for importers to use. Basically, the importer builds up a dictionary of properties inside of
    self.rec and then commits that dictionary with commit_rec(). Similarly, ingredients are built
    as self.ing and then committed with commit_ing()."""
    
    def __init__ (self, rd, threaded=False, total=0, prog=None, do_markup=True,conv=None,rating_converter=None):
        """rd is our recipeData instance. Total is used to keep track of progress
        with function progress. do_markup should be True if instructions and modifications
        come to us unmarked up (i.e. if we need to escape < and &, etc."""

        timeaction = TimeAction('importer.__init__',10)
        if not conv: self.conv = convert.converter()
        self.id_converter = {} # a dictionary for tracking named IDs
        self.total = total
        self.prog = prog
        self.do_markup=do_markup
        self.count = 0
        self.rd=rd
        self.rd_orig_ing_hooks = self.rd.add_ing_hooks
        self.added_recs=[]
        self.added_ings=[]
        #self.rd_orig_hooks = self.rd.add_hooks
        self.rd.add_ing_hooks = []
        #self.rd.add_hooks = []
        self.position=0
        self.group=None
        self.threaded=threaded
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
        
        if hasattr(self.rd,'km'):
            debug('Using existing keymanager',2)
            self.km=self.rd.km
        else:
            debug('Making new keymanager',2)
            self.km=keymanager.KeyManager(rm=self.rd)
        if not self.threaded:
            ## run ourselves, unless we're threaded, in which
            ## case we'll want to call run explicitly from outside.
            self.run()
            self._run_cleanup_()
        timeaction.end()
    # end __init__

    def run (self):
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
        gt.gtk_update()
        if self.terminated:
            raise gt.Terminated("Importer Terminated!")
        while self.suspended:
            gt.gtk_update()
            if self.terminated:
                raise gt.Terminated("Importer Terminated!")
            if not use_threads:
                # we only sleep a little while if we're suspended!
                time.sleep(0.1)
            else:
                time.sleep(1)
        timeaction.end()

    def start_rec (self, dict=None):
        self.rec_timer = TimeAction('importer RECIPE IMPORT',10)
        timeaction = TimeAction('importer.start_rec',10)
        self.check_for_sleep()
        self.added_ings=[]
        self.group = None
        if dict:
            self.rec=dict
        else:
            self.rec = {}
        #if not self.rec.has_key('id'):
        # always create a new ID     
        if self.rec.has_key('id'):
            if self.id_converter.has_key(self.rec['id']):
                self.rec['id']=self.id_converter[self.rec['id']]
            else:
                real_id = self.rd.new_id()
                self.id_converter[self.rec['id']]=real_id
                self.rec['id']=real_id
        else:
            self.rec['id']=self.rd.new_id()
        debug('New Import\'s ID=%s'%self.rec['id'],0)
        timeaction.end()

    def _move_to_instructions (self, recdic, attr):
        """A convenience method to shift information from an attribute
        to instructions.

        This is frequently a fallback for bad input -- we try to make
        sure we don't lose data this way."""
        if not recdic.has_key('instructions'):
            recdic['instructions']=recdic[attr]
        else:
            recdic['instructions']=recdic['instructions']+'\n'+recdic[attr]
        del recdic[attr]

    def commit_rec (self):
        timeaction = TimeAction('importer.commit_rec',10)
        # if servings can't be recognized as a number, add them to the
        # instructions.
        for key in ['cuisine','category','title']:
            if self.rec.has_key(key):
                self.rec[key]=re.sub('\s+',' ',self.rec[key]).strip()
        if self.rec.has_key('servings'):
            servs=self.convert_servings(self.rec['servings'])
            if servs:
                self.rec['servings']=str(servs)
            else:
                self._move_to_instructions(self.rec,'servings')
        # Check preptime and cooktime
        for t in ['preptime','cooktime']:
            if self.rec.has_key(t) and type(self.rec[t])!=int:
                secs = self.conv.timestring_to_seconds(self.rec[t])
                if secs:
                    self.rec[t]=secs
                else:
                    self._move_to_instructions(self.rec,t)
        # Markup instructions and mods as necessary
        if self.do_markup:
            for k in ['instructions','modifications']:
                if self.rec.has_key(k): self.rec[k] = xml.sax.saxutils.escape(self.rec[k])
        # A little strange, this is, but for UI reasons, we want to
        # keep track of any ratings that are not integers so that we
        # can ask the user how to convert them when we're all done
        # with importing.              
        remembered_rating = None
        if self.rec.has_key('rating') and type(self.rec['rating']) not in [int,float]:
            if string_to_rating(self.rec['rating']):
                self.rec['rating']=string_to_rating(self.rec['rating'])
            else:
                remembered_rating = self.rec['rating']
                del self.rec['rating']
        tt=TimeAction('importer.commit_rec - rd.add_rec',5)
        debug('commiting recipe %s'%self.rec,0)
        r = self.rd.add_rec(self.rec)
        tt.end()
        self.added_recs.append(r)
        if remembered_rating: self.rating_converter.add(r.id,remembered_rating)
        self.check_for_sleep()
        timeaction.end()
        self.rec_timer.end()
        self.count += 1
        if self.prog and self.total:
            self.prog(float(self.count)/self.total,
                      _("Imported %s of %s recipes."%(self.count,self.total))
                      )

    def convert_servings (self, str):
        """Return a numerical servings value"""
        timeaction = TimeAction('importer.convert_servings',10)
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
        gt.gtk_update()
        self.ing=kwargs
        self.ing['id']=self.rec['id']
        debug('ing ID %s, recipe ID %s'%(self.ing['id'],self.rec['id']),0)
        timeaction.end()
                 
    def commit_ing (self):
        timeaction = TimeAction('importer.commit_ing 1',10)
        # Strip whitespace...
        for key in ['item','ingkey','unit']:
            if self.ing.has_key(key):
                self.ing[key]=re.sub('\s+',' ',self.ing[key]).strip()
        if not (
            (self.ing.has_key('refid') and
             self.ing['refid'])
            or
            (self.ing.has_key('ingkey') and
             self.ing['ingkey'])
            ):
            #self.ing['ingkey']=self.km.get_key(self.ing['item'],0.9)
            if self.ing.has_key('item'):
                self.ing['ingkey']=self.km.get_key_fast(self.ing['item'])
            else:
                debug('Ingredient has no item! %s'%self.ing,-1)
        timeaction.end()
        # if we have an amount (and it's not None), let's convert it
        # to a number
        if self.ing.has_key('amount') and self.ing['amount']\
               and not self.ing.has_key('rangeamount'):
            if convert.RANGE_MATCHER.search(str(self.ing['amount'])):
                self.ing['amount'],self.ing['rangeamount']=parse_range(self.ing['amount'])
        if self.ing.has_key('amount'):
            self.ing['amount']=convert.frac_to_float(
                self.ing['amount']
                )
        if self.ing.has_key('rangeamount'):
            self.ing['rangeamount']=convert.frac_to_float(
                self.ing['rangeamount']
                )
        timeaction = TimeAction('importer.commit_ing 2',10)
        if not (self.ing.has_key('position') and self.ing['position']):
            self.ing['position']=self.position
            self.position+=1
        timeaction.end()
        timeaction = TimeAction('importer.commit_ing 3',10)
        if self.group:
            self.ing['inggroup']=self.group
        timeaction.end()
        timeaction = TimeAction('importer.commit_ing 4',10)
        self.added_ings.append(self.rd.add_ing(self.ing))
        timeaction.end()
        

    def add_amt (self, amount):
        timeaction = TimeAction('importer.add_amt',10)
        """We should NEVER get non-numeric amounts.
        Amounts must contain [/.0-9 ] e.g. 1.2 or 1 1/5
        or 1/3 etc."""
        gt.gtk_update()
        self.ing['amount'],self.ing['rangeamount']=parse_range(amount)
        timeaction.end()

    def add_ref (self, id):
        timeaction = TimeAction('importer.add_ref',10)
        if not self.id_converter.has_key(id):
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
    '(%(NUMBER_REGEXP)s+)\s*/\s*([\d]+)'%locals()
    )

def string_to_rating (s):
    m = simple_matcher.match(s)
    if m:
        top=float(convert.frac_to_float(m.groups()[0]))
        bottom = float(convert.frac_to_float(m.groups()[2]))
        return int(top/bottom * 10)

            
        
        
        
        
    


class MultipleImporter:
    def __init__ (self,grm,imports):
        """GRM is a GourmetRecipeManager instance.
        
        Imports is a list of classes to run and filenames.
        [(class,args,kwargs),filename]

        The classes will be initiated: c=class(*args,**kwargs) and
        then run with c.run()
        """
        self.imports = imports
        self.grm = grm
        self.total_size = 0
        self.current_prog = 0
        self.sizes = {}
        self.completed_imports = 0
        self.current_imports = 0
        self.completed_imports_last_fn = ""
        self.num_matcher = re.compile('(%s+)'%convert.NUMBER_REGEXP)
        for c,fn in imports:
            if fn and type(fn)==str:
                size = os.stat(fn)[stat.ST_SIZE]
                self.total_size += size
                self.sizes[fn]=size

    def run (self):
        for importer,fn in self.imports:
            ic,args,kwargs = importer
            self.fn = fn
            if self.total_size: self.current_percentage = float(self.sizes.get(fn,-1))/self.total_size
            else: self.current_percentage = -1
            gt.gtk_enter()
            if self.grm.progress_dialog.detail_label:
                self.grm.progress_dialog.detail_label.set_text(_('<i>Importing %s</i>')%fn)
                self.grm.progress_dialog.detail_label.set_use_markup(True)
            #self.grm.progress_dialog.label.set_text(_('<i>Importing %s</i>')%fn)
            gt.gtk_leave()
            print 'Using import class ',ic
            kwargs['progress']=self.show_progress
            self.iclass = ic(*args,**kwargs)
            self.suspend = self.iclass.suspend
            self.terminate = self.iclass.terminate
            self.resume = self.iclass.resume
            self.iclass.run()
            self.current_prog += self.current_percentage
        self.grm.set_progress_thr(1,'Import complete!')
    
    def show_progress (self, prog, msg):
        if len(self.imports)>1:
            # we muck about with the messages if we have more than one...            
            m=self.num_matcher.search(msg)
            if not m: msg=""
            elif m.groups()[0]:
                if self.fn != self.completed_imports_last_fn:
                    self.completed_imports_last_fn = self.fn
                    self.completed_imports += self.current_imports
                try:
                    self.current_imports=int(m.groups()[0])
                except:
                    pass
                else:
                    total = self.current_imports + self.completed_imports
                    if self.completed_imports:
                        msg = _("Imported %(number)s recipes from %(file)s (%(total)s total)")%{
                            'number':self.current_imports,
                            'total':total,
                            'file':os.path.split(self.fn)[1]
                            }
        self.grm.set_progress_thr(self.current_prog + (prog * self.current_percentage),
                  msg)
        

def parse_range (number_string):
    """Parse a range and return a tuple with a low and high number as floats.

    We will also parse regular numbers, in which case the tuple will
    only have one item.
    """
    if type(number_string) in [int,float]:
        return (float(number_string),None)
    nums=convert.RANGE_MATCHER.split(number_string.strip())
    if len(nums) > 2:
        debug('WARNING: String %s does not appear to be a normal range.'%number_string,0)
        retval = map(convert.frac_to_float,nums)
        # filter any non-numbers before we take 1 and 3
        retval = filter(lambda x: x, retval)        
        if len(retval) > 2:
            debug('Parsing range as %s-%s'%(retval[0],retval[-1]),0)
            retval = retval[0],retval[-1]
    else:
        retval = map(convert.frac_to_float,nums)
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
        if type(filename)==str:
            self.ofi = open(filename,'r')
            CLOSE=True
        else: self.ofi=filename
        l = self.ofi.readline()
        while l:
            if self.matcher.match(l):
                self.ofi.close()
                return True
            l = self.ofi.readline()
        if CLOSE:
            self.ofi.close()
        else:
            self.ofi.seek(0)
            
class RatingConverter:

    """A class to handle converting ratings from strings to integers.

    This is here since many of our imports will grab ratings for us in
    the form of 'excellent' or some such, and we'll want to let our
    user convert those to stars as they see fit.
    """
    
    conversions = {'excellent':5,
                   'great':4,
                   'good':3,
                   'fair':2,
                   'okay':2,
                   'poor':1,
                   _('Excellent').lower():5,
                   _('Great').lower():4,
                   _('Good').lower():3,
                   _('Fair').lower():2,
                   _('Poor').lower():1,
                   _('Okay').lower():2,
                   }
    

    def __init__ (self):
        self.to_convert = {}
        self.got_conversions = False

    def add (self, id, rating):
        self.to_convert[id]=rating

    def get_conversions (self, star_generator=None):
        """Get our conversions.

        If necessary, ask user to convert for us.
        """
        self.got_conversions=True
        if not star_generator:
            from gourmet.ratingWidget import star_generator
        ratings = []
        need_conversions = False
        for v in self.to_convert.values():
            if not need_conversions and not self.conversions.has_key(v.lower()):
                need_conversions = True
            if not v in ratings: ratings.append(v)
        if need_conversions:
            self.conversions = de.get_ratings_conversion(ratings,star_generator,defaults=self.conversions)

    def do_conversions (self, db):
        if not self.got_conversions:
            print 'Get conversion!'
            self.get_conversions()
        for id,rating in self.to_convert.items():
            try:
                db.modify_rec(db.get_rec(id),{'rating':self.conversions[str(rating).lower()]})
            except:
                print 'wtf... problem with rating ',rating,'for recipe',id
                raise

import unittest

class RatingConverterTest (unittest.TestCase):

    def setUp (self):

        class FakeDB:

            recs = dict([(n,{}) for n in range(20)])
            
            def get_rec (self, n): return n
            def modify_rec (self, n, d):
                for attr,val in d.items(): self.recs[n][attr]=val

        self.db = FakeDB()

    def testAutomaticConverter (self):
        rc = RatingConverter()
        tests = ['good','Great','Excellent','poor','okay']
        for n,rating in enumerate(tests):
            rc.add(n,rating)
            self.db.recs[n]['rating']=rating
        total = n
        rc.do_conversions(self.db)
        print 'Conversions: '
        for n,rating in enumerate(tests):
            print 'Converted',rating,'->',self.db.recs[n]['rating']

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


if __name__ == '__main__':
    unittest.main()
