"""Seasonal player life cycle and club recruitment."""
from altyapi import replenish
from finans import allocate, budget_defaults, can_pay, initialize
from menajer import targets
from oyuncu import GROUPS, ability, age_at, attributes, develop, state
from sozlesme import asking_terms, expire, renew
from transfer import add_offer, asking_fee, deal, selling_ready
from veritabani import INTAKE, P, TEAMS, available, roster, unregister, player, all_players
from yarisma import expectation

ROSTER_TARGETS = {'GK':2,'D':6,'M':6,'F':3}

def group(p):
    return next((name for name,positions in GROUPS.items() if p['pos'] in positions),'M')

def prepare_world(s):
    for key,default in (
        ('generated',{}),('season_stats',{}),('legacy_goals',{}),('sale_status',{}),('retired',{}),('released',{}),('contract_events',[]),('offers',[]),('world_history',[]),
        ('employed',True),('manager_rep',40),('board_misses',0),('jobs',[]),('job_offers',[]),
        ('club_reputation',{t:{3:75,7:56,13:42}[expectation(t)] for t in TEAMS}),
        ('managed_stats',s['teams'][s['club']].copy()),
    ):
        s.setdefault(key,default)
    for team in TEAMS:
        ledger=s['finance'][team]
        initialize(ledger)
        if 'wage_budget' not in ledger:
            ledger.update(budget_defaults(s,team))
    if 'board_targets' not in s:
        s['board_targets']=targets(s)

def age_world(s,rng):
    import personel
    coaches={team:personel.effects(s,team) for team in TEAMS} if 'staff_system' in s else {}
    for p in all_players(s):
        pid=p["id"]
        if pid in s['retired']:
            continue
        if pid in INTAKE and pid not in s['owners'] and not available(s,p):
            continue
        age=age_at(p,s['year']+1,1)
        if not isinstance(age,int) or age < 15:
            continue
        z=state(s,p)
        minutes=z.get('minutes',0)
        if pid in s['owners'] and 'minutes' not in z:
            minutes=z['apps']*75
        threshold=36 if group(p)=='GK' else 33 if group(p)=='F' else 34
        fitness=attributes(s,p)['Natural fitness']
        risk=max(0,(age-threshold)*.095 + (12-fitness)*.012 + (6.5-z['form'])*.035
                 + (.10 if minutes<450 else -.05))
        if age>=threshold-1 and (age>=43 or rng.random()<risk):
            old=unregister(s,pid)
            s['released'].pop(pid,None)
            s['sale_status'].pop(pid,None)
            s['retired'][pid]=[s['year']+1,old]
            s['contract_events'].append([s['year']+1,'retired',pid,old])
        else:
            owner=s['owners'].get(pid)
            condition=s['finance'][owner]['academy_level'] if owner else 45
            develop(s,p,rng,active=owner is not None,minutes=minutes,facility=(.90+condition/450)*personel.development_factor(coaches.get(owner,(0,0,0)),p['pos']=='GK'))

def renew_ai(s):
    for team in TEAMS:
        if s['employed'] and team==s['club']:
            continue
        squad=roster(team,s['year'],s)
        if s.get('economy_model')==2:
            from piyasa_ai import renew_contracts
            renew_contracts(s,team,squad)
            continue
        expiring=sorted((p for p in squad if state(s,p)['contract']<=s['year']),
                       key=lambda p:(-ability(s,p),p['id']))
        for p in expiring:
            terms=asking_terms(s,p,team,'Starter')
            terms['wage']=round(terms['wage']*1.15)
            renew(s,p['id'],**terms,club=team)

def season_open(s,rng):
    allocate(s)
    renew_ai(s)
    expire(s)
    recruit(s)
    replenish(s,rng)
    s['board_targets']=targets(s)

def recruit(s):
    if s.get('economy_model'):
        from ekonomi import crisis_sales
        crisis_sales(s)
    for offer in s['offers']:
        if offer['status']=='open' and (offer['year']!=s['year'] or s['week']-offer['week']>2):
            offer['status']='expired'
    if s.get('economy_model')==2:
        from piyasa_ai import recruit as plan_recruitment
        plan_recruitment(s)
        return
    pools={role:[] for role in ROSTER_TARGETS}
    for p in all_players(s):
        pid=p['id']
        if pid in s['owners'] or available(s,p):
            pools[group(p)].append(p)
    for team in TEAMS:
        managed=s['employed'] and team==s['club']
        if managed:
            continue
        squad=roster(team,s['year'],s)
        counts={role:sum(group(p)==role for p in squad) for role in ROSTER_TARGETS}
        older={role:sum(group(p)==role and age_at(p,s['year'],s['week'])>=33 for p in squad)
               for role in ROSTER_TARGETS}
        needs=sorted(ROSTER_TARGETS,key=lambda role:(counts[role]-.45*older[role])/ROSTER_TARGETS[role])
        for role in needs:
            if len(roster(team,s['year'],s))>=23 or (counts[role]>=ROSTER_TARGETS[role] and not older[role]):
                continue
            candidates=[]
            for p in pools[role]:
                owner=s['owners'].get(p['id'])
                if owner==team or (owner is None and not available(s,p)) or (owner is not None and not selling_ready(s,p)):
                    continue
                age=age_at(p,s['year'],s['week'])
                if not isinstance(age,int) or age>=39:
                    continue
                fee=asking_fee(s,p)
                quality=ability(s,p)
                if counts[role]>=ROSTER_TARGETS[role] and age>=31:
                    continue
                potential=state(s,p)['potential']
                grade=(6 if p["id"] in INTAKE else 0)+quality+(potential-quality)*(.32 if age<24 else .05)-max(0,age-29)*.48-fee/460000
                candidates.append((grade,p['id'],p,owner,fee))
            for _,_,p,owner,fee in sorted(candidates,reverse=True):
                terms=asking_terms(s,p,team,'Starter')
                terms['wage']=round(terms['wage']*1.31)
                if not can_pay(s,team,fee,terms['signing'],terms['wage']):
                    continue
                if s['employed'] and owner==s['club']:
                    if add_offer(s,p,team,fee,terms):
                        s['news'].append([s['week'],'Teklif / Offer',f"{team} → {p['name']} | ${fee:,}"])
                        break
                elif deal(s,p['id'],team,fee,**terms)[0]:
                    break
