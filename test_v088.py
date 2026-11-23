from unittest import TestCase
from unittest.mock import patch

from futbol_kalibrasyonu import open_play_target
from kariyer import LiveMatch, new
from kayit import decode, encode
from mac import eligible
from mevkiler import fit_level
from oyuncu import state
from veritabani import roster


class MatchBalance(TestCase):
    def test_model4_instructions_change_play_and_player_fitness(self):
        match_low,match_high=(LiveMatch(new('GALATASARAY',seed=887,match_model=4)) for _ in range(2))
        for m,style,level in ((match_low,'Defend',-1),(match_high,'Attack',1)):
            for _ in range(30):
                m.step()
            m.instruction('style',style)
            m.instruction('press',level)
            m.instruction('tempo',level)
            for _ in range(20):
                m.step()
        side=match_high.human
        pid=next(pid for role,pid in match_high.slots[side] if role!='GK')
        self.assertLess(match_high.player_condition(pid),match_low.player_condition(pid))
        self.assertGreater(match_high.loads[side],match_low.loads[side])
        self.assertNotEqual(match_high.play,match_low.play)

    def test_model4_opposition_manages_score_and_replaces_tired_player(self):
        m=LiveMatch(new('GALATASARAY',seed=887,match_model=4))
        side=1-m.human
        team=(m.a,m.b)[side]
        positions={pid:role for role,pid in m.slots[side]}
        for p in roster(team,m.s['year'],m.s):
            state(m.s,p)['condition']=100
        for pid in positions:
            m.initial_fitness[pid]=100
        m.minute=65
        m.score[1-side]=1
        m.coach_step(side)
        self.assertEqual((m.styles[side],m.instructions[side][:2]),('Attack',[1,1]))
        for pid in positions:
            m.exertion[pid]=32
        m.minute=70
        m.coach_step(side)
        self.assertEqual(m.instructions[side][:2],[0,1])
        substitution=next(row for row in m.play if row[3]=='sub')
        _,_,incoming,_,outgoing=substitution
        self.assertGreaterEqual(fit_level(next(p for p in roster(team,m.s['year'],m.s)
                                                if p['id']==incoming),positions[outgoing]),2)
        self.assertGreater(m.player_condition(incoming),m.player_condition(outgoing))
        m.minute=75
        m.score[side]=2
        m.coach_step(side)
        self.assertEqual((m.styles[side],m.instructions[side][:2]),('Defend',[-1,-1]))
        self.assertEqual(m.team_subs[side],1)

    def test_model4_chances_agree_with_play_and_survive_save_reload(self):
        s=new('GALATASARAY',seed=888,match_model=4)
        m=LiveMatch(s)
        m.finish()
        self.assertTrue(m.commit())
        data=decode(encode(s))['last_tactical_review']['analysis']
        outcomes={'wide','saved','on_target','goal','blocked'}
        played=[row[:4] for row in m.play if row[3] in outcomes]
        self.assertGreater(len(played),0)
        self.assertEqual([row[:4] for row in data['chances']],played)

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
