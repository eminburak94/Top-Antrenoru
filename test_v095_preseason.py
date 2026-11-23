from copy import deepcopy
from unittest import TestCase

from hazirlik import Friendly, active, book, cohesion_bonus
from kariyer import advance, new
from kayit import decode, encode
from oyuncu import state
from veritabani import roster


def summer():
    return new('GALATASARAY', seed=950, match_model=4, tactics_model=True,
               living_club=True, preseason=True)


class PreseasonTests(TestCase):
    def test_booking_roundtrip_and_isolated_effects_then_league(self):
        s = summer()
        self.assertFalse(book(s, 0, s['club']))
        self.assertTrue(book(s, 0, 'FENERBAHÇE', home=False))
        self.assertTrue(book(s, 2, 'BEŞİKTAŞ'))
        self.assertTrue(book(s, 2))
        s = decode(encode(s))
        keys = ('results', 'teams', 'goals', 'season_stats', 'managed_stats', 'finance', 'rng_state')
        before = {key: deepcopy(s[key]) for key in keys}
        match = Friendly(s)
        self.assertEqual((match.a, match.b), ('FENERBAHÇE', s['club']))
        self.assertFalse(match.commit())
        match.finish()
        pid = next(pid for pid in match.minutes if s['owners'][pid] == s['club'])
        z = state(s, next(p for p in roster(s['club'], 2000, s) if p['id'] == pid))
        opening_condition = z['condition']
        self.assertTrue(match.commit())
        self.assertFalse(match.commit())
        self.assertEqual(before, {key:s[key] for key in keys})
        self.assertLess(s['fitness'][pid]['condition'], opening_condition)
        self.assertGreater(cohesion_bonus(s, s['club'], s['formation']), 0)
        self.assertFalse(book(s, 0, 'BEŞİKTAŞ'))
        for _ in range(3):
            self.assertTrue(advance(s))
        self.assertFalse(active(s))
        self.assertEqual(s['week'], 1)
        s = decode(encode(s))
        self.assertTrue(advance(s))
        self.assertEqual((s['week'], len(s['results'])), (2, 1))

    def test_friendly_has_six_substitutions_without_reentry(self):
        s = summer()
        book(s, 0, 'BEŞİKTAŞ')
        m = Friendly(s)
        s['cap'] = 99
        squad = roster(s['club'], s['year'], m.s)
        for _, outgoing in m.slots[0][1:7]:
            incoming = next(p for p in squad if p['id'] not in m.used and p['pos'] != 'GK')
            self.assertTrue(m.substitute(outgoing, incoming['id']))
            self.assertFalse(m.substitute(incoming['id'], outgoing))
        remaining = next(p for p in squad if p['id'] not in m.used and p['pos'] == 'GK')
        self.assertFalse(m.substitute(m.slots[0][0][1], remaining['id']))
        self.assertEqual(m.team_subs, [6, 0])

    def test_legacy_career_starts_directly_in_league(self):
        s = decode(encode(new('GALATASARAY', seed=950, match_model=4)))
        self.assertFalse(active(s))
        self.assertTrue(advance(s))
        self.assertEqual(len(s['results']), 1)
