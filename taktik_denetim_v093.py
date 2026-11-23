"""Paired Model 4 tactical measurements with fixed teams, fitness and seeds."""
from math import hypot
from statistics import mean
from time import perf_counter

from kariyer import new
from mac import Match
from oyuncu import state
from veritabani import roster


SEEDS=range(9301,9325)
HOME='GALATASARAY'
RIVAL='FENERBAHÇE'
SMALL='ERZURUMSPOR'


def measure(seed,mode=None,value=None,away=RIVAL,enabled=True,capture=True):
    s=new(HOME,seed=9300,match_model=4,tactics_model=enabled)
    if mode=='fitness':
        for p in roster(HOME,s['year'],s):
            state(s,p)['condition']=value
    m=Match(s,{'home':HOME,'away':away},seed)
    m.capture=capture
    back=next(pid for position,pid in m.slots[0] if position=='RB')
    if mode=='role':
        assert m.assign_role(back,value) or m.pitch.role(0,back,'RB')==value
    elif mode and mode not in ('fitness','live'):
        assert m.instruction(mode,value)
    fullback=[]
    line=[]
    while m.minute<90:
        if mode=='live' and m.minute==70:
            m.instruction('line',value)
        m.step()
        if m.pitch.owner and m.minute>70:
            line.extend(m.pitch.xy[pid][0] for position,pid in m.slots[0] if position=='CB')
        if m.pitch.owner and m.pitch.side==0 and back in m.pitch.anchor[0]:
            fullback.append(m.pitch.xy[back][0])
    if not capture:
        return m
    own=[row for row in m.pitch.trace if s['owners'][row['player']]==HOME]
    delivered={(minute,pid,target) for minute,side,pid,event,target in m.play if side==0 and event=='pass'}
    completed=[row for row in own if (row['minute'],row['player'],row['target']) in delivered]
    failed=sum(row[3]=='pass_failed' and row[1]==0 for row in m.play)
    return dict(
        regains=m.pitch.advanced_regains[0],load=m.loads[0],goals=m.x,conceded=m.y,shots=m.shots[0],
        pass_m=mean(hypot((row['origin'][0]-row['destination'][0])*105,
                          (row['origin'][1]-row['destination'][1])*68) for row in own) if own else 0,
        wide=100*sum(abs(row['destination'][1]-.5)>.25 for row in completed)/max(1,len(completed)),
        failed=100*failed/max(1,len(own)),
        back=100*mean(fullback) if fullback else 0,line=100*mean(line) if line else 0,
        fitness=mean(m.player_condition(pid) for position,pid in m.slots[0] if position!='GK'),
    )


def compare(mode,a,b,columns):
    def group(value):
        rows=[measure(seed,mode,value) for seed in SEEDS]
        return {key:round(mean(row[key] for row in rows),2) for key in columns}
    print(mode,a,group(a),b,group(b))


if __name__=='__main__':
    compare('press',-1,1,('regains','load','fitness','shots'))
    compare('width',-1,1,('wide','pass_m','failed','shots'))
    compare('passing',-1,1,('pass_m','failed','shots'))
    compare('role','defensive_back','wingback',('back','shots','conceded'))
    compare('fitness',100,62,('fitness','shots','goals'))
    compare('live',-1,1,('line','shots','conceded'))
    matches=[measure(seed,away=SMALL) for seed in SEEDS]
    print('strong vs small', {k:round(mean(row[k] for row in matches),2)
                               for k in ('goals','conceded','shots')})
    for enabled in (False,True):
        start=perf_counter()
        for seed in SEEDS:
            measure(seed,enabled=enabled,capture=False)
        print('seconds (24 matches, no capture)',enabled,round(perf_counter()-start,3))
