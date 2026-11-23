"""Career lifecycle shared by all front ends."""
from dataclasses import asdict
import copy
import random
from uuid import uuid4

from istatistik import accumulate
from finans import gate, initial_finances, operating, prizes, wages
from dunya import age_world, prepare_world, recruit, season_open
from menajer import evaluate
from mac import Match, lineup
from oyuncu import clamp, prepare_player, state
from veritabani import INITIAL_OWNERS, P, TEAMS, index_rosters, roster, player, all_players
from yarisma import apply_score, schedule, standings, table

from yonetim import record_week, weekly_snapshot
from antrenman import ability_snapshot, record_month
import personel
import is_piyasasi
import oyuncu_yuku as workload

SCHEMA_VERSION = 3

def new(club, manager="Menajer", seed=None, unemployed=False, models=True, economy_version=2, match_model=0,
        transfer_model=False,living_club=False,tactics_model=False,preseason=False,workload_model=False):
    if club not in TEAMS:
        raise ValueError('Unknown club')
    s = dict(club=club, manager=manager, year=2000, history=[], week=1,
             teams=table(), goals={}, results=[], selected=[], formation='4-4-2',
             style='Balanced', cap=99, lang='TR', rng_state=random.Random(seed).getstate(),
             schema_version=SCHEMA_VERSION, attribute_profile=3, position_model=1, lineup_model=1, career_id=uuid4().hex)
    if match_model:s.update(match_model=match_model,match_mode='2d')
    if tactics_model and match_model==4:s['tactics_model']=1
    if transfer_model:s['transfer_model']=1
    if workload_model:s['workload_model']=1
    prepare(s)
    personel.setup(s)
    if models:
        s['economy_model']=economy_version
        if economy_version==2:
            for ledger in s['finance'].values():ledger['commercial']=0
        from ekonomi import constrain_budget
        for team in TEAMS:constrain_budget(s,team)
        if living_club:
            from menajer import targets
            from yasayan_kulup import setup
            setup(s)
            s['board_targets']=targets(s)
        is_piyasasi.setup(s,unemployed)
        if preseason and s['employed']:
            from hazirlik import setup
            setup(s)
    return s

def prepare(s):
    s.setdefault('currency','USD')
    s.setdefault('confidence', 70)
    s.setdefault('news', [])
    s.setdefault('owners', INITIAL_OWNERS.copy())
    s.setdefault('finance', initial_finances())
    s.setdefault('transfers', [])
    if 'schedule' not in s:
        s['schedule'] = schedule(s['year'])
    if '_rosters' not in s:
        index_rosters(s)
    prepare_world(s)
    return s

def random_for(s):
    rng = random.Random(0)
    rng.setstate(s['rng_state'])
    return rng

def rollover(s):
    if s['week'] != 35 or len(s['results']) != 34:
        return False
    rng = random_for(s)
    ranking = standings(s)
    rank = ranking.index(s['club']) + 1
    confidence = clamp(s['confidence'] + (12 if rank == 1 else 5 if rank <= s['board_targets'][s['club']] else -10), 0, 100)
    s['history'].append(dict(year=s['year'], club=s['club'], teams=s['teams'],
                             goals=s['goals'], confidence=confidence, managed_stats=s['managed_stats'], player_stats=s['season_stats'], legacy_goals=s['legacy_goals']))
    s['confidence']=confidence
    evaluate(s,ranking)
    prizes(s)
    s['world_history'].append({
        'year': s['year'],
        'finance': copy.deepcopy(s['finance']),
        'squads': {team: len(roster(team,s['year'],s)) for team in TEAMS},
    })
    from transfer import return_loans
    return_loans(s)
    abilities = ability_snapshot(s)
    age_world(s,rng)
    s['season_development'] = dict(year=s['year'],club=s['club'],changes={
        pid: round(s['fitness'][pid]['ability']-old,2)
        for pid,old in abilities.items() if pid not in s['retired']})
    s.pop('training_month',None)
    s.pop('manual_xi',None)
    s.update(year=s['year'] + 1, week=1, teams=table(), goals={}, results=[],
             confidence=confidence, selected=[])
    s['managed_stats']=s['teams'][s['club']].copy()
    s['season_stats']={}
    s['legacy_goals']={}
    s['schedule'] = schedule(s['year'])
    s['news'].append([1, 'Yeni sezon / New season',
                      f'{s["year"]} | Önceki sıra / Previous rank: {rank} | Güven / Confidence: {confidence}%'])
    personel.season_open(s)
    if s.get('living_club'):
        from yasayan_kulup import new_season
        new_season(s)
    season_open(s,rng)
    s['rng_state'] = rng.getstate()
    return True

def prepare_week(s, observations=None):
    from finans import pay_due_transfers,wage_shares
    pay_due_transfers(s)
    if s.get('economy_model') and s['week'] in (5,9,13,17,21,25,29,33):
        personel.refill(s)
    if s['week'] == 18 or (s['year'] == 2000 and s['week'] == 1):
        recruit(s)
    for team in TEAMS:
        operating(s,team)
    conditioning={team:personel.effects(s,team)[0] for team in TEAMS} if 'staff_system' in s else {}
    rehab={team:workload.recovery_staff(s,team) for team in TEAMS} if s.get('workload_model') else {}
    programme=personel.team_training(s,s['club'])
    for pid, team in s['owners'].items():
        p = player(s,pid)
        observation = prepare_player(s,p,team,conditioning.get(team,0),programme,rehab.get(team))
        if observation and observations is not None:
            observations[pid] = observation
        borrower,parent=wage_shares(s,pid,state(s,p)['wage'])
        wages(s,team,borrower)
        if parent:wages(s,s['loans'][pid]['parent'],parent)
    rng = random_for(s)
    fixtures = [m for m in s['schedule'] if m['week'] == s['week']]
    return [(fixture, rng.getrandbits(64), rng.getrandbits(64)) for fixture in fixtures], rng.getstate(), programme

def apply_match(s, result, seed, loads=None, observations=None, user_programme='Normal'):
    rng = random.Random(seed)
    tracked = s.get('workload_model')
    for side,(team, goals, conceded) in enumerate(((result.home, result.x, result.y), (result.away, result.y, result.x))):
        if tracked:
            rehab = workload.recovery_staff(s,team)
            relief = workload.coaching_relief(s,team)
            programme = user_programme if team == s['club'] else 'Normal'
        for p in sorted(roster(team, s['year'], s), key=lambda p: p['id']):
            z = state(s, p)
            if z['injury']:
                z['injury_matches']=z.get('injury_matches',0)+1
            minutes = result.minutes.get(p['id'], 0)
            returning = z.get('return_weeks',0)
            if tracked:
                workload.record(z,minutes,(observations or {}).get(p['id']),relief,programme)
                workload.progress_injury(z,rehab)
            else:
                z['injury'] = max(0, z['injury'] - 1)
            z['ban'] = max(0, z['ban'] - 1)
            if not minutes:
                continue
            fraction = minutes / 90
            z['apps'] += 1
            z['minutes'] = z.get('minutes', 0) + minutes
            z['condition'] = max(35, z['condition'] - round(rng.randint(15, 25) * fraction))
            if loads is not None:
                z['condition']=clamp(z['condition']-round((loads[side]-18)*.55*fraction),35,100)
            z['morale'] = clamp(z['morale'] + (2 if goals > conceded else -2 if goals < conceded else 0), 40, 90)
            z['form'] = round(clamp(.7 * z['form'] + .3 * result.ratings[p['id']], 4, 10), 1)
            risk = workload.injury_multiplier(z,returning) if tracked else 1
            if rng.random() < .012 * fraction * risk:
                z['injury'] = rng.randint(1, 4)
                z.pop('return_weeks',None)
                if team == s['club']:
                    s['news'].append([s['week'], 'Sakatlık / Injury', p['name']])
        if team == s['club'] and s['employed']:
            is_piyasasi.record_match(s,goals,conceded)
            stats=s['managed_stats']
            stats['gf']+=goals
            stats['ga']+=conceded
            stats['p']+=3 if goals>conceded else 1 if goals==conceded else 0
            stats['w' if goals>conceded else 'd' if goals==conceded else 'l']+=1
            opponent = result.away if team == result.home else result.home
            delta = 2 if goals > conceded else -3 if goals < conceded else -1 if s['board_targets'][team] <= 5 else 0
            if not s.get('living_club'):
                s['confidence'] = clamp(s['confidence'] + delta, 0, 100)
            s['news'].append([s['week'], 'Maç / Match', f'{team} {goals}–{conceded} {opponent}'])
            if not s.get('living_club'):
                s['news'][-1][2]+=f' | {s["confidence"]}%'
    for _,_,pid,event,_ in result.play:
        if event not in ('yellow','red'):
            continue
        z=state(s,player(s,pid))
        if event=='yellow':
            z['cards']+=1
            if z['cards']%4==0:
                z['ban']=max(1,z['ban'])
        else:
            z['ban']=max(2,z['ban'])
    for _, _, pid in result.events:
        s['goals'][pid] = s['goals'].get(pid, 0) + 1
    participants = sum(s['owners'].get(pid)==result.home for pid in result.minutes)
    gate(s, result.home, participants)
    apply_score(s, result.home, result.away, result.x, result.y)

def complete_week(s, plans, rng_state, user_match=None, feedback_before=None, observations=None,
                  user_programme='Normal'):
    rows = []
    for fixture, seed, effects_seed in plans:
        if user_match is not None and fixture['home'] == user_match.a and fixture['away'] == user_match.b:
            engine=user_match
            result = engine.result()
        else:
            engine=Match(s,fixture,seed)
            result=engine.finish()
        if s.get('manager_state') and s['employed'] and s['club'] in (result.home,result.away):
            s['last_tactical_review']=dict(year=s['year'],week=s['week'],
                   home=result.home,away=result.away,opening=engine.opening_review)
            if s.get("match_model"):
                s["last_tactical_review"]["analysis"]=engine.analysis
        apply_match(s,result,effects_seed,engine.loads if engine.spatial else None,observations,user_programme)
        row=asdict(result)
        accumulate(s['season_stats'],row)
        rows.append(row)
    if feedback_before is not None:
        record_week(s, feedback_before, rows, observations)
        record_month(s,s['weekly_feedback'],observations or {})
        if 'individual_training' in s:
            s['individual_training'] = {pid: plan for pid,plan in s['individual_training'].items()
                                        if s['owners'].get(pid)==s['club']}
    personel.finish_scouting(s)
    s['results'].append(rows)
    s['week'] += 1
    s['rng_state'] = rng_state
    if s.get('living_club'):
        from yasayan_kulup import record_week as club_week
        club_week(s,rows)
    is_piyasasi.weekly(s)
    if s.get('match_model') and feedback_before is not None:
        from gundem import record
        record(s,feedback_before)

def advance(s, intervention=None):
    """Play a week in bulk. Optional callback schedules user-match interventions."""
    from hazirlik import Friendly, active, rest
    if active(s):
        if str(s['preseason']['round']) not in s['preseason']['fixtures']:
            return rest(s)
        friendly = Friendly(s)
        if intervention is not None:
            intervention(friendly)
        friendly.finish()
        return friendly.commit()
    if s['week'] == 35:
        return rollover(s)
    if intervention is not None and s['employed']:
        match = LiveMatch(s)
        intervention(match)
        match.finish()
        return match.commit()
    before = weekly_snapshot(s)
    observations = {}
    plans, rng_state, programme = prepare_week(s, observations)
    complete_week(s, plans, rng_state, feedback_before=before, observations=observations,
                  user_programme=programme)
    return True

class LiveMatch(Match):
    def __init__(self, s):
        from hazirlik import active
        if active(s):
            raise ValueError('The league has not started')
        self.career = s
        self.start = (s['year'], s['week'], s['rng_state'])
        preview = copy.deepcopy({key: value for key, value in s.items()
                                 if key not in ('_rosters', 'schedule', 'history', 'results', 'world_history')})
        preview.update(schedule=s['schedule'], history=s['history'], results=s['results'][:], world_history=s['world_history'])
        index_rosters(preview)
        self.feedback_before = weekly_snapshot(preview)
        self.observations = {}
        self.plans, self.next_rng_state, self.programme = prepare_week(preview, self.observations)
        fixture, seed, _ = next(plan for plan in self.plans if s['club'] in
                                (plan[0]['home'], plan[0]['away']))
        super().__init__(preview, fixture, seed)
        self.done = False

    def commit(self):
        current = (self.career['year'], self.career['week'], self.career['rng_state'])
        if self.done or self.minute != 90 or current != self.start:
            return False
        complete_week(self.s, self.plans, self.next_rng_state, self, self.feedback_before, self.observations,
                      self.programme)
        if 'training_month' not in self.s:
            self.career.pop('training_month',None)
        self.career.update(self.s)
        self.done = True
        return True

def career(s):
 rows=[]
 for h in list(s.get('history',[]))+[s]:
  club=h.get('club',s['club']); standings=sorted(h['teams'].items(),key=lambda q:(q[1]['p'],q[1]['gf']-q[1]['ga'],q[1]['gf']),reverse=True)
  z=h.get('managed_stats',h['teams'][club]);n=z['w']+z['d']+z['l'];rank=next(i for i,(t,_) in enumerate(standings,1) if t==club)
  rows.append(dict(year=h['year'],club=club,n=n,w=z['w'],d=z['d'],l=z['l'],gf=z['gf'],ga=z['ga'],rank=rank if n and (n==34 or h is s and s['employed']) else None,title=n==34 and rank==1,finished=n==34))
 return rows
