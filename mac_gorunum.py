"""Retained Canvas renderer for bounded match frames. No simulation writes."""
import math

from tema import FONT,PALETTE


class Pitch:
    def __init__(self,canvas,number,name):
        self.canvas=canvas
        self.number=number
        self.name=name
        self.items={}
        self.ball=None
        self.last=None
        self.size=None
        self.focus=None
        canvas.bind('<Configure>',lambda _:self.draw(self.last) if self.last else None)

    def draw(self,frame):
        c=self.canvas
        self.last=frame
        w,h=c.winfo_width(),c.winfo_height()
        size=(w,h)
        if size!=self.size:
            c.delete('all')
            self.items.clear()
            self.ball=None
            self.size=size
            pad=16
            usable_w,usable_h=max(1,w-2*pad),max(1,h-2*pad)
            cw=min(usable_w,usable_h*105/68)
            ch=min(usable_h,usable_w*68/105)
            self.bounds=((w-cw)/2,(h-ch)/2,(w+cw)/2,(h+ch)/2)
            x,y,right,bottom=self.bounds
            cw,ch=right-x,bottom-y
            for i in range(10):
                c.create_rectangle(x+i*cw/10,y,x+(i+1)*cw/10,bottom,fill=('#234e47' if i%2 else '#28584c'),outline='')
            c.create_rectangle(x,y,right,bottom,outline='#b0d2c5',width=2)
            center=x+cw/2
            c.create_line(center,y,center,bottom,fill='#b0d2c5')
            radius=min(cw,ch)*.13
            mid=y+ch/2
            c.create_oval(center-radius,mid-radius,center+radius,mid+radius,outline='#b0d2c5')
            for a,b in ((x,x+.16*cw),(right-.16*cw,right)):
                c.create_rectangle(a,y+.24*ch,b,bottom-.24*ch,outline='#b0d2c5')
            c.create_line(x+18,bottom-11,x+48,bottom-11,arrow='last',fill='#44dfce',width=2)
            c.create_line(right-18,bottom-11,right-48,bottom-11,arrow='last',fill='#ff9c63',width=2)
            for px,py in ((x,y),(right,y),(x,bottom),(right,bottom)):
                c.create_line(px,py,px,py-9,fill='#abbab4')
                c.create_polygon(px,py-9,px+6,py-7,px,py-5,fill='#b69c68',outline='')
            self.ref=c.create_polygon(0,0,1,1,fill='#f1d985',outline='#263243',state='hidden')
            self.flag=c.create_line(0,0,1,1,fill='#ebcd70',width=3,state='hidden')
            self.focus=c.create_text(x+9,y+9,anchor='nw',fill='#fff6ce',font=(FONT,10,'bold'))
        x,y,right,bottom=self.bounds
        def xy(px,py):return x+px*(right-x),y+py*(bottom-y)
        all_players=[(side,pid,*xy(px,py)) for side,team in enumerate(frame[2]) for pid,px,py in team]
        tx,ty=xy(*frame[1])
        carrier=min(all_players,key=lambda v:math.hypot(v[2]-tx,v[3]-ty),default=None)
        if carrier and math.hypot(carrier[2]-tx,carrier[3]-ty)>3:carrier=None
        if len(frame)>3:
            carrier=next((v for v in all_players if v[1]==frame[3]),None)
        used=set()
        placed=[]
        radius=11 if h<420 else 13
        for side,pid,px,py in all_players:
            used.add(pid)
            draw_y=py
            attempts=0
            while any(math.hypot(px-x1,draw_y-y1)<radius*1.78 for x1,y1 in placed) and attempts<6:
                attempts+=1
                draw_y=max(y+radius,min(bottom-radius,py+(-1 if attempts%2 else 1)*radius*(1+(attempts-1)//2)))
            draw_y=max(y+radius,min(bottom-radius,draw_y))
            placed.append((px,draw_y))
            if pid not in self.items:
                bead=c.create_oval(0,0,1,1,fill=('#44dfce' if side==0 else '#ff9c63'),outline='#142636',width=2)
                label=c.create_text(0,0,text=str(self.number(pid)),font=(FONT,9,'bold'),fill='#101925')
                self.items[pid]=(bead,label)
            bead,label=self.items[pid]
            c.coords(bead,px-radius,draw_y-radius,px+radius,draw_y+radius)
            c.coords(label,px,draw_y)
            c.tag_raise(label)
            c.itemconfigure(bead,outline='#fff6ce' if carrier and carrier[1]==pid else '#142636')
        for pid in set(self.items)-used:
            for item in self.items.pop(pid):c.delete(item)
        if self.ball is None:self.ball=c.create_oval(0,0,1,1,fill='#fcfcff',outline='#132b32',width=2)
        ball_radius=max(4,min(6,(right-x)*.007))
        c.coords(self.ball,tx-ball_radius,ty-ball_radius,tx+ball_radius,ty+ball_radius)
        c.tag_raise(self.ball)
        c.itemconfigure(self.focus,text=self.name(carrier[1]) if carrier else '')
        if len(frame)>4:
            meta=frame[4]
            rx,ry=xy(*meta['referee'])
            c.coords(self.ref,rx,ry-5,rx+5,ry,rx,ry+5,rx-5,ry)
            c.itemconfigure(self.ref,state='normal')
            c.tag_raise(self.ref)
            c.coords(self.flag,tx, y,tx+7,y-8)
            c.itemconfigure(self.flag,state='normal' if meta['signal']=='offside' else 'hidden')
            c.tag_raise(self.flag)
        c.tag_raise(self.focus)


def interpolate(frames):
    # Preserve official endpoints and avoid animating a phase reset across the pitch.
    result=[]
    for index,end in enumerate(frames):
        if index:
            start=frames[index-1]
            if start[0]==end[0] and math.dist(start[1],end[1])<=.26:
                for fraction in (1/3,2/3):
                    def blend(a,b):return a+(b-a)*fraction
                    xy=tuple(blend(a,b) for a,b in zip(start[1],end[1]))
                    sides=[]
                    for old,new in zip(start[2],end[2]):
                        prev={pid:(x,y) for pid,x,y in old}
                        sides.append(tuple((pid,blend(prev.get(pid,(x,y))[0],x),blend(prev.get(pid,(x,y))[1],y))
                                           for pid,x,y in new))
                    point=(end[0],xy,tuple(sides))
                    if len(end)>3:
                        point+=(end[3] if end[3]==start[3] else None,)
                    if len(end)>4:point+=(start[4],)
                    result.append(point)
        result.append(end)
    return result
