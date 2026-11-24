"""Squad planning for careers using the second economy model."""
from collections import Counter

from ekonomi import projection,can_commit
from mevkiler import fit_level,LAYOUTS,group_for
from oyuncu import ability,age_at,state
from sozlesme import asking_terms,player_accepts,renew
from transfer import add_offer,asking_fee,deal,loan_deal,loan_fee,loan_ready,performance,selling_ready
from veritabani import TEAMS,all_players,available,roster


FORMATION=LAYOUTS['4-4-2']
DEPTH={'GK':2,'D':6,'M':7,'F':4}
POSITIONS=tuple(dict.fromkeys(FORMATION))


def known_age(s,p,fallback):
    age=age_at(p,s['year'],s['week'])
    return age if isinstance(age,int) else fallback


def starting_cover(s, squad):
    # Maximum-cardinality matching: each player can fill only one slot.
    players={p['id']:p for p in squad
             if not s.get('transfer_model') or state(s,p)['injury']<3}
    candidates={role:sorted((p for p in players.values() if fit_level(p,role)>=2),
                            key=lambda p:(-skill(s,p,role),p['id']))
                for role in POSITIONS}
    assigned={}
    def place(slot, seen):
        for p in candidates[FORMATION[slot]]:
            pid=p['id']
            if pid in seen:continue
            seen.add(pid)
            if pid not in assigned or place(assigned[pid],seen):
                assigned[pid]=slot
                return True
        return False
    for slot in sorted(range(len(FORMATION)),
                       key=lambda i:(len(candidates[FORMATION[i]]),i)):
        place(slot,set())
    cover={role:[] for role in POSITIONS}
    for pid,slot in assigned.items():
        cover[FORMATION[slot]].append(players[pid])
    return cover


def assess(s, team, squad):
    depth=Counter(group_for(p['pos']) for p in squad)
    competitive=19-s['board_targets'][team]
    needs=[]
    cover=starting_cover(s,squad)
    for role in POSITIONS:
        group=group_for(role)
        slots=FORMATION.count(role)
        core=sorted(cover[role],key=lambda p:(-skill(s,p,role),p['id']))
        shortage=max(0,slots-len(core))
        thin=max(0,DEPTH[group]-depth[group])
        aging=sum(known_age(s,p,0)>=32 for p in core)
        expiring=sum(state(s,p)['contract']<=s['year']+1 for p in core)
        quality=skill(s,core[-1],role) if core else 0
        priority=shortage*10+thin*2+aging*1.5+expiring+max(0,9+competitive*.16-quality)*.55
        if priority>.8:
            needs.append((priority,role,quality,shortage,aging))
    return sorted(needs,key=lambda n:(-n[0],n[1]))


def skill(s,p,role):
    return ability(s,p)*(.68+.08*fit_level(p,role))


def contract_cost_penalty(fee, terms, plan, budget):
    weeks=34*terms['years']
    total=fee+terms['signing']+weeks*terms['wage']
    capacity=budget+weeks*max(0,plan['wage_room']-plan['wages'])
    return 4*total/max(80000,capacity)


def recruit(s):
    modern=s.get('transfer_model')
    market=[]
    recently_signed={pid for year,event,pid,team in s['contract_events']
                     if year==s['year'] and event=='signed'}
    sold=Counter()
    listed={pid for pid,mode in s['sale_status'].items() if mode=='listed'}
    for team in TEAMS:
        if s['employed'] and team==s['club']:continue
        squad=roster(team,s['year'],s)
        by_group={g:[] for g in DEPTH}
        for p in squad:
            by_group[group_for(p['pos'])].append(p)
        for group,players in by_group.items():
            # Selling a reserve must leave the group with usable cover.
            players.sort(key=lambda p:(-ability(s,p),p['id']))
            minimum={'GK':2,'D':4,'M':4,'F':2}[group]
            for p in players[minimum:]:
                z=state(s,p)
                age=known_age(s,p,0)
                surplus=len(players)>DEPTH[group]
                if p['id'] not in recently_signed and (z['contract']<=s['year']+1 or age>=29
                                                       or surplus or z['wage']>=4000 or s.get('match_model')):
                    listed.add(p['id'])
    for p in all_players(s):
        owner=s['owners'].get(p['id'])
        if owner is None and not available(s,p):continue
        age=age_at(p,s['year'],s['week'])
        if not isinstance(age,int) or not 15<=age<38:continue
        market.append((p,age,performance(s,p['id']) if modern else 0))
    for team in TEAMS:
        if s['employed'] and team==s['club']:continue
        squad=roster(team,s['year'],s)
        if len(squad)>=24:continue
        plan=projection(s,team)
        if plan['closing']<plan['reserve']:continue
        initial=assess(s,team,squad)
        paid=0
        borrowed=False
        elite=s['club_reputation'][team]>=67
        attempted_roles=set()
        for _ in initial:
            squad=roster(team,s['year'],s)
            if len(squad)>=24:break
            # Re-rank priorities after every successful move.  Keep each role
            # to one attempt per recruitment pass, including pending offers.
            remaining=[need for need in assess(s,team,squad)
                       if need[1] not in attempted_roles]
            if not remaining:break
            _,role,baseline,shortage,aging=remaining[0]
            attempted_roles.add(role)
            ledger=s['finance'][team]
            budget=min(ledger['cash'],ledger['transfer_budget'],plan['closing']-plan['reserve'])
            if budget<=0:break
            options=[]
            for p,age,form in market:
                pid=p['id']
                owner=s['owners'].get(pid)
                fit=fit_level(p,role)
                if owner==team or fit<2:continue
                limit=2 if s.get('match_model') and shortage else 1
                if owner and (paid>=limit or sold[owner]>=2 or pid not in listed or not selling_ready(s,p)):continue
                if s.get('match_model') and owner and owner!=s['club'] and s['sale_status'].get(pid)!='listed':
                    depth=sum(group_for(q['pos'])==group_for(p['pos']) for q in roster(owner,s['year'],s))
                    if depth<={'GK':2,'D':4,'M':4,'F':2}[group_for(p['pos'])]:continue
                z=state(s,p)
                fee=asking_fee(s,p)
                if fee>=budget:continue
                quality=skill(s,p,role)
                upside=max(0,z['potential']-z['ability'])*(.30 if age<24 else .06)
                experience=.9 if shortage and 25<=age<=31 else 0
                if not shortage and quality+upside<baseline+(.1 if aging else .8):continue
                terms=asking_terms(s,p,team,'Starter')
                terms['wage']=round(terms['wage']*1.31)
                cost=fee+terms['signing']
                if cost>budget or z['contract']>s['year']+1 and owner and quality<baseline+1:continue
                if not can_commit(s,team,cost,terms['wage'],forecast=plan):continue
                score=quality+upside+experience+fit*.28-max(0,age-30)*.32
                if s.get('match_model',0)==4:
                    score-=contract_cost_penalty(fee,terms,plan,budget)
                else:
                    score-=cost/max(80000,budget)*2.8+terms['wage']/max(1000,plan['wage_room'])*5
                if modern:
                    score+=form*(.62 if elite else .35)
                    score+=quality*.14 if elite else upside*.42-cost/max(80000,budget)*.9
                options.append((score,pid,p,owner,fee,terms))
            for _,pid,p,owner,fee,terms in sorted(options,reverse=True):
                if s['employed'] and owner==s['club']:
                    ok=add_offer(s,p,team,fee,terms)
                else:
                    ok=deal(s,pid,team,fee,**terms)[0]
                if ok:
                    if owner:
                        sold[owner]+=1
                        paid+=1
                    plan=projection(s,team)
                    break
            else:
                if modern and shortage and not borrowed:
                    borrowed=borrow_cover(s,team,role,market,plan)
                    if borrowed:plan=projection(s,team)


def borrow_cover(s,team,role,market,plan):
    options=[]
    for p,age,form in market:
        pid=p['id']
        owner=s['owners'].get(pid)
        if not owner or owner==team or age>26 or fit_level(p,role)<2 or state(s,p)['injury']>=3:
            continue
        if s['employed'] and owner==s['club'] and s['sale_status'].get(pid)!='loan':
            continue
        if not loan_ready(s,p):
            continue
        fee=loan_fee(s,p)
        wage=state(s,p)['wage']
        if can_commit(s,team,fee,wage//2,forecast=plan):
            options.append((skill(s,p,role)+.4*form,pid,p,owner,fee,wage))
    for _,pid,p,owner,fee,wage in sorted(options,reverse=True):
        if s['employed'] and owner==s['club']:
            ok=add_offer(s,p,team,fee,dict(years=1,wage=min(50000,max(100,wage)),
                                         signing=0,role='Starter',kind='loan',share=50))
        else:
            ok=loan_deal(s,pid,team,fee,50)[0]
        if ok:return True
    return False


def renew_contracts(s,team,squad):
    counts=Counter(group_for(p['pos']) for p in squad)
    expiring=[p for p in squad if state(s,p)['contract']<=s['year']]
    def priority(p):
        group=group_for(p['pos'])
        age=known_age(s,p,26)
        z=state(s,p)
        return ability(s,p)+max(0,DEPTH[group]-counts[group]+1)*2+max(0,27-age)*.12-z['wage']/8000
    for p in sorted(expiring,key=lambda p:(-priority(p),p['id'])):
        group=group_for(p['pos'])
        age=known_age(s,p,26)
        z=state(s,p)
        alternatives=sum(q['id']!=p['id'] and group_for(q['pos'])==group
                         and state(s,q)['contract']>s['year'] and ability(s,q)>=ability(s,p)-1 for q in squad)
        if alternatives>=DEPTH[group] or (age>=34 and alternatives>=2 and z['wage']>4500):
            continue
        terms=asking_terms(s,p,team,'Starter')
        if s.get('match_model',0)!=4 or not player_accepts(s,p,team,**terms):
            terms['wage']=round(terms['wage']*1.23)
        renew(s,p['id'],**terms,club=team)
