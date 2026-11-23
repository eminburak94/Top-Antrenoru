from copy import deepcopy
import json
from unittest import TestCase

from hazirlik import book
from kariyer import LiveMatch, advance, new
from kayit import decode, encode
from oyuncu import prepare_player
from oyuncu_yuku import (coaching_relief, fatigue, injury_multiplier, progress_injury, record,
                        recovery_ceiling, recovery_staff)
from personel import active, contract, release
from veritabani import roster


def career(preseason=False):
    return new('GALATASARAY', seed=951, match_model=4, tactics_model=True,
               workload_model=True, preseason=preseason)


class WorkloadTests(TestCase):
    def test_three_week_window_and_real_staff_skills(self):
        s = career()
        team = s['club']
        coach = active(s, team, 'coach')[0][1]
        phys = active(s, team, 'fitness')[0][1]
        coach['skills']['coaching'] = 16
        phys['skills']['fitness'] = 15
        relief = coaching_relief(s, team)
        staff = recovery_staff(s, team)
        self.assertEqual((relief, staff), (2, (3, False)))
        self.assertTrue(release(s,team,active(s,team,'scout')[0][0]))
        self.assertTrue(contract(s,team,'medical-08',2)[0])
        staff = recovery_staff(s, team)
        self.assertEqual(staff,(5,True))
        self.assertEqual(recovery_staff(decode(encode(s)),team),staff)
        fresh = {'injury': 0}
        heavy = deepcopy(fresh)
        for _ in range(3):
            record(heavy, 90, ('physical', 'intense', 'trained', 1, -8), 0)
            record(fresh, 0, ('recovery', 'light', 'recovered', 0, 2), relief)
        self.assertLess(recovery_ceiling(heavy, (0, False)), recovery_ceiling(heavy, staff))
        self.assertLess(recovery_ceiling(heavy, staff), recovery_ceiling(fresh, staff))
        self.assertGreater(injury_multiplier(heavy, 0), injury_multiplier(fresh, 0))
        record(heavy, 90, ('physical', 'intense', 'trained', 1, -8), relief)
        self.assertEqual(heavy['workload'], [[90,8],[90,8],[90,6]])
        for _ in range(3):
            record(heavy, 0, None, relief, 'Rest')
        self.assertEqual(fatigue(heavy), 0)

    def test_return_session_treats_player_without_development_credit(self):
        s = career()
        p = roster(s['club'], s['year'], s)[0]
        pid = p['id']
        s['individual_training'] = {pid: ['physical','intense']}
        z = s['fitness'][pid]
        z['injury'] = 1
        good, poor = (3, True), (0, False)
        slow = deepcopy(z)
        progress_injury(z, good)
        progress_injury(slow, poor)
        self.assertEqual((z['return_weeks'], slow['return_weeks']), (1, 2))
        credit_before = z.get('training_weeks',0)
        observation = prepare_player(s,p,s['club'],0,'Normal',good)
        self.assertEqual(observation[:4], ['recovery','light','recovered',0])
        self.assertEqual(z.get('training_weeks',0), credit_before)
        self.assertEqual(z['condition'],92)
        progress_injury(z, good)
        self.assertNotIn('return_weeks',z)

    def test_friendlies_and_league_share_window_and_fast_live_paths_agree(self):
        s = career(preseason=True)
        self.assertTrue(book(s,0,'BEŞİKTAŞ'))
        self.assertTrue(advance(s))
        pid = next(pid for pid,z in s['fitness'].items()
                   if s['owners'].get(pid)==s['club'] and z['workload'][-1][0]>0)
        self.assertEqual(s['fitness'][pid]['apps'],0)
        self.assertTrue(book(s,1,'FENERBAHÇE'))
        for _ in range(3):
            self.assertTrue(advance(s))
        self.assertEqual(s['fitness'][pid]['workload'][-1][0],0)
        quick = decode(encode(s))
        live = LiveMatch(s)
        live.capture = True
        live.finish()
        self.assertTrue(live.commit())
        self.assertTrue(advance(quick))
        self.assertEqual(json.loads(encode(quick)),json.loads(encode(s)))
        self.assertEqual(len(s['fitness'][pid]['workload']),3)
        self.assertEqual(len(s['results']),1)
