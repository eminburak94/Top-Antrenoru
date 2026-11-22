import konumsal
from saha_motoru import PitchState
from futbol_kurallari import RulesPitch
from futbol_kalibrasyonu import CalibratedPitch
"""Match simulation independent of the desktop UI and career mutations."""
from dataclasses import dataclass
import math
import random

from istatistik import SHOT_EVENTS
from oyuncu import GROUPS, attributes, clamp, power, state
from veritabani import P, roster, player, all_players
from yarisma import formation_for, style_for
from kadro_atama import assign
from mevkiler import LAYOUTS, SKILLS_BY_POSITION, fit_factor, fit_level, group_for
from yerellestirme import is_domestic

ROLES = ('GK', 'D', 'M', 'F')
STYLE = {'Attack': (1.18, .90), 'Balanced': (1., 1.), 'Defend': (.84, 1.10)}
SKILLS = {
    'GK': ('Handling', 'Reflexes', 'One on ones', 'Aerial reach'),
    'D': ('Tackling', 'Marking', 'Positioning', 'Heading'),
    'M': ('Passing', 'Decisions', 'Vision', 'Teamwork'),
    'F': ('Finishing', 'Composure', 'Anticipation', 'First touch'),
}

def fits(p, role):
    return p['pos'] in GROUPS[role] or any(pos in GROUPS[role] for pos in p.get('alternate_positions', ()))

def eligible(s, p):
    z = state(s, p)
    return not (z['injury'] or z['ban'])

def formation_roles(formation):
    if formation.count('-')==3:
        return [group_for(role) for role in LAYOUTS[formation]]
    return [role for role,count in zip(ROLES,[1]+list(map(int,formation.split('-'))))
            for _ in range(count)]


def match_positions(s, team):
    formation=formation_for(s,team)
    return list(LAYOUTS[formation]) if s.get('position_model') else formation_roles(formation)


def suitable(s, p, role):
    return fit_level(p,role)>=2 if s.get('position_model') else fits(p,role)


def manual_slots(s, team, ids):
    roles = match_positions(s,team)
    if len(ids)!=len(roles) or len(set(ids))!=len(roles):
        return []
    squad={p['id']:p for p in roster(team,s['year'],s)}
    def allowed(pid,role):
        if pid not in squad or not eligible(s,squad[pid]):
            return False
        p=squad[pid]
        if s.get('position_model'):
            return (role=='GK')==(p['pos']=='GK')
        return fits(p,role)
    if not all(allowed(pid,role) for role,pid in zip(roles,ids)):
        return []
    if sum(not is_domestic(squad[pid]) for pid in ids)>s['cap']:
        return []
    return list(zip(roles,ids))


def select_slots(s, team, use_manual=True):
    if use_manual and team==s['club'] and s['employed']:
        slots=manual_slots(s,team,s.get('manual_xi',[]))
        if slots:
            return slots
    available = [p for p in roster(team, s['year'], s) if eligible(s, p)]
    scores = {p['id']: power(s, p) for p in available}
    preferred = set(s['selected']) if team == s['club'] and s['employed'] else set()
    foreign = 0
    slots = []
    if s.get('position_model'):
        roles=match_positions(s,team)
        levels={p['id']:{role:fit_level(p,role) for role in set(roles)} for p in available}
        if s.get('lineup_model'):
            squad={p['id']:p for p in available}
            def weight(pid,role):
                if (role=='GK')!=(squad[pid]['pos']=='GK'):
                    return None
                quality=round(100*(levels[pid][role]*5+scores[pid]+3*(pid in preferred)))
                # Reserve a legal goalkeeper when the foreign cap forces an incomplete XI.
                return quality + (100000 if role=='GK' else 0)
            return assign(roles,[(pid,is_domestic(p)) for pid,p in squad.items()],s['cap'],weight)
        for i,role in enumerate(roles):
            pool = [p for p in available if (role=='GK' or p['pos']!='GK')
                    and (is_domestic(p) or foreign<s['cap'])]
            if not pool:
                continue
            later=roles[i+1:]
            p=max(pool,key=lambda p:(levels[p['id']][role]*5+scores[p['id']]
                                      +3*(p['id'] in preferred)
                                      -2*max((levels[p['id']][r] for r in later if r!=role),default=0),
                                      p['id']))
            available.remove(p)
            slots.append((role,p['id']))
            foreign+=not is_domestic(p)
        return slots
    counts = [1] + list(map(int, formation_for(s, team).split('-')))
    for role, count in zip(ROLES, counts):
        for _ in range(count):
            pool = [p for p in available if (role == 'GK' or p['pos'] != 'GK')
                    and (is_domestic(p) or foreign < s['cap'])]
            if not pool:
                break
            player = max(pool, key=lambda p: (
                scores[p['id']] + 3 * (p['id'] in preferred) + 23 * fits(p, role),
                (p['id'].isdecimal(), -int(p['id'].rsplit('-',1)[-1])),
            ))
            available.remove(player)
            slots.append((role, player['id']))
            foreign += not is_domestic(player)
    return slots

def lineup(s, team):
    return [player(s,pid) for _, pid in select_slots(s, team)]

@dataclass
class MatchResult:
    home: str
    away: str
    x: int
    y: int
    events: list
    minutes: dict
    shots: list
    play: list
    ratings: dict
    on_target: list
    saves: list
    starters: list
    participants: list
    keepers: list
    assists: list

class Match:
    def __init__(self, s, fixture, seed):
        self.s = s
        self.a, self.b = fixture['home'], fixture['away']
        self.slots = [select_slots(s, self.a), select_slots(s, self.b)]
        self.style = s['style']
        self.styles = [style_for(s, self.a), style_for(s, self.b)]
        self.rng = random.Random(seed)
        self.detail_rng = random.Random(seed ^ 0xC153)
        self.card_rng=random.Random(seed ^ 0x267025)
        self.spatial=bool(s.get('match_model'))
        self.positional=s.get('match_model') in (2,3,4)
        self.rules=s.get('match_model') in (3,4)
        self.instructions=[[0,0,0],[0,0,0]]
        self.loads=[0.,0.]
        self.capture=False
        self.frames=[]
        self.analysis={'decisions':[],'periods':[]}
        self.human=int(self.b==s['club']) if s['employed'] and s['club'] in (self.a,self.b) else None
        self.minute = 0
        self.score = [0, 0]
        self.shots = [0, 0]
        self.events = []
        self.play = []
        self.assists=[]
        self.starters=[[pid for _,pid in side] for side in self.slots]
        self.played=[{},{}]
        self.keepers=[{},{}]
        self.yellows=set()
        self.minutes = {}
        self.subs = 0
        self.team_subs=[0,0]
        self.used = {pid for slots in self.slots for _, pid in slots}
        self.profiles = {pid: attributes(s, player(self.s,pid)) for pid in self.used}
        self.strengths = [self.strength(slots) for slots in self.slots]
        self.pitch=CalibratedPitch(self,seed) if s.get('match_model')==4 else RulesPitch(self,seed) if self.rules else PitchState(self) if self.positional else None
        if s.get('manager_state') and s['club'] in (self.a,self.b):
            self.opening_review=[]
            for team,slots,strength in zip((self.a,self.b),self.slots,self.strengths):
                players=[player(s,pid) for _,pid in slots]
                self.opening_review.append(dict(formation=formation_for(s,team),
                    strengths={k:round(strength[k],2) for k in ROLES},
                    mismatches=sum(not suitable(s,p,role) for (role,_),p in zip(slots,players)),
                    fitness=round(sum(state(s,p)['condition'] for p in players)/max(1,len(players)),1)))

    def strength(self, slots):
        values = {role: [] for role in ROLES}
        for role, pid in slots:
            p = player(self.s,pid)
            profile = self.profiles[pid]
            group = group_for(role)
            skill = sum(profile[key] for key in SKILLS[group]) / len(SKILLS[group])
            if self.s.get('position_model'):
                details = SKILLS_BY_POSITION.get(role,SKILLS[group])
                specific = sum(profile[key] for key in details)/len(details)
                skill = .70*skill + .30*specific
                factor = fit_factor(p,role)
            else:
                factor = 1 if fits(p,role) else .64
            quality = (.48 * power(self.s, p) + .52 * skill) * factor
            values[group].append(quality)
        return {role: sum(scores) / max(1, len(scores)) for role, scores in values.items()} | {'count': len(slots)}

    @property
    def x(self):
        return self.score[0]

    @property
    def y(self):
        return self.score[1]

    @property
    def la(self):
        return [player(self.s,pid) for _, pid in self.slots[0]]

    @property
    def lb(self):
        return [player(self.s,pid) for _, pid in self.slots[1]]

    def energy(self,side):
        return max(.70,1-self.loads[side]/170)

    def instruction(self,key,value,side=None):
        side=self.human if side is None else side
        if not self.spatial or self.minute>=90 or side not in (0,1):return False
        if key=='style':
            if value not in STYLE:return False
            old=self.style if side==self.human else self.styles[side]
            if old==value:return False
            if side==self.human:self.style=value
            else:self.styles[side]=value
        else:
            if key not in konumsal.KEYS or type(value) is not int or value not in (-1,0,1):return False
            i=konumsal.KEYS.index(key)
            old=self.instructions[side][i]
            if old==value:return False
            self.instructions[side][i]=value
        decisions=self.analysis['decisions']
        for row in reversed(decisions):
            if row[0]!=self.minute:break
            if row[1:3]==[side,key]:
                if row[3]==value:decisions.remove(row)
                else:row[4]=value
                return True
        decisions.append([self.minute,side,key,old,value])
        return True

    def positional_step(self):
        if self.minute>=90:return
        self.frames=[]
        if self.minute in (55,70):
            for side in (0,1):
                if side==self.human:continue
                spread=self.score[side]-self.score[1-side]
                self.instruction('style','Attack' if spread<0 else 'Defend' if spread>0 else 'Balanced',side)
                self.instruction('press',int(spread<0),side)
        if self.minute in (64,76):
            for side in (0,1):
                if side!=self.human:self.ai_substitution(side)
        self.minute+=1
        for side,slots in enumerate(self.slots):
            press,tempo,_=self.instructions[side]
            self.loads[side]+=.20+.052*press+.042*tempo
            for role,pid in slots:
                self.played[side][pid]=None
                self.minutes[pid]=self.minutes.get(pid,0)+1
                if role=='GK':self.keepers[side][pid]=self.keepers[side].get(pid,0)+1
        self.pitch.tick()
        if self.minute%5==0:
            if not self.rules:self.discipline()
            if self.human is not None:
                self.analysis['periods'].append([self.minute,self.pitch.partial_shots[:],self.pitch.partial_recovery[:],
                    [round(x,2) for x in self.loads],self.score[:]])
        self.pitch.partial_shots=[0,0] if self.minute%5==0 else self.pitch.partial_shots
        self.pitch.partial_recovery=[0,0] if self.minute%5==0 else self.pitch.partial_recovery
        if self.minute==90 and self.human is not None:self.analysis['flow']=self.pitch.summary()

    def step(self):
        if self.positional:return self.positional_step()
        if self.minute >= 90:
            return
        self.frames=[]
        if self.spatial and self.minute in (55,70):
            for side in (0,1):
                if side==self.human:continue
                spread=self.score[side]-self.score[1-side]
                self.instruction('style','Attack' if spread<0 else 'Defend' if spread>0 else 'Balanced',side)
                self.instruction('press',int(spread<0),side)
        self.minute += 5
        won=[0,0]
        prior_shots=self.shots[:]
        slots_before=tuple(side[:] for side in self.slots) if self.capture else None
        teams = (self.a, self.b)
        for side, slots in enumerate(self.slots):
            if not slots:
                continue
            for role,pid in slots:
                self.played[side][pid]=None
                if role=='GK':
                    self.keepers[side][pid]=self.keepers[side].get(pid,0)+5
                self.minutes[pid] = self.minutes.get(pid, 0) + 5
            own, opp = self.strengths[side], self.strengths[1-side]
            attack, _ = STYLE[self.style if teams[side] == self.s['club'] and self.s['employed'] else self.styles[side]]
            _, defence = STYLE[self.style if teams[1-side] == self.s['club'] and self.s['employed'] else self.styles[1-side]]
            buildup = own['M'] * .65 + own['F'] * .35 - (opp['M'] * .5 + opp['D'] * .5)
            numbers = math.exp(.13 * (own['count'] - opp['count']))
            shot = (.60 if side == 0 else .52) * math.exp(.055 * buildup) * attack / defence * numbers
            if self.spatial:
                depth,lane,pressure,energy=konumsal.phase(self,side)
                press,tempo,width=self.instructions[side]
                self.loads[side]+=max(.3,1+press*.26+tempo*.21)
                shot*= (.82+depth*.27+tempo*.075)*energy*(1-pressure*.46)
                # Wider lanes improve the angle when there is room. Tight pressure can kill the attack.
                shot*=1+width*(.03-pressure*.10)
            if self.rng.random() >= clamp(shot, .05, .96):
                if self.spatial:
                    won[1-side]+=1
                    if self.capture:self.frames.extend(konumsal.frames(slots_before,side,self.minute,depth,lane,[]))
                continue
            event_start=len(self.play)
            self.shots[side] += 1
            candidates = [(role, pid) for role, pid in slots if role != 'GK'] or slots
            _, scorer = self.rng.choices(candidates, weights=[
                self.profiles[pid]['Finishing'] * {'F': 4, 'M': 2, 'D': 1, 'GK': .1}[group_for(role)]
                for role, pid in candidates
            ])[0]
            finish = .5 * own['F'] + .5 * self.profiles[scorer]['Finishing']
            suppliers=[pid for role,pid in slots if role != 'GK' and pid!=scorer]
            provider=None
            if suppliers and self.detail_rng.random()<.72:
                provider=self.detail_rng.choices(suppliers,weights=[self.profiles[pid]['Passing'] for pid in suppliers])[0]
                self.play.append([self.minute,side,provider,'pass',scorer])
                finish+=(self.profiles[provider]['Passing']-10)*.08
            resist = .60 * opp['GK'] + .40 * opp['D']
            if self.spatial:
                finish+=(depth-.67)*9-abs(lane-.5)*2-pressure*4+(energy-1)*7
            goal = self.rng.random() < clamp(.132 * math.exp(.070 * (finish - resist)), .035, .40)
            target = goal or self.detail_rng.random() < clamp(.36 + .015*(finish-resist), .16, .64)
            keeper = next((pid for role,pid in self.slots[1-side] if role=='GK'),None)
            outcome = 'goal' if goal else 'saved' if target and keeper else 'on_target' if target else 'wide'
            self.play.append([self.minute, side, scorer, outcome, keeper if outcome=='saved' else None])
            if goal:
                self.score[side] += 1
                self.events.append([self.minute, teams[side], scorer])
                if provider is not None:
                    self.assists.append([self.minute,side,provider,scorer])
            if self.spatial and self.capture:
                self.frames.extend(konumsal.frames(slots_before,side,self.minute,depth,lane,self.play[event_start:]))
        self.discipline()
        if self.spatial and self.human is not None:
            self.analysis['periods'].append([self.minute,[a-b for a,b in zip(self.shots,prior_shots)],
               won,[round(x,2) for x in self.loads],self.score[:]])

    def discipline(self):
        for side,slots in enumerate(self.slots):
            if not slots or self.card_rng.random()>=.105:
                continue
            index=self.card_rng.randrange(len(slots))
            _,pid=slots[index]
            if self.card_rng.random()<.043:
                event='red'
            else:
                event='yellow'
                self.play.append([self.minute,side,pid,event,None])
                if pid not in self.yellows:
                    self.yellows.add(pid)
                    continue
                event='red'
            self.play.append([self.minute,side,pid,event,None])
            slots.pop(index)
            self.strengths[side]=self.strength(slots)

    def substitute(self, outid, inid):
        if self.s['club'] not in (self.a, self.b):
            return False
        side = int(self.s['club'] == self.b)
        return self.substitute_side(side,outid,inid)

    def ai_substitution(self,side):
        team=(self.a,self.b)[side]
        slots=[(role,pid) for role,pid in self.slots[side] if role!='GK']
        if not slots:return False
        def condition(p):
            return state(self.s,p)['condition']-self.minutes.get(p['id'],0)*.24
        role,out=min(slots,key=lambda row:condition(player(self.s,row[1])))
        if condition(player(self.s,out))>=88:return False
        bench=[p for p in roster(team,self.s['year'],self.s) if p['id'] not in self.used
               and eligible(self.s,p) and group_for(p['pos'])==group_for(role)]
        for p in sorted(bench,key=lambda p:(-condition(p),p['id'])):
            if condition(p)>condition(player(self.s,out))+4 and self.substitute_side(side,out,p['id']):
                return True
        return False

    def substitute_side(self,side,outid,inid):
        team=(self.a,self.b)[side]
        slots = self.slots[side]
        incoming = player(self.s,inid)
        if ((self.team_subs[side] if self.positional else self.subs) >= 3 or self.minute >= 90 or incoming is None or inid in self.used
                or self.s['owners'].get(inid) != team or not eligible(self.s, incoming)):
            return False
        for index, (role, pid) in enumerate(slots):
            if pid != outid:
                continue
            foreigners = sum(not is_domestic(player(self.s,key)) for _, key in slots if key != outid)
            if foreigners + (not is_domestic(incoming)) > self.s['cap']:
                return False
            if isinstance(self.pitch, CalibratedPitch) and not self.pitch.settle_substitution(side, outid):
                return False
            slots[index] = (role, inid)
            self.used.add(inid)
            self.team_subs[side]+=1
            if side==self.human or not self.positional:self.subs+=1
            self.play.append([self.minute,side,inid,'sub',outid])
            self.profiles[inid] = attributes(self.s, incoming)
            self.strengths[side] = self.strength(slots)
            return True
        return False

    def finish(self):
        while self.minute < 90:
            self.step()
        return self.result()

    def detail(self):
        on_target, saves = [0,0], [0,0]
        score = {pid: 6.35 for pid in self.minutes}
        for _,side,pid,event,other in self.play:
            if event not in SHOT_EVENTS:
                continue
            if event not in ('wide','blocked'):
                on_target[side]+=1
            if event=='saved':
                saves[1-side]+=1
                score[other]=score.get(other,6.35)+.19
            score[pid]+= {'goal':.85,'saved':.07,'on_target':.07,'wide':-.055,'blocked':-.03}[event]
        home_ids={pid for pid in self.minutes if self.s['owners'].get(pid)==self.a}
        ratings={pid:round(clamp(mark+clamp((self.x-self.y)*(1 if pid in home_ids else -1)*.17,-.8,.8)
                                     * min(1,self.minutes[pid]/45),3,10),1)
                 for pid,mark in score.items() if pid in self.minutes}
        return on_target,saves,ratings

    def result(self):
        if self.minute != 90:
            raise ValueError('Match is still in progress')
        on_target,saves,ratings=self.detail()
        keepers=[[pid for pid,minutes in row.items() if minutes==90] for row in self.keepers]
        return MatchResult(self.a,self.b,self.x,self.y,self.events,self.minutes,self.shots,self.play,ratings,
                           on_target,saves,self.starters,[list(side) for side in self.played],keepers,self.assists)
