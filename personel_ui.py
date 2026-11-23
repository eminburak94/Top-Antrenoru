"""Staff views for the main desktop UI."""
import tkinter as tk
from tkinter import ttk, messagebox

import personel
from oyuncu import age_at
from para import text as money
from veritabani import TEAMS, player
from yerellestirme import position_label


class StaffViews:
    def delegation_page(self):
        self.clear()
        s=self.s
        team=s['club']
        msg=self.management_text
        ttk.Label(self.body,text=msg('staff_delegation')).pack(anchor='w')
        self.button(self.body,*self.staff_labels('staff_title'),self.staff_page).pack(anchor='w')
        grid=ttk.Frame(self.body)
        grid.pack(anchor='w')
        for index,(task,(role,mode)) in enumerate(personel.TASKS.items()):
            choices=personel.active(s,team,role)
            ids=[None,*(pid for pid,_ in choices)]
            current=s['staff_system']['delegation'].get(team,{}).get(task)
            ttk.Label(grid,text=f'{msg(task)} · {msg('staff_mode_'+mode)}').grid(row=index,column=0,sticky='w')
            box=ttk.Combobox(grid,values=[msg('staff_off'),*(row['name'] for _,row in choices)],
                             state='readonly',width=28)
            box.grid(row=index,column=1,padx=8,pady=3)
            box.current(ids.index(current))
            def update(_event,key=task,keys=ids,control=box):
                if personel.delegate(s,team,key,keys[control.current()]):
                    if key=='team_training' and keys[control.current()] is not None:
                        # Explicitly choosing automation grants control until a manual plan is set.
                        s.pop('training',None)
                    self.autosave()
                    self.delegation_page()
            box.bind('<<ComboboxSelected>>',update)
        suggestion=personel.recommendation(s)
        plan=suggestion['training']
        text=msg('staff_advice',level=suggestion['level'],shape=s['formation'],
                 issues=len(suggestion['mismatches']),
                 depth=', '.join(position_label(r,self.lang) for r in suggestion['shortages']) or '—',
                 training=msg('staff_'+plan))
        ttk.Label(self.body,text=text,wraplength=860).pack(anchor='w',pady=4)
        names=[player(s,pid)['name'] for pid in suggestion['young']]
        ttk.Label(self.body,text=msg('staff_youth',names=', '.join(names) or '—'),
                  wraplength=860).pack(anchor='w')
        self.tree([msg('position'),msg('player')],
                  [(position_label(role,self.lang),player(s,pid)['name']) for role,pid in suggestion['slots']])

    def staff_labels(self,key):
        label=self.management_text(key)
        return label,label

    def scout_page(self):
        self.clear()
        s=self.s
        msg=self.management_text
        st=s['staff_system']
        ttk.Label(self.body,text=msg('staff_scouting')).pack(anchor='w')
        controls=ttk.Frame(self.body)
        controls.pack(anchor='w',pady=4)
        self.button(controls,*self.staff_labels('staff_title'),self.staff_page).pack(side='left')
        names=tk.StringVar()
        ttk.Label(controls,text=msg('staff_search')).pack(side='left',padx=5)
        ttk.Entry(controls,textvariable=names,width=16).pack(side='left')
        positions=sorted({p['pos'] for p in personel.candidates(s)})
        options=ttk.Combobox(controls,values=[msg('staff_all'),*(position_label(c,self.lang) for c in positions)],
                             state='readonly',width=16)
        options.current(0)
        options.pack(side='left',padx=3)
        clubs=[None,'free',*TEAMS]
        club=ttk.Combobox(controls,values=[msg('staff_all'),msg('free_only'),*TEAMS],state='readonly',width=20)
        club.current(0)
        club.pack(side='left',padx=3)
        ttk.Label(controls,text=msg('staff_max_age')).pack(side='left')
        age=tk.StringVar()
        ttk.Entry(controls,textvariable=age,width=5).pack(side='left')
        actions=ttk.Frame(self.body)
        actions.pack(anchor='w')
        tabs=ttk.Notebook(self.body)
        tabs.pack(fill='both',expand=True)
        search=ttk.Frame(tabs)
        results=ttk.Frame(tabs)
        tabs.add(search,text=msg('staff_search'))
        tabs.add(results,text=msg('scout_reports'))
        def grid(parent,keys):
            table=ttk.Treeview(parent,columns=keys,show='headings')
            for key in keys:
                table.heading(key,text=msg(key))
                table.column(key,width=116 if key!='player' else 180)
            scroll=ttk.Scrollbar(parent,command=table.yview)
            table.configure(yscrollcommand=scroll.set)
            scroll.pack(side='right',fill='y')
            table.pack(fill='both',expand=True)
            return table
        table=grid(search,('player','position','age'))
        asked=grid(results,('player','staff_status','scout_rating','scout_potential','scout_confidence','scout_date'))
        def update(*_args):
            table.delete(*table.get_children())
            max_age=int(age.get()) if age.get().isdecimal() and len(age.get())<4 else None
            role=positions[options.current()-1] if options.current()>0 else None
            rows=[p for p in personel.candidates(s,role,max_age,clubs[club.current()])
                  if names.get().casefold() in p['name'].casefold()]
            for p in sorted(rows,key=lambda p:(p['name'],p['id']))[:120]:
                table.insert('','end',iid=p['id'],values=(p['name'],position_label(p['pos'],self.lang),
                                                        age_at(p,s['year'],s['week'])))
        names.trace_add('write',update)
        age.trace_add('write',update)
        options.bind('<<ComboboxSelected>>',update)
        club.bind('<<ComboboxSelected>>',update)
        update()
        for pending in st['jobs']:
            if pending['club']==s['club']:
                p=player(s,pending['player'])
                asked.insert('','end',values=(p['name'],msg('scout_pending'),'—','—','—',
                      msg('scout_weeks',count=max(0,pending['due']-personel.week_key(s)))))
        for report in reversed(st['reports']):
            if report['club']!=s['club']:continue
            p=player(s,report['player'])
            a,b=(f'{lo}–{hi}' for lo,hi in report['bands'])
            asked.insert('','end',values=(p['name'],msg('scout_complete'),a,b,
                         f"{report['confidence']}/20",f"{report['year']} / {report['week']}"))
        def start():
            pid=next(iter(table.selection()),None)
            if pid and self.request_scout(pid):
                self.scout_page()
            else:
                messagebox.showinfo(msg('staff_scouting'),
                                    self.scouting_status(pid)[1] if pid else msg('scout_unavailable'),parent=self.r)
        self.button(actions,*self.staff_labels('scout_start'),start).pack(side='left')
        ttk.Label(actions,text=msg('scout_limit')).pack(side='left',padx=6)
