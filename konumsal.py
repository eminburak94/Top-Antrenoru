"""Coarse positional phases shared by match decisions and the 2D view."""
from mevkiler import LAYOUTS,coordinates

LEVELS=('Low','Normal','High')
KEYS=('press','tempo','width')


def phase(match,side):
    own,opp=match.strengths[side],match.strengths[1-side]
    press,tempo,width=match.instructions[side]
    rival_press=match.instructions[1-side][0]
    energy=match.energy(side)
    edge=own['M']-opp['M']
    depth=max(.47,min(.88,.67+edge*.009+.025*tempo-.025*rival_press))
    lane=.5+(.14+.085*width)*(1 if (match.minute//5+side)%2 else -1)
    pressure=max(-.25,min(.55,.07*rival_press+.012*(opp['D']-own['M'])))
    return depth,lane,pressure,energy


def positions(slots,side,ball):
    if not slots:return ()
    if len(slots)==11 and tuple(role for role,_ in slots) in LAYOUTS.values():
        raw=[(x/930,y/340) for x,y in coordinates([role for role,_ in slots])]
    else:
        raw=[(.10+.14*(i//3),.23+.26*(i%3)) for i in range(len(slots))]
    return tuple((pid, max(.04,min(.96,(x if side==0 else 1-x)+.18*(ball[0]-.5))),
                       max(.06,min(.94,y+.2*(ball[1]-.5))))
                 for (_,pid),(x,y) in zip(slots,raw))


def frames(slots,side,minute,depth,lane,events):
    def point(x,y):return (x if side==0 else 1-x,y)
    path=[point(.42,.5),point((.42+depth)/2,lane),point(depth,lane)]
    kinds={e[3] for e in events}
    if 'goal' in kinds:path.append(point(.99,.5))
    elif kinds & {'saved','on_target'}:path.append(point(.91,.5))
    elif 'wide' in kinds:path.append(point(.99,.24 if lane<.5 else .76))
    elif not kinds:path.append(point(max(.46,depth-.14),lane))
    provider=next((e[2] for e in events if e[3]=='pass'),None)
    shooter=next((e[2] for e in events if e[3] in ('goal','saved','on_target','wide')),None)
    expanded=[]
    for i,ball in enumerate(path):
        if i:
            old=path[i-1]
            expanded.append((tuple((a+b)/2 for a,b in zip(old,ball)),None))
        expanded.append((ball,provider if i==1 else shooter if i==2 else None))
    clip=[]
    for ball,carrier in expanded:
        layouts=[positions(slots[i],i,ball) for i in (0,1)]
        if carrier is not None:
            layouts[side]=tuple((pid,*ball) if pid==carrier else (pid,x,y) for pid,x,y in layouts[side])
        clip.append((minute,ball,tuple(layouts)))
    return clip
