"""Position model acceptance tests."""
from dataclasses import asdict
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from kariyer import new
from kayit import decode, encode
from mac import Match, manual_slots, select_slots
from mevkiler import LAYOUTS, coordinates, fit_level, label
from veritabani import player


from test_fixtures import legacy_source

class PositionTests(unittest.TestCase):
    def test_six_formations_and_manual_roundtrip(self):
        s=new('GALATASARAY',seed=792)
        fixture=next(f for f in s['schedule'] if f['week']==1 and s['club'] in (f['home'],f['away']))
        for shape,layout in LAYOUTS.items():
            with self.subTest(shape=shape):
                s['formation']=shape
                automatic=select_slots(s,s['club'],use_manual=False)
                self.assertEqual(tuple(p for p,_ in automatic),layout)
                self.assertEqual(len(set(pid for _,pid in automatic)),11)
                s['manual_xi']=[pid for _,pid in automatic]
                snapshot=decode(encode(s))
                self.assertEqual(manual_slots(snapshot,s['club'],snapshot['manual_xi']),automatic)
                engine=Match(snapshot,fixture,43)
                side=int(fixture['away']==s['club'])
                self.assertEqual(engine.slots[side],automatic)
                self.assertEqual(asdict(engine.finish()),asdict(Match(decode(encode(s)),fixture,43).finish()))
                self.assertEqual(len(set(coordinates(layout))),11)

    def test_fit_model_and_skills_reach_engine(self):
        s=new('GALATASARAY',seed=792)
        fixture=next(f for f in s['schedule'] if f['week']==1 and s['club'] in (f['home'],f['away']))
        match=Match(s,fixture,19)
        pid=next(pid for role,pid in select_slots(s,s['club']) if role=='RB')
        p=player(s,pid)
        self.assertNotEqual(fit_level(dict(pos='RB'),'RB'),fit_level(dict(pos='RB'),'CB'))
        self.assertEqual(fit_level(dict(pos='CB',alternate_positions=['RB']),'RB'),3)
        base=match.strength([('RB',pid)])['D']
        match.profiles[pid]['Crossing']+=4
        self.assertGreater(match.strength([('RB',pid)])['D'],base)
        for first,second,group in [('RB','CB','D'),('DM','AM','M'),('RW','CM','M')]:
            self.assertNotEqual(match.strength([(first,pid)])[group],match.strength([(second,pid)])[group])
        self.assertTrue(p['pos'])

    def test_legacy_engine_matches_backup(self):
        import json
        source=legacy_source(self, 'yedek_v0.7.9.1')
        code="""import json
from dataclasses import asdict
from kariyer import new
from kayit import encode
from mac import Match
s=new('GALATASARAY',seed=54)
f=next(f for f in s['schedule'] if f['week']==1 and s['club'] in (f['home'],f['away']))
print(encode(s))
print(json.dumps(asdict(Match(s,f,12).finish())))
"""
        raw,result=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',code],
                            cwd=source,encoding='utf8').splitlines()
        s=decode(raw)
        self.assertNotIn('position_model',s)
        f=next(f for f in s['schedule'] if f['week']==1 and s['club'] in (f['home'],f['away']))
        self.assertEqual(asdict(Match(s,f,12).finish()),json.loads(result))

    def test_pitch_and_labels(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI
        r=tk.Tk()
        self.addCleanup(r.destroy)
        u=UI(r)
        u.begin(new('GALATASARAY',seed=57))
        r.geometry('960x600')
        for lang in ('TR','EN'):
            u.lang=lang
            for shape in LAYOUTS:
                u.s['formation']=shape
                u.tactics()
                r.update()
                pitch=next(x for x in u.body.winfo_children() if isinstance(x,tk.Canvas))
                self.assertEqual(len([x for x in pitch.winfo_children() if isinstance(x,ttk.Combobox)]),11)
                all_labels=[pitch.itemcget(item,'text') for item in pitch.find_all() if pitch.type(item)=='text']
                self.assertIn(label('GK',lang),all_labels)
                self.assertGreater(pitch.winfo_height(),90)


if __name__=='__main__':
    unittest.main()
