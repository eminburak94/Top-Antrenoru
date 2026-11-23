"""Manager identity, dated vacancies and human applications."""
from veritabani import TEAMS
from yarisma import standings
from oyuncu import clamp


def clock(s):
    return s['year']*34+s['week']


def blank_stats():
    return dict.fromkeys(('p','w','d','l','gf','ga'),0)


def setup(s, unemployed):
    s['employed']=not unemployed
    team=None if unemployed else s['club']
    s['manager_state']=dict(version=1,id=s['career_id'],active_team=team,spells=[],honours=[],
                            applications=[],vacancies={},decision='none')
    if team:
        begin_spell(s,team)
    else:
        smallest=min(TEAMS,key=lambda t:(s['club_reputation'][t],t))
        vacancy(s,smallest,'opening')


def begin_spell(s,team):
    s['manager_state']['active_team']=team
    s['manager_state']['spells'].append(dict(team=team,start=clock(s),end=None,reason=None,
                                            stats=blank_stats()))
    if s.get('living_club'):
        from yasayan_kulup import begin_spell as board_spell
        board_spell(s)


def vacancy(s,team,reason):
    m=s['manager_state']
    if team==m['active_team'] or team in m['vacancies']:return
    required=max(10,s['club_reputation'][team]-(18 if reason=='opening' else 10))
    m['vacancies'][team]=dict(opened=clock(s),reason=reason,required=required,
                             target=s['board_targets'][team],closes=clock(s)+5)


def application(s,team):
    rows=s['manager_state']['applications']
    opening=s['manager_state']['vacancies'].get(team)
    return next((r for r in reversed(rows) if opening and r['team']==team
                 and r['opened']==opening['opened']),None)


def apply(s,team):
    vacancy_row=s['manager_state']['vacancies'].get(team)
    if not vacancy_row or clock(s)>=vacancy_row['closes'] or application(s,team):return False
    if s.get('match_model',0)==4 and clock(s)+1>=vacancy_row['closes']:
        return False
    s['manager_state']['applications'].append(dict(team=team,opened=vacancy_row['opened'],
           status='pending',due=clock(s)+1,expires=None,reason=None))
    return True


def application_score(s):
    spells=s['manager_state']['spells']
    track=min(8,sum(row['stats']['w'] for row in spells)//6)
    fiscal=4 if any(row['reason']=='financial' for row in spells[-2:]) else 0
    return s['manager_rep']+track-fiscal


def resolve(s):
    m=s['manager_state']
    now=clock(s)
    for team,opening in list(m['vacancies'].items()):
        app=application(s,team)
        if app and app['status']=='pending' and now>=app['due']:
            if s.get('match_model',0)==4 and now>=opening['closes']:
                app.update(status='expired',reason='deadline')
            elif application_score(s)>=opening['required']:
                app.update(status='offered',expires=min(opening['closes'],now+2),reason='qualified')
            else:
                app.update(status='rejected',reason='requirements')
        if app and app['status']=='offered' and now>=app['expires']:
            app.update(status='expired',reason='deadline')
        if now>=opening['closes']:
            del m['vacancies'][team]
    s['job_offers']=[a['team'] for a in m['applications'] if a['status']=='offered']


def clear_controls(s):
    for key in ('manual_xi','auto_xi','individual_training','auto_training','training'):
        s.pop(key,None)
    s.update(selected=[],formation='4-4-2',style='Balanced',managed_stats=blank_stats())


def leave(s,reason):
    m=s['manager_state']
    team=m['active_team']
    if team is None:return False
    m['spells'][-1].update(end=clock(s),reason=reason)
    m.update(active_team=None,decision=reason)
    s['employed']=False
    s['jobs'].append([s['year'],'fired' if reason in ('performance','financial') else reason,team])
    if reason!='moved':
        s['manager_rep']=max(10,s['manager_rep']-(3 if reason=='resigned' else 5))
    clear_controls(s)
    vacancy(s,team,reason)
    return True


def offer(s,team,accept):
    m=s['manager_state']
    row=application(s,team)
    if not row or row['status']!='offered' or clock(s)>=row['expires']:return False
    row['status']='accepted' if accept else 'declined'
    s['job_offers']=[t for t in s['job_offers'] if t!=team]
    if not accept:return True
    if s['employed']:leave(s,'moved')
    del m['vacancies'][team]
    s.update(club=team,employed=True,confidence=70,board_misses=0)
    clear_controls(s)
    begin_spell(s,team)
    s['jobs'].append([s['year'],'hired',team])
    m['decision']='hired'
    return True


def record_match(s,goals,conceded):
    if not s.get('manager_state') or not s['employed']:return
    row=s['manager_state']['spells'][-1]['stats']
    row['gf']+=goals
    row['ga']+=conceded
    row['p']+=3 if goals>conceded else int(goals==conceded)
    row['w' if goals>conceded else 'd' if goals==conceded else 'l']+=1


def open_entry_job(s, ranking):
    m=s['manager_state']
    score=application_score(s)
    now=clock(s)
    for team,opening in m['vacancies'].items():
        app=application(s,team)
        if ((app and app['status']=='offered') or
            score>=opening['required'] and
            ((app and app['status']=='pending') or (app is None and now+1<opening['closes']))):
            return
    pool=[team for team in ranking[-6:] if team not in m['vacancies']]
    if not pool:
        return
    team=min(pool,key=lambda t:(s['finance'][t]['cash']<0,s['club_reputation'][t],t))
    vacancy(s,team,'opening')
    opening=m['vacancies'][team]
    # Minimum reputation (10) minus the recent financial dismissal penalty (4).
    opening['required']=6


def weekly(s):
    if 'manager_state' not in s:return
    resolve(s)
    m=s['manager_state']
    if s['week'] not in (7,15,23,31):return
    ranking=standings(s)
    team=m['active_team']
    if team and not s.get('living_club'):
        rank=ranking.index(team)+1
        recent=[match for round_results in s['results'][-4:] for match in round_results
                if team in (match['home'],match['away'])]
        losses=sum((r['x']<r['y'] if r['home']==team else r['y']<r['x']) for r in recent)
        if s['confidence']<=15 and rank>s['board_targets'][team] and losses>=3:
            leave(s,'performance')
        elif s['finance'][team]['cash']<-250000 and s['confidence']<=40 and rank>s['board_targets'][team]:
            leave(s,'financial')
    if len(m['vacancies'])<3:
        bad=[t for rank,t in enumerate(ranking,1) if rank>=s['board_targets'][t]+2
             and rank>=12 and t!=m['active_team'] and t not in m['vacancies']]
        if bad:vacancy(s,bad[-1],'performance')
    if s.get('match_model',0)==4 and not s['employed']:
        open_entry_job(s,ranking)
