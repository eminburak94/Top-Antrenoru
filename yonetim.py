"""Read models for management screens. They never advance a career."""
from dunya import ROSTER_TARGETS, group
from oyuncu import age_at
from veritabani import player, roster


def weekly_snapshot(s):
    club = s['club']
    return {p['id']: s.get('fitness', {}).get(p['id'], {}).copy()
            for p in roster(club, s['year'], s)}


def record_week(s, before, results, observations=None):
    club, year, week = (s[k] for k in ('club', 'year', 'week'))
    result = next((r for r in results if club in (r['home'], r['away'])), None)
    if result is None:
        return
    previous = s.get('weekly_feedback', {})
    earlier = (previous.get('players', {}) if
               (previous.get('club'), previous.get('year'), previous.get('week')) ==
               (club, year, week - 1) else {})
    players = {}
    for p in roster(club, year, s):
        pid = p['id']
        old = before.get(pid)
        now = s['fitness'][pid]
        minutes = result['minutes'].get(pid, 0)
        players[pid] = dict(
            minutes=minutes,
            minute_change=minutes-earlier[pid]['minutes'] if pid in earlier else None,
            condition=now['condition'], morale=now['morale'], form=now['form'],
            condition_change=now['condition']-old.get('condition',100) if old is not None else None,
            form_change=round(now['form']-old.get('form',6.5),1) if old is not None else None,
            injury=now['injury'],
            training=round(now.get('training_weeks',0)-old.get('training_weeks',0),3) if old is not None else None,
            age=age_at(p,year,week),
        )
        if pid in (observations or {}):
            focus,intensity,status,_,condition=observations[pid]
            players[pid]['session']=[focus,intensity,status,condition]
    s['weekly_feedback'] = dict(club=club, year=year, week=week, players=players)


def squad_review(s):
    club, year, week = (s[k] for k in ('club', 'year', 'week'))
    groups = {role: [] for role in ROSTER_TARGETS}
    fitness = s.get('fitness', {})
    for p in roster(club, year, s):
        z = fitness.get(p['id'], {})
        age = age_at(p, year, week)
        expiry = z.get('contract', 2002+int(p['id'])%3 if p['id'].isdecimal() else year+3)
        groups[group(p)].append(dict(player=p, age=age, expiry=expiry,
                                     condition=z.get('condition',100),
                                     injury=z.get('injury',0), ban=z.get('ban',0),
                                     potential=z.get('potential'),ability=z.get('ability',p['rating'])))
    expired = [p for event_year, event, pid, team in s['contract_events']
               if event_year == year and team == club and event == 'expired'
               and (p := player(s,pid)) is not None]
    ledger = s['finance'][club]
    return dict(groups=groups, expired=expired, targets=ROSTER_TARGETS.copy(), transfer=ledger['transfer_budget'],
                wage=ledger['wage_budget'], payroll=sum(fitness.get(row['player']['id'], {}).get('wage',
                            int(400+row['player']['rating']**2*14))
                            for rows in groups.values() for row in rows),
                fixture=next((m for m in s['schedule'] if club in (m['home'],m['away'])),None))
