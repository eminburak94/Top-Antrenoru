import json
import unittest
from unittest.mock import patch

from kariyer import LiveMatch,advance,new
from kayit import decode,encode


def game(seed=813):
    return new('GALATASARAY',seed=seed,match_model=1)


class MatchTests(unittest.TestCase):
    def test_quick_and_live_with_or_without_frames_match(self):
        initial=encode(game())
        quick,text,spatial=map(decode,(initial,initial,initial))
        advance(quick)
        for state,capture in ((text,False),(spatial,True)):
            match=LiveMatch(state)
            match.capture=capture
            match.finish()
            self.assertEqual(bool(match.frames),capture)
            self.assertTrue(match.commit())
            self.assertFalse(match.commit())
        self.assertEqual(json.loads(encode(quick)),json.loads(encode(text)))
        self.assertEqual(json.loads(encode(quick)),json.loads(encode(spatial)))

    def test_intervention_frame_parity_and_bounds(self):
        raw=encode(game())
        results=[]
        for capture in (False,True):
            career=decode(raw)
            match=LiveMatch(career);match.capture=capture
            for _ in range(8):match.step()
            self.assertTrue(match.instruction('press',1))
            self.assertTrue(match.instruction('width',1))
            self.assertFalse(match.instruction('width',1))
            match.finish()
            before=match.rng.getstate()
            for minute,ball,sides in match.frames:
                self.assertEqual(minute,90)
                self.assertTrue(all(0<=x<=1 for x in ball))
                self.assertTrue(all(0<=x<=1 and 0<=y<=1 for team in sides for _,x,y in team))
            self.assertEqual(before,match.rng.getstate())
            match.commit()
            results.append(json.loads(encode(career)))
        self.assertEqual(*results)

    def test_tactics_can_change_shots_and_energy(self):
        changed=0
        for seed in range(810,822):
            raw=encode(game(seed))
            control=LiveMatch(decode(raw))
            adjusted=LiveMatch(decode(raw))
            side=adjusted.human
            adjusted.instruction('press',1)
            adjusted.instruction('tempo',1)
            adjusted.instruction('width',1)
            adjusted.finish();control.finish()
            self.assertLess(adjusted.energy(side),control.energy(side))
            changed+=adjusted.shots!=control.shots
        self.assertGreater(changed,0)

    def test_substitution_affects_played_minutes(self):
        from mac import eligible
        from veritabani import roster
        s=game()
        m=LiveMatch(s)
        m.step()
        self.assertTrue(any(m.substitute(out,p['id'])
            for _,out in list(m.slots[m.human]) for p in roster(s['club'],s['year'],m.s)
            if p['id'] not in m.used and eligible(m.s,p)))
        _,_,incoming,_,outgoing=m.play[-1]
        m.finish()
        self.assertEqual(m.minutes[outgoing],5)
        self.assertGreater(m.minutes[incoming],0)
        self.assertLessEqual(m.minutes[incoming],85)

    def test_inbox_is_bounded_and_reload_keeps_flow(self):
        s=game()
        for _ in range(15):advance(s)
        self.assertEqual(len(s['inbox']),12)
        self.assertEqual(len({(x['year'],x['week']) for x in s['inbox']}),12)
        a=decode(encode(s))
        advance(a);advance(s)
        self.assertEqual(json.loads(encode(a)),json.loads(encode(s)))

    def test_old_economy_and_match_flags_remain_independent(self):
        s=decode(encode(new('GALATASARAY',seed=811)))
        advance(s)
        self.assertEqual(s['economy_model'],2)
        self.assertNotIn('match_model',s)
        self.assertNotIn('inbox',s)


class ManagementTests(unittest.TestCase):
    def test_signing_bonus_can_compensate_only_with_new_formula(self):
        from sozlesme import asking_terms,player_objection
        from veritabani import roster
        s=game()
        club=s['club']
        baseline=decode(encode(s))
        del baseline['match_model']
        baseline['match_mode']='live'
        differences=[]
        for p in roster(club,s['year'],s):
            terms=asking_terms(s,p,club,'Starter')
            terms['wage']=int(terms['wage']*.82)
            terms['signing']=terms['wage']*14
            if player_objection(s,p,club,**terms) is None:
                differences.append(player_objection(baseline,p,club,**terms))
        self.assertIn('compensation',differences)

    def test_youth_exposure_helps_but_remains_below_potential(self):
        import random
        from oyuncu import develop,state
        from veritabani import roster
        s=game()
        p=dict(roster(s['club'],s['year'],s)[0],dob='1983-08-01')
        z=state(s,p)
        z.update(ability=10,potential=13,condition=90,training_weeks=14)
        same=decode(encode(s))
        develop(s,p,random.Random(31),minutes=0)
        develop(same,p,random.Random(31),minutes=3060)
        self.assertGreater(state(same,p)['ability'],state(s,p)['ability'])
        self.assertLess(state(same,p)['ability'],13)


class InterfaceTests(unittest.TestCase):
    def test_live_canvas_pause_finish_and_inbox_bilingual(self):
        import tkinter as tk
        from tkinter import ttk
        from arayuz import UI

        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)

        root=tk.Tk();self.addCleanup(root.destroy)
        ui=UI(root)
        root.geometry('960x600')
        ui.autosave=lambda:None
        for lang in ('TR','EN'):
            s=game();s['lang']=lang
            ui.begin(s);ui.preparation();ui.live();root.update()
            self.assertEqual((root.winfo_width(),root.winfo_height()),(960,600))
            pop=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
            self.assertLessEqual(pop.winfo_height(),600)
            def button(tr,en):
                return next(w for w in descendants(pop) if isinstance(w,ttk.Button) and w.cget('text')==ui.tr(tr,en))
            canvas=next(w for w in descendants(pop) if isinstance(w,tk.Canvas))
            self.assertGreater(len(canvas.find_all()),44)
            level=next(w for w in descendants(pop) if isinstance(w,ttk.Combobox) and w.cget('width')==8)
            level.current(2);level.event_generate('<<ComboboxSelected>>');root.update()
            button('Başlat','Start').invoke()
            button('Durdur','Pause').invoke()
            speed=next(w for w in descendants(pop) if isinstance(w,ttk.Combobox) and w.cget('width')==4)
            speed.current(2)
            button('Başlat','Start').invoke()
            button('Durdur','Pause').invoke()
            button('Maçı bitir','Finish match').invoke()
            self.assertEqual(s['week'],2)
            self.assertTrue(s['inbox'])
            self.assertIn('analysis',s['last_tactical_review'])
            self.assertTrue(any(row[2]=='press' for row in s['last_tactical_review']['analysis']['decisions']))
            ui.youth_watch()
            ui.last_report()
            root.update()
            for child in root.winfo_children():
                if isinstance(child,tk.Toplevel):child.destroy()
