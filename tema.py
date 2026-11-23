"""Shared colors and typography for the desktop interface."""
import tkinter as tk
from tkinter import ttk

PALETTE={
    'base':'#101925','panel':'#182536','hero':'#132837','action':'#263d51',
    'hover':'#34556a','pressed':'#223548','accent':'#5adac5','accent_hover':'#86e8d7',
    'ink':'#0e2530','text':'#edf5fb','muted':'#bacbd9','line':'#84adaf',
    'row':'#203044','stripe':'#27394e','field':'#214744','goal':'#b6d7d7',
    'input':'#f3f7fa','white':'#ffffff','warning':'#f4cd79',
}

FONT='Segoe UI'


def install(root):
    p=PALETTE
    root.configure(bg=p['base'])
    style=ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=p['panel'], foreground=p['text'], font=(FONT,10))
    style.configure('Desk.TFrame',background=p['row'])
    style.configure('DeskTitle.TLabel',background=p['row'],foreground=p['accent'],font=(FONT,12,'bold'))
    style.configure('DeskBody.TLabel',background=p['row'],foreground=p['text'])
    style.configure('Title.TLabel', font=(FONT,21,'bold'), foreground=p['accent'])
    style.configure('Warning.TLabel',foreground=p['warning'])
    style.configure('TCheckbutton',background=p['panel'],foreground=p['text'],
                    indicatorbackground=p['row'],indicatorforeground=p['accent'],focuscolor=p['accent'],padding=3)
    style.map('TCheckbutton',background=[('active',p['hover'])],
              foreground=[('disabled',p['muted'])],
              indicatorbackground=[('selected',p['action']),('disabled',p['base'])],
              indicatorforeground=[('selected',p['accent'])])
    style.configure('TMenubutton',background=p['action'],foreground=p['text'],arrowcolor=p['accent'],padding=(8,5))
    style.configure('TButton', background=p['action'],foreground=p['text'],padding=(10,6),focuscolor=p['accent'],borderwidth=0)
    style.map('TButton', background=[('disabled',p['base']),('pressed',p['pressed']),('active',p['hover'])],
              foreground=[('disabled',p['muted'])])
    style.configure('Accent.TButton',background=p['accent'],foreground=p['ink'])
    style.map('Accent.TButton',background=[('active',p['accent_hover'])],foreground=[('active',p['ink'])])
    style.configure('TNotebook.Tab',background=p['action'],foreground=p['text'],padding=(10,5))
    style.map('TNotebook.Tab',background=[('selected',p['accent'])],foreground=[('selected',p['ink'])])
    for widget in ('TCombobox','TEntry'):
        style.configure(widget,fieldbackground=p['row'],foreground=p['text'],
                        insertcolor=p['text'],arrowcolor=p['accent'],bordercolor=p['action'],
                        lightcolor=p['action'],darkcolor=p['action'],padding=5)
    style.map('TCombobox',fieldbackground=[('disabled',p['base']),('readonly',p['row'])],
              foreground=[('disabled',p['muted']),('readonly',p['text'])],
              bordercolor=[('focus',p['accent'])],
              selectbackground=[('readonly',p['action'])],selectforeground=[('readonly',p['text'])])
    for key,value in {'background':'row','foreground':'text','selectBackground':'accent','selectForeground':'ink'}.items():
        root.option_add('*TCombobox*Listbox.'+key,p[value])
    style.configure('Treeview',background=p['row'],fieldbackground=p['row'],foreground=p['text'],rowheight=27,borderwidth=0)
    style.configure('Treeview.Heading',background=p['base'],foreground=p['accent'],padding=7)
    style.map('Treeview',background=[('selected',p['accent'])],foreground=[('selected',p['ink'])])
    style.map('Treeview.Heading',background=[('active',p['hover'])])


class MenuButton(ttk.Button):
    """Keyboard- and pointer-operable navigation popup with the shared palette."""

    def __init__(self, parent, label, entries):
        super().__init__(parent, text=label+' ▾', command=self.open)
        self.entries=entries
        self.popup=None
        for key in ('<Return>','<Down>'):
            self.bind(key,self.open)

    def open(self, event=None):
        if self.instate(('disabled',)):
            return 'break'
        if self.popup is not None:
            self.close()
            return 'break'
        p=PALETTE
        w=self.popup=tk.Toplevel(self)
        w.overrideredirect(True)
        w.transient(self.winfo_toplevel())
        box=tk.Listbox(w,height=len(self.entries),width=max(22,max(len(s) for s,_ in self.entries)+3),
                       background=p['row'],foreground=p['text'],selectbackground=p['accent'],
                       selectforeground=p['ink'],highlightbackground=p['line'],
                       highlightcolor=p['accent'],highlightthickness=1,font=(FONT,10),
                       exportselection=False,activestyle='none')
        box.pack(fill='both',expand=True)
        for label,_ in self.entries:
            box.insert('end',label)
        box.selection_set(0)
        box.activate(0)
        def select(index):
            callback=self.entries[index][1]
            self.close()
            callback()
            return 'break'
        box.bind('<Return>',lambda _:select(box.index('active')))
        box.bind('<space>',lambda _:select(box.index('active')))
        box.bind('<ButtonRelease-1>',lambda e:select(box.nearest(e.y)))
        w.bind('<Escape>',lambda _:self.close())
        w.bind('<ButtonPress-1>',lambda e:self.close() if e.widget==w else None)
        w.update_idletasks()
        x=min(self.winfo_rootx(),w.winfo_screenwidth()-w.winfo_reqwidth())
        y=self.winfo_rooty()+self.winfo_height()
        w.geometry(f'+{max(0,x)}+{y}')
        w.deiconify()
        w.wait_visibility()
        w.grab_set()
        box.focus_force()
        return 'break'

    def close(self):
        if self.popup is not None:
            w,self.popup=self.popup,None
            w.grab_release()
            w.destroy()
            self.focus_set()
        return 'break'


def wrap_controls(frame):
    """Wrap controls without grid propagation changing the measured width."""
    frame.grid_propagate(False)
    padding=frame.cget('padding')
    inset=2*frame.winfo_pixels(padding[0]) if padding else 0
    previous=None

    def arrange(event=None):
        nonlocal previous
        widgets=frame.winfo_children()
        if not widgets:
            return
        cell_width=max(w.winfo_reqwidth() for w in widgets)+4
        cell_height=max(w.winfo_reqheight() for w in widgets)+2
        columns=max(1,((event.width-inset)//cell_width if event else len(widgets)))
        layout=(columns,cell_height)
        if previous==layout:
            return
        previous=layout
        for index,widget in enumerate(widgets):
            row,column=divmod(index,columns)
            widget.grid(row=row,column=column,sticky='w',padx=2,pady=1)
        rows=(len(widgets)+columns-1)//columns
        frame.configure(height=rows*cell_height+inset)

    frame.bind('<Configure>',arrange)
    arrange()
