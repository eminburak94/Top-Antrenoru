from unittest import TestCase

from kariyer import LiveMatch, new
from veritabani import roster


class GoalkeeperSubstitutions(TestCase):
    def setUp(self):
        self.career=new('GALATASARAY',seed=888,match_model=4)
        self.match=LiveMatch(self.career)
        self.side=self.match.human
        slots=self.match.slots[self.side]
        self.keeper=next(pid for role,pid in slots if role=='GK')
        self.outfield=next(pid for role,pid in slots if role!='GK')
        bench=[p for p in roster(self.career['club'],self.career['year'],self.career)
               if p['id'] not in self.match.used]
        self.bench_keeper=next(p['id'] for p in bench if p['pos']=='GK')
        self.bench_player=next(p['id'] for p in bench if p['pos']!='GK')

    def test_normal_substitutions_preserve_goalkeeper_role(self):
        self.assertFalse(self.match.substitute(self.keeper,self.bench_player))
        self.assertFalse(self.match.substitute(self.outfield,self.bench_keeper))
        self.assertTrue(self.match.substitute(self.keeper,self.bench_keeper))
        self.assertIn(('GK',self.bench_keeper),self.match.slots[self.side])

    def test_dismissed_keeper_can_be_replaced_at_cost_of_outfield_slot(self):
        original=self.match.pitch.anchor[self.side].copy()
        self.match.pitch.card(self.side,self.keeper,2)
        self.assertEqual(self.match.pitch.anchor[self.side],
                         {pid:xy for pid,xy in original.items() if pid!=self.keeper})
        self.assertTrue(self.match.substitute(self.outfield,self.bench_keeper))
        slots=self.match.slots[self.side]
        self.assertEqual(len(slots),10)
        self.assertIn(('GK',self.bench_keeper),slots)
        self.assertNotIn(self.keeper,[pid for _,pid in slots])
        self.match.capture=True
        self.match.step()
        self.assertIn(self.bench_keeper,[pid for pid,*_ in self.match.frames[-1][2][self.side]])


class CareerPlaythrough(TestCase):
    def test_ui_and_domain_remain_consistent_through_rollover(self):
        import tkinter as tk
        from tkinter import ttk
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        from arayuz import UI
        from kariyer import advance
        from kayit import decode, encode
        from mac import eligible, select_slots
        from oyuncu import age_at, state
        from para import edit_value
        from sozlesme import asking_terms
        from test_v088_2d import button, descendants
        from transfer import asking_fee, deal
        from veritabani import TEAMS, all_players, roster, player
        from yarisma import standings, table

        def find(widget,kind,predicate=lambda _:True):
            return next(w for w in descendants(widget) if isinstance(w,kind) and predicate(w))

        def verify_ownership(s):
            indexed={p['id']:team for team in TEAMS for p in roster(team,s['year'],s)}
            self.assertEqual(sum(len(roster(t,s['year'],s)) for t in TEAMS),len(indexed))
            self.assertEqual(indexed,s['owners'])

        with TemporaryDirectory() as directory:
            root=tk.Tk()
            path=Path(directory)/'season.json'
            try:
                ui=UI(root)
                ui.autosave=lambda:None
                button(root,'TR / EN').invoke()
                find(root,ttk.Combobox).set('FENERBAHÇE')
                with patch('arayuz.new',side_effect=lambda *a,**kw:new(*a,seed=888,**kw)):
                    button(root,'Start career').invoke()
                s=ui.s
                club=s['club']
                self.assertEqual(club,'FENERBAHÇE')
                from hazirlik import DAYS
                for _ in range(DAYS):
                    self.assertTrue(advance(s))

                ui.squad()
                self.assertEqual(len(find(ui.body,ttk.Treeview).get_children()),len(roster(club,2000,s)))
                ui.tactics()
                root.update()
                shape=find(ui.body,ttk.Combobox,lambda w:'4-4-2' in w.cget('values'))
                shape.set('4-3-3')
                shape.event_generate('<<ComboboxSelected>>')
                root.update()
                button(ui.body,ui.management_text('apply_xi')).invoke()
                self.assertEqual(s['formation'],'4-3-3')
                self.assertEqual(len(s['manual_xi']),11)

                for target in all_players(s):
                    pid=target['id']
                    seller=s['owners'].get(pid)
                    if not seller or seller==club:
                        continue
                    fee=asking_fee(s,target)
                    terms=asking_terms(s,target,club,'Starter')
                    if deal(decode(encode(s)),pid,club,fee,**terms)[0]:
                        break
                else:self.fail('No eligible paid transfer')
                before={t:s['finance'][t].copy() for t in (club,seller)}
                ui.negotiate(target)
                offer=find(root,tk.Toplevel)
                with patch('arayuz.messagebox.showinfo',return_value='ok'):
                    button(offer,'Submit offer').invoke()
                self.assertFalse(offer.winfo_exists())
                self.assertEqual(s['owners'][pid],club)
                self.assertEqual(s['finance'][club]['cash'],before[club]['cash']-fee-terms['signing'])
                self.assertEqual(s['finance'][club]['transfer_budget'],before[club]['transfer_budget']-fee-terms['signing'])
                self.assertEqual(s['finance'][seller]['fees_received'],before[seller]['fees_received']+fee)
                self.assertEqual(state(s,target)['contract'],2000+terms['years'])
                verify_ownership(s)
                ui.finance_page()
                ledger_grid=find(ui.body,ttk.Treeview)
                displayed=dict(ledger_grid.item(i,'values') for i in ledger_grid.get_children())
                self.assertEqual(displayed['Cash'],edit_value(s,s['finance'][club]['cash']))
                self.assertEqual(displayed['Fees paid'],edit_value(s,s['finance'][club]['fees_paid']))

                # Exercise a known unavailable starter without engineering the match score.
                injured=s['manual_xi'][-1]
                state(s,player(s,injured))['injury']=2
                ui.squad()
                entries=[find(ui.body,ttk.Treeview).item(row,'values') for row in find(ui.body,ttk.Treeview).get_children()]
                injured_row=next(row for row in entries if row[0]==player(s,injured)['name'])
                self.assertEqual(int(injured_row[9]),2)
                self.assertNotIn(injured,[p for _,p in select_slots(s,club)])
                ui.preparation()
                fixture=next(f for f in s['schedule'] if f['week']==1 and club in (f['home'],f['away']))
                rival=fixture['away'] if fixture['home']==club else fixture['home']
                self.assertTrue(any(rival in w.cget('text') for w in descendants(ui.body) if isinstance(w,ttk.Label)))
                with patch('arayuz.messagebox.askyesno',return_value=True):
                    button(ui.body,'Start match week').invoke()
                    popup=find(root,tk.Toplevel)
                    button(popup,'Step').invoke()
                    root.update()
                    button(popup,'Substitute').invoke()
                    dialog=find(popup,tk.Toplevel)
                    incoming=list(w for w in descendants(dialog) if isinstance(w,ttk.Combobox))[1]
                    incoming.current(0)
                    button(dialog,'Apply').invoke()
                    self.assertFalse(dialog.winfo_exists())
                    button(popup,'Finish match').invoke()
                    root.update()
                self.assertEqual(s['week'],2)
                first=next(row for row in s['results'][0] if club in (row['home'],row['away']))
                self.assertTrue(any(e[3]=='sub' for e in first['play']))
                self.assertNotIn(injured,first['minutes'])
                self.assertGreater(s['finance'][fixture['home']]['tickets'],0)
                self.assertGreater(s['finance'][club]['wages_paid'],0)

                while s['week']<35:
                    self.assertTrue(advance(s))
                independently_counted=table()
                for week in s['results']:
                    for row in week:
                        a,b,x,y=(row[key] for key in ('home','away','x','y'))
                        for team,scored,conceded in ((a,x,y),(b,y,x)):
                            dst=independently_counted[team]
                            dst['gf']+=scored
                            dst['ga']+=conceded
                            dst['p']+=3 if scored>conceded else int(scored==conceded)
                            dst['w' if scored>conceded else 'd' if scored==conceded else 'l']+=1
                self.assertEqual(sum(map(len,s['results'])),306)
                self.assertEqual(s['teams'],independently_counted)
                ui.table()
                grid=find(ui.body,ttk.Treeview)
                self.assertEqual([(grid.item(i,'values')[0],int(grid.item(i,'values')[-1])) for i in grid.get_children()],
                                 [(t,independently_counted[t]['p']) for t in standings(s)])
                verify_ownership(s)
                self.assertTrue(s['employed'])
                expire_target=min(roster(club,s['year'],s),key=lambda p:age_at(p,s['year'],s['week']) or 99)
                state(s,expire_target)['contract']=2001
                with patch('arayuz.messagebox.askyesno',return_value=True):
                    ui.next()
                self.assertEqual((s['year'],s['week']),(2001,1))
                self.assertEqual(s['history'][-1]['teams'],independently_counted)
                self.assertIn([2001,'expired',expire_target['id'],club],s['contract_events'])
                self.assertTrue(all(state(s,player(s,uid))['contract']>2001 for uid in s['owners']))
                verify_ownership(s)
                with patch('arayuz.filedialog.asksaveasfilename',return_value=str(path)), patch('arayuz.user_directory',return_value=Path(directory)):
                    ui.save()
                snapshot=encode(s)
                self.assertTrue(path.is_file())
                print(f'Audit 34 weeks / 306 games, paid fee {fee}, recorded expiries '
                      f'{sum(row[1]=="expired" for row in s["contract_events"])}',flush=True)
            finally:
                root.destroy()
            root=tk.Tk()
            try:
                ui=UI(root)
                with patch('arayuz.filedialog.askopenfilename',return_value=str(path)):
                    button(root,'Kayıt yükle').invoke()
                self.assertEqual(encode(ui.s),snapshot)
            finally:
                root.destroy()
