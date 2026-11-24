import unittest
from unittest.mock import patch
from contextlib import ExitStack
import mac


class AIYouthLineupTests(unittest.TestCase):
    def selected(self, age=20, condition=80, potential=15, senior=10.4,
                 team='AI', employed=True, mode='legacy', injury=0, ban=0):
        s = dict(year=2000, week=1, club='USER', employed=employed,
                 selected=[], cap=11, position_model=mode != 'legacy',
                 lineup_model=mode == 'assignment')
        players = [{'id':'1','pos':'GK'}, {'id':'2','pos':'GK'}]
        states = {'1':dict(ability=10, potential=potential, condition=condition,
                           injury=injury, ban=ban),
                  '2':dict(ability=senior, potential=senior, condition=100,
                           injury=0, ban=0)}
        with ExitStack() as stack:
            for name, kwargs in {
                'mac.roster':dict(return_value=players),
                'mac.state':dict(side_effect=lambda s,p: states[p['id']]),
                'mac.power':dict(side_effect=lambda s,p: states[p['id']]['ability']),
                'mac.is_domestic':dict(return_value=True),
                'mac.formation_for':dict(return_value='4-4-2'),
                'mac.fits':dict(return_value=True),
                'mac.match_positions':dict(return_value=['GK']),
                'mac.fit_level':dict(return_value=4),
                'oyuncu.age_at':dict(side_effect=lambda p,y,w: age if p['id']=='1' else 30),
            }.items():
                stack.enter_context(patch(name, **kwargs))
            slots = mac.select_slots(s, team, use_manual=False)
        return next(pid for role,pid in slots if role=='GK')

    def test_youth_advantage_all_modes(self):
        for mode in ('legacy','position','assignment'):
            with self.subTest(mode=mode):
                self.assertEqual(self.selected(mode=mode), '1')

    def test_superior_senior(self): self.assertEqual(self.selected(senior=11), '2')
    def test_age_boundary(self): self.assertEqual(self.selected(age=23), '2')
    def test_condition_boundary(self): self.assertEqual(self.selected(condition=75), '1')
    def test_low_condition(self): self.assertEqual(self.selected(condition=74), '2')
    def test_no_potential_gap(self): self.assertEqual(self.selected(potential=10), '2')
    def test_user_team(self): self.assertEqual(self.selected(team='USER'), '2')
    def test_invalid_age(self): self.assertEqual(self.selected(age='?'), '2')
    def test_injured(self): self.assertEqual(self.selected(injury=1), '2')
    def test_suspended(self): self.assertEqual(self.selected(ban=1), '2')
    def test_unemployed_team(self): self.assertEqual(self.selected(team='USER', employed=False), '1')

if __name__ == '__main__':
    unittest.main()
