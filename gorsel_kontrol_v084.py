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
    folder=Path('V084_EKRANLAR')
    folder.mkdir(exist_ok=True)
    root=tk.Tk()
    try:
        ui=UI(root)
        root.geometry('1280x720+24+24')
        ui.autosave=lambda:None
        s=new('GALATASARAY',seed=813,match_model=1)
        for _ in range(2):advance(s)
        ui.begin(s)
        for name,callback in (('01_menajer',ui.dashboard),('02_kadro',ui.squad),
                              ('03_futbolcu_arama',ui.market),('04_personel_arama',lambda:ui.staff_page('all'))):
            callback()
            capture(root,folder/(name+'.png'))
        table=next(w for w in children(ui.body) if isinstance(w,ttk.Treeview))
        table.selection_set(table.get_children()[0])
        control=next(w for w in children(ui.body) if isinstance(w,ttk.Button)
                     and w.cget('text')==ui.management_text('open_profile'))
        control.invoke()
        popup=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
        capture(popup,folder/'06_personel_profili.png')
        popup.destroy()
        ui.profile(roster(s['club'],s['year'],s)[0])
        popup=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
        capture(popup,folder/'05_futbolcu_profili.png')
        popup.destroy()
        ui.live();root.update()
        popup=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
        controls={w.cget('text'):w for w in children(popup) if isinstance(w,ttk.Button)}
        next(w for w in children(popup) if isinstance(w,ttk.Checkbutton)).invoke()
        controls['Başlat'].invoke()
        end=time.monotonic()+.7
        while time.monotonic()<end:
            root.update()
            time.sleep(.02)
        controls['Durdur'].invoke()
        capture(popup,folder/'07_mac_merkezi.png')
        controls['Maçı bitir'].invoke()
        ui.last_report()
        popup=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
        tabs=next(w for w in children(popup) if isinstance(w,ttk.Notebook))
        for tab in tabs.tabs():
            if tabs.tab(tab,'text')=='Taktik analizi':tabs.select(tab)
        capture(popup,folder/'08_mac_sonrasi.png')
    finally:
        root.destroy()


if __name__=='__main__':
    main()
