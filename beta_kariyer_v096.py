"""Reproducible season-by-season beta check with no user save access."""
import argparse
import json
from pathlib import Path
from statistics import mean
from tempfile import TemporaryDirectory
from time import perf_counter

from hazirlik import book
from kariyer import advance, new
from kayit import decode, encode, load_game, save_game
from veritabani import TEAMS, roster


def audit(club, seasons, model, seed):
    s = new(club, seed=seed, match_model=model, tactics_model=model == 4, transfer_model=True,
            living_club=True, preseason=True, workload_model=True)
    for index, rival in zip((0, 2), (team for team in TEAMS if team != club)):
        assert book(s, index, rival)
    for _ in range(4):
        assert advance(s)
    with TemporaryDirectory() as directory:
        path = Path(directory) / 'probe.json'
        for _ in range(seasons):
            tick = perf_counter()
            transfer_start = len(s['transfers'])
            retired = len(s['retired'])
            generated = len(s['generated'])
            injured_player_weeks = player_weeks = 0
            for _ in range(34):
                assert advance(s)
                active = [s['fitness'][pid] for pid in s['owners']]
                player_weeks += len(active)
                injured_player_weeks += sum(z['injury'] > 0 for z in active)
            assert s['week'] == 35 and len(s['results']) == 34
            assert all(len(round_results) == 9 for round_results in s['results'])
            assert sum(row['gf'] for row in s['teams'].values()) == sum(row['ga'] for row in s['teams'].values())
            finish = s['year']
            if finish in (2000, 2004, 2009, 2019) or finish == 1999 + seasons:
                save_game(s, path)
                loaded = load_game(path)
                assert json.loads(encode(s)) == json.loads(encode(loaded))
                s = loaded
            assert advance(s) and s['year'] == finish + 1 and s['week'] == 1
            loaded = decode(encode(s))
            assert json.loads(encode(s)) == json.loads(encode(loaded))
            squads = [len(roster(team,s['year'],s)) for team in TEAMS]
            assert min(squads) >= 11 and sum(squads) == len(s['owners'])
            finances = list(s['finance'].values())
            assert all(row['transfer_budget'] >= 0 and row['wage_budget'] >= 0 for row in finances)
            assert not set(s['owners']) & set(s['retired'])
            print(json.dumps(dict(season=finish, matches=306, squad=[min(squads),max(squads)],
                generated=len(s['generated'])-generated, retired=len(s['retired'])-retired,
                transfers=len(s['transfers'])-transfer_start,
                mean_wage=round(mean(s['fitness'][pid]['wage'] for pid in s['owners'])),
                cash_min=min(row['cash'] for row in finances),
                median_budget=sorted(row['transfer_budget'] for row in finances)[len(finances)//2],
                injured_player_weeks=injured_player_weeks, player_weeks=player_weeks,
                seconds=round(perf_counter()-tick,2))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--club', default='GALATASARAY')
    parser.add_argument('--seasons', type=int, required=True)
    parser.add_argument('--model', type=int, choices=(0,4), default=4)
    parser.add_argument('--seed', type=int, default=960)
    args = parser.parse_args()
    audit(args.club, args.seasons, args.model, args.seed)
