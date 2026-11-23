"""Transfer offers, counters and settlement."""
from donem import scaled
from finans import book_deal, can_pay
from mevkiler import fit_level, group_for
from oyuncu import ability, age_at, state
from sozlesme import asking_terms, player_accepts, set_contract
from veritabani import TEAMS, available, register, roster, player
from yarisma import TRANSFER_PERIODS, window

def value(s,p):
    if p['id'] not in s['owners']:
        return 0
    base=ability(s,p)
    if not s.get('transfer_model'):
        return scaled(s,'transfer',base ** 3 * 350)
    age=age_at(p,s['year'],s['week'])
    age=age if isinstance(age,int) else 27
    upside=max(0,state(s,p)['potential']-base)
    factor=1+min(.28,upside*.055) if age<=24 else 1-min(.35,max(0,age-29)*.05)
    return scaled(s,'transfer',base ** 3 * 350 * factor * (1+performance(s,p['id'])*.09))


def performance(s,pid):
    rows=s['season_stats'].get(pid)
    if not rows and s['history']:
        rows=s['history'][-1].get('player_stats',{}).get(pid)
    rows=(rows or {}).values()
    games=sum(row['rated'] for row in rows)
    if games<5:return 0
    return min(2,max(-2,sum(row['rating_sum'] for row in rows)/(10*games)-6.5))

def asking_fee(s,p):
    seller = s['owners'].get(p['id'])
    if seller is None:
        return 0
    listed=s['sale_status'].get(p['id'])=='listed'
    discount=.52 if listed else .58 if state(s,p)['contract']<=s['year']+1 else .88
    if s.get('transfer_model') and not listed:
        ledger=s['finance'][seller]
        if ledger['cash']<0 or ledger['debt']>max(0,ledger['cash']):discount*=.85
        elif state(s,p)['contract']>=s['year']+3:discount*=1.08
    return round(value(s,p)*discount)

def selling_ready(s,p):
    seller = s['owners'].get(p['id'])
    if seller is None or p['id'] in s.get('loans',{}) or s['sale_status'].get(p['id'])=='blocked':
        return False
    squad=roster(seller,s['year'],s)
    return len(squad)>16 and (p['pos']!='GK' or sum(q['pos']=='GK' for q in squad)>1)

def room(s,team):
    return (len(roster(team,s['year'],s))+
            sum(loan['parent']==team for loan in s.get('loans',{}).values()))<30


def shirt_number(s,buyer):
    numbers=s.get('numbers',{})
    used={numbers.get(q['id'],q['number']) for q in roster(buyer,s['year'],s)}
    return next((n for n in range(1,100) if n not in used),None)


def purchase_offer(s,pid,buyer,fee,years,wage,signing,role='Rotation',payments=1,rounds=0):
    p=player(s,pid)
    if not p or not window(s) or buyer not in TEAMS or type(fee) is not int or fee<0:
        return False,'unavailable',None
    seller=s['owners'].get(pid)
    if seller and seller!=buyer and selling_ready(s,p):
        start=next(first for first,last in TRANSFER_PERIODS if first<=s['week']<=last)
        withdrawal=[s['year'],start,buyer,seller]
        if s.get('transfer_withdrawals',{}).get(pid)==withdrawal:
            return False,'withdrawn',None
        ask=asking_fee(s,p)
        premium=round(ask*.05) if payments==3 else 0
        quote=ask+premium
        floor=round(ask*(.84 if s['sale_status'].get(pid)=='listed' else .92))+premium
        if fee<floor:
            if fee<ask*.48 or rounds>=2:
                s.setdefault('transfer_withdrawals',{})[pid]=withdrawal
                return False,'withdrawn',None
            return False,'counter',max(floor,round((fee+quote)*.5))
    ok,reason=deal(s,pid,buyer,fee,years,wage,signing,role,seller_consent=True,payments=payments)
    return ok,reason,None


def deal(s,pid,buyer,fee,years,wage,signing,role='Rotation',seller_consent=False,payments=1):
    p = player(s,pid)
    if p is None or buyer not in TEAMS or not window(s) or type(fee) is not int or fee < 0:
        return False,'unavailable'
    seller = s['owners'].get(pid)
    if type(payments) is not int or (payments!=1 and
            (payments!=3 or not s.get('transfer_model') or seller is None or fee<3)):
        return False,'fee'
    if seller == buyer or pid in s['retired'] or (seller is None and not available(s,p)):
        return False,'unavailable'
    if seller and (not selling_ready(s,p) or (not seller_consent and fee < asking_fee(s,p))):
        return False,'seller'
    if seller is None and fee:
        return False,'fee'
    if not player_accepts(s,p,buyer,years,wage,signing,role):
        return False,'player'
    if not room(s,buyer) or not can_pay(s,buyer,fee,signing,wage,payments=payments):
        return False,'budget'
    number = shirt_number(s,buyer)
    if number is None:
        return False,'unavailable'
    book_deal(s,buyer,seller,fee,signing,payments)
    register(s,pid,buyer)
    s['released'].pop(pid,None)
    s['sale_status'].pop(pid,None)
    s.setdefault('numbers',{})[pid] = number
    set_contract(s,p,years,wage,role)
    s['transfers'].append([s['year'],p['name'],seller or 'Serbest / Free',buyer,fee])
    s['contract_events'].append([s['year'],'signed',pid,buyer])
    source=f'{seller} → ' if seller and s.get('transfer_model') else ''
    message=f"{p['name']} | {source}{buyer} | ${fee:,}" if source else f"{p['name']} → {buyer} | ${fee:,}"
    s['news'].append([s['week'],'Transfer',message])
    return True,'accepted'


def loan_ready(s,p):
    if not s.get('transfer_model') or not selling_ready(s,p) or state(s,p)['contract']<=s['year']:
        return False
    owner=s['owners'][p['id']]
    group=group_for(p['pos'])
    cover=sum(group_for(q['pos'])==group and not state(s,q)['injury'] for q in roster(owner,s['year'],s)
              if q['id']!=p['id'])
    return cover>={'GK':2,'D':4,'M':4,'F':2}[group]


def loan_fee(s,p):
    weeks=35-s['week']
    return max(1,round(value(s,p)*.05*weeks/34))


def loan_deal(s,pid,buyer,fee,share,seller_consent=False):
    p=player(s,pid)
    parent=s['owners'].get(pid)
    if not p or buyer not in TEAMS or buyer==parent or not window(s) or not loan_ready(s,p):
        return False,'unavailable'
    if type(fee) is not int or fee<0 or type(share) is not int or share not in (25,50,75,100):
        return False,'fee'
    if not seller_consent and (fee<loan_fee(s,p) or share<50):
        return False,'seller'
    peers=[q for q in roster(buyer,s['year'],s) if not state(s,q)['injury']
           and fit_level(q,p['pos'])>=2 and ability(s,q)>ability(s,p)+.5]
    if len(peers)>=2 or s['club_reputation'][parent]-s['club_reputation'][buyer]>35 and peers:
        return False,'player'
    wage=state(s,p)['wage']*share//100
    number=shirt_number(s,buyer)
    if number is None or not room(s,buyer) or not can_pay(s,buyer,fee,0,wage):
        return False,'budget'
    book_deal(s,buyer,parent,fee,0)
    s.setdefault('loans',{})[pid]=dict(parent=parent,borrower=buyer,share=share)
    s['sale_status'].pop(pid,None)
    register(s,pid,buyer)
    s.setdefault('numbers',{})[pid]=number
    s['news'].append([s['week'],'Kiralama / Loan',f"{p['name']} | {parent} → {buyer} | ${fee:,}"])
    return True,'accepted'


def return_loans(s):
    for pid,loan in s.pop('loans',{}).items():
        parent=loan['parent']
        p=player(s,pid)
        number=shirt_number(s,parent)
        register(s,pid,parent)
        s.setdefault('numbers',{})[pid]=number
        s['news'].append([34,'Kiralama bitti / Loan ended',f"{p['name']} → {parent}"])

def transfer(s,pid,buyer):
    p = player(s,pid)
    if p is None or buyer not in TEAMS:
        return False
    terms = asking_terms(s,p,buyer)
    terms.update(wage=round(terms['wage']*1.35),signing=0)
    return deal(s,pid,buyer,value(s,p),**terms)[0]

def set_sale_status(s,pid,mode):
    modes=('listed','blocked','normal','loan') if s.get('transfer_model') else ('listed','blocked','normal')
    if not s['employed'] or s['owners'].get(pid)!=s['club'] or mode not in modes or pid in s.get('loans',{}):
        return False
    if mode=='normal':
        s['sale_status'].pop(pid,None)
    else:
        s['sale_status'][pid]=mode
    if mode=='blocked':
        for offer in s['offers']:
            if offer['pid']==pid and offer['status']=='open':
                offer['status']='rejected'
    return True

def reject_all(s):
    count=0
    for index,offer in enumerate(s['offers']):
        if offer['status']=='open' and answer_offer(s,index,'reject')[0]:
            count+=1
    return count

def add_offer(s,p,buyer,fee,terms):
    if s['sale_status'].get(p['id'])=='blocked':
        return False
    for offer in reversed(s['offers']):
        if (offer['pid']==p['id'] and offer['buyer']==buyer and offer['status'] in ('expired','rejected')
                and (s['year']-offer['year'])*34+s['week']-offer['week']<20
                and fee<=offer['fee']*1.12):
            return False
    if any(o['pid']==p['id'] and o['buyer']==buyer and o['status']=='open' for o in s['offers']):
        return False
    wage=terms['wage']*terms['share']//100 if terms.get('kind')=='loan' else terms['wage']
    if not can_pay(s,buyer,fee,terms['signing'],wage):
        return False
    s['offers'].append(dict(pid=p['id'],buyer=buyer,seller=s['owners'][p['id']],
                            fee=fee,year=s['year'],week=s['week'],status='open',**terms))
    return True

def counter_limit(s,offer):
    if s.get('match_model',0)!=4:
        return round(offer['fee']*1.22)
    from mevkiler import fit_level
    from piyasa_ai import assess
    buyer=offer['buyer']
    p=player(s,offer['pid'])
    needs=assess(s,buyer,roster(buyer,s['year'],s))
    priority=max((row[0] for row in needs if fit_level(p,row[1])>=2),default=0)
    premium=.08+min(12,priority)*.015
    return round(offer['fee']*(1+premium))

def answer_offer(s,index,answer,fee=None):
    offer = s['offers'][index]
    if not s['employed'] or s['club'] != offer['seller'] or offer['status'] != 'open' or not window(s) or offer['year']!=s['year'] or s['week']-offer['week']>2:
        return False,'unavailable'
    if s['owners'].get(offer['pid']) != offer['seller']:
        return False,'unavailable'
    if answer == 'reject':
        offer['status']='rejected'
        return True,'rejected'
    if answer not in ('accept','counter'):
        return False,'unavailable'
    amount = offer['fee'] if answer == 'accept' else fee
    if type(amount) is not int or amount < 0:
        return False,'fee'
    if answer=='counter' and amount>counter_limit(s,offer):
        if s.get('transfer_model') and amount>round(counter_limit(s,offer)*1.15):
            offer['status']='rejected'
            return False,'withdrawn'
        return False,'buyer'
    if offer.get('kind')=='loan':
        ok,reason=loan_deal(s,offer['pid'],offer['buyer'],amount,offer['share'],seller_consent=True)
    else:
        ok, reason = deal(s,offer['pid'],offer['buyer'],amount,offer['years'],offer['wage'],
                      offer['signing'],offer['role'],seller_consent=True)
    if ok:
        offer['status']='accepted'
        if s.get('match_model',0)==4:
            for other in s['offers']:
                if other['pid']==offer['pid'] and other['status']=='open':
                    other['status']='expired'
    return ok,reason
