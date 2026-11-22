"""Paired calibration using the project's 2000/01 catalog."""
from collections import Counter
import json
from pathlib import Path
from statistics import mean
from time import perf_counter

from kariyer import new
from mac import Match
from veritabani import TEAMS
from yarisma import expectation


def sample(model):
    s=new('GALATASARAY',seed=1,match_model=model)
    markers=Counter()
    goals=[];shots=[];events=Counter();wins=Counter()
    pass_attempts=completed=0
    possession=[];load=[];keepers=[]
    started=perf_counter()
    for i in range(250):
        pairing=[TEAMS[i%18],TEAMS[(i+1+(i//18)%17)%18]]
        for flip in (0,1):
            home,away=pairing[::(-1 if flip else 1)]
            m=Match(s,{'home':home,'away':away},81000+i)
            distance=0
            while m.minute<90:
                m.step()
                if m.positional:
                    for side,slots in enumerate(m.slots):
                        for role,pid in slots:
                            if role=='GK' and pid in m.pitch.xy:
                                x=m.pitch.xy[pid][0]
                                distance=max(distance,x if side==0 else 1-x)
            f=m.result()
            goals.append(f.x+f.y);shots.append(sum(f.shots))
            events.update(row[3] for row in f.play)
            wins['home' if f.x>f.y else 'away' if f.x<f.y else 'draw']+=1
            tiers=expectation(home),expectation(away)
            if tiers[0]!=tiers[1]:
                stronger=int(tiers[0]>tiers[1])
                scores=(f.x,f.y)
                markers['unequal']+=1
                markers['stronger_win']+=scores[stronger]>scores[1-stronger]
            load.extend(m.loads)
            if m.positional:
                flow=m.pitch.summary()
                pass_attempts+=sum(flow['passes']);completed+=sum(flow['completed'])
                possession.append(flow['possession'][0]/max(1,sum(flow['possession'])))
                keepers.append(distance)
    return dict(games=len(goals),goals=mean(goals),shots=mean(shots),per_match_ms=(perf_counter()-started)*2,
               wins=wins,markers=markers,events=events,pass_attempts=pass_attempts,completed=completed,
               home_possession=mean(possession) if possession else None,load=mean(load),
               keeper_depth_max=max(keepers,default=None),zero=goals.count(0),
               goals5plus=sum(x>=5 for x in goals))


if __name__=='__main__':
    rows={model:sample(model) for model in (1,2)}
    Path('V085_MAC_KALIBRASYONU.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps(rows))
