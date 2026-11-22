"""Isolated Model 4 long-career audit, invoked once per club and seed."""
import json
from pathlib import Path
from statistics import median
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

import is_piyasasi as jobs
from kariyer import advance,new,rollover
from kayit import encode,load_game,save_game
from test_v076 import ram
from veritabani import TEAMS,roster

CLUBS=('GALATASARAY','GENÇLERBİRLİĞİ','ERZURUMSPOR')

def run(index, seed, limit):
    start=perf_counter()
    s=new(CLUBS[index],seed=seed,match_model=4,unemployed=index==2)
    extrema=dict(cash_low=float('inf'),cash_high=float('-inf'),debt_high=0,min_squad=99,negative_weeks=0)
    slow_week=0
    yearly=[]
    with TemporaryDirectory() as tmp:
        path=Path(tmp)/'career.json'
        for season in range(1,limit+1):
            season_start=perf_counter()
            assert s['year']==1999+season and s['week']==1
            assert len(s['schedule'])==306
            for w in range(1,35):
                assert s['week']==w
                if not s['employed']:
                    for team in tuple(s['manager_state']['vacancies']):
                        jobs.apply(s,team)
                    for team in tuple(s['job_offers']):
                        if jobs.offer(s,team,True):
                            break
                ts=perf_counter()
                assert advance(s) and len(s['results'][-1])==9
                slow_week=max(slow_week,perf_counter()-ts)
                cash=[row['cash'] for row in s['finance'].values()]
                extrema['cash_low']=min(extrema['cash_low'],*cash)
                extrema['cash_high']=max(extrema['cash_high'],*cash)
                extrema['debt_high']=max(extrema['debt_high'],*(row['debt'] for row in s['finance'].values()))
                extrema['negative_weeks']+=any(x<0 for x in cash)
            assert len(s['results'])==34 and all(sum(row[k] for k in ('w','d','l'))==34 for row in s['teams'].values())
            assert len(s['owners'])==len({p['id'] for team in TEAMS for p in roster(team,s['year'],s)})
            depths=[len(roster(team,s['year'],s)) for team in TEAMS]
            assert min(depths)>=11
            extrema['min_squad']=min(extrema['min_squad'],*depths)
            if season in (25,50,100):
                checkpoint=encode(s)
                save_game(s,path)
                s=load_game(path)
                assert encode(s)==checkpoint
                m=s['manager_state']
                f=list(s['finance'].values())
                row=dict(seasons=season,club=CLUBS[index],active_team=m['active_team'],seed=seed,
                     hired=sum(j[1]=='hired' for j in s['jobs']),fired=sum(j[1]=='fired' for j in s['jobs']),
                     applications=len(m['applications']),rejected=sum(a['status']=='rejected' for a in m['applications']),
                     spells=len(m['spells']),vacancies=len(m['vacancies']),retired=len(s['retired']),generated=len(s['generated']),
                     contract_events=len(s['contract_events']),expired=sum(c[1]=='expired' for c in s['contract_events']),
                     active_contracts=sum(s['fitness'][p]['contract']>s['year'] for p in s['owners']),
                     paid=sum(t[4]>0 for t in s['transfers']),free=sum(t[4]==0 and t[2]=='Serbest / Free' for t in s['transfers']),
                     fees=sum(t[4] for t in s['transfers']),cash_median=int(median(a['cash'] for a in f)),
                     cash_negative=sum(a['cash']<0 for a in f),debt=sum(a['debt'] for a in f),min_squad=min(depths),
                     save=path.stat().st_size,ram=ram(),max_week_seconds=round(slow_week,3),
                     elapsed=round(perf_counter()-start,2),extrema=extrema.copy())
                yearly.append(row)
                print(json.dumps(row,ensure_ascii=False),flush=True)
            assert rollover(s) and s['week']==1 and s['year']==2000+season
            if season in (25,50,100):
                save_game(s,path)
                s=load_game(path)
                assert s['week']==1 and s['year']==2000+season
            if season%10==0:
                print(f'progress {index} {season}/{limit} {perf_counter()-season_start:.2f}s',flush=True)
    return yearly

if __name__=='__main__':
    index,seed,limit=map(int,sys.argv[1:])
    rows=run(index,seed,limit)
    output=Path(f'.build/v088-long-{limit}.json')
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
