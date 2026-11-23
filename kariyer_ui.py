"""Manager profile and employment market screens."""
from tkinter import ttk, messagebox

import is_piyasasi as jobs
from menajer import resign


class CareerViews:
    def employment_page(self):
        self.clear()
        s=self.s
        m=s['manager_state']
        msg=self.management_text
        ttk.Label(self.body,text=msg('manager_summary',name=s['manager'],rep=s['manager_rep'],
                   club=m['active_team'] or msg('unemployed_flag'),confidence=s['confidence']
                   if s['employed'] else '—',reason=msg('job_'+m['decision']))).pack(anchor='w')
        controls=ttk.Frame(self.body)
        controls.pack(anchor='w',pady=5)
        def button(key,callback):
            text=msg(key)
            self.button(controls,text,text,callback).pack(side='left',padx=3)
        def history():
            self.clear()
            title=msg('career_record')
            self.button(self.body,msg('job_market_title'),msg('job_market_title'),self.employment_page).pack(anchor='w')
            def when(day):
                if day is None:return '—'
                year,week=divmod(day-1,34)
                return f'{year}/{week+1}'
            honours=', '.join(f"{row['year']} · {row['team']}" for row in m['honours']) or '—'
            ttk.Label(self.body,text=msg('career_honours',value=honours),wraplength=840).pack(anchor='w')
            self.tree([title,msg('job_date'),msg('expiry'),msg('status'),'W/D/L','Pts'],
                       [(r['team'],when(r['start']),when(r['end']),
                         msg('job_'+r['reason']) if r['reason'] else '—',
                         '/'.join(str(r['stats'][k]) for k in ('w','d','l')),r['stats']['p'])
                        for r in m['spells']],wide=True)
        button('career_record',history)
        keys=list(m['vacancies'])
        columns=('club_label','job_date','job_reason','job_required','job_goal','status','expiry')
        rows=[]
        for team in keys:
            v=m['vacancies'][team]
            a=jobs.application(s,team)
            year,week=divmod(v['opened']-1,34)
            expires=(a.get('expires') if a else None) or v['closes']
            end_y,end_w=divmod(expires-1,34)
            rows.append((team,f'{year}/{week+1}',msg('job_'+v['reason']),v['required'],v['target'],
                         msg('job_'+a['status']) if a else msg('job_opening'),f'{end_y}/{end_w+1}'))
        ttk.Label(self.body,text=msg('job_market_title')).pack(anchor='w')
        if s.get('match_model',0)==4:
            ttk.Label(self.body,text=msg('job_score',score=jobs.application_score(s))).pack(anchor='w')
        table=self.tree([msg(key) for key in columns],rows,wide=True)
        def action(mode):
            if not table.selection():return
            team=keys[int(table.selection()[0])]
            if mode in ('accept','decline') and not messagebox.askyesno(msg('job_market_title'),
                      msg('job_confirm',team=team),parent=self.r):return
            ok=jobs.apply(s,team) if mode=='apply' else jobs.offer(s,team,mode=='accept')
            if ok:
                self.header()
                self.autosave()
                self.employment_page()
            else:messagebox.showinfo(msg('job_market_title'),msg('job_unavailable'),parent=self.r)
        for mode in ('apply','accept','decline'):
            button('job_'+mode,lambda mode=mode:action(mode))
        def quit_job():
            if messagebox.askyesno(msg('job_market_title'),msg('job_quit'),parent=self.r) and resign(s):
                self.header()
                self.autosave()
                self.employment_page()
        if s['employed']:button('job_resigned',quit_job)
        recent=m['applications'][-5:]
        if recent:
            ttk.Label(self.body,text=' · '.join(f"{r['team']}: {msg('job_'+r['status'])}"+
                      (f" ({msg('job_'+r['reason'])})" if r['reason'] else '') for r in recent),
                      wraplength=870).pack(before=table.master,anchor='w')
