from veritabani import TEAMS
from donem import scaled
from yarisma import expectation, standings

FLOW=('tickets','season_tickets','broadcast','sponsors','prize','staff','academy','maintenance','bonuses','investment','interest','borrowed','repaid')

def initial_finances():
    rich = ('GALATASARAY', 'FENERBAHÇE', 'BEŞİKTAŞ', 'TRABZONSPOR')
    return {team: dict(cash=5000000 if team in rich else 1800000) for team in TEAMS}

def wages(s, team, amount):
    ledger = s['finance'][team]
    ledger['cash'] -= amount
    ledger['wages_paid'] += amount

def capacity(team):
    tier=expectation(team)
    # Fictional financial model, in seats.
    return {3:33500,7:22500,13:13500}[tier]

def cycle(year):
    return {2000:1.,2001:.84,2002:.93,2008:.91,2009:.94,2020:.73,2021:.84}.get(year,1.)

def initialize(ledger):
    ledger.setdefault('debt',0)
    ledger.setdefault('academy_level',45)
    ledger.setdefault('facilities',45)
    for key in FLOW:
        ledger.setdefault(key,0)

def flow(ledger,key,amount,expense=False):
    ledger[key]+=amount
    ledger['cash']+=-amount if expense else amount

def gate(s,home,participants):
    ledger=s['finance'][home]
    crowd=capacity(home)*(.40+s['club_reputation'][home]/180)
    receipts=scaled(s,'gate',crowd*4.75*min(11,participants)/11*cycle(s['year']))
    flow(ledger,'tickets',receipts)

def prizes(s):
    for rank,team in enumerate(standings(s),1):
        ledger=s['finance'][team]
        flow(ledger,'prize',scaled(s,'prize',155000+(19-rank)*29000))
        flow(ledger,'bonuses',scaled(s,'prize',(19-rank)*7500),expense=True)
        receipts=sum(ledger[k] for k in ('tickets','season_tickets','broadcast','sponsors','prize'))
        # Board funds visible long-lived assets from surplus above operating reserves.
        receipts+=ledger.get('commercial',0)
        reserve=scaled(s,'operations',850000)+receipts
        investment=int(max(0,ledger['cash']-reserve-ledger['debt'])*.22)
        if investment:
            flow(ledger,'investment',investment,expense=True)
            ledger['academy_level']=min(100,ledger['academy_level']+investment//420000)
            ledger['facilities']=min(100,ledger['facilities']+investment//370000)
        service(s,team)

def service(s,team):
    ledger=s['finance'][team]
    if ledger['cash']<0:
        ceiling=scaled(s,'operations',350000+s['club_reputation'][team]*11000)
        draw=min(-ledger['cash'],max(0,ceiling-ledger['debt']))
        ledger['debt']+=draw
        flow(ledger,'borrowed',draw)
    elif ledger['debt'] and ledger['cash']>230000:
        pay=min(ledger['debt'],(ledger['cash']-230000)//4)
        ledger['debt']-=pay
        flow(ledger,'repaid',pay,expense=True)

def settle_transfer(s, buyer, seller, fee):
    s['finance'][buyer]['cash'] -= fee
    if seller:
        s['finance'][seller]['cash'] += fee


def payroll(s, team):
    from oyuncu import state
    from veritabani import roster
    loans=s.get('loans',{})
    total=sum(wage_shares(s,p['id'],state(s,p)['wage'])[0] for p in roster(team,s['year'],s))
    return total+sum(wage_shares(s,pid,s['fitness'][pid]['wage'])[1]
                     for pid,loan in loans.items() if loan['parent']==team)


def wage_shares(s,pid,wage):
    loan=s.get('loans',{}).get(pid)
    borrower=wage*loan['share']//100 if loan else wage
    return borrower,wage-borrower


def commitments(s,team):
    outgoing=incoming=0
    for _,_,buyer,seller,amount in s.get('transfer_payments',[]):
        if buyer==team:outgoing+=amount
        if seller==team:incoming+=amount
    return outgoing,incoming

def budget_defaults(s, team):
    ledger = s['finance'][team]
    baseline = 180000 if expectation(team) == 3 else 90000
    return {
        'transfer_budget': int(max(0,ledger['cash']-ledger.get('debt',0)*.6)*.52),
        'wage_budget': max(24000, int(baseline * 17 / 34 * .88 + max(0,ledger['cash']-ledger.get('debt',0)) / 170), payroll(s, team)),
        'wages_paid': 0, 'operating_paid': 0, 'fees_paid': 0, 'fees_received': 0, 'signing_paid': 0,
    }

def allocate(s):
    for team in TEAMS:
        ledger=s['finance'][team]
        ledger.update(budget_defaults(s,team))
        ledger.update(dict.fromkeys(FLOW,0))
        if s.get('economy_model')==2:ledger['commercial']=0
        if s.get('economy_model'):
            from ekonomi import constrain_budget
            constrain_budget(s,team)

def can_pay(s, team, fee, signing, wage, previous_wage=0, payments=1):
    ledger = s['finance'][team]
    reserved,_=commitments(s,team)
    upfront=fee-2*(fee//3) if payments==3 else fee
    if not (fee+signing<=ledger['transfer_budget'] and upfront+signing<=ledger['cash']-reserved
            and payroll(s,team)+wage-previous_wage<=ledger['wage_budget']):
        return False
    if payments==3:
        from ekonomi import can_commit
        return can_commit(s,team,fee+signing,wage-previous_wage,cash_due=upfront+signing+reserved)
    if s.get('economy_model') and not (team==s['club'] and s['employed']):
        from ekonomi import can_commit
        return can_commit(s,team,fee+signing,wage-previous_wage)
    return True

def record_fee(s,buyer,seller,paid):
    settle_transfer(s,buyer,seller,paid)
    s['finance'][buyer]['fees_paid']+=paid
    if seller:
        s['finance'][seller]['transfer_budget']+=int(paid*.75)
        s['finance'][seller]['fees_received']+=paid


def book_deal(s, buyer, seller, fee, signing, payments=1):
    if payments==3:
        deferred=fee//3
        record_fee(s,buyer,seller,fee-2*deferred)
        for delay in (4,8):
            s.setdefault('transfer_payments',[]).append([s['year'],s['week']+delay,buyer,seller,deferred])
    else:
        record_fee(s,buyer,seller,fee)
    ledger = s['finance'][buyer]
    ledger['cash'] -= signing
    ledger['transfer_budget'] -= fee + signing
    ledger['signing_paid'] += signing


def pay_due_transfers(s):
    rows=s.get('transfer_payments')
    if not rows:
        return
    future=[]
    for year,week,buyer,seller,amount in rows:
        if (year,week)<=(s['year'],s['week']):
            record_fee(s,buyer,seller,amount)
        else:
            future.append([year,week,buyer,seller,amount])
    if future:s['transfer_payments']=future
    else:s.pop('transfer_payments')

def operating(s,team):
    ledger=s['finance'][team]
    season,recurring,fixed=operating_plan(s,team)
    if s['week']==1:flow(ledger,'season_tickets',season)
    for key,amount in recurring.items():flow(ledger,key,amount)
    from personel import weekly_cost
    expenses={'staff':weekly_cost(s,team),**fixed}
    for key,amount in expenses.items():
        flow(ledger,key,amount,expense=True)
    ledger['operating_paid']+=sum(expenses.values())
    service(s,team)


def operating_plan(s,team):
    ledger=s['finance'][team]
    scale=cycle(s['year'])
    rep=s['club_reputation'][team]
    seats=capacity(team)
    season=scaled(s,'gate',seats*(4.2+rep*.085)*scale)
    recurring={'broadcast':scaled(s,'broadcast',(17500+rep*115)*scale),
               'sponsors':scaled(s,'sponsors',(2800+rep*114)*scale)}
    if s.get('economy_model')==2:
        relative=(sum(s['club_reputation'].values())/len(TEAMS)-55)/250
        recurring['broadcast']=int(recurring['broadcast']*(1+relative))
        played=max(1,s['week']-1)
        performance=min(.16,s['teams'][team]['p']/played*.055)
        recurring['commercial']=scaled(s,'commercial',(seats*.10+rep*21)*(1+performance)*scale)
    fixed={'academy':scaled(s,'facilities',2400+ledger['academy_level']*103),
           'maintenance':scaled(s,'facilities',4500+seats//4+ledger['facilities']*65),
           'interest':ledger['debt']*9//3400}
    return season,recurring,fixed
