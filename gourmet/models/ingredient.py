from sqlalchemy import Column, Integer, Text, Float, Boolean, ForeignKey

from gourmet.models import Base
from gourmet.plugin_loader import pluggable_method
from gourmet import convert
from gourmet.defaults import lang as defaults

class Ingredient (Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    refid = Column(Integer, ForeignKey('recipe.id'))
    unit = Column(Text)
    amount = Column(Float)
    rangeamount = Column(Float)
    item = Column(Text)
    ingkey = Column(Text)
    optional = Column(Boolean)
    #Integer so we can distinguish unset from False
    shopoptional = Column(Integer)
    inggroup = Column(Text)
    position = Column(Integer)
    deleted = Column(Boolean)

    #TODO: So far,
    # we did the following before persisting ingredient data to the DB:
#     def validate_ingdic (self,dic):
#         """Do any necessary validation and modification of ingredient dictionaries."""
#         if not dic.has_key('deleted'): dic['deleted']=False
#         self._force_unicode(dic)
#
#     def _force_unicode (self, dic):
#        for k,v in dic.items():
#             if type(v)==str and k not in ['image','thumb']:
#                 # force unicode...
#                 dic[k]=unicode(v)

    def get_amount (self, mult=1):
        """Given an ingredient object, return the amount for it.

        Amount may be a tuple if the amount is a range, a float if
        there is a single amount, or None"""
        amt = self.amount
        try:
            ramt = self.rangeamount
        except:
            # this blanket exception is here for our lovely upgrade
            # which requires a working export with an out-of-date DB
            ramt = None
        if mult != 1:
            if amt: amt = amt * mult
            if ramt: ramt = ramt * mult
        if ramt:
            return (amt,ramt)
        else:
            return amt

    def __repr__(self):
        return "<Ingredient(amount='%s', unit='%s', item='%s')>" % \
                (self.amount, self.unit, self.item)

    def __str__(self):
        if self.rangeamount:
            return "%s %s %s %s" % (self.amount, self.rangeamount, self.unit,
                                    self.item)
        else:
            return "%s %s %s" % (self.amount, self.unit, self.item)

    #@pluggable_method #FIXME
    def get_amount_and_unit (self, mult=1, conv=None, fractions=None, adjust_units=False,
                             favor_current_unit=True,preferred_unit_groups=[]):
        """Return a tuple of strings representing our amount and unit.

        If we are handed a converter interface, we will adjust the
        units to make them readable.
        """
        amt = self.get_amount(mult)
        unit = self.unit
        ramount = None
        if type(amt)==tuple: amt,ramount = amt
        if adjust_units or preferred_unit_groups:
            if not conv:
                conv = convert.get_converter()
            amt,unit = conv.adjust_unit(amt,unit,
                                        favor_current_unit=favor_current_unit,
                                        preferred_unit_groups=preferred_unit_groups)
            if ramount and unit != self.unit:
                # if we're changing units... convert the upper range too
                ramount = ramount * conv.converter(self.unit, unit)
        if ramount: amt = (amt,ramount)
        return (self._format_amount_string_from_amount(amt,fractions=fractions,unit=unit),unit)

    def get_amount_as_string (self,
                              mult=1,
                              fractions=None,
                              ):
        """Return a string representing our amount.
        If we have a multiplier, multiply the amount before returning it.
        """
        amt = self.get_amount(mult)
        return self._format_amount_string_from_amount(amt, fractions=fractions)

    def _format_amount_string_from_amount (self, amt, fractions=None, unit=None):
        """Format our amount string given an amount tuple.

        If fractions is None, we use the default setting from
        convert.USE_FRACTIONS. Otherwise, we will override that
        setting.

        If you're thinking of using this function from outside, you
        should probably just use a convenience function like
        get_amount_as_string or get_amount_and_unit
        """
        if fractions is None:
            # None means use the default value
            fractions = convert.USE_FRACTIONS
        if unit:
            approx = defaults.unit_rounding_guide.get(unit,0.01)
        else:
            approx = 0.01
        if type(amt)==tuple:
            return "%s-%s"%(convert.float_to_frac(amt[0],fractions=fractions,approx=approx).strip(),
                            convert.float_to_frac(amt[1],fractions=fractions,approx=approx).strip())
        elif type(amt) in (float,int):
            return convert.float_to_frac(amt,fractions=fractions,approx=approx)
        else: return ""

# Convenience functions for dealing with ingredients

def order_ings (ings):
    """Handed a view of ingredients, we return an alist:
    [['group'|None ['ingredient1', 'ingredient2', ...]], ... ]
    """
    defaultn = 0
    groups = {}
    group_order = {}
    n = 0; group = 0
    for i in ings:
        # defaults
        if not hasattr(i,'inggroup'):
            group = None
        else:
            group=i.inggroup
        if group == None:
            group = n; n+=1
        if not hasattr(i,'position'):
            print 'Bad: ingredient without position',i
            i.position=defaultn
            defaultn += 1
        if groups.has_key(group):
            groups[group].append(i)
            # the position of the group is the smallest position of its members
            # in other words, positions pay no attention to groups really.
            if i.position < group_order[group]: group_order[group]=i.position
        else:
            groups[group]=[i]
            group_order[group]=i.position
    # now we just have to sort an i-listify
    def sort_groups (x,y):
        if group_order[x[0]] > group_order[y[0]]: return 1
        elif group_order[x[0]] == group_order[y[0]]: return 0
        else: return -1
    alist=groups.items()
    alist.sort(sort_groups)
    def sort_ings (x,y):
        if x.position > y.position: return 1
        elif x.position == y.position: return 0
        else: return -1
    for g,lst in alist:
        lst.sort(sort_ings)
    final_alist = []
    last_g = -1
    for g,ii in alist:
        if type(g)==int:
            if last_g == None:
                final_alist[-1][1].extend(ii)
            else:
                final_alist.append([None,ii])
            last_g = None
        else:
            final_alist.append([g,ii])
            last_g = g
    return final_alist
