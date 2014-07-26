from gourmet.convert import float_to_frac

class Yield(object):
    def __init__(self, yields, yield_unit):
        self.yields = yields
        self.yield_unit = yield_unit

    def __composite_values__(self):
        return self.yields, self.yield_unit

    def __repr__(self):
        return "Yield(yields=%s, yield_unit=%s)" % (self.yields, self.yield_unit)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return self.__format__(None)

    def __format__(self, spec):
        ret = ''
        if self.yields:
            if spec and spec == 'q':
                ret += unicode(float_to_frac(self.yields))
            else:
                ret += unicode(self.yields)
        if self.yields and self.yield_unit:
            ret += ' '
        if self.yield_unit:
            ret += self.yield_unit

        return ret

    def __eq__(self, other):
        return isinstance(other, Yield) and \
            other.yields == self.yields and \
            other.yield_unit == self.yield_unit

    def __ne__(self, other):
        return not self.__eq__(other)

    def __mul__(self, other):
        if self.yields:
            return Yield(float(other)*self.yields, self.yield_unit)
        else:
            return Yield(None, self.yield_unit)

    def __rmul__(self, other):
        return self.__mul__(other)
