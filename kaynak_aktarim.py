"""Rebuild the research audit and verified score overlay from local sources."""
from collections import Counter,defaultdict
from contextlib import closing
from pathlib import Path,PurePosixPath
import csv
import json
import re
import sqlite3
import tempfile
import zipfile
from kaynak_okuyucu import WORLD,WorldReader,decoded,save_csv,tar,tff_detail,tff_round
from tarihsel import identity

ROOT=Path(__file__).parent
SOURCE=ROOT/'VERI_KAYNAKLARI'

def safe_tff(folder):
    path=SOURCE/'TFF'/'TFF_VERI.rar'
    names=decoded(tar('-tf',path)).splitlines()
    if any('..' in PurePosixPath(n).parts or n.startswith(('/',chr(92))) or ':' in n or chr(92) in n for n in names):
        raise ValueError('Unsafe TFF path')
    if any(line[:1] not in ('-','d') for line in decoded(tar('-tvf',path)).splitlines() if line):
        raise ValueError('Unexpected TFF member type')
    tar('-xf',path,'-C',folder)

def scores(base):
    checks=[];verified={};tff_ids=set();raw_appearances=0
    with tempfile.TemporaryDirectory() as temp:
        safe_tff(temp)
        folder=Path(temp)/'TFF_VERI'
        found={}
        for path in sorted(folder.glob('hafta_*.html')):
            week=int(path.stem.rsplit('_',1)[1])
            for pid,home,away,x,y in tff_round(path.read_text(encoding='utf-8')):
                if pid in found:raise ValueError('duplicate TFF fixture')
                found[pid]=(week,home,away,x,y)
        for row in base['matches']:
            pid=str(row['id']);week=row['week']
            path=folder/f'mac_{pid}.html'
            page=path.read_text(encoding='utf-8') if path.is_file() else ''
            ids=re.findall(r'_grdTakim[12]_rpt(?:Kadrolar|Yedekler)_[^"]+lnkOyuncu"[^>]+kisiId=(\d+)',page,re.I)
            raw_appearances+=len(ids)
            tff_ids.update(ids)
            detail=tff_detail(page)
            round_=found.get(pid)
            status='incelenmeli';result=('','')
            if round_ and round_[0]==week and tuple(map(identity,round_[1:3]))==tuple(map(identity,(row['home'],row['away']))):
                if detail==round_[3:]:
                    status='hafta ve maç detayı doğruladı';result=detail
                    verified[pid]={'score':list(detail),'week':week,'home':row['home'],'away':row['away'],
                                   'source':f'https://www.tff.org/Default.aspx?pageId=397&macId={pid}'}
                elif detail is None:
                    status='hafta doğruladı; detay okunamadı';result=round_[3:]
                    verified[pid]={'score':list(result),'week':week,'home':row['home'],'away':row['away'],
                                  'source':f'https://www.tff.org/Default.aspx?pageId=397&macId={pid}'}
            checks.append([pid,week,row['home'],row['away'],*row['score'],*result,
                           f'https://www.tff.org/Default.aspx?pageId=397&macId={pid}',status])
    save_csv(ROOT/'TARIHSEL_SKOR_DOGRULAMA.csv',('mac_id','hafta','ev_sahibi','deplasman','ham_ev_gol',
             'ham_deplasman_gol','dogrulanmis_ev_gol','dogrulanmis_deplasman_gol','kaynak','durum'),checks)
    (ROOT/'tarihsel_skorlar.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return tff_ids,raw_appearances,Counter(row[-1] for row in checks),verified

def identity_audit(base,historical,tff_ids):
    known=base['players']+historical
    matches={p['id']:[] for p in known}
    lookup=defaultdict(dict)
    for p in known:
        for name in (p['name'],p.get('full_name') or p['name']):
            lookup[(identity(name),p['dob'])][p['id']]=p
    book=SOURCE/'CM'/'cm0102-reborn-main.zip'
    totals=[];raw_total=usable_total=0
    with tempfile.TemporaryDirectory() as directory,zipfile.ZipFile(book) as z,closing(sqlite3.connect(Path(directory)/'audit.sqlite')) as db:
        db.execute('CREATE TABLE person(name TEXT, born TEXT, nation TEXT, PRIMARY KEY(name,born,nation)) WITHOUT ROWID')
        variants=[n for n in z.namelist() if WORLD.search(n)]
        for n in sorted(variants):
            data=json.loads(z.read(n))
            if 'players' not in data:
                continue
            reader=WorldReader(data)
            raw_total+=len(data['players']);usable=0
            def records():
                nonlocal usable
                for (name,dob,nat),ref,full in reader.identities():
                    usable+=1
                    for pid,p in lookup.get((name,dob),{}).items():
                        country={item['country_id'] for item in p.get('citizenships',[])} or {p.get('nation')}
                        if 'TR' in country and nat not in ('TUR','TR'):
                            matches[pid].append((Path(n).stem,'ülke kontrolü'))
                        else:
                            matches[pid].append((Path(n).stem,'ad ve doğum eşleşmesi'))
                    yield name,dob,nat
            db.executemany('INSERT OR IGNORE INTO person VALUES (?,?,?)',records())
            totals.append([Path(n).name,data.get('season'),len(data['players']),usable])
            usable_total+=usable
        unique=db.execute('SELECT COUNT(*) FROM person').fetchone()[0]
    researched=defaultdict(list)
    research=SOURCE/'Oyuncu_arastirmalari'
    for path in sorted(research.glob('*.csv')):
        with path.open(encoding='utf-8-sig',newline='') as stream:
            for row in csv.DictReader(stream):
                researched[row.get('ID','')].append(path.name)
    match_rows=[[p['id'],p['name'],p.get('dob'),str(p['id']) in tff_ids,
                 '; '.join(f'{source}: {decision}' for source,decision in sorted(set(matches[p['id']]))),
                 '; '.join(researched[p['id']]),'oyun kimliği korundu'] for p in known]
    missing=sorted(tff_ids-{str(p['id']) for p in known})
    for pid in missing:
        match_rows.append([pid,'','',True,'','','TFF maç kadrosu; kimlik alanı eksik, oyuna alınmadı'])
    save_csv(ROOT/'FUTBOLCU_ESLESTIRME_RAPORU.csv',
        ('oyun_veya_tff_id','ad','dogum','tff_kadro','cm_karsilastirma','onceki_arastirma','karar'),match_rows)
    return totals,raw_total,usable_total,unique,len(missing),sum(bool(v) for v in matches.values())

def main():
    base=json.loads((ROOT/'data.json').read_text(encoding='utf8'))
    historical=json.loads((ROOT/'tarihsel_girisler.json').read_text(encoding='utf8'))
    ids, appearances,status,verified=scores(base)
    totals,raw,usable,unique,missing,matched=identity_audit(base,historical,ids)
    save_csv(ROOT/'TARIHSEL_OYUNCU_GIRIS_RAPORU.csv',
      ('id','ad','dogum','giris','kaynak','guven','kaynak_kulubu','karar'),
      [[p['id'],p['name'],p['dob'],p['available_from'],p['source'],p.get('confidence','TFF kimlik ve lisans'),
        p.get('facts',{}).get('club_at_threshold',''),'v0.7.6' if 'facts' in p else 'v0.7.5'] for p in historical])
    pts=Counter();goals=Counter()
    for r in verified.values():
        x,y=r['score'];goals['home']+=x;goals['away']+=y
        pts[r['home']]+=3 if x>y else int(x==y)
        pts[r['away']]+=3 if y>x else int(x==y)
    print(json.dumps(dict(totals=totals,raw=raw,usable=usable,unique=unique,tff_appearances=appearances,tff_ids=len(ids),
        tff_missing=missing,aligned=matched,scores=status,home=goals['home'],away=goals['away'],
        standings=pts.most_common(4)),ensure_ascii=False))

if __name__=='__main__':
    main()
