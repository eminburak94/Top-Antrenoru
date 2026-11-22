import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

from arayuz import UI
from kariyer import advance,LiveMatch,new
from kayit import SaveError,decode,encode,load_game,save_game
from mac_gorunum import interpolate
from personel import candidates,start_scout
from veritabani import roster


def widgets(root,kind):
    for child in root.winfo_children():
        if isinstance(child,kind):yield child
        yield from widgets(child,kind)


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk()
        self.addCleanup(self.root.destroy)
        self.ui=UI(self.root)
        self.ui.autosave=lambda:None
        self.s=new('GALATASARAY',seed=813,match_model=1)
        self.ui.begin(self.s)

    def button(self,text,parent=None):
        return next(e for e in widgets(parent or self.ui.body,ttk.Button) if e.cget('text')==text)

    def test_layout_three_sizes_and_two_languages(self):
        for index,(w,h) in enumerate(((960,600),(1280,720),(1920,1080))):
            self.root.geometry(f'{w}x{h}')
            self.root.tk.call('tk','scaling',(1.333,1.667,2.0)[index])
            for locale in ('TR','EN'):
                self.ui.lang=locale
                self.ui.menu()
                for page in (self.ui.dashboard,self.ui.squad,self.ui.market,lambda:self.ui.staff_page('all')):
                    page()
                    self.root.update()
                    self.assertEqual((self.root.winfo_width(),self.root.winfo_height()),(w,h))
                    right=self.root.winfo_rootx()+w
                    buttons=widgets(self.ui.body,ttk.Button)
                    self.assertTrue(all(e.winfo_rootx()+e.winfo_width()<=right for e in buttons if e.winfo_ismapped()))

    def test_player_shortlist_filters_offer_and_hidden_ca(self):
        self.ui.lang='EN'
        self.ui.market()
        table=next(widgets(self.ui.body,ttk.Treeview))
        first=table.get_children()[0]
        self.assertEqual(table.set(first,6),'—')
        table.selection_set(first)
        self.button('Shortlist').invoke()
        combos=list(widgets(self.ui.body,ttk.Combobox))
        next(w for w in combos if 'Shortlist' in w.cget('values')).set('Shortlist')
        self.root.after(150,self.root.quit)
        self.root.mainloop()
        self.assertEqual(table.get_children(),(first,))
        table.selection_set(first)
        with patch.object(self.ui,'negotiate') as offer:
            self.button('Make offer').invoke()
            self.assertEqual(offer.call_args.args[0]['id'],first)
        fields=[w for w in widgets(self.ui.body,ttk.Entry) if w.winfo_class()=='TEntry']
        fields[0].insert(0,'no matching footballer!')
        fields[1].insert(0,'16')
        self.root.after(150,self.root.quit)
        self.root.mainloop()
        self.assertFalse(table.get_children())
        saved=decode(encode(self.s))['ui_preferences']
        self.assertEqual(saved['players'],[first])
        self.assertEqual(saved['player_filters']['min_age'],'16')
        self.button('Reset').invoke()
        self.assertTrue(table.get_children())

    def test_staff_search_sort_long_name_and_profile(self):
        self.ui.lang='EN'
        pool=self.s['staff_system']['pool']
        key=next(iter(pool))
        pool[key]['name']='An Example With A Long Staff Name'
        self.ui.staff_page('all')
        table=next(widgets(self.ui.body,ttk.Treeview))
        self.root.tk.call(table.heading(4,'command'))
        wages=[pool[uid]['wage'] for uid in table.get_children()]
        self.assertEqual(wages,sorted(wages))
        self.root.tk.call(table.heading(4,'command'))
        wages=[pool[uid]['wage'] for uid in table.get_children()]
        self.assertEqual(wages,sorted(wages,reverse=True))
        field=next(widgets(self.ui.body,ttk.Entry))
        field.insert(0,'Long Staff Name')
        self.root.after(150,self.root.quit)
        self.root.mainloop()
        self.assertEqual(table.get_children(),(key,))
        self.assertGreater(table.column(0,'width'),230)
        table.selection_set(key)
        self.button(self.ui.management_text('open_profile')).invoke()
        self.assertTrue(any(w.title()==pool[key]['name'] for w in widgets(self.root,tk.Toplevel)))


class ModelTests(unittest.TestCase):
    def test_interpolation_preserves_engine_endpoints_and_rng(self):
        s=new('GALATASARAY',seed=813,match_model=1)
        match=LiveMatch(s);match.capture=True
        match.step()
        before=match.rng.getstate()
        frames=interpolate(match.frames)
        self.assertEqual((frames[0],frames[-1]),(match.frames[0],match.frames[-1]))
        self.assertGreater(len(frames),len(match.frames))
        self.assertEqual(before,match.rng.getstate())

    def test_v083_save_load_and_new_preferences(self):
        previous=Path(__file__).resolve().parent.parent/'top ant v0.8.3'
        code="from kariyer import new; from kayit import encode; print(encode(new('GALATASARAY',seed=813,match_model=1)))"
        raw=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',code],cwd=previous,encoding='utf-8')
        restored=decode(raw)
        self.assertEqual(restored['match_model'],1)
        restored['ui_preferences']={'players':['123'],'player_filters':{'min_age':'18'}}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'career.json'
            save_game(restored,path)
            self.assertEqual(load_game(path)['ui_preferences'],restored['ui_preferences'])
        restored['ui_preferences']['players']=['123','123']
        with self.assertRaises(SaveError):decode(encode(restored))

    def test_scout_skill_ranges_are_bounded_and_saved(self):
        s=new('GALATASARAY',seed=813,match_model=1)
        p=next(iter(candidates(s)))
        self.assertTrue(start_scout(s,p['id']))
        advance(s);advance(s)
        report=s['staff_system']['reports'][-1]
        self.assertEqual(set(report['groups']),{'technical','mental','physical'})
        self.assertTrue(all(1<=a<b<=20 for a,b in report['groups'].values()))
        self.assertEqual(decode(encode(s))['staff_system']['reports'][-1],report)
