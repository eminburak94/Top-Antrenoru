"""Tkinter entry point and bundled distribution check."""
import sys
import tkinter as tk
from pathlib import Path


def check_package(output):
    import json
    from tempfile import TemporaryDirectory
    from kariyer import LiveMatch,new
    from kayit import load_game,save_game
    from veritabani import TEAMS
    from arayuz import UI

    root=tk.Tk()
    try:
        root.withdraw()
        ui=UI(root)
        state=new('GALATASARAY',seed=821,match_model=4)
        ui.begin(state)
        ui.market()
        ui.staff_page('all')
        ui.squad()
        ui.tactics()
        ui.set_piece_page().destroy()
        match=LiveMatch(state)
        match.capture=True
        match.instruction('press',1)
        match.finish()
        assert match.frames and match.commit()
        with TemporaryDirectory() as folder:
            path=Path(folder)/'probe.json'
            save_game(state,path)
            restored=load_game(path)
        result={'version':root.title(),'frozen':bool(getattr(sys,'frozen',False)),
                'clubs':len(TEAMS),'economy_model':restored['economy_model'],
                'search':True,'match_model':restored['match_model'],'frames':len(match.frames),'flow':match.pitch.summary(),
                'week':restored['week'],'played':len(restored['results'][0])}
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
