"""World regression and optional 25-season diagnostics."""
from collections import Counter
import copy
import csv
import os
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest
from unittest.mock import patch
from unittest.mock import patch

import kariyer as k
from dunya import age_world, group, recruit
from istatistik import SHOT_EVENTS
from finans import payroll
from kayit import SaveError, decode, encode
from menajer import accept_job, evaluate, resign
from oyuncu import age_at, develop, state
from sozlesme import asking_terms, expire, player_accepts, renew
from transfer import add_offer, answer_offer, asking_fee, deal, selling_ready
from veritabani import INTAKE, P, TEAMS, available, roster, player
from yarisma import standings

ROOT=Path(__file__).resolve().parent
GEN=next(t for t in TEAMS if t.startswith('GEN'))
EZ='ERZURUMSPOR'
GS='GALATASARAY'

def generous(s,p,team):
    terms=asking_terms(s,p,team,'Starter')
    terms['wage']=round(terms['wage']*1.34)
    return terms

from test_fixtures import legacy_source

class WorldTests(unittest.TestCase):
    def test_contract_and_budgets(self):
        s=k.new(GS,seed=1,models=False)
        p=next(p for p in roster(EZ,2000,s) if p['pos']!='GK')
        pid=p['id']
        state(s,p)['contract']=2000
        expire(s)
        self.assertNotIn(pid,s['owners'])
        self.assertTrue(available(s,p))
        self.assertEqual(asking_fee(s,p),0)
        terms=generous(s,p,GS)
        self.assertEqual(deal(s,pid,GS,1000,**terms),(False,'fee'))
        low=dict(terms,wage=100,signing=0)
        self.assertEqual(deal(s,pid,GS,0,**low),(False,'player'))
        ledger=s['finance'][GS]
        old=ledger.copy()
        wage_cap=ledger['wage_budget']
        ledger['wage_budget']=payroll(s,GS)
        self.assertEqual(deal(s,pid,GS,0,**terms),(False,'budget'))
        ledger['wage_budget']=wage_cap
        self.assertEqual(deal(s,pid,GS,0,**terms),(True,'accepted'))
        self.assertEqual(s['transfers'][-1][-1],0)
        self.assertEqual(ledger['cash'],old['cash']-terms['signing'])
        self.assertEqual(ledger['transfer_budget'],old['transfer_budget']-terms['signing'])
        self.assertEqual(ledger['wage_budget'],old['wage_budget'])
        self.assertTrue(renew(s,pid,**dict(terms,years=2))[0])
        self.assertEqual(state(s,p)['contract'],2002)

    def test_reputation_and_role(self):
        s=k.new(GS,seed=1)
        p=max((p for p in roster(GS,2000,s) if age_at(p,2000,1)<34),key=lambda p:p['rating'])
        z=state(s,p)
        z['minutes']=1800
        s['club_reputation'][GS]=80
        ask=asking_terms(s,p,GS,'Starter')
        wage=ask['wage']
        self.assertTrue(player_accepts(s,p,GS,2,wage,0,'Starter'))
        self.assertFalse(player_accepts(s,p,GS,2,wage,0,'Rotation'))
        s['club_reputation'][GS]=35
        self.assertFalse(player_accepts(s,p,GS,2,wage,0,'Starter'))

    def test_retirement_development_and_intake(self):
        s=k.new(GS,seed=1)
        p=next(p for p in P.values() if p['id'] not in s['owners'] and 18<=age_at(p,2001,1)<=21)
        pid=p['id']
        with patch.dict(INTAKE,{pid:{'available_from':'2003-08-08','source':'fixture'}}):
            s.update(year=2003,week=1)
            self.assertFalse(available(s,p))
            s['week']=2
            self.assertTrue(available(s,p))
        s.update(year=2000,week=1)
        previous=state(s,p)['ability']
        age_world(s,random.Random(1))
        self.assertNotEqual(state(s,p)['ability'],previous)
        a,b=copy.deepcopy(s),copy.deepcopy(s)
        state(a,p)['training_weeks']=30
        develop(a,p,random.Random(22),minutes=2400)
        develop(b,p,random.Random(22),minutes=100)
        self.assertGreater(state(a,p)['ability'],state(b,p)['ability'])
        self.assertLess(state(a,p)['ability'],state(a,p)['potential'])
        old=max((P[pid] for pid in s['owners']),key=lambda p:age_at(p,2000,1))
        s['year']=2025
        age_world(s,random.Random(5))
        self.assertIn(old['id'],s['retired'])
        self.assertNotIn(old['id'],s['owners'])
        self.assertFalse(available(s,old))

    def test_ai_bids_and_counter(self):
        s=k.new(GS,seed=9,models=False)
        recruit(s)
        self.assertTrue(any(seller in TEAMS and buyer!=GS and seller!=GS
                            for _,_,seller,buyer,_ in s['transfers']))
        self.assertTrue(s['offers'])
        index=0
        offer=s['offers'][index]
        self.assertEqual(offer['seller'],GS)
        self.assertEqual(answer_offer(s,index,'counter',offer['fee']*2),(False,'buyer'))
        self.assertTrue(answer_offer(s,index,'counter',round(offer['fee']*1.01))[0])
        self.assertEqual(offer['status'],'accepted')
        self.assertEqual(s['owners'][offer['pid']],offer['buyer'])
        self.assertFalse(answer_offer(s,index,'accept')[0])

    def test_manager_jobs(self):
        s=k.new(GS,seed=1,models=False)
        last=[t for t in TEAMS if t!=GS]+[GS]
        old=s['manager_rep']
        evaluate(s,last)
        self.assertLess(s['manager_rep'],old)
        evaluate(s,last)
        self.assertFalse(s['employed'])
        self.assertTrue(s['job_offers'])
        team=s['job_offers'][0]
        self.assertTrue(accept_job(s,team))
        self.assertTrue(s['employed'])
        self.assertEqual(s['club'],team)
        self.assertTrue(resign(s))
        self.assertFalse(s['employed'])
        k.advance(s)
        self.assertEqual(s['week'],2)
        self.assertEqual(k.career(s)[-1]['n'],0)
        self.assertFalse(accept_job(s,s['job_offers'][0]))

    def test_match_event_totals(self):
        s=k.new(GEN,seed=17)
        fast=decode(encode(s))
        live=k.LiveMatch(s)
        for _ in range(18):live.step()
        self.assertTrue(live.commit())
        k.advance(fast)
        self.assertEqual(json.loads(encode(s)),json.loads(encode(fast)))
        for m in s['results'][-1]:
            for side in (0,1):
                shots=[row for row in m['play'] if row[1]==side and row[3] in SHOT_EVENTS]
                self.assertEqual(m['shots'][side],len(shots))
                self.assertEqual(m['on_target'][side],sum(row[3]!='wide' for row in shots))
                self.assertEqual(m['saves'][1-side],sum(row[3]=='saved' for row in shots))
                self.assertEqual((m['x'],m['y'])[side],sum(row[3]=='goal' for row in shots))
            self.assertEqual(m['ratings'].keys(),m['minutes'].keys())
        invalid=json.loads(encode(s))
        invalid['results'][0][0]['on_target'][0]+=1
        with self.assertRaises(SaveError):decode(json.dumps(invalid))

    def test_v060_original_save(self):
        raw=subprocess.check_output([sys.executable,'-B','-c',
             "import kariyer as k; from kayit import encode; s=k.new('GALATASARAY',seed=8); k.advance(s); print(encode(s))"],
             cwd=legacy_source(self, 'yedek_v0.6.0', root=ROOT),encoding='utf8',env={**os.environ,'PYTHONUTF8':'1'})
        old=json.loads(raw)
        upgraded=decode(raw)
        self.assertEqual(old['schema_version'],1)
        self.assertEqual(upgraded['schema_version'],3)
        self.assertEqual(old['teams'],upgraded['teams'])
        self.assertEqual(old['results'],upgraded['results'])
        self.assertEqual(old['rng_state'],json.loads(encode(upgraded))['rng_state'])
        k.advance(upgraded)
        self.assertEqual(upgraded['week'],3)
        self.assertIn('play',upgraded['results'][-1][0])

    @unittest.skipUnless('--gui' in sys.argv,'use --gui')
    def test_world_ui(self):
        import tkinter as tk
        from arayuz import UI
        root=tk.Tk()
        root.withdraw()
        try:
            ui=UI(root)
            s=k.new(GS,seed=4)
            ui.begin(s)
            ui.jobs_page()
            ui.offers_page()
            ui.market()
            ui.squad()
            ui.negotiate(roster(GS,2000,s)[0],True)
            root.update()
            for child in root.winfo_children():
                if isinstance(child,tk.Toplevel):
                    child.destroy()
            ui.autosave=lambda:None
            ui.s['match_mode']='quick'
            with patch('arayuz.messagebox.askyesno',return_value=True):
                ui.next()
            ui.last_report()
            root.update()
            self.assertTrue(any(isinstance(child,tk.Toplevel) and child.title()=='Maç raporu'
                                for child in root.winfo_children()))
        finally:
            root.destroy()

    def test_data_unchanged(self):
        self.assertEqual(len(P),606)
        self.assertEqual(len(TEAMS),18)

    def test_dataset_matches_archive(self):
        self.assertEqual((ROOT/'data.json').read_bytes(),(legacy_source(self, 'yedek_v0.6.0', root=ROOT)/'data.json').read_bytes())

    @unittest.skipUnless('--long' in sys.argv,'use --long')
    def test_twenty_five_seasons(self):
        export=[]
        club_export=[]
        for initial,seed in ((GEN,701),(GS,702),(EZ,703)):
            s=k.new(initial,seed=seed)
            seasons=[]
            for year in range(2000,2025):
                if not s['employed'] and s['job_offers']:
                    self.assertTrue(accept_job(s,s['job_offers'][0]))
                club=s['club']
                if s['employed']:
                    for p in roster(club,year,s)[:]:
                        if state(s,p)['contract']<=year+1:
                            renew(s,p['id'],**generous(s,p,club))
                    free=sorted((p for p in P.values() if available(s,p)),
                                key=lambda p:(-state(s,p)['ability'],p['id']))
                    for p in free[:6]:
                        if len(roster(club,year,s))>=19:break
                        deal(s,p['id'],club,0,**generous(s,p,club))
                for week in range(1,35):
                    self.assertEqual(s['week'],week)
                    self.assertTrue(k.advance(s))
                    self.assertEqual(len(s['results'][-1]),9)
                    self.assertTrue(all(m['x']+m['y']==len(m['events']) for m in s['results'][-1]))
                self.assertEqual(s['year'],year)
                teams=s['teams'].values()
                self.assertTrue(all(z['w']+z['d']+z['l']==34 for z in teams))
                self.assertEqual(sum(z['gf'] for z in teams),sum(s['goals'].values()))
                sizes=[len(roster(t,year,s)) for t in TEAMS]
                ages=[age_at(player(s,pid),year,34) for pid in s['owners']]
                age_bands=[sum(a<20 for a in ages),*[sum(lo<=a<lo+5 for a in ages) for lo in (20,25,30,35)],
                           sum(a>=40 for a in ages)]
                cash=[s['finance'][t]['cash'] for t in TEAMS]
                wages=sum(z['wages_paid'] for z in s['finance'].values())
                without_gk=sum(not any(p['pos']=='GK' for p in roster(t,year,s)) for t in TEAMS)
                transfers=[row for row in s['transfers'] if row[0]==year]
                record=[year,club,standings(s).index(club)+1,sum(sizes),min(sizes),max(sizes),
                        sum(n<11 for n in sizes),without_gk,age_bands,len(s['retired']),len(transfers),
                        sum(row[2] not in TEAMS for row in transfers),wages,sum(cash),
                        sum(c<0 for c in cash),min(cash),sum(z['operating_paid'] for z in s['finance'].values())]
                seasons.append(record)
                export.append([initial,seed,*record[:8],*age_bands,*record[9:]])
                for team in TEAMS:
                    club_squad=roster(team,year,s)
                    club_ages=[age_at(p,year,34) for p in club_squad]
                    ledger=s['finance'][team]
                    club_export.append([initial,seed,year,team,len(club_squad),sum(p['pos']=='GK' for p in club_squad),
                        round(sum(club_ages)/len(club_ages),2) if club_ages else '',
                        sum(row[0]==year and row[1]==team for row in s['retired'].values()),
                        sum(row[3]==team for row in transfers),sum(row[2]==team for row in transfers),
                        *(ledger[key] for key in ('cash','transfer_budget','wage_budget','wages_paid','operating_paid',
                                                 'fees_paid','fees_received','signing_paid'))])
                s=decode(encode(s))
                self.assertTrue(k.advance(s))
            self.assertEqual((s['year'],s['week'],len(s['world_history'])),(2025,1,25))
            print('WORLD_JSON '+json.dumps(dict(initial=initial,seed=seed,seasons=seasons,jobs=s['jobs'],
                 retired=len(s['retired']),expired=sum(row[1]=='expired' for row in s['contract_events'])),
                 ensure_ascii=False),flush=True)
        if '--csv' in sys.argv:
            with (ROOT/'KARIYER_25_SEZON.csv').open('w',encoding='utf-8-sig',newline='') as stream:
                out=csv.writer(stream)
                out.writerow(['baslangic_kulubu','tohum','yil','yonetilen_kulup','sira',
                              'aktif_oyuncu','en_kucuk_kadro','en_buyuk_kadro','11_alti_kulup',
                              'kalecisiz_kulup','yas_20_alti','yas_20_24','yas_25_29','yas_30_34',
                              'yas_35_39','yas_40_ustu','biriken_emekli','transfer','bonservissiz',
                              'lig_maas_gideri','lig_nakdi','eksi_nakitli_kulup','en_dusuk_nakit','isletme_gideri'])
                out.writerows(export)
            with (ROOT/'KULUP_25_SEZON.csv').open('w',encoding='utf-8-sig',newline='') as stream:
                out=csv.writer(stream)
                out.writerow(['baslangic_kulubu','tohum','yil','kulup','kadro','kaleci','ortalama_yas',
                              'sezon_basinda_emeklilik','gelen_transfer','giden_transfer','nakit','transfer_butcesi',
                              'haftalik_maas_butcesi','maas_gideri','isletme_gideri','bonservis_odenen',
                              'bonservis_alinan','imza_parasi'])
                out.writerows(club_export)

if __name__=='__main__':
    unittest.main(argv=[arg for arg in sys.argv if arg not in ('--long','--csv','--gui')],verbosity=2)
