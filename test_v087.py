import json
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from futbol_kalibrasyonu import shot_probabilities, touchline_crossing
from kariyer import LiveMatch, advance, new, rollover
from kayit import decode, encode
from tema import MenuButton, PALETTE, install


def career(model=4, seed=813):
    return new('GALATASARAY', seed=seed, match_model=model)


from test_fixtures import legacy_source

class CalibrationTests(TestCase):
    def test_touchline_crossing_and_last_touch(self):
        self.assertEqual(touchline_crossing((.3,.2),(.7,-.2)),(.5,0))
        self.assertIsNone(touchline_crossing((.9,.8),(1.5,1.1)))
        m=LiveMatch(career())
        defender=m.slots[1][3][1]
        self.assertTrue(m.pitch.boundary((.3,.2),(.7,-.2),1,defender))
        self.assertEqual((m.pitch.restart,m.pitch.side,m.pitch.ball),('throw',0,(.5,0)))
        m.step()
        self.assertEqual([r[1:4:2] for r in m.play if r[3].startswith('throw')],[[1,'throw_awarded'],[0,'throw']])

    def test_controlled_keeper_quality_and_shot_conditions(self):
        shooter={'Finishing':13,'Composure':13}
        keeper={key:10 for key in ('Positioning','Reflexes','Handling','One on ones')}
        lo=shot_probabilities(.23,.18,.25,1,.70,shooter,dict(keeper,Reflexes=5))
        hi=shot_probabilities(.23,.18,.25,1,.70,shooter,dict(keeper,Reflexes=17))
        self.assertEqual(hi[0],lo[0])
        self.assertGreater(hi[1],lo[1])
        self.assertLess(hi[1]-lo[1],.09)
        self.assertLess(shot_probabilities(.41,.40,.55,.6,.7,shooter,keeper)[0],hi[0])

    def test_pass_time_interference_and_direct_restart_exception(self):
        m=LiveMatch(career())
        p=m.pitch
        passer,candidate,target=[pid for _,pid in m.slots[0][-3:]]
        rivals=[pid for _,pid in m.slots[1]]
        for pid in rivals:p.xy[pid]=(.60,.8)
        p.xy[rivals[0]]=(.91,.45)
        p.xy[rivals[1]]=(.82,.45)
        p.xy[passer]=(.51,.45)
        p.xy[target]=(.81,.45)
        p.xy[candidate]=(.84,.45)
        p.receive(0,passer)
        self.assertFalse(p.before_delivery(target,'throw'))
        self.assertTrue(p.before_delivery(target,None))
        self.assertEqual((p.restart,m.play[-1][2]),('indirect',candidate))

    def test_corner_continuation_tags_following_goal(self):
        m=LiveMatch(career());p=m.pitch;side=m.human
        p.dead_ball('corner',side,(.99 if not side else .01,.02))
        p.prefs[side]={'corner':'short'}
        with patch.object(m.rng,'random',return_value=0):
            m.step()
        self.assertEqual(p.corner_phase,(side,m.minute))
        m.minute+=1
        p.set_piece=None
        with patch.object(m.rng,'uniform',return_value=0), patch.object(m.rng,'random',side_effect=(.99,0,.99)):
            p.shoot()
        self.assertTrue(any(row[3]=='set_piece_goal' for row in m.play))

    def test_capture_matches_quick(self):
        initial=encode(career())
        a,b=decode(initial),decode(initial)
        advance(a)
        m=LiveMatch(b)
        m.capture=True
        m.finish()
        self.assertTrue(m.commit())
        self.assertEqual(json.loads(encode(a)),json.loads(encode(b)))

    def test_old_models_round_trip(self):
        src=legacy_source(self, 'top ant v0.8.6', sibling=True)
        for model in (1,2,3):
            script=f"from kariyer import new,advance;from kayit import encode;s=new('GALATASARAY',seed=813,match_model={model});print(encode(s));advance(s);print(encode(s))"
            before,after=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',script],
                                                 cwd=src,encoding='utf8').splitlines()
            state=decode(before)
            advance(state)
            self.assertEqual(json.loads(encode(state)),json.loads(after))

    def test_league_and_rollover_remain_turkish(self):
        s=career()
        self.assertEqual(len(s['schedule']),306)
        for _ in range(34):
            self.assertTrue(advance(s))
        self.assertTrue(rollover(s))
        self.assertEqual(len(decode(encode(s))['schedule']),306)
        self.assertEqual(len(s['finance']),18)


class ThemeTests(TestCase):
    def test_model_four_set_piece_dialog(self):
        from arayuz import UI
        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        ui.autosave=lambda:None
        ui.begin(career())
        dialog=ui.set_piece_page()
        self.assertIsNotNone(dialog)
        dialog.destroy()

    def test_popup_selected_disabled_and_keyboard(self):
        from tkinter import ttk
        root=tk.Tk()
        self.addCleanup(root.destroy)
        install(root)
        output=[]
        button=MenuButton(root,'Taktik',[('Pass',lambda:output.append(0)),('Defence',lambda:output.append(1))])
        button.pack()
        root.update()
        button.state(['disabled'])
        button.open()
        self.assertIsNone(button.popup)
        button.state(['!disabled'])
        button.open()
        box=button.popup.winfo_children()[0]
        root.update()
        self.assertEqual(box.cget('background'),PALETTE['row'])
        box.event_generate('<Down>')
        box.event_generate('<Return>')
        root.update()
        self.assertEqual(output,[1])
        button.open()
        box=button.popup.winfo_children()[0]
        root.update()
        box.event_generate('<Escape>')
        self.assertIsNone(button.popup)
        combo=ttk.Combobox(root,values=('One','Two'),state='readonly')
        combo.pack()
        root.update()
        root.tk.call('ttk::combobox::Post',str(combo))
        listbox=str(combo)+'.popdown.f.l'
        self.assertEqual(root.tk.call(listbox,'cget','-background'),PALETTE['row'])
        root.tk.call('ttk::combobox::Unpost',str(combo))
