import math
import re
from collections import Counter, deque
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path
from kariyer import new, prepare, advance, rollover, career, LiveMatch, lineup
from veritabani import P, TEAMS, available, roster, player, all_players, verified_results
from finans import commitments,payroll
from para import CURRENCIES,rate as money_rate,text as money_text,edit_value,from_display
from menajer import accept_job, resign
from sozlesme import asking_terms, renew, contract_time, player_objection
from oyuncu import ability, age_at, attributes, state, GROUPS
from transfer import (asking_fee, deal, answer_offer, loan_deal, loan_fee, loan_ready,
                      purchase_offer, reject_all, set_sale_status, selling_ready, value)
from yarisma import window, FORMATIONS, STYLES, TRANSFER_PERIODS, opening_date
from mac import eligible, fits, formation_roles, manual_slots, select_slots, match_positions, suitable
from istatistik import SHOT_EVENTS, combine
from yerellestirme import position_code,  country_label, position_label, citizenship_ids, player_countries
from kayit import save_game, load_game, autosave, backup_path, SaveError
from yonetim import squad_review
from yonetim_metinleri import TEXT
from antrenman import FOCUSES, INTENSITIES, recent_minutes

from mevkiler import LAYOUTS, POSITION_NAMES, FIT_NAMES, coordinates, fit_level, label as detail_position

from personel_ui import StaffViews
from personel import team_training

from kariyer_ui import CareerViews
from kulup_ui import ClubLifeViews
from arama_bilesenleri import resize_columns,table as data_table
from ise_alim_ui import RecruitmentViews, report_index
from ekonomi import projection
from mac_gorunum import Pitch,interpolate
from duran_top_ui import SetPieceViews
from taktik import OPTIONS as TACTICAL_OPTIONS, ROLES as TACTICAL_ROLES
from tema import PALETTE as THEME,FONT,install,wrap_controls
from kayit import user_directory

class UI(SetPieceViews,RecruitmentViews,StaffViews,CareerViews,ClubLifeViews):
 def __init__(self,r):
  self.r=r;self.s=None;self.lang='TR';r.title('Top Antrenörü v0.9.4 Playtest Beta');r.geometry('1200x760');r.minsize(960,600);r.configure(bg=THEME['base'])
  install(r)
  self.head=tk.Label(r,bg=THEME['base'],fg=THEME['accent'],font=(FONT,19,'bold'),pady=11);self.head.pack(fill='x');self.nav=ttk.Frame(r,padding=8);self.nav.pack(fill='x');self.body=ttk.Frame(r,padding=16);self.body.pack(fill='both',expand=True);self.status=tk.Label(r,bg=THEME['base'],fg=THEME['muted'],anchor='w',padx=16,pady=8,text='TOP ANTRENÖRÜ  |  2000–2001  |  v0.9.4 Playtest Beta');self.status.pack(side='bottom',fill='x');self.start()
 def tr(self,a,b):return a if self.lang=='TR' else b
 def management_text(self,key,**values):
  return self.tr(*TEXT[key]).format(**values)
 def clear(self):
  for x in self.body.winfo_children():x.destroy()
 def button(self,parent,a,b,cmd):return ttk.Button(parent,text=self.tr(a,b),command=cmd)
 def start(self):
  self.clear();self.head.config(text='TOP ANTRENÖRÜ  /  2000');v=tk.StringVar(value='GALATASARAY');name=tk.StringVar();unemployed=tk.BooleanVar();outer=ttk.Frame(self.body);outer.pack(expand=True,fill='both');left=tk.Frame(outer,bg=THEME['hero'],padx=32,pady=30);left.pack(side='left',fill='both',expand=True,padx=(0,16));tk.Label(left,text='2000 / 01',font=(FONT,36,'bold'),bg=THEME['hero'],fg=THEME['accent']).pack(anchor='w');tk.Label(left,text=self.tr('Futbolun geçmişine dön.\nKendi tarihini yaz.','Return to football history.\nWrite your own.'),justify='left',font=(FONT,19),bg=THEME['hero'],fg=THEME['text']).pack(anchor='w',pady=20);c=tk.Canvas(left,width=330,height=210,bg=THEME['field'],highlightthickness=0);c.pack(anchor='w',fill='x');c.create_rectangle(12,12,318,198,outline=THEME['line'],width=2);c.create_line(165,12,165,198,fill=THEME['line'],width=2);c.create_oval(130,70,200,140,outline=THEME['line'],width=2);c.create_rectangle(12,55,65,155,outline=THEME['line']);c.create_rectangle(265,55,318,155,outline=THEME['line']);right=ttk.Frame(outer,padding=24);right.pack(side='right',fill='y');ttk.Label(right,text=self.tr('Yeni kariyer','New career'),font=(FONT,21,'bold')).pack(anchor='w',pady=(20,22));ttk.Label(right,text=self.tr('Menajer adı','Manager name')).pack(anchor='w');e=ttk.Entry(right,textvariable=name,width=34);e.pack(fill='x',pady=(5,18));ttk.Label(right,text=self.tr('Kulübünü seç','Choose your club')).pack(anchor='w');ttk.Combobox(right,textvariable=v,values=TEAMS,state='readonly',width=32).pack(fill='x',pady=(5,22));ttk.Checkbutton(right,text=self.management_text('start_unemployed'),variable=unemployed).pack(anchor='w');defstart=lambda:self.begin(dict(new(v.get(),name.get().strip() or self.tr('Menajer','Manager'),unemployed=unemployed.get(),match_model=4,transfer_model=True,living_club=True,tactics_model=True),lang=self.lang));ttk.Button(right,text=self.tr('Kariyeri başlat','Start career'),style='Accent.TButton',command=defstart).pack(fill='x',pady=5);self.button(right,'Kayıt yükle','Load career',self.load).pack(fill='x',pady=5);links=ttk.Frame(right);links.pack(fill='x',pady=5);ttk.Button(links,text='TR / EN',command=lambda:(self.toggle(),self.start())).pack(side='left');self.button(links,'Emeği Geçenler','Credits',self.credits).pack(side='left',padx=(6,0));e.bind('<Return>',lambda _:defstart());e.focus_set()
 def credits(self):
  self.clear()
  title=self.tr('Emeği Geçenler','Credits')
  self.head.configure(text=title)
  card=ttk.Frame(self.body,padding=16,style='Desk.TFrame')
  card.pack(fill='x',pady=6)
  contributors=(
   ('Emin Burak Öncel','Proje Sahibi ve Oyun Tasarımı','Project Owner and Game Design'),
   ('OpenAI Codex','Yapay Zekâ Geliştirme','AI Development'),
   ('Atlas (ChatGPT)','Planlama ve Koordinasyon','Planning and Coordination'),
   ('Claude','Kod İnceleme','Code Review'),
   ('Qwen3 + OpenCode','Yerel Ön Denetim','Local Pre-audit'),
  )
  for name,tr,en in contributors:
   ttk.Label(card,text=name,style='DeskTitle.TLabel').pack(anchor='w')
   ttk.Label(card,text=self.tr(tr,en),style='DeskBody.TLabel').pack(anchor='w',pady=(0,8))
  self.button(self.body,'Ana menüye dön','Back to main menu',self.start).pack(anchor='w',pady=8)
 def toggle(self):self.lang='EN' if self.lang=='TR' else 'TR'
 def begin(self,s):s.setdefault('manager','Menajer');s.setdefault('year',2000);s.setdefault('history',[]);self.s=prepare(s);self.lang=s.get('lang',self.lang);self.menu();self.dashboard()
 def menu(self):
  for item in self.nav.winfo_children():item.destroy()
  tr=self.tr
  self.button(self.nav,'Ana sayfa','Home',self.dashboard)
  club_links=[('Kulüp yönetimi','Club desk',self.club_life_page)] if self.s.get('living_club') else []
  groups=[
   ('Takım','Team',[('Kadro','Squad',self.squad),('Taktik','Tactics',self.tactics),
                   (*TEXT['staff_title'],self.staff_page)]+club_links),
   ('Maç','Match',[('Maç hazırlığı','Match preparation',self.preparation),('Son maç','Last match',self.last_report),
                   ('Maç ayarı','Match mode',self.match_settings)]),
   ('Transfer','Recruitment',[('Futbolcu arama','Player search',self.market),
                              ('Gelen teklifler','Incoming offers',self.offers_page),('Finans','Finance',self.finance_page)]
                             +([('Kiralamalar','Loans',self.loans_page)] if self.s.get('transfer_model') else [])),
   ('Dünya','World',[('Lig','Table',self.table),('Fikstür','Fixtures',self.fixtures),('Arşiv','History',self.archive),
                    ('Oyuncu istatistikleri','Player statistics',self.scorers)]),
   ('Kariyer','Career',[('Menajer geçmişi','Career record',self.career_page),('İş piyasası','Job market',self.jobs_page),
                      ('Kaydet','Save',self.save),('Yükle','Load',self.load),('TR / EN','TR / EN',self.switch)])]
  from tema import MenuButton,wrap_controls
  for a,b,entries in groups:
   MenuButton(self.nav,tr(a,b),[(tr(left,right),callback) for left,right,callback in entries])
  self.button(self.nav,'Gündem','Inbox',self.inbox_page)
  ttk.Button(self.nav,text=tr('Devam','Continue'),style='Accent.TButton',command=self.next)
  wrap_controls(self.nav)
  self.header()
 def dashboard(self):
  if 'manager_state' in self.s and not self.s['employed']:return self.employment_page()
  from yarisma import standings
  self.clear();s=self.s;tr=self.tr;club=s['club']
  players=roster(club,s['year'],s)
  rows=[state(s,p) for p in players]
  injured=sum(bool(row['injury']) for row in rows)
  fit=round(sum(row['condition'] for row in rows)/max(1,len(rows)))
  morale=round(sum(row['morale'] for row in rows)/max(1,len(rows)))
  expiring=sum(row['contract']<=s['year']+1 for row in rows)
  offers=sum(o['status']=='open' and o['seller']==club and o['year']==s['year']
             and 0<=s['week']-o['week']<=2 for o in s['offers'])
  fixture=next((row for row in s['schedule'] if row['week']==s['week'] and club in (row['home'],row['away'])),None)
  match_text=tr('Sezon karşılaşmaları tamamlandı.','Season fixtures complete.')
  if fixture:
   rival=fixture['away'] if club==fixture['home'] else fixture['home']
   venue=tr('Ev sahibi','Home') if club==fixture['home'] else tr('Deplasman','Away')
   from datetime import date,timedelta
   day=(date(s['year'],8,1)+timedelta(weeks=s['week']-1)).isoformat()
   match_text=f"{rival} · {venue} · {day} · {tr('Hafta','Week')} {s['week']}"
  recent=[]
  for week in s['results'][-5:]:
   match=next((r for r in week if club in (r['home'],r['away'])),None)
   if match:
    scored,conceded=(match['x'],match['y']) if match['home']==club else (match['y'],match['x'])
    recent.append((match,scored,conceded))
  form=' · '.join(tr('G','W') if x>y else tr('B','D') if x==y else tr('M','L') for _,x,y in recent) or '—'
  last=tr('Henüz maç oynanmadı.','No match played yet.')
  if recent:
   match,_,_=recent[-1]
   last=f"{match['home']} {match['x']}–{match['y']} {match['away']}"
  finance=s['finance'][club]
  pressure=payroll(s,club)>=finance['wage_budget'] or finance['cash']<0
  gap=max(0,11-len(select_slots(s,club)))
  ttk.Label(self.body,text=tr('Menajer masası','Manager desk'),style='Title.TLabel').pack(anchor='w')
  cards=ttk.Frame(self.body);cards.pack(fill='both',expand=True,pady=(8,0))
  for col in (0,1):cards.columnconfigure(col,weight=1,uniform='desk')
  def panel(i,title,message,links):
   card=ttk.Frame(cards,padding=(12,6),style='Desk.TFrame')
   card.grid(row=i//2,column=i%2,sticky='nsew',padx=4,pady=4)
   ttk.Label(card,text=title,style='DeskTitle.TLabel').pack(anchor='w')
   ttk.Label(card,text=message,style='DeskBody.TLabel',wraplength=385).pack(anchor='w',pady=(3,5))
   bar=ttk.Frame(card,style='Desk.TFrame')
   if len(links)>2:
    from tema import wrap_controls
    bar.pack(fill='x')
    for a,b,callback in links:self.button(bar,a,b,callback)
    wrap_controls(bar)
   else:
    bar.pack(anchor='w')
    for a,b,callback in links:self.button(bar,a,b,callback).pack(side='left',padx=(0,4))
   return bar
  panel(0,tr('Sıradaki maç','Next match'),match_text,[('Maça hazırlan','Prepare match',self.preparation)])
  panel(1,tr('Takım durumu','Squad status'),
        f"#{standings(s).index(club)+1} · {form} · {tr('Kondisyon','Fitness')} %{fit} · {tr('Moral','Morale')} {morale}{chr(10)}"
        f"{tr('Sakat','Injured')} {injured} · {tr('İlk 11 açığı','XI short')} {gap}",
        [('Kadro','Squad',self.squad),('Taktik','Tactics',self.tactics)])
  club_status=''
  if s.get('living_club'):
   from yasayan_kulup import pending_question
   life=s['living_club'];score=life['fans'][club][0]
   club_status=f" · {tr('Taraftar','Supporters')} {score}/100 · {tr('İş riski','Job risk')} {life['board']['risk']}/100"
   if pending_question(s):club_status+=chr(10)+tr('Basın sorusu bekliyor','Press question pending')
  panel(2,tr('Yapılacak işler','To do'),
        f"{tr('Yaklaşan sözleşme','Expiring contracts')} {expiring} · {tr('Gelen teklif','Incoming offers')} {offers}{chr(10)}"
        f"{tr('Yönetim hedefi','Board target')} #{s['board_targets'][club]} · {tr('Güven','Confidence')} %{s['confidence']}"+club_status,
        [('Kadro kontrolü','Squad review',self.review_page),('Teklifler','Offers',self.offers_page)])
  latest=s.get('inbox',[])
  count=len(latest[-1]['items']) if latest and latest[-1]['club']==club else 0
  panel(3,tr('Son gelişmeler','Latest developments'),
        last+chr(10)+(tr('Gündemdeki son öğeler','Latest inbox items')+f' {count}' if count else tr('Yeni gündem kaydı yok.','No new inbox entry.')),
        [('Son maç','Last match',self.last_report),('Gündem','Inbox',self.inbox_page),('Haberler','News',self.news_page)])
  panel(4,tr('Finans','Finance'),
        f"{money_text(s,finance['cash'])} · {tr('Maaş bütçesi','Wage budget')} {money_text(s,finance['wage_budget'])}"
        +(f"{chr(10)}{tr('Bütçe baskısı','Budget pressure')}" if pressure else ''),
        [('Mali döküm','Financial breakdown',self.finance_page)])
  training_bar=panel(5,tr('Antrenman ve ekip','Training and staff'),
        tr('Haftalık plan ve oyuncu gelişim raporları','Weekly plans and player development reports'),
        [('Antrenman','Training',self.training_page),('Haftalık rapor','Weekly report',self.weekly_page)])
  programs={'Normal':tr('Normal','Normal'),'Rest':tr('Dinlenme','Rest'),'Development':tr('Gelişim','Development')}
  choice=ttk.Combobox(training_bar,values=list(programs.values()),width=10,state='readonly')
  choice.current(list(programs).index(team_training(s,club)))
  choice.bind('<<ComboboxSelected>>',lambda _:s.update(training=list(programs)[choice.current()]))
  choice.pack(side='left')
 def news_page(self):
  self.clear()
  self.button(self.body,'Menajer masası','Manager desk',self.dashboard).pack(anchor='w')
  if self.s.get('living_club'):
   self.button(self.body,'Spor servisi','Sports desk',lambda:self.club_life_page(2)).pack(anchor='w')
  loan_types={'Kiralama / Loan':self.tr('Kiralama','Loan'),
              'Kiralama bitti / Loan ended':self.tr('Kiralama bitti','Loan ended')}
  self.tree([self.tr('Hafta','Week'),self.tr('Haber','News'),self.tr('Ayrıntı','Details')],
            [(week,loan_types.get(kind,kind),self.money_news(message))
             for week,kind,message in reversed(self.s['news'][-50:])],wide=True)

 def inbox_page(self):
  self.clear()
  tr=self.tr
  s=self.s
  if s.get('living_club'):
   from yasayan_kulup import pending_question
   if pending_question(s):
    self.button(self.body,'Basın sorusunu yanıtla','Answer press question',lambda:self.club_life_page(2)).pack(anchor='w')
  ttk.Label(self.body,text=tr('Haftalık gündem','Weekly inbox'),style='Title.TLabel').pack(anchor='w')
  bar=ttk.Frame(self.body);bar.pack(anchor='w',pady=6)
  self.button(bar,'Maça hazırlan','Match preparation',self.preparation).pack(side='left')
  self.button(bar,'Genç oyuncu takibi','Youth watch',self.youth_watch).pack(side='left')
  self.button(bar,'Son maç','Last match',self.last_report).pack(side='left')
  captions={'injury':tr('Yeni sakatlık','New injury'),'recovery':tr('İyileşti','Recovered'),
            'tired':tr('Yorgunluk','Fatigue'),'form':tr('Form değişimi','Form moved'),
            'youth':tr('Genç oyuncu dakikası','Youth minutes'),'contract':tr('Sözleşme bitişi','Contract expiring'),
            'transfer':tr('Transfer teklifi','Transfer offer'),'job':tr('İş teklifi','Job offer'),
            'fixture':tr('Sıradaki rakip','Next opponent')}
  entries=[(entry,item) for entry in reversed(s.get('inbox',[])) if entry['club']==s['club'] for item in entry['items']]
  def caption(subject):
   p=player(s,subject)
   return p['name'] if p else subject
  grid=self.tree([tr('Hafta','Week'),tr('Olay','Event'),tr('Kişi / Kulüp','Person / Club'),tr('Değer','Value')],
     [(f"{entry['year']}/{entry['week']}",captions[kind],caption(subject),value)
      for entry,(_,kind,subject,value) in entries],wide=True)
  def action():
   if not grid.selection():return
   _,(_,kind,subject,_) = entries[int(grid.selection()[0])]
   if kind=='fixture':self.preparation()
   elif kind=='job':self.jobs_page()
   elif kind=='transfer':self.offers_page()
   elif s['employed'] and s['owners'].get(subject)==s['club']:
    if kind=='contract':self.negotiate(player(s,subject),True)
    else:self.training_page([subject])
  self.button(bar,'Seçili olay','Open selected',action).pack(side='left')
 def preparation(self):
  self.clear()
  ttk.Label(self.body,text=self.tr('Maç hazırlığı','Match preparation'),style='Title.TLabel').pack(anchor='w')
  ttk.Label(self.body,text=self.calendar_text(),wraplength=860).pack(anchor='w',pady=12)
  s=self.s
  fixture=next((m for m in s['schedule'] if m['week']==s['week']
                and s['club'] in (m['home'],m['away'])),None)
  if fixture:
   rival=fixture['away'] if fixture['home']==s['club'] else fixture['home']
   stats=s['teams'][rival]
   row=self.tr('Rakip · {club} · {points} puan · G/A {goals}/{against}',
               'Opponent · {club} · {points} points · GF/GA {goals}/{against}')
   ttk.Label(self.body,text=row.format(club=rival,points=stats['p'],goals=stats['gf'],against=stats['ga'])).pack(anchor='w',pady=(0,8))
  self.button(self.body,'Taktik ve ilk 11','Tactics and XI',self.tactics).pack(anchor='w')
  self.button(self.body,'İzleme modu','Match mode',self.match_settings).pack(anchor='w')
  self.button(self.body,'Maç haftasını başlat','Start match week',self.next).pack(anchor='w')
 def youth_watch(self):
  from gundem import cohorts
  self.clear();s=self.s;tr=self.tr
  ttk.Label(self.body,text=tr('Genç oyuncu takibi','Youth watch'),style='Title.TLabel').pack(anchor='w')
  ttk.Label(self.body,text=tr('Yaş grupları A takım kadrosundan filtrelenir.','Age groups filter the senior squad.')).pack(anchor='w')
  squads=cohorts(s)
  players=[(group,p) for group in ('U18','U20') for p in squads[group]]
  grid=self.tree([tr('Oyuncu','Player'),tr('Grup','Group'),tr('Yaş','Age'),tr('Dakika','Minutes'),tr('Yetenek','Ability')],
    [(p['name'],group,age_at(p,s['year'],s['week']),state(s,p)['minutes'],ability(s,p)) for group,p in players])
  self.button(self.body,'Bireysel antrenman','Individual training',
     lambda:self.training_page([players[int(grid.selection()[0])][1]['id']]) if grid.selection() and s['employed'] else None).pack(anchor='w')
 def weekly_page(self):
  self.clear()
  s=self.s; msg=self.management_text
  ttk.Label(self.body,text=msg('week_title')).pack(anchor='w')
  report=s.get('weekly_feedback',{})
  if report.get('club')!=s['club'] or report.get('year')!=s['year']:
   ttk.Label(self.body,text=msg('no_week')).pack(anchor='w',pady=8)
   self.button(self.body,*TEXT['desk'],self.dashboard).pack(anchor='w')
   return
  ttk.Label(self.body,text=msg('week_explain',week=report['week']),wraplength=850).pack(anchor='w',pady=8)
  def change(delta):
   return '—' if delta is None else f'{delta:+g}'
  rows=[]
  for pid,z in report['players'].items():
   p=player(s,pid)
   if p is None:continue
   alerts=[]
   if z['injury']:alerts.append(msg('injury',count=z['injury']))
   if z['condition']<70:alerts.append(msg('fatigue'))
   if isinstance(z['age'],int) and z['age']<25:alerts.append(msg('youth'))
   if 'session' in z:
    focus,intensity,status,delta=z['session']
    outcome={'trained':self.tr('çalıştı','trained'),'recovered':self.tr('toparlandı','recovered'),
             'injured':self.tr('sakatlık nedeniyle katılmadı','missed through injury')}
    alerts.append(f"{msg(focus)} / {msg(intensity)} · {outcome[status]} · {delta:+g}")
   rows.append((p['name'],z['minutes'],change(z['minute_change']),
                f"{z['condition']}% ({change(z['condition_change'])})",
                round(z['morale']),f"{z['form']} ({change(z['form_change'])})",
                '—' if z['training'] is None else z['training'],', '.join(alerts)))
  self.button(self.body,*TEXT['desk'],self.dashboard).pack(anchor='w')
  self.tree([msg(key) for key in ('player','minutes','change','fitness','morale','form','training','alerts')],rows,wide=True)
 def review_page(self):
  self.clear()
  s=self.s; msg=self.management_text; info=squad_review(s)
  ttk.Label(self.body,text=msg('squad_title')).pack(anchor='w')
  fixture=info['fixture']
  if fixture:
   first=msg('fixture',week=fixture['week'],home=fixture['home'],away=fixture['away'])
   ttk.Label(self.body,text=first,wraplength=850).pack(anchor='w')
  ttk.Label(self.body,text=msg('budgets',transfer=money_text(s,info['transfer']),
            paid=money_text(s,info['payroll']),wage=money_text(s,info['wage']))).pack(anchor='w',pady=6)
  for role,players in info['groups'].items():
   target=info['targets'][role]
   eligible=sum(not row['injury'] and not row['ban'] and row['condition']>=70 for row in players)
   older=sum(isinstance(row['age'],int) and row['age']>=32 for row in players)
   status=msg('shortage') if len(players)<target else msg('weak') if eligible<target else ''
   ttk.Label(self.body,text=msg('group',role=position_label(role,self.lang),count=len(players),
             target=target,eligible=eligible,older=older,status=status)).pack(anchor='w')
  ttk.Label(self.body,text=msg('review_explain'),wraplength=850).pack(anchor='w',pady=6)
  rows=[]
  for role,players in info['groups'].items():
   for row in players:
    alerts=[]
    if row['expiry']<=s['year']:alerts.append(msg('expired'))
    elif row['expiry']==s['year']+1:alerts.append(msg('expires'))
    if row['injury']:alerts.append(msg('injury',count=row['injury']))
    if row['ban']:alerts.append(msg('suspended'))
    if row['condition']<70:alerts.append(msg('fatigue'))
    young=isinstance(row['age'],int) and row['age']<25
    if young:alerts.append(msg('youth'))
    pa=msg('potential_room' if row['potential']-row['ability']>=1 else 'potential_limited') if young and row['potential'] is not None else '—'
    rows.append((row['player']['name'],position_label(role,self.lang),row['age'],
                 row['expiry'],f"{row['condition']}%",pa,', '.join(alerts)))
  self.button(self.body,*TEXT['desk'],self.dashboard).pack(anchor='w')
  rows.extend((p['name'],position_label(p['pos'],self.lang),
               age_at(p,s['year'],s['week']),s['year'],'—','—',msg('expired_at_open'))
              for p in info['expired'])
  self.tree([msg(key) for key in ('player','position','age','expiry','fitness','potential','alerts')],rows,wide=True)
 def money_news(self,text):
  if self.s['currency']=='USD':
   return text
  return re.sub(r"\$\s*([0-9][0-9,]*)",lambda match:money_text(self.s,int(match[1].replace(',',''))),text)
 def switch(self):self.toggle();self.s['lang']=self.lang;self.menu();self.squad()
 def header(self):
  s=self.s
  manager=s.get('manager_state')
  club=(manager['active_team'] or self.management_text('unemployed_flag')) if manager else s['club']
  self.head.config(text=f"{club} • {s['year']}/{str(s['year']+1)[-2:]} • {s['manager']} • {self.tr('Hafta','Week')} {min(34,s['week'])}")
 def tree(self,cols,rows,wide=False):
  frame=ttk.Frame(self.body);frame.pack(fill='both',expand=True);t=ttk.Treeview(frame,columns=list(range(len(cols))),show='headings');scroll=ttk.Scrollbar(frame,command=t.yview);t.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y')
  if wide:
   horizontal=ttk.Scrollbar(frame,orient='horizontal',command=t.xview)
   t.configure(xscrollcommand=horizontal.set);horizontal.pack(side='bottom',fill='x')
  t.pack(fill='both',expand=True)
  for i,c in enumerate(cols):t.heading(i,text=c,command=lambda i=i:self.sort_tree(t,i));t.column(i,width=(260 if i==0 else 124) if wide else (240 if i==0 else 95),minwidth=50,stretch=not wide,anchor='w' if i==0 else 'center')
  t.tag_configure('even',background=THEME['row']);t.tag_configure('odd',background=THEME['stripe'])
  for i,row in enumerate(rows):t.insert('', 'end',iid=str(i),values=row,tags=('odd' if i%2 else 'even',))
  if rows:resize_columns(t,compact=True)
  return t
 def sort_tree(self,t,i,raw=None):
  def key(k):
   if raw is not None:return raw[int(k)]
   v=t.set(k,i)
   try:return (0,float(v))
   except ValueError:return (1,v.casefold())
  rev=getattr(t,'_sort',None)==(i,False);t._sort=(i,rev)
  for n,k in enumerate(sorted(t.get_children(),key=key,reverse=rev)):t.move(k,'',n)
 def external_profile(self,p):
  s=self.s;tr=self.tr
  w=tk.Toplevel(self.r);w.title(p['name']);w.geometry('560x360')
  panel=ttk.Frame(w,padding=18);panel.pack(fill='both',expand=True)
  ttk.Label(panel,text=p['name'],style='Title.TLabel',wraplength=490).pack(anchor='w')
  team=s['owners'].get(p['id'],tr('Serbest','Free'))
  for text in (team,position_label(p['pos'],self.lang),player_countries(p,self.lang)):
   ttk.Label(panel,text=text).pack(anchor='w',pady=4)
  report=report_index(s).get(p['id'])
  text=tr('Gözlem raporu gerekli','Scouting report required')
  if report:
   ratings=['–'.join(map(str,band)) for band in report['bands']]
   text=f"{tr('Yetenek / Potansiyel','Ability / Potential')} · {' / '.join(ratings)}"
  ttk.Label(panel,text=text).pack(anchor='w',pady=12)
  if report and report.get('groups'):
   for key,label in (('technical',tr('Teknik','Technical')),('mental',tr('Zihinsel','Mental')),
                     ('physical',tr('Fiziksel','Physical'))):
    lo,hi=report['groups'][key]
    ttk.Label(panel,text=f'{label} · {lo}–{hi}').pack(anchor='w')
  if s['employed'] and s['owners'].get(p['id'])!=s['club']:
   self.button(panel,'Teklif ver','Make offer',lambda:self.negotiate(p)).pack(anchor='w')
  return w
 def profile(self,p):
  if self.s['owners'].get(p['id'])!=self.s['club'] or not self.s['employed']:
   return self.external_profile(p)
  w=tk.Toplevel(self.r);w.title(p['name']);w.configure(bg=THEME['panel']);w.geometry('850x560');f=ttk.Frame(w,padding=24);f.pack(fill='both',expand=True)
  tk.Label(f,text=p['name'],font=(FONT,26,'bold'),bg=THEME['base'],fg=THEME['accent'],pady=12).pack(fill='x');ttk.Label(f,text=self.s['owners'].get(p['id'],'Serbest / Free')+'  /  '+position_label(p['pos'], self.lang)).pack(anchor='w',pady=8)
  if p['id'] in self.s['owners']:
   ttk.Label(f,text=self.contract_label(p)).pack(anchor='w')
  if self.s.get('position_model') and p.get('alternate_positions'):
   alternatives=', '.join(detail_position(code,self.lang) if code in POSITION_NAMES
                          else position_label(code,self.lang) for code in p['alternate_positions'])
   ttk.Label(f,text=self.management_text('secondary_catalog',positions=alternatives)).pack(anchor='w')
  bar=ttk.Frame(f);bar.pack(anchor='w',pady=6)
  self.button(bar,'Sözleşme görüşmesi','Contract talks',lambda:self.negotiate(p,True)).pack(side='left',padx=2)
  self.button(bar,'Bireysel antrenman','Individual training',lambda:(w.destroy(),self.training_page([p['id']]))).pack(side='left',padx=2)
  tabs=ttk.Notebook(f);tabs.pack(fill='both',expand=True);z=state(self.s,p)
  for title,items in [(self.tr('Profil','Profile'),[(self.tr('Mevki','Position'),position_label(p['pos'], self.lang)),(self.tr('Yaş','Age'),age_at(p,self.s['year'],self.s['week'])),(self.tr('Yetenek (tahmini)','Ability (estimated)'),str(round(z['ability'],1))+'/20'),(self.tr('Kondisyon','Fitness'),str(z['condition'])+'%'),(self.tr('Moral','Morale'),round(z['morale'])),(self.tr('Form','Form'),z['form']),(self.tr('Maç','Apps'),z['apps']),(self.tr('Dakika','Minutes'),z.get('minutes','—')),(self.tr('Gol','Goals'),self.s['goals'].get(p['id'],0))]),(self.tr('Kişisel bilgiler','Personal details'),[(self.tr('Tam adı','Full name'),p.get('full_name',p['name'])),(self.tr('Doğum tarihi','Date of birth'),p.get('dob')),(self.tr('Milliyet','Nationality'),player_countries(p, self.lang))])]:
   pane=ttk.Frame(tabs,padding=14);tabs.add(pane,text=title);pane.columnconfigure(1,weight=1)
   for i,(label,value) in enumerate(items):
    ttk.Label(pane,text=label).grid(row=i,column=0,sticky='w',padx=(0,25),pady=5);ttk.Label(pane,text=str(value) if value not in (None,'','?') else '—',foreground=THEME['accent']).grid(row=i,column=1,sticky='w',pady=5)
  history=ttk.Frame(tabs,padding=10)
  tabs.add(history,text=self.tr('Kariyer','Career'))
  grid=data_table(history,[self.tr('Sezon','Season'),self.tr('Kulüp','Club'),self.tr('Maç','Apps'),
                          self.tr('Dakika','Minutes'),self.tr('Gol','Goals'),self.tr('Asist','Assists')])
  stats=[(self.s['year'],self.s.get('season_stats',{}))]+[
         (season['year'],season.get('player_stats',{})) for season in reversed(self.s['history'])]
  for year,season in stats:
   for club,results in season.get(p['id'],{}).items():
    grid.insert('','end',values=(year,club,*[results[k] for k in ('apps','minutes','goals','assists')]))
  resize_columns(grid,compact=True)
  development=ttk.Frame(tabs,padding=14)
  tabs.add(development,text=self.tr('Gelişim','Development'))
  season=self.s.get('season_development',{})
  change=season.get('changes',{}).get(p['id'])
  ttk.Label(development,text=self.tr('Son sezon yetenek değişimi','Last season ability change')+
    (' · —' if change is None else f' · {change:+.2f}')).pack(anchor='w')
  ttk.Label(development,text=self.tr('Sezon dakikası','Season minutes')+f" · {z.get('minutes',0)}").pack(anchor='w',pady=6)
  pane=ttk.Frame(tabs,padding=8);tabs.add(pane,text=self.tr('Özellikler (tahmini)','Attributes (estimated)'))
  labels='Bitiricilik,Pas,Teknik,Dribling,Top kapma,Markaj,Kafa,Orta,İlk kontrol,Uzaktan şut,Duran top,Top tutma,Karar,Vizyon,Pozisyon,Çalışkanlık,Kararlılık,Soğukkanlılık,Sezgi,Takım oyunu,Konsantrasyon,Yaratıcılık,Liderlik,Cesaret,Hız,Hızlanma,Dayanıklılık,Güç,Çeviklik,Denge,Sıçrama,Refleks,Bire bir,Vuruş,Hava hakimiyeti,Doğal kondisyon'.split(',')
  for i,(name,val) in enumerate(attributes(self.s,p).items()):
   col=(i//12)*2;row=i%12;ttk.Label(pane,text=self.tr(labels[i],name)).grid(row=row,column=col,sticky='w',padx=4);ttk.Label(pane,text=str(val),foreground=THEME['accent']).grid(row=row,column=col+1,padx=8)
 def career_page(self):
  if 'manager_state' in self.s:return self.employment_page()
  self.clear();rows=career(self.s); totals={k:sum(r[k] for r in rows) for k in ('n','w','d','l','gf','ga')}; pct=100*totals['w']/max(1,totals['n']);tr=self.tr
  ttk.Label(self.body,text=self.s['manager']+'  /  '+tr('Menajer kariyeri','Manager career'),font=(FONT,22,'bold')).pack(anchor='w',pady=(0,14))
  bar=ttk.Frame(self.body);bar.pack(fill='x',pady=(0,15))
  for label,val in [(tr('Maç','Matches'),totals['n']),(tr('Galibiyet','Wins'),totals['w']),(tr('Beraberlik','Draws'),totals['d']),(tr('Mağlubiyet','Losses'),totals['l']),(tr('Galibiyet oranı','Win rate'),f'{pct:.1f}%'),(tr('Lig şampiyonluğu','League titles'),sum(r['title'] for r in rows))]:
   tile=tk.Frame(bar,bg=THEME['base'],padx=9,pady=10);tile.pack(side='left',fill='both',expand=True,padx=3);tk.Label(tile,text=label,bg=THEME['base'],fg=THEME['muted']).pack();tk.Label(tile,text=val,bg=THEME['base'],fg=THEME['accent'],font=(FONT,21,'bold')).pack()
  self.tree([tr('Sezon / Kulüp','Season / Club'),tr('Maç','P'),tr('G','W'),tr('B','D'),tr('M','L'),tr('AG','GF'),tr('YG','GA'),tr('G %','Win %'),tr('Sıra','Rank'),tr('Başarı','Honours')],[(f"{r['year']}/{str(r['year']+1)[-2:]} · {r['club']}",r['n'],r['w'],r['d'],r['l'],r['gf'],r['ga'],f"{100*r['w']/max(1,r['n']):.1f}%",r['rank'] or '—',tr('Şampiyon','Champion') if r['title'] else tr('Devam ediyor','In progress') if not r['finished'] else '—') for r in rows])
 def contract_label(self,p):
  expiry,years,months=contract_time(self.s,p)
  date=expiry.strftime('%d.%m.%Y') if self.lang=='TR' else expiry.isoformat()
  return f"{self.tr('Sözleşme','Contract')} {date} · {years} {self.tr('yıl','yr')} {months} {self.tr('ay','mo')}"
 def contract_cells(self,p):
  expiry,years,months=contract_time(self.s,p)
  return expiry.isoformat(),f"{years} {self.tr('y','yr')} {months} {self.tr('ay','mo')}"
 def training_page(self, ids=None):
  if 'manager_state' in self.s and not self.s['employed']:return self.employment_page()
  self.clear()
  s=self.s; msg=self.management_text
  people=[p for p in roster(s['club'],s['year'],s) if ids is None or p['id'] in ids]
  ttk.Label(self.body,text=self.tr('Haftalık antrenman planı','Weekly training plan')).pack(anchor='w')
  ttk.Label(self.body,text=msg('training_explain'),wraplength=820).pack(anchor='w',pady=8)
  ttk.Label(self.body,text=self.tr(
   'Son lig maçında 60+ dakika oynayanlarda yoğun çalışma 2 ek kondisyon puanı tüketebilir. '
   'Otomatik plan, dinç genç yedeklere son maçta oynamadılarsa teknik çalışma verir. '
   'Toparlanma kondisyonu artırır, gelişim puanı vermez.',
   'Intense work can cost two extra condition points after 60+ minutes in the last league match. '
   'Automatic planning assigns technical work to fit young players who missed that match. '
   'Recovery restores condition without adding development credit.'
  ),wraplength=820).pack(anchor='w')
  plans=s.setdefault('individual_training',{})
  enabled=tk.BooleanVar(value=s.get('auto_training',False))
  ttk.Checkbutton(self.body,text=msg('automatic'),variable=enabled,
                  command=lambda:s.update(auto_training=enabled.get())).pack(anchor='w')
  panel=ttk.Frame(self.body);panel.pack(anchor='w',pady=8)
  focus=ttk.Combobox(panel,values=[msg(key) for key in (*FOCUSES,'inherit')],state='readonly',width=24)
  speed=ttk.Combobox(panel,values=[msg(key) for key in INTENSITIES],state='readonly',width=16)
  selected={tuple(plans.get(p['id'],('inherit','normal'))) for p in people}
  f,l=next(iter(selected)) if len(selected)==1 else ('inherit','normal')
  focus.current((*FOCUSES,'inherit').index(f)); speed.current(INTENSITIES.index(l))
  focus.pack(side='left'); speed.pack(side='left',padx=6)
  def apply():
   if not s['employed']:return
   selection=grid.selection()
   subjects=[people[int(i)] for i in selection] if selection else people
   for p in subjects:
    if focus.current()==len(FOCUSES):
     plans.pop(p['id'],None)
    else:
     plans[p['id']]=[FOCUSES[focus.current()],INTENSITIES[speed.current()]]
   self.training_page(ids)
  self.button(panel,*TEXT['assign'],apply).pack(side='left')
  self.button(panel,*TEXT['monthly_title'],self.monthly_page).pack(side='left',padx=4)
  self.button(panel,*TEXT['back_squad'],self.squad).pack(side='left',padx=4)
  rows=[]
  for p in people:
   pid=p['id']; fitness=s['fitness'][pid]; minutes=recent_minutes(s,pid)
   cue=(self.tr('Sakat','Injured') if fitness['injury'] else
        self.tr('Toparlanma önerilir','Recovery recommended') if fitness['condition']<70 else
        self.tr('Yükü izle','Monitor load') if minutes is not None and minutes>=60 else
        self.tr('Maç pratiği eksik','Lacks match practice') if minutes==0 else '—')
   focus_key,intensity=plans.get(pid,('inherit',None))
   rows.append((p['name'],msg(focus_key),msg(intensity) if intensity else '—',
                f"{fitness['condition']}%",minutes if minutes is not None else '—',cue))
  grid=self.tree([msg('player'),msg('focus'),msg('intensity'),self.tr('Kondisyon','Condition'),
             self.tr('Son maç dk.','Last match min.'),self.tr('Hazırlık notu','Readiness note')],rows,wide=True)
 def monthly_page(self):
  self.clear()
  s=self.s; msg=self.management_text
  ttk.Label(self.body,text=msg('monthly_title')).pack(anchor='w')
  reports=[row for row in s.get('monthly_training',[]) if row['club']==s['club']]
  actual=s.get('season_development',{})
  if actual.get('club')==s['club']:
   changes=actual['changes']
  else:
   changes={}
  controls=ttk.Frame(self.body);controls.pack(anchor='w',pady=5)
  self.button(controls,*TEXT['back_squad'],self.squad).pack(side='left')
  if not reports and not changes:
   ttk.Label(self.body,text=msg('no_month')).pack(anchor='w')
   return
  options=[row['month'] for row in reports]
  if changes:options.append(msg('annual',year=actual['year']))
  choice=ttk.Combobox(controls,values=options,state='readonly',width=34)
  choice.current(len(reports)-1 if reports else 0);choice.pack(side='left',padx=8)
  widgets=[]
  def view(_event=None):
   for widget in widgets:widget.destroy()
   widgets.clear()
   i=choice.current()
   if i==len(reports):
    if s.get('match_model',0)==4:
     label=ttk.Label(self.body,text=msg('annual_development_explain'),wraplength=840)
     label.pack(anchor='w');widgets.append(label)
    rows=[(p['name'],f'{delta:+.2f}') for pid,delta in changes.items() if (p:=player(s,pid))]
    tree=self.tree([msg('player'),msg('actual_ca')],rows)
   else:
    report=reports[i]
    previous=reports[i-1]['players'] if i and (int(report['month'][:4])*12+int(report['month'][5:]))-(int(reports[i-1]['month'][:4])*12+int(reports[i-1]['month'][5:]))==1 else {}
    label=ttk.Label(self.body,text=msg('month_explain',weeks=report['weeks']),wraplength=840)
    label.pack(anchor='w');widgets.append(label)
    rows=[]
    for pid,row in report['players'].items():
     p=player(s,pid)
     if p is None:continue
     plan=', '.join(f'{msg(f)} / {msg(l)} ×{n}' for key,n in row['plans'].items() for f,l in [key.split('/')])
     if row['team_weeks']:plan+=' '+msg('team_weeks',count=row['team_weeks'])
     last=previous.get(pid)
     comparison=(f"{row['minutes']-last['minutes']:+d}′ · {row['condition']-last['condition']:+g}%" if last else '—')
     rows.append((p['name'],row['minutes'],plan,row['participation'],row['training'],
                  row['condition'],row['recovery'],round(row['morale']),row['form'],
                  f"{row['injured_weeks']} / {row['injury']}",comparison,msg('youth') if row['youth'] else '—'))
    tree=self.tree([msg(key) for key in ('player','minutes','focus','participation','training','fitness',
             'recovery','morale','form','injury_summary','last_month','youth_watch')],rows,wide=True)
    tree.column(2,width=330)
   widgets.append(tree.master)
  choice.bind('<<ComboboxSelected>>',view)
  view()
 def squad(self):
  if 'manager_state' in self.s and not self.s['employed']:return self.club_squad(self.s['club'])
  self.clear();s=self.s;ps=roster(s['club'],s['year'],s);chosen={p['id'] for p in lineup(s,s['club'])};ttk.Label(self.body,text=self.tr('Ctrl ile ilk 11 tercihini seç.','Ctrl-select preferred XI.')).pack();t=self.tree([self.tr('Oyuncu','Player'),'No',self.tr('Mevki','Position'),self.tr('Yaş','Age'),self.tr('Ülke','Nation'),self.tr('Yetenek*','Ability*'),self.tr('Kond.','Fit.'),self.tr('Moral','Morale'),self.tr('Form','Form'),self.tr('Sakat','Inj.'),self.tr('İlk 11','XI'),self.tr('Sözl. bitiş','Expiry'),self.tr('Kalan','Time left')],[(p['name'],s.get('numbers',{}).get(p['id'],p['number']),position_label(p['pos'], self.lang),str(age_at(p,s['year'],s['week'])).replace('?','—'),player_countries(p, self.lang),round(state(s,p)['ability'],1),state(s,p)['condition'],round(state(s,p)['morale']),state(s,p)['form'],state(s,p)['injury'],'✓' if p['id'] in chosen else '',*self.contract_cells(p)) for p in ps]);t.bind('<Double-1>',lambda e:self.profile(ps[int(t.identify_row(e.y))]) if t.identify_row(e.y) else None);self.button(self.body,'Tercihi uygula','Apply selection',lambda:(s.update(selected=[ps[int(i)]['id'] for i in t.selection()][:11]),s.pop('manual_xi',None),s.pop('auto_xi',None),self.squad())).pack()
  management=ttk.Frame(self.body);management.pack(anchor='w')
  self.button(management,*TEXT['individual'],lambda:self.training_page(
      [ps[int(i)]['id'] for i in t.selection()] or [p['id'] for p in ps])).pack(side='left')
  self.button(management,*TEXT['monthly_title'],self.monthly_page).pack(side='left',padx=6)
  def contract():
   selected=t.selection()
   if selected and s['employed']:
    self.negotiate(ps[int(selected[0])],True)
  scroll=ttk.Scrollbar(t.master,orient='horizontal',command=t.xview)
  scroll.pack(side='bottom',fill='x',before=t)
  t.configure(xscrollcommand=scroll.set)
  for col in range(1,13):t.column(col,stretch=False)
  t.tag_configure('expiring',foreground='#ffd17d')
  for i,p in enumerate(ps):
   expiry,years,months=contract_time(s,p)
   tags=tuple(t.item(str(i),'tags'))
   if years==0 and months<=6:
    t.item(str(i),tags=tags+('expiring',))
  contract_bar=ttk.Frame(self.body);contract_bar.pack(fill='x',pady=3)
  summary=ttk.Label(contract_bar);summary.pack(side='left')
  def selected_contract(_event):
   selected=t.selection()
   if selected:
    z=state(s,ps[int(selected[0])])
    status={'listed':self.tr('Satılık','Listed'),'blocked':self.tr('Satışa kapalı','Not for sale')}
    status['loan']=self.tr('Kiralanabilir','Available for loan')
    p=ps[int(selected[0])]
    loan=s.get('loans',{}).get(p['id'])
    label=self.tr('Kiralık','On loan') if loan else status.get(s['sale_status'].get(p['id']),'—')
    summary.config(text=f"{self.contract_label(p)} · {money_text(s,z['wage'])} · {label}")
  t.bind('<<TreeviewSelect>>',selected_contract)
  self.button(contract_bar,'Sözleşme yenile','Renew contract',contract).pack(side='right')
  def sale(mode):
   if t.selection() and set_sale_status(s,ps[int(t.selection()[0])]['id'],mode):
    selected_contract(None);self.autosave()
  modes=[('Satılık','List','listed'),('Satışa kapat','Block sale','blocked'),('Sıfırla','Reset','normal')]
  if s.get('transfer_model'):modes.append(('Kiralık listesi','List for loan','loan'))
  for a,b,mode in modes:
   self.button(contract_bar,a,b,lambda mode=mode:sale(mode)).pack(side='right',padx=2)
 def reason(self,reason):
  messages={
   'player':('Oyuncu koşulları reddetti. Maaşı, imza parasını veya rolü değiştirin.','Player rejected the terms. Adjust wages, signing bonus or role.'),
   'seller':('Satıcı kulüp bu bedeli kabul etmedi veya kadrosu yetersiz.','The selling club rejected the fee or its squad is too small.'),
   'buyer':('Alıcı karşı teklifi reddetti.','The buying club rejected the counteroffer.'),
   'withdrawn':('Kulüp bu transfer döneminde görüşmeden çekildi.','The club has withdrawn for this transfer window.'),
   'budget':('Nakit, transfer veya haftalık maaş bütçesi ya da kadro sınırı yetersiz.','Insufficient cash, transfer or weekly wage budget, or squad space.'),
   'fee':('Geçersiz bonservis bedeli.','Invalid transfer fee.'),
   'unavailable':('İşlem şu anda yapılamıyor.','The deal is currently unavailable.'),
  }
  return self.tr(*messages.get(reason,messages['unavailable']))
 def negotiate(self,p,renewal=False):
  s=self.s
  if not s['employed'] or p['id'] in s.get('loans',{}) or (not renewal and not window(s)):
   messagebox.showinfo('Top Antrenörü',self.reason('unavailable'));return
  tr=self.tr;club=s['club'];z=state(s,p)
  terms=asking_terms(s,p,club,'Starter')
  owner=s['owners'].get(p['id'])
  w=tk.Toplevel(self.r);w.title(p['name']);w.transient(self.r);w.grab_set()
  f=ttk.Frame(w,padding=18);f.pack(fill='both',expand=True)
  if renewal or owner:
   ttk.Label(f,text=f"{tr('Mevcut maaş','Current wage')} {money_text(s,z['wage'])} · {tr('Bitiş sezonu','Expiry season')} {z['contract']}").grid(row=0,column=0,columnspan=2,sticky='w',pady=6)
  fields=[('years',tr('Süre (sezon)','Length (seasons)'),terms['years']),
          ('wage',tr('Haftalık maaş','Weekly wage'),terms['wage']),
          ('signing',tr('İmza parası','Signing bonus'),terms['signing'])]
  if not renewal:
   fields.insert(0,('fee',tr('Bonservis','Transfer fee'),asking_fee(s,p)))
  entries={}
  for row,(key,label,default) in enumerate(fields,1):
   ttk.Label(f,text=label if key=='years' else f'{label} ({money_rate(s)[1]})').grid(row=row,column=0,sticky='w',pady=4)
   entries[key]=tk.StringVar(value=str(default) if key=='years' else edit_value(s,default))
   ttk.Entry(f,textvariable=entries[key]).grid(row=row,column=1,pady=4)
  installments=None
  bargain=bool(s.get('transfer_model') and owner and not renewal)
  if bargain:
   ttk.Label(f,text=tr('Ödeme','Payment')).grid(row=5,column=0,sticky='w')
   installments=ttk.Combobox(f,state='readonly',values=(tr('Peşin','Upfront'),tr('3 taksit','3 installments')))
   installments.current(0);installments.grid(row=5,column=1)
  rounds=0
  roles=(tr('İlk 11','Starter'),tr('Rotasyon','Rotation'))
  role=ttk.Combobox(f,values=roles,state='readonly')
  role.current(0);role.grid(row=6,column=1)
  ttk.Label(f,text=tr('Beklenen rol','Expected role')).grid(row=6,column=0,sticky='w')
  feedback=ttk.Label(f,wraplength=370);feedback.grid(row=8,column=0,columnspan=2)
  def submit():
   nonlocal rounds
   try: amounts={key:int(var.get()) if key=='years' else from_display(s,var.get()) for key,var in entries.items()}
   except ValueError: feedback.config(text=tr('Tutarları sayı olarak girin.','Enter numeric terms.'));return
   amounts['role']='Starter' if role.current()==0 else 'Rotation'
   if bargain:
    ok,reason,quote=purchase_offer(s,p['id'],club,**amounts,
                                  payments=3 if installments.current()==1 else 1,rounds=rounds)
    if reason=='counter':
     rounds+=1
     entries['fee'].set(edit_value(s,quote))
     feedback.config(text=tr('Satıcının karşı teklifi','Seller counteroffer')+' · '+money_text(s,quote))
     return
    if reason=='withdrawn':
     feedback.config(text=self.reason(reason));submit_button.state(['disabled']);self.autosave()
     return
   else:
    ok,reason=renew(s,p['id'],**amounts) if renewal else deal(s,p['id'],club,**amounts)
   if ok:
    if s.get('match_model'):
     messagebox.showinfo(tr('Teklif kabul edildi','Offer accepted'),
      tr('Ücret, imza parası, süre ve forma rolü oyuncunun koşullarını karşıladı.',
         'Wage, signing bonus, term and squad role met the player’s terms.'),parent=w)
    w.destroy();self.autosave();(self.squad if renewal else self.market)()
   else:
    explanation=None
    if reason=='player':
     explanation=player_objection(s,p,club,**{k:amounts[k] for k in ('years','wage','signing','role')})
    elif reason=='seller':
     explanation='seller_fee' if selling_ready(s,p) else 'seller_unavailable'
    feedback.config(text=self.management_text(explanation) if explanation in TEXT else self.reason(reason))
  msg=self.management_text
  details=ttk.Label(f,wraplength=540,justify='left')
  details.grid(row=9,column=0,columnspan=2,sticky='w')
  def preview(*_args):
   try:
    fee=from_display(s,entries['fee'].get()) if 'fee' in entries else 0
    wage=from_display(s,entries['wage'].get())
    signing=from_display(s,entries['signing'].get())
   except ValueError:
    details.configure(text=msg('invalid_amount'));return
   estimate=asking_terms(s,p,club,'Starter' if role.current()==0 else 'Rotation')
   ledger=s['finance'][club]
   wage_after=payroll(s,club)+wage-(z['wage'] if renewal else 0)
   details.configure(text=msg('offer_preview',value=money_text(s,value(s,p)),
     ask=money_text(s,0 if renewal else asking_fee(s,p)),wage=money_text(s,estimate['wage']),
     years=estimate['years'],signing=money_text(s,estimate['signing']),
     fee_cost=money_text(s,fee+signing),transfer=money_text(s,ledger['transfer_budget']),
     cash=money_text(s,ledger['cash']),after=money_text(s,wage_after),
     wage_limit=money_text(s,ledger['wage_budget'])))
   if installments is not None and installments.current()==1 and fee>=3:
    deferred=fee//3
    schedule_text=tr('Bugün {first}; {w1}. ve {w2}. haftalarda {later}. Toplam tutar bütçeden ayrılır.',
                     'Today {first}; {later} in weeks {w1} and {w2}. The full amount is reserved.')
    details.configure(text=details.cget('text')+'\n'+schedule_text.format(
      first=money_text(s,fee-2*deferred+signing),later=money_text(s,deferred),
      w1=s['week']+4,w2=s['week']+8))
   if s.get('match_model'):
    try:years=int(entries['years'].get())
    except ValueError:return
    result=player_objection(s,p,club,years,wage,signing,'Starter' if role.current()==0 else 'Rotation')
    assessment=msg(result) if result in TEXT else self.reason(result) if result else tr(
      'Oyuncu koşulları karşılanıyor. Satıcı ve bütçe onayı ayrıca gerekir.',
      'Player terms are met. Budget and seller approval are checked separately.')
    details.configure(text=details.cget('text')+'\n'+assessment)
  for field in entries.values():field.trace_add('write',preview)
  role.bind('<<ComboboxSelected>>',preview)
  if installments is not None:installments.bind('<<ComboboxSelected>>',preview)
  preview()
  submit_button=self.button(f,'Teklifi ilet','Submit offer',submit)
  submit_button.grid(row=7,column=1,pady=8)
 def offer_loan(self,p):
  s=self.s;tr=self.tr;club=s['club'];pid=p['id']
  if not s['employed'] or not window(s) or s['owners'].get(pid)==club or not loan_ready(s,p):
   messagebox.showinfo('Top Antrenörü',tr('Oyuncu kiralamaya uygun değil.','Player is unavailable for loan.'),parent=self.r)
   return
  w=tk.Toplevel(self.r);w.title(tr('Kiralama teklifi','Loan offer'));w.transient(self.r);w.grab_set()
  ttk.Label(w,text=f"{p['name']} · "+tr('Sezon sonuna kadar','Until season end')).pack(padx=14,pady=8)
  ttk.Label(w,text=tr('Kiralama bedeli','Loan fee')+f' ({money_rate(s)[1]})').pack()
  fee=ttk.Entry(w);fee.insert(0,edit_value(s,loan_fee(s,p)));fee.pack(padx=14,pady=4)
  ttk.Label(w,text=tr('Ödeyeceğin maaş payı','Your wage share')).pack()
  share=ttk.Combobox(w,state='readonly',values=('25%','50%','75%','100%'))
  share.current(1);share.pack(padx=14,pady=4)
  weekly=ttk.Label(w);weekly.pack(padx=14,pady=4)
  def refresh(_event=None):
   wage=state(s,p)['wage']*(share.current()+1)//4
   weekly.config(text=tr('Haftalık gider','Weekly cost')+' · '+money_text(s,wage))
  share.bind('<<ComboboxSelected>>',refresh);refresh()
  feedback=ttk.Label(w,wraplength=430);feedback.pack()
  def submit():
   try:amount=from_display(s,fee.get())
   except ValueError:feedback.config(text=self.reason('fee'));return
   ok,reason=loan_deal(s,pid,club,amount,25*(share.current()+1))
   if ok:
    w.destroy();self.autosave();self.loans_page()
   else:feedback.config(text=self.reason(reason))
  self.button(w,'Kiralama teklifini ilet','Submit loan offer',submit).pack(pady=8)
 def loans_page(self):
  self.clear();s=self.s;tr=self.tr;club=s['club']
  self.button(self.body,'Transfer merkezi','Transfer centre',self.market).pack(anchor='w')
  rows=[]
  for pid,loan in s.get('loans',{}).items():
   if club not in (loan['borrower'],loan['parent']):continue
   p=player(s,pid);wage=state(s,p)['wage'];borrower=wage*loan['share']//100
   rows.append((p['name'],loan['parent'],loan['borrower'],f"{loan['share']}%",
                money_text(s,borrower if club==loan['borrower'] else wage-borrower),s['year']+1))
  if not rows:ttk.Label(self.body,text=tr('Aktif kiralama yok.','No active loans.')).pack(anchor='w')
  self.tree([tr('Oyuncu','Player'),tr('Asıl kulüp','Parent club'),tr('Kiralayan','Borrower'),
             tr('Kiralayan maaş payı','Borrower wage share'),tr('Haftalık kulüp gideri','Weekly club cost'),
             tr('Dönüş sezonu','Return season')],rows,wide=True)
 def offers_page(self):
  s=self.s;tr=self.tr;self.clear()
  ttk.Label(self.body,text=tr('Gelen transfer teklifleri','Incoming transfer offers')).pack(anchor='w')
  entries=[(i,o) for i,o in enumerate(s['offers']) if o['seller']==s['club'] and o['status']=='open'
           and window(s) and o['year']==s['year'] and 0<=s['week']-o['week']<=2 and s['owners'].get(o['pid'])==s['club']]
  msg=self.management_text
  table=self.tree([msg(key) for key in ('player','buyer','fee','offer_wage','years','signing','role','status')],
                  [(player(s,o['pid'])['name'],o['buyer'],money_text(s,o['fee']),
                    money_text(s,o['wage']*o['share']//100 if o.get('kind')=='loan' else o['wage']),
                    tr('Sezon sonu','Season end') if o.get('kind')=='loan' else o['years'],money_text(s,o['signing']),
                    tr('Kiralama','Loan')+f" · {o['share']}%" if o.get('kind')=='loan' else msg(o['role']),
                    msg('open')) for _,o in entries],wide=True)
  for column,key in ((2,'fee'),(3,'wage'),(5,'signing')):
   values=[o['wage']*o['share']//100 if key=='wage' and o.get('kind')=='loan' else o[key] for _,o in entries]
   table.heading(column,command=lambda c=column,v=values:self.sort_tree(table,c,v))
  detail=ttk.Label(self.body,text=msg('compare_help' if entries else 'no_offers'),wraplength=880)
  detail.pack(anchor='w')
  def compare(_event):
   if not table.selection():return
   _,offer=entries[int(table.selection()[0])]
   p=player(s,offer['pid'])
   detail.configure(text=msg('incoming_preview',value=money_text(s,value(s,p)),
     current=money_text(s,state(s,p)['wage']),income=money_text(s,int(offer['fee']*.75)),
     fee=money_text(s,offer['fee'])))
  table.bind('<<TreeviewSelect>>',compare)
  def answer(choice):
   if not table.selection() or not s['employed']:return
   index,offer=entries[int(table.selection()[0])]
   amount=None
   if choice=='counter':
    label=tr('Karşı teklif','Counteroffer')
    prompt=f'{label} ({money_rate(s)[1]})'
    if s.get('match_model',0)==4:
     prompt+='\n'+tr('Kabul sınırı alıcının kadro ihtiyacına ve bütçesine bağlıdır.',
                      "The buyer's squad needs and budget determine what it can accept.")
    raw=simpledialog.askstring('Top Antrenörü',prompt,initialvalue=edit_value(s,offer['fee']),parent=self.r)
    if raw is not None:
     try:amount=from_display(s,raw)
     except ValueError:messagebox.showinfo('Top Antrenörü',self.reason('fee'));return
   if choice=='counter' and amount is None:return
   ok,reason=answer_offer(s,index,choice,amount)
   if ok or reason=='withdrawn':self.offers_page();self.autosave()
   if not ok:messagebox.showinfo('Top Antrenörü',self.reason(reason))
  bar=ttk.Frame(self.body);bar.pack()
  def decline_all():
   if reject_all(s):
    self.offers_page();self.autosave()
  self.button(bar,'Tümünü reddet','Reject all',decline_all).pack(side='right',padx=4)
  for label,en,choice in [('Kabul et','Accept','accept'),('Reddet','Reject','reject'),('Karşı teklif','Counter','counter')]:
   self.button(bar,label,en,lambda choice=choice:answer(choice)).pack(side='left',padx=4,pady=5)
 def jobs_page(self):
  if 'manager_state' in self.s:return self.employment_page()
  self.clear();s=self.s;tr=self.tr
  ttk.Label(self.body,text=f"{tr('Menajer itibarı','Manager reputation')}: {s['manager_rep']}").pack(anchor='w')
  if s['week']!=1:
   ttk.Label(self.body,text=tr('İş teklifleri sezonun ilk haftasında kabul edilir.','Job offers can be accepted in week one.')).pack(anchor='w')
  jobs=s['job_offers'][:]
  tree=self.tree([tr('İş teklifi','Job offer'),tr('Kulüp itibarı','Club reputation'),tr('Hedef sıra','Target rank')],
                 [(team,s['club_reputation'][team],s['board_targets'][team]) for team in jobs])
  def take():
   if tree.selection() and accept_job(s,jobs[int(tree.selection()[0])]):
    self.header();self.dashboard();self.autosave()
  def leave():
   if s['employed'] and messagebox.askyesno('Top Antrenörü',tr('Kulüpten istifa edilsin mi?','Resign from the club?')):
    resign(s);self.header();self.jobs_page();self.autosave()
  self.button(self.body,'Teklifi kabul et','Accept job',take).pack()
  if s['employed']:self.button(self.body,'İstifa et','Resign',leave).pack()
 def table(self):
  self.clear();rows=[]
  for t,z in sorted(self.s['teams'].items(),key=lambda q:(q[1]['p'],q[1]['gf']-q[1]['ga'],q[1]['gf']),reverse=True):rows.append((t,z['w']+z['d']+z['l'],z['w'],z['d'],z['l'],z['gf'],z['ga'],z['p']))
  table=self.tree([self.tr('Kulüp','Club'),'Pld','W','D','L','GF','GA','Pts'],rows)
  def open_club(_event=None):
   if table.selection():self.club_squad(rows[int(table.selection()[0])][0])
  table.bind('<Double-1>',open_club)
  self.button(self.body,*TEXT['club_squad'],open_club).pack(anchor='w')
 def club_squad(self,team):
  self.clear()
  msg=self.management_text
  players=roster(team,self.s['year'],self.s)
  ttk.Label(self.body,text=team).pack(anchor='w')
  table=self.tree([msg(k) for k in ('player','position','age','expiry')],
            [(p['name'],position_label(p['pos'],self.lang),age_at(p,self.s['year'],self.s['week']),
              state(self.s,p)['contract']) for p in players],wide=True)
  def profile(_event=None):
   if table.selection():self.profile(players[int(table.selection()[0])])
  table.bind('<Double-1>',profile)
  self.button(self.body,*TEXT['open_profile'],profile).pack(side='left')
  self.button(self.body,*TEXT['back_table'],self.table).pack(side='left',padx=6)
 def fixtures(self):
  self.clear();self.tree([self.tr('Ev sahibi','Home'),self.tr('Deplasman','Away'),self.tr('Hafta','Week'),self.tr('Sonuç','Result')],[(m['home'],m['away'],m['week'],f"{next(q for q in self.s['results'][m['week']-1] if q['home']==m['home'] and q['away']==m['away'])['x']} - {next(q for q in self.s['results'][m['week']-1] if q['home']==m['home'] and q['away']==m['away'])['y']}" if m['week']<self.s['week'] else '-') for i,m in enumerate(self.s['schedule'])])
 def archive(self):
  self.clear();rows=[]
  self.button(self.body,'Doğrulanmış 2000/01','Verified 2000/01',self.historical_results).pack(anchor='w')
  for h in self.s.get('history',[]):
   t,z=max(h['teams'].items(),key=lambda q:(q[1]['p'],q[1]['gf']-q[1]['ga'],q[1]['gf']));rows.append((str(h['year'])+'/'+str(h['year']+1)[-2:],t,z['p']))
  self.tree([self.tr('Sezon','Season'),self.tr('Şampiyon','Champion'),self.tr('Puan','Points')],rows)
 def historical_results(self):
  self.clear()
  tr=self.tr
  self.button(self.body,'Sezon arşivi','Season archive',self.archive).pack(anchor='w')
  self.tree([tr('Ev sahibi','Home'),tr('Deplasman','Away'),tr('Hafta','Week'),tr('TFF skoru','TFF score')],
            [(m['home'],m['away'],m['week'],f"{m['score'][0]}–{m['score'][1]}") for m in verified_results()])
 def scorers(self):
  self.clear();s=self.s;tr=self.tr
  histories={str(h['year']):h for h in s['history']}
  histories[str(s['year'])]=s
  seasons=list(reversed(histories))
  clubs={tr('Tüm kulüpler','All clubs'):None,**{team:team for team in TEAMS}}
  positions={tr('Tüm mevkiler','All positions'):None}
  positions.update({position_label(p['pos'],self.lang):p['pos'] for p in all_players(s)})
  filters=ttk.Frame(self.body);filters.pack(fill='x')
  year=tk.StringVar(value=seasons[0])
  club=tk.StringVar(value=next(iter(clubs)))
  position=tk.StringVar(value=next(iter(positions)))
  for var,values in ((year,seasons),(club,list(clubs)),(position,list(positions))):
   ttk.Combobox(filters,textvariable=var,values=values,state='readonly').pack(side='left',padx=3)
  note=ttk.Label(self.body);note.pack(anchor='w')
  columns=[tr('Oyuncu','Player'),tr('Kulüp','Club'),tr('Mevki','Position'),tr('Maç','Apps'),
           tr('İlk 11','Starts'),tr('Dakika','Minutes'),tr('Gol','Goals'),tr('Asist','Assists'),
           tr('Ort. puan','Avg rating'),tr('Maçın adamı','POTM'),tr('Sarı','Yellow'),
           tr('Kırmızı','Red'),tr('Kurtarış','Saves'),tr('Gol yemedi','Clean sheets')]
  grid=self.tree(columns,[])
  scroll=ttk.Scrollbar(grid.master,orient='horizontal',command=grid.xview)
  scroll.pack(side='bottom',fill='x',before=grid)
  grid.configure(xscrollcommand=scroll.set)
  for i in range(1,len(columns)):grid.column(i,width=82,minwidth=62,stretch=False)
  def refresh(*args):
   h=histories[year.get()]
   stats=h.get('season_stats',h.get('player_stats',{}))
   legacy=h.get('legacy_goals',h['goals'] if not stats else {})
   note.config(text=tr('Eski kayıtta ayrıntısı olmayan goller ayrıca gösterilir.',
                       'Goals without details from older saves are shown separately.') if legacy else '')
   target,role=clubs[club.get()],positions[position.get()]
   grid.delete(*grid.get_children())
   rows=[]
   for pid in sorted(set(stats)|set(legacy)):
    p=player(s,pid)
    if p is None or role and p['pos']!=role:continue
    records=stats.get(pid,{})
    selected=[(team,row) for team,row in records.items() if target is None or team==target]
    if not selected:
     if target is None and pid in legacy:
      rows.append((p['name'],'—',position_label(p['pos'],self.lang),'—','—','—',legacy[pid],*(['—']*7)))
     continue
    z=combine([row for _,row in selected])
    rows.append((p['name'],' / '.join(team for team,_ in selected),position_label(p['pos'],self.lang),
         z['apps'],z['starts'],z['minutes'],z['goals']+(legacy.get(pid,0) if target is None else 0),z['assists'],
         round(z['rating_sum']/10/z['rated'],2) if z['rated'] else '—',z['motm'],z['yellow'],z['red'],z['saves'],z['clean']))
   for i,row in enumerate(sorted(rows,key=lambda r:(-r[6],r[0]))):
    grid.insert('','end',iid=str(i),values=row)
  for var in (year,club,position):var.trace_add('write',refresh)
  refresh()
 def tactics(self):
  if 'manager_state' in self.s and not self.s['employed']:return self.employment_page()
  self.clear()
  s=self.s; msg=self.management_text
  bar=ttk.Frame(self.body);bar.pack(anchor='w',pady=6)
  formation=tk.StringVar(value=s['formation'])
  shape=ttk.Combobox(bar,textvariable=formation,values=tuple(LAYOUTS) if s.get('position_model') else FORMATIONS,state='readonly',width=10)
  ttk.Label(bar,text=msg('formation')).pack(side='left');shape.pack(side='left',padx=5)
  style=ttk.Combobox(bar,values=[msg(key) for key in STYLES],state='readonly',width=16)
  style.current(STYLES.index(s['style']));style.pack(side='left',padx=5)
  def set_formation(_event):
   s['formation']=formation.get()
   s.pop('manual_xi',None)
   s.pop('auto_xi',None)
   self.tactics()
  shape.bind('<<ComboboxSelected>>',set_formation)
  style.bind('<<ComboboxSelected>>',lambda _e:s.update(style=STYLES[style.current()]))
  ttk.Label(self.body,text=msg('xi_help'),wraplength=850).pack(anchor='w')
  slots=select_slots(s,s['club'])
  roles=match_positions(s,s['club'])
  detailed=s.get('position_model')
  if detailed:
   by_role={}
   for role,pid in slots:by_role.setdefault(role,[]).append(pid)
   current=[by_role[role].pop(0) if by_role.get(role) else None for role in roles]
   pitch=tk.Canvas(self.body,width=930,height=255,bg=THEME['field'],highlightthickness=0)
   pitch.create_rectangle(8,8,922,247,outline='#e1f1e3',width=2)
   pitch.create_line(465,8,465,247,fill='#e1f1e3')
   pitch.create_oval(420,84,510,174,outline='#e1f1e3')
   points=list(coordinates(roles))
  else:
   current=[pid for _,pid in slots]+[None]*max(0,11-len(slots))
   style_frame=ttk.Frame(self.body);style_frame.pack(anchor='w',pady=4)
  current=s.get('manual_xi',current)
  squad=[p for p in roster(s['club'],s['year'],s) if eligible(s,p)]
  selectors=[]
  for i,role in enumerate(roles):
   if detailed:
    options=sorted((p for p in squad if (role=='GK')==(p['pos']=='GK')),
                   key=lambda p:(-fit_level(p,role),p['name']))
    choices={f"{p['name']} · {p['id']} [{fit_level(p,role)}]":p['id'] for p in options}
    x,y=points[i];y*=.75
    pitch.create_text(x,y-20,text=detail_position(role,self.lang),fill='white',font=(FONT,9,'bold'))
    box=ttk.Combobox(pitch,values=['',*choices],state='readonly',width=17)
    pitch.create_window(x,y,window=box)
   else:
    choices={f"{p['name']} · {p['id']}":p['id'] for p in squad if fits(p,role)}
    ttk.Label(style_frame,text=position_label(role,self.lang)).grid(row=i%6,column=(i//6)*2,sticky='w')
    box=ttk.Combobox(style_frame,values=['',*choices],state='readonly',width=32)
    box.grid(row=i%6,column=(i//6)*2+1,padx=6,pady=2)
   box.set(next((name for name,pid in choices.items() if pid==current[i]), ''))
   selectors.append((box,choices))
  if detailed:
   ttk.Label(self.body,text=' · '.join(f'{i} {text[self.lang=="EN"]}' for i,text in enumerate(FIT_NAMES)),
             wraplength=885).pack(anchor='w')
  status=ttk.Label(self.body,text=msg('manual_active' if manual_slots(s,s['club'],s.get('manual_xi',[]))
                                         else 'auto_active' if s.get('auto_xi') else 'xi_unconfirmed'))
  status.pack(anchor='w')
  def apply():
   if not s['employed']:return
   ids=[choices.get(box.get()) for box,choices in selectors]
   if not manual_slots(s,s['club'],ids):
    status.configure(text=msg('invalid_xi'));return
   s['manual_xi']=ids
   s.pop('auto_xi',None)
   status.configure(text=msg('manual_active' if all(suitable(s,player(s,pid),r) for r,pid in zip(roles,ids)) else 'position_warning'))
  def automatic():
   s.pop('manual_xi',None)
   s['selected']=[]
   s['auto_xi']=True
   self.tactics()
  buttons=ttk.Frame(self.body);buttons.pack(anchor='w')
  self.button(buttons,*TEXT['apply_xi'],apply).pack(side='left')
  self.button(buttons,*TEXT['auto_xi'],automatic).pack(side='left',padx=6)
  if s.get('match_model') in (3,4):
   self.button(buttons,'Duran Toplar','Set pieces',self.set_piece_page).pack(side='left',padx=5)
  if s.get('tactics_model'):
   self.button(buttons,'Taktik planı','Tactical plan',self.tactical_plan_page).pack(side='left',padx=5)
  if detailed:pitch.pack(anchor='w')
 def calendar_text(self):
  from datetime import date,timedelta
  s=self.s; msg=self.management_text
  round_number=min(34,s['week']) if s.get('match_model') else 1
  fixture=next(m for m in s['schedule'] if m['week']==round_number and s['club'] in (m['home'],m['away']))
  periods=', '.join(f'{a}–{b}' for a,b in TRANSFER_PERIODS)
  week=s['week']
  day=date(s['year'],8,1)+timedelta(weeks=min(34,week)-1)
  historic=opening_date(s['year'],fixture) if round_number==1 else None
  if s.get('match_model') and 1<week<=34:
   text=self.tr('Hafta {week} · {date} · Sıradaki maç {home} – {away} · Transfer {status}',
                'Week {week} · {date} · Next match {home} – {away} · Transfer {status}')
   return text.format(week=week,date=day.isoformat(),home=fixture['home'],away=fixture['away'],
                      status=msg('open' if window(s) else 'closed'))
  return msg('calendar',date=day.isoformat(),week=week,home=fixture['home'],away=fixture['away'],
             periods=periods,status=msg('open' if window(s) else 'closed')) + (
                '\n'+msg('historic_opening',date=historic) if historic else '')
 def confirm_lineup(self):
  s=self.s
  if not s['employed']:return True
  slots=select_slots(s,s['club'])
  squad={p['id']:p for p in roster(s['club'],s['year'],s)}
  fallback=len(slots)!=11 or any(not suitable(s,squad[pid],role) for role,pid in slots)
  invalid='manual_xi' in s and not manual_slots(s,s['club'],s['manual_xi'])
  complete_keeper=bool(slots and squad[slots[0][1]]['pos']=='GK' and len(slots)==11)
  if s.get('auto_xi') and not invalid and 'manual_xi' not in s and complete_keeper:
   return True
  if not (fallback or invalid or not (s.get('auto_xi') or 'manual_xi' in s)):
   return True
  msg=self.management_text
  key='xi_warning_manual' if fallback and 'manual_xi' in s and not invalid else 'xi_warning_short' if fallback else 'xi_warning'
  if not messagebox.askyesno('Top Antrenörü',msg(key,count=len(slots)),parent=self.r):
   self.tactics()
   return False
  if invalid:
   s.pop('manual_xi',None)
  s['auto_xi']=True
  return True
 def finance_page(self):
  self.clear();s=self.s;tr=self.tr
  self.button(self.body,'Transfer merkezi','Transfer centre',self.market).pack(anchor='w')
  row=s['finance'][s['club']]
  history=[r for r in s.get('world_history',[]) if s['club'] in r['finance']]
  if history:
   self.button(self.body,'Sezon geçmişi','Season history',lambda:self.finance_history(history)).pack(anchor='w')
  ttk.Label(self.body,text=self.tr('Transfer bütçesi','Transfer budget')+' '+money_text(s,row['transfer_budget'])
   +' · '+self.tr('Haftalık maaş bütçesi','Weekly wage budget')+' '+money_text(s,row['wage_budget'])).pack(anchor='w')
  if s.get('transfer_model'):
   outgoing,incoming=commitments(s,s['club'])
   ttk.Label(self.body,text=tr('Ödenecek / alınacak taksitler','Installments payable / receivable')
    +' · '+money_text(s,outgoing)+' / '+money_text(s,incoming)).pack(anchor='w')
   due=Counter()
   for _,week,buyer,_,amount in s.get('transfer_payments',[]):
    if buyer==s['club']:due[week]+=amount
   if due:
    week=min(due)
    ttk.Label(self.body,text=tr('Sonraki ödeme','Next payment')+f' · {week} · '+money_text(s,due[week])).pack(anchor='w')
  if s.get('economy_model'):
   plan=projection(s,s['club'])
   ttk.Label(self.body,text=self.management_text('financial_plan',
    closing=money_text(s,plan['closing']),reserve=money_text(s,plan['reserve'])),wraplength=830).pack(anchor='w')
   weekly=self.tr('Haftalık gelir tahmini','Projected weekly income')
   wages=self.tr('Futbolcu / teknik ekip / idari maaş','Player wages / staff / administration')
   ttk.Label(self.body,text=f"{weekly} {money_text(s,plan['weekly_income'])} · {wages} "+
      ' / '.join(money_text(s,plan[key]) for key in ('wages','staff','admin')),wraplength=840).pack(anchor='w')
   if plan['closing']<plan['reserve'] or plan['wages']>=plan['wage_room']:
    ttk.Label(self.body,style='Warning.TLabel',text=self.management_text('financial_limit')).pack(anchor='w')
  entries=[
   ('cash','Nakit','Cash'),('debt','Borç','Debt'),('tickets','Bilet','Match tickets'),
   ('season_tickets','Kombine','Season tickets'),('broadcast','Yayın','Broadcast'),
   ('sponsors','Sponsorluk','Sponsors'),('commercial','Ticari gelir','Commercial revenue'),('prize','Lig ödülü','Prize money'),
   ('fees_received','Gelen bonservis','Fees received'),('wages_paid','Oyuncu maaşı','Player wages'),
   ('staff','Personel','Staff'),('academy','Altyapı','Academy'),('maintenance','Bakım','Maintenance'),
   ('investment','Tesis yatırımı','Facilities investment'),('bonuses','Prim','Bonuses'),
   ('fees_paid','Giden bonservis','Fees paid'),('signing_paid','İmza parası','Signing fees'),
   ('interest','Faiz','Interest'),('borrowed','Borçlanma','Borrowed'),('repaid','Borç geri ödeme','Principal repaid')]
  self.tree([tr('Mali kalem','Financial item'),money_rate(s)[1]],[(tr(a,b),edit_value(s,row[k])) for k,a,b in entries if k in row])
 def finance_history(self,history):
  self.clear()
  self.button(self.body,'Finans','Finance',self.finance_page).pack(anchor='w')
  tr=self.tr
  def values(record):
   row=record['finance'][self.s['club']]
   income=sum(row.get(k,0) for k in ('tickets','season_tickets','broadcast','sponsors','commercial','prize','fees_received'))
   expenses=sum(row.get(k,0) for k in ('wages_paid','operating_paid','bonuses','investment','fees_paid','signing_paid'))
   return (record['year'],*(money_text(dict(self.s,year=record['year']),v) for v in
       (income,expenses,row['wages_paid'],row['fees_paid'],row['cash'],row['debt'])))
  self.tree([tr('Sezon','Season'),tr('Gelir','Income'),tr('Gider','Expenses'),tr('Maaş','Wages'),
             tr('Bonservis','Fees'),tr('Nakit','Cash'),tr('Borç','Debt')],
            [values(record) for record in reversed(history[-15:])],wide=True)
 def commentary(self,event,teams):
  n,side,pid,kind,other=event
  name=player(self.s,pid)['name']
  labels={
   'goal':self.tr('Gol','Goal'),
   'wide':self.tr('Şut dışarıda','Shot wide'),
   'on_target':self.tr('İsabetli şut','Shot on target'),
   'saved':self.tr('Kurtarış','Save'),
   'sub':self.tr('Oyuncu değişikliği','Substitution'),
   'pass':self.tr('Pas','Pass') if self.s.get('match_model') in (2,3,4) else self.tr('Şut pası','Pass before shot'),
   'kickoff':self.tr('Santra','Kick-off'),
   'throw':self.tr('Taç','Throw-in'),
   'corner':self.tr('Korner','Corner'),
   'freekick':self.tr('Serbest vuruş','Free kick'),
   'penalty':self.tr('Penaltı','Penalty'),
   'goal_kick':self.tr('Kale vuruşu','Goal kick'),
   'offside':self.tr('Ofsayt','Offside'),
   'foul':self.tr('Faul','Foul'),
   'advantage':self.tr('Avantaj','Advantage'),
   'second_yellow':self.tr('İkinci sarı','Second yellow'),
   'indirect':self.tr('Endirekt serbest vuruş','Indirect free kick'),
   'rebound':self.tr('Kaleciden döndü','Parried by goalkeeper'),
   'clearance':self.tr('Uzaklaştırma','Clearance'),
   'header':self.tr('Kafa vuruşu','Header'),
   'throw_awarded':self.tr('Top taça çıktı','Ball out for throw-in'),
   'set_piece_goal':self.tr('Duran top golü','Set-piece goal'),
   'blocked':self.tr('Şut bloklandı','Shot blocked'),
   'pass_failed':self.tr('Pas başarısız','Pass unsuccessful'),
   'tackle':self.tr('Top kazanıldı','Ball recovered'),
   'yellow':self.tr('Sarı kart','Yellow card'),
   'red':self.tr('Kırmızı kart','Red card'),
  }
  secondary=f" / {player(self.s,other)['name']}" if other else ''
  return f"{n}′ {labels[kind]} · {name}{secondary} ({teams[side]})"
 def match_numbers(self,shots,on_target,saves):
  return (f"{self.tr('Şut','Shots')} {shots[0]}–{shots[1]}   "
          f"{self.tr('İsabet','On target')} {on_target[0]}–{on_target[1]}   "
          f"{self.tr('Kurtarış','Saves')} {saves[0]}–{saves[1]}")
 def shot_label(self,action):
  return {
   'shot':self.tr('Şut','Shot'), 'goal':self.tr('Gol','Goal'),
   'saved':self.tr('Kurtarış','Save'), 'wide':self.tr('Dışarı','Wide'),
   'blocked':self.tr('Blok','Blocked'), 'on_target':self.tr('İsabetli şut','On target'),
  }.get(action,'')
 def report(self,match,parent=None,review=None):
  w=tk.Toplevel(parent or self.r);w.title(self.tr('Maç raporu','Match report'))
  w.geometry('650x560')
  f=ttk.Frame(w,padding=12);f.pack(fill='both',expand=True)
  home,away=match['home'],match['away']
  ttk.Label(f,text=f"{home} {match['x']}–{match['y']} {away}").pack(anchor='w')
  if review:
   for team,row in zip((home,away),review['opening']):
    ttk.Label(f,text=self.management_text('opening_review',team=team,formation=row['formation'],
     strengths=' / '.join(f"{row['strengths'][role]:.1f}" for role in ('GK','D','M','F')),
     fitness=row['fitness'],mismatches=row['mismatches']),wraplength=615).pack(anchor='w')
  if 'play' not in match:
   ttk.Label(f,text=self.tr('Bu kayıt ayrıntılı maç verisi içermiyor.','This save has no detailed match data.')).pack(anchor='w')
  else:
   ttk.Label(f,text=self.match_numbers(match['shots'],match['on_target'],match['saves'])).pack(anchor='w')
  tabs=ttk.Notebook(f);tabs.pack(fill='both',expand=True,pady=6)
  log=tk.Listbox(tabs);tabs.add(log,text=self.tr('Olaylar','Events'))
  for event in match.get('play',[]):log.insert('end',self.commentary(event,(home,away)))
  if review and review.get('analysis'):
   breakdown=ttk.Frame(tabs)
   tabs.add(breakdown,text=self.tr('Taktik analizi','Tactical review'))
   audit=tk.Listbox(breakdown,bg=THEME['row'],fg=THEME['text'],font=(FONT,10),selectbackground=THEME['action'])
   scroll=ttk.Scrollbar(breakdown,command=audit.yview)
   audit.configure(yscrollcommand=scroll.set)
   scroll.pack(side='right',fill='y');audit.pack(fill='both',expand=True)
   data=review['analysis']
   keys={key:self.tr(*option[:2]) for key,option in TACTICAL_OPTIONS.items()}
   keys['style']=self.tr('Yaklaşım','Approach')
   for minute,side,key,old,value in data['decisions']:
    def label(v):
     if key=='style' and v in STYLES:return self.management_text(v)
     if key in TACTICAL_OPTIONS and type(v) is int and -1<=v<=1:
      return TACTICAL_OPTIONS[key][2 if self.lang=='TR' else 3][v+1]
     return str(v)
    effective=minute+(1 if self.s.get('match_model') in (2,3,4) else 5)
    audit.insert('end',f"{minute}′ → {effective}′ · {(home,away)[side]} · {keys[key]} {label(old)} → {label(value)}")
   role_changes=data.get('role_changes',[])
   for minute,side,pid,old,new in role_changes:
    name=player(self.s,pid)['name']
    audit.insert('end',f"{minute}′ → {minute+1}′ · {(home,away)[side]} · {name} · {self.tr(*TACTICAL_ROLES[old][:2])} → {self.tr(*TACTICAL_ROLES[new][:2])}")
   if 'advanced_regains' in data:
    a,b=data['advanced_regains']
    audit.insert('end',f"{self.tr('İleri bölgede top kazanma','Advanced recoveries')} · {a}–{b}")
   changes={row[0] for row in data['decisions']} | {row[0] for row in role_changes}
   if changes and 'play' in match:
    audit.insert('end',self.tr('Müdahale çevresi · Şut (isabet) · Ev–dep',
                              'Around changes · Shots (on target) · Home–away'))
    audit.insert('end',self.tr('İlk dakika talimat, ikinci dakika motor adımı. Ölçümler nedensellik göstermez.',
                              'First minute is the order, second is the engine step. These figures do not establish causation.'))
    for minute in sorted(changes):
     first,last=max(1,minute-4),min(90,minute+5)
     def attempts(start,end):
      shots=[0,0];target=[0,0];passes=[0,0];completed=[0,0]
      for tick,side,_,event,_ in match['play']:
       if start<=tick<=end:
        if event in SHOT_EVENTS:
         shots[side]+=1;target[side]+=event not in ('wide','blocked')
        if event in ('pass','pass_failed'):
         passes[side]+=1;completed[side]+=event=='pass'
      return ('–'.join(f'{a} ({b})' for a,b in zip(shots,target))
              +' · '+self.tr('Pas','Passes')+' '+'–'.join(f'{a}/{b}' for a,b in zip(completed,passes)))
     before=f'{first}–{minute}′ {attempts(first,minute)}' if minute else '—'
     audit.insert('end',f"{minute}′ · {before}  →  {minute+1}–{last}′ {attempts(minute+1,last)}")
   metrics=self.tr('Dakika · Şut · Duran hücum · Yük','Minute · Shots · Stopped attacks · Load')
   if 'flow' in data:
    flow=data['flow']
    for label,key in ((self.tr('Topa sahip dakika','Possession minutes'),'possession'),
                     (self.tr('Pas denemesi','Pass attempts'),'passes'),
                     (self.tr('İsabetli pas','Completed passes'),'completed'),
                     (self.tr('Top kazanma','Recoveries'),'recoveries')):
     a,b=flow[key];audit.insert('end',f'{label} · {a}–{b}')
    metrics=self.tr('Dakika · Şut · Top kazanma · Yük','Minute · Shots · Recoveries · Load')
   if 'zones' in data:
    audit.insert('end',self.tr('Topa sahip olunan adımlar · Savunma / orta / hücum üçte biri',
                              'Possession steps · Defensive / middle / attacking third'))
    for team,zones in zip((home,away),data['zones']):
     audit.insert('end',team+' · '+' / '.join(map(str,zones)))
   if self.s.get('match_model') in (3,4):
    events=Counter(row[3] for row in match.get('play',[]))
    labels=(('foul','Faul','Foul'),('offside','Ofsayt','Offside'),('corner','Korner','Corner'),
            ('penalty','Penaltı','Penalty'),('throw','Taç','Throw-in'),
            ('yellow','Sarı kart','Yellow card'),('red','Kırmızı kart','Red card'),
            ('sub','Değişiklik','Substitution'),('set_piece_goal','Duran top golü','Set-piece goal'))
    audit.insert('end',' · '.join(f'{self.tr(a,b)} {events[key]}' for key,a,b in labels))
   audit.insert('end',metrics)
   for minute,shots,won,load,_ in data['periods']:
    audit.insert('end',f"{minute:02d}′ · {shots[0]}:{shots[1]} · {won[0]}:{won[1]} · {load[0]}:{load[1]}")
   if 'chances' in data:
    chances=ttk.Treeview(tabs,columns=('minute','player','zone','result'),show='headings')
    tabs.add(chances,text=self.tr('Pozisyonlar','Chances'))
    for column,title,width in (
      ('minute',self.tr('Dakika','Minute'),50),('player',self.tr('Oyuncu / takım','Player / team'),290),
      ('zone',self.tr('Kaleye mesafe','Distance to goal'),110),('result',self.tr('Sonuç','Outcome'),100)):
     chances.heading(column,text=title);chances.column(column,width=width)
    for minute,side,pid,outcome,x,y in data['chances']:
     distance=round(math.hypot((1-x if side==0 else x)*105,(y-.5)*68))
     chances.insert('','end',values=(f'{minute}′',f"{player(self.s,pid)['name']} · {(home,away)[side]}",
                                     f'{distance} m',self.shot_label(outcome)))
  scorer_tab=ttk.Frame(tabs)
  tabs.add(scorer_tab,text=self.management_text('scorers_link'))
  scorers=tk.Listbox(scorer_tab);scorers.pack(fill='both',expand=True)
  ids=[]
  for minute,team,pid in match['events']:
   p=player(self.s,pid)
   if p:
    ids.append(pid);scorers.insert('end',f"{minute}′ {p['name']} · {team}")
  def scorer_profile(_event=None):
   if scorers.curselection():self.profile(player(self.s,ids[scorers.curselection()[0]]))
  scorers.bind('<Double-1>',scorer_profile)
  self.button(scorer_tab,*TEXT['open_profile'],scorer_profile).pack(anchor='w')
  log.bind('<Double-1>',lambda _e:self.profile(player(self.s,match['play'][log.curselection()[0]][2]))
           if log.curselection() else None)
  goals=Counter(row[2] for row in match['events'])
  assists=Counter(row[2] for row in match.get('assists',[]))
  shots=Counter(row[2] for row in match.get('play',[]) if row[3] in SHOT_EVENTS)
  saves=Counter(row[4] for row in match.get('play',[]) if row[3]=='saved')
  marks=ttk.Treeview(tabs,columns=('name','minute','rating','goals','assists','shots','saves'),show='headings')
  tabs.add(marks,text=self.tr('Oyuncu puanları','Player ratings'))
  for column,title in [('name',self.tr('Oyuncu','Player')),('minute',self.tr('Dakika','Minutes')),
                       ('rating',self.tr('Puan','Rating')),('goals',self.tr('Gol','Goals')),
                       ('assists',self.tr('Asist','Assists')),('shots',self.tr('Şut','Shots')),
                       ('saves',self.tr('Kurtarış','Saves'))]:
   marks.heading(column,text=title);marks.column(column,width=215 if column=='name' else 62)
  for pid,rating in sorted(match.get('ratings',{}).items(),key=lambda row:(-row[1],player(self.s,row[0])['name'])):
   marks.insert('','end',values=(player(self.s,pid)['name'],match['minutes'][pid],rating,
                                 goals[pid],assists[pid],shots[pid],saves[pid]))
 def instruction_level(self,value):
  levels=(self.tr('Düşük','Low'),self.tr('Normal','Normal'),self.tr('Yüksek','High'))
  return levels[value+1] if type(value) is int and -1<=value<=1 else str(value)
 def last_report(self):
  s=self.s
  if s['results']:
   match=next(m for m in s['results'][-1] if s['club'] in (m['home'],m['away']))
   review=s.get('last_tactical_review')
   if review and (review['year'],review['week'],review['home'],review['away'])!=(s['year'],s['week']-1,match['home'],match['away']):review=None
   self.report(match,review=review)
 def live(self):
  s=self.s;m=LiveMatch(s)
  w=tk.Toplevel(self.r);w.title(self.tr('Maç merkezi','Match centre'))
  width=min(1500,max(850,self.r.winfo_width()-35))
  height=min(900,max(550,self.r.winfo_height()-58))
  width=min(width,self.r.winfo_screenwidth()-40)
  height=min(height,self.r.winfo_screenheight()-80)
  x=max(0,min(self.r.winfo_rootx(),self.r.winfo_screenwidth()-width-20))
  y=max(0,min(self.r.winfo_rooty(),self.r.winfo_screenheight()-height-60))
  w.geometry(f'{width}x{height}+{x}+{y}');w.minsize(760,440);w.transient(self.r);w.grab_set()
  f=ttk.Frame(w,padding=10);f.pack(fill='both',expand=True)
  header=ttk.Frame(f);header.pack(fill='x')
  score=ttk.Label(header,style='Title.TLabel')
  score.pack(pady=2)
  names=ttk.Frame(header);names.pack()
  for team,color in zip((m.a,m.b),('#44dfce','#ff9c63')):
   tk.Label(names,text=team,bg=THEME['panel'],fg=color,font=(FONT,10,'bold')).pack(side='left',padx=8)
  live_status=ttk.Label(header);live_status.pack()
  bar=ttk.Frame(f);bar.pack(side='top',fill='x',pady=(5,0))
  style=tk.StringVar(value=m.style)
  cb=ttk.Combobox(bar,textvariable=style,values=['Balanced','Attack','Defend'],state='readonly',width=13)
  cb.bind('<<ComboboxSelected>>',lambda _:setattr(m,'style',style.get()))
  stage=ttk.Panedwindow(f,orient='horizontal')
  stage.pack(fill='both',expand=True)
  field=ttk.Frame(stage);stage.add(field,weight=5)
  pitch=tk.Canvas(field,bg=THEME['field'],width=620,height=270,highlightthickness=0)
  pitch.pack(fill='both',expand=True)
  sidebar=ttk.Notebook(stage,width=206);stage.add(sidebar,weight=2)
  event_box=ttk.Frame(sidebar);sidebar.add(event_box,text=self.tr('Olaylar','Events'))
  stats_box=ttk.Frame(sidebar,padding=10);sidebar.add(stats_box,text=self.tr('İstatistik','Statistics'))
  log=tk.Text(event_box,bg=THEME['base'],fg=THEME['text'],width=22,wrap='word',
              padx=8,pady=6,font=(FONT,10),relief='flat',state='disabled')
  yscroll=ttk.Scrollbar(event_box,command=log.yview)
  log.configure(yscrollcommand=yscroll.set)
  log.tag_configure('critical',foreground=THEME['accent'])
  log.tag_configure('decision',foreground=THEME['warning'])
  key_events=SHOT_EVENTS | {'yellow','red','second_yellow','offside','foul','advantage',
              'corner','penalty','freekick','indirect','throw','rebound'}
  applied=ttk.Label(f,style='Warning.TLabel',wraplength=700)
  applied.pack(before=stage,side='top',anchor='w')
  caption=ttk.Label(f,wraplength=700)
  caption.pack(before=stage,side='top',anchor='w')
  def pending_orders(issued):
   return sum(row[0]==issued and row[1]==m.human
              for key in ('decisions','role_changes') for row in m.analysis.get(key,()))
  def requested():
   if not pending_orders(m.minute):
    applied.configure(text=self.tr('Bekleyen talimat yok','No pending orders'))
    return
   effective=m.minute+(1 if m.positional else 5)
   applied.configure(text=self.tr('Talimat {issued}′ · Uygulama {effective}′ bekleniyor',
                                  'Order {issued}′ · Awaiting {effective}′').format(
                                     issued=m.minute,effective=effective))
  def advance_minute():
   issued=m.minute
   changes=pending_orders(issued)
   m.step()
   if changes:
    applied.configure(text=self.tr('Talimat {issued}′ · Uygulandı {effective}′ ({count})',
                                   'Order {issued}′ · Applied {effective}′ ({count})').format(
                                      issued=issued,effective=m.minute,count=changes))
  def change(key,value):
   if m.instruction(key,value):
    requested()
  yscroll.pack(side='right',fill='y');log.pack(fill='both',expand=True)
  stats=ttk.Label(stats_box,wraplength=200);stats.pack(anchor='w')
  renderer=Pitch(pitch,lambda pid:m.s.get('numbers',{}).get(pid,player(m.s,pid)['number']),
                 lambda pid:player(m.s,pid)['name'])
  spatial=s.get('match_model') in (1,2,3,4)
  m.capture=spatial and s.get('match_mode')=='2d'
  if spatial and not m.capture:stage.forget(field)
  frames=deque()
  important=tk.BooleanVar(value=True)
  if m.capture:
   ttk.Checkbutton(field,text=self.tr('Önemli anlar','Highlights'),variable=important).pack(
       before=pitch,side='bottom',anchor='w')
  sound=tk.BooleanVar(value=False)
  if m.rules:
   ttk.Checkbutton(bar,text=self.tr('Ses','Sound'),variable=sound)
  if spatial:
   tactical=ttk.Frame(f);tactical.pack(before=applied,side='top',fill='x')
   for key,tr_name,en_name in [('press','Pres','Press'),('tempo','Tempo','Tempo'),('width','Genişlik','Width')]:
    ttk.Label(tactical,text=self.tr(tr_name,en_name)).pack(side='left',padx=4)
    control=ttk.Combobox(tactical,values=[self.tr('Düşük','Low'),self.tr('Normal','Normal'),self.tr('Yüksek','High')],state='readonly',width=8)
    control.current(m.instructions[m.human][('press','tempo','width').index(key)]+1);control.pack(side='left')
    control.bind('<<ComboboxSelected>>',lambda _,key=key,c=control:change(key,c.current()-1))
   cb.configure(values=[self.management_text(key) for key in STYLES])
   cb.current(STYLES.index(m.style))
   cb.bind('<<ComboboxSelected>>',lambda _:change('style',STYLES[cb.current()]))
  rating_line=ttk.Label(stats_box,wraplength=200);rating_line.pack(anchor='w',pady=8)
  frame_delay=55
  def show_score(minute,pair=None,action=None):
   home,away=shown if pair is None else pair
   label=f'{home} – {away}    {minute}′'
   if action:label+=f' · {self.shot_label(action)}'
   if score.cget('text')!=label:score.configure(text=label)
  def draw(frame):
   nonlocal frame_delay
   meta=frame[4] if len(frame)>4 else {}
   action=meta.get('action')
   frame_delay=780 if action in SHOT_EVENTS else 55
   renderer.draw(frame)
   show_score(frame[0],meta.get('score'),action)
   if action in SHOT_EVENTS:
    caption.configure(text=f'{frame[0]}′ · {self.shot_label(action)}')
   if 'delivery' in meta:
    passer,receiver=(player(m.s,pid)['name'] for pid in meta['delivery'])
    caption.configure(text=f"{frame[0]}′ · {self.tr('Pas','Pass')} · {passer} → {receiver}")
   if action=='goal' and sound.get():w.bell()
  shown_log=None
  shown=[0,0]
  def refresh():
   shown[:]=m.score
   show_score(m.minute)
   on_target,saves,ratings=m.detail()
   totals=self.match_numbers(m.shots,on_target,saves)
   if m.positional:
    flow=m.pitch.summary()
    pairs=[(self.tr('Topa sahip dakika','Possession minutes'),flow['possession']),
           (self.tr('İsabetli pas','Completed passes'),flow['completed']),
           (self.tr('Top kazanma','Recoveries'),flow['recoveries'])]
    totals+='\n\n'+'\n'.join(f'{key} · {a}–{b}' for key,(a,b) in pairs)
   if m.rules:
    totals+=f"\n\n{self.tr('Hakem profili','Referee profile')} {m.pitch.referee.identity}"
   if m.tactical_ai and m.human is not None:
    rival=1-m.human
    press,tempo,_=m.instructions[rival]
    totals+=f"\n\n{self.tr('Rakip taktikleri','Opposition tactics')}\n"
    totals+=f"{self.management_text(m.styles[rival])} · {self.tr('Pres','Press')} {self.instruction_level(press)}\n"
    totals+=f"Tempo {self.instruction_level(tempo)}"
   stats.configure(text=totals)
   nonlocal shown_log
   current_log=m.play[-35:]
   if current_log:
    caption.configure(text=self.commentary(current_log[-1],(m.a,m.b)))
   if current_log!=shown_log:
    shown_log=current_log
    log.configure(state='normal')
    log.delete('1.0','end')
    if not current_log:log.insert('end',self.tr('Henüz kayıtlı olay yok','No recorded events yet'))
    for event in reversed(current_log):
     kind=event[3]
     tag='decision' if kind in ('foul','offside','yellow','second_yellow','red') else 'critical' if kind in key_events else ()
     log.insert('end',self.commentary(event,(m.a,m.b))+'\n\n',tag)
    log.configure(state='disabled')
   if ratings:
    best=max(ratings,key=ratings.get)
    rating_line.config(text=f"{self.tr('Öne çıkan','Top rated')} · {player(self.s,best)['name']} {ratings[best]:.1f}")
  def complete():
   pause()
   m.commit()
   w.destroy()
   self.header()
   (self.inbox_page if spatial else self.dashboard)()
   self.autosave()
  def drain():
   draw(frames.popleft())
   if not frames:
    refresh()
    if m.minute==90:complete()
  def tick():
   if frames:
    drain()
    return
   if m.minute==90:
    complete()
    return
   before=len(m.play)
   advance_minute()
   events={row[3] for row in m.play[before:]}
   audible={'offside','foul','penalty'}
   if not (m.tactical_ai and m.capture):audible.add('goal')
   if m.rules and sound.get() and events & audible:w.bell()
   if m.capture and m.frames:
    if not important.get() or events & key_events:
     previous=renderer.last
     if m.tactical_ai and previous:
      frames.extend(interpolate([previous,*m.frames],bridge=True)[1:])
     else:
      frames.extend(interpolate(m.frames))
    else:frames.append(m.frames[-1])
    drain()
   else:
    refresh()
    if m.minute==90:complete()
  running=False;timer=None;fast=False;speed=tk.StringVar(value='2x')
  def status():
   label=(self.tr('Hızlı simülasyon','Fast simulation') if fast else self.tr('Oynuyor','Playing')
          if running else self.tr('Duraklatıldı','Paused'))
   live_status.configure(text=f'{label} · {speed.get()}')
  speed.trace_add('write',lambda *_:status())
  status()
  def pause():
   nonlocal running,timer,fast
   running=False;fast=False
   status()
   if timer is not None:w.after_cancel(timer);timer=None
  def cancel_on_destroy(event):
   if event.widget is w and timer is not None:w.after_cancel(timer)
  w.bind('<Destroy>',cancel_on_destroy)
  def auto():
   nonlocal timer
   timer=None
   if not running:return
   tick()
   if running:timer=w.after((frame_delay if frames else 750)//int(speed.get()[0]),auto)
  def start():
   nonlocal running
   if not running and not fast:running=True;status();auto()
  def batch():
   nonlocal timer
   timer=None
   if not fast:return
   capture=m.capture
   m.capture=False
   try:
    for _ in range(8 if m.positional else 3):
     if m.minute==90:break
     advance_minute()
   finally:
    m.capture=capture
   refresh()
   if m.minute==90:complete()
   else:timer=w.after_idle(batch)
  def finish():
   nonlocal fast,timer
   pause()
   if m.positional and not messagebox.askyesno(self.tr('Maçı tamamla','Complete match'),
        self.tr('Kalan süre mevcut taktiklerle simüle edilsin mi?',
                'Simulate the remaining time with the current tactics?'),parent=w):
    return
   frames.clear()
   fast=True;status()
   timer=w.after_idle(batch)
  def single():pause();tick()
  def sub():
   _,_,ratings=m.detail()
   positions={pid:role for side in m.slots for role,pid in side}
   def sub_label(p):
    pid=p['id']; played=m.minutes.get(pid,0)
    condition=round(m.player_condition(pid)) if m.tactical_ai else max(0,round(state(m.s,p)['condition']-played*20/90))
    actual=positions.get(pid,p['pos'])
    label=detail_position(actual,self.lang) if actual in POSITION_NAMES else position_code(actual,self.lang)
    return f"{label} · {p['name']} · {self.tr('Kond.','Fit.')} {condition}% · {self.tr('Puan','Rating')} {ratings.get(pid,'—')}"
   pause()
   side=int(s['club']==m.b)
   ls=m.la if side==0 else m.lb
   bench=[p for p in roster(s['club'],s['year'],m.s) if p['id'] not in m.used and eligible(m.s,p)]
   d=tk.Toplevel(w);d.title(self.tr('Oyuncu değişikliği','Substitution'))
   remaining=3-(m.team_subs[side] if m.positional else m.subs)
   ttk.Label(d,text=f"{self.tr('Kalan değişiklik','Substitutions remaining')} · {remaining}").pack(pady=(8,0))
   a=ttk.Combobox(d,values=[sub_label(p) for p in ls],state='readonly',width=58)
   b=ttk.Combobox(d,state='readonly',width=58)
   a.pack(padx=12,pady=8);b.pack(padx=12,pady=8)
   candidates=[]
   def available_replacements(_=None):
    candidates.clear()
    if a.current()>=0:
     role=positions[ls[a.current()]['id']]
     candidates.extend(p for p in bench if m.replacement_role(side,role,p) is not None)
    b.configure(values=[sub_label(p) for p in candidates])
    b.set('')
   a.bind('<<ComboboxSelected>>',available_replacements)
   if ls:a.current(0)
   available_replacements()
   d.transient(w);d.grab_set()
   def close():
    d.destroy();w.grab_set()
   d.protocol('WM_DELETE_WINDOW',close)
   d.bind('<Escape>',lambda _:close())
   def apply():
    if a.current()>=0 and b.current()>=0 and m.substitute(ls[a.current()]['id'],candidates[b.current()]['id']):
     frames.clear()
     event=m.play[-1]
     close()
     if m.capture and m.positional:
      m.pitch.align();m.pitch.frame()
      frame=m.frames[-1]
      if len(frame)>4:
       frame=(*frame[:4],frame[4] | {'substitution':event[2]})
      draw(frame)
     refresh()
     caption.configure(text=self.commentary(event,(m.a,m.b)))
    else:messagebox.showinfo('Top Antrenörü',self.tr('Değişiklik yapılamadı.','Substitution unavailable.'),parent=d)
   ttk.Button(d,text=self.tr('Uygula','Apply'),command=apply).pack(pady=8)
  self.button(bar,'Oyuncu değiştir','Substitute',sub)
  self.button(bar,'Başlat','Start',start)
  self.button(bar,'Durdur','Pause',pause)
  ttk.Combobox(bar,textvariable=speed,values=['1x','2x','4x'],state='readonly',width=4)
  self.button(bar,'Adım' if m.positional else '5 dakika','Step' if m.positional else '5 minutes',single)
  self.button(bar,'Maçı bitir','Finish match',finish)
  if m.team_orders is not None and m.human is not None:
   def live_plan():
    pause()
    self.tactical_plan_page(m,parent=w,on_apply=requested)
   self.button(bar,'Taktik planı','Tactical plan',live_plan)
  wrap_controls(bar)
  w.protocol('WM_DELETE_WINDOW',lambda:messagebox.showinfo('Top Antrenörü',self.tr('Önce maçı bitir.','Finish match first.')))
  w.update_idletasks();refresh()
  if m.capture or not spatial:
   from konumsal import positions
   if m.positional:
    m.pitch.frame()
    draw(m.frames[-1])
   else:draw((0,(.5,.5),tuple(positions(ls,i,(.5,.5)) for i,ls in enumerate(m.slots))))
 def match_settings(self):
  self.clear()
  modes={'live':self.tr('Canlı metin','Live text'),'quick':self.tr('Hızlı sonuç','Quick result')}
  if self.s.get('match_model'):modes['2d']=self.tr('2D maç','2D match')
  ttk.Label(self.body,text=self.tr('Varsayılan maç modu','Default match mode')).pack()
  chooser=ttk.Combobox(self.body,values=list(modes.values()),state='readonly')
  chooser.current(list(modes).index(self.s.get('match_mode','live')))
  chooser.pack()
  chooser.bind('<<ComboboxSelected>>',lambda _:(self.s.update(match_mode=list(modes)[chooser.current()]),self.autosave()))
  currency=tk.StringVar(value=self.s['currency'])
  ttk.Label(self.body,text=self.tr('Para birimi','Currency')).pack(pady=(14,3))
  box=ttk.Combobox(self.body,textvariable=currency,values=CURRENCIES,state='readonly')
  box.pack()
  box.bind('<<ComboboxSelected>>',lambda _: (self.s.update(currency=currency.get()),self.autosave()))
 def next(self):
  if self.s['week']>34:
   if messagebox.askyesno('Top Antrenörü',self.tr('Yeni sezona geçilsin mi?','Start next season?')):rollover(self.s);self.header();self.dashboard();self.autosave()
   return
  if not self.confirm_lineup():return
  if self.s['employed'] and self.s.get('match_mode','live')!='quick':self.live();return
  self.s['lang']=self.lang;advance(self.s);self.header();self.clear();rows=self.s['results'][-1];self.tree([self.tr('Ev sahibi','Home'),self.tr('Sonuç','Score'),self.tr('Deplasman','Away')],[(m['home'],f"{m['x']} - {m['y']}",m['away']) for m in rows]);m=next(m for m in rows if self.s['club'] in (m['home'],m['away']));ttk.Label(self.body,text='\n'.join(f"{n}′ {player(self.s,pid)['name']} ({team})" for n,team,pid in m['events']) or '0-0').pack();self.button(self.body,'Maç raporu','Match report',self.last_report).pack();self.autosave()
 def autosave(self):
  try:
   autosave(self.s)
  except (OSError, SaveError):
   self.status.config(text=self.tr('Otomatik kayıt yazılamadı','Autosave failed'))
 def save(self):
  folder=user_directory()/'saves'
  try:
   folder.mkdir(parents=True,exist_ok=True)
  except OSError:
   folder=Path.home()
  path=filedialog.asksaveasfilename(defaultextension='.json',initialdir=folder)
  if path:
   try:
    save_game(self.s,path)
   except (OSError, SaveError):
    messagebox.showerror('Top Antrenörü',self.tr('Kayıt yazılamadı.','Save could not be written.'))
 def load(self):
  folder=user_directory()/'saves'
  previous=[user_directory().parent/version/'saves' for version in ('v0.9.3','v0.9.2','v0.9.1','v0.9.0','v0.8.9','v0.8.8','v0.8.7','v0.8.6','v0.8.5','v0.8.4','v0.8.3')]
  legacy=Path.home()/'TopAntrenoru'/'saves'
  initial=next((item for item in (folder,*previous,legacy) if item.is_dir()),Path.home())
  path=filedialog.askopenfilename(filetypes=[('JSON','*.json')],initialdir=initial)
  if not path:
   return
  try:
   loaded=load_game(path)
  except (OSError, SaveError):
   backup=backup_path(Path(path))
   if not backup.is_file() or not messagebox.askyesno('Top Antrenörü',self.tr('Kayıt okunamadı. Önceki sağlam kopya açılsın mı?','Save could not be read. Open its backup?')):
    if not backup.is_file():
     messagebox.showerror('Top Antrenörü',self.tr('Kayıt okunamadı.','Save could not be read.'))
    return
   try:
    loaded=load_game(backup)
   except (OSError, SaveError):
    messagebox.showerror('Top Antrenörü',self.tr('Yedek okunamadı.','Backup could not be read.'))
    return
  self.begin(loaded)
