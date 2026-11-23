import json
from unittest import TestCase

from antrenman import apply_plan, plan_for, recent_minutes
from kariyer import LiveMatch, advance, new
from kayit import decode, encode
from oyuncu import prepare_player
from veritabani import roster
from yasayan_kulup import record_week


def career():
    return new('GALATASARAY', seed=94, match_model=4, tactics_model=True, living_club=True)


class Playtest094(TestCase):
    def test_intensity_counts_minutes_without_changing_development_credit(self):
        rested = dict(condition=90, injury=0)
        fatigued = rested.copy()
        lower = apply_plan(rested, 'physical', 'intense', 20, 0)
        higher = apply_plan(fatigued, 'physical', 'intense', 20, 90)
        self.assertEqual(higher[3], lower[3])
        self.assertEqual(higher[4], lower[4]-2)

    def test_auto_training_uses_pre_recovery_condition_and_recent_minutes(self):
        s=career()
        pid=roster(s['club'],s['year'],s)[0]['id']
        p=roster(s['club'],s['year'],s)[0]
        z=s['fitness'][pid]
        s['auto_training']=True
        s['week']=2
        s['weekly_feedback']=dict(club=s['club'],year=s['year'],week=1,players={pid:{'minutes':0}})
        self.assertEqual(recent_minutes(s,pid),0)
        self.assertEqual(plan_for(s,p,z,20),('technical','normal'))
        z['condition']=65
        self.assertEqual(prepare_player(s,p,s['club'],0,'Normal')[:3],
                         ['recovery','normal','recovered'])
        s['week']=3
        self.assertIsNone(recent_minutes(s,pid))

    def test_first_win_and_financial_pressure_have_separate_reasons(self):
        for stressed in (False,True):
            with self.subTest(stressed=stressed):
                s=career()
                club=s['club']
                life=s['living_club']
                self.assertEqual(life['board']['risk'],10)
                life['board']['risk']=0  # Legacy career before its first review.
                s['week']=2
                if stressed:s['finance'][club]['cash']=-1
                record_week(s,[dict(home=club,away='FENERBAHÇE',x=3,y=0)])
                review=life['match_review']
                self.assertEqual(review['stress'],stressed)
                self.assertEqual(review['risk'],8 if stressed else -1)
                self.assertEqual(review['trust'],0 if stressed else 2)
                self.assertGreater(review['fans'],0)

    def test_live_capture_and_fast_match_share_zone_metrics_and_career(self):
        s=career()
        pid=roster(s['club'],s['year'],s)[0]['id']
        s['individual_training']={pid:['recovery','normal']}
        other=decode(encode(s))
        live=LiveMatch(s)
        live.capture=True
        fast=LiveMatch(other)
        fast.capture=False
        deliveries=[]
        for match in (live,fast):
            for _ in range(12): match.step()
            self.assertTrue(match.instruction('line',1))
            while match.minute<90:
                match.step()
                deliveries.extend(frame[4]['delivery'] for frame in match.frames
                                  if len(frame)>4 and 'delivery' in frame[4])
            self.assertTrue(match.commit())
        self.assertTrue(deliveries)
        self.assertEqual(json.loads(encode(s)),json.loads(encode(other)))
        self.assertEqual(json.loads(encode(s)),json.loads(encode(decode(encode(s)))))
        audit=s['last_tactical_review']['analysis']
        self.assertEqual([sum(row) for row in audit['zones']],audit['flow']['possession'])
        self.assertEqual(audit['decisions'][0][0],12)
        self.assertEqual(s['weekly_feedback']['players'][pid]['session'][:2],['recovery','normal'])
        self.assertNotIn('tactical_plans',s)
        self.assertTrue(advance(other))
