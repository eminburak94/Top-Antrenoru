"""Reproducible comparative career audit. No personal save is used."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

CLUBS=('GALATASARAY','GENÇLERBİRLİĞİ','ERZURUMSPOR')


def career(club,seed,limit):
    from kariyer import new,advance,rollover
    from kayit import decode,encode
    from oyuncu import age_at,ability
    from personel import active
    from veritabani import roster,TEAMS
    from yarisma import standings
    from mevkiler import fit_level

    from inspect import signature
    model={'match_model':1} if 'match_model' in signature(new).parameters else {}
    s=new(club,seed=seed,**model)
    start=time.perf_counter()
    for season in range(1,limit+1):
        assert len(s['schedule'])==306
        for _ in range(34):assert advance(s)
        assert sum(len(w) for w in s['results'])==306
        if season not in (10,25,50,100):
            assert rollover(s)
            continue
        ai=[t for t in TEAMS if t!=s['club'] or not s['employed']]
        all_rows=list(s['finance'].values())
        ledger=[s['finance'][t] for t in ai]
        revenue=sum(sum(r.get(k,0) for k in ('tickets','season_tickets','broadcast','sponsors','commercial')) for r in all_rows)
        squads=[roster(t,s['year'],s) for t in TEAMS]
        players=[p for squad in squads for p in squad]
        ages=[age_at(p,s['year'],s['week']) for p in players]
        fees=[r[4] for r in s['transfers'] if r[4]>0]
        free=sum(r[2]=='Serbest / Free' and r[4]==0 for r in s['transfers'])
        other=len(s['transfers'])-len(fees)-free
        expiries=sum(r[1]=='expired' for r in s['contract_events'])
        average=round(statistics.mean(ability(s,p) for p in players),2)
        serial=encode(s)
        s=decode(serial)
        assert min(map(len,squads))>=11
        leader=standings(s)[0]
        assert rollover(s)
        print(json.dumps(dict(club=club,seed=seed,seasons=season,
            median_cash=int(statistics.median(r['cash'] for r in ledger)),
            negative=sum(r['cash']<0 for r in ledger),debt=sum(r['debt'] for r in ledger),
            staffless=sum(not active(s,t) for t in ai),salary_share=round(sum(r['wages_paid'] for r in all_rows)/revenue,3),
            fees=sum(fees),mean_fee=round(statistics.mean(fees)) if fees else 0,
            median_fee=round(statistics.median(fees)) if fees else 0,paid=len(fees),free=free,
            other=other,expiries=expiries,
            avg_age=round(statistics.mean(a for a in ages if isinstance(a,int)),2),
            avg_ability=average,
            min_squad=min(map(len,squads)),mean_squad=round(statistics.mean(map(len,squads)),2),
            position_gaps=sum(sum(fit_level(p,role)>=2 for p in squad)<n for squad in squads
                for role,n in Counter(('GK','RB','LB','CB','CB','LM','RM','CM','CM','ST','ST')).items()),
            winner=leader,champion_points=s['history'][-1]['teams'][leader]['p'],catalog=len(players),
            save_bytes=len(serial.encode('utf8')),seconds=round(time.perf_counter()-start,2)),ensure_ascii=False),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',nargs=3)
    parser.add_argument('--baseline',action='store_true')
    parser.add_argument('--output',default='V083_KARIYER.csv')
    parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args()
    if args.case:
        club,seed,limit=args.case
        career(club,int(seed),int(limit))
        return
    folder=Path(__file__).resolve().parent
    cases=[('083',folder,club,seed,25 if seed==811 else 10) for club in CLUBS for seed in range(811,816)]
    cases.extend([('083',folder,CLUBS[0],852,50),('083',folder,CLUBS[2],853,100)])
    if args.baseline:
        baseline=folder.parent/'top ant v0.8.2'
        cases.extend(('082',baseline,club,seed,25 if seed==811 else 10) for club in CLUBS for seed in range(811,816))

    def audit(case):
        version,working,club,seed,limit=case
        # The script directory would otherwise take precedence over the working version.
        caller=("import sys,runpy; sys.path.insert(0,'.'); sys.argv="+
                repr([str(folder/'kalibrasyon_v083.py'),'--case',club,str(seed),str(limit)])+
                "; runpy.run_path(sys.argv[0],run_name='__main__')")
        result=subprocess.run([sys.executable,'-B','-X','utf8','-c',caller],cwd=working,
                              capture_output=True,text=True,encoding='utf-8')
        if result.returncode:
            print(case,result.stderr,flush=True)
        rows=[dict(version=version,**json.loads(line)) for line in result.stdout.splitlines()]
        print(version,club,seed,limit,len(rows),result.returncode,flush=True)
        return rows,result.returncode

    with ThreadPoolExecutor(max_workers=args.workers) as pool, open(folder/args.output,'w',newline='',encoding='utf-8-sig') as out:
        writer=None
        failed=False
        for rows,status in pool.map(audit,cases):
            failed|=bool(status)
            if rows and writer is None:
                writer=csv.DictWriter(out,fieldnames=rows[0]);writer.writeheader()
            for row in rows:writer.writerow(row)
            out.flush()
    sys.exit(failed)


if __name__=='__main__':
    main()
