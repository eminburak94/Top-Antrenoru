"""Regression: a versatile player cannot occupy two starting positions."""
import unittest
from unittest.mock import patch
import piyasa_ai as ai


class SquadPlanningTests(unittest.TestCase):
    def test_versatile_player_cannot_cover_both_fullback_slots(self):
        player = {'id': 'versatile', 'pos': 'RB', 'alternate_positions': ['LB']}
        s = {'year': 2000, 'week': 1, 'board_targets': {'club': 10},
             'transfer_model': True}
        with patch.object(ai, 'ability', return_value=15), \
             patch.object(ai, 'known_age', return_value=25), \
             patch.object(ai, 'state', return_value={'injury': 0, 'contract': 2004}):
            needs = {role: shortage for _, role, _, shortage, _ in ai.assess(s, 'club', [player])}
        self.assertEqual(needs.get('RB', 0) + needs.get('LB', 0), 1,
                         'One versatile fullback cannot fill two starting slots')


if __name__ == '__main__':
    unittest.main()
