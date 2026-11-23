import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from kariyer import LiveMatch, advance, new
from kayit import SaveError, decode, encode, load_game, save_game
from oyuncu import state
from sozlesme import asking_terms, player_objection, renew
from transfer import deal
from veritabani import player, roster
from yonetim import squad_review

ROOT = Path(__file__).resolve().parent


from test_fixtures import legacy_source

class ManagementTests(unittest.TestCase):
    def test_weekly_actual_values_and_live_parity(self):
        s = new('GALATASARAY', seed=72)
        s['training'] = 'Development'
        other = copy.deepcopy(s)
        start = copy.deepcopy(s.get('fitness', {}))
        self.assertNotIn('weekly_feedback', s)
        self.assertTrue(advance(s))
        match = LiveMatch(other)
        match.finish()
        self.assertTrue(match.commit())
        self.assertFalse(match.commit())
        self.assertEqual(s['weekly_feedback'], other['weekly_feedback'])
        self.assertEqual(s['rng_state'], other['rng_state'])
        report = s['weekly_feedback']['players']
        result = next(r for r in s['results'][0] if s['club'] in (r['home'],r['away']))
        self.assertIn(0,[row['minutes'] for row in report.values()])
        self.assertIn(90,[row['minutes'] for row in report.values()])
        for pid, row in report.items():
            actual = s['fitness'][pid]
            self.assertEqual(row['minutes'], result['minutes'].get(pid,0))
            self.assertEqual(row['form'], actual['form'])
            self.assertEqual(row['condition'], actual['condition'])
            if pid in start:
                self.assertEqual(row['condition_change'], actual['condition']-start[pid]['condition'])
                self.assertEqual(row['form_change'], round(actual['form']-start[pid]['form'],1))
                self.assertEqual(row['training'], actual.get('training_weeks',0)-start[pid].get('training_weeks',0))
        self.assertTrue(advance(s))
        for pid,row in s['weekly_feedback']['players'].items():
            if pid in report:
                self.assertEqual(row['minute_change'],row['minutes']-report[pid]['minutes'])

    def test_v077_save_and_unchanged_simulation(self):
        code = """from kariyer import new,advance
from kayit import encode
s=new('GENÇLERBİRLİĞİ', seed=96)
for _ in range(34): advance(s)
print(encode(s))
advance(s)
advance(s)
print(encode(s))
"""
        raw, expected = subprocess.check_output([sys.executable,'-X','utf8','-B','-c',code],
                           cwd=legacy_source(self, 'yedek_v0.7.7', root=ROOT),encoding='utf8').splitlines()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'isolated.json'
            path.write_text(raw,encoding='utf8')
            s=load_game(path)
            self.assertNotIn('weekly_feedback',s)
            self.assertTrue(advance(s))
            self.assertEqual((s['year'],s['week']),(2001,1))
            self.assertTrue(advance(s))
            save_game(s,path)
            final=load_game(path)
        self.assertEqual(final['weekly_feedback'],s['weekly_feedback'])
        normalized=json.loads(encode(final))
        normalized.pop('weekly_feedback')
        normalized.pop('monthly_training')
        normalized.pop('training_month',None)
        normalized.pop('season_development')
        legacy=json.loads(expected)
        # The verified injury-counter fix changes only this counter at first rollover.
        for save in (normalized,legacy):
            for fitness in save['fitness'].values():
                fitness.pop('injury_matches',None)
        self.assertEqual(normalized,legacy)

    def test_review_is_read_only_and_reports_depth_and_budgets(self):
        for club in ('GALATASARAY','ERZURUMSPOR','GENÇLERBİRLİĞİ'):
            s=new(club,seed=19)
            before=encode(s)
            view=squad_review(s)
            self.assertEqual(before,encode(s))
            self.assertEqual(view['transfer'],s['finance'][club]['transfer_budget'])
            self.assertEqual(view['wage'],s['finance'][club]['wage_budget'])
            self.assertEqual(sum(map(len,view['groups'].values())),len(roster(club,s['year'],s)))
            from veritabani import unregister
            for entry in view['groups']['GK']:
                unregister(s,entry['player']['id'])
            self.assertEqual(squad_review(s)['groups']['GK'],[])
            p=roster(club,s['year'],s)[0]
            state(s,p)['contract']=s['year']+1
            self.assertTrue(any(r['player']['id']==p['id'] and r['expiry']==s['year']+1
                                for group in squad_review(s)['groups'].values() for r in group))
            from sozlesme import expire
            state(s,p)['contract']=s['year']
            expire(s)
            self.assertIn(p,squad_review(s)['expired'])
            self.assertNotIn(p,roster(club,s['year'],s))

    def test_invalid_feedback_rejected(self):
        s=new('GALATASARAY',seed=12)
        advance(s)
        raw=json.loads(encode(s))
        next(iter(raw['weekly_feedback']['players'].values()))['minutes']=91
        with self.assertRaises(SaveError):
            decode(json.dumps(raw))

    def test_contract_diagnostic_and_free_signing(self):
        s=new('GALATASARAY',seed=34,models=False)
        p=player(s,'53537')
        s['released'][p['id']]=s['year']
        club=s['club']
        terms=asking_terms(s,p,club)
        terms.update(wage=round(terms['wage']*1.45),signing=0)
        self.assertEqual(player_objection(s,p,club,1,100,0,'Rotation'),'compensation')
        self.assertEqual(deal(s,p['id'],club,1,**terms),(False,'fee'))
        old_budget=s['finance'][club]['wage_budget']
        s['finance'][club]['wage_budget']=0
        self.assertEqual(deal(s,p['id'],club,0,**terms),(False,'budget'))
        s['finance'][club]['wage_budget']=old_budget
        self.assertEqual(deal(s,p['id'],club,0,**terms),(True,'accepted'))
        self.assertEqual(deal(s,p['id'],club,0,**terms),(False,'unavailable'))
        self.assertEqual(renew(s,p['id'],**terms),(True,'accepted'))

    def test_tkinter_tr_en_and_long_names(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI

        root=tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        ui=UI(root)
        ui.begin(new('GALATASARAY',seed=15,models=False))
        p=roster(ui.s['club'],ui.s['year'],ui.s)[0]
        self.addCleanup(p.update,name=p['name'])
        p['name']='Uzun Oyuncu Adı ' * 8
        for lang in ('TR','EN'):
            ui.lang=lang
            for screen in (ui.weekly_page,ui.review_page,ui.offers_page):
                screen()
                root.update_idletasks()
        advance(ui.s)
        ui.weekly_page()
        root.update_idletasks()
        tree=next(w for f in ui.body.winfo_children() for w in f.winfo_children()
                  if isinstance(w,ttk.Treeview))
        self.assertTrue(any(p['name'].strip() in str(tree.item(i,'values')) for i in tree.get_children()))
        from transfer import add_offer
        from veritabani import TEAMS
        ui.s['offers'].clear()
        buyers=[team for team in TEAMS if team!=ui.s['club']][:2]
        for fee,buyer in zip((10000,999),buyers):
            self.assertTrue(add_offer(ui.s,p,buyer,fee,
                            dict(years=1,wage=100,signing=0,role='Rotation')))
        ui.offers_page()
        root.update_idletasks()
        offers=next(w for f in ui.body.winfo_children() for w in f.winfo_children()
                    if isinstance(w,ttk.Treeview))
        self.assertEqual(len(offers.get_children()),2)
        root.tk.call(offers.heading(2,'command'))
        self.assertEqual(offers.get_children(),('1','0'))
        ui.negotiate(p, renewal=True)
        root.update_idletasks()
        self.assertTrue(any(isinstance(w,tk.Toplevel) for w in root.winfo_children()))


if __name__ == '__main__':
    unittest.main()

