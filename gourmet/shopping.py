import sys
from gourmet import convert
from gettext import gettext as _
from .gdebug import debug
import unittest, time

class Shopper:
    def __init__ (self, inglist):
        """We expect a list of tuples/lists, each of which contains
        amount, unit, key [[amt,un,key],[amt,un,key],...]

        amount can be either a single number or a tuple
        2,3, etc., in which case it is a range.
        """
        ## First, we create a dictionary from our list (keyed by ingredient)
        ## each value in the dict. is a list of values. We'll try to add these
        ## as best as we can.
        self.dic = {}
        self.default_pantry=[_('flour, all purpose'),_('sugar'),_('salt'),
                             _('black pepper, ground'),
                             _('ice'), _('water'),
                             _('oil, vegetable'),
                             _('oil, olive')]
        self.init_pantry()
        self.mypantry = {}
        for a, u, k in inglist:
            if self.pantry.has_key(k) and self.pantry[k]:
                # print "%s is in pantry" %k
                dic=self.mypantry
            else:
                dic=self.dic
            try:
                a = float(a)
            except:
                if not isinstance(a, tuple):
                    debug("Warning, can't make sense of amount %s; reading as None"%a,0)
                    a = None
            if k in dic:
                dic[k].append([a,u])
            else:
                dic[k]=[[a,u]]
        self.init_converter()
        for ing,amts in list(self.dic.items()):
            self.dic[ing]=self.combine_ingredient(ing,amts)
        for ing,amts in list(self.mypantry.items()):
            self.mypantry[ing]=self.combine_ingredient(ing,amts)
        self.init_orgdic()
        self.init_ingorder_dic()
        self.init_catorder_dic()

    def init_converter (self):
        self.cnv = convert.get_converter()

    def combine_ingredient (self, ing, amts):
        """We take an ingredient and a list of amounts. We return a
        list of amounts (ideally shortened, if combinifying is
        possible)."""
        itms = []
        for a,u in amts:
            if not itms:
                ## if this is our first...
                itms.append([a,u])
            else:
                flag = 0
                ind = 0
                while not flag and len(itms) > ind:
                    amt,unit = itms[ind]
                    if isinstance(amt, tuple) or isinstance(a, tuple):
                        # we're adding ranges -- we'll force both
                        # our amounts to look like ranges to simplify the addition
                        if not isinstance(amt, tuple):
                            amt=(amt,amt)
                        if not isinstance(a, tuple):
                            a=(a,a)
                        # print 'amt:',amt,' unit:',unit,'a:',a,'u:',u
                        add_low = self.cnv.add_reasonably(amt[0],unit,a[0],u,ing)
                        add_high = self.cnv.add_reasonably(amt[1],unit,a[1],u,ing)
                        if (not add_low) or (not add_high):
                            add = False
                        else:
                            # Adjust units
                            add_low = self.cnv.adjust_unit(
                                *add_low,   # lowest+lowest
                                **{'favor_current_unit':False}
                                )
                            add_high = self.cnv.adjust_unit(
                                *add_high,  # highest+highest
                                **{'favor_current_unit':False}
                                )
                            if add_low:
                                add_low = self.cnv.adjust_unit(*add_low,**{'favor_current_unit':False})
                            if add_high:
                                add_high = self.cnv.adjust_unit(*add_high,**{'favor_current_unit':False})
                            if add_low[1]==add_high[1]:  # same unit...
                                add=((add_low[0],add_high[0]),add_low[1])
                            else:
                                # otherwise, let's use our unit for add_high...
                                u1_to_u2=self.cnv.converter(add_low[1],add_high[1])
                                add=( (add_low[0]*u1_to_u2,add_high[0]),  # amount tuple
                                      add_high[1]  # unit from add_high
                                      )
                    else:
                        add = self.cnv.add_reasonably(amt,unit,a,u,ing)
                        if add:
                            # adjust unit to make readable
                            add=self.cnv.adjust_unit(*add,**{'favor_current_unit':False})
                    # add_reasonably returns a nice a,u pair if successful
                    # Otherwise, it return False/None
                    if add:
                        itms.pop(ind)     # out with the old...
                        itms.append(add)  # in with the new
                        flag = 1
                    else:
                        ind += 1
                if not flag:
                    itms.append([a,u])
        return itms

    def ing_to_string (self, ing, amts):
        return "%s %s" %(self.amt_to_string(amts),ing)

    def amt_to_string (self, amts):
        retstr = self.cnv.amt_string(amts[0])
        if len(amts) > 1:
            for a in amts[1:]:
                retstr = "%s + %s" %(self.cnv.amt_string(a), retstr)
        return retstr

    def pretty_print (self, out=sys.stdout):
        self.list_writer(
            write_category= lambda c: out.write("\n---\n%s\n---\n"%c),
            write_item = lambda a,i: out.write("%s %s\n"%(a,i))
            )

    def list_writer (self,
                      write_category,
                      write_item,):
        org = self.organize(self.dic)
        for c,d in org:
            if not c: c = _('Unknown')
            write_category(c.title())
            for i,a in d:
                write_item(a,i)

    def organize (self, dic=None):
        """We organize our ingredients into lists in the form.
           [Category, [[ingredient, amt],
                       [ingredient, amt]...
                      ]
           ]"""
        ## first we build a dictionary, since it gives us an
        ## easy way to sort by category
        cats = {}
        if not dic:
            pass
        for i,a in list(dic.items()):
            if self.orgdic.has_key(i) and self.orgdic[i]:
                c = self.orgdic[i]
            else:
                c = _("Unknown")
            if c in cats:
                cats[c][i]=a
            else:
                cats[c]={i:a}
        ## next we turn our nested dictionaries into nested lists
        lst = []
        for c,d in list(cats.items()):
            itms = []
            for i,amts in list(d.items()):
                itms.append([i,self.amt_to_string(amts)])
            lst.append([c,itms])
        ## now that we have lists, we can sort them
        from functools import cmp_to_key
        lst.sort(key=cmp_to_key(self._cat_compare))
        for l in lst:
            l[1].sort(key=cmp_to_key(self._ing_compare))
        return lst

    def _cat_compare (self,cata,catb):
        """Put two categories in order"""
        cata = cata[0]
        catb = catb[0]
        if not cata and not catb: return 0
        elif not cata: return 1
        elif not catb: return -1
        if cata in self.catorder_dic and catb in self.catorder_dic:
            # if both categories have known positions, we use them to compare
            cata = self.catorder_dic[cata]
            catb = self.catorder_dic[catb]
        else:
            # otherwise, we just use > to sort alphabetically
            cata = cata.lower()
            catb = catb.lower()
        if cata > catb: return 1
        if cata == catb: return 0
        else: return -1

    def _ing_compare (self,inga,ingb):
        """Put two ingredients in order"""
        inga = inga[0]
        ingb = ingb[0]
        if False and inga in self.ingorder_dic and ingb in self.ingorder_dic:
            # if both ings have known positions, we use them to compare
            inga = self.ingorder_dic[inga]
            ingb = self.ingorder_dic[ingb]
        else:
            # otherwise, we just use > to sort alphabetically
            inga = inga.lower()
            ingb = ingb.lower()
        if inga > ingb: return 1
        if inga == ingb: return 0
        else: return -1


    def get_porg_categories (self):
        """Return a list of categories used for sorting."""
        tmp = {}
        for v in list(self.orgdic.values()):
            tmp[v]=1
        return list(tmp.keys())

    def add_org_itm (self, itm, cat):
        self.orgdic[itm]=cat
        # for k,v in self.orgdic.items():
            # print "%s:%s, "%(k,v)

    def add_to_pantry (self, key):
        self.pantry[key]=True

    def remove_from_pantry (self, key):
        self.pantry[key]=False

    def init_orgdic (self):
        """This allows those subclassing us to do something fancy...
        as is, we just use a default dictionary."""
        self.default_orgdic = setup_default_orgdic()
        self.orgdic = self.default_orgdic

    def init_ingorder_dic (self):
        self.ingorder_dic = {}
    def init_catorder_dic (self):
        debug("Initializing empty catorder_dic",5)
        self.catorder_dic = {}

    def init_pantry (self):
        self.pantry={}
        for i in self.default_pantry:
            self.pantry[i]=True

    def get_orgcats (self):
        """Return a list of categories being used for our Shopper"""
        self.orgcats=[]
        for v in list(self.orgdic.values()):
            if v and (v not in  self.orgcats):
                self.orgcats.append(v)
        self.orgcats.sort()
        return self.orgcats

def setup_default_orgdic ():
    from .defaults.defaults import lang as defaults
    return defaults.shopdic

class ShoppingList:

    def __init__ (self):
        self.recs = {}; self.extras = []
        self.includes = {}
        self.data,self.pantry=self.grabIngsFromRecs([])
        from . import backends
        self.rd = backends.db.get_database()
        from . import prefs
        self.prefs = prefs.Prefs.instance()

    def get_shopper (self, lst):
        return Shopper(lst)

    def grabIngsFromRecs (self, recs, start=[]):
        debug("grabIngsFromRecs (self, recs):",5)
        """Handed an array of (rec . mult)s, we combine their ingredients.
        recs may be IDs or objects."""
        self.lst = start[0:]
        for rec,mult in recs:
            self.lst.extend(self.grabIngFromRec(rec,mult=mult))
        return self.organize_list(self.lst)

    def organize_list (self, lst):
        self.sh = self.get_shopper(lst)
        data = self.sh.organize(self.sh.dic)
        pantry = self.sh.organize(self.sh.mypantry)
        debug("returning: data=%s pantry=%s"%(data,pantry),5)
        return data,pantry

    def grabIngFromRec (self, rec, mult=1):
        """Get an ingredient from a recipe and return a list with our amt,unit,key"""
        """We will need [[amt,un,key],[amt,un,key]]"""
        debug("grabIngFromRec (self, rec=%s, mult=%s):"%(rec,mult),5)
        # Grab all of our ingredients
        ings = self.rd.get_ings(rec)
        lst = []
        include_dic = self.includes.get(rec.id) or {}
        for i in ings:
            if hasattr(i,'refid'): refid=i.refid
            else: refid=None
            debug("adding ing %s, %s"%(i.item,refid),4)
            if i.optional:
                # handle boolean includes value which applies to ALL ingredients
                if not include_dic:
                    continue
                if isinstance(include_dic, dict):
                    # Then we have to look at the dictionary itself...
                    if ((i.ingkey not in include_dic)
                        or
                            not include_dic[i.ingkey]):
                        # we ignore our ingredient (don't add it)
                        continue
            if self.rd.get_amount(i):
                amount=self.rd.get_amount(i,mult=mult)
            else: amount=None
            if refid:
                ## a reference tells us to get another recipe
                ## entirely.  it has two parts: i.item (regular name),
                ## i.refid, i.refmult (amount we multiply recipe by)
                ## if we don't have the reference (i.refid), we just
                ## output the recipe name
                debug("Grabbing recipe as ingredient!",2)
                # disallow recursion
                subrec = self.rd.get_referenced_rec(i)
                if subrec.id == rec.id:
                    de.show_message(
                        label=_('Recipe calls for itself as an ingredient.'),
                        sublabel=_('Ingredient %s will be ignored.')%rec.title + _('Infinite recursion is not allowed in recipes!'))
                    continue
                if subrec:
                    # recipe refs need an amount. We'll
                    # assume if need be.
                    amt = self.rd.get_amount_as_float(i)
                    if not amt: amount=amt
                    refmult=mult*amt
                    if subrec.id not in include_dic:
                        d = self.getOptionalDic(self.rd.get_ings(subrec),
                                                refmult,
                                                self.prefs,
                                                )
                        include_dic[subrec.id]=d
                    nested_list=self.grabIngFromRec(subrec,
                                                    refmult)
                    lst.extend(nested_list)
                    continue
                else:
                    # it appears we don't have this recipe
                    debug("We don't have recipe %s"%i.item,0)
                    if not i.unit:
                        i.unit='recipe'
                    if not i.ingkey:
                        i.ingkey=i.item
            lst.append([amount,i.unit,i.ingkey])
        debug("grabIngFromRec returning %s"%lst,5)
        return lst

    def getOptionalDic (self, ivw, mult, prefs):
        """Return a dictionary of optional ingredients with a TRUE|FALSE value

        Alternatively, we return a boolean value, in which case that is
        the value for all ingredients.

        The dictionary will tell us which ingredients to add to our shopping list.
        We look at prefs to see if 'shop_always_add_optional' is set, in which case
        we don't ask our user."""
        return True

    # Saving and printing
    def doSave (self, filename):
        debug("doSave (self, filename):",5)
        # import exporters.lprprinter
        # self._printList(exporters.lprprinter.SimpleWriter,file=filename,show_dialog=False)
        with open(filename,'w') as ofi:
            ofi.write(_("Shopping list for %s") % time.strftime("%x") + '\n\n')
            ofi.write(_("For the following recipes:"+'\n'))
            ofi.write('--------------------------------\n')
            for r,mult in list(self.recs.values()):
                itm = "%s"%r.title
                if mult != 1:
                    itm += _(" x%s")%mult
                ofi.write(itm+'\n')
            write_itm = lambda a,i: ofi.write("%s %s"%(a,i) + '\n')
            write_subh = lambda h: ofi.write('\n_%s_\n'%h)
            self.sh.list_writer(write_subh,write_itm)

    def _printList (self, printer, *args, **kwargs):
        w = printer(*args,**kwargs)
        w.write_header(_("Shopping list for %s")%time.strftime("%x"))
        w.write_subheader(_("For the following recipes:"))
        for r,mult in list(self.recs.values()):
            itm = "%s"%r.title
            if mult != 1:
                itm += _(" x%s")%mult
            w.write_paragraph(itm)
        write_itm = lambda a,i: w.write_paragraph("%s %s"%(a,i))
        self.sh.list_writer(w.write_subheader,write_itm)
        w.close()

    # Setting up recipe...
    def addRec (self, rec, mult, includes={}):
        debug("addRec (self, rec, mult, includes={}):",5)
        """Add recipe to our list, assuming it's not already there.
        includes is a dictionary of optional items we want to include/exclude."""
        if rec.id in self.recs:
            _, mult_already = self.recs[rec.id]
            mult += mult_already
        self.recs[rec.id]=(rec,mult)
        self.includes[rec.id]=includes
        self.reset()

    def reset (self):
        self.grabIngsFromRecs(list(self.recs.values()),self.extras)


class ShopperTestCase (unittest.TestCase):
    def testAddition (self):
        sh = Shopper([('1','tsp.','pepper'),
                      ('1','tsp.','pepper')])
        assert(sh.dic['pepper'][0][0] == 2)

    def testUnitConversion (self):
        sh = Shopper([('1','tsp.','pepper'),
                      ('1','tsp.','pepper'),
                      ('1','tsp.','pepper'),])
        assert(sh.dic['pepper'][0][0] == 1)
        assert(sh.dic['pepper'][0][1] == 'tbs.')

    def testRangeAddition (self):
        sh = Shopper([((1,2),'c.','milk'),
                      (1,'c.','milk')]
                     )
        assert(sh.dic['milk'][0][0]==(2,3))

if __name__ == '__main__':
    unittest.main()
