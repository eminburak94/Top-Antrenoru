from unittest import TestCase
from unittest.mock import patch

from futbol_kalibrasyonu import open_play_target
from kariyer import LiveMatch, new


class MatchBalance(TestCase):
    def test_open_play_effect_is_bounded_and_neutral_at_equal_strength(self):
        self.assertEqual(open_play_target(.5,12,12),.5)
        self.assertGreater(open_play_target(.5,14,12),.5)
        self.assertLess(open_play_target(.5,12,14),.5)
        self.assertEqual(open_play_target(.5,20,1),.6)

    def test_deferred_second_yellow_prevents_duplicate_dismissal(self):
        match=LiveMatch(new('GALATASARAY',seed=813,match_model=4))
        pitch=match.pitch
        defender=match.slots[1][3][1]
        attacker=match.slots[0][-1][1]
        pitch.card(1,defender,1)
        pitch.pending_cards.append((1,defender,1))
        pitch.xy[attacker]=(.65,.5)
        pitch.receive(0,attacker)
        with patch.object(match.card_rng,'random',return_value=0):
            pitch.foul(defender,.95,allow_advantage=False)
        self.assertEqual(pitch.restart,'freekick')
        self.assertEqual(len(match.slots[1]),10)
        for event,count in [('yellow',2),('second_yellow',1),('red',1),('foul',1)]:
            self.assertEqual(sum(row[2]==defender and row[3]==event for row in match.play),count)
