import json
import tkinter as tk
from tkinter import ttk
from unittest import TestCase

from arayuz import UI
from kariyer import LiveMatch, advance, new
from kayit import SaveError, decode, encode
from mac import eligible
from mevkiler import fit_level
from taktik_denetim_v093 import measure
from test_v088_2d import button, descendants
from veritabani import roster


def career():
    return new('GALATASARAY',seed=9300,match_model=4,tactics_model=True)


class TacticalEngine(TestCase):
    def replacement(self,match,position,fits):
        return next(p['id'] for p in roster(match.s['club'],match.s['year'],match.s)
                    if p['pos']!='GK' and p['id'] not in match.used and eligible(match.s,p)
                    and bool(fit_level(p,position))==fits)

    def test_unsuitable_saved_role_falls_back_after_emergency_substitution(self):
        s=career()
        m=LiveMatch(s)
        side=m.human
        outgoing=next(pid for role,pid in m.slots[side] if role=='RB')
        incoming=self.replacement(m,'RB',False)
        s['player_roles']={s['club']:{incoming:'defensive_back'}}
        m=LiveMatch(s)
        self.assertTrue(m.substitute(outgoing,incoming))
        self.assertIn(('RB',incoming),m.slots[side])
        self.assertEqual(m.pitch.role(side,incoming,'RB'),'wingback')
        self.assertFalse(m.assign_role(incoming,'defensive_back'))
        self.assertEqual(s['player_roles'][s['club']][incoming],'defensive_back')

    def test_outfield_substitute_inherits_slot_anchor_after_red_card(self):
        m=LiveMatch(career())
        side=m.human
        dismissed=next(pid for role,pid in m.slots[side] if role=='CB')
        outgoing=next(pid for role,pid in m.slots[side] if role=='RB')
        incoming=self.replacement(m,'RB',True)
        self.assertTrue(m.assign_role(outgoing,'defensive_back'))
        m.pitch.card(side,dismissed,2)
        anchor=m.pitch.anchor[side][outgoing]
        self.assertTrue(m.substitute(outgoing,incoming))
        m.pitch.align()
        self.assertEqual(len(m.slots[side]),10)
        self.assertIn(('RB',incoming),m.slots[side])
        self.assertEqual(m.pitch.anchor[side][incoming],anchor)
        self.assertNotIn(dismissed,m.pitch.anchor[side])
        self.assertNotIn(outgoing,m.pitch.anchor[side])
        self.assertFalse(m.assign_role(dismissed,'stopper'))
        self.assertEqual(m.pitch.role(side,incoming,'RB'),'wingback')
        m.pitch.card(side,incoming,2)
        self.assertEqual(len(m.slots[side]),9)
        self.assertFalse(m.assign_role(incoming,'defensive_back'))

    def test_emergency_keeper_keeps_goalkeeping_position_after_red_card(self):
        m=LiveMatch(career())
        side=m.human
        keeper=next(pid for role,pid in m.slots[side] if role=='GK')
        outgoing=next(pid for role,pid in m.slots[side] if role=='RB')
        incoming=next(p['id'] for p in roster(m.s['club'],m.s['year'],m.s)
                      if p['pos']=='GK' and p['id'] not in m.used and eligible(m.s,p))
        self.assertTrue(m.assign_role(outgoing,'defensive_back'))
        m.pitch.card(side,keeper,2)
        self.assertTrue(m.substitute(outgoing,incoming))
        m.pitch.align()
        self.assertEqual(len(m.slots[side]),10)
        self.assertIn(('GK',incoming),m.slots[side])
        self.assertEqual(m.pitch.anchor[side][incoming],(.055 if side==0 else .945,.5))
        self.assertIsNone(m.pitch.role(side,incoming,'GK'))
        self.assertFalse(m.assign_role(incoming,'wingback'))

    def test_same_minute_changes_keep_only_the_final_effective_decisions(self):
        s=career()
        m=LiveMatch(s)
        side=m.human
        pid=next(pid for role,pid in m.slots[side] if role=='CM')
        for _ in range(12):
            m.step()
        for key,value in (('line',1),('press',1),('line',-1),('press',0)):
            self.assertTrue(m.instruction(key,value))
        for role in ('ball_winner','box_to_box','playmaker','ball_winner'):
            self.assertTrue(m.assign_role(pid,role))
        self.assertFalse(m.assign_role(pid,'ball_winner'))
        self.assertEqual(m.team_orders[side]['line'],-1)
        self.assertEqual(m.pitch.role(side,pid,'CM'),'ball_winner')
        self.assertEqual(m.analysis['decisions'],[[12,side,'line',0,-1]])
        self.assertEqual(m.analysis['role_changes'],[[12,side,pid,'playmaker','ball_winner']])
        m.finish()
        self.assertTrue(m.commit())
        self.assertNotIn('player_roles',s)
        self.assertNotIn('tactical_plans',s)

    def test_paired_tactics_change_passes_regains_and_position(self):
        for mode,low,high,metric in (
                ('press',-1,1,'regains'),('width',-1,1,'wide'),
                ('passing',-1,1,'pass_m'),('role','defensive_back','wingback','back')):
            with self.subTest(tactic=mode):
                a=sum(measure(seed,mode,low)[metric] for seed in range(9301,9309))
                b=sum(measure(seed,mode,high)[metric] for seed in range(9301,9309))
                self.assertGreater(b,a)

    def test_live_instructions_and_roles_affect_next_steps_without_rewriting_plan(self):
        s=career()
        s['tactical_plans']={s['club']:{'line':1,'passing':0}}
        starting=LiveMatch(s)
        back=next(pid for position,pid in starting.slots[starting.human] if position=='RB')
        s['player_roles']={s['club']:{back:'wingback'}}
        m=LiveMatch(s)
        side=m.human
        start=m.team_orders[side]['line']
        self.assertEqual(start,1)
        for _ in range(70):
            m.step()
        pos,pid=next((pos,pid) for pos,pid in m.slots[side] if pos=='RB')
        self.assertFalse(m.assign_role(pid,'target'))
        self.assertTrue(m.assign_role(pid,'defensive_back'))
        self.assertTrue(m.instruction('line',-1))
        self.assertEqual(m.minute,70)
        self.assertEqual(m.pitch.role(side,pid,pos),'defensive_back')
        self.assertEqual(m.analysis['role_changes'][0][:3],[70,side,pid])
        m.step()
        self.assertEqual(m.minute,71)
        m.finish()
        self.assertTrue(m.commit())
        restored=decode(encode(s))
        self.assertEqual(restored['tactical_plans'][s['club']]['line'],1)
        self.assertEqual(restored['player_roles'][s['club']],{back:'wingback'})
        self.assertIn([70,side,'line',1,-1],restored['last_tactical_review']['analysis']['decisions'])
        self.assertEqual(restored['last_tactical_review']['analysis']['role_changes'],m.analysis['role_changes'])

    def test_capture_and_quick_play_share_authoritative_result(self):
        s=career()
        s['tactical_plans']={s['club']:{'press':1,'passing':1,'line':-1}}
        quick=decode(encode(s))
        self.assertTrue(advance(quick))
        live=LiveMatch(s)
        live.capture=True
        live.finish()
        self.assertTrue(live.frames)
        self.assertTrue(live.commit())
        self.assertEqual(json.loads(encode(s)),json.loads(encode(quick)))

    def test_invalid_order_is_rejected_and_legacy_order_is_inactive(self):
        s=career()
        s['tactical_plans']={s['club']:{'line':4}}
        with self.assertRaises(SaveError):
            decode(encode(s))
        old=new('GALATASARAY',seed=9300,match_model=4)
        restored=decode(encode(old))
        self.assertNotIn('tactics_model',restored)
        self.assertFalse(LiveMatch(restored).instruction('line',-1))


class TacticalPlanDialog(TestCase):
    def test_switching_players_preserves_pending_roles_and_explicit_automatic(self):
        s=career()
        s['lang']='EN'
        m=LiveMatch(s)
        slots=[(position,pid) for position,pid in m.slots[m.human] if position!='GK']
        back=slots[0][1]
        centre=slots[1][1]
        s['player_roles']={s['club']:{back:'target',centre:'stopper'}}
        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        ui.autosave=lambda:None
        ui.begin(s)
        plan=ui.tactical_plan_page()
        who,role=[w for w in descendants(plan) if isinstance(w,ttk.Combobox)][-2:]

        def select(box,value):
            box.current(value) if isinstance(value,int) else box.set(value)
            box.event_generate('<<ComboboxSelected>>')

        self.assertEqual(role.get(),'Automatic')
        self.assertNotIn('Target forward',role['values'])
        select(role,'Defensive fullback')
        select(who,1)
        self.assertEqual(role.get(),'Centre-back')
        select(role,'Automatic')
        select(who,0)
        self.assertEqual(role.get(),'Defensive fullback')
        select(who,1)
        self.assertEqual(role.get(),'Automatic')
        button(plan,'Apply').invoke()
        self.assertEqual(s['player_roles'][s['club']],{back:'defensive_back'})
