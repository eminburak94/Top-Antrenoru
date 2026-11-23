from unittest import TestCase
from unittest.mock import patch

from finans import book_deal, can_pay, transfer_quote
from ise_alim_ui import formation_coverage
from kariyer import new
from kayit import decode, encode
from mevkiler import fit_level
from personel import active, finish_scouting, scout_assignment, start_scout
from veritabani import player, roster


class RecruitmentDepth(TestCase):
    def setUp(self):
        self.s=new('GALATASARAY',seed=970,match_model=4,transfer_model=True)

    def test_installment_quote_matches_booking(self):
        s=self.s
        club=s['club']
        ledger=s['finance'][club]
        s['transfer_payments']=[[2000,5,club,'BEŞİKTAŞ',101]]
        cash,budget=ledger['cash'],ledger['transfer_budget']
        quote=transfer_quote(s,club,301,47,0,payments=3)
        self.assertEqual((quote['upfront'],quote['deferred'],quote['reserved']),(148,100,101))
        self.assertTrue(can_pay(s,club,301,47,0,payments=3))
        self.assertEqual(quote['cash_left'],cash-101-148)
        book_deal(s,club,'FENERBAHÇE',301,47,3)
        self.assertEqual(ledger['cash'],cash-quote['upfront'])
        self.assertEqual(ledger['transfer_budget'],budget-348)
        self.assertEqual(quote['budget_left'],ledger['transfer_budget'])
        blocked=transfer_quote(s,club,budget+cash,0,ledger['wage_budget']+1)
        self.assertEqual(blocked['issues'],['transfer','cash','wages'])

    def test_scouting_report_age_tracks_elapsed_weeks(self):
        from ise_alim_ui import RecruitmentViews

        class DummyView(RecruitmentViews):
            def __init__(self, state):
                self.s = state

            def tr(self, turkish, english):
                return english

        view = DummyView(self.s)
        report = {'year': 2000, 'week': 0, 'confidence': 12}
        self.s['week'] = 0
        self.assertIn('0 weeks ago', view.scouting_age(report))
        self.s['week'] = 1
        self.assertIn('1 weeks ago', view.scouting_age(report))
        self.s['week'] = 3
        self.assertIn('3 weeks ago', view.scouting_age(report))
        self.s['year'], self.s['week'] = 2001, 0
        self.assertIn('34 weeks ago', view.scouting_age(report))

    def test_scouting_uses_free_colleague_and_roundtrips(self):
        s=self.s
        club=s['club']
        primary=active(s,club,'scout')[0][0]
        pool=s['staff_system']['pool']
        secondary=next(uid for uid,row in pool.items() if row['role']=='scout' and row['club'] is None)
        pool[secondary].update(club=club,start=2000,end=2002)
        s['staff_system']['delegation'][club]={'scouting':primary}
        a,b,c=[p['id'] for p in roster('FENERBAHÇE',s['year'],s)[:3]]
        self.assertEqual(scout_assignment(s,a),('ready',primary))
        self.assertTrue(start_scout(s,a))
        self.assertEqual(scout_assignment(s,a),('pending',2))
        self.assertFalse(start_scout(s,a))
        self.assertEqual(scout_assignment(s,b),('ready',secondary))
        self.assertTrue(start_scout(s,b))
        self.assertEqual(scout_assignment(s,c),('busy',None))
        s=decode(encode(s))
        s['week']=2
        finish_scouting(s)
        self.assertEqual({r['player'] for r in s['staff_system']['reports']},{a,b})
        self.assertEqual(scout_assignment(s,c),('ready',primary))

    def test_formation_coverage_respects_slots_and_availability(self):
        s=self.s
        s['formation']='3-5-2'
        slots=formation_coverage(s)
        self.assertEqual(slots['CB'][0],3)
        self.assertNotIn('RB',slots)
        p=next(p for p in roster(s['club'],s['year'],s) if fit_level(p,'CB')>=2)
        s['fitness'][p['id']]['injury']=2
        self.assertEqual(formation_coverage(s)['CB'],(3,slots['CB'][1]-1))
        s['formation']='4-3-3'
        self.assertIn('RB',formation_coverage(s))

    def test_profile_can_request_report(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI
        from test_v088_2d import button, descendants

        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        ui.begin(self.s)
        ui.lang='EN'
        p=roster('FENERBAHÇE',self.s['year'],self.s)[0]
        with patch.object(ui,'autosave') as save:
            popup=ui.external_profile(p)
            action=button(popup,'Request scouting')
            action.invoke()
            self.assertTrue(action.instate(['disabled']))
            self.assertTrue(any('2 weeks remaining' in w.cget('text')
                                for w in descendants(popup) if isinstance(w,ttk.Label)))
            save.assert_called_once()

    def test_market_filters_by_formation_and_shows_budget_room(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI
        from test_v088_2d import descendants

        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        ui.begin(self.s)
        ui.lang='EN'
        self.s['formation']='3-5-2'
        self.s['ui_preferences']={'player_filters':{'formation_slot':'CB'}}
        ui.market()
        tree=next(w for w in descendants(ui.body) if isinstance(w,ttk.Treeview))
        rows=tree.get_children()
        self.assertTrue(rows)
        self.assertTrue(all(fit_level(player(self.s,pid),'CB')>=2 for pid in rows))
        self.assertTrue(any('3 in formation' in w.cget('text')
                            for w in descendants(ui.body) if isinstance(w,ttk.Label)))
        target=roster('FENERBAHÇE',self.s['year'],self.s)[0]
        ui.negotiate(target)
        popup=next(w for w in descendants(root) if isinstance(w,tk.Toplevel))
        self.assertTrue(any('Available cash left' in w.cget('text') and 'Wage budget left' in w.cget('text')
                            for w in descendants(popup) if isinstance(w,ttk.Label)))
