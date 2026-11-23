"""Contract terms, player preferences and renewals."""
from donem import multiplier,scaled
from finans import book_deal, can_pay
from mevkiler import fit_level
from oyuncu import ability, age_at, state
from veritabani import P, roster, unregister, player, all_players

def terms_valid(years, wage, signing):
    return (type(years) is int and 1 <= years <= 5 and type(wage) is int
            and 100 <= wage <= 50000 and type(signing) is int and 0 <= signing <= 2000000)

def asking_terms(s, p, team, role='Rotation'):
    z = state(s, p)
    reputation = s['club_reputation'][team]
    estimate = scaled(s,'wage',400 + ability(s, p) ** 2 * 13)
    wage = round(max(estimate, z['wage'] * .78) * (1.19 - reputation / 250) / 25) * 25
    age = age_at(p, s['year'], s['week'])
    years = 1 if isinstance(age, int) and age >= 33 else 2
    return {'years': years, 'wage': max(100, wage), 'signing': max(0, int(wage * 2 * multiplier(s,'signing') / multiplier(s,'wage'))), 'role': role}

def player_accepts(s, p, team, years, wage, signing, role):
    return player_objection(s, p, team, years, wage, signing, role) is None

def player_objection(s, p, team, years, wage, signing, role):
    if not terms_valid(years, wage, signing) or role not in ('Starter', 'Rotation'):
        return 'terms'
    owner = s['owners'].get(p['id'])
    ask = asking_terms(s, p, team, role)
    played = state(s, p).get('minutes', 0)
    rival = s['club_reputation'].get(owner, 40)
    demand = ask['wage'] * (1 + max(0, rival - s['club_reputation'][team]) / 160)
    if role == 'Rotation' and (played > 1400 or ability(s,p) >= 14):
        demand *= 1.12
    if role == 'Starter':
        peers = [q for q in roster(team,s['year'],s) if q['pos'] == p['pos'] and q['id'] != p['id']]
        if sum(ability(s,q) > ability(s,p) + 1 for q in peers) >= 2:
            demand *= 1.12
    age = age_at(p, s['year'], s['week'])
    if isinstance(age,int) and age >= 34 and years > 2:
        return 'length'
    limit=.12
    if s.get('match_model'):
        limit=.20
        # A credible starting role and an aligned term can offset some wage demand.
        peers=[q for q in roster(team,s['year'],s) if q['pos']==p['pos'] and q['id']!=p['id']]
        if role=='Starter' and sum(ability(s,q)>ability(s,p)+.7 for q in peers)<2:
            demand*=.94
        if isinstance(age,int) and ((age<=23 and years in (3,4)) or (age>=31 and years<=2)):
            demand*=.96
        if owner and s['board_targets'][team]+4<=s['board_targets'][owner]:
            demand*=.97
    if s.get('transfer_model'):
        rivals=sum(fit_level(q,p['pos'])>=2 and ability(s,q)>ability(s,p)+.5
                   for q in roster(team,s['year'],s) if q['id']!=p['id'] and not state(s,q)['injury'])
        young=isinstance(age,int) and age<=23
        if role=='Starter' and rivals<2:
            demand*=.93 if young else .97
        elif role=='Rotation' and (young and state(s,p)['potential']>ability(s,p)+2 or played>=1800):
            demand*=1.12
        if young and years>=3 and role=='Rotation' and rivals>=2:
            return 'pathway'
        if owner!=team:
            prestige=s['club_reputation'][team]-rival
            demand*=1-min(.08,max(0,prestige)*.004)
    if wage + min(signing / 52, demand * limit) < demand:
        return 'compensation'
    return None

def set_contract(s, p, years, wage, role):
    state(s,p).update(contract=s['year'] + years, wage=wage, role=role)

def renew(s, pid, years, wage, signing, role='Rotation', club=None):
    if club is None and not s['employed']:
        return False, 'unavailable'
    club = s['club'] if club is None else club
    if s['owners'].get(pid) != club or pid in s.get('loans',{}):
        return False, 'unavailable'
    p = player(s,pid)
    if not player_accepts(s,p,club,years,wage,signing,role):
        return False, 'player'
    if not can_pay(s,club,0,signing,wage,state(s,p)['wage']):
        return False, 'budget'
    book_deal(s,club,None,0,signing)
    set_contract(s,p,years,wage,role)
    s['contract_events'].append([s['year'],'renewed',pid,club])
    return True, 'accepted'

def expire(s):
    for pid in sorted(s['owners']):
        p = player(s,pid)
        if state(s,p)['contract'] <= s['year']:
            team = unregister(s,pid)
            s['released'][pid] = s['year']
            s['sale_status'].pop(pid,None)
            s['contract_events'].append([s['year'], 'expired', pid, team])


def contract_time(s,p):
    from datetime import date,timedelta
    expiry=date(state(s,p)['contract'],7,31)
    today=date(s['year'],8,1)+timedelta(weeks=s['week']-1)
    months=max(0,(expiry.year-today.year)*12+expiry.month-today.month-(expiry.day<today.day))
    return expiry,months//12,months%12
