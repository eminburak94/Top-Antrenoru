"""Regression tests for AI loan candidate parent-club coverage guard."""
import unittest
from unittest.mock import Mock, patch
import piyasa_ai as ai


class LoanCoverageTests(unittest.TestCase):
    def run_candidate(self, preserves=True, ready=True, affordable=True, user_parent=False):
        p = {'id': '1'}
        squad = [p]
        s = {'owners': {'1': 'parent'}, 'year': 2000,
             'employed': user_parent, 'club': 'parent' if user_parent else 'other',
             'sale_status': {'1': 'loan'}}
        mocks = dict(fit_level=Mock(return_value=4),
                     state=Mock(return_value={'injury': 0, 'wage': 1000, 'potential': 15, 'ability': 10}),
                     loan_ready=Mock(return_value=ready),
                     roster=Mock(return_value=squad),
                     sale_preserves_cover=Mock(return_value=preserves),
                     loan_fee=Mock(return_value=100),
                     can_commit=Mock(return_value=affordable),
                     skill=Mock(return_value=10),
                     loan_deal=Mock(return_value=(True, 'accepted')),
                     add_offer=Mock(return_value=True))
        plan = {}
        with patch.multiple(ai, **mocks):
            result = ai.borrow_cover(s, 'buyer', 'ST', [(p, 20, 7)], plan)
        return result, mocks, s, squad, plan

    def test_critical_parent_player_not_borrowed(self):
        result, m, s, squad, _ = self.run_candidate(preserves=False)
        self.assertFalse(result)
        m['sale_preserves_cover'].assert_called_once_with(s, squad, '1')
        m['loan_deal'].assert_not_called()
        m['can_commit'].assert_not_called()

    def test_safe_candidate_borrowed(self):
        result, m, s, squad, plan = self.run_candidate()
        self.assertTrue(result)
        m['roster'].assert_called_once_with('parent', 2000, s)
        m['sale_preserves_cover'].assert_called_once_with(s, squad, '1')
        m['can_commit'].assert_called_once_with(s, 'buyer', 100, 500, forecast=plan)
        m['loan_deal'].assert_called_once_with(s, '1', 'buyer', 100, 50)

    def test_existing_readiness_guard(self):
        result, m, *_ = self.run_candidate(ready=False)
        self.assertFalse(result)
        m['sale_preserves_cover'].assert_not_called()
        m['loan_deal'].assert_not_called()

    def test_existing_financial_guard(self):
        result, m, *_ = self.run_candidate(affordable=False)
        self.assertFalse(result)
        m['loan_deal'].assert_not_called()

    def test_user_parent_critical_player_not_offered(self):
        result, m, *_ = self.run_candidate(preserves=False, user_parent=True)
        self.assertFalse(result)
        m['add_offer'].assert_not_called()

    def test_user_parent_safe_player_offered(self):
        result, m, *_ = self.run_candidate(user_parent=True)
        self.assertTrue(result)
        m['add_offer'].assert_called_once()
        m['loan_deal'].assert_not_called()


class LoanPotentialTests(unittest.TestCase):
    def winner(self, age, potential, ability=10, base=10, affordable=True):
        a, b = {'id': '1'}, {'id': '2'}
        s = {'owners': {'1': 'parent', '2': 'parent'}, 'year': 2000,
             'employed': False, 'club': 'other', 'sale_status': {}}
        states = {'1': dict(injury=0, wage=1000, potential=potential, ability=ability),
                  '2': dict(injury=0, wage=2000, potential=10, ability=10)}
        deal = Mock(return_value=(True, 'accepted'))
        with patch.multiple(ai, fit_level=Mock(return_value=4),
                            state=Mock(side_effect=lambda s,p: states[p['id']]),
                            loan_ready=Mock(return_value=True),
                            roster=Mock(return_value=[a,b]),
                            sale_preserves_cover=Mock(return_value=True),
                            loan_fee=Mock(return_value=100),
                            can_commit=Mock(side_effect=lambda s,t,f,w,**kw: affordable or w!=500),
                            skill=Mock(side_effect=lambda s,p,r: base if p is a else 10),
                            loan_deal=deal):
            self.assertTrue(ai.borrow_cover(s,'buyer','ST',[(a,age,7),(b,26,7)],{}))
        return deal.call_args.args[1]

    def test_youth_potential_preferred(self):
        self.assertEqual(self.winner(22,17), '1')

    def test_age_boundary(self):
        self.assertEqual(self.winner(23,17), '2')

    def test_no_growth_no_bonus(self):
        self.assertEqual(self.winner(20,10), '2')

    def test_negative_growth_no_penalty(self):
        self.assertEqual(self.winner(20,8,base=10.1), '1')

    def test_bonus_cap(self):
        self.assertEqual(self.winner(20,30,base=9.2), '2')

    def test_bonus_does_not_override_budget(self):
        self.assertEqual(self.winner(20,30,affordable=False), '2')


if __name__ == '__main__':
    unittest.main()
