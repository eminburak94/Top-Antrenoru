"""Versioned JSON saves, validation and recovery copies."""
from collections import ChainMap, defaultdict
from datetime import date
import re
import hashlib
import json
import math
import os
from pathlib import Path
import random
import tempfile
from uuid import uuid4

from kariyer import SCHEMA_VERSION, new, prepare
from veritabani import P, HISTORICAL, TEAMS
from yerellestirme import COUNTRIES
from para import CURRENCIES
from finans import FLOW
from istatistik import SHOT_EVENTS,FIELDS
from yarisma import FORMATIONS, STYLES, apply_score, schedule, table

DATABASE_VERSION = '2000-01-v060'

class SaveError(ValueError):
    pass

def require(check, message):
    if not check:
        raise SaveError(message)

def integer(value, minimum, maximum=None):
    return type(value) is int and value >= minimum and (maximum is None or value <= maximum)

def numeric(value, a, b):
    return type(value) in (int, float) and a <= value <= b and math.isfinite(value)

def payload(s):
    return {key: value for key, value in s.items() if not key.startswith('_')}

def migrate(raw):
    require(isinstance(raw, dict), 'Save root must be an object')
    if 'schema_version' in raw:
        require(type(raw['schema_version']) is int and raw['schema_version'] in (1,2,SCHEMA_VERSION), 'Unsupported save version')
        require(raw.get('database_version') == DATABASE_VERSION, 'Unsupported database version')
        if raw['schema_version']!=SCHEMA_VERSION:
            raw['schema_version']=SCHEMA_VERSION
            raw['legacy_goals']=raw['goals'].copy()
        return raw
    require({'club', 'teams', 'year', 'week', 'results'} <= raw.keys(), 'Incomplete legacy save')
    canonical = json.dumps(raw, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf8')
    seed = int.from_bytes(hashlib.sha256(canonical).digest())
    result = new(raw['club'], seed=seed, models=False)
    result.pop('_rosters', None)
    result.pop('attribute_profile',None)
    result.pop('position_model',None)
    result.pop('lineup_model',None)
    result.pop('staff_system',None)
    result.pop('manager_state',None)
    result.pop('economy_model',None)
    result.update(raw)
    result.update(schema_version=SCHEMA_VERSION, database_version=DATABASE_VERSION,
                  career_id=hashlib.sha256(canonical).hexdigest()[:32],
                  rng_state=random.Random(seed).getstate())
    expected = schedule(result['year'])
    stored = raw.get('schedule')
    if stored is not None:
        actual = [{key: fixture[key] for key in ('week', 'home', 'away')} for fixture in stored]
        require(actual == expected or actual == schedule(2000), 'Legacy fixture cannot be mapped')
    result['schedule'] = expected
    result.pop('board_targets',None)
    result.pop('managed_stats',None)
    result['legacy_goals']=result['goals'].copy()
    ids_by_name = defaultdict(list)
    for pid, p in P.items():
        ids_by_name[p['name']].append(pid)
    for week in result['results']:
        for match in week:
            converted = []
            for minute, club, name in match.get('events', []):
                ids = ids_by_name[name]
                if len(ids) == 1:
                    converted.append([minute, club, ids[0]])
                else:
                    converted.append([minute, club, None, name])
            match['events'] = converted
    return result

def validate_table(rows):
    require(set(rows) == set(TEAMS), 'Invalid club table')
    for row in rows.values():
        require(set(row) == {'p', 'w', 'd', 'l', 'gf', 'ga'} and
                all(integer(value, 0) for value in row.values()), 'Invalid standings row')
        require(row['p'] == 3 * row['w'] + row['d'], 'Invalid points')

def catalog(s):
    generated=s.get('generated',{})
    require(isinstance(generated,dict),'Invalid academy catalog')
    for pid,p in generated.items():
        require(re.fullmatch(r'y[0-9]{4}-[0-9]+',pid) and p['id']==pid and p['kind']=='fictional'
                and p['club'] in TEAMS and integer(p['number'],1,99) and numeric(p['rating'],4,20)
                and integer(p['pa_base'],40,200) and isinstance(p['name'],str)
                and p['pos'] in ('GK','CB','LB','RB','CM','DM','AM','RM','LM','CF','ST','SS')
                and len(p['citizenships'])==1 and p['citizenships'][0]['country_id'] in COUNTRIES,
                'Invalid academy player')
        date.fromisoformat(p['dob'])
    return ChainMap(P,HISTORICAL,generated)

def validate_preferences(prefs):
    require(isinstance(prefs,dict) and set(prefs)<={
        'players','staff','player_filters','staff_filters'},'Invalid search preferences')
    for kind in ('players','staff'):
        rows=prefs.get(kind,[])
        require(isinstance(rows,list) and len(rows)<=250
                and all(isinstance(uid,str) and len(uid)<=128 for uid in rows)
                and len(set(rows))==len(rows),'Invalid shortlist')
    for name in ('player_filters','staff_filters'):
        values=prefs.get(name,{})
        require(isinstance(values,dict) and len(values)<=30
                and all(isinstance(k,str) and isinstance(v,str) and len(k)<=40 and len(v)<=180
                         for k,v in values.items()),'Invalid search filters')


def validate_match_options(s):
    from futbol_kurallari import CORNERS,DEFENCE,FREE,ROLES,TAKERS
    from taktik import OPTIONS,ROLES as TACTICAL_ROLES
    require(integer(s.get('tactics_model',0),0,1),'Invalid tactical model')
    if s.get('tactics_model'):
        require(s.get('match_model')==4,'Invalid tactical engine')
        ROLES=TACTICAL_ROLES
    if 'tactical_plans' in s:
        plans=s['tactical_plans']
        require(s.get('tactics_model')==1 and isinstance(plans,dict) and set(plans)<=set(TEAMS),
                'Invalid tactical plans')
        for row in plans.values():
            require(isinstance(row,dict) and set(row)<=set(OPTIONS)
                    and all(integer(v,-1,1) for v in row.values()),'Invalid tactical order')
    for key in ('set_pieces','player_roles'):
        values=s.get(key,{})
        require(isinstance(values,dict) and set(values)<=set(TEAMS),'Invalid tactic clubs')
        for row in values.values():
            require(isinstance(row,dict) and len(row)<=64,'Invalid tactic settings')
            if key=='player_roles':
                require(all(isinstance(pid,str) and role in ROLES for pid,role in row.items()),'Invalid player role')
            else:
                options={'corner':CORNERS,'defence':DEFENCE,'free_approach':FREE}
                require(set(row)<=set(options)|set(TAKERS)|{'target'},'Invalid set-piece option')
                require(all(isinstance(value,str) and len(value)<=80 and (name not in options or value in options[name])
                            for name,value in row.items()),'Invalid set-piece choice')


def validate(s):
    validate_match_options(s)
    if 'ui_preferences' in s:validate_preferences(s['ui_preferences'])
    P=catalog(s)
    require(s['club'] in TEAMS and isinstance(s['manager'], str), 'Invalid manager or club')
    require(integer(s['year'], 2000, 9998) and integer(s['week'], 1, 35), 'Invalid calendar')
    from mevkiler import LAYOUTS
    require(integer(s.get('position_model',0),0,1),'Invalid position model')
    require(integer(s.get('lineup_model',0),0,1) and
            (not s.get('lineup_model') or s.get('position_model')), 'Invalid lineup model')
    formations=LAYOUTS if s.get('position_model') else FORMATIONS
    require(s['formation'] in formations and s['style'] in STYLES and s['lang'] in ('TR', 'EN')
            and integer(s['cap'], 0, 99), 'Invalid tactics or language')
    require(s.get('training', 'Normal') in ('Normal', 'Rest', 'Development') and
            s.get('match_mode', 'live') in (('live','quick','2d') if s.get('match_model') in (1,2,3,4) else ('live','quick'))
            and integer(s.get('match_model',0),0,4), 'Invalid match settings')
    cid = s['career_id']
    require(isinstance(cid, str) and len(cid) == 32 and all(c in '0123456789abcdef' for c in cid), 'Invalid career ID')
    require(integer(s['confidence'], 0, 100), 'Invalid board confidence')
    require(isinstance(s['owners'], dict) and all(pid in P and team in TEAMS for pid, team in s['owners'].items()), 'Invalid registration')
    require(set(s['finance']) == set(TEAMS) and
            all(type(row['cash']) is int for row in s['finance'].values()), 'Invalid finances')
    require(isinstance(s['selected'], list) and len(s['selected']) <= 11 and
            all(pid in P for pid in s['selected']), 'Invalid team selection')
    require(integer(s.get('attribute_profile',1),1,3),'Invalid attribute profile')
    require(type(s.get('auto_xi',False)) is bool,'Invalid automatic lineup preference')
    if 'manual_xi' in s:
        xi=s['manual_xi']
        require(isinstance(xi,list) and len(xi)==11 and
                all(isinstance(pid,str) and pid in P for pid in xi) and len(set(xi))==11,
                'Invalid manual lineup')
    require(all(pid in P and integer(n, 1, 99) for pid, n in s.get('numbers', {}).items()), 'Invalid shirt numbers')
    for pid, z in s.get('fitness', {}).items():
        require(pid in P and isinstance(z, dict), 'Unknown player state')
        require({'condition','morale','form','injury','apps'} <= z.keys(), 'Incomplete player state')
        ranges = {'condition': (0, 100), 'morale': (0, 100), 'form': (0, 10),
                  'ability': (1, 20), 'potential': (1, 20)}
        require(all(key not in z or numeric(z[key], *bounds) for key, bounds in ranges.items()), 'Invalid player ratings')
        require(all(key not in z or integer(z[key], 0) for key in
                    ('injury', 'apps', 'minutes', 'wage', 'contract', 'cards', 'ban')), 'Invalid player counters')
    if 'weekly_feedback' in s:
        report = s['weekly_feedback']
        require(isinstance(report, dict) and report.get('club') in TEAMS
                and integer(report.get('year'), 2000, s['year'])
                and integer(report.get('week'), 1, 34)
                and isinstance(report.get('players'), dict),
                'Invalid weekly feedback')
        for pid, row in report['players'].items():
            require(pid in P and isinstance(row, dict), 'Invalid feedback player')
            ranges = dict(minutes=(0,90), condition=(0,100), morale=(0,100),
                          form=(0,10))
            require(all(numeric(row.get(key), *bounds) for key,bounds in ranges.items())
                    and integer(row.get('injury'), 0)
                    and (row.get('age') == '?' or type(row.get('age')) is int),
                    'Invalid weekly player values')
            deltas = dict(minute_change=(-90,90), condition_change=(-100,100),
                          form_change=(-10,10), training=(0,1))
            require(all(key in row and (row[key] is None or numeric(row[key], *bounds))
                        for key,bounds in deltas.items()), 'Invalid weekly deltas')
    validate_training(s, P)
    validate_staff(s, P)
    validate_manager(s)
    for key, size in (('news', 3), ('transfers', 5)):
        require(isinstance(s[key], list) and all(isinstance(row, list) and len(row) == size for row in s[key]), 'Invalid ' + key)
    for field in ('goals','legacy_goals'):
        require(all(pid in P and integer(goals,0) for pid,goals in s.get(field,{}).items()),'Invalid scorer totals')
    expected = schedule(s['year'])
    require(s['schedule'] == expected, 'Invalid fixture sequence')
    require(isinstance(s['results'], list) and len(s['results']) == s['week'] - 1, 'Invalid result weeks')
    combined = {'teams': table()}
    for index, rows in enumerate(s['results']):
        require(isinstance(rows, list) and len(rows) == 9, 'Invalid results for week')
        pairs = {(m['home'], m['away']) for m in expected[index*9:(index+1)*9]}
        require(len(pairs) == len(rows) and pairs == {(m['home'], m['away']) for m in rows}, 'Results do not match fixture')
        for match in rows:
            home, away, x, y = (match[key] for key in ('home', 'away', 'x', 'y'))
            require(integer(x, 0) and integer(y, 0), 'Invalid result score')
            for event in match['events']:
                require(isinstance(event, list) and len(event) in (3, 4), 'Invalid match event')
                require(integer(event[0], 1, 90) and event[1] in (home, away) and
                        ((len(event) == 3 and event[2] in P) or
                         (len(event) == 4 and event[2] is None and isinstance(event[3], str))), 'Invalid match event player')
            require(all(pid in P and integer(m, 1, 90) for pid, m in match.get('minutes', {}).items()), 'Invalid match minutes')
            if 'shots' in match:
                require('minutes' in match and all(len(event) == 3 and event[2] in match['minutes']
                        for event in match['events']), 'Missing match participant')
                require(sum(event[1] == home for event in match['events']) == x and
                        sum(event[1] == away for event in match['events']) == y, 'Goals do not match events')
                require(len(match['shots']) == 2 and integer(match['shots'][0], x)
                        and integer(match['shots'][1], y), 'Invalid shot totals')
            if 'play' in match:
                require(set(match['ratings'])==set(match['minutes'])
                        and all(numeric(mark,3,10) for mark in match['ratings'].values()),'Invalid ratings')
                shots,on_target,saves=[0,0],[0,0],[0,0]
                for minute,side,pid,event,other in match['play']:
                    require(integer(minute,0,90) and integer(side,0,1) and pid in P
                            and (other is None or other in P),'Invalid commentary event')
                    require(event in ('sub','wide','saved','on_target','goal','pass','yellow','red','blocked','pass_failed','tackle','kickoff','throw','corner','freekick','penalty','goal_kick','offside','foul','advantage','second_yellow','indirect','clearance','header','throw_awarded','set_piece_goal','rebound'),'Invalid commentary category')
                    if event in SHOT_EVENTS:
                        shots[side]+=1
                        on_target[side]+=event not in ('wide','blocked')
                        saves[1-side]+=event=='saved'
                require(shots==match['shots'] and on_target==match['on_target'] and saves==match['saves'],'Invalid event totals')
            apply_score(combined, home, away, x, y)
    validate_table(s['teams'])
    require(s['teams'] == combined['teams'], 'Standings do not match results')
    require(isinstance(s['history'], list), 'Invalid history')
    for season in s['history']:
        validate_table(season['teams'])
        require(integer(season['year'], 2000, s['year']-1) and season['club'] in TEAMS, 'Invalid historical season')
    rng = s['rng_state']
    s['rng_state'] = (rng[0], tuple(rng[1]), rng[2])
    random.Random(0).setstate(s['rng_state'])
    return s

def validate_manager(s):
    require(integer(s.get('economy_model',0),0,2),'Invalid economy model')
    if 'last_tactical_review' in s:
        review=s['last_tactical_review']
        require(isinstance(review,dict) and integer(review.get('year'),2000,s['year'])
                and integer(review.get('week'),1,34) and review.get('home') in TEAMS
                and review.get('away') in TEAMS and review['away']!=review['home']
                and isinstance(review.get('opening'),list) and len(review['opening'])==2,
                'Invalid tactical review')
        for row in review['opening']:
            require(isinstance(row,dict) and row.get('formation') in FORMATIONS
                    and isinstance(row.get('strengths'),dict) and set(row['strengths'])=={'GK','D','M','F'}
                    and all(type(v) in (float,int) and 0<=v<1000 for v in row['strengths'].values())
                    and integer(row.get('mismatches'),0,11) and type(row.get('fitness')) in (float,int)
                    and 0<=row['fitness']<=100,'Invalid tactical data')
    if 'inbox' in s:
        require(s.get('match_model') in (1,2,3,4) and isinstance(s['inbox'],list) and len(s['inbox'])<=12,'Invalid inbox')
        for entry in s['inbox']:
            require(isinstance(entry,dict) and integer(entry.get('year'),2000,s['year'])
                    and integer(entry.get('week'),1,34) and entry.get('club') in TEAMS
                    and isinstance(entry.get('items'),list) and len(entry['items'])<=7,'Invalid inbox entry')
            for item in entry['items']:
                require(isinstance(item,list) and len(item)==4 and integer(item[0],1,9)
                        and item[1] in ('injury','recovery','tired','form','youth','contract','transfer','job','fixture')
                        and isinstance(item[2],str) and type(item[3]) in (int,float,str),'Invalid inbox item')
    review=s.get('last_tactical_review',{})
    if 'analysis' in review:
        audit=review['analysis']
        require(s.get('match_model') in (1,2,3,4) and isinstance(audit,dict)
                and isinstance(audit.get('periods'),list) and len(audit['periods'])==18
                and isinstance(audit.get('decisions'),list),'Invalid match audit')
        if 'flow' in audit:
            flow=audit['flow']
            require(s.get('match_model') in (2,3,4) and isinstance(flow,dict)
                    and set(flow)=={'possession','passes','completed','turnovers','recoveries'}
                    and all(isinstance(pair,list) and len(pair)==2 and all(integer(n,0,90) for n in pair)
                            for pair in flow.values())
                    and all(a<=b for a,b in zip(flow['completed'],flow['passes']))
                    and sum(flow['possession'])<=90,'Invalid positional match totals')
        for i,row in enumerate(audit['periods'],1):
            require(isinstance(row,list) and len(row)==5 and row[0]==i*5
                    and all(isinstance(pair,list) and len(pair)==2
                            and all(type(value) in (float,int) and 0<=value<=100 for value in pair)
                            for pair in row[1:]),'Invalid match period')
        from taktik import EXTRA
        keys=('press','tempo','width','style')+(EXTRA if s.get('tactics_model') else ())
        for row in audit['decisions']:
            require(isinstance(row,list) and len(row)==5 and integer(row[0],0,89 if s.get('match_model') in (2,3,4) else 85) and integer(row[1],0,1)
                    and row[2] in keys,'Invalid match instruction')
            if row[2] in EXTRA:
                require(all(integer(v,-1,1) for v in row[3:]),'Invalid live tactical order')
        if 'advanced_regains' in audit:
            rows=audit['advanced_regains']
            require(s.get('tactics_model')==1 and isinstance(rows,list) and len(rows)==2
                    and all(integer(v,0,90) for v in rows),'Invalid advanced recoveries')
        if 'role_changes' in audit:
            from taktik import ROLES
            rows=audit['role_changes']
            require(s.get('tactics_model')==1 and isinstance(rows,list) and len(rows)<=990,
                    'Invalid role changes')
            players=catalog(s)
            for row in rows:
                require(isinstance(row,list) and len(row)==5 and integer(row[0],0,89)
                        and integer(row[1],0,1) and isinstance(row[2],str) and row[2] in players
                        and row[3] in ROLES and row[4] in ROLES,'Invalid role change')
        if 'chances' in audit:
            chances=audit['chances']
            players=catalog(s)
            require(s.get('match_model')==4 and isinstance(chances,list) and len(chances)<=90,
                    'Invalid match chances')
            for row in chances:
                require(isinstance(row,list) and len(row)==6 and integer(row[0],1,90)
                        and integer(row[1],0,1) and isinstance(row[2],str) and row[2] in players
                        and row[3] in SHOT_EVENTS and all(numeric(value,0,1) for value in row[4:]),
                        'Invalid match chance')
    if 'manager_state' not in s:return
    m=s['manager_state']
    require(isinstance(m,dict) and m.get('version')==1 and m.get('id')==s['career_id']
            and m.get('active_team')==(s['club'] if s['employed'] else None)
            and all(isinstance(m.get(k),list) for k in ('spells','honours','applications'))
            and isinstance(m.get('vacancies'),dict),'Invalid manager state')
    reasons=('opening','resigned','moved','performance','financial')
    require(m.get('decision') in ('none','hired',*reasons),'Invalid employment decision')
    opened=0
    for row in m['spells']:
        require(isinstance(row,dict) and row.get('team') in TEAMS and integer(row.get('start'),68001)
                and (row.get('end') is None or integer(row.get('end'),row['start']))
                and (row.get('reason') is None or row['reason'] in reasons)
                and isinstance(row.get('stats'),dict)
                and all(integer(row['stats'].get(k),0) for k in ('p','w','d','l','gf','ga')),
                'Invalid employment record')
        opened+=row['end'] is None
    require(opened==int(s['employed']) and (not opened or m['spells'][-1]['team']==s['club']),
            'Invalid active employment')
    for row in m['honours']:
        require(isinstance(row,dict) and row.get('team') in TEAMS and integer(row.get('year'),2000,s['year']),
                'Invalid manager honour')
    for team,row in m['vacancies'].items():
        require(team in TEAMS and team!=m['active_team'] and isinstance(row,dict)
                and row.get('reason') in reasons and integer(row.get('opened'),68001)
                and integer(row.get('closes'),row['opened']+1) and integer(row.get('required'),0,100)
                and integer(row.get('target'),1,18),'Invalid vacancy')
    seen=set()
    for row in m['applications']:
        require(isinstance(row,dict) and row.get('team') in TEAMS and integer(row.get('opened'),68001)
                and integer(row.get('due'),row['opened']+1)
                and row.get('status') in ('pending','rejected','offered','accepted','declined','expired')
                and (row.get('expires') is None or integer(row['expires'],row['due']))
                and row.get('reason') in (None,'qualified','requirements','deadline'),
                'Invalid application')
        key=(row['team'],row['opened'])
        require(key not in seen,'Duplicate application')
        seen.add(key)
        if row['status']=='offered':
            require(row['expires'] is not None and m['vacancies'].get(row['team'],{}).get('opened')==row['opened'],
                    'Invalid open offer')


def validate_staff(s,players):
    from personel import ROLES,SKILLS,TASKS,REPORT_LIMIT
    if 'staff_system' not in s:return
    st=s['staff_system']
    require(isinstance(st,dict) and st.get('version')==1 and isinstance(st.get('pool'),dict)
            and 120<=len(st['pool'])<=(150 if s.get('economy_model') else 120), 'Invalid staff system')
    pool=st['pool']
    for pid,row in pool.items():
        require(isinstance(pid,str) and isinstance(row,dict) and isinstance(row.get('name'),str)
                and row.get('role') in ROLES and row.get('source')=='fictional'
                and integer(row.get('wage'),1) and isinstance(row.get('skills'),dict)
                and set(row['skills'])==set(SKILLS)
                and all(integer(x,1,20) for x in row['skills'].values()),'Invalid staff row')
        require((row.get('club') is None and row.get('start') is None and row.get('end') is None)
                or (row.get('club') in TEAMS and integer(row.get('start'),2000,s['year'])
                    and integer(row.get('end'),s['year']+1)), 'Invalid staff contract')
    delegation=st.get('delegation')
    require(isinstance(delegation,dict),'Invalid delegation')
    for team,tasks in delegation.items():
        require(team in TEAMS and isinstance(tasks,dict),'Invalid delegation club')
        for task,pid in tasks.items():
            require(task in TASKS and isinstance(pid,str) and pid in pool
                    and pool[pid]['club']==team and pool[pid]['role']==TASKS[task][0],
                    'Invalid delegate')
    booked=st.get('booked')
    require(isinstance(booked,dict) and all(t in TEAMS and integer(w,0) for t,w in booked.items()),
            'Invalid payroll periods')
    for key in ('jobs','reports'):
        rows=st.get(key)
        require(isinstance(rows,list) and len(rows)<=REPORT_LIMIT,'Invalid scouting history')
        used=set()
        for row in rows:
            require(isinstance(row,dict) and row.get('club') in TEAMS and isinstance(row.get('scout'),str)
                    and row['scout'] in pool and pool[row['scout']]['role']=='scout'
                    and isinstance(row.get('player'),str) and row['player'] in players
                    and integer(row.get('due'),0),'Invalid scouting row')
            if key=='jobs':
                require(row['scout'] not in used and pool[row['scout']]['club']==row['club'],
                        'Invalid active scouting assignment')
                used.add(row['scout'])
            else:
                bands=row.get('bands')
                require(integer(row.get('year'),2000,s['year']) and integer(row.get('week'),1,34)
                        and integer(row.get('confidence'),1,20) and isinstance(bands,list)
                        and len(bands)==2 and all(isinstance(b,list) and len(b)==2 and
                        integer(b[0],1,19) and integer(b[1],b[0]+1,20) for b in bands),
                        'Invalid scouting report')
                if 'groups' in row:
                    groups=row['groups']
                    require(isinstance(groups,dict) and set(groups)=={'technical','mental','physical'}
                            and all(isinstance(b,list) and len(b)==2 and integer(b[0],1,19)
                                    and integer(b[1],b[0]+1,20) for b in groups.values()),
                            'Invalid scouted attribute ranges')


def validate_training(s, players):
    from antrenman import FOCUSES, INTENSITIES, MONTH_LIMIT
    plans = s.get('individual_training', {})
    require(type(s.get('auto_training',False)) is bool and isinstance(plans,dict)
            and all(pid in players and isinstance(plan,list) and len(plan)==2
                    and plan[0] in FOCUSES and plan[1] in INTENSITIES
                    for pid,plan in plans.items()), 'Invalid individual training plans')
    history = s.get('monthly_training', [])
    require(isinstance(history,list) and len(history)<=MONTH_LIMIT, 'Invalid monthly training history')
    active = [s['training_month']] if 'training_month' in s else []
    seen = set()
    plan_keys = {f'{focus}/{level}' for focus in FOCUSES for level in INTENSITIES}
    for report in history+active:
        require(isinstance(report,dict) and report.get('club') in TEAMS and
                isinstance(report.get('players'),dict) and
                integer(report.get('last_week'),1,34) and integer(report.get('weeks'),1,5),
                'Invalid monthly training report')
        month = report.get('month')
        require(isinstance(month,str) and len(month)==7 and month[:4].isascii()
                and month[:4].isdigit() and month[4:] in tuple(f'-{m:02d}' for m in range(1,13)),
                'Invalid training month')
        key = (month,report['club'])
        require(key not in seen,'Duplicate training month')
        seen.add(key)
        for pid,row in report['players'].items():
            require(pid in players and isinstance(row,dict) and isinstance(row.get('plans'),dict)
                    and type(row.get('youth')) is bool, 'Invalid training player')
            require(all(k in plan_keys and integer(n,1,5) for k,n in row['plans'].items()),
                    'Invalid monthly plan')
            require(all(integer(row.get(k),0,5) for k in ('weeks','participation','team_weeks','injured_weeks'))
                    and integer(row.get('injury'),0) and integer(row.get('minutes'),0,450)
                    and numeric(row.get('condition'),0,100) and numeric(row.get('morale'),0,100)
                    and numeric(row.get('form'),0,10) and numeric(row.get('training'),0,5)
                    and numeric(row.get('recovery'),0,35), 'Invalid monthly measurements')
    annual = s.get('season_development')
    if 'season_development' in s:
        require(isinstance(annual,dict) and annual.get('club') in TEAMS
                and integer(annual.get('year'),2000,s['year']-1)
                and isinstance(annual.get('changes'),dict)
                and all(pid in players and numeric(delta,-20,20)
                        for pid,delta in annual['changes'].items()), 'Invalid annual development')


def validate_world(s):
    P=catalog(s)
    require(s['currency'] in CURRENCIES,'Invalid currency')
    stats=s['managed_stats']
    require(set(stats)=={'p','w','d','l','gf','ga'} and all(integer(v,0) for v in stats.values())
            and stats['p']==3*stats['w']+stats['d'] and stats['w']+stats['d']+stats['l']<=s['week']-1,
            'Invalid management record')
    require(type(s['employed']) is bool and integer(s['manager_rep'],10,100)
            and integer(s['board_misses'],0),'Invalid manager state')
    for key,minimum,maximum in (('club_reputation',15,90),('board_targets',1,18)):
        require(set(s[key])==set(TEAMS) and all(integer(v,minimum,maximum) for v in s[key].values()),'Invalid '+key)
    require(all(team in TEAMS for team in s['job_offers']), 'Invalid job offers')
    for pid,row in s['retired'].items():
        require(pid in P and pid not in s['owners'] and pid not in s['released'] and
                isinstance(row,list) and len(row)==2 and integer(row[0],2000,s['year']) and
                (row[1] is None or row[1] in TEAMS),'Invalid retirement')
    require(all(pid in P and pid not in s['owners'] and integer(year,2000,s['year'])
            for pid,year in s['released'].items()),'Invalid released player')
    budget_keys=('transfer_budget','wage_budget','wages_paid','operating_paid','fees_paid','fees_received','signing_paid','debt','academy_level','facilities',*FLOW)
    if s.get('economy_model')==2:
        require(all(integer(row.get('commercial'),0) for row in s['finance'].values()),'Invalid commercial revenue')
    require(all(all(integer(row[key],0) for key in budget_keys) for row in s['finance'].values()),'Invalid budget')
    for offer in s['offers']:
        require(offer['pid'] in P and offer['buyer'] in TEAMS and offer['seller'] in TEAMS
                and integer(offer['fee'],0) and integer(offer['year'],2000,s['year'])
                and integer(offer['week'],1,34) and offer['status'] in ('open','expired','accepted','rejected')
                and integer(offer['wage'],100,50000) and integer(offer['years'],1,5)
                and integer(offer['signing'],0,2000000) and offer['role'] in ('Starter','Rotation'),'Invalid offer')
        if 'kind' in offer:
            require(s.get('transfer_model')==1 and offer['kind']=='loan' and offer.get('share') in (25,50,75,100),
                    'Invalid loan offer')
    require(integer(s.get('transfer_model',0),0,1),'Invalid transfer model')
    if s.get('transfer_model'):
        loans=s.get('loans',{})
        require(isinstance(loans,dict),'Invalid loans')
        for pid,row in loans.items():
            require(pid in P and pid in s['fitness'] and isinstance(row,dict) and row.get('parent') in TEAMS
                    and row.get('borrower') in TEAMS and row['parent']!=row['borrower']
                    and s['owners'].get(pid)==row['borrower'] and type(row.get('share')) is int
                    and row['share'] in (25,50,75,100),'Invalid loan')
        payments=s.get('transfer_payments',[])
        require(isinstance(payments,list),'Invalid transfer payments')
        for row in payments:
            require(isinstance(row,list) and len(row)==5 and row[0]==s['year'] and integer(row[1],s['week'],34)
                    and row[2] in TEAMS and row[3] in TEAMS and row[2]!=row[3] and integer(row[4],1),
                    'Invalid transfer payment')
        withdrawals=s.get('transfer_withdrawals',{})
        require(isinstance(withdrawals,dict),'Invalid transfer withdrawals')
        for pid,row in withdrawals.items():
            require(pid in P and isinstance(row,list) and len(row)==4 and row[0]==s['year'] and row[1] in (1,18)
                    and row[2] in TEAMS and row[3] in TEAMS and row[2]!=row[3],'Invalid transfer withdrawal')
    else:
        require(not any(key in s for key in ('loans','transfer_payments','transfer_withdrawals')),
                'Missing transfer model')
    require(all(isinstance(row,list) and len(row)==3 and row[2] in TEAMS for row in s['jobs']),'Invalid job history')
    require(isinstance(s['world_history'],list) and isinstance(s['contract_events'],list),'Invalid world history')
    if 'living_club' in s:
        validate_living_club(s)
    for pid,mode in s['sale_status'].items():
        modes=('listed','blocked','loan') if s.get('transfer_model') else ('listed','blocked')
        require(pid in P and mode in modes,'Invalid sale status')
    for stats in [s['season_stats'],*(h.get('player_stats',{}) for h in s['history'])]:
        require(isinstance(stats,dict),'Invalid player statistics')
        for pid,clubs in stats.items():
            require(pid in P and all(team in TEAMS and set(row)==set(FIELDS)
                    and all(integer(v,0) for v in row.values()) for team,row in clubs.items()),'Invalid statistical row')
    return s


def validate_living_club(s):
    from yasayan_kulup import PRESS_KINDS
    life=s['living_club']
    require(isinstance(life,dict) and 'manager_state' in s,'Invalid living club')
    fans=life.get('fans')
    require(isinstance(fans,dict) and set(fans)==set(TEAMS),'Invalid supporter data')
    for row in fans.values():
        require(isinstance(row,list) and len(row)==3 and integer(row[0],0,100)
                and integer(row[1],-5,5) and integer(row[2],-10,10),'Invalid supporter record')
    board=life.get('board')
    require(isinstance(board,dict) and board.get('club')==s['club']
            and isinstance(board.get('form'),list) and len(board['form'])<=6
            and all(type(p) is int and p in (0,1,3) for p in board['form'])
            and integer(board.get('sport'),0,8) and integer(board.get('fiscal'),0,8)
            and integer(board.get('risk'),0,100) and integer(board.get('meeting'),0,34)
            and type(board.get('used_recovery')) is bool,'Invalid board review')
    for key in ('promise','recovery'):
        if key in life:
            row=life[key]
            require(isinstance(row,list) and len(row)==2 and integer(row[0],1,3)
                    and integer(row[1],0,(3-row[0])*3),'Invalid club commitment')
    if 'question' in life:
        row=life['question']
        require(isinstance(row,list) and len(row)==5 and row[0]==s['year'] and integer(row[1],1,34)
                and row[2] in ('derby','poor','streak','transfer') and row[3]==s['club']
                and isinstance(row[4],str),'Invalid press question')
    briefs=life.get('briefs')
    require(isinstance(briefs,list) and len(briefs)<=30,'Invalid press archive')
    for row in briefs:
        require(isinstance(row,list) and len(row)==6 and integer(row[0],2000,s['year'])
                and integer(row[1],1,34) and row[2] in PRESS_KINDS and row[3] in TEAMS
                and all(isinstance(v,str) for v in row[4:]),'Invalid press article')
        if row[2]=='budget':
            require(len(row[5])<=8 and row[5].isdecimal(),'Invalid budget report')

def decode(text):
    try:
        raw = json.loads(text)
        s = migrate(raw)
        return validate_world(prepare(validate(s)))
    except SaveError:
        raise
    except (KeyError, TypeError, ValueError, AttributeError, IndexError, OverflowError) as exc:
        raise SaveError('Invalid save data') from exc

def encode(s):
    data = payload(s)
    data['database_version'] = DATABASE_VERSION
    return json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':'))

def atomic_write(path, text):
    with tempfile.NamedTemporaryFile('w', encoding='utf8', dir=path.parent,
                                     prefix=path.name + '.', suffix='.tmp', delete=False) as stream:
        tmp = Path(stream.name)
        try:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)

def backup_path(path):
    return path.with_name(path.stem + '.backup' + path.suffix)

def save_game(s, path):
    path = Path(path)
    text = encode(s)
    decode(text)
    if path.exists():
        try:
            previous = path.read_text(encoding='utf-8-sig')
            decode(previous)
        except (SaveError, UnicodeError):
            pass
        else:
            atomic_write(backup_path(path), previous)
    atomic_write(path, text)

def load_game(path):
    try:
        return decode(Path(path).read_text(encoding='utf-8-sig'))
    except UnicodeError as exc:
        raise SaveError('Invalid save encoding') from exc

def user_directory():
    local=os.environ.get('LOCALAPPDATA')
    return (Path(local) if local else Path.home()) / 'TopAntrenoru' / 'v0.9.3'


def autosave(s, directory=None):
    folder = Path(directory) if directory is not None else user_directory() / 'autosaves'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (s['career_id'] + '.json')
    save_game(s, path)
    return path
