"""Regression tests for transfer installments crossing season boundaries."""
from unittest import TestCase

from finans import book_deal, commitments, pay_due_transfers


class TransferInstallmentSeasonBoundary(TestCase):
    def test_week_32_installments_roll_into_next_season(self):
        buyer, seller = 'BUYER', 'SELLER'
        s = {
            'year': 2000,
            'week': 32,
            'finance': {
                buyer: {'cash': 1000, 'transfer_budget': 1000,
                        'fees_paid': 0, 'signing_paid': 0},
                seller: {'cash': 500, 'transfer_budget': 0,
                         'fees_received': 0},
            },
        }

        book_deal(s, buyer, seller, fee=300, signing=30, payments=3)
        self.assertEqual(s['transfer_payments'], [
            [2001, 2, buyer, seller, 100],
            [2001, 6, buyer, seller, 100],
        ])
        self.assertEqual(commitments(s, buyer), (200, 0))
        self.assertEqual(s['finance'][buyer]['cash'], 870)

        for year, week, expected_cash, expected_due in (
            (2000, 34, 870, 200),
            (2001, 1, 870, 200),
            (2001, 2, 770, 100),
            (2001, 5, 770, 100),
            (2001, 6, 670, 0),
        ):
            with self.subTest(year=year, week=week):
                s.update(year=year, week=week)
                pay_due_transfers(s)
                self.assertEqual(s['finance'][buyer]['cash'], expected_cash)
                self.assertEqual(commitments(s, buyer), (expected_due, 0))

        self.assertNotIn('transfer_payments', s)
        self.assertEqual(s['finance'][buyer]['fees_paid'], 300)
        self.assertEqual(s['finance'][seller]['fees_received'], 300)
        self.assertEqual(s['finance'][seller]['cash'], 800)
        self.assertEqual(s['finance'][buyer]['signing_paid'], 30)
