"""Economy v2, recruitment and safe desktop regression checks."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import donem
import finans
import ekonomi
from kariyer import advance,new
from kayit import backup_path,decode,encode,load_game,save_game,SaveError
from piyasa_ai import assess
from veritabani import roster
from sozlesme import asking_terms
from transfer import value

CLUB='GALATASARAY'
SMALL='ERZURUMSPOR'


from test_fixtures import legacy_source

class DynamicEconomy(unittest.TestCase):
    def test_period_indices_are_deterministic_distinct_and_bounded(self):
        self.assertEqual({donem.index(2000,key) for key in donem.LIMITS},{1})
        for key,limit in donem.LIMITS.items():
            earlier,later,late=(donem.index(year,key) for year in (2025,2050,2500))
            self.assertLess(1,earlier)
            self.assertLess(earlier,later)
            self.assertLess(later,late)
            self.assertLess(late,limit)
        self.assertNotEqual(donem.index(2050,'wage'),donem.index(2050,'transfer'))

    def test_income_and_prices_use_same_historical_clock_with_legacy_isolation(self):
        modern=new(CLUB,seed=811)
        legacy=new(CLUB,seed=811,economy_version=1)
        a=decode(encode(legacy))
        self.assertEqual(a['economy_model'],1)
        self.assertNotIn('commercial',a['finance'][CLUB])
        modern['year']=legacy['year']=2035
        p=roster(CLUB,2000,modern)[0]
        self.assertGreater(value(modern,p),value(legacy,p))
        self.assertGreater(asking_terms(modern,p,CLUB)['wage'],asking_terms(legacy,p,CLUB)['wage'])
        _,new_income,new_expense=finans.operating_plan(modern,CLUB)
        _,old_income,old_expense=finans.operating_plan(legacy,CLUB)
        self.assertGreater(new_income['broadcast'],old_income['broadcast'])
        self.assertGreater(new_expense['maintenance'],old_expense['maintenance'])
        self.assertIn('commercial',new_income)
        self.assertNotIn('commercial',old_income)

    def test_v081_file_replays_without_switching_economy(self):
        import subprocess
        import sys
        folder=legacy_source(self, 'top ant tester v0.8.1', sibling=True)
        source=("from kariyer import new,advance; from kayit import encode; "
                "s=new('GALATASARAY',seed=811); print(encode(s)); "
                "advance(s); print(encode(s))")
        before,after=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',source],
                                             cwd=folder,encoding='utf-8').splitlines()
        s=decode(before)
        self.assertEqual(s['economy_model'],1)
        advance(s)
        self.assertEqual(json.loads(encode(s)),json.loads(after))

    def test_commercial_income_books_cash_exactly_and_preserves_save(self):
        s=new(CLUB,seed=811)
        team=SMALL
        opening=s['finance'][team]['cash']
        finans.operating(s,team)
        row=s['finance'][team]
        self.assertGreater(row['commercial'],0)
        earned=sum(row[k] for k in ('season_tickets','broadcast','sponsors','commercial','borrowed'))
        self.assertEqual(row['cash']-opening,earned-row['operating_paid']-row['repaid'])
        self.assertEqual(decode(encode(s))['finance'][team],row)
        self.assertFalse(ekonomi.can_commit(s,team,row['cash']+1,1))

    def test_missing_keeper_becomes_first_need_and_fit_is_respected(self):
        s=new(CLUB,seed=811)
        squad=roster(SMALL,s['year'],s)
        no_keepers=[p for p in squad if p['pos']!='GK']
        plan=assess(s,SMALL,no_keepers)
        self.assertEqual(plan[0][1],'GK')
        self.assertEqual(plan[0][3],1)

    def test_transfer_and_financial_books_are_deterministic(self):
        s=new(CLUB,seed=811)
        other=decode(encode(s))
        advance(s)
        advance(other)
        self.assertEqual(json.loads(encode(s)),json.loads(encode(other)))
        self.assertTrue(s['transfers'])
        self.assertEqual(sum(t[4] for t in s['transfers']),sum(r['fees_paid'] for r in s['finance'].values()))
        self.assertEqual(sum(r['fees_paid'] for r in s['finance'].values()),
                         sum(r['fees_received'] for r in s['finance'].values()))


class SaveAndUI(unittest.TestCase):
    def test_interrupted_commit_preserves_old_save_and_valid_backup(self):
        import os
        s=new(CLUB,seed=812)
        real_replace=os.replace
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'career.json'
            save_game(s,path)
            original=path.read_bytes()
            advance(s)
            def failure(source,target):
                if Path(target)==path:
                    raise OSError('simulated interrupted final commit')
                real_replace(source,target)
            with patch('kayit.os.replace',side_effect=failure),self.assertRaises(OSError):
                save_game(s,path)
            self.assertEqual(original,path.read_bytes())
            self.assertEqual(original,backup_path(path).read_bytes())
            self.assertEqual(load_game(backup_path(path))['week'],1)
            self.assertFalse(list(Path(tmp).glob('*.tmp')))
            path.write_text('{',encoding='utf-8')
            with self.assertRaises(SaveError):
                load_game(path)
            save_game(s,path)
            self.assertEqual(backup_path(path).read_bytes(),original)

    def test_theme_screens_save_and_load_at_960(self):
        import tkinter as tk
        from arayuz import UI
        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        root.geometry('960x600')
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            for lang in ('TR','EN'):
                s=new(CLUB,seed=813)
                ui.begin(dict(s,lang=lang))
                for page in (ui.dashboard,ui.squad,ui.tactics,ui.market,ui.finance_page,ui.staff_page):
                    page()
                    root.update()
                    self.assertTrue(ui.body.winfo_children())
                ui.profile(roster(CLUB,2000,s)[0])
                root.update()
                for child in root.winfo_children():
                    if isinstance(child,tk.Toplevel):child.destroy()
                path=folder/(lang+'.json')
                with patch('arayuz.user_directory',return_value=folder),patch('arayuz.filedialog.asksaveasfilename',return_value=str(path)):
                    ui.save()
                self.assertTrue(path.exists())
                with patch('arayuz.user_directory',return_value=folder),patch('arayuz.filedialog.askopenfilename',return_value=str(path)):
                    ui.load()
                self.assertEqual(ui.s['lang'],lang)
                self.assertEqual((root.winfo_width(),root.winfo_height()),(960,600))
