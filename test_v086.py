import json
from pathlib import Path
import subprocess
import sys
import tkinter as tk
import unittest

from futbol_kurallari import Referee,offside
from kariyer import LiveMatch,advance,new
from kayit import decode,encode
from mac import eligible
from mac_gorunum import interpolate
from veritabani import roster


def game(seed=813):
    return new('GALATASARAY',seed=seed,match_model=3)


from test_fixtures import legacy_source

class FixedRandom:
    def random(self):return 0


class RulesTests(unittest.TestCase):
    def test_offside_line_active_play_and_exemptions(self):
        rivals=[(.95,.6),(.80,.4),(.60,.5)]
        target=(.84,.45)
        self.assertTrue(offside(0,(.65,.4),target,rivals))
        self.assertTrue(offside(1,(.35,.4),(.16,.45),[(1-x,y) for x,y in rivals]))
        self.assertFalse(offside(0,(.45,.4),(.49,.3),rivals))
        self.assertFalse(offside(0,(.85,.4),target,rivals))
        self.assertFalse(offside(0,(.65,.4),(.80,.4),rivals))
        self.assertFalse(offside(0,(.65,.4),target,rivals,active=False))
        for restart in ('throw','corner','goal_kick'):
            self.assertFalse(offside(0,(.65,.4),target,rivals,restart=restart))

    def test_offside_stops_play_and_awards_indirect(self):
        m=LiveMatch(game())
        pitch=m.pitch
        giver=m.slots[0][3][1];target=m.slots[0][-1][1]
        pitch.xy[giver]=(.58,.4);pitch.xy[target]=(.90,.46)
        for i,(_,uid) in enumerate(m.slots[1]):pitch.xy[uid]=(.82-i*.022,.5)
        pitch.receive(0,giver)
        self.assertTrue(pitch.before_delivery(target,None))
        self.assertEqual((pitch.restart,pitch.side,pitch.owner),('indirect',1,None))
        m.step()
        self.assertTrue(any(row[3]=='indirect' and row[1]==1 for row in m.play))

    def test_referee_advantage_and_discipline(self):
        m=LiveMatch(game())
        p=m.pitch
        attacker=m.slots[0][-1][1];defender=m.slots[1][3][1]
        p.xy[attacker]=(.68,.50)
        p.receive(0,attacker)
        m.card_rng=FixedRandom()
        p.foul(defender,.47)
        self.assertEqual(p.owner,attacker)
        self.assertEqual(p.pending_cards,[(1,defender,1)])
        self.assertEqual([r[3] for r in m.play[-2:]],['foul','advantage'])
        p.flush_cards()
        self.assertIn(defender,m.yellows)
        p.foul(defender,.5,allow_advantage=False)
        self.assertEqual([r[3] for r in m.play[-4:]],['foul','yellow','second_yellow','red'])
        self.assertNotIn(defender,[pid for _,pid in m.slots[1]])
        self.assertEqual(m.strengths[1]['count'],10)
        another=m.slots[1][3][1]
        p.receive(0,attacker)
        p.foul(another,.96)
        self.assertEqual(m.play[-1][3],'red')
        self.assertNotIn(another,[pid for _,pid in m.slots[1]])
        self.assertEqual(Referee.assign(8),Referee.assign(8))

    def test_corner_layout_short_delivery_and_taker_replacement(self):
        counts=[]
        for approach in ('short','near','far','central'):
            s=game()
            s['set_pieces']={s['club']:{'corner':approach}}
            m=LiveMatch(s);m.capture=True
            side=m.human
            point=(.99 if side==0 else .01,.02)
            m.pitch.dead_ball('corner',side,point)
            m.step()
            corner=next(row for row in m.play if row[3]=='corner')
            layout=next(f for f in m.frames if f[4]['set_piece']=='corner' and f[3]==corner[2])
            self.assertEqual(layout[1],point)
            self.assertEqual(sum(len(side) for side in layout[2]),22)
            counts.append(sum(m.shots))
        self.assertEqual(counts[0],0)
        m=LiveMatch(game())
        side=m.human
        outgoing=m.slots[side][-1][1]
        key='left_corner' if side==0 else 'right_corner'
        m.pitch.prefs[side]={key:outgoing}
        m.pitch.dead_ball('corner',side,(.99 if side==0 else .01,.02))
        self.assertEqual(m.pitch.take(side,'corner'),outgoing)
        incoming=next(p for p in roster(m.s['club'],m.s['year'],m.s) if p['id'] not in m.used and eligible(m.s,p))
        self.assertTrue(m.substitute(outgoing,incoming['id']))
        self.assertNotEqual(m.pitch.take(side,'corner'),outgoing)

    def test_free_kick_wall_penalty_and_restart_states(self):
        for kind in ('freekick','penalty','throw','goal_kick','kickoff'):
            m=LiveMatch(game());m.capture=True
            m.pitch.dead_ball(kind,0,(.895,.5) if kind=='penalty' else (.79,.48) if kind=='freekick'
                                  else (.5,0) if kind=='throw' else (.06,.5) if kind=='goal_kick' else (.5,.5))
            m.step()
            event=next(r for r in m.play if r[3]==kind)
            frames=[f for f in m.frames if f[4]['set_piece']==kind]
            self.assertTrue(frames)
            if kind=='freekick':self.assertTrue(any(len(f[4]['wall'])==4 for f in frames))
            if kind=='penalty':self.assertEqual(sum(m.shots),1)
            if kind=='goal_kick':self.assertEqual(event[2],m.slots[0][0][1])
        m=LiveMatch(game());m.minute=45;m.step()
        self.assertTrue(any(row[0]==46 and row[1]==1 and row[3]=='kickoff' for row in m.play))

    def test_roles_change_position_and_pass_preference(self):
        m=LiveMatch(game());p=m.pitch
        side=m.human
        pos,pid=m.slots[side][-1]
        p.side=side
        p.role_prefs[side]={pid:'finisher'}
        finisher=p.target_adjust(side,pid,pos,.5,.35)
        p.role_prefs[side][pid]='holding'
        holding=p.target_adjust(side,pid,pos,.5,.35)
        self.assertGreater(finisher[0] if side==0 else 1-finisher[0],
                           holding[0] if side==0 else 1-holding[0])
        p.role_prefs[side][pid]='playmaker'
        self.assertGreater(p.pass_preference(side,pid,pos),0)

    def test_quick_live_and_rng_share_result(self):
        raw=encode(game())
        a,b=map(decode,(raw,raw))
        advance(a)
        m=LiveMatch(b);m.capture=True;m.finish()
        rng=m.rng.getstate()
        interpolate(m.frames)
        self.assertEqual(m.rng.getstate(),rng)
        self.assertTrue(m.commit())
        self.assertEqual(json.loads(encode(a)),json.loads(encode(b)))

    def test_model_one_and_two_replay_same_week(self):
        folder=legacy_source(self, 'top ant v0.8.5', sibling=True)
        for model in (1,2):
            cmd=("from kariyer import new,advance; from kayit import encode; "
                 f"s=new('GALATASARAY',seed=813,match_model={model}); print(encode(s)); advance(s); print(encode(s))")
            before,after=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',cmd],cwd=folder,encoding='utf-8').splitlines()
            s=decode(before)
            advance(s)
            self.assertEqual(json.loads(encode(s)),json.loads(after))

    def test_bilingual_set_piece_controls(self):
        from arayuz import UI
        from tkinter import ttk
        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        ui.autosave=lambda:None
        s=game();ui.begin(s)
        for lang,size in zip(('TR','EN','TR'),('960x600','1280x720','1920x1080')):
            root.geometry(size)
            ui.lang=lang
            ui.tactics()
            w=ui.set_piece_page()
            root.update()
            self.assertTrue(w.winfo_ismapped())
            frame=w.winfo_children()[0]
            controls=[item for item in frame.winfo_children() if isinstance(item,ttk.Combobox)]
            controls[5].current(3)
            next(item for item in frame.winfo_children() if isinstance(item,ttk.Button)).invoke()
            self.assertEqual(decode(encode(s))['set_pieces'][s['club']]['corner'],'short')
