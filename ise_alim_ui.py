"""Player and staff recruitment views."""
import tkinter as tk
from tkinter import messagebox,ttk

from arama_bilesenleri import Search,number
import personel
from mac import eligible
from mevkiler import LAYOUTS,fit_level,label as detail_position
from oyuncu import GROUPS,age_at
from para import from_display,text as money
from sozlesme import asking_terms
from transfer import asking_fee
from veritabani import TEAMS,all_players,available,roster
from yerellestirme import citizenship_ids,country_label,position_label


def report_index(s):
    return {row['player']:row for row in s.get('staff_system',{}).get('reports',[])
            if row['club']==s['club']}


def shortlists(s):
    return s.setdefault('ui_preferences',{})


def formation_coverage(s):
    slots=LAYOUTS[s['formation']] if s.get('position_model') else ()
    squad=roster(s['club'],s['year'],s)
    return {pos:(slots.count(pos),sum(fit_level(p,pos)>=2 and eligible(s,p) for p in squad))
            for pos in dict.fromkeys(slots)}


class RecruitmentViews:
    def scouting_age(self,report):
        from personel import week_key
        weeks=max(0,week_key(self.s)-(report['year']*34+report['week']+1))
        return self.tr('Rapor {year}/{week} · {age} hafta önce · Güven {confidence}/20',
                       'Report {year}/{week} · {age} weeks ago · Confidence {confidence}/20').format(
                           **report,age=weeks)

    def scouting_status(self,pid):
        status,detail=personel.scout_assignment(self.s,pid)
        labels=dict(
            pending=self.tr('Gözlem sürüyor · kalan hafta {weeks}','Scouting underway · {weeks} weeks remaining'),
            no_scout=self.tr('Kulüpte gözlemci yok.','The club has no scout.'),
            busy=self.tr('Tüm gözlemciler görevde.','All scouts are on assignment.'),
            ready=self.tr('Gözlemci uygun · rapor iki hafta içinde.','Scout available · report in two weeks.'),
            unavailable=self.tr('Bu oyuncu için gözlem başlatılamıyor.','Scouting cannot start for this player.'))
        return status,labels[status].format(weeks=detail)

    def request_scout(self,pid):
        if personel.start_scout(self.s,pid):
            self.autosave()
            return True
        return False

    def search_buttons(self,search,items,key,lookup,open_profile):
        tr=self.tr
        def toggle(add):
            uid=search.selection()
            if not uid:return
            saved=items.setdefault(key,[])
            if add and uid not in saved and len(saved)<250:saved.append(uid)
            if not add and uid in saved:saved.remove(uid)
            search.refresh()
        def profile():
            uid=search.selection()
            if uid:open_profile(lookup(uid))
        search.button(tr('Kısa listeye ekle','Shortlist'),lambda:toggle(True))
        search.button(tr('Listeden çıkar','Remove'),lambda:toggle(False))
        search.button(self.management_text('open_profile'),profile)
        search.table.bind('<Double-1>',lambda _:profile())
        search.table.bind('<Return>',lambda _:profile())

    def market(self):
        self.clear()
        s=self.s
        tr=self.tr
        prefs=shortlists(s)
        ttk.Label(self.body,text=tr('Futbolcu arama','Player search'),style='Title.TLabel').pack(anchor='w')
        links=ttk.Frame(self.body);links.pack(anchor='w',pady=4)
        for a,b,command in (('Teklifler','Offers',self.offers_page),('Finans','Finance',self.finance_page),
                             ('Gözlem raporları','Scouting reports',self.scout_page)):
            if command==self.scout_page and not s.get('staff_system'):continue
            self.button(links,a,b,command).pack(side='left',padx=3)
        clubs=s['owners']
        players={p['id']:p for p in all_players(s)
                 if clubs.get(p['id'])!=s['club'] and (p['id'] in clubs or available(s,p))}
        reports=report_index(s)
        any_value=[('*','')]
        choices=lambda pairs:any_value+list(pairs)
        codes=sorted({code for p in players.values() for code in citizenship_ids(p)})
        roles=sorted({p['pos'] for p in players.values()}|{code for p in players.values() for code in p.get('alternate_positions',())})
        modes=choices([(tr('Serbest','Free'),'free'),(tr('Sözleşmeli','Contracted'),'owned')])
        coverage=formation_coverage(s)
        fields=[
          ('name',tr('Oyuncu adı','Player name'),None),('club',tr('Kulüp','Club'),choices((t,t) for t in TEAMS)),
          ('position',tr('Mevki','Position'),choices((position_label(c,self.lang),c) for c in roles)),
          ('nation',tr('Uyruk','Nationality'),choices((country_label(c,self.lang),c) for c in codes)),
          ('status',tr('Sözleşme','Contract'),modes),('scope',tr('Liste','List'),choices([(tr('Kısa liste','Shortlist'),'short')])),
          ('min_age',tr('Alt yaş','Min age'),None),('max_age',tr('Üst yaş','Max age'),None),
          ('fee',tr('Azami bedel','Max fee'),None),('wage',tr('Azami maaş','Max wage'),None),
          ('ca',tr('Yetenek alt sınır*','Min ability*'),None),('pa',tr('Potansiyel alt sınır*','Min potential*'),None),
          ('technical',tr('Teknik ≥*','Technical ≥*'),None),('mental',tr('Zihinsel ≥*','Mental ≥*'),None),
          ('physical',tr('Fiziksel ≥*','Physical ≥*'),None),
        ]
        if coverage:
            fields.insert(4,('formation_slot',tr('Diziliş mevkii','Formation position'),
                              choices((detail_position(pos,self.lang),pos) for pos in coverage)))
        columns=[tr('Futbolcu','Player'),tr('Kulüp','Club'),tr('Mevki','Position'),tr('Yaş','Age'),
                 tr('Bedel','Fee'),tr('Maaş','Wage'),tr('Yetenek*','Ability*'),tr('Potansiyel*','Potential*')]
        ttk.Label(self.body,text=tr('* Gözlem raporu aralığı. Rapor yoksa aralık bilinmiyor.',
                                    '* Scouting report range. Unreported ability is unknown.')).pack(anchor='w')
        cache={}
        def query(f):
            try:
                lo,hi,ca,pa=(number(f,k) for k in ('min_age','max_age','ca','pa'))
                groups={k:number(f,k) for k in ('technical','mental','physical')}
                fee,wage=(number(f,k,lambda v:from_display(s,v)) for k in ('fee','wage'))
                if lo is not None and hi is not None and lo>hi:raise ValueError()
            except (ValueError,OverflowError):
                return [],tr('Geçerli sayı veya aralık girin.','Enter a valid number or range.')
            rows=[]
            for uid,p in players.items():
                owner=clubs.get(uid)
                if f['status']=='free' and owner:continue
                if f['status']=='owned' and not owner or f['club'] and f['club']!=owner:continue
                if f['scope']=='short' and uid not in prefs.get('players',[]):continue
                if f['name'].casefold() not in p['name'].casefold():continue
                positions={p['pos'],*p.get('alternate_positions',())}
                if f['position'] and f['position'] not in positions and not (GROUPS.get(f['position'],set()) & positions):continue
                if f.get('formation_slot') and fit_level(p,f['formation_slot'])<2:continue
                if f['nation'] and f['nation'] not in citizenship_ids(p):continue
                if uid not in cache:
                    cache[uid]=(age_at(p,s['year'],s['week']),asking_fee(s,p),asking_terms(s,p,s['club'],'Starter')['wage'])
                age,price,salary=cache[uid]
                if (lo is not None or hi is not None) and (not isinstance(age,int) or lo is not None and age<lo or hi is not None and age>hi):continue
                if fee is not None and price>fee or wage is not None and salary>wage:continue
                categories=reports.get(uid,{}).get('groups',{})
                if any(bound is not None and (k not in categories or categories[k][0]<bound)
                       for k,bound in groups.items()):continue
                bands=reports.get(uid,{}).get('bands',[(None,None),(None,None)])
                if any(bound is not None and (band[0] is None or band[0]<bound) for bound,band in zip((ca,pa),bands)):continue
                pos=position_label(p['pos'],self.lang)
                team=owner or tr('Serbest','Free')
                values=(p['name'],team,pos,age,money(s,price),money(s,salary),
                        *(f'{a}–{b}' if a is not None else '—' for a,b in bands))
                rows.append((uid,values,(p['name'].casefold(),team,pos,age if isinstance(age,int) else None,
                                         price,salary,bands[0][0],bands[1][0])))
            return rows,None
        search=Search(self,self.body,fields,columns,query,prefs.setdefault('player_filters',{}),
                      basic={'name','min_age','max_age','position','status'})
        summary=ttk.Label(self.body,text=tr('Özet için futbolcu seçin.','Select a player for a summary.'),wraplength=840)
        summary.pack(side='bottom',anchor='w',pady=4)
        def selection_summary(_=None):
            uid=search.selection()
            slot_control=search.variables.get('formation_slot')
            slot=slot_control[1].get(slot_control[0].get()) if slot_control else None
            line=''
            if slot in coverage:
                required,ready=coverage[slot]
                line=tr('{pos} · Dizilişte {required}, kadroda hazır ve uyumlu {ready}',
                        '{pos} · {required} in formation, {ready} eligible fits in squad').format(
                            pos=detail_position(slot,self.lang),required=required,ready=ready)
            if not uid:
                summary.configure(text=line or tr('Özet için futbolcu seçin.','Select a player for a summary.'))
                return
            p=players[uid]
            age,fee,_=cache[uid]
            scouted=self.scouting_age(reports[uid]) if uid in reports else self.scouting_status(uid)[1]
            summary.configure(text=f"{p['name']} · {clubs.get(uid) or tr('Serbest','Free')} · "
                f"{position_label(p['pos'],self.lang)} · {age} · {money(s,fee)} · {scouted}"
                +('\n'+line if line else ''))
        search.table.bind('<<TreeviewSelect>>',selection_summary)
        if coverage:
            search.variables['formation_slot'][0].trace_add('write',lambda *_:selection_summary())
        selection_summary()
        self.search_buttons(search,prefs,'players',players.get,self.profile)
        search.button(tr('Teklif ver','Make offer'),lambda:self.negotiate(players[search.selection()]) if search.selection() else None)
        if s.get('transfer_model'):
            search.button(tr('Kiralama teklifi','Loan offer'),
                          lambda:self.offer_loan(players[search.selection()]) if search.selection() else None)
        def scout():
            uid=search.selection()
            if uid:
                self.request_scout(uid)
                messagebox.showinfo(tr('Gözlem','Scouting'),self.scouting_status(uid)[1],parent=self.r)
                selection_summary()
        search.button(tr('Gözlemle','Scout'),scout)

    def staff_page(self,mode='mine'):
        self.clear()
        s=self.s;tr=self.tr;msg=self.management_text
        st=s.get('staff_system')
        ttk.Label(self.body,text=tr('Teknik ekip merkezi','Staff centre'),style='Title.TLabel').pack(anchor='w')
        if not st:
            ttk.Label(self.body,text=msg('staff_legacy')).pack(anchor='w')
            return
        prefs=shortlists(s)
        team=s['club']
        pool=st['pool']
        ttk.Label(self.body,text=msg('staff_budget_line',count=len(personel.active(s,team)),
                  capacity=personel.capacity(s,team),pay=money(s,personel.payroll(s,team)),
                  limit=money(s,personel.salary_limit(s,team)))).pack(anchor='w')
        links=ttk.Frame(self.body);links.pack(anchor='w',pady=4)
        for key,a,b in (('mine','Kulübüm','My staff'),('all','Personel arama','Find staff'),('short','Kısa liste','Shortlist')):
            ttk.Button(links,text=tr(a,b),command=lambda key=key:self.staff_page(key),
                       style='Accent.TButton' if key==mode else 'TButton').pack(side='left',padx=3)
        self.button(links,*self.staff_labels('staff_delegation'),self.delegation_page).pack(side='left')
        self.button(links,*self.staff_labels('staff_scouting'),self.scout_page).pack(side='left')
        any_value=[('*','')]
        skill_keys=('coaching','motivation','discipline','goalkeeping','fitness','judging')
        fields=[] if mode=='mine' else [
            ('name',tr('Personel adı','Staff name'),None),
            ('role',tr('Görev','Role'),any_value+[(msg('role_'+k),k) for k in personel.ROLES]),
            ('status',tr('Sözleşme','Contract'),any_value+[(tr('Kulüpsüz','Free'),'free'),(tr('Sözleşmeli','Employed'),'owned')]),
            ('special',tr('Uzmanlık','Specialty'),any_value+[(msg('skill_'+k),k) for k in personel.SKILLS]),
            ('min_wage',tr('Alt maaş','Min wage'),None),('max_wage',tr('Üst maaş','Max wage'),None),
            ('years',tr('En çok kalan yıl','Max years left'),None),
            *[(k,msg('skill_'+k)+' ≥',None) for k in skill_keys]]
        columns=[tr('Ad soyad','Full name'),tr('Görev','Role'),tr('Kulüp','Club'),tr('Uzmanlık','Specialty'),tr('Maaş','Wage'),tr('Bitiş','Expiry')]
        def query(f):
            try:
                bounds=[number(f,k) for k in skill_keys]
                lo,hi=[number(f,k,lambda v:from_display(s,v)) for k in ('min_wage','max_wage')]
                years=number(f,'years')
                if lo is not None and hi is not None and lo>hi:raise ValueError()
            except (ValueError,OverflowError):return [],tr('Geçerli sayı girin.','Enter a valid number.')
            rows=[]
            for uid,p in pool.items():
                if mode=='mine' and p['club']!=team or mode=='short' and uid not in prefs.get('staff',[]):continue
                if f.get('name','').casefold() not in p['name'].casefold() or f.get('role') and p['role']!=f['role']:continue
                if f.get('status')=='free' and p['club'] or f.get('status')=='owned' and not p['club']:continue
                if f.get('special') and f['special'] not in personel.SPECIAL[p['role']]:continue
                if lo is not None and p['wage']<lo or hi is not None and p['wage']>hi:continue
                if years is not None and (p['end'] or s['year'])-s['year']>years:continue
                if any(val is not None and p['skills'][k]<val for k,val in zip(skill_keys,bounds)):continue
                role=msg('role_'+p['role'])
                owner=p['club'] or tr('Kulüpsüz','Free')
                skill=' / '.join(msg('skill_'+k) for k in personel.SPECIAL[p['role']])
                rows.append((uid,(p['name'],role,owner,skill,money(s,p['wage']),p['end'] or '—'),
                            (p['name'].casefold(),role,owner,skill,p['wage'],p['end'])))
            return rows,None
        search=Search(self,self.body,fields,columns,query,prefs.setdefault('staff_filters',{}),
                      basic={'name','role','status','min_wage','max_wage'})
        self.search_buttons(search,prefs,'staff',pool.get,lambda p:self.staff_profile(p,search,search.selection()))
        if s['employed'] and mode=='mine':
            search.button(msg('staff_renew'),lambda:self.staff_action(search,'staff_renew'))
            search.button(msg('staff_release'),lambda:self.staff_action(search,'staff_release'))

    def staff_action(self,search,action,years=2,uid=None):
        s=self.s
        uid=uid or search.selection()
        if not uid or not s['employed']:return
        row=s['staff_system']['pool'][uid]
        msg=self.management_text
        if not messagebox.askyesno(msg('staff_title'),msg('staff_confirm',name=row['name']),parent=self.r):return
        if action=='staff_release':
            ok=personel.release(s,s['club'],uid)
            reason='unavailable'
        else:
            ok,reason=personel.contract(s,s['club'],uid,years,renew=action=='staff_renew')
        if ok:
            search.refresh()
            self.autosave()
            return True
        else:
            messagebox.showinfo(msg('staff_title'),msg(reason) if reason.startswith('staff_') else self.reason(reason),parent=self.r)

    def staff_profile(self,p,search,uid):
        w=tk.Toplevel(self.r)
        w.title(p['name'])
        w.geometry('550x480')
        panel=ttk.Frame(w,padding=18);panel.pack(fill='both',expand=True)
        tr=self.tr;msg=self.management_text;s=self.s
        ttk.Label(panel,text=p['name'],style='Title.TLabel',wraplength=490).pack(anchor='w')
        ttk.Label(panel,text=f"{msg('role_'+p['role'])} · {p['club'] or tr('Kulüpsüz','Free')} · {money(s,p['wage'])} · {p['end'] or '—'}").pack(anchor='w',pady=6)
        ttk.Label(panel,text=msg('fictional_staff')).pack(anchor='w')
        caps=f"{len(personel.active(s,s['club']))}/{personel.capacity(s,s['club'])}"
        ttk.Label(panel,text=tr('Kulüp kontenjanı','Club capacity')+' '+caps).pack(anchor='w',pady=5)
        for key,value in p['skills'].items():
            ttk.Label(panel,text=f"{msg('skill_'+key)} · {value}/20").pack(anchor='w')
        if s['employed'] and p['club'] in (None,s['club']):
            eligible=('staff_hire',) if p['club'] is None else ('staff_renew','staff_release')
            years=ttk.Combobox(panel,values=(1,2,3),state='readonly',width=4)
            years.current(1);years.pack(anchor='w')
            for action in eligible:
                self.button(panel,msg(action),msg(action),lambda action=action:w.destroy() if self.staff_action(search,action,int(years.get()),uid) else None).pack(side='left',padx=5)
