import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import ekonomi
import finans
import is_piyasasi as jobs
import personel
from kariyer import LiveMatch, advance, new, rollover
from kayit import SaveError, decode, encode, load_game, save_game
from transfer import set_sale_status
from veritabani import TEAMS


GS = 'GALATASARAY'
SMALL = 'ERZURUMSPOR'


from test_fixtures import legacy_source

class CareerTests(unittest.TestCase):
    def setUp(self):
        self.s = new(GS, seed=811)

    def offer(self, team, reputation=95):
        s = self.s
        s['manager_rep'] = reputation
        jobs.vacancy(s, team, 'opening')
        before = s['rng_state']
        self.assertTrue(jobs.apply(s, team))
        self.assertFalse(jobs.apply(s, team))
        self.assertEqual(s['rng_state'], before)
        advance(s)
        return jobs.application(s, team)

    def test_switch_twice_preserves_world_and_personal_results(self):
        s = self.s
        self.assertEqual(s['manager_state']['active_team'], GS)
        for team in (SMALL, 'FENERBAHÇE'):
            self.assertEqual(self.offer(team)['status'], 'offered')
            keys = ('schedule', 'results', 'teams', 'finance', 'transfers', 'owners', 'staff_system', 'rng_state')
            before = copy.deepcopy({key:s[key] for key in keys})
            self.assertTrue(jobs.offer(s, team, True))
            self.assertFalse(jobs.offer(s, team, True))
            self.assertEqual(before, {key:s[key] for key in keys})
            self.assertEqual(s['club'], team)
            self.assertEqual(s['manager_state']['spells'][-1]['stats'], jobs.blank_stats())
        spells = s['manager_state']['spells']
        self.assertEqual([sum(r['stats'][k] for k in ('w','d','l')) for r in spells], [1,1,0])
        restored=decode(encode(s))
        self.assertEqual(restored['manager_state'],s['manager_state'])
        self.assertEqual(restored['schedule'],s['schedule'])
        self.assertEqual(restored['rng_state'],s['rng_state'])
        self.assertEqual(restored['staff_system'],s['staff_system'])

    def test_reject_decline_and_expire(self):
        s = self.s
        self.assertEqual(self.offer('FENERBAHÇE', 10)['status'], 'rejected')
        declined = self.offer(SMALL)
        self.assertTrue(jobs.offer(s, SMALL, False))
        self.assertEqual(declined['status'], 'declined')
        expires = self.offer('BEŞİKTAŞ')
        while jobs.clock(s) < expires['expires']:
            advance(s)
        self.assertEqual(expires['status'], 'expired')
        self.assertFalse(jobs.offer(s, 'BEŞİKTAŞ', True))

    def test_resign_and_financial_dismissal(self):
        s = self.s
        self.assertTrue(jobs.leave(s, 'resigned'))
        self.assertEqual(s['manager_state']['spells'][0]['reason'], 'resigned')
        self.assertFalse(jobs.leave(s, 'resigned'))
        self.assertEqual(self.offer(SMALL)['status'], 'offered')
        self.assertTrue(jobs.offer(s, SMALL, True))
        while s['week'] < 7:
            advance(s)
        s['confidence'] = 25
        s['finance'][SMALL]['cash'] = -400000
        s['board_targets'][SMALL] = 1
        s['teams'][SMALL]['p'] = -30
        jobs.weekly(s)
        self.assertFalse(s['employed'])
        self.assertEqual(s['manager_state']['decision'], 'financial')

    def test_unemployed_rollover_and_disk_roundtrip(self):
        s = new(GS, seed=811, unemployed=True)
        self.assertIsNone(s['manager_state']['active_team'])
        self.assertFalse(set_sale_status(s, next(iter(s['owners'])), 'listed'))
        for _ in range(34):
            advance(s)
        self.assertEqual(len(s['results']), 34)
        self.assertTrue(rollover(s))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_game(s, path)
            a, b = load_game(path), load_game(path)
            advance(a)
            advance(b)
            self.assertEqual(encode(a), encode(b))
            self.assertIsNone(a['manager_state']['active_team'])
        with self.assertRaises(SaveError):
            decode('{"schema_version":3,')

    def test_quick_and_live_tactical_review_identical(self):
        s = self.s
        live_state = decode(encode(s))
        live = LiveMatch(live_state)
        live.finish()
        self.assertTrue(live.commit())
        advance(s)
        self.assertEqual(json.loads(encode(s)), json.loads(encode(live_state)))
        review=s['last_tactical_review']['opening']
        self.assertEqual(len(review),2)
        self.assertEqual(set(review[0]['strengths']),{'GK','D','M','F'})

    def test_legacy_saves_continue_with_legacy_models(self):
        root = Path(__file__).resolve().parent
        script = ("from kariyer import new,advance; from kayit import encode; "
                  "s=new('GALATASARAY',seed=811); print(encode(s)); advance(s); print(encode(s))")
        for version in ('0.7.9.1','0.7.9.2','0.7.9.3','0.8.0'):
            with self.subTest(version=version):
                raw = subprocess.check_output([sys.executable,'-B','-X','utf8','-c',script],
                     cwd=legacy_source(self, f'yedek_v{version}', root=root),encoding='utf-8').splitlines()
                s = decode(raw[0])
                self.assertNotIn('economy_model',s)
                self.assertNotIn('manager_state',s)
                advance(s)
                expected=json.loads(raw[1])
                actual=json.loads(encode(s))
                for key in ('results','finance','teams','owners','staff_system','rng_state'):
                    self.assertEqual(actual.get(key),expected.get(key),key)


class FinanceTests(unittest.TestCase):
    def test_weekly_reconciliation_and_debt_recovery(self):
        s=new(GS,seed=812)
        row=s['finance'][SMALL]
        row.update(cash=-100000,debt=0)
        finans.service(s,SMALL)
        self.assertEqual((row['cash'],row['debt'],row['borrowed']),(0,100000,100000))
        row['cash']=730000
        finans.service(s,SMALL)
        self.assertEqual((row['cash'],row['debt'],row['repaid']),(630000,0,100000))
        before=row.copy()
        finans.operating(s,SMALL)
        income=('season_tickets','broadcast','sponsors','commercial')
        expense=('staff','academy','maintenance','interest','repaid')
        self.assertEqual(row['cash']-before['cash'],sum(row[k]-before[k] for k in income)
                         -sum(row[k]-before[k] for k in expense))
        self.assertEqual(row['staff']-before['staff'],ekonomi.admin(s,SMALL)+personel.payroll(s,SMALL))

    def test_no_double_salary_and_funded_staff_replacement(self):
        s=new(GS,seed=813)
        for pid,_ in personel.active(s,SMALL):
            self.assertTrue(personel.release(s,SMALL,pid))
        s['finance'][SMALL]['cash']=3_000_000
        s['week']=17
        personel.refill(s)
        hires=personel.active(s,SMALL)
        self.assertTrue(hires)
        pid=hires[0][0]
        self.assertFalse(personel.contract(s,'FENERBAHÇE',pid,1)[0])
        before=s['finance'][SMALL]['staff']
        finans.operating(s,SMALL)
        self.assertEqual(s['finance'][SMALL]['staff']-before,ekonomi.admin(s,SMALL)+personel.payroll(s,SMALL))

    def test_high_cash_alone_does_not_permit_unsustainable_wage(self):
        s=new(SMALL,seed=814)
        s['finance'][GS]['cash']=20_000_000
        self.assertFalse(ekonomi.can_commit(s,GS,0,1_000_000))
        s['finance'][GS]['transfer_budget']=100
        self.assertFalse(finans.can_pay(s,GS,101,0,0))
        self.assertFalse(ekonomi.can_commit(s,GS,19_999_999,0))

    def test_small_club_can_operate_without_a_transfer(self):
        from unittest.mock import patch
        s=new(SMALL,seed=811)
        initial=s['finance'][SMALL]['cash']
        with patch('kariyer.recruit'):
            for _ in range(34):
                advance(s)
        cash=s['finance'][SMALL]
        self.assertEqual(s['transfers'],[])
        self.assertGreater(cash['cash'],0)
        self.assertGreater(cash['wages_paid'],0)
        credits=('tickets','season_tickets','broadcast','sponsors','commercial','borrowed')
        debits=('wages_paid','staff','academy','maintenance','interest','repaid')
        self.assertEqual(cash['cash'],initial+sum(cash[key] for key in credits)
                         -sum(cash[key] for key in debits))

    def test_overspending_has_a_cash_and_debt_cost(self):
        from oyuncu import state
        from veritabani import roster
        normal=new(GS,seed=815)
        expensive=decode(encode(normal))
        for player in roster(GS,expensive['year'],expensive):
            state(expensive,player)['wage']+=30_000
        for _ in range(20):
            advance(normal)
            advance(expensive)
        baseline=normal['finance'][GS]
        stressed=expensive['finance'][GS]
        self.assertGreater(stressed['wages_paid'],baseline['wages_paid'])
        self.assertLess(stressed['cash'],baseline['cash'])
        self.assertGreater(stressed['debt'],baseline['debt'])

    def test_pool_expansion_is_bounded_and_deterministic(self):
        s=new(GS,seed=815)
        club=SMALL
        for pid,_ in personel.active(s,club):
            personel.release(s,club,pid)
        for row in s['staff_system']['pool'].values():
            if row['club'] is None:
                row.update(club=GS,start=s['year'],end=s['year']+1)
        from oyuncu import state
        from veritabani import roster
        for p in roster(club,s['year'],s):
            state(s,p)['wage']=100
        s['finance'][club]['cash']=5_000_000
        rng=s['rng_state']
        personel.refill(s)
        pool=s['staff_system']['pool']
        self.assertTrue(120<len(pool)<=150)
        self.assertTrue(all(row['source']=='fictional' for row in pool.values()))
        self.assertEqual(rng,s['rng_state'])


class InterfaceTests(unittest.TestCase):
    def test_bilingual_application_hiring_and_match_report_at_minimum_size(self):
        import tkinter as tk
        from tkinter import ttk
        from unittest.mock import patch
        from arayuz import UI

        def widgets(root):
            for child in root.winfo_children():
                yield child
                yield from widgets(child)

        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        ui.autosave=lambda: None
        root.geometry('960x600')
        for lang in ('TR','EN'):
            with self.subTest(language=lang):
                s=new(GS,seed=816,unemployed=True)
                s.update(lang=lang,manager_rep=90)
                ui.begin(s)
                ui.jobs_page()

                def select_and_invoke(key):
                    tree=next(w for w in widgets(ui.body) if isinstance(w,ttk.Treeview))
                    tree.selection_set(tree.get_children()[0])
                    button=next(w for w in widgets(ui.body) if isinstance(w,ttk.Button)
                                and w.cget('text')==ui.management_text(key))
                    root.update()
                    self.assertTrue(button.winfo_ismapped())
                    button.invoke()

                select_and_invoke('job_apply')
                ui.next()
                ui.jobs_page()
                with patch('kariyer_ui.messagebox.askyesno',return_value=True):
                    select_and_invoke('job_accept')
                self.assertTrue(s['employed'])
                s['match_mode']='quick'
                with patch('arayuz.messagebox.askyesno',return_value=True):
                    ui.next()
                ui.last_report()
                labels=[w.cget('text') for w in widgets(root) if isinstance(w,ttk.Label)]
                self.assertTrue(any('K/S/O/H' in label or 'GK/D/M/F' in label for label in labels))
                for w in root.winfo_children():
                    if isinstance(w,tk.Toplevel):w.destroy()
                ui.finance_page()
                root.update()
                self.assertEqual((root.winfo_width(),root.winfo_height()),(960,600))
