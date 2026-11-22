"""Reviewable historical import. Commercial source files are never bundled."""
import argparse
import csv
from datetime import date
import json
from pathlib import Path
import unicodedata
from yerellestirme import COUNTRIES

def identity(name):
    normalized = unicodedata.normalize('NFKD', name.casefold().replace('ı','i'))
    return ''.join(c for c in normalized if c.isalnum())

def reconcile(existing, candidates):
    ids={p['id'] for p in existing}
    people={(identity(name),p.get('dob')):p for p in existing
            for name in (p['name'],p.get('full_name',p['name']))}
    by_name={name for name,_ in people}
    accepted, review=[],[]
    for row in candidates:
        try:
            pid=row['id']; name=identity(row['name']); dob=date.fromisoformat(row['dob'])
            day=date.fromisoformat(row['available_from']); nation=row['nation']
            estimate=row['estimates']; ca,pa=estimate['ca'],estimate['pa']
            if not isinstance(pid,str) or not pid.isdecimal() or not name or nation not in COUNTRIES or nation=='ZZ':
                raise ValueError('incomplete identity')
            if dob>=day or day.year<2000 or not row['source'].startswith('https://'):
                raise ValueError('invalid dated source')
            if estimate['position'] not in ('GK','D','M','F','CB','RB','LB','CM','DM','AM','RM','LM','RW','LW','CF','ST','SS'):
                raise ValueError('unknown position')
            if not 40<=ca<=pa<=200:
                raise ValueError('invalid separate estimate')
            if pid in ids:
                raise ValueError('duplicate source identifier')
            if (name,row['dob']) in people:
                match=people[(name,row['dob'])]
                recorded={entry['country_id'] for entry in match.get('citizenships',[])}
                if not recorded and match.get('nation') in COUNTRIES:
                    recorded={match['nation']}
                raise ValueError('duplicate identity / nationality conflicts' if recorded and nation not in recorded
                                 else 'duplicate identity')
            if name in by_name:
                raise ValueError('same name / alternate identity requires review')
        except (KeyError,TypeError,ValueError,AttributeError) as exc:
            review.append({'row':row,'reason':str(exc)})
            continue
        ids.add(pid);people[(name,row['dob'])]=row;by_name.add(name)
        accepted.append(row)
    return accepted,review

def load_entries(path, originals):
    rows=json.loads(path.read_text(encoding='utf8'))
    accepted,review=reconcile(originals,rows)
    if review:
        raise ValueError(f'Historical intake needs review: {review}')
    return {row['id']:dict(id=row['id'],name=row['name'],full_name=row['name'],dob=row['dob'],
                nation=row['nation'],citizenships=[dict(country_id=row['nation'],valid_from=None,raw=row['nation'])],
                pos=row['estimates']['position'],rating=row['estimates']['ca']/10,
                pa_base=row['estimates']['pa'],kind='real',number=0,source=row['source'],
                available_from=row['available_from'],facts=row.get('facts',{}),
                source_confidence=row.get('confidence','primary-identity-and-registration')) for row in accepted}

def main():
    parser=argparse.ArgumentParser(description='Review an authorized normalized CSV export (no proprietary binary reader).')
    parser.add_argument('csv',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    base=Path(__file__).parent
    originals=json.loads((base/'data.json').read_text(encoding='utf8'))['players']
    originals += json.loads((base/'tarihsel_girisler.json').read_text(encoding='utf8'))
    with args.csv.open(encoding='utf-8-sig',newline='') as stream:
        candidates=[]
        for row in csv.DictReader(stream):
            try:
                row['estimates']={'position':row.pop('position'),'ca':int(row.pop('ca')),'pa':int(row.pop('pa'))}
            except (TypeError,ValueError,KeyError):
                row['estimates']={}
            candidates.append(row)
    accepted,review=reconcile(originals,candidates)
    with args.output.open('x',encoding='utf8') as stream:
        json.dump({'accepted':accepted,'review':review},stream,ensure_ascii=False,indent=2)

if __name__=='__main__':
    main()
