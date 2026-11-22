"""Model 3 rules layered over the position simulation."""
import math
from dataclasses import dataclass

from saha_motoru import PitchState,clamp
from mevkiler import group_for

EXEMPT={'throw','corner','goal_kick'}
EVENTS={'offside','foul','advantage','second_yellow','indirect','clearance','header','throw_awarded'}
CORNERS=('near','far','central','short')
DEFENCE=('zone','man','mixed')
FREE=('auto','shoot','cross','short')
ROLES=('playmaker','finisher','target','holding','wingback','winger','stopper','ball_winner')
TAKERS=('left_corner','right_corner','free','penalty')


def offside(side,ball,attacker,opponents,active=True,restart=None):
    if not active or restart in EXEMPT:return False
    def depth(x):return x if side==0 else 1-x
    lines=sorted((depth(x) for x,_ in opponents),reverse=True)
    second=lines[1] if len(lines)>1 else lines[0] if lines else .5
    player=depth(attacker[0])
    return player>max(.5,depth(ball[0]),second)+.000001


def default_role(position):
    return {'CM':'playmaker','AM':'playmaker','DM':'holding','CB':'stopper','RB':'wingback',
            'LB':'wingback','RWB':'wingback','LWB':'wingback','RW':'winger','LW':'winger',
            'RM':'winger','LM':'winger','CF':'target','ST':'finisher','SS':'finisher'}.get(position)


@dataclass(frozen=True)
class Referee:
    identity:int
    tolerance:float
    strictness:float
    advantage:float

    @classmethod
    def assign(cls,seed):
        key=seed%12
        return cls(key+1,.92+.02*(key%7),.9+.04*(key%6),.16+.025*(key%5))


class RulesPitch(PitchState):
    def __init__(self,match,seed):
        super().__init__(match)
        self.referee=Referee.assign(seed)
        self.prefs=[match.s.get('set_pieces',{}).get(team,{}) for team in (match.a,match.b)]
        self.role_prefs=[match.s.get('player_roles',{}).get(team,{}) for team in (match.a,match.b)]
        self.signal=None
        self.set_piece=None
        self.wall=()
        self.pending_cards=[]

    def frame(self):
        if not self.m.capture:return
        super().frame()
        current=self.m.frames[-1]
        self.m.frames[-1]=current+({'signal':self.signal,'set_piece':self.set_piece,
             'wall':self.wall,'referee':(clamp(self.ball[0]-.085,.10,.90),clamp(self.ball[1]+.10,.14,.86))},)

    def role(self,side,pid,position):
        return self.role_prefs[side].get(pid,default_role(position))

    def target_adjust(self,side,pid,position,x,y):
        role=self.role(side,pid,position)
        direction=1 if side==0 else -1
        attacking=self.side==side
        if role in ('finisher','target') and attacking:
            x+=direction*(.045 if role=='finisher' else .026)
            y+=(.5-y)*.19
        elif role=='wingback' and attacking:
            x+=direction*(.040+.012*self.m.instructions[side][1])
        elif role in ('holding','stopper'):
            x-=direction*(.035 if role=='holding' else .025)
            y+=(.5-y)*.14
        elif role=='winger':
            y+=(.5-y)*-.17
        elif role in ('ball_winner','playmaker'):
            if (role=='ball_winner')!=attacking:
                x+=(self.ball[0]-x)*.10
                y+=(self.ball[1]-y)*.14
        return clamp(x,.05,.95),clamp(y,.055,.945)

    def pass_preference(self,side,target,position):
        return {'playmaker':.045,'target':.029,'holding':.013}.get(self.role(side,target,position),0)

    def take(self,side,kind):
        positions=self.m.slots[side]
        ids=[pid for _,pid in positions]
        if not ids:return None
        key=('left_corner' if (self.ball[1]<.5)==(side==0) else 'right_corner') if kind=='corner' else 'free' if kind in ('freekick','indirect') else kind
        chosen=self.prefs[side].get(key)
        if chosen in ids:return chosen
        if kind=='goal_kick':
            return next((pid for pos,pid in positions if pos=='GK'),None) or self.nearest(side,self.ball)
        if kind in ('corner','freekick','penalty','indirect'):
            skill='Finishing' if kind=='penalty' else 'Set pieces'
            valid=[pid for pos,pid in positions if pos!='GK'] or ids
            return max(valid,key=lambda pid:(self.m.profiles[pid][skill],pid))
        return self.nearest(side,self.ball,True) or self.nearest(side,self.ball)

    def event(self,side,pid,kind,other=None):
        self.m.play.append([self.m.minute,side,pid,kind,other])

    def card(self,side,offender,level):
        m=self.m
        if not level:return
        if level==1:
            self.event(side,offender,'yellow')
            if offender not in m.yellows:
                m.yellows.add(offender)
                self.signal='yellow'
                return
            self.event(side,offender,'second_yellow')
        self.event(side,offender,'red')
        self.signal='red'
        m.slots[side]=[(r,pid) for r,pid in m.slots[side] if pid!=offender]
        m.strengths[side]=m.strength(m.slots[side])
        self.align()

    def foul(self,defender,severity,allow_advantage=True):
        side=self.side
        owner=self.owner
        self.event(1-side,defender,'foul',owner)
        self.signal='foul'
        flying=self.m.card_rng
        level=2 if severity>.88 and flying.random()<.38*self.referee.strictness else (
            1 if flying.random()<clamp((severity-.26)*self.referee.strictness,.04,.72) else 0)
        x,y=self.ball
        depth=x if side==0 else 1-x
        in_box=depth>.84 and abs(y-.5)<.20
        if allow_advantage and not in_box and level!=2 and .51<depth<.84 and flying.random()<self.referee.advantage:
            self.event(side,owner,'advantage',defender)
            self.signal='advantage'
            if level:self.pending_cards.append((1-side,defender,level))
            return
        self.flush_cards()
        self.card(1-side,defender,level)
        point=(.895 if side==0 else .105,.5) if in_box else self.ball
        self.dead_ball('penalty' if in_box else 'freekick',side,point)

    def flush_cards(self):
        for side,pid,level in self.pending_cards:
            if pid in self.anchor[side]:self.card(side,pid,level)
        self.pending_cards.clear()

    def prepare_layout(self,kind,side,taker):
        reverse=1-side
        direction=1 if side==0 else -1
        end=.99 if side==0 else .01
        keeper=next((pid for role,pid in self.m.slots[reverse] if role=='GK'),None)
        if kind=='penalty':
            for team,slots in enumerate(self.m.slots):
                for i,(role,pid) in enumerate(slots):
                    if role!='GK' and pid not in (taker,keeper):
                        self.xy[pid]=(end-direction*(.22+.04*team),.12+(i%11)*.074)
            if keeper:self.xy[keeper]=(end,.5)
        if kind=='corner':
            target_depth={'near':.06,'far':.09,'central':.13,'short':.18}
            option=self.prefs[side].get('corner','central')
            target=end-direction*target_depth[option]
            aim=.38 if option=='near' else .62 if option=='far' else .5
            if self.ball[1]>.5:aim=1-aim
            mode=self.prefs[reverse].get('defence','mixed')
            attackers=[pid for role,pid in self.m.slots[side] if role!='GK' and pid!=taker]
            attackers.sort(key=lambda pid:-self.m.profiles[pid]['Heading'])
            runners=attackers[:4]
            nominated=self.prefs[side].get('target')
            if nominated in attackers:runners=[nominated,*[pid for pid in attackers if pid!=nominated][:3]]
            for i,pid in enumerate(runners):self.xy[pid]=(target-direction*i*.023,aim+(i-1.5)*.068)
            defenders=[pid for role,pid in self.m.slots[reverse] if role!='GK'][:5]
            for i,pid in enumerate(defenders):
                if mode!='zone' and i<len(runners) and (mode=='man' or i<3):
                    x,y=self.xy[runners[i]]
                    self.xy[pid]=(x+direction*.018,y+.018)
                else:self.xy[pid]=(end-direction*(.058+.035*(i%2)),.32+i*.08)
            if keeper:self.xy[keeper]=(end-direction*.022,.50)
            if option=='short' and runners:self.xy[runners[0]]=(clamp(self.ball[0]-direction*.11,.02,.98),.11 if self.ball[1]<.5 else .89)
            return runners[0] if runners else None
        if kind=='freekick' and abs(end-self.ball[0])<.30 and abs(self.ball[1]-.5)<.36:
            players=[pid for role,pid in self.m.slots[reverse] if role!='GK'][:4]
            x,y=self.ball
            for i,pid in enumerate(players):self.xy[pid]=(clamp(x+direction*.088,.04,.96),clamp(y+(i-1.5)*.028,.07,.93))
            self.wall=tuple(players)
        return None

    def delivery(self,target=None,restart=None):
        if not target:
            candidates=[pid for r,pid in self.m.slots[self.side] if pid!=self.owner and r!='GK']
            if candidates:
                prefer=self.prefs[self.side].get('free_approach')
                if restart=='goal_kick':
                    prefer='cross' if self.m.instructions[1-self.side][0]>0 else 'short'
                target=(max if prefer=='cross' else min)(candidates,key=lambda pid:math.dist(self.xy[pid],self.ball))
        if target:self.pass_ball(0,target=target,restart=restart)

    def restart_play(self):
        kind=self.restart
        self.restart=None
        side=self.side
        self.flush_cards()
        taker=self.take(side,kind)
        if taker is None:
            self.receive(1-side,self.nearest(1-side,self.ball))
            return
        self.set_piece=kind
        self.xy[taker]=self.ball
        self.receive(side,taker)
        target=self.prepare_layout(kind,side,taker)
        self.event(side,taker,kind)
        self.frame()
        if kind=='penalty':
            self.shoot(True)
        elif kind=='corner':
            self.delivery(target,kind)
            if self.owner==target and self.side==side and target and self.prefs[side].get('corner','central')!='short':
                if self.m.rng.random()<.37:
                    self.event(side,target,'header')
                    self.shoot()
            elif self.owner is not None and self.side!=side:
                self.event(self.side,self.owner,'clearance',taker)
        elif kind=='freekick':
            depth=self.ball[0] if side==0 else 1-self.ball[0]
            choice=self.prefs[side].get('free_approach','auto')
            if (choice=='shoot' or choice=='auto' and self.m.profiles[taker]['Set pieces']>=8) and depth>.70 and abs(self.ball[1]-.5)<.27:
                self.shoot()
            else:self.delivery(restart=kind)
        else:
            self.delivery(restart=kind)

    def line(self,side):
        depths=sorted((self.xy[pid][0] if side==0 else 1-self.xy[pid][0]
                      for _,pid in self.m.slots[1-side]),reverse=True)
        return max(.5,self.ball[0] if side==0 else 1-self.ball[0],depths[min(1,len(depths)-1)] if depths else .5)

    def before_delivery(self,target,restart):
        opposite=[self.xy[pid] for _,pid in self.m.slots[1-self.side]]
        if not offside(self.side,self.ball,self.xy[target],opposite,restart=restart):return False
        side=self.side
        self.event(side,target,'offside',self.owner)
        self.signal='offside'
        self.dead_ball('indirect',1-side,self.xy[target])
        self.frame()
        return True

    def pass_miss(self,dest,origin):
        px,py=dest
        ox,oy=origin
        rng=self.m.rng
        # A failed lateral delivery keeps its component toward the touchline.
        exit_y=py+(py-oy)*.65+rng.uniform(-.22,.22)
        if exit_y<0 or exit_y>1:
            side=self.side
            self.event(side,self.last_kicker,'throw_awarded')
            self.dead_ball('throw',1-side,(px,0 if exit_y<0 else 1))
            return
        self.ball=(px,exit_y)
        thief=self.nearest(1-self.side,self.ball)
        if thief is not None:self.win(thief)
        else:self.dead_ball('throw',1-self.side,(px,0 if exit_y<.5 else 1))

    def carry(self,pressure):
        m=self.m
        defender=self.nearest(1-self.side,self.ball,True)
        if defender and pressure>.17:
            skills=m.profiles[defender]
            severity=clamp(.10+pressure*.39+(20-skills['Tackling'])*.012
                           +(1-m.energy(1-self.side))*.46+m.card_rng.random()*.30,0,1)
            risk=(.13+pressure*.31)*severity/self.referee.tolerance
            if m.card_rng.random()<risk:
                self.foul(defender,severity)
                return
        super().carry(pressure)

    def tick(self):
        self.signal=None
        self.set_piece=None
        self.wall=()
        if self.m.minute==46:
            self.flush_cards()
            self.dead_ball('kickoff',1,(.5,.5))
        super().tick()
        if self.m.minute==90:self.flush_cards()
