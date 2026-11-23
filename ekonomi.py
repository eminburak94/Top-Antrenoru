"""Conservative cash forecasts for the v1 economy, in internal currency."""
from finans import capacity,commitments,cycle,payroll,operating_plan
from donem import scaled


def admin(s,team):
    return scaled(s,'operations',6200+s['club_reputation'][team]*65)


def projection(s,team):
    from personel import payroll as staff_payroll
    ledger=s['finance'][team]
    rep=s['club_reputation'][team]
    seats=capacity(team)
    scale=cycle(s['year'])
    weeks=max(0,35-s['week'])
    homes=sum(m['home']==team and m['week']>=s['week'] for m in s['schedule'])
    recurring=(17500+rep*115+2800+rep*114)*scale
    gate=seats*(.40+rep/180)*4.75*scale*.95
    tickets=seats*(4.2+rep*.085)*scale if s['week']==1 else 0
    if s.get('economy_model')==2:
        season,flows,fixed=operating_plan(s,team)
        recurring=sum(flows.values())
        gate=scaled(s,'gate',gate)
        tickets=season if s['week']==1 else 0
    income=int(weeks*recurring+homes*gate+tickets)
    staff=staff_payroll(s,team)
    wages=payroll(s,team)
    facilities=2400+ledger['academy_level']*103+4500+seats//4+ledger['facilities']*65
    interest=ledger['debt']*9//3400
    reserve=25000+rep*600
    if s.get('economy_model')==2:
        facilities=fixed['academy']+fixed['maintenance']
        reserve=scaled(s,'operations',reserve)
    operating=staff+wages+admin(s,team)+facilities+interest
    closing=ledger['cash']+income-operating*weeks-commitments(s,team)[0]
    # Annualized recurring sustainability, excluding prize money or player sales.
    annual=int(34*recurring+17*gate+(season if s.get('economy_model')==2 else seats*(4.2+rep*.085)*scale))
    # Forecast a modest committed debt-service buffer without deducting it from the ledger.
    debt_buffer=min(ledger['debt']//10,annual//12)
    wage_room=max(0,(annual-reserve-debt_buffer)//34-(staff+admin(s,team)+facilities+interest))
    return dict(weekly_income=int(recurring+gate/2), income=income, wages=wages, staff=staff,
                admin=admin(s,team), facilities=facilities, interest=interest, reserve=reserve,
                closing=closing-debt_buffer, debt_buffer=debt_buffer, wage_room=wage_room, weeks=weeks)


def can_commit(s,team,fee,wage_change,staff_change=0,forecast=None,cash_due=None):
    plan=projection(s,team) if forecast is None else forecast
    ledger=s['finance'][team]
    added=wage_change+staff_change
    if fee==0 and added<=0:
        return True
    if wage_change+plan['wages']+staff_change>plan['wage_room']:
        return False
    return (ledger['cash']-(fee if cash_due is None else cash_due)>=min(plan['reserve'],25000)
            and plan['closing']-fee-added*plan['weeks']>=plan['reserve'])


def constrain_budget(s,team):
    ledger=s['finance'][team]
    plan=projection(s,team)
    ledger['wage_budget']=min(ledger['wage_budget'],max(plan['wages'],plan['wage_room']))
    ledger['transfer_budget']=min(ledger['transfer_budget'],max(0,plan['closing']-plan['reserve']))


def crisis_sales(s):
    from veritabani import TEAMS,roster
    from oyuncu import state
    for team in TEAMS:
        if team==s['club'] and s['employed']:continue
        plan=projection(s,team)
        if s['finance'][team]['cash']>=0 and plan['closing']>=0:continue
        squad=roster(team,s['year'],s)
        # Keep a playable minimum and never advertise the only keeper.
        candidates=[p for p in squad if p['pos']!='GK']
        for p in sorted(candidates,key=lambda q:(-state(s,q)['wage'],q['id']))[:max(0,min(2,len(squad)-18))]:
            s['sale_status'][p['id']]='listed'
