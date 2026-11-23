import json
import tempfile
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from unittest.mock import patch
from arayuz import UI
from gorsel_kontrol_v087 import children,capture
from kariyer import new
from transfer import add_offer, asking_fee
from veritabani import roster,TEAMS

def button(root,label):
    return next(w for w in children(root) if isinstance(w,ttk.Button) and w.cget('text')==label)

def dialog(root):
    return next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))

root=tk.Tk()
steps=[]
try:
    ui=UI(root)
    ui.autosave=lambda:None
    button(root,'TR / EN').invoke()
    assert ui.lang=='EN'
    steps.append('EN')
    button(root,'Start career').invoke()
    assert ui.s['match_model']==4 and ui.s['year']==2000
    ui.switch()
    assert ui.lang=='TR'
    steps.append('TR club squad')
    ui.tactics()
    ui.set_piece_page().destroy()
    steps.append('tactics')
    ui.live()
    popup=dialog(root)
    button(popup,'Adım').invoke()
    cb=next(w for w in children(popup) if isinstance(w,ttk.Combobox) and w.cget('values')==('Düşük','Normal','Yüksek'))
    cb.current(2)
    cb.event_generate('<<ComboboxSelected>>')
    button(popup,'Oyuncu değiştir').invoke()
    sub=dialog(popup)
    combo=[w for w in children(sub) if isinstance(w,ttk.Combobox)]
    for w in combo:w.current(0)
    button(sub,'Uygula').invoke()
    assert not sub.winfo_exists()
    with patch('arayuz.messagebox.askyesno',return_value=True):
        button(popup,'Maçı bitir').invoke()
    root.update()
    assert ui.s['week']==2
    match=next(m for m in ui.s['results'][0] if ui.s['club'] in (m['home'],m['away']))
    assert any(row[3]=='sub' for row in match['play'])
    ui.last_report()
    dialog(root).destroy()
    steps.append('match instruction substitution report')
    ui.market()
    ui.staff_page('all')
    for team in TEAMS:
        if team==ui.s['club']:
            continue
        p=roster(team,ui.s['year'],ui.s)[-1]
        result=add_offer(ui.s,p,ui.s['club'],asking_fee(ui.s,p),{'years':2,'wage':2000,'signing':0,'role':'Rotation'})
        if result:
            break
    assert ui.s.get('offers')
    steps.append('player and staff search and transfer offer through domain')
    ui.s['match_mode']='quick'
    with patch.object(ui,'confirm_lineup',return_value=True),patch('arayuz.messagebox.askyesno',return_value=True):
        for _ in range(34):ui.next()
    assert ui.s['year']==2001 and ui.s['week']==1
    steps.append('full season rollover')
    with tempfile.TemporaryDirectory() as path:
        location=str(Path(path)/'isolated.json')
        with patch('arayuz.filedialog.asksaveasfilename',return_value=location):ui.save()
        root.destroy()
        root=tk.Tk()
        ui=UI(root)
        with patch('arayuz.filedialog.askopenfilename',return_value=location):ui.load()
        assert ui.s['year']==2001 and ui.s['week']==1
        steps.append('save close restart load')
    ui.start()
    check=next(w for w in children(root) if isinstance(w,ttk.Checkbutton))
    check.invoke()
    button(root,'Kariyeri başlat').invoke()
    assert not ui.s['employed']
    steps.append('unemployed')
    for size in ('960x600','1280x720','1920x1080'):
        ui.begin(new('GALATASARAY',seed=822,match_model=4))
        ui.autosave=lambda:None
        root.geometry(size+'+0+0')
        root.update()
        nav=[w for w in ui.nav.winfo_children() if isinstance(w,ttk.Button)]
        assert all(w.winfo_ismapped() and w.winfo_rootx()+w.winfo_width()<=root.winfo_rootx()+root.winfo_width() for w in nav)
        capture(root,Path('V087_EKRANLAR')/('boyut_'+size+'.png'))
        steps.append(size)
    print(json.dumps(steps,ensure_ascii=False))
finally:
    root.destroy()
