from collections import Counter
from json import dumps
from random import Random
from pathlib import Path
from kariyer import new
from mac import Match
from veritabani import TEAMS
from yarisma import expectation
from futbol_kalibrasyonu import shot_probabilities
out={}
skills={'Finishing':13,'Composure':13}
base={key:10 for key in ('Reflexes','Positioning','Handling','One on ones')}
rng=Random(1807)
trials=[(rng.random(),rng.random()) for _ in range(10000)]
for reflex in (5,17):
    t,s=shot_probabilities(.23,.18,.25,1,.70,skills,dict(base,Reflexes=reflex))
    out[f'micro_{reflex}']=dict(target_probability=t,save_probability=s,
           targets=sum(a<t for a,b in trials),saves=sum(a<t and b<s for a,b in trials))
for model in (3,4):
    s=new('GALATASARAY',seed=1,match_model=model)
    for reflex in (5,17):
        row=Counter()
        for seed in range(81000,81300):
            m=Match(s,dict(home=TEAMS[0],away=TEAMS[1]),seed)
            k=next(pid for role,pid in m.slots[1] if role=='GK')
            m.profiles[k]=dict(m.profiles[k],Reflexes=reflex)
            for minute in range(90):m.step()
            f=m.result()
            row.update(goals=f.x,saves=f.saves[1],targets=f.on_target[0])
        out[f'full_{model}_{reflex}']=row
    groups={}
    for i in range(250):
        pair=[TEAMS[i%18],TEAMS[(i+1+(i//18)%17)%18]]
        for home,away in (pair,pair[::-1]):
            m=Match(s,dict(home=home,away=away),81000+i)
            for minute in range(90):m.step()
            f=m.result()
            for side,team in enumerate((home,away)):
                group=groups.setdefault(expectation(team),Counter())
                team_score,rival_score=((f.x,f.y) if side==0 else (f.y,f.x))
                flow=m.pitch.summary()
                group.update(apps=1,wins=team_score>rival_score,draws=team_score==rival_score,
                  home_apps=side==0,home_wins=side==0 and team_score>rival_score,
                  goals=team_score,shots=f.shots[side],possession=flow['possession'][side],
                  passes=flow['passes'][side],completed=flow['completed'][side],
                  set_piece_goals=sum(r[1]==side and r[3]=='set_piece_goal' for r in f.play))
    out[f'tiers_{model}']=groups
print(dumps(out,indent=2))
Path('V087_KALECI_TAKIM_HAM.json').write_text(dumps(out,indent=2),encoding='utf8')
