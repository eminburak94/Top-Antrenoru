"""Versioned fictional staff, delegation and scouting. No career RNG is consumed."""
import random
from donem import scaled

from veritabani import TEAMS, available, player, all_players, roster

CORE_ROLES=('assistant','coach','fitness','goalkeeping','scout')
ROLES=(*CORE_ROLES,'medical')
SKILLS=('coaching','attack','defence','goalkeeping','fitness','judging','potential',
        'tactics','motivation','discipline')
SPECIAL=dict(zip(ROLES,(('tactics','motivation'),('coaching','attack','defence'),
                       ('fitness','discipline'),('goalkeeping',),('judging','potential'),('fitness',))))
TASKS={'lineup':('assistant','advice'), 'team_training':('coach','automatic'),
       'individual_training':('coach','advice'), 'scouting':('scout','advice')}
FIRST=('Deniz','Ekin','Erdem','Bora','Alp','Mert','Selin','Sarp','Işıl','Yağız','Özge','Barış')
LAST=('Acar','Esen','Güney','Torun','Gök','Erden','Yalın','Vardar','Tunç','Günay','Sezer')
REPORT_LIMIT=60
MEDICAL_CANDIDATES=8


def capacity(s,team):
    reputation=s['club_reputation'][team]
    return 5 if reputation>=65 else 4 if reputation>=50 else 3


def setup(s):
    pool={}
    for i,team in enumerate((*TEAMS,*([None]*6))):
        for j,role in enumerate(CORE_ROLES):
            index=i*len(CORE_ROLES)+j
            pid=f'staff-{index+1:03d}'
            rng=random.Random(f'Top Antrenoru staff v1:{pid}')
            skills={key:rng.randint(*( (9,17) if key in SPECIAL[role] else (4,12))) for key in SKILLS}
            owned=team if team and j<capacity(s,team) else None
            pool[pid]=dict(name=f'{FIRST[index%len(FIRST)]} {LAST[index%len(LAST)]}',role=role,
                skills=skills,wage=450+50*max(skills[k] for k in SPECIAL[role]),
                club=owned,start=s['year'] if owned else None,end=s['year']+2+j%2 if owned else None,
                source='fictional')
    s['staff_system']=dict(version=1,pool=pool,delegation={},jobs=[],reports=[],booked={})
    medical_market(s)


def medical_market(s):
    st=s.get('staff_system')
    if not s.get('workload_model') or not st:
        return
    pool=st['pool']
    for index in range(MEDICAL_CANDIDATES):
        pid=f'medical-{index+1:02}'
        if pid in pool:
            continue
        skill=10+index
        pool[pid]=dict(name=f'{FIRST[index]} {LAST[-index-1]}',role='medical',
            skills={key:skill if key=='fitness' else 6 for key in SKILLS},
            wage=450+skill*30,club=None,start=None,end=None,source='fictional')


def active(s,team,role=None):
    return [(pid,row) for pid,row in s.get('staff_system',{}).get('pool',{}).items()
            if row['club']==team and (role is None or row['role']==role)]


def salary_limit(s,team):
    return scaled(s,'staff',4500+s['club_reputation'][team]*45)


def payroll(s,team):
    return sum(row['wage'] for _,row in active(s,team))


def contract(s,team,pid,years,renew=False):
    st=s.get('staff_system')
    if not st or team not in TEAMS:
        return False,'unavailable'
    row=st['pool'].get(pid)
    if not row or type(years) is not int or not 1<=years<=3:
        return False,'unavailable'
    if renew:
        if row['club']!=team or row['end']>=s['year']+years:
            return False,'unavailable'
    elif row['club'] is not None or len(active(s,team))>=capacity(s,team):
        return False,'staff_capacity'
    wage=scaled(s,'staff',row.get('base_wage',row['wage']))
    delta=wage-(row['wage'] if renew else 0)
    cost=payroll(s,team)+delta
    if cost>salary_limit(s,team) or s['finance'][team]['cash']<cost*4:
        return False,'staff_budget'
    if s.get('economy_model') and (not renew or delta>0) and (team!=s['club'] or not s['employed']):
        from ekonomi import can_commit,projection
        plan=projection(s,team)
        # A funded emergency hire restores basic operations after a vacancy.
        core=(not active(s,team) and s['finance'][team]['cash']>=plan['reserve']+4*wage
              and plan['closing']-plan['weeks']*wage>=plan['reserve'])
        if not core and not can_commit(s,team,0,0,delta,forecast=plan):
            return False,'staff_budget'
    if s.get('economy_model')==2:
        row.setdefault('base_wage',row['wage'])
        row['wage']=wage
    row.update(club=team,start=row['start'] if renew else s['year'],end=s['year']+years)
    return True,'accepted'


def release(s,team,pid):
    st=s.get('staff_system')
    row=st['pool'].get(pid) if st else None
    if not row or row['club']!=team:
        return False
    row.update(club=None,start=None,end=None)
    st['delegation']={t:{task:key for task,key in tasks.items() if key!=pid}
                      for t,tasks in st['delegation'].items()}
    st['jobs']=[job for job in st['jobs'] if job['scout']!=pid]
    return True


def season_open(s):
    st=s.get('staff_system')
    if not st:return
    for pid,row in st['pool'].items():
        if row['club'] is not None and row['end']<=s['year']:
            release(s,row['club'],pid)
    refill(s)


def refill(s):
    st=s.get('staff_system')
    if not st:return
    for team in TEAMS:
        if team==s['club'] and s['employed']:continue
        existing={row['role'] for _,row in active(s,team)}
        for role in ROLES[:capacity(s,team)]:
            if role not in existing:
                options=[(pid,row) for pid,row in st['pool'].items()
                         if row['club'] is None and row['role']==role]
                if s.get('economy_model'):
                    count=sum(row['role']!='medical' for row in st['pool'].values())
                    if not options and count<150:
                        from ekonomi import can_commit
                        if can_commit(s,team,0,0,900):
                            pid=f"staff-{count+1:03d}"
                            rng=random.Random(pid)
                            row=dict(name=f'{FIRST[rng.randrange(len(FIRST))]} {LAST[rng.randrange(len(LAST))]}',
                                     role=role,skills={k:rng.randint(5,13) for k in SKILLS},
                                     wage=900,club=None,start=None,end=None,source='fictional')
                            st['pool'][pid]=row
                            options=[(pid,row)]
                    options.sort(key=lambda pair:(pair[1]['wage'],pair[0]))
                    options=options[:1]
                for pid,row in options:
                    if contract(s,team,pid,2)[0]:
                        break


def week_key(s):
    return s['year']*34+s['week']


def weekly_cost(s,team):
    st=s.get('staff_system')
    rep=s['club_reputation'][team]
    if not st:
        return 12700+rep*165
    key=week_key(s)
    if st['booked'].get(team)==key:return 0
    st['booked'][team]=key
    if s.get('economy_model'):
        from ekonomi import admin
        return admin(s,team)+payroll(s,team)
    return 11000+rep*100+payroll(s,team)


def best(s,team,role,skill):
    return max((row['skills'][skill] for _,row in active(s,team,role)),default=0)


def effects(s,team):
    return (best(s,team,'fitness','fitness')//6,
            best(s,team,'coach','coaching'),best(s,team,'goalkeeping','goalkeeping'))


def development_factor(effect,goalkeeper):
    return 1+(effect[1]+(effect[2] if goalkeeper else 0))*.002


def delegate(s,team,task,pid):
    st=s.get('staff_system')
    if not st or task not in TASKS or team!=s['club'] or not s['employed']:
        return False
    if pid is not None and pid not in {key for key,_ in active(s,team,TASKS[task][0])}:
        return False
    tasks=st['delegation'].setdefault(team,{})
    if pid is None:tasks.pop(task,None)
    else:tasks[task]=pid
    return True


def assigned(s,team,task):
    st=s.get('staff_system',{})
    return st.get('pool',{}).get(st.get('delegation',{}).get(team,{}).get(task))


def team_training(s,team):
    if team!=s['club'] or not s['employed']:return 'Normal'
    if 'training' in s:return s['training']
    coach=assigned(s,team,'team_training')
    return suggested_training(s,team,coach['skills']['coaching']) if coach else 'Normal'


def suggested_training(s,team,level):
    squad=roster(team,s['year'],s)
    fitness=s.get('fitness',{})
    if squad and sum(fitness.get(p['id'],{}).get('condition',100) for p in squad)/len(squad)<72:
        return 'Rest'
    return 'Development' if level>=11 else 'Normal'


def recommendation(s):
    from mac import select_slots, suitable
    from oyuncu import age_at
    from dunya import ROSTER_TARGETS,group
    team=s['club']
    assistant=assigned(s,team,'lineup')
    level=assistant['skills']['tactics'] if assistant else best(s,team,'assistant','tactics')
    coach=assigned(s,team,'individual_training')
    slots=select_slots(s,team,use_manual=False) if level else []
    squad=roster(team,s['year'],s)
    return dict(slots=slots,level=level,mismatches=[pid for role,pid in slots
                if not suitable(s,player(s,pid),role)], shortages=[r for r,n in ROSTER_TARGETS.items()
                if sum(group(p)==r for p in squad)<n] if level>=10 else [],
                young=[p['id'] for p in squad if isinstance(age:=age_at(p,s['year'],s['week']),int)
                       and age<25][:3] if coach else [],
                training=suggested_training(s,team,level))


def eligible_target(s,p):
    return p['id'] in s['owners'] or available(s,p)


def candidates(s,role=None,max_age=None,club=None):
    from oyuncu import age_at
    for p in all_players(s):
        owner=s['owners'].get(p['id'])
        if not eligible_target(s,p) or (role and role not in (p['pos'],*p.get('alternate_positions',()))):
            continue
        if club is not None and (owner or 'free')!=club:continue
        age=age_at(p,s['year'],s['week'])
        if max_age is not None and (not isinstance(age,int) or age>max_age):continue
        yield p


def start_scout(s,pid):
    st=s.get('staff_system')
    team=s['club']
    p=player(s,pid)
    if not st or not s['employed'] or not p or not eligible_target(s,p):return False
    scout=st['delegation'].get(team,{}).get('scouting')
    if scout is None:
        scout=next((key for key,_ in active(s,team,'scout')),None)
    if scout is None or any(j['scout']==scout or (j['club'],j['player'])==(team,pid) for j in st['jobs']):
        return False
    st['jobs'].append(dict(scout=scout,club=team,player=pid,due=week_key(s)+2))
    return True


def finish_scouting(s):
    from oyuncu import ability,attributes,state
    st=s.get('staff_system')
    if not st:return
    now=week_key(s)+1
    for job in st['jobs'][:]:
        if job['due']>now:continue
        st['jobs'].remove(job)
        p=player(s,job['player'])
        scout=st['pool'][job['scout']]
        if scout['club']!=job['club'] or not p or not eligible_target(s,p):continue
        z=state(s,p)
        rng=random.Random(f"{job['scout']}:{p['id']}:{job['due']}")
        bands=[]
        for actual,skill in ((ability(s,p),'judging'),(z['potential'],'potential')):
            radius=1+(20-scout['skills'][skill])*.20
            midpoint=actual+rng.uniform(-.5,.5)*radius
            lo=max(1,min(19,int(midpoint-radius)))
            hi=min(20,max(lo+1,int(midpoint+radius+.99)))
            bands.append([lo,hi])
        traits=list(attributes(s,p).values())
        groups={}
        spread=1.1+(20-scout['skills']['judging'])*.23
        for label,values in (('technical',traits[:12]),('mental',traits[12:24]),
                             ('physical',traits[24:31]+traits[-1:])):
            mean=sum(values)/len(values)
            mid=mean+rng.uniform(-.45,.45)*spread
            low=max(1,min(19,int(mid-spread)))
            groups[label]=[low,min(20,max(low+1,int(mid+spread+.99)))]
        st['reports'].append(dict(job,year=s['year'],week=s['week'],bands=bands,groups=groups,
                                  confidence=(scout['skills']['judging']+scout['skills']['potential'])//2))
    del st['reports'][:-REPORT_LIMIT]
