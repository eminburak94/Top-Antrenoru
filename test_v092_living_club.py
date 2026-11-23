from unittest import TestCase

from finans import gate
from kariyer import advance, new
from kayit import decode, encode
from oyuncu import state
from veritabani import roster
import yasayan_kulup as life


CLUBS=('GALATASARAY','TRABZONSPOR','ERZURUMSPOR')


def career(club):
    return new(club,seed=92,match_model=4,transfer_model=True,living_club=True)


class LivingClub(TestCase):
    def test_three_profiles_keep_distinct_targets_and_play_through(self):
        targets=[]
        for club in CLUBS:
            with self.subTest(club=club):
                s=career(club)
                targets.append(s['board_targets'][club])
                for _ in range(5):
                    self.assertTrue(advance(s))
                self.assertEqual(len(s['living_club']['board']['form']),5)
                self.assertEqual(encode(decode(encode(s))),encode(s))
        self.assertLess(targets[0],targets[1])
        self.assertLess(targets[1],targets[2])

    def test_derby_response_affects_support_and_gate(self):
        s=career(CLUBS[0])
        club=s['club']
        s['week']=2
        life.update_support(s,club,'FENERBAHÇE',0,2)
        after=s['living_club']['fans'][club][0]
        self.assertLess(after,45)
        self.assertTrue(life.pending_question(s))
        p=roster(club,s['year'],s)[0]
        initial=state(s,p)['morale']
        self.assertTrue(life.press_answer(s,'protect'))
        self.assertEqual(state(s,p)['morale'],initial+2)
        self.assertFalse(life.press_answer(s,'responsibility'))
        self.assertEqual(s['living_club']['fans'][club][0],after-1)
        baseline=career(club)
        gate(baseline,club,11)
        gate(s,club,11)
        self.assertLess(s['finance'][club]['tickets'],baseline['finance'][club]['tickets'])

    def test_press_promise_settles_on_third_result(self):
        for points,expected in (([3,1,1],(3,2)),([1,0,1],(-5,-3))):
            with self.subTest(points=points):
                s=career(CLUBS[1])
                club=s['club']
                s['week']=2
                life.question(s,'poor',club,'FENERBAHÇE',week=1)
                self.assertTrue(life.press_answer(s,'promise'))
                base_fans=s['living_club']['fans'][club][0]
                base_board=s['confidence']
                for mark in points:
                    life.settle_promises(s,club,mark)
                self.assertNotIn('promise',s['living_club'])
                self.assertEqual((s['living_club']['fans'][club][0]-base_fans,s['confidence']-base_board),expected)

    def test_board_budget_reallocation_is_funded_and_has_cooldown(self):
        s=career(CLUBS[0])
        for _ in range(3):
            advance(s)
        ledger=s['finance'][s['club']]
        before=ledger.copy()
        wage,cost=life.budget_shift(s)
        self.assertGreater(wage,0)
        self.assertTrue(life.meeting(s,'budget'))
        self.assertFalse(life.meeting(s,'budget'))
        self.assertEqual(ledger['wage_budget'],before['wage_budget']+wage)
        self.assertEqual(ledger['transfer_budget'],before['transfer_budget']-cost)
        self.assertEqual(ledger['cash'],before['cash'])

    def test_dismissal_requires_a_sustained_run(self):
        s=career(CLUBS[2])
        club=s['club']
        s['teams'][club]['ga']=10
        for played in range(1,16):
            s['week']=played+1
            life.review(s,club,0)
            if played<=8:
                self.assertTrue(s['employed'])
            if not s['employed']:
                self.assertEqual(played%4,0)
                break
        self.assertFalse(s['employed'])
        self.assertEqual(s['manager_state']['decision'],'performance')
