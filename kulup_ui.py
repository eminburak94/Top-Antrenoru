"""Club desk with board meetings, supporter signals and newspaper editions."""
from tkinter import ttk, messagebox

from ekonomi import projection
from para import text as money
from yarisma import standings
import yasayan_kulup as life


class ClubLifeViews:
    def club_life_page(self, section=0):
        self.clear()
        s,tr=self.s,self.tr
        club=s['club']
        model=s['living_club']
        tabs=ttk.Notebook(self.body)
        tabs.pack(fill='both',expand=True)
        board,support,press=(ttk.Frame(tabs,padding=14) for _ in range(3))
        for panel,title in ((board,tr('Yönetim kurulu','Board')),
                            (support,tr('Taraftarlar','Supporters')),
                            (press,tr('Spor servisi','Sports desk'))):
            tabs.add(panel,text=title)
        tabs.select(section)

        def line(parent,text,heading=False):
            style='Title.TLabel' if heading else 'TLabel'
            ttk.Label(parent,text=text,style=style,wraplength=750,justify='left').pack(anchor='w',pady=4)

        def act(panel,label,explanation,action,tab,enabled=True):
            def submit():
                if messagebox.askyesno(label,explanation,parent=self.r) and action():
                    self.autosave()
                    self.club_life_page(tab)
            button=ttk.Button(panel,text=label,command=submit)
            button.pack(anchor='w',pady=3)
            if not enabled:button.state(['disabled'])

        row=model['board']
        line(board,club,True)
        rank=f"#{standings(s).index(club)+1}" if s['results'] else '—'
        line(board,tr('Sezon hedefi #{target} · Lig sırası {rank}',
                      'Season target #{target} · League position {rank}').format(
                          target=s['board_targets'][club],rank=rank))
        line(board,tr('Yönetim güveni {trust}/100 · İş riski {risk}/100',
                      'Board confidence {trust}/100 · Job risk {risk}/100').format(
                          trust=s['confidence'],risk=row['risk']))
        line(board,tr('Sportif baskı {sport}/8 · Mali baskı {fiscal}/8 · Son maç puanları: {form}',
                      'Sporting pressure {sport}/8 · Financial pressure {fiscal}/8 · Recent points: {form}').format(
                          sport=row['sport'],fiscal=row['fiscal'],form=' · '.join(map(str,row['form'])) or '—'))
        plan=projection(s,club)
        latest=model.get('match_review')
        if latest:
            status=tr('Son maç {opponent} · {goals}–{conceded} · Güven {trust:+d} · Risk {risk:+d}',
                      'Last match {opponent} · {goals}–{conceded} · Confidence {trust:+d} · Risk {risk:+d}')
            line(board,status.format(**latest))
            line(board,tr('Sportif baskı {sport:+d} · Mali baskı {fiscal:+d}',
                          'Sporting pressure {sport:+d} · Financial pressure {fiscal:+d}').format(**latest))
            if latest['under']:
                line(board,tr('Lig sırası ve son maç puanları hedefin altında.',
                              'League position and recent points fell short of the target.'))
            if latest['stress']:
                line(board,tr('Nakit veya maaş baskısı risk değerlendirmesine girdi.',
                              'Cash or wage pressure affected the risk assessment.'))
            if latest['pledge']:
                line(board,tr('Tamamlanan taahhüdün güvene etkisi','Confidence effect of resolved commitments')
                     +f" {latest['pledge']:+d}")
        line(board,tr('Sezon sonu nakit tahmini','Projected season-end cash')+' · '+money(s,plan['closing']))
        ready=s['employed'] and (not row['meeting'] or s['week']-row['meeting']>=6)
        if row['meeting'] and not ready:
            line(board,tr('Yeni görüşme için son görüşmeden itibaren altı hafta gerekir.',
                          'The board will meet again six weeks after your last meeting.'))
        wage,cost=life.budget_shift(s)
        if wage:
            label=tr('Bütçeyi dengele','Rebalance budgets')
            explanation=tr('Transfer bütçesi {cost} azalır. Haftalık maaş bütçesi {wage} artar.',
                           'Transfer budget falls by {cost}. Weekly wage budget rises by {wage}.').format(
                               cost=money(s,cost),wage=money(s,wage))
            line(board,explanation)
            act(board,label,explanation,lambda:life.meeting(s,'budget'),0,ready)
        else:
            line(board,tr('Yönetim mevcut mali planda maaş bütçesine aktarım alanı görmüyor.',
                          'The current financial plan leaves no room to reallocate funds to wages.'))
        if 'recovery' in model:
            self.commitment_line(line,board,model['recovery'],tr('Toparlanma planı','Recovery plan'))
        elif not row['used_recovery'] and s['week']<=32 and row['risk']>=40:
            act(board,tr('Toparlanma planı iste','Request a recovery plan'),
                tr('Yönetim üç maç süre verir. 5 puan güveni +4, daha azı −5 değiştirir.',
                   'The board gives you three matches. Five points earns +4 confidence. Fewer costs 5.'),
                lambda:life.meeting(s,'recovery'),0,ready)

        score,run,change=model['fans'][club]
        line(support,tr('Taraftar güveni','Supporter confidence'),True)
        ttk.Progressbar(support,maximum=100,value=score,length=400).pack(anchor='w')
        line(support,f'{score}/100 · {tr("Son tepki","Latest reaction")} {change:+d}')
        if latest:
            goals,conceded=latest['goals'],latest['conceded']
            result=(tr('Galibiyet','Win') if goals>conceded else
                    tr('Mağlubiyet','Defeat') if goals<conceded else tr('Beraberlik','Draw'))
            context=[result,f"{latest['opponent']} {goals}–{conceded}"]
            if club in life.ISTANBUL_RIVALS and latest['opponent'] in life.ISTANBUL_RIVALS:
                context.append(tr('derbi','derby'))
            if abs(goals-conceded)>=3:context.append(tr('farklı skor','wide margin'))
            if abs(run)>=3:context.append(tr('sonuç serisi','run of results'))
            line(support,' · '.join(context)+f" · {tr('Son maç tepkisi','Last match reaction')} {latest['fans']:+d}")
        if run:
            label=tr('Galibiyet serisi','Winning run') if run>0 else tr('Mağlubiyet serisi','Losing run')
            line(support,f'{label} · {abs(run)}')
        line(support,tr('Ev maçlarının bilet gelirine güncel etki','Current effect on home gate receipts')
             +f' · {(life.attendance(s,club)-1)*100:+.1f}%')
        line(support,tr('Derbiler, lig beklentileri, seriler ve önemli transferler tribünleri etkiler.',
                        'Derbies, league expectations, runs of form and major transfers shape the crowd’s response.'))

        article_frame=ttk.Frame(press)
        question=life.pending_question(s)
        if question:
            _,_,kind,_,subject=question
            prompts={
                'derby':tr('{name} derbisinden sonra tribünlere ne söylersiniz?',
                           'What do you tell the supporters after the {name} derby?'),
                'poor':tr('{name} maçından sonra eleştirilere yanıtınız nedir?',
                          'How do you respond to criticism after the {name} match?'),
                'streak':tr('{name} maçından sonra seri sürüyor. Bundan sonra hedefiniz ne?',
                            'The run continues after the {name} match. What is your next target?'),
                'transfer':tr('{name} haberiyle ilgili taraftarlara ne söylersiniz?',
                              'What do you tell the fans about the news on {name}?'),
            }
            line(press,prompts[kind].format(name=subject),True)
            answers=(
                ('responsibility',tr('Sorumluluğu al','Take responsibility'),
                 tr('Yönetim güveni +1 ve taraftar güveni +1.', 'Board confidence +1 and supporter confidence +1.'),True),
                ('protect',tr('Oyuncuları koru','Shield the players'),
                 tr('Kadro morali +2, taraftar güveni −1.', 'Squad morale +2, supporter confidence −1.'),True),
                ('promise',tr('Üç maçta beş puan sözü ver','Promise five points in three matches'),
                 tr('Taraftar güveni hemen +2. Söz tutulursa taraftar +3 ve yönetim +2, tutulmazsa taraftar −5 ve yönetim −3.',
                    'Supporter confidence rises by 2 immediately. Keeping the promise adds 3 supporter and 2 board confidence. Missing it costs 5 and 3.'),
                 'promise' not in model and s['week']<=32),
            )
            for key,label,preview,enabled in answers:
                act(press,label,preview,lambda key=key:life.press_answer(s,key),2,enabled)
        if 'promise' in model:
            self.commitment_line(line,press,model['promise'],tr('Basına verilen söz','Press promise'))
        article_frame.pack(fill='both',expand=True,pady=(8,0))
        table=ttk.Treeview(article_frame,columns=('date','club','article'),show='headings')
        scroll=ttk.Scrollbar(article_frame,command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y')
        table.pack(side='left',fill='both',expand=True)
        for key,title,width in (('date',tr('Sezon / hafta','Season / week'),105),
                                ('club',tr('Kulüp','Club'),170),('article',tr('Manşet','Headline'),480)):
            table.heading(key,text=title)
            table.column(key,width=width,stretch=key=='article')
        for year,week,kind,team,subject,detail in reversed(model['briefs']):
            table.insert('','end',values=(f'{year} / {week}',team,self.club_headline(kind,subject,detail)))

    def commitment_line(self,line,panel,progress,label):
        remaining,points=progress
        line(panel,f"{label} · {self.tr('Kalan maç','Matches left')} {remaining} · {self.tr('Puan','Points')} {points}/5")

    def club_headline(self,kind,subject,detail):
        tr=self.tr
        if kind=='budget':
            return tr('Maaş bütçesi aktarımla yükseldi','Wage budget raised by reallocation')+' · '+money(self.s,int(detail))
        if kind=='dismissed':
            return tr('Mali kriz sonrası görevden alma','Dismissal amid financial pressure') if detail=='financial' else tr(
                'Yönetim teknik direktörle yollarını ayırdı','Board dismisses the manager')
        titles={
            'derby':tr('Derbi manşeti','Derby headlines'),
            'poor':tr('Sonuçların ardından eleştiri','Criticism after defeat'),
            'heavy':tr('Farklı yenilgi sonrası savunmaya eleştiri','Defence criticised after heavy defeat'),
            'streak':tr('Galibiyet serisi sürüyor','Winning run continues'),
            'strong':tr('Sahada güçlü yanıt','Convincing performance'),
            'promise_met':tr('Basına verilen söz tutuldu','Press promise kept'),
            'promise_missed':tr('Basına verilen söz tutulamadı','Press promise missed'),
            'recovery_met':tr('Toparlanma hedefi karşılandı','Recovery target met'),
            'recovery_missed':tr('Toparlanma hedefi kaçtı','Recovery target missed'),
            'board_warning':tr('Yönetim sabır sınırında','Board patience wearing thin'),
            'response_responsibility':tr('Teknik direktör sorumluluğu üstlendi','Manager takes responsibility'),
            'response_protect':tr('Teknik direktör oyuncularını savundu','Manager shields the players'),
            'response_promise':tr('Teknik direktörden beş puan sözü','Manager promises five points'),
            'transfer':tr('Transfer masasında','On the transfer desk'),
            'transfer_reinforcement':tr('İlk 11 için takviye','Reinforcement for the starting XI'),
            'transfer_cost':tr('Bonservis tartışma yarattı','Transfer fee draws scrutiny'),
            'transfer_exit':tr('Ayrılık kadroda boşluk bıraktı','Departure leaves a gap in the squad'),
        }
        return ' · '.join(part for part in (titles[kind],subject,detail) if part)
