import json
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

from arayuz import UI
from kariyer import LiveMatch,advance,new
from kayit import decode,encode
from mac import SHOT_EVENTS,eligible
from mac_gorunum import interpolate
from sozlesme import asking_terms
from veritabani import player,roster


def game(seed=813):
    return new('GALATASARAY',seed=seed,match_model=2)


def widgets(parent,kind):
    for child in parent.winfo_children():
        if isinstance(child,kind):yield child
        yield from widgets(child,kind)


from test_fixtures import legacy_source

class PitchTests(unittest.TestCase):
    def test_pass_chain_restarts_shots_and_coordinates(self):
        observed=set()
        for seed in range(810,822):
            m=LiveMatch(game(seed));m.capture=True
            consecutive=0
            previous=None
            while m.minute<90:
                before=len(m.play)
                m.step()
                for _,side,pid,kind,target in m.play[before:]:
                    observed.add(kind)
                    if kind=='pass':
                        if previous==(side,pid):consecutive+=1
                        previous=(side,target)
                    elif kind not in ('sub','yellow','red'):
                        previous=None
                if m.pitch.owner is not None:
                    self.assertEqual(m.pitch.ball,m.pitch.xy[m.pitch.owner])
                self.assertTrue(all(0<=v<=1 for pair in m.pitch.xy.values() for v in pair))
            self.assertGreater(consecutive,0)
            self.assertEqual(len(m.analysis['periods']),18)
            self.assertTrue(all(row['origin']!=row['destination'] for row in m.pitch.trace))
            self.assertEqual(sum(m.shots),sum(row[3] in SHOT_EVENTS for row in m.play))
        self.assertTrue({'kickoff','corner','freekick','goal','saved','pass_failed','tackle','sub'}<=observed)

    def test_restart_transitions_and_keeper_depth(self):
        from saha_motoru import RESTARTS
        for kind in RESTARTS:
            m=LiveMatch(game())
            side=1
            point=(.1,.5) if kind=='penalty' else (.5,.04)
            m.pitch.dead_ball(kind,side,point)
            m.step()
            self.assertTrue(any(e[1]==side and e[3]==kind for e in m.play))
            if kind=='penalty':self.assertEqual(sum(m.shots),1)
        m=LiveMatch(game())
        for _ in range(90):
            m.step()
            for side,slots in enumerate(m.slots):
                for role,pid in slots:
                    if role=='GK':
                        x=m.pitch.xy[pid][0]
                        self.assertLessEqual(x if side==0 else 1-x,.181)

    def test_three_modes_and_intervention_equivalence(self):
        initial=encode(game())
        direct,watched=map(decode,(initial,initial))
        advance(direct)
        m=LiveMatch(watched);m.capture=True;m.finish()
        before=m.rng.getstate()
        interpolate(m.frames)
        self.assertEqual(before,m.rng.getstate())
        self.assertTrue(m.commit())
        self.assertEqual(json.loads(encode(direct)),json.loads(encode(watched)))
        outcomes=[]
        for show in (True,False):
            s=decode(initial)
            m=LiveMatch(s);m.capture=show
            for _ in range(32):m.step()
            m.instruction('press',1)
            m.instruction('tempo',1)
            m.finish()
            outcomes.append(m.result())
        self.assertEqual(*outcomes)

    def test_substitution_and_pressure_load(self):
        m=LiveMatch(game());m.step()
        side=m.human
        out=next(pid for role,pid in m.slots[side] if role!='GK')
        new_player=next(p for p in roster(m.s['club'],m.s['year'],m.s) if eligible(m.s,p) and p['id'] not in m.used)
        self.assertTrue(m.substitute(out,new_player['id']))
        m.instruction('press',1);m.instruction('tempo',1)
        m.finish()
        self.assertEqual(m.minutes[out],1)
        self.assertGreater(m.minutes[new_player['id']],0)
        self.assertGreater(m.loads[side],m.loads[1-side])
        self.assertTrue(m.commit())
        self.assertEqual(decode(encode(m.career))['match_model'],2)

    def test_v084_replay_exactly_matches(self):
        folder=legacy_source(self, 'top ant v0.8.4', sibling=True)
        cmd=("from kariyer import new,advance; from kayit import encode; "
             "s=new('GALATASARAY',seed=813,match_model=1); print(encode(s)); advance(s); print(encode(s))")
        source,expected=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',cmd],cwd=folder,encoding='utf-8').splitlines()
        s=decode(source)
        advance(s)
        self.assertEqual(json.loads(encode(s)),json.loads(expected))


class Playthrough(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk();self.addCleanup(self.root.destroy)
        self.ui=UI(self.root)
        self.root.geometry('960x600')
        self.ui.autosave=lambda:None
        self.s=game()
        self.ui.begin(self.s)

    def button(self,parent,label):
        return next(w for w in widgets(parent,ttk.Button) if w.cget('text')==label)

    def test_a_match_preparation_live_press_and_analysis(self):
        self.button(self.ui.body,'Maça hazırlan').invoke()
        self.ui.tactics()
        self.button(self.ui.body,self.ui.management_text('auto_xi')).invoke()
        match=LiveMatch(self.s)
        with patch('arayuz.LiveMatch',return_value=match):self.ui.live()
        self.root.update()
        dialog=next(widgets(self.root,tk.Toplevel))
        next(widgets(dialog,ttk.Checkbutton)).invoke()
        start=self.button(dialog,'Başlat');pause=self.button(dialog,'Durdur')
        start.invoke();pause.invoke()
        minute=match.minute
        self.root.update()
        self.assertEqual(match.minute,minute)
        press=next(w for w in widgets(dialog,ttk.Combobox) if w.cget('width')==8)
        press.current(2);press.event_generate('<<ComboboxSelected>>');self.root.update()
        self.assertEqual(match.instructions[match.human][0],1)
        self.button(dialog,'Oyuncu değiştir').invoke()
        sub=next(widgets(dialog,tk.Toplevel))
        combos=list(widgets(sub,ttk.Combobox))
        combos[0].current(1);combos[1].current(0)
        self.button(sub,'Uygula').invoke()
        self.assertEqual(match.subs,1)
        with patch('arayuz.messagebox.askyesno',side_effect=[False,True]):
            self.button(dialog,'Maçı bitir').invoke()
            self.assertEqual(self.s['week'],1)
            self.button(dialog,'Maçı bitir').invoke()
        self.root.update()
        self.assertEqual(self.s['week'],2)
        self.ui.last_report()
        self.assertIn('flow',self.s['last_tactical_review']['analysis'])

    def test_b_filter_scout_and_real_offer(self):
        self.ui.lang='EN'
        p=player(self.s,'53537')
        self.s['released'][p['id']]=2000
        self.ui.market()
        self.button(self.ui.body,'Advanced').invoke()
        position=next(w for w in widgets(self.ui.body,ttk.Combobox) if 'Left-back' in w.cget('values'))
        position.set('Left-back')
        prefs=self.s['ui_preferences']['player_filters']
        fields=[w for w in widgets(self.ui.body,ttk.Entry) if w.winfo_class()=='TEntry']
        fields[2].insert(0,'22')
        fields[4].insert(0,'4500')
        self.button(self.ui.body,'Search').invoke()
        self.assertEqual((prefs['position'],prefs['max_age'],prefs['wage']),('LB','22','4500'))
        self.button(self.ui.body,'Reset').invoke()
        name=next(w for w in widgets(self.ui.body,ttk.Entry) if w.winfo_class()=='TEntry')
        name.insert(0,p['name'])
        self.button(self.ui.body,'Search').invoke()
        table=next(widgets(self.ui.body,ttk.Treeview))
        self.assertIn(p['id'],table.get_children())
        table.selection_set(p['id'])
        with patch('tkinter.messagebox.showinfo'):
            self.button(self.ui.body,'Scout').invoke()
            self.assertTrue(any(job['player']==p['id'] for job in self.s['staff_system']['jobs']))
            self.button(self.ui.body,'Make offer').invoke()
            dialog=next(widgets(self.root,tk.Toplevel))
            entries=[w for w in widgets(dialog,ttk.Entry) if w.winfo_class()=='TEntry']
            wage=asking_terms(self.s,p,self.s['club'])['wage']
            entries[2].delete(0,'end');entries[2].insert(0,str(round(wage*1.45)))
            self.button(dialog,'Submit offer').invoke()
        self.assertEqual(self.s['owners'].get(p['id']),self.s['club'])

    def test_c_desk_training_decision_and_weekly_review(self):
        self.ui.dashboard()
        picker=next(widgets(self.ui.body,ttk.Combobox))
        picker.current(1);picker.event_generate('<<ComboboxSelected>>');self.root.update()
        self.assertEqual(self.s['training'],'Rest')
        self.s['match_mode']='quick'
        with patch('arayuz.messagebox.askyesno',return_value=True):self.ui.next()
        self.assertEqual(self.s['week'],2)
        self.assertTrue(self.s['inbox'])
        self.ui.dashboard()
        self.button(self.ui.body,'Haftalık rapor').invoke()
        self.assertEqual(self.s['weekly_feedback']['week'],1)
