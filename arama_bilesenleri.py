"""Shared paginated and sortable search widgets."""
import math
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tema import FONT


class Search:
    def __init__(self,ui,parent,fields,columns,query,prefs,basic=None):
        self.ui=ui
        self.query=query
        self.prefs=prefs
        self.variables={}
        self.blank={}
        self.page=0
        self.order=None
        self.ids=[]
        self.pending=None
        self.panel=ttk.Frame(parent)
        self.panel.pack(fill='x',pady=(0,5))
        self.advanced=ttk.Frame(parent)
        counter=[0,0]
        self.advanced_keys=set()
        for key,label,choices in fields:
            advanced=basic is not None and key not in basic
            if advanced:self.advanced_keys.add(key)
            panel=self.advanced if advanced else self.panel
            line,col=divmod(counter[advanced],6)
            counter[advanced]+=1
            cell=ttk.Frame(panel)
            cell.grid(row=line,column=col,sticky='ew',padx=3,pady=2)
            panel.columnconfigure(col,weight=1)
            ttk.Label(cell,text=label).pack(anchor='w')
            options=dict(choices or [])
            stored=prefs.get(key,'')
            current=next((k for k,v in options.items() if v==stored),'*') if choices else stored
            var=tk.StringVar(value=current)
            self.variables[key]=(var,options)
            self.blank[key]='*' if choices else ''
            if choices:
                ttk.Combobox(cell,textvariable=var,values=list(options),state='readonly',width=10).pack(fill='x')
            else:
                ttk.Entry(cell,textvariable=var,width=9).pack(fill='x')
            var.trace_add('write',self.defer)
        self.filter_actions=ttk.Frame(parent)
        self.filter_actions.pack(fill='x',pady=(0,4))
        self.actions=ttk.Frame(parent)
        self.actions.pack(fill='x',pady=(0,4))
        self.button(ui.tr('Ara','Search'),self.refresh,parent=self.filter_actions)
        self.advanced_button=None
        if counter[1]:
            self.advanced_button=self.button(ui.tr('Gelişmiş','Advanced'),self.toggle_advanced,parent=self.filter_actions)
        self.button(ui.tr('Sıfırla','Reset'),self.reset,parent=self.filter_actions)
        self.button('‹',lambda:self.move(-1),parent=self.filter_actions)
        self.button('›',lambda:self.move(1),parent=self.filter_actions)
        self.message=ttk.Label(self.filter_actions)
        self.message.pack(side='right',padx=6)
        self.table=table(parent,columns)
        self.table.bind('<Destroy>',lambda _:self.cancel())
        for i,c in enumerate(columns):
            self.table.heading(i,text=c,command=lambda i=i:self.sort(i))
        self.refresh()

    def button(self,label,action,parent=None):
        widget=ttk.Button(parent or self.actions,text=label,command=action)
        widget.pack(side='left',padx=2)
        return widget

    def toggle_advanced(self):
        if self.advanced.winfo_manager():
            self.advanced.pack_forget()
        else:
            self.advanced.pack(fill='x',before=self.filter_actions,pady=(0,4))

    def cancel(self):
        if self.pending is not None:
            self.panel.after_cancel(self.pending)
            self.pending=None

    def defer(self,*_):
        self.cancel()
        self.pending=self.panel.after(120,self.refresh)

    def reset(self):
        for key,(var,_) in self.variables.items():var.set(self.blank[key])
        self.refresh()

    def selection(self):
        return next(iter(self.table.selection()),None)

    def sort(self,index):
        self.order=(index,self.order==(index,False))
        self.refresh()

    def move(self,delta):
        self.page=max(0,min(self.page+delta,max(0,(len(self.rows)-1)//60)))
        self.draw()

    def refresh(self):
        self.cancel()
        filters={key:options.get(var.get(),'') if options else var.get().strip()[:180]
                 for key,(var,options) in self.variables.items()}
        self.prefs.update(filters)
        if self.advanced_button:
            active=sum(bool(filters[key]) for key in self.advanced_keys)
            self.advanced_button.configure(text=self.ui.tr('Gelişmiş','Advanced')+(f' ({active})' if active else ''))
        self.rows,error=self.query(filters)
        if self.order is not None:
            index,rev=self.order
            def key(row):
                value=row[2][index]
                return (value is None, type(value) is str, value if value is not None else '')
            known=[row for row in self.rows if row[2][index] is not None]
            unknown=[row for row in self.rows if row[2][index] is None]
            self.rows=sorted(known,key=key,reverse=rev)+unknown
        self.page=0
        self.draw(error)

    def draw(self,error=None):
        t=self.table
        t.delete(*t.get_children())
        if error:
            self.message.configure(text=error)
            return
        count=len(self.rows)
        label=f'{count} · {self.page+1}/{max(1,(count+59)//60)}' if count else self.ui.tr('Sonuç yok','No results')
        self.message.configure(text=label)
        for i,(uid,values,_) in enumerate(self.rows[self.page*60:(self.page+1)*60]):
            t.insert('','end',iid=uid,values=values,tags=('odd' if i%2 else 'even',))
        resize_columns(t)


def table(parent,columns):
    outer=ttk.Frame(parent)
    outer.pack(fill='both',expand=True)
    outer.columnconfigure(0,weight=1)
    outer.rowconfigure(0,weight=1)
    grid=ttk.Treeview(outer,columns=list(range(len(columns))),show='headings',selectmode='browse')
    grid.grid(row=0,column=0,sticky='nsew')
    vertical=ttk.Scrollbar(outer,command=grid.yview)
    vertical.grid(row=0,column=1,sticky='ns')
    horizontal=ttk.Scrollbar(outer,orient='horizontal',command=grid.xview)
    horizontal.grid(row=1,column=0,sticky='ew')
    grid.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set)
    grid.tag_configure('odd',background='#27394e')
    grid.tag_configure('even',background='#203044')
    for i,c in enumerate(columns):grid.heading(i,text=c)
    return grid


def resize_columns(grid,compact=False):
    measure=font.Font(root=grid,font=(FONT,10)).measure
    for i,column in enumerate(grid['columns']):
        fit=max([measure(grid.heading(column,'text'))+28]+[measure(grid.set(item,column))+26 for item in grid.get_children()])
        grid.column(column,width=min(440,max(52 if compact else 80,fit)),
                    minwidth=45 if compact else 70,stretch=i==0,anchor='w' if i==0 else 'center')


def number(filters,key,parse=float):
    value=filters.get(key)
    if not value:return None
    result=parse(value)
    if not math.isfinite(result) or result<0:raise ValueError(value)
    return result
