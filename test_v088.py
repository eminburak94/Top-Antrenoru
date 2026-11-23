from unittest import TestCase
from unittest.mock import patch

from futbol_kalibrasyonu import open_play_target
from kariyer import LiveMatch, new
from mac import eligible
from veritabani import roster


class MatchBalance(TestCase):
    def test_model4_deflections_use_the_first_line_crossed_and_last_touch(self):
        pitch=LiveMatch(new('GALATASARAY',seed=813,match_model=4)).pitch
        cases=(
            ((.9,.7),(1.1,.8),0,('goal_kick',1,(.94,.5))),
            ((.9,.7),(1.1,.8),1,('corner',0,(.99,.98))),
            ((.1,.3),(-.1,.2),1,('goal_kick',0,(.06,.5))),
            ((.1,.3),(-.1,.2),0,('corner',1,(.01,.02))),
            ((.8,.9),(1.1,1.2),0,('throw',1,(.9,1))),
        )
        for origin,destination,last_side,(restart,side,point) in cases:
            with self.subTest(origin=origin,destination=destination,last_side=last_side):
                last_player=pitch.m.slots[last_side][0][1]
                pitch.receive(last_side,last_player)
                pitch.last_pass=(last_side,last_player,last_player)
                self.assertTrue(pitch.boundary(origin,destination,last_side,last_player))
                self.assertEqual((pitch.restart,pitch.side),(restart,side))
                self.assertIsNone(pitch.owner)
                self.assertIsNone(pitch.last_pass)
                for actual,expected in zip(pitch.ball,point):
                    self.assertAlmostEqual(actual,expected)

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


    def test_substitution_cannot_erase_deferred_caution_or_replace_dismissed_player(self):
        for previous in (False, True):
            with self.subTest(previous=previous):
                match=LiveMatch(new('GALATASARAY',seed=813,match_model=4))
                side=match.human
                pitch=match.pitch
                outgoing=match.slots[side][-1][1]
                incoming=next(p['id'] for p in roster(match.s['club'],match.s['year'],match.s)
                              if p['id'] not in match.used and eligible(match.s,p))
                if previous:
                    pitch.card(side,outgoing,1)
                pitch.pending_cards.append((side,outgoing,1))
                self.assertEqual(match.substitute(outgoing,incoming),not previous)
                self.assertEqual(len(match.slots[side]),10 if previous else 11)
                self.assertFalse(pitch.pending_cards)
                relevant=[row[3] for row in match.play if row[2]==outgoing]
                self.assertEqual(relevant,['yellow','yellow','second_yellow','red'] if previous else ['yellow'])


    def test_no_caution_does_not_depend_on_pitch_anchor(self):
        match=LiveMatch(new('GALATASARAY',seed=813,match_model=4))
        self.assertTrue(match.pitch.settle_substitution(match.human,'not-yet-aligned'))
