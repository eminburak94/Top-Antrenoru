from unittest import TestCase
from unittest.mock import patch

from kariyer import LiveMatch, new
from kayit import decode, encode
from mac import Match


class OpponentCoachTests(TestCase):
    def test_controls_respond_to_score_condition_and_profiles(self):
        m = LiveMatch(new('GALATASARAY', seed=960, match_model=4, tactics_model=True))
        side = 1 - m.human
        for _,pid in m.slots[side]:
            m.initial_fitness[pid] = 95
            m.profiles[pid]['Work rate'] = 15
            m.profiles[pid]['Pace'] = 7
        for _,pid in m.slots[m.human]:
            m.profiles[pid]['Pace'] = 17
        m.score[m.human] = 1
        m.minute = 60
        m.coach_step(side)
        self.assertEqual((m.styles[side],m.instructions[side][:2]), ('Attack',[1,1]))
        self.assertEqual(m.team_orders[side]['line'], -1)
        for _,pid in m.slots[side]:
            m.exertion[pid] = 29
        m.minute = 70
        m.coach_step(side)
        self.assertEqual(m.instructions[side][:2], [-1,0])
        m.minute = 80
        m.score[side] = 2
        m.coach_step(side)
        self.assertEqual((m.styles[side],m.team_orders[side]['counter']), ('Defend',1))

    def test_seeded_lineups_change_match_flow_beyond_the_score(self):
        for club,shape,seed in [('GALATASARAY','4-4-2',960),('ERZURUMSPOR','3-5-2',961),
                                ('GENÇLERBİRLİĞİ','4-3-3',962)]:
            with self.subTest(club=club,shape=shape):
                s = new(club, seed=seed, match_model=4, tactics_model=True)
                s['formation'] = shape
                other = decode(encode(s))
                fixture = next(m for m in s['schedule'] if m['week']==1 and club in (m['home'],m['away']))
                current, previous = Match(s,fixture,seed), Match(other,fixture,seed)
                current.finish()
                with patch.object(Match,'adaptive_orders',return_value={}):
                    previous.finish()
                self.assertTrue(any(row[1]!=current.human and row[2] in ('line','passing','counter','overlap')
                                    for row in current.analysis['decisions']))
                metrics = lambda match: (match.analysis['flow'],match.analysis['zones'],
                                         match.analysis['advanced_regains'])
                self.assertNotEqual(metrics(current),metrics(previous))
