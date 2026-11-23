"""Regression tests. Run with py -3 -B test_v060.py [--long] [--gui]."""
from collections import Counter
import copy
import csv
import json
from pathlib import Path
import random
import runpy
import sys
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

import kariyer as k
from kayit import SaveError, autosave, backup_path, decode, encode, load_game, save_game
from mac import Match, select_slots
from oyuncu import state
from transfer import transfer, value
from veritabani import D, P, TEAMS, roster, player
from yarisma import schedule, standings
from yerellestirme import citizenship_ids, country_label, is_domestic, position_label

CLUBS = ('GALATASARAY', 'YİMPAŞ YOZGATSPOR', 'ERZURUMSPOR')

from test_fixtures import legacy_source

class Regression(unittest.TestCase):
    def test_dataset(self):
        self.assertEqual((len(P), len(TEAMS)), (606, 18))
        self.assertEqual(len(D['matches']), 306)
        self.assertTrue(all(m['score'][1] == 0 for m in D['matches']))
        self.assertTrue(all(set(m) == {'week','home','away'} for m in schedule(2000)))
        with Path('TARIHSEL_SKOR_DOGRULAMA.csv').open(encoding='utf-8-sig') as f:
            self.assertEqual(len(list(csv.DictReader(f))), 306)
        self.assertFalse([entry for p in P.values() for entry in p['citizenships'] if entry['country_id'] == 'ZZ'])
        self.assertEqual(sum(len(p['citizenships']) > 1 for p in P.values()), 10)
        self.assertTrue(all(c['valid_from'] is None for p in P.values() for c in p['citizenships']))
        self.assertIn('YU', {c for p in P.values() for c in citizenship_ids(p)})
        self.assertIn('RS-YU', {c for p in P.values() for c in citizenship_ids(p)})
        self.assertEqual(country_label('TR','TR'), 'Türkiye')
        self.assertEqual(country_label('TR','EN'), 'Turkey')
        self.assertEqual(position_label('GK','TR'), 'Kaleci')
        self.assertEqual(position_label('GK','EN'), 'Goalkeeper')

    def test_dataset_matches_archive(self):
        raw = json.loads((legacy_source(self, 'yedek_v0.5.5')/'data.json').read_text(encoding='utf8'))
        self.assertEqual(raw['matches'], D['matches'])
        self.assertEqual(raw['teams'], D['teams'])
        self.assertEqual(raw['players'], [
            {key: val for key, val in p.items() if key != 'citizenships'} for p in P.values()
        ])

    def test_mode_parity(self):
        for club in CLUBS:
            for seed in (601, 602, 876):
                fast = k.new(club, seed=seed)
                live = decode(encode(fast))
                fast['training'] = live['training'] = 'Development'
                k.advance(fast)
                match = k.LiveMatch(live)
                self.assertFalse(match.commit())
                match.finish()
                self.assertTrue(match.commit())
                self.assertFalse(match.commit())
                self.assertEqual(json.loads(encode(fast)), json.loads(encode(live)))

    def test_interventions(self):
        initial = k.new(CLUBS[0], seed=30)
        live, fast = (decode(encode(initial)) for _ in range(2))
        def plan(match):
            for _ in range(6):
                match.step()
            match.style = 'Attack'
            slots = match.la if match.a == initial['club'] else match.lb
            outgoing = slots[-1]['id']
            incoming = next(p['id'] for p in roster(initial['club'], 2000, match.s) if p['id'] not in match.used)
            self.assertTrue(match.substitute(outgoing, incoming))
            return outgoing, incoming
        match = k.LiveMatch(live)
        outgoing, incoming = plan(match)
        match.finish()
        self.assertEqual((match.minutes[outgoing], match.minutes[incoming]), (30, 60))
        self.assertTrue(match.commit())
        k.advance(fast, plan)
        self.assertEqual(json.loads(encode(fast)), json.loads(encode(live)))
        self.assertEqual(live['fitness'][outgoing]['minutes'], 30)
        self.assertEqual(live['fitness'][incoming]['minutes'], 60)

    def test_commits(self):
        s = k.new(CLUBS[0], seed=2)
        stale, active = k.LiveMatch(s), k.LiveMatch(s)
        stale.finish()
        active.finish()
        self.assertTrue(active.commit())
        saved = encode(s)
        self.assertFalse(stale.commit())
        self.assertEqual(saved, encode(s))

    def test_role_strengths_and_ids(self):
        s = k.new(CLUBS[0], seed=11)
        fixture = next(m for m in s['schedule'] if s['club'] in (m['home'], m['away']))
        match = Match(s, fixture, 2)
        side = int(match.b == s['club'])
        slots = match.slots[side]
        first, last = slots[0][1], slots[-1][1]
        wrong = [('GK', last), *slots[1:-1], ('F', first)]
        self.assertLess(match.strength(wrong)['GK'], match.strengths[side]['GK'])
        match.profiles[first]['Reflexes'] += 5
        self.assertGreater(match.strength(slots)['GK'], match.strengths[side]['GK'])
        for club in TEAMS:
            s['cap'] = 3
            self.assertLessEqual(sum(not is_domestic(P[pid]) for _, pid in select_slots(s,club)), 3)
        match.finish()
        self.assertTrue(all(pid in P for _, _, pid in match.events))

    def test_save_backup_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = k.new(CLUBS[0], seed=91)
            k.advance(s)
            target = autosave(s, tmp)
            original = encode(s)
            recovered = load_game(target)
            for _ in range(3):
                k.advance(recovered)
                k.advance(s)
            self.assertEqual(encode(s), encode(recovered))
            self.assertEqual(autosave(s, tmp), target)
            self.assertEqual(encode(load_game(backup_path(target))), original)
            other = autosave(k.new(CLUBS[0], seed=91), tmp)
            self.assertNotEqual(other, target)
            target.write_text('{broken', encoding='utf8')
            with self.assertRaises(SaveError):
                load_game(target)
            save_game(s, target)
            self.assertEqual(encode(load_game(backup_path(target))), original)
            self.assertEqual(encode(load_game(target)), encode(s))

    def test_invalid_saves(self):
        base = k.new(CLUBS[0], seed=1)
        k.advance(base)
        for change in (lambda s:s.update(schema_version=999),
                       lambda s:s.update(year='2000'),
                       lambda s:s.update(rng_state=[3, [], None]),
                       lambda s:s['owners'].update(impossible=CLUBS[0]),
                       lambda s:s['results'][0][0].update(home=CLUBS[2]),
                       lambda s:s['results'][0][0].update(x=99)):
            data = json.loads(encode(base))
            change(data)
            with self.assertRaises(SaveError):
                decode(json.dumps(data))

    def test_legacy_v055(self):
        old = runpy.run_path(str(legacy_source(self, 'yedek_v0.5.5')/'oyun.py'))
        random.seed(90)
        original = old['prepare'](old['new'](CLUBS[0]))
        original['year'] = 2006
        original['schedule'] = old['schedule'](2006)
        old['advance'](original)
        old['advance'](original)
        for schedule_missing in (True, False):
            data = copy.deepcopy(original)
            if schedule_missing:
                del data['schedule']
            else:
                data['schedule'] = old['D']['matches']
            text = json.dumps(data)
            restored = decode(text)
            self.assertEqual(restored['schedule'], schedule(2006))
            self.assertEqual(restored['teams'], original['teams'])
            self.assertEqual(encode(restored), encode(decode(text)))
            k.advance(restored)
            self.assertEqual(restored['week'], 4)
        original['results'][0][0]['away'] = 'Unknown'
        with self.assertRaises(SaveError):
            decode(json.dumps(original))

    def test_transfer_training_and_rollover(self):
        s = k.new(CLUBS[0], seed=1, models=False)
        target = next(p for p in P.values() if p['id'] in s['owners'] and p['club'] != s['club'] and p['rating'] <= 10)
        fee = value(s, target)
        source = target['club']
        balances = s['finance'][source]['cash'], s['finance'][s['club']]['cash']
        s['week'] = 4
        self.assertFalse(transfer(s, target['id'], s['club']))
        s['week'] = 1
        self.assertTrue(transfer(s, target['id'], s['club']))
        self.assertIn(target, roster(s['club'], 2000, s))
        self.assertEqual(s['finance'][source]['cash'], balances[0]+fee)
        self.assertEqual(s['finance'][s['club']]['cash'], balances[1]-fee)
        self.assertFalse(k.rollover(s))
        s['training'] = 'Development'
        resumed = decode(encode(s))
        k.advance(s)
        k.advance(resumed)
        self.assertEqual(s['week'], 2)
        self.assertEqual(json.loads(encode(s)), json.loads(encode(resumed)))

    @unittest.skipUnless('--gui' in sys.argv, 'run with --gui')
    def test_tkinter(self):
        from arayuz import UI
        root = tk.Tk()
        root.withdraw()
        try:
            ui = UI(root)
            root.update()
            self.assertIn('v0.9.0 Playtest Beta', root.title())
            ui.begin(k.new(CLUBS[0], seed=16))
            ui.autosave = lambda: None
            for screen in (ui.dashboard, ui.career_page, ui.squad, ui.table, ui.fixtures,
                           ui.tactics, ui.scorers, ui.market, ui.archive, ui.match_settings):
                screen()
                root.update()
            ui.switch()
            self.assertEqual(ui.lang, 'EN')
            ui.market()
            def descendants(parent):
                for widget in parent.winfo_children():
                    yield widget
                    yield from descendants(widget)
            market = next(widget for widget in descendants(ui.body) if isinstance(widget, ttk.Treeview))
            # The shared search displays sixty rows and keeps the remaining matches pageable.
            self.assertEqual(len(market.get_children()),60)
            first_page=market.get_children()
            next_button=next(widget for widget in descendants(ui.body) if
                             isinstance(widget,ttk.Button) and widget.cget('text')=='›')
            next_button.invoke()
            self.assertTrue(market.get_children())
            self.assertTrue(set(first_page).isdisjoint(market.get_children()))
            root.tk.call(market.heading(0, 'command'))
            first = market.item(market.get_children()[0], 'values')
            self.assertEqual(first[0], min((p['name'] for p in P.values()
                           if p['id'] in ui.s['owners'] and p['club'] != CLUBS[0]), key=str.casefold))
            self.assertEqual(first[2], position_label(next(p for p in P.values() if p['name']==first[0])['pos'],'EN'))
            ui.profile(roster(CLUBS[0], 2000, ui.s)[0])
            root.update()
            ui.s['match_mode'] = 'quick'
            with patch('arayuz.messagebox.askyesno',return_value=True):
                ui.next()
            ui.fixtures()
            ui.s['match_mode'] = 'live'
            with patch('arayuz.messagebox.askyesno',return_value=True):
                ui.next()
            root.update()
            next(widget for widget in descendants(root)
                 if 'text' in widget.keys() and widget.cget('text') == 'Finish match').invoke()
            root.update()
            self.assertEqual(ui.s['week'], 3)
        finally:
            root.destroy()

    @unittest.skipUnless('--long' in sys.argv, 'run with --long')
    def test_ten_seasons(self):
        for club in CLUBS:
            for seed in (601, 602):
                s = k.new(club, seed=seed)
                ranks = []
                totals = Counter()
                for year in range(2000, 2010):
                    self.assertEqual(s['year'], year)
                    self.assertEqual(len({(m['home'],m['away']) for m in s['schedule']}),306)
                    for week in range(1, 35):
                        self.assertEqual(s['week'], week)
                        if week in (1, 18, 34):
                            comparison = decode(encode(s)) if week == 18 else None
                            live = k.LiveMatch(s)
                            live.finish()
                            self.assertTrue(live.commit())
                            if comparison is not None:
                                k.advance(comparison)
                                self.assertEqual(json.loads(encode(s)), json.loads(encode(comparison)))
                        else:
                            k.advance(s)
                        results = s['results'][-1]
                        self.assertEqual(len(results),9)
                        self.assertEqual(len({m[key] for m in results for key in ('home','away')}),18)
                        for m in results:
                            self.assertEqual(m['x']+m['y'],len(m['events']))
                            self.assertTrue(all(player(s,pid) is not None for _,_,pid in m['events']))
                            totals.update(matches=1, goals=m['x']+m['y'], home=m['x']>m['y'], draw=m['x']==m['y'])
                    rows = s['teams'].values()
                    self.assertTrue(all(z['w']+z['d']+z['l']==34 and z['p']==3*z['w']+z['d'] for z in rows))
                    self.assertEqual(sum(z['gf'] for z in rows), sum(z['ga'] for z in rows))
                    self.assertEqual(sum(z['gf'] for z in rows), sum(s['goals'].values()))
                    ranks.append((standings(s).index(club)+1, s['teams'][club]['p']))
                    s = decode(encode(s))
                    self.assertTrue(k.advance(s))
                self.assertEqual((s['year'],s['week'],len(s['history'])),(2010,1,10))
                self.assertEqual(totals['matches'],3060)
                print(f"CAREER {club} {seed} {ranks} {dict(totals)}", flush=True)

if __name__ == '__main__':
    unittest.main(argv=[arg for arg in sys.argv if arg not in ('--long','--gui')], verbosity=2)

