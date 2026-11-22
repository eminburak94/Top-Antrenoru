"""Club-scoped set-piece and role controls."""
import tkinter as tk
from tkinter import ttk

from futbol_kurallari import CORNERS,DEFENCE,FREE,ROLES
from veritabani import roster

ROLE_NAMES=dict(zip(ROLES,(
    ('Oyun kurucu','Playmaker'),('Bitirici forvet','Finisher'),('Hedef santrfor','Target forward'),
    ('Defansif orta saha','Holding midfielder'),('Hücumcu bek','Attacking fullback'),
    ('Kanat oyuncusu','Winger'),('Stoper','Centre-back'),('Top kazanan orta saha','Ball-winning midfielder'))))


class SetPieceViews:
    def set_piece_page(self):
        s=self.s
        if not s['employed'] or s.get('match_model') not in (3,4):return
        team=s['club']
        tr=self.tr
        w=tk.Toplevel(self.r)
        w.title(tr('Duran Toplar','Set pieces'))
        w.geometry('570x500')
        w.transient(self.r)
        panel=ttk.Frame(w,padding=14)
        panel.pack(fill='both',expand=True)
        panel.columnconfigure(1,weight=1)
        people={p['id']:p['name']+' · '+p['id'] for p in roster(team,s['year'],s) if p['pos']!='GK'}
        p0=tr('Otomatik','Automatic')
        players={'':p0,**people}
        prefs=s.get('set_pieces',{}).get(team,{})
        assignments=s.get('player_roles',{}).get(team,{})
        pending=assignments.copy()
        controls={}

        def choice(row,key,label,options):
            ttk.Label(panel,text=label).grid(row=row,column=0,sticky='w',pady=3,padx=(0,12))
            box=ttk.Combobox(panel,values=list(options.values()),state='readonly',width=32)
            box.grid(row=row,column=1,sticky='ew',pady=3)
            defaults={'corner':'central','defence':'mixed','free_approach':'auto'}
            current=prefs.get(key,defaults.get(key,next(iter(options))))
            box.set(options.get(current,next(iter(options.values()))))
            controls[key]=(box,{v:k for k,v in options.items()})

        for row,(key,a,b) in enumerate((('left_corner','Sol korner kullanıcısı','Left corner taker'),
          ('right_corner','Sağ korner kullanıcısı','Right corner taker'),('free','Serbest vuruş','Free kick taker'),
          ('penalty','Penaltıcı','Penalty taker'),('target','Korner hedefi','Corner target'))):
            choice(row,key,tr(a,b),players)
        choice(5,'corner',tr('Korner yaklaşımı','Corner delivery'),dict(zip(CORNERS,
               [tr('Ön direk','Near post'),tr('Arka direk','Far post'),tr('Penaltı noktası','Penalty spot'),tr('Kısa','Short')])))
        choice(6,'defence',tr('Savunma','Marking'),dict(zip(DEFENCE,
               [tr('Alan','Zonal'),tr('Adam','Man'),tr('Karma','Mixed')])))
        choice(7,'free_approach',tr('Serbest vuruş tercihi','Free kick plan'),dict(zip(FREE,
               [p0,tr('Şut','Shot'),tr('Orta','Cross'),tr('Kısa','Short')])))
        ttk.Label(panel,text=tr('Oyuncu rolü','Player role')).grid(row=8,column=0,sticky='w',pady=5)
        who=ttk.Combobox(panel,values=list(people.values()),state='readonly')
        who.grid(row=8,column=1,sticky='ew')
        codes=['',*ROLES]
        role=ttk.Combobox(panel,values=[p0,*[tr(*ROLE_NAMES[key]) for key in ROLES]],state='readonly')
        role.grid(row=9,column=1,sticky='ew')
        def pick(_=None):
            uid=list(people)[who.current()]
            role.current(codes.index(pending.get(uid,'')))
        def select(_):
            if who.current()<0:return
            uid=list(people)[who.current()]
            value=codes[role.current()]
            if value:pending[uid]=value
            else:pending.pop(uid,None)
        who.bind('<<ComboboxSelected>>',pick)
        role.bind('<<ComboboxSelected>>',select)
        if people:who.current(0);pick()
        def save():
            s.setdefault('set_pieces',{})[team]={key:values[box.get()] for key,(box,values) in controls.items()}
            s.setdefault('player_roles',{})[team]=pending
            self.autosave()
            w.destroy()
        ttk.Button(panel,text=tr('Uygula','Apply'),style='Accent.TButton',command=save).grid(row=10,column=1,sticky='e',pady=10)
        return w
