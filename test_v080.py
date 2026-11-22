"""Isolated staff, budget, training and scouting regressions."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest
from unittest.mock import patch

import personel as st
from finans import operating
from kariyer import LiveMatch, advance, new
from kayit import decode, encode
from oyuncu import age_at,develop,prepare_player,state
from veritabani import HISTORICAL,player,roster


def game():
    return new('GALATASARAY',seed=800,models=False)


class StaffTests(unittest.TestCase):
    def test_contract_limit_expiry_and_single_owner(self):
        s=game()
        team=s['club']
        pid,row=st.active(s,team,'assistant')[0]
        free=next(key for key,p in s['staff_system']['pool'].items() if p['club'] is None)
        self.assertEqual(st.contract(s,team,free,2),(False,'staff_capacity'))
        self.assertTrue(st.contract(s,team,pid,3,renew=True)[0])
        self.assertTrue(st.release(s,team,pid))
        s['finance'][team]['cash']=0
        self.assertEqual(st.contract(s,team,free,2),(False,'staff_budget'))
        s['finance'][team]['cash']=1000000
        self.assertTrue(st.contract(s,team,free,2)[0])
        self.assertFalse(st.contract(s,'FENERBAHÇE',free,2)[0])
        s['year']=2002
        st.season_open(s)
        self.assertIsNone(s['staff_system']['pool'][free]['club'])
        self.assertEqual(len(s['staff_system']['pool']),120)

    def test_payroll_not_repeated_and_changes_with_hiring(self):
        s=game()
        team=s['club']
        cash=s['finance'][team]
        initial=st.payroll(s,team)
        admin=11000+s['club_reputation'][team]*100
        operating(s,team)
        operating(s,team)
        self.assertEqual(cash['staff'],admin+initial)
        s=decode(encode(s))
        cash=s['finance'][team]
        operating(s,team)
        self.assertEqual(cash['staff'],admin+initial)
        pid,row=st.active(s,team,'fitness')[0]
        wage=row['wage']
        self.assertTrue(st.release(s,team,pid))
        s['week']=2
        operating(s,team)
        self.assertEqual(cash['staff'],2*(admin+initial)-wage)
        self.assertTrue(st.contract(s,team,pid,2)[0])
        s['week']=3
        operating(s,team)
        self.assertEqual(cash['staff'],3*(admin+initial)-wage)


    def test_four_week_payroll_recalculation(self):
        s=game()
        team=s['club']
        expected=11000+s['club_reputation'][team]*100+st.payroll(s,team)
        for _ in range(4):
            operating(s,team)
            restored=decode(encode(s))
            operating(restored,team)
            s=restored
            advance(s)
        self.assertEqual(s['finance'][team]['staff'],4*expected)

    def test_pool_exhaustion_and_empty_staff(self):
        s=game()
        team=s['club']
        for pid,_ in st.active(s,team):st.release(s,team,pid)
        self.assertEqual(st.payroll(s,team),0)
        self.assertEqual(st.effects(s,team),(0,0,0))
        self.assertFalse(st.recommendation(s)['slots'])
        target=next(iter(s['owners']))
        self.assertFalse(st.start_scout(s,target))
        self.assertFalse(st.contract(s,team,'staff-missing',2)[0])
        # Exhaust the available supply without minting another candidate.
        pool=s['staff_system']['pool']
        for row in pool.values():row.update(club='FENERBAHÇE',start=2000,end=2003)
        count=len(pool)
        st.season_open(s)
        self.assertEqual(len(pool),count)
        self.assertFalse(any(row['club'] is None for row in pool.values()))

    def test_coaches_and_manual_priority(self):
        s=game()
        team=s['club']
        coach_id,coach=st.active(s,team,'coach')[0]
        p=next(p for p in roster(team,2000,s) if p['pos']!='GK' and age_at(p,2000,1)<23)
        state(s,p).update(condition=40,ability=10,potential=16)
        values=[]
        for skill in (1,20):
            trial=deepcopy(s)
            st.active(trial,team,'fitness')[0][1]['skills']['fitness']=skill
            prepare_player(trial,p,team)
            values.append(state(trial,p)['condition'])
        self.assertEqual(values,[63,66])
        high=st.development_factor((0,20,20),True)
        self.assertEqual(high,1.08)
        z=state(s,p)
        z.update(training_weeks=20,injury_matches=4)
        a,b=deepcopy(s),deepcopy(s)
        develop(a,p,random.Random(32),minutes=1800,facility=1)
        develop(b,p,random.Random(32),minutes=1800,facility=high)
        self.assertGreater(state(b,p)['ability'],state(a,p)['ability'])
        self.assertLess(state(b,p)['ability'],16)
        self.assertTrue(st.delegate(s,team,'team_training',coach_id))
        coach['skills']['coaching']=20
        self.assertIn(st.team_training(s,team),('Development','Rest'))
        s['training']='Normal'
        self.assertEqual(st.team_training(s,team),'Normal')
        self.assertTrue(st.delegate(s,team,'team_training',None))
        self.assertTrue(st.delegate(s,team,'individual_training',coach_id))
        self.assertTrue(st.release(s,team,coach_id))
        self.assertIsNone(st.assigned(s,team,'individual_training'))

    def test_scouts_timing_uncertainty_future_and_roundtrip(self):
        base=game()
        team=base['club']
        scout_id,_=st.active(base,team,'scout')[0]
        future=next(p for p in HISTORICAL.values() if p['available_from']>'2020')
        self.assertFalse(st.start_scout(base,future['id']))
        self.assertNotIn(future['id'],{p['id'] for p in st.candidates(base)})
        target='29663'
        intervals=[]
        for skill in (5,20):
            s=deepcopy(base)
            scout=s['staff_system']['pool'][scout_id]
            scout['skills'].update(judging=skill,potential=skill)
            self.assertTrue(st.delegate(s,team,'scouting',scout_id))
            self.assertTrue(st.start_scout(s,target))
            self.assertFalse(st.start_scout(s,target))
            s=decode(encode(s))
            advance(s)
            self.assertEqual(s['staff_system']['reports'],[])
            s=decode(encode(s))
            advance(s)
            report=s['staff_system']['reports'][0]
            self.assertEqual(report['confidence'],skill)
            intervals.append(sum(hi-lo for lo,hi in report['bands']))
            self.assertEqual(decode(encode(s))['staff_system'],s['staff_system'])
        self.assertGreater(intervals[0],intervals[1])

    def test_advice_never_replaces_manual_lineup(self):
        from mac import select_slots
        s=game()
        team=s['club']
        ids=[pid for _,pid in select_slots(s,team)]
        ids[1],ids[2]=ids[2],ids[1]
        s['manual_xi']=ids
        pid,row=st.active(s,team,'assistant')[0]
        st.delegate(s,team,'lineup',pid)
        before=s['manual_xi'][:]
        self.assertIn('slots',st.recommendation(s))
        self.assertEqual([key for _,key in select_slots(s,team)],before)
        self.assertTrue(st.release(s,team,pid))
        self.assertIsNone(st.assigned(s,team,'lineup'))

    def test_legacy_and_live_equivalence(self):
        source=Path(__file__).resolve().parent/'yedek_v0.7.9.3'
        script="""from kariyer import new,advance
from kayit import encode
s=new('GALATASARAY',seed=800)
print(encode(s));advance(s);print(encode(s))
"""
        raw,expected=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',script],
                             encoding='utf8',cwd=source).splitlines()
        old=decode(raw)
        self.assertNotIn('staff_system',old)
        advance(old)
        self.assertEqual(json.loads(expected),json.loads(encode(old)))
        s=game()
        a=decode(encode(s))
        self.assertTrue(st.start_scout(s,'29663'))
        self.assertTrue(st.start_scout(a,'29663'))
        for _ in range(2):
            advance(s)
            live=LiveMatch(a)
            live.finish()
            self.assertTrue(live.commit())
            self.assertFalse(live.commit())
            self.assertEqual(json.loads(encode(s)),json.loads(encode(a)))

    def test_staff_gui_at_minimum_size(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI
        root=tk.Tk()
        self.addCleanup(root.destroy)
        u=UI(root)
        u.begin(game())
        root.geometry('960x600')
        s=u.s
        u.autosave=lambda:None
        for lang in ('TR','EN'):
            u.lang=lang
            u.menu()
            for screen in (u.staff_page,u.delegation_page,u.scout_page):
                screen()
                root.update()
                buttons=[w for box in u.body.winfo_children() for w in (box,*box.winfo_children())
                         if isinstance(w,ttk.Button)]
                self.assertTrue(buttons)
                for b in buttons:
                    self.assertTrue(b.winfo_ismapped())
                    self.assertLessEqual(b.winfo_rootx()+b.winfo_width(),root.winfo_rootx()+960)
            u.staff_page()
            root.update()
            table=next(w for box in u.body.winfo_children() for w in box.winfo_children()
                       if isinstance(w,ttk.Treeview))
            pid=st.active(s,s['club'])[0][0]
            table.selection_set(pid)
            release=next(w for box in u.body.winfo_children() for w in box.winfo_children()
                         if isinstance(w,ttk.Button) and w['text']==u.management_text('staff_release'))
            with patch('personel_ui.messagebox.askyesno',return_value=False):release.invoke()
            self.assertEqual(s['staff_system']['pool'][pid]['club'],s['club'])
            with patch('personel_ui.messagebox.askyesno',return_value=True):release.invoke()
            self.assertIsNone(s['staff_system']['pool'][pid]['club'])


if __name__=='__main__':
    unittest.main()
