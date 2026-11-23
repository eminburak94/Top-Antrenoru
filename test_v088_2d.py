from unittest import TestCase
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk

from arayuz import UI
from kariyer import LiveMatch, advance, new
from kayit import decode, encode
from mac_gorunum import Pitch, interpolate


def descendants(parent):
    for child in parent.winfo_children():
        yield child
        yield from descendants(child)


def button(parent, text):
    return next(w for w in descendants(parent) if isinstance(w,ttk.Button) and w.cget('text')==text)


class PlaybackTests(TestCase):
    def start_match(self, match, width=960, language='EN', scale=None):
        root=tk.Tk()
        self.addCleanup(root.destroy)
        if scale is not None:
            previous_scale=root.tk.call('tk','scaling')
            self.addCleanup(root.tk.call,'tk','scaling',previous_scale)
            root.tk.call('tk','scaling',scale)
        ui=UI(root)
        ui.autosave=lambda:None
        ui.lang=language
        ui.begin(match.s)
        root.geometry(f'{width}x600')
        root.update()
        with patch('arayuz.LiveMatch',return_value=match):
            ui.live()
        root.update()
        return root,next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))

    def test_controls_fit_a_small_match_window_at_high_tk_scale(self):
        for language in ('TR','EN'):
            with self.subTest(language=language):
                s=new('GALATASARAY',seed=901,match_model=4)
                s['lang']=language
                root,window=self.start_match(LiveMatch(s),language=language,scale=2.5)
                try:
                    window.geometry('800x510')
                    root.update()
                    right=window.winfo_rootx()+window.winfo_width()
                    bottom=window.winfo_rooty()+window.winfo_height()
                    for widget in descendants(window):
                        if isinstance(widget,(ttk.Button,ttk.Checkbutton,ttk.Combobox)):
                            self.assertTrue(widget.winfo_ismapped(),widget)
                            self.assertLessEqual(widget.winfo_rootx()+widget.winfo_width(),right)
                            self.assertLessEqual(widget.winfo_rooty()+widget.winfo_height(),bottom)
                finally:
                    window.destroy()

    def test_final_animation_commits_without_an_extra_step(self):
        s=new('GALATASARAY',seed=822,match_model=4)
        s['lang']='EN'
        quick=decode(encode(s))
        self.assertTrue(advance(quick))
        match=LiveMatch(s)
        while match.minute<89:match.step()
        root,window=self.start_match(match)
        highlights=next(w for w in descendants(window) if isinstance(w,ttk.Checkbutton) and w.cget('text')=='Highlights')
        highlights.invoke()
        with patch.object(match,'step',wraps=match.step) as step:
            for _ in range(50):
                if not window.winfo_exists():break
                button(window,'Step').invoke()
                root.update()
            self.assertFalse(window.winfo_exists())
            self.assertEqual(step.call_count,1)
        self.assertEqual(s['results'],quick['results'])

    def test_speed_pause_engine_tactics_and_substitution(self):
        s=new('GALATASARAY',seed=822,match_model=4)
        s['lang']='EN'
        match=LiveMatch(s)
        root,window=self.start_match(match)
        combos=[w for w in descendants(window) if isinstance(w,ttk.Combobox)]
        speed=next(w for w in combos if w.cget('values')==('1x','2x','4x'))
        speed.current(2)
        press=next(w for w in combos if w.cget('values')==('Low','Normal','High'))
        press.current(2)
        press.event_generate('<<ComboboxSelected>>')
        root.update()
        self.assertEqual(match.instructions[match.human][0],1)
        self.assertTrue(any(w.cget('text').startswith('Sent to match engine') for w in descendants(window)
                            if isinstance(w,ttk.Label)))
        button(window,'Start').invoke()
        button(window,'Pause').invoke()
        minute=match.minute
        self.assertFalse(root.tk.call('after','info'))
        self.assertEqual(match.minute,minute)
        button(window,'Substitute').invoke()
        dialog=next(w for w in window.winfo_children() if isinstance(w,tk.Toplevel))
        self.assertEqual(dialog.grab_current(),dialog)
        for combo in (w for w in descendants(dialog) if isinstance(w,ttk.Combobox)):
            combo.current(0)
        button(dialog,'Apply').invoke()
        self.assertFalse(dialog.winfo_exists())
        self.assertEqual(window.grab_current(),window)
        self.assertTrue(any(event[3]=='sub' for event in match.play))
        self.assertEqual(match.minute,minute)

    def test_fast_finish_yields_to_tk_then_completes(self):
        for model in (1,3,4):
            with self.subTest(model=model):
                s=new('GALATASARAY',seed=823,match_model=model)
                s['lang']='EN'
                match=LiveMatch(s)
                root,window=self.start_match(match)
                with patch('arayuz.messagebox.askyesno',return_value=True):
                    button(window,'Finish match').invoke()
                self.assertEqual(match.minute,0)
                observed=[]
                root.after(0,lambda:observed.append(match.minute))
                root.update()
                self.assertEqual(observed,[0])
                self.assertEqual(match.minute,90)
                self.assertEqual(s['week'],2)


class CanvasTests(TestCase):
    def test_interpolation_respects_stoppage_and_drops_identical_frames(self):
        a=(20,(.5,.5),((),()),None,dict(signal=None,set_piece=None,wall=(),referee=(.3,.6)))
        b=(20,(.55,.5),((),()),None,dict(signal='offside',set_piece=None,wall=(),referee=(.35,.6)))
        c=(20,(.60,.5),((),()),None,dict(signal='offside',set_piece=None,wall=(),referee=(.4,.6)))
        frames=interpolate([a,a,b,c])
        self.assertEqual(frames[:2],[a,b])
        self.assertEqual(frames[-1],c)
        self.assertEqual(len(frames),5)

    def test_repeat_frame_avoids_canvas_writes(self):
        root=tk.Tk()
        self.addCleanup(root.destroy)
        canvas=tk.Canvas(root,width=420,height=240)
        canvas.pack()
        root.update()
        render=Pitch(canvas,str,str)
        frame=(1,(.5,.5),(((1,.5,.5),),((2,.5,.5),)),1)
        render.draw(frame)
        with patch.object(canvas,'coords',wraps=canvas.coords) as coords:
            render.draw(frame)
            coords.assert_not_called()
        self.assertEqual(len(render.items),2)
