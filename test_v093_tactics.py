import json
from unittest import TestCase

from kariyer import LiveMatch, advance, new
from kayit import SaveError, decode, encode
from taktik_denetim_v093 import measure


def career():
    return new('GALATASARAY',seed=9300,match_model=4,tactics_model=True)


class TacticalEngine(TestCase):
    def test_paired_tactics_change_passes_regains_and_position(self):
        for mode,low,high,metric in (
                ('press',-1,1,'regains'),('width',-1,1,'wide'),
                ('passing',-1,1,'pass_m'),('role','defensive_back','wingback','back')):
            with self.subTest(tactic=mode):
                a=sum(measure(seed,mode,low)[metric] for seed in range(9301,9309))
                b=sum(measure(seed,mode,high)[metric] for seed in range(9301,9309))
                self.assertGreater(b,a)

    def test_live_instructions_and_roles_affect_next_steps_without_rewriting_plan(self):
        s=career()
        s['tactical_plans']={s['club']:{'line':1,'passing':0}}
        m=LiveMatch(s)
        side=m.human
        start=m.team_orders[side]['line']
        self.assertEqual(start,1)
        for _ in range(70):
            m.step()
        pos,pid=next((pos,pid) for pos,pid in m.slots[side] if pos=='RB')
        self.assertFalse(m.assign_role(pid,'target'))
        self.assertTrue(m.assign_role(pid,'defensive_back'))
        self.assertTrue(m.instruction('line',-1))
        self.assertEqual(m.minute,70)
        self.assertEqual(m.pitch.role(side,pid,pos),'defensive_back')
        self.assertEqual(m.analysis['role_changes'][0][:3],[70,side,pid])
        m.step()
        self.assertEqual(m.minute,71)
        m.finish()
        self.assertTrue(m.commit())
        restored=decode(encode(s))
        self.assertEqual(restored['tactical_plans'][s['club']]['line'],1)
        self.assertIn([70,side,'line',1,-1],restored['last_tactical_review']['analysis']['decisions'])
        self.assertEqual(restored['last_tactical_review']['analysis']['role_changes'],m.analysis['role_changes'])

    def test_capture_and_quick_play_share_authoritative_result(self):
        s=career()
        s['tactical_plans']={s['club']:{'press':1,'passing':1,'line':-1}}
        quick=decode(encode(s))
        self.assertTrue(advance(quick))
        live=LiveMatch(s)
        live.capture=True
        live.finish()
        self.assertTrue(live.frames)
        self.assertTrue(live.commit())
        self.assertEqual(json.loads(encode(s)),json.loads(encode(quick)))

    def test_invalid_order_is_rejected_and_legacy_order_is_inactive(self):
        s=career()
        s['tactical_plans']={s['club']:{'line':4}}
        with self.assertRaises(SaveError):
            decode(encode(s))
        old=new('GALATASARAY',seed=9300,match_model=4)
        restored=decode(encode(old))
        self.assertNotIn('tactics_model',restored)
        self.assertFalse(LiveMatch(restored).instruction('line',-1))
