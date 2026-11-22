import random
from veritabani import D, TEAMS, VERIFIED_SCORES

def schedule(year):
 if year == 2000:
  return [{key: m[key] for key in ('week', 'home', 'away')} for m in D['matches']]
 ts=list(TEAMS);random.Random(year).shuffle(ts);out=[]
 for w in range(17):
  for i in range(9):
   a,b=ts[i],ts[-1-i];a,b=(b,a) if (w+i)%2 else (a,b);out.extend([dict(week=w+1,home=a,away=b),dict(week=w+18,home=b,away=a)])
  ts=[ts[0],ts[-1]]+ts[1:-1]
 return sorted(out,key=lambda m:m['week'])

def standings(s):return sorted(s['teams'],key=lambda t:(s['teams'][t]['p'],s['teams'][t]['gf']-s['teams'][t]['ga'],s['teams'][t]['gf']),reverse=True)

def expectation(t):return 3 if t in ('GALATASARAY','FENERBAHÇE','BEŞİKTAŞ') else 7 if t in ('TRABZONSPOR','GAZİANTEPSPOR','MKE ANKARAGÜCÜ') else 13

TRANSFER_PERIODS = ((1,3),(18,19))

def window(s):return any(start<=s['week']<=end for start,end in TRANSFER_PERIODS)

# Match dates from TFF detail pages referenced by VERIFIED_SCORES.
OPENING_DAYS_2000 = {
    '20642': 11,
    '20643': 12, '20644': 12, '20645': 12, '20646': 12,
    '20647': 13, '20648': 13, '20649': 13, '20650': 13,
}


def opening_date(year, fixture):
    if year != 2000:
        return None
    for source_id, day in OPENING_DAYS_2000.items():
        row = VERIFIED_SCORES[source_id]
        if all(row[key]==fixture[key] for key in ('week','home','away')):
            return f'2000-08-{day:02d}'
    return None


FORMATIONS = ('4-4-2', '4-3-3', '3-5-2', '5-3-2')
STYLES = ('Attack', 'Balanced', 'Defend')

def formation_for(s, team):
    if team == s['club'] and s.get('employed',True):
        return s['formation']
    return FORMATIONS[(TEAMS.index(team) + s['year']) % len(FORMATIONS)]

def style_for(s, team):
    if team == s['club'] and s.get('employed',True):
        return s['style']
    return STYLES[(TEAMS.index(team) + s['week'] // 5) % len(STYLES)]

def table():
    return {team: dict(p=0, w=0, d=0, l=0, gf=0, ga=0) for team in TEAMS}

def apply_score(s, home, away, x, y):
    for team, goals, conceded in ((home, x, y), (away, y, x)):
        row = s['teams'][team]
        row['gf'] += goals
        row['ga'] += conceded
        row['p'] += 3 if goals > conceded else 1 if goals == conceded else 0
        row['w' if goals > conceded else 'd' if goals == conceded else 'l'] += 1
