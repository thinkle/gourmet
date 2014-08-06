from sqlalchemy import Column, Integer, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, composite

from ast import literal_eval
from copy import copy

from meta import Base
#from gourmet.plugin_loader import pluggable_method
from gourmet.convert import FRACTIONS_NORMAL, get_converter
from gourmet.defaults import lang as defaults

from gourmet.util.amount import Amount

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

    recipe_ref = relationship("Recipe", foreign_keys=refid, uselist=False)

    amt = composite(Amount, amount, rangeamount)

    def __imul__(self, other):
        self.amt *= other
        return self

    def __mul__(self, other):
        result = copy(self)
        return result.__imul__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    #@pluggable_method
    def __format__(self, spec):
        # We're currently abusing spec -- which should normally be a format
        # string containing placeholders like %s and the like -- as a
        # parameter to pass along a dict of options, for which we set the
        # defaults in the following.
        # TODO: Someday, we should come up with a proper Format Specification
        # Mini-Language (see that section in the Python docs), comprising
        # placeholders for range as fraction or fixed point, unit as passed or
        # as preferred etc.

        specdict = {'fractions': FRACTIONS_NORMAL,
                    'adjust_units': False,
                    'favor_current_unit': True,
                    'preferred_unit_groups': []}
        specdict.update(literal_eval(spec))
        amountspec={'fractions': specdict['fractions']}

        factor = 1
        unit = self.unit

        if spec:
            if self.unit:
                amountspec['approx'] = defaults.unit_rounding_guide.get(self.unit,0.01)
            else:
                amountspec['approx'] = 0.01

            # TODO: Maybe we should move some of this logic into a Quantity
            # class of its own which comprises both the amount (i.e. derives
            # from the Amount class, or maybe just has a member of that class),
            # and the unit.
            if specdict['adjust_units'] or specdict['preferred_unit_groups']:
                conv = get_converter()
                amount,unit = conv.adjust_unit(self.amt.amount,self.unit,
                                          favor_current_unit=specdict['favor_current_unit'],
                                          preferred_unit_groups=specdict['preferred_unit_groups'])
                if unit != self.unit:
                    factor = conv.converter(self.unit, unit)

        if unit:
            ret = u"%s %s %s" % (format(factor*self.amt, str(amountspec)), unit, self.item)
        else:
            ret = u"%s %s" % (format(factor*self.amt, str(amountspec)), self.item)

        if self.optional:
            ret += ' ' + _('(Optional)')
        return ret

    def __repr__(self):
        return u"<Ingredient(amt='%s', unit='%s', item='%s')>" % \
                (self.amt, self.unit, self.item)

    def __unicode__(self):
        return self.__format__('{}')

    def __str__(self):
        return unicode(self).encode('utf-8')


class RecRef:
    def __init__ (self, refid, title):
        self.refid = refid
        self.item = title
        self.amount = 1
