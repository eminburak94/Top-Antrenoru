"""July preparation calendar, separate from the league and its accounting."""
from datetime import date, timedelta
from random import Random

from mac import Match
from oyuncu import clamp, prepare_player, state
import oyuncu_yuku as workload
import personel
from veritabani import TEAMS, index_rosters, roster

DAYS = 4


def setup(s):
    s['preseason'] = dict(club=s['club'], round=0, fixtures={}, results=[], cohesion={})


def active(s):
    return (s['year'] == 2000 and s['week'] == 1 and s.get('employed')
            and s.get('preseason', {}).get('club') == s['club']
            and s['preseason']['round'] < DAYS)


def day(round_index):
    return date(2000, 7, 4) + timedelta(weeks=round_index)


def book(s, round_index, opponent=None, home=True):
    if not active(s) or type(round_index) is not int or not s['preseason']['round'] <= round_index < DAYS:
        return False
    fixtures = s['preseason']['fixtures']
    key = str(round_index)
    if opponent is None:
        fixtures.pop(key, None)
        return True
    if opponent not in TEAMS or opponent == s['club']:
        return False
    fixtures[key] = [opponent, bool(home)]
    return True


def recover(s, teams, programme):
    observations = {}
    for team in teams:
        rehab = workload.recovery_staff(s, team)
        conditioning = personel.effects(s, team)[0]
        for p in roster(team, s['year'], s):
            observations[p['id']] = prepare_player(s, p, team, conditioning, programme, rehab)
    return observations


def close_week(s, teams, observations, minutes, user_programme):
    for team in teams:
        rehab = workload.recovery_staff(s, team)
        relief = workload.coaching_relief(s, team)
        programme = user_programme if team == s['club'] else 'Normal'
        for p in roster(team, s['year'], s):
            z = state(s, p)
            if s.get('workload_model'):
                pid = p['id']
                workload.record(z, minutes.get(pid, 0), observations[pid], relief, programme)
                workload.progress_injury(z, rehab)
            else:
                z['injury'] = max(0, z['injury'] - 1)


def rest(s):
    if not active(s):
        return False
    preparation = s['preseason']
    if str(preparation['round']) in preparation['fixtures']:
        return False
    clubs = TEAMS if s.get('workload_model') else (s['club'],)
    programme = personel.team_training(s,s['club'])
    close_week(s, clubs, recover(s, clubs, programme), {}, programme)
    preparation['round'] += 1
    return True


def cohesion_bonus(s, team, formation):
    preparation = s.get('preseason')
    if not preparation or s['year'] != 2000 or team != preparation['club']:
        return 0
    weeks_left = max(0, 5 - s['week'])
    return .12 * preparation['cohesion'].get(formation, 0) * weeks_left / 4


class Friendly(Match):
    def __init__(self, s):
        from copy import deepcopy
        from kariyer import random_for

        if not active(s):
            raise ValueError('Preparation is over')
        self.career = s
        self.round = s['preseason']['round']
        self.booking = tuple(s['preseason']['fixtures'][str(self.round)])
        opponent, home = self.booking
        clubs = (s['club'], opponent)
        self.training_clubs = TEAMS if s.get('workload_model') else clubs
        preview = dict(s, fitness=deepcopy(s['fitness']), preseason=deepcopy(s['preseason']),
                       _friendly=True)
        index_rosters(preview)
        self.programme = personel.team_training(preview,s['club'])
        self.observations = recover(preview, self.training_clubs, self.programme)
        ordered = clubs if home else clubs[::-1]
        seed = random_for(s).getrandbits(64) ^ (0x9500 + self.round)
        super().__init__(preview, dict(home=ordered[0], away=ordered[1], friendly=True), seed)
        self.effects_rng = Random(seed ^ 0xB7)
        self.done = False

    def commit(self):
        s = self.career
        preparation = s['preseason']
        if (self.done or self.minute != 90 or not active(s) or preparation['round'] != self.round
                or tuple(preparation['fixtures'].get(str(self.round), ())) != self.booking):
            return False
        result = self.result()
        for pid, minutes in result.minutes.items():
            z = self.s['fitness'][pid]
            z['condition'] = max(35, z['condition'] - round(self.effects_rng.randint(12, 20) * minutes / 90))
            z['form'] = round(clamp(.85 * z['form'] + .15 * result.ratings[pid], 4, 10), 1)
        close_week(self.s, self.training_clubs, self.observations, result.minutes, self.programme)
        s['fitness'].update(self.s['fitness'])
        familiarity = preparation['cohesion']
        formation = self.s['formation']
        familiarity[formation] = familiarity.get(formation, 0) + 1
        preparation['results'].append([self.round, result.home, result.away, result.x, result.y])
        preparation['round'] += 1
        self.done = True
        return True
