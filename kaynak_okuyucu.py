"""Read-only inventory and validated parsers for local research archives."""
import argparse
import csv
import gzip
import io
import html
import json
import re
from collections import Counter
from pathlib import Path
import subprocess
import tempfile
import zipfile
from datetime import date
from tarihsel import identity

ARCHIVES={'.zip','.rar','.7z','.tar','.tgz'}
WORLD=re.compile(r'/public/data/world[^/]*\.json$')
LIMIT=180_000_000

def tar(*args):
    return subprocess.check_output(['tar',*map(str,args)],stderr=subprocess.PIPE)

def decoded(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('cp1254')

def classified(name):
    ext=Path(name).suffix.lower()
    return {
        '.dat':'özel ikili DAT', '.dbi':'özel ikili DBI', '.db':'ikili DB', '.lnc':'yapılandırma metni',
        '.xml':'XML', '.json':'JSON', '.csv':'CSV', '.html':'HTML', '.txt':'metin', '.cfg':'yapılandırma metni',
        '.png':'görsel', '.webp':'görsel', '.m4a':'ses', '.tac':'taktik biçimi'
    }.get(ext,ext[1:] or 'uzantısız')

def inspect(root):
    rows=[]
    def add(name,depth,fmt,status,length=None,records=None,version='',note=''):
        rows.append([name,depth,fmt,status,'' if length is None else length,
                     '' if records is None else records,version,note])
    def archive(path,label,depth):
        try:
            extension=path.suffix.lower()
            if depth>8:
                add(label,depth,extension,'depth-limit')
                return
            if extension=='.zip':
                with zipfile.ZipFile(path) as z:
                    files=[entry for entry in z.infolist() if not entry.is_dir()]
                    add(label,depth,'ZIP','listed',path.stat().st_size,len(files))
                    members(path,label,depth,[(i.filename,i.file_size) for i in files],z.read)
            else:
                entries=[n for n in decoded(tar('-tf',path)).splitlines() if n]
                add(label,depth,extension[1:].upper(),'listed',path.stat().st_size,len(entries))
                members(path,label,depth,[(name,None) for name in entries],lambda name:tar('-xOf',path,name))
        except (OSError,ValueError,RuntimeError,subprocess.SubprocessError,zipfile.BadZipFile) as exc:
            add(label,depth,path.suffix,'error',note=str(exc))

    def members(path,label,depth,entries,read):
        for name,size in entries:
            full=label+'!'+name
            suffix=Path(name).suffix.lower()
            if suffix in ARCHIVES:
                try:
                    if size is not None and size>LIMIT:
                        raise ValueError('archive member over safety limit')
                    if size is None:
                        with tempfile.TemporaryDirectory() as folder:
                            nested=Path(folder)/('nested'+suffix)
                            with nested.open('wb') as stream:
                                proc=subprocess.Popen(['tar','-xOf',str(path),name],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
                                with proc:
                                    length=0
                                    while chunk:=proc.stdout.read(65536):
                                        length+=len(chunk)
                                        if length>LIMIT:
                                            proc.kill()
                                            raise ValueError('archive member over safety limit')
                                        stream.write(chunk)
                                    if proc.wait():
                                        raise ValueError('cannot read member')
                            archive(nested,full,depth+1)
                    else:
                        with tempfile.TemporaryDirectory() as folder:
                            nested=Path(folder)/('nested'+suffix)
                            nested.write_bytes(read(name))
                            archive(nested,full,depth+1)
                except (ValueError,OSError,RuntimeError,zipfile.BadZipFile) as exc:
                    add(full,depth+1,classified(name),'error',note=str(exc))
            elif suffix=='.gz':
                try:
                    length=0
                    with gzip.GzipFile(fileobj=io.BytesIO(read(name))) as stream:
                        while chunk:=stream.read(65536):
                            length+=len(chunk)
                            if length>LIMIT:
                                raise ValueError('expanded gzip exceeds safety limit')
                    add(full,depth+1,'GZIP','gzip-read',size,note=f'{length} expanded bytes; fixture payload')
                except (ValueError,OSError,EOFError,RuntimeError,subprocess.SubprocessError) as exc:
                    add(full,depth+1,'GZIP','error',size,note=str(exc))
            elif WORLD.search(name) or name.endswith('/maclar.json'):
                try:
                    data=json.loads(read(name))
                    count=len(data) if isinstance(data,list) else len(data.get('players',[]))
                    version='' if isinstance(data,list) else str(data.get('source',''))
                    add(full,depth+1,'JSON','parsed',size,count,version)
                except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as exc:
                    add(full,depth+1,'JSON','error',note=str(exc))
            else:
                add(full,depth+1,classified(name),'indexed',size,note='No executable or binary payload was run')

    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        name=path.relative_to(root).as_posix()
        ext=path.suffix.lower()
        if ext in ARCHIVES:
            archive(path,name,0)
        elif ext=='.csv':
            with path.open(encoding='utf-8-sig',newline='') as f:
                add(name,0,'CSV','parsed',path.stat().st_size,sum(1 for _ in csv.DictReader(f)))
        else:
            with path.open('rb') as stream:
                sample=stream.read(96)
            add(name,0,classified(name),'sampled',path.stat().st_size,note='header '+sample[:12].hex())
    return rows

class WorldReader:
    def __init__(self,data):
        self.data=data
        self.columns={key:i for i,key in enumerate(data['playerFields'])}
        required={'id','first','last','dob','nation'}
        if not required<=self.columns.keys():
            raise ValueError('Unsupported player schema')
        self.nations=data['nations']
    def identities(self):
        c=self.columns
        for row in self.data['players']:
            full=' '.join(str(row[c[field]] or '').strip() for field in ('first','last')).strip()
            born=row[c['dob']]
            nat=row[c['nation']]
            if not full or not isinstance(born,str) or not isinstance(nat,int) or not 0<=nat<len(self.nations):
                continue
            try:
                if date.fromisoformat(born).year<=1900:
                    continue
            except ValueError:
                continue
            yield (identity(full),born,self.nations[nat].get('code','')),str(row[c['id']]),full

def tff_round(text):
    for chunk in re.findall(r'<tr class="haftaninMaclariTr">(.*?)</tr>',text,re.S|re.I):
        match=re.search(r'macId=(\d+)',chunk,re.I)
        values={n:html.unescape(v).strip() for n,v in re.findall(r'_Label(1|4|5|6)"[^>]*>([^<]*)</span>',chunk)}
        if match and {'1','4','5','6'}<=values.keys() and values['5'].isdigit() and values['6'].isdigit():
            yield match[1],values['4'],values['1'],int(values['5']),int(values['6'])

def tff_detail(text):
    first=re.search(r'lblTakim1Skor"[^>]*>\s*(\d+)',text)
    second=re.search(r'dtMacBilgisi_(?:lblTakim2Skor|Label12)"[^>]*>\s*(\d+)',text)
    return (int(first[1]),int(second[1])) if first and second else None

def save_csv(path,header,rows):
    with Path(path).open('w',encoding='utf-8-sig',newline='') as stream:
        out=csv.writer(stream);out.writerow(header);out.writerows(rows)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    rows=inspect(args.source)
    save_csv(args.output,('kaynak','derinlik','bicim','durum','bayt','satir_veya_uye','surum','not'),rows)
    print(len(rows),Counter(row[3] for row in rows))

if __name__=='__main__':
    main()
