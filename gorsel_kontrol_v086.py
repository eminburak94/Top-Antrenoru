"""Capture only windows created by the visual QA process."""
from ctypes import wintypes
import ctypes as c
from pathlib import Path
import struct
import time
import tkinter as tk
from tkinter import ttk
import zlib

from arayuz import UI
from kariyer import new,advance
from veritabani import roster

user=c.windll.user32
gdi=c.windll.gdi32
HANDLE=wintypes.HANDLE
for lib,name,types,result in (
    (user,'GetAncestor',[HANDLE,c.c_uint],HANDLE),
    (user,'GetWindowRect',[HANDLE,c.POINTER(wintypes.RECT)],c.c_int),
    (user,'GetDC',[HANDLE],HANDLE),
    (user,'ReleaseDC',[HANDLE,HANDLE],c.c_int),
    (user,'PrintWindow',[HANDLE,HANDLE,c.c_uint],c.c_int),
    (gdi,'CreateCompatibleDC',[HANDLE],HANDLE),
    (gdi,'CreateCompatibleBitmap',[HANDLE,c.c_int,c.c_int],HANDLE),
    (gdi,'SelectObject',[HANDLE,HANDLE],HANDLE),
    (gdi,'DeleteObject',[HANDLE],c.c_int),
    (gdi,'DeleteDC',[HANDLE],c.c_int),
    (gdi,'GetDIBits',[HANDLE,HANDLE,c.c_uint,c.c_uint,c.c_void_p,c.c_void_p,c.c_uint],c.c_int),
):
    func=getattr(lib,name)
    func.argtypes=types
    func.restype=result


def chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))


def capture(widget,path):
    widget.lift()
    widget.update()
    handle=user.GetAncestor(widget.winfo_id(),2)
    rect=wintypes.RECT()
    assert user.GetWindowRect(handle,c.byref(rect))
    w,h=rect.right-rect.left,rect.bottom-rect.top
    screen=user.GetDC(handle)
    mem=gdi.CreateCompatibleDC(screen)
    bitmap=gdi.CreateCompatibleBitmap(screen,w,h)
    previous=gdi.SelectObject(mem,bitmap)
    try:
        assert user.PrintWindow(handle,mem,2)
        gdi.SelectObject(mem,previous)
        buffer=c.create_string_buffer(w*h*4)
        header=c.create_string_buffer(struct.pack('<IiiHHIIiiII',40,w,-h,1,32,0,0,0,0,0,0))
        assert gdi.GetDIBits(mem,bitmap,0,h,buffer,header,0)==h
        raw=buffer.raw
        rgb=bytearray(w*h*3)
        rgb[0::3],rgb[1::3],rgb[2::3]=raw[2::4],raw[1::4],raw[0::4]
        assert len(set(rgb))>20
        scans=b''.join(b'\0'+rgb[i:i+w*3] for i in range(0,len(rgb),w*3))
        path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
                         +chunk(b'IDAT',zlib.compress(scans))+chunk(b'IEND',b''))
        print(path,w,h)
    finally:
        gdi.SelectObject(mem,previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(mem)
        user.ReleaseDC(handle,screen)


def children(root):
    for child in root.winfo_children():
        yield child
        yield from children(child)


def main():
    from unittest.mock import patch
    from kariyer import LiveMatch
    from mac_gorunum import Pitch
    required={'corner','freekick','penalty','offside','foul'}
    found=None
    for seed in range(810,2000):
        s=new('GALATASARAY',seed=seed,match_model=3)
        preview=LiveMatch(s)
        wall=False
        while preview.minute<90:
            preview.step()
            wall=wall or bool(preview.pitch.wall)
        if wall and required<={e[3] for e in preview.play}:
            found=seed
            break
    assert found
    log=[]
    folder=Path('V086_EKRANLAR')
    folder.mkdir(exist_ok=True)
    sequence=folder/'korner_kareleri'
    sequence.mkdir(exist_ok=True)
    root=tk.Tk()
    try:
        ui=UI(root);root.geometry('1280x720+24+24')
        ui.autosave=lambda:None;ui.begin(s)
        dialog=ui.set_piece_page()
        capture(dialog,folder/'07_duran_top_taktikleri.png')
        dialog.destroy()
        match=LiveMatch(s)
        created=[]
        def make(*args):
            renderer=Pitch(*args)
            created.append(renderer)
            return renderer
        with patch('arayuz.LiveMatch',return_value=match),patch('arayuz.Pitch',side_effect=make):
            ui.live()
        root.update()
        popup=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
        renderer=created[0]
        controls={w.cget('text'):w for w in children(popup) if isinstance(w,ttk.Button)}
        next(w for w in children(popup) if isinstance(w,ttk.Checkbutton)).invoke()
        labels={'corner':'02_korner','freekick':'03_serbest_vurus','penalty':'04_penalti',
                'offside':'05_ofsayt','foul':'06_hakem_karari'}
        done=set()
        corner_minute=None;frames=0;last=None
        for _ in range(4000):
            if not popup.winfo_exists():break
            controls['Adım'].invoke()
            if 'foul' not in done and match.play:
                logs=[w for w in children(popup) if isinstance(w,tk.Text)]
                if logs and any(term in logs[0].get('1.0','4.0').lower() for term in ('faul','avantaj','sarı kart','kırmızı kart')):
                    capture(popup,folder/(labels['foul']+'.png'))
                    log.append(('foul journal',match.minute))
                    done.add('foul')
            root.update()
            frame=renderer.last
            if not frame or len(frame)<5 or frame is last:continue
            last=frame
            minute=frame[0];meta=frame[4]
            if 'normal' not in done and minute>1 and frame[3] and not meta['set_piece']:
                capture(popup,folder/'01_normal_mac.png')
                done.add('normal')
                log.append(('normal',minute))
            kind=meta['set_piece']
            signal=meta['signal']
            if kind=='freekick' and not meta['wall']:kind=None
            current=kind if kind in labels else signal if signal=='offside' else 'foul' if signal in ('foul','advantage','yellow','red') else None
            if 'foul' not in done and signal in ('foul','advantage','yellow','red'):
                capture(popup,folder/(labels['foul']+'.png'))
                log.append(('foul',minute))
                done.add('foul')
            if current and current not in done:
                if current in ('corner','freekick','penalty') and not frame[3]:continue
                capture(popup,folder/(labels[current]+'.png'))
                log.append((current,minute))
                done.add(current)
                if current=='corner':corner_minute=minute
            if minute==corner_minute and frames<4:
                frames+=1
                capture(popup,sequence/(f'{frames:02d}.png'))
            if done=={'normal',*labels} and frames>=3:break
        assert done=={'normal',*labels},(found,done)
        with patch('arayuz.messagebox.askyesno',return_value=True):controls['Maçı bitir'].invoke()
        root.update()
        ui.last_report()
        popup=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
        tabs=next(w for w in children(popup) if isinstance(w,ttk.Notebook))
        for tab in tabs.tabs():
            if tabs.tab(tab,'text')=='Taktik analizi':tabs.select(tab)
        capture(popup,folder/'08_mac_sonrasi.png')
        import json
        (folder/'olay_kaniti.json').write_text(json.dumps(dict(seed=found,home=match.a,away=match.b,events=log,
                                     final=[match.x,match.y],corner_frames=frames),ensure_ascii=False),encoding='utf-8')
    finally:
        root.destroy()


if __name__=='__main__':
    main()
