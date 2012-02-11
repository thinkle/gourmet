import unittest
import convert

class ConvertTest (unittest.TestCase):

    def setUp (self):
        self.c = convert.get_converter()

    def testEqual (self):
        self.assertEqual(self.c.convert_simple('c','c'),1)

    def testDensity (self):
         self.assertEqual(self.c.convert_w_density('ml','g',item='water'),1)
         self.assertEqual(self.c.convert_w_density('ml','g',density=0.5),0.5)

    def testReadability (self):
        self.failUnless(self.c.readability_score(1,'cup') > self.c.readability_score(0.8,'cups') )
        self.failUnless(self.c.readability_score(1/3.0,'tsp.') > self.c.readability_score(0.123,'tsp.'))
    
    def testAdjustments (self):
        amt,unit = self.c.adjust_unit(12,'Tbs.','water')
        self.assertEqual(amt,.75)

    def testIntegerRounding (self):
        self.failUnless(convert.integerp(0.99))
    
    def testFractionGenerator (self):
        for d in [2,3,4,5,6,8,10,16]:
            self.assertEqual(
                convert.float_to_frac(1.0/d,fractions=convert.FRACTIONS_ASCII),
                ('1/%s'%d)
                )
            
    def testFractToFloat (self):
        for s,n in [
            ('1',1),
            ('123',123),
            ('1 1/2',1.5),
            ('74 2/5',74.4),
            ('1/10',0.1),
            ('one',1),
            ('a half',0.5),
            ('three quarters',0.75),
            ]:
            self.assertEqual(convert.frac_to_float(s),n)
        
    def test_ingmatcher (self):
        for s,a,u,i in [
            ('1 cup sugar', '1','cup','sugar'),
            ('1 1/2 cup sugar', '1 1/2','cup','sugar'),
            ('two cloves garlic', 'two','cloves','garlic'),
                        ]:
            match = convert.ING_MATCHER.match(s)
            self.failUnless(match)
            self.assertEqual(match.group(convert.ING_MATCHER_AMT_GROUP).strip(),a)
            self.assertEqual(match.group(convert.ING_MATCHER_UNIT_GROUP).strip(),u)
            self.assertEqual(match.group(convert.ING_MATCHER_ITEM_GROUP).strip(),i)
            
if __name__ == '__main__':
    unittest.main()
        
