"""Model 4: contact trajectories and a two-stage finishing model."""
import math

from futbol_kurallari import EXEMPT, RulesPitch, offside
from saha_motoru import clamp


def touchline_crossing(origin, destination):
    x, y = destination
    if 0 <= y <= 1 or y == origin[1]:
        return None
    edge = 0 if y < 0 else 1
    fraction = (edge - origin[1]) / (y - origin[1])
    crossing = origin[0] + (x - origin[0]) * fraction
    return (crossing, edge) if 0 <= crossing <= 1 else None


def shot_probabilities(distance, angle, pressure, visibility, alignment, shooter, keeper):
    """Conditional probabilities of an on-target attempt and a save."""
    finish = (.65 * shooter['Finishing'] + .35 * shooter['Composure'] - 10) / 10
    target = clamp(.66 + .20 * finish - .31 * distance - .16 * angle - .11 * pressure, .17, .77)
    if keeper is None:
        return target, 0
    skill = (.32 * keeper['Reflexes'] + .30 * keeper['Positioning']
             + .23 * keeper['Handling'] + .15 * keeper['One on ones'] - 10) / 10
    save = clamp(.39 + .25 * distance + .10 * angle + .19 * skill
                 + .13 * alignment - .16 * (1 - visibility) - .24 * finish, .13, .89)
    return target, save


class CalibratedPitch(RulesPitch):
    def __init__(self, match, seed):
        super().__init__(match, seed)
        self.corner_phase = None

    def boundary(self, origin, destination, last_side, last_player):
        point = touchline_crossing(origin, destination)
        if point is None:
            return False
        self.ball = point
        self.owner = None
        self.frame()
        self.event(last_side, last_player, 'throw_awarded')
        self.dead_ball('throw', 1-last_side, point)
        return True

    def pass_miss(self, dest, origin):
        side, player = self.side, self.last_kicker
        x, y = dest
        lateral = y - origin[1]
        reach = .10 + .67 * abs(lateral)
        projected = (x + (x-origin[0])*.22, y + lateral*1.05 + self.m.rng.uniform(-reach, reach))
        if self.boundary(origin, projected, side, player):
            return
        self.ball = dest
        defender = self.nearest(1-side, dest)
        if defender is not None:
            self.win(defender)

    def carry(self, pressure):
        m = self.m
        side, owner = self.side, self.owner
        defender = self.nearest(1-side, self.ball, True)
        if defender is not None and pressure > .04:
            attack, defence = m.profiles[owner], m.profiles[defender]
            fitness = m.energy(1-side)
            willingness = clamp(.20 + pressure*.55 + m.instructions[1-side][0]*.07
                                + (defence['Work rate']-10)*.009, .05, .86)
            if m.rng.random() < willingness:
                severity = clamp(.12+pressure*.27+(1-fitness)*.46
                                 +(20-defence['Tackling'])*.011
                                 +(20-defence['Positioning'])*.008
                                 +m.card_rng.random()*.36, 0, 1)
                if m.card_rng.random() < severity*.70/self.referee.tolerance:
                    self.foul(defender, severity)
                    return
                clean = clamp(.44 + (defence['Tackling']-attack['Dribbling'])*.025
                              + pressure*.25 + (fitness-1)*.25, .12, .80)
                if m.rng.random() < clean:
                    x,y = self.ball
                    dx,dy = self.xy[defender]
                    if self.boundary(self.ball,(x+(x-dx)*1.35,y+(y-dy)*2.15),1-side,defender):
                        return
                    self.win(defender)
                    return
        # Advance the carrier without rolling a second, independent challenge.
        x,y = self.ball
        skills=m.profiles[owner]
        direction=1 if side==0 else -1
        step=(.058+skills['Dribbling']*.003+skills['Pace']*.0015)*m.energy(side)
        is_keeper=any(pos=='GK' and pid==owner for pos,pid in m.slots[side])
        lo,hi=((.055,.18) if side==0 else (.82,.945)) if is_keeper else (.055,.945)
        self.xy[owner]=self.ball=(clamp(x+direction*step,lo,hi),y+(.5-y)*.12)

    def before_delivery(self, target, restart):
        if restart in EXEMPT:
            return False
        if super().before_delivery(target,restart):
            return True
        # An attacker beyond the line affects play if challenging the opponent
        # in the immediate receiving lane. The pass-time location is retained.
        side = self.side
        rivals = [self.xy[pid] for _,pid in self.m.slots[1-side]]
        receiver = self.xy[target]
        for _, candidate in self.m.slots[side]:
            if candidate in (self.owner,target):
                continue
            point = self.xy[candidate]
            if (math.dist(point,receiver)<.052 and any(math.dist(point,r)<.033 for r in rivals)
                    and offside(side,self.ball,point,rivals)):
                return super().before_delivery(candidate,restart)
        return False

    def shoot(self,penalty=False):
        m=self.m
        side, player = self.side,self.owner
        rival=1-side
        x,y=self.ball
        goal_x=.99 if side==0 else .01
        keeper=next((pid for role,pid in m.slots[rival] if role=='GK'),None)
        defender=self.nearest(rival,self.ball,True)
        pressure=clamp(1-math.dist(self.xy[defender],self.ball)/.21,0,1) if defender else 0
        distance=math.hypot(x-goal_x,(y-.5)*.65)
        angle=min(1,abs(y-.5)*2)
        aim=.5+m.rng.uniform(-.105,.105)
        visible=.60 if self.wall else 1.0
        opponents=[self.xy[uid] for _,uid in m.slots[rival]]
        advanced=set()
        if not penalty:
            for _,uid in m.slots[side]:
                if uid==player or not offside(side,(x,y),self.xy[uid],opponents):
                    continue
                advanced.add(uid)
                px,py=self.xy[uid]
                fraction=(px-x)/(goal_x-x) if abs(goal_x-x)>.001 else 0
                sight=(keeper and abs(px-self.xy[keeper][0])<.085 and 0<fraction<1
                       and abs(py-(y+(aim-y)*fraction))<.027)
                if sight:
                    self.event(side,uid,'offside',player)
                    self.signal='offside'
                    self.dead_ball('indirect',rival,(px,py))
                    self.frame()
                    return
        alignment=clamp(1-abs(self.xy[keeper][1]-aim)*5,0,1) if keeper else 0
        skills=m.profiles[player]
        if self.set_piece=='corner':
            skills=dict(skills,Finishing=skills['Heading'])
        keep=m.profiles[keeper] if keeper else None
        if penalty and keeper:
            self.xy[keeper]=(goal_x,clamp(.5+m.rng.uniform(-.14,.14),.28,.72))
            alignment=clamp(1-abs(self.xy[keeper][1]-aim)*5,0,1)
        target, save=shot_probabilities(distance,angle,pressure,visible,alignment,skills,keep)
        if penalty:
            target=clamp(.93+(skills['Composure']-10)*.006,.84,.99)
            save=clamp(.16+save*.16+alignment*.05,.13,.36) if keeper else 0
        else:
            target*=m.energy(side)
            if side==0:target=min(.82,target*1.045)
        m.shots[side]+=1
        self.partial_shots[side]+=1
        assist=self.last_pass
        self.last_pass=None
        self.owner=None
        self.ball=((x+goal_x)*.5,(y+aim)*.5)
        self.frame()
        if not penalty and defender and m.rng.random()<.035+.26*pressure:
            outcome='blocked'
            self.dead_ball('corner',side,(goal_x,.02 if y<.5 else .98))
        elif m.rng.random()>=target:
            outcome='wide'
            self.ball=(goal_x,.23 if aim<.5 else .77)
            self.frame()
            self.dead_ball('goal_kick',rival,(.94 if side==0 else .06,.5))
        elif keeper and m.rng.random()<save:
            outcome='saved'
            self.ball=(goal_x,aim)
            self.frame()
            if m.rng.random()<clamp(.24-(keep['Handling']-10)*.017,.06,.43):
                point=(.87 if side==0 else .13,aim)
                attacker=self.nearest(side,point,True)
                stopper=self.nearest(rival,point,True)
                self.event(rival,keeper,'rebound')
                if attacker and (not stopper or math.dist(self.xy[attacker],point)<math.dist(self.xy[stopper],point)):
                    if attacker in advanced:
                        self.event(side,attacker,'offside',player)
                        self.signal='offside'
                        self.dead_ball('indirect',rival,self.xy[attacker])
                        self.frame()
                    else:
                        self.receive(side,attacker)
                else:
                    self.receive(rival,stopper or keeper)
            else:
                self.receive(rival,keeper)
        else:
            outcome='goal'
            self.ball=(goal_x,aim)
            self.frame()
            m.score[side]+=1
            m.events.append([m.minute,(m.a,m.b)[side],player])
            if assist and assist[0]==side and assist[2]==player:
                m.assists.append([m.minute,side,assist[1],player])
            if self.set_piece in ('corner','freekick','penalty') or self.corner_phase==(side,m.minute-1):
                self.event(side,player,'set_piece_goal')
            self.dead_ball('kickoff',rival,(.5,.5))
        self.event(side,player,outcome,keeper if outcome=='saved' else None)

    def restart_play(self):
        kind=self.restart
        team=self.side
        super().restart_play()
        if kind=='corner' and self.side==team and self.owner is not None:
            self.corner_phase=(team,self.m.minute)

