import unittest
from unittest.mock import patch
import piyasa_ai as ai

class SaleCoverTests(unittest.TestCase):
    def setUp(self):
        self.s={'transfer_model':True}
        self.a={'id':'a','pos':'RB','alternate_positions':['LB']}
        self.b={'id':'b','pos':'LB'}
        self.c={'id':'c','pos':'RB'}
        self.cb1={'id':'cb1','pos':'CB'}
        self.cb2={'id':'cb2','pos':'CB'}
        for name, value in [('ability',15),('state',{'injury':0})]:
            patcher=patch.object(ai,name,return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_critical_player_protected(self):
        self.assertFalse(ai.sale_preserves_cover(self.s,[self.a,self.b],'a'))

    def test_surplus_player_can_be_sold(self):
        self.assertTrue(ai.sale_preserves_cover(self.s,[self.a,self.b,self.c,self.cb1,self.cb2],'c'))

    def test_second_sale_rechecks_remaining_squad(self):
        self.assertTrue(ai.sale_preserves_cover(self.s,[self.a,self.b,self.c,self.cb1,self.cb2],'c'))
        self.assertFalse(ai.sale_preserves_cover(self.s,[self.a,self.b,self.cb1,self.cb2],'b'))

    def test_injured_critical_player_protected(self):
        with patch.object(ai,'state',return_value={'injury':4}):
            self.assertFalse(ai.sale_preserves_cover(self.s,[self.a],'a'))

if __name__=='__main__':
    unittest.main()
