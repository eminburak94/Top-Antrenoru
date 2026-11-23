"""Windows Tkinter beta smoke test with a real transfer and isolated save."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import tkinter as tk
from tkinter import ttk

from arayuz import UI
from hazirlik import DAYS, rest
from oyun import check_package
from test_v088_2d import button, descendants


def find(parent, kind, predicate=lambda _:True):
    return next(w for w in descendants(parent) if isinstance(w,kind) and predicate(w))


class BetaUI(TestCase):
    def test_career_transfer_match_and_disk_reload(self):
        with TemporaryDirectory() as directory:
            output=Path(directory)/'probe.json'
            check_package(output)
            result=json.loads(output.read_text(encoding='utf8'))
            self.assertEqual((result['club'],result['formation'],result['week'],result['played']),
                             ('FENERBAHÇE','4-3-3',2,9))
            self.assertTrue(result['transfer'] and result['reload'] and result['canvas_items'])

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
                prep=button(ui.body,'Book opponent' if lang=='EN' else 'Rakibi planla')
                self.assertTrue(prep.winfo_ismapped())
                forward=button(ui.body,'Advance preparation week' if lang=='EN' else 'Hazırlık haftasını ilerlet')
                self.assertTrue(forward.winfo_ismapped())
                for _ in range(DAYS):
                    self.assertTrue(rest(ui.s))
                ui.menu()
                ui.dashboard()
                root.update()
                news=button(ui.body,'News' if lang=='EN' else 'Haberler')
                self.assertGreaterEqual(news.winfo_width(),news.winfo_reqwidth())
                ui.tactics()
                root.update()
                self.assertTrue(find(ui.body,ttk.Combobox).winfo_ismapped())
                ui.market()
                root.update()
                self.assertTrue(button(ui.body,'Make offer' if lang=='EN' else 'Teklif ver').winfo_ismapped())
