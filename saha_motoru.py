"""Authoritative positional match state for model 2.

Each decision tick covers one simulated minute. Flights begin and resolve
inside that tick; capture records their endpoints without consuming RNG.
"""
import math
from collections import deque

from konumsal import positions

SHOT_NAMES=('goal','wide','saved','on_target','blocked')
RESTARTS=('kickoff','throw','corner','freekick','penalty','goal_kick')


def clamp(value,lo,hi):
    return lo if value<lo else hi if value>hi else value


class PitchState:
    def __init__(self,match):
        self.m=match
        self.anchor=[{pid:(x,y) for pid,x,y in positions(slots,side,(.5,.5))}
                     for side,slots in enumerate(match.slots)]
        self.xy={**self.anchor[0],**self.anchor[1]}
        self.ball=(.5,.5)
        self.owner=None
        self.side=0
        self.restart='kickoff'
        self.last_pass=None
        self.trace=deque(maxlen=180)
        self.counters={key:[0,0] for key in ('possession','passes','completed','turnovers','recoveries')}
        self.partial_shots=[0,0]
        self.partial_recovery=[0,0]

    def frame(self):
        m=self.m
        if m.capture:
            m.frames.append((m.minute,self.ball,tuple(tuple((pid,*self.xy[pid])
                              for _,pid in slots if pid in self.xy) for slots in m.slots),self.owner))

    def align(self):
        m=self.m
        for side,slots in enumerate(m.slots):
            anchors=self.anchor[side]
            if len(anchors)!=len(slots) or any(pid not in anchors for _,pid in slots):
                updated={pid:(x,y) for pid,x,y in positions(slots,side,(.5,.5))}
                for pid,point in updated.items():self.xy.setdefault(pid,point)
                self.anchor[side]=updated

    def nearest(self,side,ball,outfield=False):
        return min((pid for role,pid in self.m.slots[side] if not outfield or role!='GK'),
                   key=lambda pid:abs(self.xy[pid][0]-ball[0])+abs(self.xy[pid][1]-ball[1]),default=None)

    def shape(self):
        m=self.m
        bx,by=self.ball
        for side,slots in enumerate(m.slots):
            direction=1 if side==0 else -1
            press,tempo,width=m.instructions[side]
            approach=m.style if side==m.human else m.styles[side]
            attack=.045 if approach=='Attack' else -.04 if approach=='Defend' else 0
            chasing=self.nearest(side,self.ball,True) if side!=self.side else None
            energy=m.energy(side)
            for role,pid in slots:
                ax,ay=self.anchor[side][pid]
                px,py=self.xy[pid]
                if pid==self.owner:
                    continue
                pace=m.profiles[pid]['Pace']
                if role=='GK':
                    x=.055 if side==0 else .945
                    y=clamp(.5+(by-.5)*.32,.36,.64)
                else:
                    x=clamp(ax+(bx-.5)*.37+direction*(attack+.024*press+.018*tempo),.06,.94)
                    y=clamp(.5+(ay-.5)*(1+width*.18)+(by-.5)*.15,.07,.93)
                    if pid==chasing:
                        pursuit=.34+press*.11
                        x+=(bx-x)*pursuit
                        y+=(by-y)*pursuit
                if self.m.rules and role!='GK':x,y=self.target_adjust(side,pid,role,x,y)
                step=(.10+.004*pace)*energy
                if m.tactical_ai and role!='GK':
                    step*=.85+.15*m.player_condition(pid)/100
                self.xy[pid]=(px+clamp(x-px,-step,step),py+clamp(y-py,-step,step))

    def receive(self,side,pid,point=None):
        self.side,self.owner=side,pid
        if pid is not None:self.ball=self.xy[pid]
        elif point is not None:self.ball=point

    def dead_ball(self,kind,side,point):
        self.restart=kind
        self.receive(side,None,point)
        self.last_pass=None

    def restart_play(self):
        kind=self.restart
        self.restart=None
        side=self.side
        taker=self.nearest(side,self.ball,kind!='goal_kick') or self.nearest(side,self.ball)
        if taker is None:
            rival=self.nearest(1-side,self.ball)
            self.receive(1-side,rival,self.ball)
            return
        self.xy[taker]=self.ball
        self.receive(side,taker)
        self.m.play.append([self.m.minute,side,taker,kind,None])
        self.frame()
        if kind=='penalty':
            self.shoot(True)

    def pass_ball(self,pressure,target=None,restart=None):
        m=self.m
        side,pid=self.side,self.owner
        x,y=self.ball
        direction=1 if side==0 else -1
        press,tempo,width=m.instructions[side]
        candidates=[]
        forced=target
        legal_line=self.line(side) if m.rules and forced is None else 1
        for role,target in m.slots[side]:
            if target==pid or role=='GK' or forced is not None and target!=forced:continue
            tx,ty=self.xy[target]
            distance=abs(tx-x)+.6*abs(ty-y)
            if distance<.08 and forced is None:continue
            forward=(tx-x)*direction
            quality=forward*(.8+.18*tempo)-.83*distance+abs(ty-y)*width*.08
            quality+=m.profiles[target]['Anticipation']*.008
            if m.rules:
                quality+=self.pass_preference(side,target,role)+max(0,forward)*.21
                if (tx if side==0 else 1-tx)>legal_line+.000001:quality-=.21
            if m.team_orders is not None and forced is None and restart is None:
                quality+=self.open_pass_bias(side,ty,forward,distance)
            candidates.append((quality,target,distance))
        if not candidates:
            self.carry(pressure)
            return
        _,target,distance=max(candidates)
        self.counters['passes'][side]+=1
        dest=self.xy[target]
        if m.rules:self.last_kicker=pid
        passing=m.profiles[pid]['Passing']
        difficulty=(self.delivery_adjustment(side,target,x,dest,distance)
                    if m.team_orders is not None and forced is None and restart is None else 0)
        threshold=clamp(.91+.016*(passing-10)-.32*distance-.20*pressure+difficulty, .25,.96)
        self.owner=None
        self.ball=((x+dest[0])*.5,(y+dest[1])*.5)
        self.frame()
        success=m.rng.random()<threshold
        if m.capture:
            self.trace.append(dict(minute=m.minute,player=pid,target=target,
                origin=(x,y),destination=dest,success=success,pressure=pressure,
                probability=threshold,passing=passing,tempo=tempo,width=width))
        if success:
            if m.rules:
                self.ball=(x,y)
                self.owner=pid
                if self.before_delivery(target,restart):return
            self.receive(side,target)
            self.counters['completed'][side]+=1
            self.last_pass=(side,pid,target)
            m.play.append([m.minute,side,pid,'pass',target])
        else:
            m.play.append([m.minute,side,pid,'pass_failed',target])
            if m.rules:
                self.pass_miss(dest,(x,y))
                return
            self.ball=dest
            thief=self.nearest(1-side,dest)
            if thief is not None and abs(self.xy[thief][0]-dest[0])+abs(self.xy[thief][1]-dest[1])<.28:
                self.win(thief)
            else:
                self.dead_ball('throw',1-side,(dest[0],.02 if dest[1]<.5 else .98))

    def win(self,thief):
        side=1-self.side
        previous=self.owner
        self.counters['turnovers'][self.side]+=1
        self.counters['recoveries'][side]+=1
        self.partial_recovery[side]+=1
        self.receive(side,thief)
        self.last_pass=None
        self.m.play.append([self.m.minute,side,thief,'tackle',previous])

    def carry(self,pressure):
        m=self.m
        side,pid=self.side,self.owner
        rival=1-side
        defender=self.nearest(rival,self.ball,True)
        if defender and m.rng.random()<.06+.35*pressure:
            if m.rng.random()<.13 and not m.rules:
                x,y=self.ball
                kind='penalty' if (x if side==0 else 1-x)>.90 and abs(y-.5)<.22 else 'freekick'
                point=(.895 if side==0 else .105,.5) if kind=='penalty' else self.ball
                self.dead_ball(kind,side,point)
            else:
                self.win(defender)
            return
        x,y=self.ball
        profile=m.profiles[pid]
        velocity=(.058+profile['Dribbling']*.003+profile['Pace']*.0015)*m.energy(side)
        direction=1 if side==0 else -1
        is_keeper=any(role=='GK' and uid==pid for role,uid in m.slots[side])
        lo,hi=((.055,.18) if side==0 else (.82,.945)) if is_keeper else (.055,.945)
        self.xy[pid]=(clamp(x+velocity*direction,lo,hi),y+(.5-y)*.18)
        self.ball=self.xy[pid]

    def shoot(self,penalty=False):
        m=self.m
        side,pid=self.side,self.owner
        rival=1-side
        x,y=self.ball
        goal=(.99 if side==0 else .01,.5)
        distance=math.hypot(x-goal[0],(y-.5)*.65)
        defender=self.nearest(rival,self.ball,True)
        keeper=next((pid for role,pid in m.slots[rival] if role=='GK'),None)
        cover=m.strengths[rival]['D']
        reflex=m.profiles[keeper]['Reflexes'] if keeper else 3
        gap=abs(self.xy[keeper][1]-.5) if keeper else .45
        chance=clamp(.287-distance*.60+(.009*(m.profiles[pid]['Finishing']-10))
                    -.009*(reflex-10)-.005*(cover-10)+gap*.15,.027,.38)*m.energy(side)
        if side==0:chance*=1.055
        m.shots[side]+=1
        self.partial_shots[side]+=1
        block=not penalty and defender is not None and math.dist(self.xy[defender],self.ball)<.14
        draw=m.rng.random()
        accuracy=.34
        penalty_goal=.72
        if m.rules:
            chance=clamp(chance+.078+.010*(m.strengths[side]['F']-cover),.022,.43)
            if self.set_piece=='corner':
                chance=clamp(chance+(m.profiles[pid]['Heading']-10)*.008,.025,.40)
            if self.wall:chance*=.72
            accuracy=clamp(.35+(.011*(m.profiles[pid]['Finishing']-10))-.12*distance,.19,.51)
            if penalty:
                aim=.27+m.rng.random()*.46
                if keeper:self.xy[keeper]=(self.xy[keeper][0],clamp(aim+m.rng.uniform(-.14,.14),.23,.77))
                penalty_goal=clamp(.72+.012*(m.profiles[pid]['Finishing']-10)-.012*(reflex-10),.50,.88)
                goal=(goal[0],aim)
        assist=self.last_pass
        self.last_pass=None
        self.owner=None
        self.ball=((x+goal[0])*.5,(y+.5)*.5)
        self.frame()
        if draw<(penalty_goal if penalty else chance):
            self.ball=goal
            self.frame()
            m.score[side]+=1
            m.events.append([m.minute,(m.a,m.b)[side],pid])
            if assist and assist[0]==side and assist[2]==pid:m.assists.append([m.minute,side,assist[1],pid])
            outcome='goal'
            if m.rules and self.set_piece in ('corner','freekick','penalty'):
                m.play.append([m.minute,side,pid,'set_piece_goal',None])
            self.dead_ball('kickoff',rival,(.5,.5))
        elif not penalty and block and draw<chance+.18:
            outcome='blocked'
            self.dead_ball('corner',side,(goal[0],.02 if y<.5 else .98))
        elif keeper and draw<(.90 if penalty else chance+accuracy):
            outcome='saved'
            if m.rules and penalty and m.rng.random()<.23:
                point=(.82 if side==0 else .18,.48)
                receiver=self.nearest(rival,point,True)
                if receiver:self.receive(rival,receiver)
                else:self.receive(rival,keeper)
            else:self.receive(rival,keeper)
        else:
            outcome='wide'
            self.ball=(goal[0],.25 if y<.5 else .75)
            self.frame()
            self.dead_ball('goal_kick',rival,(.94 if side==0 else .06,.5))
        m.play.append([m.minute,side,pid,outcome,keeper if outcome=='saved' else None])

    def tick(self):
        m=self.m
        self.align()
        self.shape()
        if self.owner not in self.anchor[self.side] and self.restart is None:
            self.receive(self.side,self.nearest(self.side,self.ball))
        self.frame()
        if self.restart:
            self.restart_play()
        elif m.team_orders is not None and self.owner is not None and self.press_recovery():
            self.frame()
            return
        elif self.owner is not None:
            side=self.side
            self.counters['possession'][side]+=1
            x,y=self.ball
            depth=x if side==0 else 1-x
            nearest=self.nearest(1-side,self.ball,True)
            distance=math.dist(self.xy[nearest],self.ball) if nearest else .8
            pressure=max(0,1-distance/.24)
            tempo=m.instructions[side][1]
            odds=.22+.053*tempo+.035*(m.strengths[side]['F']-m.strengths[1-side]['D'])
            threshold=.58 if m.rules else .64
            if depth>threshold and m.rng.random()<clamp(odds+.92*(depth-threshold)+(.075 if m.rules else 0),.11,.76):
                self.shoot()
            elif m.rng.random()<clamp(.64+.08*tempo+pressure*.12,.40,.87):
                self.pass_ball(pressure)
            else:
                self.carry(pressure)
        self.frame()

    def summary(self):
        return {key:value[:] for key,value in self.counters.items()}
