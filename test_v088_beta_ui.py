"""Windows Tkinter beta smoke test with a real transfer and isolated save."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk

from arayuz import UI
from kayit import decode, encode
from sozlesme import asking_terms
from test_v088_2d import button, descendants
from transfer import asking_fee, deal
from veritabani import all_players, available, roster


def find(parent, kind, predicate=lambda _:True):
    return next(w for w in descendants(parent) if isinstance(w,kind) and predicate(w))


class BetaUI(TestCase):
    def test_career_transfer_match_and_disk_reload(self):
        with TemporaryDirectory() as directory, patch.dict(os.environ,{'LOCALAPPDATA':directory}):
            path=Path(directory)/'test-save.json'
            root=tk.Tk()
            try:
                ui=UI(root)
                button(root,'TR / EN').invoke()
                combo=find(root,ttk.Combobox)
                combo.set('FENERBAHÇE')
                button(root,'Start career').invoke()
                s=ui.s
                self.assertEqual((s['club'],s['year'],s['match_model']),('FENERBAHÇE',2000,4))

                ui.squad()
                root.update()
                table=find(ui.body,ttk.Treeview)
                self.assertEqual(len(table.get_children()),len(roster(s['club'],s['year'],s)))

                ui.tactics()
                root.update()
                shape=find(ui.body,ttk.Combobox,lambda w:'4-4-2' in w.cget('values'))
                shape.set('4-3-3')
                shape.event_generate('<<ComboboxSelected>>')
                root.update()
                self.assertEqual(s['formation'],'4-3-3')

                ui.market()
                root.update()
                market=find(ui.body,ttk.Treeview)
                visible=set(market.get_children())
                for player in all_players(s):
                    pid=player['id']
                    owner=s['owners'].get(pid)
                    if pid not in visible or owner==s['club'] or not owner and not available(s,player):
                        continue
                    terms=asking_terms(s,player,s['club'],'Starter')
                    clone=decode(encode(s))
                    accepted,_=deal(clone,pid,s['club'],asking_fee(s,player),terms['years'],
                                    terms['wage'],terms['signing'],'Starter')
                    if accepted:break
                else:self.fail('No valid offer candidate in the visible market')
                market.selection_set(pid)
                button(ui.body,'Make offer').invoke()
                offer=find(root,tk.Toplevel)
                with patch('arayuz.messagebox.showinfo',return_value='ok') as message:
                    button(offer,'Submit offer').invoke()
                self.assertTrue(message.called)
                self.assertFalse(offer.winfo_exists())
                self.assertEqual(s['owners'][pid],s['club'])

                ui.live()
                match=find(root,tk.Toplevel)
                button(match,'Step').invoke()
                root.update()
                with patch('arayuz.messagebox.askyesno',return_value=True):
                    button(match,'Finish match').invoke()
                root.update()
                self.assertFalse(match.winfo_exists())
                self.assertEqual((s['week'],len(s['results'][0])),(2,9))
                self.assertTrue(any(s['club'] in (r['home'],r['away']) for r in s['results'][0]))
                with patch('arayuz.filedialog.asksaveasfilename',return_value=str(path)):
                    ui.save()
                snapshot=encode(s)
                self.assertTrue(path.is_file())
            finally:
                root.destroy()
            root=tk.Tk()
            try:
                ui=UI(root)
                with patch('arayuz.filedialog.askopenfilename',return_value=str(path)):
                    button(root,'Kayıt yükle').invoke()
                self.assertEqual(encode(ui.s),snapshot)
            finally:
                root.destroy()

    def test_localized_navigation_and_tactics_fit_supported_windows(self):
        root=tk.Tk()
        self.addCleanup(root.destroy)
        ui=UI(root)
        base=float(root.tk.call('tk','scaling'))
        for width,height,lang,factor in ((960,600,'TR',1.5),(960,600,'EN',1.5),(1280,720,'EN',1.25),(1920,1080,'TR',1)):
            with self.subTest(width=width,language=lang,scale=factor):
                root.tk.call('tk','scaling',base*factor)
                root.geometry(f'{width}x{height}')
                ui.lang=lang
                ui.start()
                root.update()
                button(root,'Start career' if lang=='EN' else 'Kariyeri başlat').invoke()
                root.update()
                categories=[w for w in ui.nav.winfo_children() if isinstance(w,ttk.Button)]
                self.assertTrue(categories)
                for widget in categories:
                    self.assertTrue(widget.winfo_ismapped(),widget.cget('text'))
                    self.assertGreaterEqual(widget.winfo_width(),widget.winfo_reqwidth(),widget.cget('text'))
                news=button(ui.body,'News' if lang=='EN' else 'Haberler')
                self.assertGreaterEqual(news.winfo_width(),news.winfo_reqwidth())
                ui.tactics()
                root.update()
                self.assertTrue(find(ui.body,ttk.Combobox).winfo_ismapped())
                ui.market()
                root.update()
                self.assertTrue(button(ui.body,'Make offer' if lang=='EN' else 'Teklif ver').winfo_ismapped())
