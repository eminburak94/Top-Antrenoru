"""Club-scoped set-piece and role controls."""
import tkinter as tk
from tkinter import ttk

from futbol_kurallari import CORNERS,DEFENCE,FREE,ROLES
from mac import select_slots
from taktik import EXTRA, OPTIONS, ROLES as PLAYER_ROLES, eligible_role, roles_for
from veritabani import player, roster
from yerellestirme import position_label

ROLE_NAMES=dict(zip(ROLES,(
    ('Oyun kurucu','Playmaker'),('Bitirici forvet','Finisher'),('Hedef santrfor','Target forward'),
    ('Defansif orta saha','Holding midfielder'),('Hücumcu bek','Attacking fullback'),
    ('Kanat oyuncusu','Winger'),('Stoper','Centre-back'),('Top kazanan orta saha','Ball-winning midfielder'))))


class SetPieceViews:
    def tactical_plan_page(self,match=None,parent=None,on_apply=None):
        s=self.s
        if not s.get('tactics_model') or not s['employed']:
            return
        team=s['club']
        tr=self.tr
        active=match is not None
        slots=match.slots[match.human] if active else select_slots(s,team)
        orders=(match.team_orders[match.human] if active else s.get('tactical_plans',{}).get(team,{}))
        w=tk.Toplevel(parent or self.r)
        w.title(tr('Taktik planı','Tactical plan'))
        w.transient(parent or self.r)
        panel=ttk.Frame(w,padding=14)
        panel.pack(fill='both',expand=True)
        panel.columnconfigure(1,weight=1)
        controls={}
        for row,key in enumerate(EXTRA if active else OPTIONS):
            a,b,labels_tr,labels_en=OPTIONS[key]
            ttk.Label(panel,text=tr(a,b)).grid(row=row,column=0,sticky='w',padx=(0,12),pady=2)
            box=ttk.Combobox(panel,state='readonly',values=labels_tr if self.lang=='TR' else labels_en,width=28)
            box.grid(row=row,column=1,sticky='ew',pady=2)
            box.current(orders.get(key,0)+1)
            controls[key]=box
        row=len(controls)
        choices=[(position,pid) for position,pid in slots if roles_for(position)]
        names=[f"{position_label(position,self.lang)} · {player(s,pid)['name']}" for position,pid in choices]
        ttk.Separator(panel).grid(row=row,columnspan=2,sticky='ew',pady=8)
        ttk.Label(panel,text=tr('Sahadaki oyuncu','On-field player')).grid(row=row+1,column=0,sticky='w')
        who=ttk.Combobox(panel,values=names,state='readonly',width=35)
        who.grid(row=row+1,column=1,sticky='ew',pady=3)
        ttk.Label(panel,text=tr('Oyuncu rolü','Player role')).grid(row=row+2,column=0,sticky='w')
        role=ttk.Combobox(panel,state='readonly',width=28)
        role.grid(row=row+2,column=1,sticky='ew',pady=3)
        explanation=ttk.Label(panel,wraplength=455)
        explanation.grid(row=row+3,columnspan=2,sticky='w',pady=6)
        assigned=s.get('player_roles',{}).get(team,{})
        pending={}
        roles=[]

        def describe(code):
            if code:
                explanation.config(text=tr(*PLAYER_ROLES[code][2:4]))
            else:
                explanation.config(text=tr('Rolü dizilişteki mevki belirler.',
                                           'The role follows the position in the formation.'))

        def pick(_=None):
            if who.current()<0:return
            position,pid=choices[who.current()]
            roles[:]=[code for code in roles_for(position) if eligible_role(player(s,pid),position,code)]
            current=(match.pitch.role(match.human,pid,position) if active else assigned.get(pid,''))
            if active:
                if current and current not in roles:roles.insert(0,current)
            else:
                roles.insert(0,'')
            selected=pending.get(pid,current)
            role.configure(values=[tr(*PLAYER_ROLES[code][:2]) if code else tr('Otomatik','Automatic') for code in roles])
            if roles:
                role.current(roles.index(selected) if selected in roles else 0)
                describe(roles[role.current()])

        def choose(_=None):
            if who.current()>=0 and role.current()>=0:
                code=roles[role.current()]
                pending[choices[who.current()][1]]=code
                describe(code)

        who.bind('<<ComboboxSelected>>',pick)
        role.bind('<<ComboboxSelected>>',choose)
        if names:who.current(0);pick()

        def close():
            w.destroy()
            if active and parent.winfo_exists():parent.grab_set()

        def apply():
            selected={key:box.current()-1 for key,box in controls.items()}
            if active:
                changed=[match.instruction(key,value) for key,value in selected.items()]
                changed.extend(match.assign_role(pid,code) for pid,code in pending.items())
                if any(changed) and on_apply:on_apply()
            else:
                s.setdefault('tactical_plans',{})[team]=selected
                updated=assigned.copy()
                for pid,code in pending.items():
                    if code:updated[pid]=code
                    else:updated.pop(pid,None)
                s.setdefault('player_roles',{})[team]=updated
                self.autosave()
            close()

        ttk.Button(panel,text=tr('Uygula','Apply'),command=apply).grid(row=row+4,column=1,sticky='e')
        if active:
            w.grab_set()
            w.protocol('WM_DELETE_WINDOW',close)
        return w

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
            current=pending.get(uid,'')
            role.current(codes.index(current) if current in codes else 0)
        def select(_):
            if who.current()<0:return
            uid=list(people)[who.current()]
            value=codes[role.current()]
            if value:pending[uid]=value
            else:pending.pop(uid,None)
        who.bind('<<ComboboxSelected>>',pick)
        role.bind('<<ComboboxSelected>>',select)
        if people:who.current(0);pick()
        if s.get('tactics_model'):
            for widget in panel.grid_slaves(row=8)+panel.grid_slaves(row=9):widget.grid_remove()
        def save():
            s.setdefault('set_pieces',{})[team]={key:values[box.get()] for key,(box,values) in controls.items()}
            if not s.get('tactics_model'):
                s.setdefault('player_roles',{})[team]=pending
            self.autosave()
            w.destroy()
        ttk.Button(panel,text=tr('Uygula','Apply'),style='Accent.TButton',command=save).grid(row=10,column=1,sticky='e',pady=10)
        return w
