"""Versioned calibration and assignment checks."""
from pathlib import Path
import itertools
import json
import random
import subprocess
import sys
import unittest

from kadro_atama import assign
from kariyer import LiveMatch, advance, new
from kayit import decode,encode
from mac import Match, select_slots
from oyuncu import attributes, state
from veritabani import player, roster


from test_fixtures import legacy_source

class CalibrationTests(unittest.TestCase):
    def test_assignment_avoids_consuming_only_centre_back(self):
        roles=['RB','CB']
        matrix={('versatile','RB'):9,('versatile','CB'):15,
                ('right','RB'):8,('right','CB'):1}
        result=assign(roles,[('right',True),('versatile',True)],0,lambda p,r:matrix[p,r])
        self.assertEqual(result,[('RB','right'),('CB','versatile')])

    def test_small_assignment_matches_exhaustive_search(self):
        rng=random.Random(793)
        roles=('A','B','C')
        players=[('0',False),('1',False),('2',True),('3',True)]
        for _ in range(25):
            matrix={(p,r):rng.choice((None,1,2,4,20)) for p,_ in players for r in roles}
            for cap in range(3):
                result=assign(roles,players,cap,lambda p,r:matrix[p,r])
                feasible=[]
                for permutation in itertools.product((None,*[p for p,_ in players]),repeat=3):
                    used=[p for p in permutation if p is not None]
                    if len(used)!=len(set(used)) or sum(p in ('0','1') for p in used)>cap:
                        continue
                    values=[matrix[p,r] for p,r in zip(permutation,roles) if p is not None]
                    if None not in values:
                        feasible.append((len(values),sum(values)))
                self.assertEqual((len(result),sum(matrix[p,r] for r,p in result)),max(feasible))

    def test_keeper_injury_cap_and_no_duplicate(self):
        s=new('GALATASARAY',seed=793)
        s['cap']=1
        team=s['club']
        from yerellestirme import is_domestic
        for p in roster(team,s['year'],s):
            if p['pos']=='GK' and is_domestic(p):
                state(s,p)['injury']=1
        slots=select_slots(s,team)
        selected=[player(s,pid) for _,pid in slots]
        self.assertEqual(slots[0][0],'GK')
        self.assertEqual(selected[0]['pos'],'GK')
        self.assertEqual(len(selected),len({p['id'] for p in selected}))
        self.assertEqual(sum(not is_domestic(p) for p in selected),1)
        for p in selected:self.assertFalse(state(s,p)['injury'])
        s['cap']=0
        self.assertNotIn('GK',[p for p,_ in select_slots(s,team)])

    def test_profile_and_match_roles(self):
        s=new('GALATASARAY',seed=793)
        jardel=player(s,'29663')
        taffarel=player(s,'29479')
        hagi=next(p for p in roster(s['club'],2000,s) if p['name']=='Hagi')
        self.assertTrue(attributes(s,jardel)['Finishing']>attributes(s,jardel)['Tackling'])
        self.assertTrue(attributes(s,taffarel)['Reflexes']>attributes(s,taffarel)['Finishing'])
        m=LiveMatch(s)
        for role,p,field,group in (('ST',jardel,'Finishing','F'),('GK',taffarel,'Reflexes','GK'),('AM',hagi,'Passing','M')):
            m.profiles[p['id']]=attributes(m.s,p)
            p0=m.strength([(role,p['id'])])[group]
            m.profiles[p['id']][field]+=1
            self.assertGreater(m.strength([(role,p['id'])])[group],p0)

    def test_both_legacy_modes(self):
        root=Path(__file__).resolve().parent
        script="""from kariyer import new,advance
from kayit import encode
s=new('GALATASARAY',seed=793)
print(encode(s))
advance(s)
print(encode(s))
"""
        for ver in ('v0.7.9.1','v0.7.9.2'):
            before,after=subprocess.check_output([sys.executable,'-B','-X','utf8','-c',script],
                  cwd=legacy_source(self, f'yedek_{ver}', root=root),encoding='utf8').splitlines()
            s=decode(before)
            advance(s)
            self.assertEqual(json.loads(encode(s)),json.loads(after))

    def test_new_rng(self):
        x=new('GALATASARAY',seed=793)
        y=decode(encode(x))
        advance(x)
        m=LiveMatch(y)
        m.finish()
        self.assertTrue(m.commit())
        self.assertEqual(json.loads(encode(x)),json.loads(encode(y)))


if __name__=='__main__':
    unittest.main()

