"""Board expectations, manager reputation and employment."""
from oyuncu import ability, clamp
from veritabani import TEAMS, roster
from yarisma import standings

def strength(s, team):
    squad=roster(team,s['year'],s)
    best=sorted((ability(s,p) for p in squad),reverse=True)[:11]
    return sum(best)/11 + min(3,s['finance'][team]['wage_budget']/45000)

def targets(s):
    order=sorted(TEAMS,key=lambda t:(-strength(s,t),t))
    return {team:min(17,rank+2) for rank,team in enumerate(order,1)}

def job_market(s):
    if 'manager_state' in s:
        from is_piyasasi import resolve
        resolve(s)
        return
    current = s['club'] if s['employed'] else None
    recent={team for year,event,team in s['jobs']
            if event in ('fired','resigned','moved') and year>=s['year']-1}
    pool=[t for t in TEAMS if t!=current and t not in recent]
    suitable=[t for t in pool if s['club_reputation'][t]<=s['manager_rep']+17]
    if not suitable and not s['employed'] and pool:
        suitable=[min(pool,key=lambda t:(s['club_reputation'][t],t))]
    order=sorted(suitable,key=lambda t:(-s['club_reputation'][t],t))
    s['job_offers'] = order[:(1 if s['employed'] else 3)] if not s['employed'] or s['manager_rep'] >= 50 else []

def evaluate(s, ranking):
    for rank,team in enumerate(ranking,1):
        delta=2 if rank<=3 else -2 if rank>=16 else 0
        s['club_reputation'][team]=clamp(s['club_reputation'][team]+delta,15,90)
    if s['employed']:
        club=s['club']
        rank=ranking.index(club)+1
        goal=s['board_targets'][club]
        delta=12 if rank==1 else 5 if rank<=goal else -5
        s['manager_rep']=clamp(s['manager_rep']+delta,10,100)
        s['board_misses']=0 if rank<=goal else s['board_misses']+1
        if 'manager_state' in s and rank==1:
            s['manager_state']['honours'].append(dict(year=s['year'],team=club))
        if s['board_misses']>=2 or (rank>goal and s['confidence']<=10):
            if 'manager_state' in s:
                from is_piyasasi import leave
                leave(s,'performance')
            else:
                s['employed']=False
                s['jobs'].append([s['year'],'fired',club])
            s['news'].append([35,'Yönetim / Board',f'{club}: Görevden alındı / Dismissed'])
    job_market(s)

def resign(s):
    if 'manager_state' in s:
        from is_piyasasi import leave
        return leave(s,'resigned')
    if not s['employed']:
        return False
    s['employed']=False
    s['selected']=[]
    s['manager_rep']=max(10,s['manager_rep']-3)
    s['jobs'].append([s['year'],'resigned',s['club']])
    job_market(s)
    return True

def accept_job(s,team):
    if 'manager_state' in s:
        from is_piyasasi import offer
        return offer(s,team,True)
    if s['week'] != 1 or team not in s['job_offers']:
        return False
    if s['employed']:
        s['jobs'].append([s['year'],'moved',s['club']])
    s.update(club=team,employed=True,confidence=70,board_misses=0,selected=[],job_offers=[],
             managed_stats=s['teams'][team].copy())
    s['jobs'].append([s['year'],'hired',team])
    return True
