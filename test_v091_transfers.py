from unittest import TestCase

from finans import commitments, pay_due_transfers, payroll, wage_shares
from kariyer import new
from kayit import decode, encode
from oyuncu import state
from sozlesme import asking_terms, renew
from transfer import asking_fee, deal, loan_deal, loan_fee, purchase_offer, return_loans
from veritabani import player


class TransferLifecycle(TestCase):
    def setUp(self):
        self.s=new('FENERBAHÇE',seed=91,match_model=4,transfer_model=True)

    def test_counteroffer_and_installments_survive_reload(self):
        s=self.s
        buyer=s['club']
        p=player(s,'22261')
        seller=s['owners'][p['id']]
        terms=asking_terms(s,p,buyer,'Starter')
        terms['wage']=round(terms['wage']*1.4)
        cash=s['finance'][buyer]['cash']
        budget=s['finance'][buyer]['transfer_budget']
        low=round(asking_fee(s,p)*.65)
        ok,reason,quote=purchase_offer(s,p['id'],buyer,low,**terms,payments=3)
        self.assertEqual((ok,reason),(False,'counter'))
        self.assertEqual(s['owners'][p['id']],seller)
        self.assertEqual(s['finance'][buyer]['cash'],cash)
        self.assertTrue(purchase_offer(s,p['id'],buyer,quote,**terms,payments=3,rounds=1)[0])
        s=decode(encode(s))
        deferred=quote//3
        ledger=s['finance'][buyer]
        self.assertEqual(ledger['cash'],cash-(quote-2*deferred)-terms['signing'])
        self.assertEqual(ledger['transfer_budget'],budget-quote-terms['signing'])
        self.assertEqual(commitments(s,buyer),(2*deferred,0))
        for week in (5,9,9):
            s['week']=week
            pay_due_transfers(s)
        self.assertEqual(ledger['cash'],cash-quote-terms['signing'])
        self.assertEqual(ledger['fees_paid'],quote)
        self.assertEqual(s['finance'][seller]['fees_received'],quote)
        self.assertEqual(commitments(s,buyer),(0,0))

    def test_loan_shares_wages_and_returns_original_contract(self):
        s=self.s
        borrower=s['club']
        p=player(s,'27547')
        pid=p['id']
        parent=s['owners'][pid]
        contract=state(s,p)['contract']
        wage=state(s,p)['wage']
        before=[payroll(s,team) for team in (borrower,parent)]
        self.assertTrue(loan_deal(s,pid,borrower,loan_fee(s,p),50)[0])
        s=decode(encode(s))
        first,second=wage_shares(s,pid,wage)
        self.assertEqual((first+second,s['owners'][pid]),(wage,borrower))
        self.assertEqual([payroll(s,team) for team in (borrower,parent)],
                         [before[0]+first,before[1]-first])
        terms=asking_terms(s,p,borrower)
        self.assertFalse(renew(s,pid,**terms)[0])
        self.assertFalse(deal(s,pid,parent,0,**terms)[0])
        return_loans(s)
        self.assertEqual((s['owners'][pid],state(s,p)['contract']),(parent,contract))
        self.assertEqual([payroll(s,team) for team in (borrower,parent)],before)

    def test_withdrawal_closes_the_current_window_and_reopens_in_winter(self):
        s=self.s
        p=player(s,'22261')
        buyer=s['club']
        terms=asking_terms(s,p,buyer,'Starter')
        self.assertEqual(purchase_offer(s,p['id'],buyer,0,**terms)[1],'withdrawn')
        s=decode(encode(s))
        fee=asking_fee(s,p)
        self.assertEqual(purchase_offer(s,p['id'],buyer,fee,**terms)[1],'withdrawn')
        s['week']=18
        self.assertNotEqual(purchase_offer(s,p['id'],buyer,fee,**terms)[1],'withdrawn')
