from collections import defaultdict
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from kariyer import advance, new
from kayit import decode, encode
from mac import Match, manual_slots, select_slots
from oyuncu import attributes, state
from sozlesme import asking_terms
from transfer import deal
from veritabani import HISTORICAL, P, available, player, roster
from yarisma import opening_date, window

ROOT=Path(__file__).resolve().parent


from test_fixtures import legacy_source

class TesterFixes(unittest.TestCase):
    def test_tactics_reaches_motor_after_reload(self):
        s=new('GALATASARAY',seed=19)
        fixture=next(m for m in s['schedule'] if m['week']==1 and s['club'] in (m['home'],m['away']))
        default=Match(s,fixture,19)
        s.update(formation='4-3-3',style='Attack')
        automatic=select_slots(s,s['club'])
        ids=[pid for _,pid in automatic]
        ids[1],ids[2]=ids[2],ids[1]
        self.assertTrue(manual_slots(s,s['club'],ids))
        self.assertFalse(manual_slots(s,s['club'],[ids[0]]*11))
        self.assertFalse(manual_slots(s,s['club'],ids[1:]+ids[:1]))
        s['manual_xi']=ids
        loaded=decode(encode(s))
        motor=Match(loaded,fixture,19)
        side=int(fixture['away']==s['club'])
        self.assertEqual(motor.starters[side],ids)
        self.assertNotEqual(motor.slots[side],default.slots[side])
        self.assertEqual((default.style,motor.style),('Balanced','Attack'))
        self.assertEqual(default.rng.getstate(),motor.rng.getstate())
        self.assertNotEqual(default.strengths[side],motor.strengths[side])
        state(loaded,player(loaded,ids[0]))['injury']=1
        self.assertFalse(manual_slots(loaded,s['club'],ids))
        self.assertNotIn(ids[0], [pid for _,pid in select_slots(loaded,s['club'])])

    def test_dates_windows_and_sequential_weeks(self):
        s=new('GALATASARAY',seed=23)
        first=next(m for m in s['schedule'] if m['week']==1 and s['club'] in (m['home'],m['away']))
        self.assertEqual(opening_date(2000,first),'2000-08-13')
        self.assertTrue(all(opening_date(2000,m) for m in s['schedule'] if m['week']==1))
        self.assertIsNone(opening_date(2001,first))
        for week in range(1,21):
            self.assertEqual(s['week'],week)
            self.assertEqual(window(s),week in (1,2,3,18,19))
            self.assertTrue(advance(s))
            self.assertEqual(len(s['results']),week)

    def test_old_save_retains_attribute_values(self):
        code="""from kariyer import new
from kayit import encode
from oyuncu import attributes
from veritabani import player
import json
s=new('GALATASARAY',seed=3)
print(encode(s))
print(json.dumps(attributes(s,player(s,'29663'))))
"""
        import json
        raw, expected=subprocess.check_output([sys.executable,'-X','utf8','-B','-c',code],
                                     cwd=legacy_source(self, 'yedek_v0.7.9', root=ROOT),encoding='utf8').splitlines()
        s=decode(raw)
        self.assertNotIn('attribute_profile',s)
        self.assertEqual(attributes(s,player(s,'29663')),json.loads(expected))

    def test_attribute_distribution(self):
        s=new('GALATASARAY',seed=17)
        sums=defaultdict(lambda:[0,0,0,0])
        maximum=[0,0]
        for p in (*P.values(),*HISTORICAL.values()):
            s['attribute_profile']=1
            old=attributes(s,p)
            s['attribute_profile']=2
            current=attributes(s,p)
            for i,a in enumerate((old,current)):
                self.assertEqual(len(a),36)
                self.assertTrue(all(1<=v<=20 for v in a.values()))
                maximum[i]+=sum(v==20 for v in a.values())
            row=sums[p['pos']]
            row[0]+=1
            row[1]+=current['Finishing']
            row[2]+=current['Tackling']
            row[3]+=current['Reflexes']
        self.assertEqual(maximum,[96,92])
        t=attributes(s,player(s,'29479'))
        j=attributes(s,player(s,'29663'))
        self.assertEqual((j['Finishing'],j['Tackling'],j['Marking']),(20,15,15))
        self.assertEqual((t['Reflexes'],t['One on ones'],t['Passing'],t['Vision'],t['Finishing']),(20,20,14,15,13))
        self.assertGreater(sums['GK'][3]/sums['GK'][0],sums['GK'][1]/sums['GK'][0])

    def test_gui_tactics_market_and_identity_links(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI
        root=tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        ui=UI(root)
        s=new('GALATASARAY',seed=8,models=False)
        ui.begin(s)
        def descendants(parent, cls):
            return [w for child in parent.winfo_children()
                    for w in ([child] if isinstance(child,cls) else [])+descendants(child,cls)]
        def button(parent,text):
            return next(w for w in descendants(parent,ttk.Button) if w['text']==text)
        for lang in ('TR','EN'):
            ui.lang=lang
            ui.tactics()
            self.assertEqual(len(descendants(ui.body,ttk.Combobox)),13)
            button(ui.body,ui.management_text('apply_xi')).invoke()
            self.assertIn('manual_xi',s)
            button(ui.body,ui.management_text('auto_xi')).invoke()
            self.assertTrue(s['auto_xi'])
            ui.table()
            table=descendants(ui.body,ttk.Treeview)[0]
            item=next(i for i in table.get_children() if table.item(i,'values')[0]=='FENERBAHÇE')
            table.selection_set(item)
            button(ui.body,ui.management_text('club_squad')).invoke()
            table=descendants(ui.body,ttk.Treeview)[0]
            table.selection_set('0')
            with patch.object(ui,'profile') as profile:
                button(ui.body,ui.management_text('open_profile')).invoke()
                self.assertEqual(profile.call_args.args[0]['id'],roster('FENERBAHÇE',2000,s)[0]['id'])
        s.pop('auto_xi')
        with patch('arayuz.messagebox.askyesno',side_effect=[False,True]):
            self.assertFalse(ui.confirm_lineup())
            self.assertTrue(ui.confirm_lineup())
        s['match_mode']='quick'
        with patch.object(ui,'autosave'):
            ui.next()
        self.assertEqual(s['week'],2)
        p=player(s,'53537')
        s['released'][p['id']]=2000
        ui.market()
        free_filter=next(box for box in descendants(ui.body,ttk.Combobox) if 'Free' in box.cget('values'))
        free_filter.set('Free')
        button(ui.body,'Search').invoke()
        table=descendants(ui.body,ttk.Treeview)[0]
        self.assertGreater(len(table.get_children()),0)
        for item in table.get_children():
            self.assertEqual(table.item(item,'values')[1],'Free')
        terms=asking_terms(s,p,s['club'])
        terms.update(wage=round(terms['wage']*1.45),signing=0)
        self.assertTrue(available(s,p))
        self.assertTrue(deal(s,p['id'],s['club'],0,**terms)[0])
        first,second=player(s,'29479'),player(s,'29663')
        old=second['name']
        self.addCleanup(second.update,name=old)
        second['name']=first['name']
        ui.report(dict(home=s['club'],away='FENERBAHÇE',x=2,y=0,
                       events=[(11,s['club'],first['id']),(31,s['club'],second['id'])]))
        report=descendants(root,tk.Toplevel)[-1]
        scorers=descendants(report,tk.Listbox)[1]
        scorers.selection_set(1)
        with patch.object(ui,'profile') as profile:
            button(report,ui.management_text('open_profile')).invoke()
            self.assertEqual(profile.call_args.args[0]['id'],second['id'])


if __name__ == '__main__':
    unittest.main()
