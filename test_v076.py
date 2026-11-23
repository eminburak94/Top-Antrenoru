"""Currency, accounting and long-career diagnostics for v0.7.6."""
from collections import Counter
import csv
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
from statistics import mean,median
import os,subprocess,sys,time,unittest

from finans import FLOW,operating,service
from kariyer import new,advance,rollover
from kayit import encode,decode
from para import CURRENCIES,rate,edit_value,from_display
from dunya import group
from oyuncu import state,age_at
from veritabani import D,HISTORICAL,TEAMS,roster,available
from yarisma import standings

ROOT=Path(__file__).parent
REVENUE=('tickets','season_tickets','broadcast','sponsors','commercial','prize','fees_received')
EXPENSE=('wages_paid','staff','academy','maintenance','bonuses','investment','interest','fees_paid','signing_paid')

def ram():
    if sys.platform!='win32':
        return 0,0
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('Faults',wintypes.DWORD)]+[
            (name,ctypes.c_size_t) for name in ('peak','working','pp','p','np','n','page','peak_page')]
    c=Counters();c.cb=ctypes.sizeof(c)
    kernel=ctypes.WinDLL('kernel32');kernel.GetCurrentProcess.restype=wintypes.HANDLE
    read=ctypes.WinDLL('psapi').GetProcessMemoryInfo
    read.argtypes=(wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD)
    if not read(kernel.GetCurrentProcess(),ctypes.byref(c),c.cb):
        return 0,0
    return c.working,c.peak

def report(name,head,rows):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as stream:
        out=csv.writer(stream);out.writerow(head.split());out.writerows(rows)

from test_fixtures import legacy_source

class Economy(unittest.TestCase):
    def test_currency_invariant(self):
        base=new('GALATASARAY',seed=761)
        alternatives=[decode(encode(base)) for _ in CURRENCIES]
        for s,unit in zip(alternatives,CURRENCIES):
            s['currency']=unit
            for v in (0,1,2677,4000000,-12437):
                self.assertEqual(from_display(s,edit_value(s,v)),v)
            advance(s)
        normalized=[json.loads(encode(s)) for s in alternatives]
        for s in normalized:s.pop('currency')
        self.assertTrue(all(s==normalized[0] for s in normalized))

    def test_turkish_change(self):
        s=new('GALATASARAY',seed=1);s.update(year=2004,week=22,currency='TRY')
        factor,label=rate(s)
        self.assertEqual(label,'TRL')
        s['week']=23
        self.assertEqual(rate(s)[1],'YTL')
        self.assertGreater(factor,100000)
        s.update(year=2009,week=1)
        self.assertEqual(rate(s)[1],'TRY')

    def test_financial_ledger(self):
        s=new('ERZURUMSPOR',seed=762)
        team=s['club'];ledger=s['finance'][team]
        before=ledger['cash']
        operating(s,team)
        self.assertEqual(ledger['cash']-before,sum(ledger[k] for k in REVENUE)-sum(ledger[k] for k in EXPENSE))
        ledger['cash']=-120000
        service(s,team)
        self.assertEqual(ledger['cash'],0)
        self.assertEqual(ledger['debt'],120000)
        ledger['cash']=900000
        service(s,team)
        self.assertEqual(ledger['debt'],0)
        self.assertEqual(ledger['borrowed'],ledger['repaid'])

    def test_preserved_database_and_scores(self):
        self.assertEqual(len(D['players'])+len(HISTORICAL),619)
        scores=json.loads((ROOT/'tarihsel_skorlar.json').read_text(encoding='utf8'))
        self.assertEqual(scores['20642']['score'],[0,4])
        self.assertEqual(len(scores),306)
        self.assertTrue(all(k in HISTORICAL for k in ('673538','1723820')))

    def test_dataset_matches_archive(self):
        self.assertEqual((ROOT/'data.json').read_bytes(),(legacy_source(self, 'yedek_v0.7.5', root=ROOT)/'data.json').read_bytes())

    def test_v075_saved_career(self):
        code=("from kariyer import new,advance; from kayit import encode; "
              "s=new('GALATASARAY',seed=76); [advance(s) for _ in range(36)]; print(encode(s))")
        raw=subprocess.check_output([sys.executable,'-B','-c',code],cwd=legacy_source(self, 'yedek_v0.7.5', root=ROOT),
                                    encoding='utf8',env={**os.environ,'PYTHONUTF8':'1'})
        old=json.loads(raw);current=decode(raw)
        for field in ('rng_state','owners','generated','results','season_stats','year','week'):
            self.assertEqual(json.loads(encode(current))[field],old[field])
        self.assertTrue(all(current['finance'][t]['cash']==old['finance'][t]['cash']
                            and current['finance'][t]['debt']==0 for t in TEAMS))
        self.assertEqual(current['currency'],'USD')
        self.assertTrue(advance(current))
        arda=HISTORICAL['1723820']
        current.update(year=2020,week=22)
        self.assertFalse(available(current,arda))
        current['week']=25
        self.assertTrue(available(current,arda))

    @unittest.skipUnless('--long' in sys.argv,'use --long')
    def test_careers(self):
        seasons=[];clubs=[];distributions=[]
        for start,seed,length in (('GENÇLERBİRLİĞİ',751,50),('GALATASARAY',752,100),('ERZURUMSPOR',753,50)):
            t=time.perf_counter();s=new(start,seed=seed)
            startup=time.perf_counter()-t
            finance_open={team:s['finance'][team]['cash'] for team in TEAMS}
            known=set(); transfer_offset=0; growth={}
            for index in range(1,length+1):
                tick=time.perf_counter()
                year=s['year']
                for _ in range(34):self.assertTrue(advance(s))
                active=[p for team in TEAMS for p in roster(team,year,s)]
                real={p['id'] for p in active if p.get('kind')!='fictional'}
                n_gen=len(active)-len(real)
                youth={p['id']:state(s,p)['ability'] for p in active if isinstance(age_at(p,year,34),int)
                        and age_at(p,year,34)<24}
                gains=[(val-growth[pid])*10 for pid,val in youth.items() if pid in growth]
                growth=youth
                sizes=[len(roster(team,year,s)) for team in TEAMS]
                minima=[min(sum(group(p)==role for p in roster(team,year,s)) for team in TEAMS)
                        for role in ('GK','D','M','F')]
                self.assertGreaterEqual(min(sizes),11)
                self.assertEqual(sum(sum(z[x] for x in ('w','d','l')) for z in s['teams'].values()),612)
                goals=sum(s['goals'].values())
                self.assertEqual(goals,sum(z['gf'] for z in s['teams'].values()))
                ranking=standings(s)
                tx=s['transfers'][transfer_offset:];transfer_offset=len(s['transfers'])
                fees=[r[4] for r in tx if r[4]]
                pre=sum(ledger['cash'] for ledger in s['finance'].values())
                payload=encode(s); save_bytes=len(payload.encode('utf8'))
                ram_now,peak=ram()
                if index in (10,25,50,100):
                    s=decode(payload)
                    buckets={}
                    for p in active:
                        value=state(s,p)
                        nation=sorted(c['country_id'] for c in p['citizenships'])
                        bucket=(('TR' if 'TR' in nation else nation[0]) if nation else 'ZZ',p.get('kind','real'))
                        buckets.setdefault(bucket,[]).append((value['ability']*10,value['potential']*10))
                    for (nation,kind),measure in sorted(buckets.items()):
                        ca,pa=zip(*measure)
                        distributions.append([start,index,nation,kind,len(measure),round(min(ca),2),round(mean(ca),2),
                            round(max(ca),2),round(min(pa),2),round(mean(pa),2),round(max(pa),2)])
                young_entered=len((real-known)&HISTORICAL.keys())
                known.update(real)
                retired=len(s['retired']);created=len(s['generated'])
                self.assertTrue(rollover(s))
                audit=s['world_history'][-1]['finance']
                post=sum(row['cash'] for row in audit.values())
                for team,ledger in audit.items():
                    revenue=sum(ledger[k] for k in REVENUE)
                    expenses=sum(ledger[k] for k in EXPENSE)
                    self.assertEqual(ledger['cash'],finance_open[team]+revenue-expenses+ledger['borrowed']-ledger['repaid'])
                    clubs.append([start,index,team,ledger['cash'],ledger['debt'],revenue,expenses,
                                  *[ledger[k] for k in (*REVENUE,*EXPENSE,'borrowed','repaid')]])
                finance_open={team:row['cash'] for team,row in audit.items()}
                seasons.append([start,seed,index,year,len(real),n_gen,young_entered,created,retired,min(sizes),max(sizes),
                    *minima,ranking[0],s['history'][-1]['teams'][ranking[0]]['p'],goals,round(goals/306,4),
                    pre,post,sum(row['debt'] for row in audit.values()),
                    sum(sum(row[k] for k in REVENUE) for row in audit.values()),
                    sum(sum(row[k] for k in EXPENSE) for row in audit.values()),len(tx),len(fees),
                    int(median(fees)) if fees else 0,len(gains),round(mean(gains),3) if gains else '',
                    save_bytes,ram_now,peak,round(time.perf_counter()-tick,3),round(startup,4)])
                if index in (10,25,50,100):
                    print('CHECKPOINT',start,index,pre,post,len(real),n_gen,min(sizes),save_bytes,peak,flush=True)
            self.assertEqual(s['year'],2000+length)
        report('KARIYER_10_25_50_100_V076.csv','club seed season year real regen new_historical produced retired min_roster max_roster min_gk min_def min_mid min_fwd champion points goals goals_per_match pre_prize_cash closing_cash debt revenue expense transfers paid median_fee youth_sample youth_mean_ca_change save_bytes ram_bytes peak_bytes season_seconds new_game_seconds',seasons)
        report('KULUP_EKONOMI_V076.csv','club season team cash debt revenue expense '+' '.join((*REVENUE,*EXPENSE,'borrowed','repaid')),clubs)
        report('CA_PA_V076.csv','club season nation kind count min_ca avg_ca max_ca min_pa avg_pa max_pa',distributions)

if __name__=='__main__':
    unittest.main(argv=[arg for arg in sys.argv if arg!='--long'],verbosity=2)
