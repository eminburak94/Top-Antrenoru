"""Transfer offers, counters and settlement."""
from donem import scaled
from finans import book_deal, can_pay
from oyuncu import ability
from sozlesme import asking_terms, player_accepts, set_contract
from veritabani import P, TEAMS, available, register, roster, player, all_players
from yarisma import window

def value(s,p):
    return scaled(s,'transfer',ability(s,p) ** 3 * 350) if p['id'] in s['owners'] else 0

def asking_fee(s,p):
    seller = s['owners'].get(p['id'])
    if seller is None:
        return 0
    from oyuncu import state
    listed=s['sale_status'].get(p['id'])=='listed'
    discount=.52 if listed else .58 if state(s,p)['contract']<=s['year']+1 else .88
    return round(value(s,p)*discount)

def selling_ready(s,p):
    seller = s['owners'].get(p['id'])
    if seller is None or s['sale_status'].get(p['id'])=='blocked':
        return False
    squad=roster(seller,s['year'],s)
    return len(squad)>16 and (p['pos']!='GK' or sum(q['pos']=='GK' for q in squad)>1)

def deal(s,pid,buyer,fee,years,wage,signing,role='Rotation',seller_consent=False):
    p = player(s,pid)
    if p is None or buyer not in TEAMS or not window(s) or type(fee) is not int or fee < 0:
        return False,'unavailable'
    seller = s['owners'].get(pid)
    if seller == buyer or pid in s['retired'] or (seller is None and not available(s,p)):
        return False,'unavailable'
    if seller and (not selling_ready(s,p) or (not seller_consent and fee < asking_fee(s,p))):
        return False,'seller'
    if seller is None and fee:
        return False,'fee'
    if not player_accepts(s,p,buyer,years,wage,signing,role):
        return False,'player'
    squad = roster(buyer,s['year'],s)
    if len(squad) >= 30 or not can_pay(s,buyer,fee,signing,wage):
        return False,'budget'
    numbers = s.setdefault('numbers',{})
    used = {numbers.get(q['id'],q['number']) for q in squad}
    number = next((n for n in range(1,100) if n not in used),None)
    if number is None:
        return False,'unavailable'
    book_deal(s,buyer,seller,fee,signing)
    register(s,pid,buyer)
    s['released'].pop(pid,None)
    s['sale_status'].pop(pid,None)
    numbers[pid] = number
    set_contract(s,p,years,wage,role)
    s['transfers'].append([s['year'],p['name'],seller or 'Serbest / Free',buyer,fee])
    s['contract_events'].append([s['year'],'signed',pid,buyer])
    s['news'].append([s['week'],'Transfer',f"{p['name']} → {buyer} | ${fee:,}"])
    return True,'accepted'

def transfer(s,pid,buyer):
    p = player(s,pid)
    if p is None or buyer not in TEAMS:
        return False
    terms = asking_terms(s,p,buyer)
    terms.update(wage=round(terms['wage']*1.35),signing=0)
    return deal(s,pid,buyer,value(s,p),**terms)[0]

def set_sale_status(s,pid,mode):
    if not s['employed'] or s['owners'].get(pid)!=s['club'] or mode not in ('listed','blocked','normal'):
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
    if not can_pay(s,buyer,fee,terms['signing'],terms['wage']):
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
        return False,'buyer'
    ok, reason = deal(s,offer['pid'],offer['buyer'],amount,offer['years'],offer['wage'],
                      offer['signing'],offer['role'],seller_consent=True)
    if ok:
        offer['status']='accepted'
        if s.get('match_model',0)==4:
            for other in s['offers']:
                if other['pid']==offer['pid'] and other['status']=='open':
                    other['status']='expired'
    return ok,reason
