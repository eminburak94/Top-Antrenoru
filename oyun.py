"""Tkinter entry point and executable distribution check."""
import sys
import tkinter as tk
from pathlib import Path


def check_package(output):
    import json
    import os
    from tempfile import TemporaryDirectory
    from tkinter import ttk
    from unittest.mock import patch

    from arayuz import UI
    from kayit import decode, encode, user_directory
    from sozlesme import asking_terms
    from transfer import asking_fee, deal
    from veritabani import HISTORICAL, P, TEAMS, all_players, available, roster

    def find(parent, kind, predicate=lambda _: True):
        for widget in parent.winfo_children():
            if isinstance(widget,kind) and predicate(widget):
                return widget
            nested=find(widget,kind,predicate)
            if nested is not None:
                return nested
        return None

    def click(window, text):
        find(window,ttk.Button,lambda w:w.cget('text')==text).invoke()

    with TemporaryDirectory() as folder, patch.dict(os.environ,{
        'LOCALAPPDATA':folder, 'USERPROFILE':folder,
    }):
        assert user_directory()==Path(folder)/'TopAntrenoru'/'v0.9.5'
        path=user_directory()/'saves'/'probe.json'
        root=tk.Tk()
        try:
            ui=UI(root)
            click(root,'Emeği Geçenler')
            assert find(root,ttk.Label,lambda w:w.cget('text')=='Emin Burak Öncel')
            click(root,'Ana menüye dön')
            click(root,'TR / EN')
            click(root,'Credits')
            assert find(root,ttk.Label,lambda w:w.cget('text')=='Local Pre-audit')
            click(root,'Back to main menu')
            find(root,ttk.Combobox).set('FENERBAHÇE')
            click(root,'Start career')
            s=ui.s
            assert (s['club'],s['year'],s['match_model'])==('FENERBAHÇE',2000,4)
            version=root.title()
            opponent=find(ui.body,ttk.Combobox,lambda w:'GALATASARAY' in w.cget('values'))
            opponent.set('GALATASARAY')
            click(ui.body,'Book opponent')
            s['match_mode']='quick'
            click(ui.body,'Advance preparation week')
            find(root,tk.Toplevel).destroy()
            assert s['preseason']['results'][0][:3]==[0,'FENERBAHÇE','GALATASARAY']
            assert not s['results'] and s['week']==1
            for _ in range(3):
                click(ui.body,'Advance preparation week')
            s['match_mode']='2d'

            ui.squad()
            root.update()
            assert len(find(ui.body,ttk.Treeview).get_children())==len(roster(s['club'],s['year'],s))
            ui.tactics()
            root.update()
            shape=find(ui.body,ttk.Combobox,lambda w:'4-4-2' in w.cget('values'))
            shape.set('4-3-3')
            shape.event_generate('<<ComboboxSelected>>')
            root.update()
            assert s['formation']=='4-3-3'
            ui.set_piece_page().destroy()

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
                accepted,_=deal(decode(encode(s)),pid,s['club'],asking_fee(s,player),
                                terms['years'],terms['wage'],terms['signing'],'Starter')
                if accepted:
                    break
            else:
                raise AssertionError('No valid offer candidate in the visible market')
            market.selection_set(pid)
            click(ui.body,'Make offer')
            offer=find(root,tk.Toplevel)
            with patch('arayuz.messagebox.showinfo',return_value='ok') as message:
                click(offer,'Submit offer')
            assert message.called and not offer.winfo_exists() and s['owners'][pid]==s['club']

            ui.live()
            popup=find(root,tk.Toplevel)
            click(popup,'Step')
            root.update()
            canvas_items=len(find(popup,tk.Canvas).find_all())
            assert canvas_items>=22
            with patch('arayuz.messagebox.askyesno',return_value=True):
                click(popup,'Finish match')
            root.update()
            assert not popup.winfo_exists()
            assert (s['week'],len(s['results'][0]))==(2,9)
            assert any(s['club'] in (r['home'],r['away']) for r in s['results'][0])
            with patch('arayuz.filedialog.asksaveasfilename',return_value=str(path)):
                ui.save()
            assert path.is_file()
            snapshot=encode(s)
        finally:
            root.destroy()

        root=tk.Tk()
        try:
            ui=UI(root)
            with patch('arayuz.filedialog.askopenfilename',return_value=str(path)):
                click(root,'Kayıt yükle')
            assert encode(ui.s)==snapshot
            result=dict(version=version,frozen=bool(getattr(sys,'frozen',False)),
                        clubs=len(TEAMS),players=len(P)+len(HISTORICAL),club=s['club'],
                        match_model=s['match_model'],formation=s['formation'],transfer=pid,
                        canvas_items=canvas_items,week=s['week'],played=len(s['results'][0]),reload=True,
                        credits=True,save_directory=user_directory().name)
            output.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
        finally:
            root.destroy()


def main():
    if len(sys.argv)==3 and sys.argv[1]=='--check-package':
        check_package(Path(sys.argv[2]))
        return
    from arayuz import UI
    root=tk.Tk()
    UI(root)
    root.mainloop()


if __name__=='__main__':
    main()
