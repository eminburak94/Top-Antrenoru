import json
from itertools import chain
from tarihsel import load_entries
from pathlib import Path

D = json.loads(Path(__file__).with_name('data.json').read_text(encoding='utf-8'))
P = {player['id']: player for player in D['players']}
HISTORICAL = load_entries(Path(__file__).with_name('tarihsel_girisler.json'),D['players'])
TEAMS = tuple(D['teams'])
VERIFIED_SCORES = json.loads(Path(__file__).with_name('tarihsel_skorlar.json').read_text(encoding='utf8'))

def verified_results():
    return sorted(VERIFIED_SCORES.values(),key=lambda m:m['week'])
INITIAL_OWNERS = {pid: p['club'] for pid, p in P.items() if p['first'] == 1}
RESERVES = {team: [] for team in TEAMS}
for player in P.values():
    if player['first'] != 1:
        RESERVES[player['club']].append(player)

def roster(team, year, s=None):
    if s is None or 'owners' not in s:
        return [P[pid] for pid, owner in INITIAL_OWNERS.items() if owner == team]
    if '_rosters' not in s:
        return [player(s,pid) for pid, owner in s['owners'].items() if owner == team]
    return s['_rosters'][team]


def index_rosters(s):
    indexed = {team: [] for team in TEAMS}
    for pid, owner in s['owners'].items():
        indexed[owner].append(player(s,pid))
    s['_rosters'] = indexed

# Optional sourced, dated admissions. No new players ship in this release.
INTAKE = {row['player_id']: row for row in D.get('historical_intake', [])} | HISTORICAL
for pid, entry in INTAKE.items():
    from datetime import date
    if (pid not in P and pid not in HISTORICAL) or pid in INITIAL_OWNERS or not entry.get('source'):
        raise ValueError(f'Invalid historical intake: {pid}')
    date.fromisoformat(entry['available_from'])

def available(s, p):
    from datetime import date, timedelta
    from oyuncu import age_at
    pid = p['id']
    if pid in s['owners'] or pid in s['retired']:
        return False
    if pid in s['released']:
        return True
    entry = INTAKE.get(pid)
    if entry:
        today = date(s['year'], 8, 1) + timedelta(weeks=s['week'] - 1)
        return today >= date.fromisoformat(entry['available_from'])
    age = age_at(p, s['year'], s['week'])
    return s['year'] > 2000 and isinstance(age, int) and age >= 17

def unregister(s, pid):
    owner = s['owners'].pop(pid, None)
    if owner is not None and '_rosters' in s:
        s['_rosters'][owner].remove(player(s,pid))
    return owner

def register(s, pid, team):
    unregister(s, pid)
    s['owners'][pid] = team
    if '_rosters' in s:
        s['_rosters'][team].append(player(s,pid))


def player(s,pid):
    return P.get(pid) or HISTORICAL.get(pid) or s.get('generated',{}).get(pid)

def all_players(s):
    return chain(P.values(), HISTORICAL.values(), s.get('generated',{}).values())
