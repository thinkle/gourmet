from gourmet.convert import float_to_frac, \
    FRACTIONS_ALL, FRACTIONS_NORMAL, FRACTIONS_ASCII, FRACTIONS_OFF

from ast import literal_eval

class Amount(object):
    def __init__(self, amount=None, rangeamount=None):
        self.amount = amount
        self.rangeamount = rangeamount

    def __composite_values__(self):
        return self.amount, self.rangeamount

    def __repr__(self):
        return "Amount(amount=%s, rangeamount=%s)" % (self.amount, self.rangeamount)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.__format__("{'fractions': %s}"%FRACTIONS_OFF)

    def __format__(self, spec):
        specdict = {'fractions': FRACTIONS_NORMAL,
                    'approx': 0.01}
        specdict.update(literal_eval(spec))

        amt = unicode(float_to_frac(self.amount,
                                    approx=specdict['approx'],
                                    fractions=specdict['fractions']))

        if self.rangeamount:
            return amt + '-' + unicode(float_to_frac(self.rangeamount,
                                                     approx=specdict['approx'],
                                                     fractions=specdict['fractions']))
        else:
            return amt

    def __eq__(self, other):
        return isinstance(other, Amount) and \
            other.amount == self.amount and \
            other.rangeamount == self.rangeamount

    def __ne__(self, other):
        return not self.__eq__(other)

    def __imul__(self, other):
        if self.amount:
            self.amount *= float(other)
        if self.rangeamount:
            self.rangeamount *= float(other)
        return self

    def __mul__(self, other):
        result = self
        return result.__imul__(other)

    def __rmul__(self, other):
        return self.__mul__(other)
