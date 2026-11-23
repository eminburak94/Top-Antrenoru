import copy
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from antrenman import FOCUSES, INTENSITIES, MONTH_LIMIT, record_month
from kariyer import LiveMatch, advance, new
from kayit import decode, encode, load_game, save_game
from oyuncu import age_at, develop, prepare_player, state
from veritabani import roster

ROOT = Path(__file__).resolve().parent


def young(s):
    return next(p for p in roster(s['club'],s['year'],s) if age_at(p,s['year'],1)<25)


from test_fixtures import legacy_source

class TrainingTests(unittest.TestCase):
    def test_focus_intensity_recovery_and_injury_ab(self):
        s=new('GALATASARAY',seed=1)
        s.pop('staff_system')  # Keep the original no-staff training fixture.
        p=young(s)
        original=state(s,p)
        original.update(condition=40,ability=10,potential=17)
        results={}
        for focus in FOCUSES:
            for intensity in INTENSITIES:
                trial=copy.deepcopy(s)
                trial['training']='Development'
                trial['individual_training']={p['id']:[focus,intensity]}
                obs=prepare_player(trial,p,s['club'])
                z=state(trial,p)
                self.assertEqual(z['ability'],10)
                self.assertEqual(z.get('training_weeks',0),obs[3])
                results[focus,intensity]=(z['condition'],obs[3])
        self.assertEqual(results['physical','intense'],(55,1))
        self.assertEqual(results['physical','light'],(60,.65))
        self.assertEqual(results['technical','normal'],(61,.81))
        self.assertEqual(results['recovery','normal'],(68,0))
        s['auto_training']=True
        original['injury']=2
        obs=prepare_player(s,p,s['club'])
        self.assertEqual(obs,['recovery','normal','injured',0,0])
        self.assertEqual(original['injury'],2)

    def test_seasonal_credit_and_injury_reset_ab(self):
        baseline=new('GALATASARAY',seed=2)
        p=young(baseline)
        state(baseline,p).update(ability=10,potential=16)
        outcomes=[]
        for credits, injuries in ((0,0),(34,0),(34,12)):
            s=copy.deepcopy(baseline)
            z=state(s,p)
            z.update(training_weeks=credits,injury_matches=injuries)
            develop(s,p,random.Random(88),minutes=1400)
            self.assertEqual(z['injury_matches'],0)
            self.assertEqual(z['training_weeks'],0)
            self.assertLess(z['ability'],z['potential'])
            self.assertEqual(z['potential'],16)
            outcomes.append(z['ability'])
        self.assertGreater(outcomes[1],outcomes[0])
        self.assertLess(outcomes[2],outcomes[1])

    def test_old_save_month_dedup_and_live_parity(self):
        code="from kariyer import new; from kayit import encode; print(encode(new('GALATASARAY',seed=3)))"
        raw=subprocess.check_output([sys.executable,'-X','utf8','-B','-c',code],
                                     cwd=legacy_source(self, 'yedek_v0.7.8', root=ROOT),encoding='utf8')
        s=decode(raw)
        pid=young(s)['id']
        s['individual_training']={pid:['technical','light']}
        other=decode(encode(s))
        self.assertTrue(advance(s))
        m=LiveMatch(other)
        m.finish()
        self.assertTrue(m.commit())
        self.assertEqual(encode(s),encode(other))
        while not s['monthly_training']:
            advance(s)
            m=LiveMatch(other)
            m.finish()
            self.assertTrue(m.commit())
            self.assertEqual(encode(s),encode(other))
        history=copy.deepcopy(s['monthly_training'])
        record_month(s,s['weekly_feedback'],{})
        self.assertEqual(s['monthly_training'],history)
        report=history[0]
        recorded=report['players'][pid]
        self.assertGreaterEqual(recorded['participation'],1)
        self.assertGreater(recorded['training'],0)
        result_minutes=sum(r['minutes'].get(pid,0) for week in s['results'] for r in week)
        self.assertEqual(recorded['minutes'],result_minutes)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'isolated.json'
            save_game(s,path)
            self.assertEqual(encode(load_game(path)),encode(s))

    def test_long_career_bounded_reports_and_actual_season_change(self):
        s=new('GALATASARAY',seed=79)
        s['auto_training']=True
        for _ in range(10):
            for _ in range(34):
                self.assertTrue(advance(s))
            before=copy.deepcopy(s['fitness'])
            self.assertTrue(advance(s))
            actual=s['season_development']
            self.assertEqual(actual['year'],s['year']-1)
            for pid,change in actual['changes'].items():
                self.assertAlmostEqual(change,s['fitness'][pid]['ability']-before[pid]['ability'],places=2)
            self.assertLessEqual(len(s['monthly_training']),MONTH_LIMIT)
            self.assertEqual(encode(decode(encode(s))),encode(s))
        self.assertEqual(len(s['monthly_training']),MONTH_LIMIT)

    def test_training_and_monthly_gui_in_both_languages(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI
        root=tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        ui=UI(root)
        s=new('GALATASARAY',seed=17)
        ui.begin(s)
        ids=[p['id'] for p in roster(s['club'],s['year'],s)[:2]]
        for lang in ('TR','EN'):
            ui.lang=lang
            ui.training_page(ids)
            panel=next(w for w in ui.body.winfo_children() if isinstance(w,ttk.Frame))
            boxes=[w for w in panel.winfo_children() if isinstance(w,ttk.Combobox)]
            boxes[0].current(2)
            boxes[1].current(0)
            next(w for w in panel.winfo_children() if isinstance(w,ttk.Button)).invoke()
            self.assertTrue(all(s['individual_training'][pid]==['physical','light'] for pid in ids))
            ui.monthly_page()
            root.update_idletasks()
        while not s.get('monthly_training'):
            advance(s)
        ui.monthly_page()
        root.update_idletasks()


if __name__ == '__main__':
    unittest.main()
