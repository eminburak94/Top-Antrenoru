import random
import unittest
from unittest.mock import patch

import is_piyasasi as jobs
from finans import can_pay
from kariyer import advance, new
from kayit import decode, encode
from mevkiler import fit_level
from oyuncu import ability, age_at, develop, state
from piyasa_ai import contract_cost_penalty
from sozlesme import asking_terms, player_accepts
from transfer import add_offer, answer_offer, counter_limit, selling_ready
from veritabani import roster


CLUB = 'GALATASARAY'
BUYER = 'FENERBAHÇE'


class ManagementDepth(unittest.TestCase):
    def test_total_cost_can_favour_paid_transfer(self):
        plan = {'wages': 17000, 'wage_room': 22000}
        fee = {'years': 2, 'wage': 1100, 'signing': 2200}
        free = {'years': 2, 'wage': 3000, 'signing': 6000}
        self.assertLess(contract_cost_penalty(100000, fee, plan, 400000),
                        contract_cost_penalty(0, free, plan, 400000))

    def test_counter_needs_and_budget_change_the_outcome(self):
        s = new(CLUB, seed=813, match_model=4)
        for p in sorted(roster(CLUB, s['year'], s), key=lambda p: ability(s, p)):
            terms = asking_terms(s, p, BUYER, 'Starter')
            terms['wage'] = round(1.31 * terms['wage'])
            if (selling_ready(s, p) and fit_level(p, p['pos']) >= 2
                    and player_accepts(s, p, BUYER, **terms)
                    and can_pay(s, BUYER, 1260, terms['signing'], terms['wage'])):
                break
        else:
            self.fail('No affordable player to test the counteroffer')
        self.assertTrue(add_offer(s, p, BUYER, 1000, terms))
        offer = s['offers'][0]
        with patch('piyasa_ai.assess', return_value=[]):
            self.assertEqual(counter_limit(s, offer), 1080)
            self.assertEqual(answer_offer(s, 0, 'counter', 1200), (False, 'buyer'))
        with patch('piyasa_ai.assess', return_value=[(12, p['pos'], 0, 1, 0)]):
            self.assertEqual(counter_limit(s, offer), 1260)
            ledger = s['finance'][BUYER]
            budget = ledger['transfer_budget']
            ledger['transfer_budget'] = 0
            self.assertEqual(answer_offer(s, 0, 'counter', 1200), (False, 'budget'))
            self.assertEqual(offer['status'], 'open')
            ledger['transfer_budget'] = budget
            self.assertEqual(answer_offer(s, 0, 'counter', 1200), (True, 'accepted'))
        self.assertEqual(s['owners'][p['id']], BUYER)
        self.assertEqual(s['transfers'][-1][-1], 1200)

    def test_season_performance_changes_youth_development(self):
        s = new(CLUB, seed=813, match_model=4)
        p = next(p for p in roster(CLUB, s['year'], s)
                 if 16 <= age_at(p, s['year']+1, 1) <= 23)
        outcomes = []
        for mark in (57, 65, 74):
            career = new(CLUB, seed=813, match_model=4)
            z = state(career, p)
            z.update(potential=19, ability=12, condition=100, training_weeks=20)
            career['season_stats'][p['id']] = {CLUB: {'rated': 25, 'rating_sum': 25*mark}}
            develop(career, p, random.Random(30), minutes=2200)
            outcomes.append(z['ability'])
        self.assertLess(outcomes[0], outcomes[1])
        self.assertLess(outcomes[1], outcomes[2])

    def test_natural_fitness_changes_senior_decline(self):
        declines = []
        for fitness in (6, 16):
            s = new(CLUB, seed=813, match_model=4)
            p = next(p for p in roster(CLUB, s['year'], s)
                     if isinstance(age_at(p, s['year']+1, 1), int) and age_at(p, s['year']+1, 1) >= 33)
            state(s, p).update(ability=12, potential=16)
            with patch('oyuncu.attributes', return_value={'Natural fitness': fitness}):
                develop(s, p, random.Random(30), minutes=2200)
            declines.append(12-ability(s, p))
        self.assertGreater(declines[0], declines[1])
        self.assertGreater(declines[1], 0)

    def test_low_reputation_gets_a_reentry_job_and_round_trips(self):
        s = new(CLUB, seed=813, match_model=4)
        self.assertTrue(jobs.leave(s, 'financial'))
        s['manager_rep'] = 10
        self.assertEqual(jobs.application_score(s), 6)
        while s['week'] < 7:
            self.assertTrue(advance(s))
        team = next(team for team, row in s['manager_state']['vacancies'].items()
                    if row['required'] <= 6)
        self.assertTrue(jobs.apply(s, team))
        self.assertTrue(advance(s))
        s = decode(encode(s))
        self.assertEqual(jobs.application(s, team)['status'], 'offered')
        self.assertTrue(jobs.offer(s, team, True))
        self.assertEqual(s['manager_state']['active_team'], team)

    def test_last_week_to_apply_leaves_time_to_consider_offer(self):
        s = new(CLUB, seed=813, match_model=4, unemployed=True)
        team, opening = next(iter(s['manager_state']['vacancies'].items()))
        while jobs.clock(s)+1 < opening['closes']:
            self.assertTrue(advance(s))
        self.assertFalse(jobs.apply(s, team))
        self.assertIsNone(jobs.application(s, team))
