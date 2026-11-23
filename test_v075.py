from collections import Counter,defaultdict
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import kariyer as k
from dunya import group
from finans import payroll
from istatistik import combine
from kayit import decode,encode
from tarihsel import reconcile
from oyuncu import state
from sozlesme import asking_terms
from transfer import add_offer,reject_all,set_sale_status
from veritabani import HISTORICAL,P,TEAMS,available,player,roster
from yerellestirme import citizenship_ids,is_domestic
from yarisma import standings

ROOT=Path(__file__).resolve().parent

from test_fixtures import legacy_source

class Generations(unittest.TestCase):
    def test_import_and_dates(self):
        self.assertEqual(len(P),606)
        self.assertGreaterEqual(len(HISTORICAL),5)
        records=json.loads((ROOT/'tarihsel_girisler.json').read_text(encoding='utf8'))
        accepted,review=reconcile(list(P.values()),records+[records[0]])
        self.assertEqual((len(accepted),len(review)),(len(records),1))
        collision=dict(records[0],id='99999999',dob='1985-11-10')
        self.assertTrue(reconcile([records[0]],[collision])[1])
        s=k.new('GALATASARAY',seed=6)
        selcuk=HISTORICAL['53537']
        self.assertFalse(available(s,selcuk))
        s['week']=4
        self.assertTrue(available(s,selcuk))
        self.assertFalse(available(s,HISTORICAL['433728']))

    def test_old_save_bonus_once(self):
        script="import kariyer as k; from kayit import encode; s=k.new('GALATASARAY',seed=6); k.advance(s); print(encode(s))"
        raw=subprocess.check_output([sys.executable,'-B','-c',script],cwd=legacy_source(self, 'yedek_v0.7.0', root=ROOT),
                 encoding='utf8',env={**os.environ,'PYTHONUTF8':'1'})
        old=json.loads(raw);s=decode(raw)
        self.assertEqual(old['schema_version'],2)
        self.assertEqual(s['schema_version'],3)
        self.assertEqual(s['legacy_goals'],old['goals'])
        self.assertEqual(json.loads(encode(s))['rng_state'],old['rng_state'])
        for domestic in (True,False):
            pid=next(pid for pid,z in old['fitness'].items() if is_domestic(P[pid])==domestic and z['potential']<17)
            z=state(s,P[pid])
            self.assertEqual(z['ability'],old['fitness'][pid]['ability'])
            delta=round(z['potential']*10)-round(old['fitness'][pid]['potential']*10)
            self.assertIn(delta,range(5,11) if domestic else [0])
            self.assertEqual(state(decode(encode(s)),P[pid])['potential'],z['potential'])
        k.advance(s)
        self.assertEqual(s['week'],3)

    def test_academy_and_stats(self):
        s=k.new('GALATASARAY',seed=9)
        fresh=k.new('GALATASARAY',seed=9)
        state_before=decode(encode(s))
        match=k.LiveMatch(s);match.finish();self.assertTrue(match.commit())
        k.advance(state_before)
        self.assertEqual(json.loads(encode(s)),json.loads(encode(state_before)))
        def totals(key):
            return sum(row[key] for clubs in s['season_stats'].values() for row in clubs.values())
        results=s['results'][0]
        self.assertEqual(totals('goals'),sum(r['x']+r['y'] for r in results))
        self.assertEqual(totals('assists'),sum(len(r['assists']) for r in results))
        self.assertEqual(totals('red'),sum(e[3]=='red' for r in results for e in r['play']))
        self.assertGreater(totals('yellow'),0)
        self.assertEqual(totals('saves'),sum(sum(r['saves']) for r in results))
        self.assertEqual(totals('motm'),9)
        self.assertEqual(totals('starts'),198)
        for _ in range(34):k.advance(s)
        self.assertTrue(s['history'][0]['player_stats'])
        self.assertFalse(s['season_stats'])
        self.assertTrue(s['generated'])
        for p in s['generated'].values():
            self.assertIsNone(player(fresh,p['id']))
            z=state(s,p)
            delta=round(z['potential']*10)-p['pa_base']
            self.assertIn(delta,range(1,6) if is_domestic(p) else [0])
        self.assertEqual(decode(encode(s))['generated'],s['generated'])

    def test_offer_controls(self):
        s=k.new('GALATASARAY',seed=55,models=False)
        p=next(p for p in roster(s['club'],2000,s) if p['pos']=='CM')
        buyer='FENERBAHÇE'
        terms=asking_terms(s,p,buyer,'Starter')
        self.assertTrue(add_offer(s,p,buyer,50000,terms))
        self.assertEqual(reject_all(s),1)
        self.assertFalse(add_offer(s,p,buyer,50500,terms))
        self.assertTrue(add_offer(s,p,buyer,75000,terms))
        self.assertTrue(set_sale_status(s,p['id'],'blocked'))
        self.assertFalse(add_offer(s,p,buyer,85000,terms))
        self.assertTrue(set_sale_status(s,p['id'],'listed'))
        self.assertTrue(add_offer(s,p,buyer,125000,terms))

    @unittest.skipUnless('--long' in sys.argv,'run with --long')
    def test_fifty_seasons(self):
        summaries=[];distributions=[]
        for club,seed in (('GENÇLERBİRLİĞİ',751),('GALATASARAY',752),('ERZURUMSPOR',753)):
            s=k.new(club,seed=seed)
            previous=0;retired=0;transfers=0
            for index in range(1,51):
                year=s['year']
                for _ in range(34):
                    self.assertTrue(k.advance(s))
                squads={team:roster(team,year,s) for team in TEAMS}
                self.assertGreaterEqual(min(map(len,squads.values())),11)
                self.assertEqual(sum(z['w']+z['d']+z['l'] for z in s['teams'].values()),18*34)
                self.assertEqual(sum(s['goals'].values()),sum(rows['gf'] for rows in s['teams'].values()))
                real=sum(p.get('kind')!='fictional' for ps in squads.values() for p in ps)
                gen=sum(map(len,squads.values()))-real
                groups=[sum(group(p)==role for ps in squads.values() for p in ps) for role in ('GK','D','M','F')]
                mins=[min(sum(group(p)==role for p in ps) for ps in squads.values()) for role in ('GK','D','M','F')]
                cash=[row['cash'] for row in s['finance'].values()]
                transaction=s['transfers'][transfers:]
                summaries.append([club,seed,index,year,real,gen,len(s['generated'])-previous,len(s['generated']),
                    len(s['retired'])-retired,len(s['retired']),min(map(len,squads.values())),max(map(len,squads.values())),
                    *groups,*mins,sum(cash),min(cash),sum(x<0 for x in cash),
                    sum(f['wages_paid'] for f in s['finance'].values()),len(transaction),
                    sum(row[2] not in TEAMS for row in transaction),sum(row[4] for row in transaction)])
                if index in (25,50):
                    buckets=defaultdict(list)
                    for ps in squads.values():
                        for p in ps:
                            z=state(s,p)
                            identifiers=sorted(citizenship_ids(p))
                            country='TR' if 'TR' in identifiers else identifiers[0]
                            buckets[(country,p.get('kind','real'))].append((z['ability']*10,z['potential']*10))
                    for (country,kind),values in sorted(buckets.items()):
                        ca,pa=zip(*values)
                        distributions.append([club,seed,index,country,kind,len(ca),
                            round(min(ca),2),round(sum(ca)/len(ca),2),round(max(ca),2),
                            round(min(pa),2),round(sum(pa)/len(pa),2),round(max(pa),2)])
                    print('CHECKPOINT',club,index,real,gen,mins,min(map(len,squads.values())),len(s['generated']),len(s['retired']),sum(cash),min(cash),flush=True)
                previous,retired,transfers=len(s['generated']),len(s['retired']),len(s['transfers'])
                if index in (1,25,50):
                    s=decode(encode(s))
                self.assertTrue(k.rollover(s))
            self.assertEqual(s['year'],2050)
        for name,columns,rows in [
            ('KARIYER_25_50_V075.csv','kulup tohum sezon yil gercek kurgu yeni_kurgu toplam_kurgu yeni_emekli toplam_emekli min_kadro max_kadro kaleci defans orta_saha forvet min_kaleci min_defans min_orta_saha min_forvet nakit min_nakit negatif_nakit maas transfer serbest bonservis',summaries),
            ('CA_PA_DAGILIMI_V075.csv','kulup tohum sezon ulke tur adet min_ca ort_ca max_ca min_pa ort_pa max_pa',distributions)]:
            if '--csv' not in sys.argv:
                continue
            with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as stream:
                out=csv.writer(stream);out.writerow(columns.split());out.writerows(rows)

if __name__=='__main__':
    unittest.main(argv=[a for a in sys.argv if a not in ('--long','--csv')],verbosity=2)
