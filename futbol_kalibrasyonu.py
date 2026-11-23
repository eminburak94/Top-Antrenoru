"""Model 4: contact trajectories and a two-stage finishing model."""
import math

from futbol_kurallari import EXEMPT, RulesPitch, default_role, offside
from mevkiler import fit_level
from saha_motoru import clamp
from taktik import CENTRE_BACKS, FULLBACKS, role_factor, roles_for
from veritabani import player

ATTACK_RUN={'wingback':.071,'box_to_box':.064,'finisher':.051,'target':.030,'inside_winger':.033}
PASS_OUTLET={'playmaker':.115,'ball_playing':.086,'target':.073,'dropping':.078,
             'winger':.043,'inside_winger':.046}

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


def open_play_target(target, attack, defence):
    """Apply a small finishing-space adjustment from the active lineups."""
    space_quality = clamp((attack - defence) * .028, -.10, .10)
    return clamp(target + space_quality, .12, .82)


class CalibratedPitch(RulesPitch):
    def __init__(self, match, seed):
        super().__init__(match, seed)
        self.corner_phase = None
        self.advanced_regains=[0,0]
        self.last_regain=(-1,-10)
        self.position_fit={}

    def role(self,side,pid,position):
        if self.m.team_orders is None:
            return super().role(side,pid,position)
        allowed=roles_for(position)
        preferred=self.role_prefs[side].get(pid)
        if preferred in allowed and self.slot_fit(pid,position)>=1:
            return preferred
        return default_role(position) or (allowed[0] if allowed else None)

    def slot_fit(self,pid,position):
        key=pid,position
        fit=self.position_fit.get(key)
        if fit is None:
            fit=self.position_fit[key]=fit_level(player(self.m.s,pid),position)
        return fit

    def influence(self,pid,position,role):
        return role_factor(self.m.profiles,pid,role,self.m.player_condition(pid),self.slot_fit(pid,position))

    def transition(self,side):
        owner,minute=self.last_regain
        return self.m.team_orders[side]['counter'] if owner==side and self.m.minute-minute<=3 else 0

    def target_adjust(self,side,pid,position,x,y):
        if self.m.team_orders is None:
            return super().target_adjust(side,pid,position,x,y)
        direction=1 if side==0 else -1
        attacking=self.side==side
        order=self.m.team_orders[side]
        role=self.role(side,pid,position)
        factor=self.influence(pid,position,role) if role else 1
        if position in FULLBACKS or position in CENTRE_BACKS:
            x+=direction*order['line']*.078
        elif position in ('DM','CM','AM'):
            x+=direction*order['line']*.035
        if attacking:
            if position in FULLBACKS:
                x+=direction*order['overlap']*.038*factor
            if role in ATTACK_RUN:
                advance=ATTACK_RUN[role]
                x+=direction*(advance+.022*self.transition(side))*factor
            elif role in ('defensive_back','dropping','holding'):
                x-=direction*(.079 if role=='dropping' else .045)*factor
            elif role in ('playmaker','ball_playing'):
                x+=(self.ball[0]-x)*.17*factor
                y+=(self.ball[1]-y)*.17*factor
            if role=='inside_winger':y+=(.5-y)*.40*factor
            elif role=='winger':y-=(.5-y)*(.24+.16*self.m.instructions[side][2])*factor
            y+=direction*order['flank']*.018
        else:
            if role=='ball_winner':
                x+=(self.ball[0]-x)*.19*factor
                y+=(self.ball[1]-y)*.23*factor
            if role in ('stopper','defensive_back','holding','box_to_box'):
                x-=direction*.026*factor
                if role!='defensive_back':y+=(.5-y)*.14*factor
        return clamp(x,.05,.95),clamp(y,.055,.945)

    def pass_preference(self,side,target,position):
        if self.m.team_orders is None:
            return super().pass_preference(side,target,position)
        role=self.role(side,target,position)
        bias=PASS_OUTLET.get(role,0)
        return bias*self.influence(target,position,role) if bias else 0

    def open_pass_bias(self,side,ty,forward,distance):
        order=self.m.team_orders[side]
        width=self.m.instructions[side][2]
        flank=order['flank']*(1 if side==0 else -1)
        return (order['passing']*(.72*forward+.29*distance)
                +self.transition(side)*.55*forward
                +.33*flank*(ty-.5)+.56*width*(abs(ty-.5)-.12))

    def delivery_adjustment(self,side,target,origin_x,dest,distance):
        m=self.m
        rival=1-side
        direct=m.team_orders[side]['passing']
        impact=-.12*max(0,distance-.16)*max(0,direct)
        forward=(dest[0]-origin_x)*(1 if side==0 else -1)
        space=max(0,m.team_orders[rival]['line']*.65+m.instructions[rival][0]*.35)
        if distance<.22 and (forward<=.16 or not space):
            return impact
        defender=self.nearest(rival,dest,True)
        if defender is None:
            return impact
        profile=m.profiles[target]
        position=next(role for role,pid in m.slots[side] if pid==target)
        if distance>=.22 and self.role(side,target,position)=='target':
            opposing=m.profiles[defender]
            edge=(profile['Heading']+profile['Strength']-opposing['Heading']-opposing['Strength'])/2
            impact+=clamp(edge*.012,-.09,.09)
        if forward>.16 and space:
            pace=profile['Pace']-m.profiles[defender]['Pace']
            impact+=space*clamp(.045+pace*.007,0,.09)
        return impact

    def press_recovery(self):
        m=self.m
        side=1-self.side
        if m.instructions[side][0]<1:
            return False
        depth=self.ball[0] if side==0 else 1-self.ball[0]
        if depth<.48:
            return False
        candidates=[]
        for position,pid in m.slots[side]:
            if position=='GK':continue
            distance=math.dist(self.xy[pid],self.ball)
            if distance<=.135:
                role=self.role(side,pid,position)
                bonus=.024 if role=='ball_winner' else 0
                candidates.append((distance-bonus,pid,distance))
        if not candidates:
            return False
        _,pid,distance=min(candidates)
        skills=m.profiles[pid]
        holder=m.profiles[self.owner]
        duel=(skills['Tackling']+skills['Work rate']-holder['First touch']-holder['Composure'])/2
        chance=clamp(.23-distance*1.1+duel*.013,.035,.29)*m.player_condition(pid)/100
        if m.rng.random()>=chance:
            return False
        self.win(pid)
        return True

    def win(self,thief):
        if self.m.team_orders is not None:
            side=1-self.side
            depth=self.ball[0] if side==0 else 1-self.ball[0]
            if depth>=.58:self.advanced_regains[side]+=1
            self.last_regain=(side,self.m.minute)
        super().win(thief)

    def frame(self, action=None, ball=None):
        if not self.m.capture:
            return
        super().frame()
        minute,point,players,owner,meta=self.m.frames[-1]
        self.m.frames[-1]=(minute,ball if ball is not None else point,players,owner,
                           meta | {'score':tuple(self.m.score),'action':action,'restart':self.restart})

    def align(self):
        # Preserve coordinates of surviving players after a dismissal.
        previous=self.anchor[:]
        super().align()
        for side,slots in enumerate(self.m.slots):
            if len(slots)==11 or self.anchor[side] is previous[side]:
                continue
            for role,pid in slots:
                if pid in previous[side]:
                    self.anchor[side][pid]=previous[side][pid]
                elif role=='GK':
                    point=(.055 if side==0 else .945,.5)
                    self.anchor[side][pid]=self.xy[pid]=point

    def card(self, side, offender, level):
        # A deferred second caution may already have sent this player off.
        if offender in self.anchor[side]:
            super().card(side, offender, level)

    def settle_substitution(self, side, outgoing):
        # Show a deferred caution before a substitution can remove its recipient.
        due = [(team, pid, level) for team, pid, level in self.pending_cards
               if (team, pid) == (side, outgoing)]
        if not due:
            return True
        self.pending_cards = [item for item in self.pending_cards if item[:2] != (side, outgoing)]
        for team, pid, level in due:
            self.card(team, pid, level)
        return any(pid == outgoing for _, pid in self.m.slots[side])

    def boundary(self, origin, destination, last_side, last_player):
        point = touchline_crossing(origin, destination)
        if point is not None:
            self.receive(last_side, None, point)
            self.frame()
            self.event(last_side, last_player, 'throw_awarded')
            self.dead_ball('throw', 1-last_side, point)
            return True

        # Swap axes to test the same segment against the goal lines.
        crossing = touchline_crossing(origin[::-1], destination[::-1])
        if crossing is None:
            return False
        y, x = crossing
        self.receive(last_side, None, (x, y))
        self.frame()
        defending = int(x)
        if last_side == defending:
            corner = (.99 if defending else .01, .02 if y < .5 else .98)
            self.dead_ball('corner', 1-defending, corner)
        else:
            self.dead_ball('goal_kick', defending, (.94 if defending else .06, .5))
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
            fitness = m.energy(1-side)*(.83+.17*m.player_condition(defender)/100)
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
        step*=.87+.13*m.player_condition(owner)/100
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
            if self.set_piece is None:
                target=open_play_target(target,m.strengths[side]['F'],m.strengths[rival]['D'])
            target*=m.energy(side)*(.94+.06*m.player_condition(player)/100)
            if side==0:target=min(.82,target*1.045)
        m.shots[side]+=1
        self.partial_shots[side]+=1
        assist=self.last_pass
        self.last_pass=None
        self.owner=None
        self.ball=((x+goal_x)*.5,(y+aim)*.5)
        self.frame('shot')
        if not penalty and defender and m.rng.random()<.035+.26*pressure:
            outcome='blocked'
            self.frame(outcome,self.xy[defender])
            self.dead_ball('corner',side,(goal_x,.02 if y<.5 else .98))
        elif m.rng.random()>=target:
            outcome='wide'
            self.ball=(goal_x,.23 if aim<.5 else .77)
            self.frame(outcome)
            self.dead_ball('goal_kick',rival,(.94 if side==0 else .06,.5))
        elif keeper and m.rng.random()<save:
            outcome='saved'
            self.ball=(goal_x,aim)
            self.frame(outcome)
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
            m.score[side]+=1
            self.frame(outcome)
            m.events.append([m.minute,(m.a,m.b)[side],player])
            if assist and assist[0]==side and assist[2]==player:
                m.assists.append([m.minute,side,assist[1],player])
            if self.set_piece in ('corner','freekick','penalty') or self.corner_phase==(side,m.minute-1):
                self.event(side,player,'set_piece_goal')
            self.dead_ball('kickoff',rival,(.5,.5))
        self.event(side,player,outcome,keeper if outcome=='saved' else None)
        if m.human is not None:
            m.analysis['chances'].append([m.minute,side,player,outcome,round(x,3),round(y,3)])

    def restart_play(self):
        kind=self.restart
        team=self.side
        super().restart_play()
        if kind=='corner' and self.side==team and self.owner is not None:
            self.corner_phase=(team,self.m.minute)

