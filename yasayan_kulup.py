"""Supporter reactions, press choices and evidence-based board reviews."""
from donem import scaled
from ekonomi import projection
from oyuncu import ability, clamp, state
from veritabani import TEAMS, roster
from yarisma import standings


ISTANBUL_RIVALS=frozenset(('GALATASARAY','FENERBAHÇE','BEŞİKTAŞ'))
PRESS_KINDS=('derby','poor','heavy','streak','transfer','transfer_reinforcement','transfer_cost',
             'transfer_exit','strong','promise_met','promise_missed',
             'board_warning','dismissed','recovery_met','recovery_missed','budget',
             'response_responsibility','response_protect','response_promise')


def setup(s):
    s['living_club']={'fans':{team:[50,0,0] for team in TEAMS},'board':{},'briefs':[]}
    begin_spell(s)


def begin_spell(s):
    club=s['club']
    life=s['living_club']
    life['board']=dict(club=club,form=[],sport=0,fiscal=0,risk=(100-s['confidence'])//3,
                       meeting=0,used_recovery=False)
    life.pop('match_review',None)
    for key in ('question','promise','recovery'):
        life.pop(key,None)


def strength_bonus(s,team):
    ledger=s['finance'][team]
    history=s['history']
    recent=0
    if history:
        previous=history[-1]['teams']
        rank=sorted(TEAMS,key=lambda t:(-previous[t]['p'],previous[t]['ga']-previous[t]['gf'],t)).index(team)+1
        recent=max(-.4,.8-rank*.07)
    backing=ledger['transfer_budget']/max(1,scaled(s,'transfer',2000000))
    strain=.5 if ledger['cash']<0 or ledger['debt']>max(0,ledger['cash']) else 0
    return (s['club_reputation'][team]-50)/30+recent+min(.55,backing*.3)-strain


def attendance(s,team):
    life=s.get('living_club')
    return .90+life['fans'][team][0]*.002 if life else 1


def fans(s,team,change):
    row=s['living_club']['fans'][team]
    previous=row[0]
    row[0]=clamp(previous+change,0,100)
    row[2]=row[0]-previous


def brief(s,kind,team,subject='',detail='',week=None):
    rows=s['living_club']['briefs']
    rows.append([s['year'],s['week'] if week is None else week,kind,team,subject,detail])
    del rows[:-30]


def question(s,kind,team,subject='',week=None):
    if not s['employed'] or s['club']!=team:
        return
    life=s['living_club']
    if pending_question(s) is None:
        life['question']=[s['year'],s['week'] if week is None else week,kind,team,subject]


def pending_question(s):
    row=s['living_club'].get('question')
    if row and s['employed'] and row[0]==s['year'] and row[3]==s['club'] and 0<=s['week']-row[1]<=2:
        return row
    return None


def transfer(s,p,buyer,seller,fee,loan=False):
    if not s.get('living_club'):
        return
    level=ability(s,p)
    starters=sorted((ability(s,q) for q in roster(buyer,s['year'],s)),reverse=True)[:11]
    first_team=level>=sum(starters)/max(1,len(starters))
    costly=fee>=scaled(s,'transfer',650000)
    notable=first_team or costly
    if not notable:
        return
    fans(s,buyer,1 if loan else 3 if first_team else 1)
    exit_concern=False
    if seller and not loan:
        best=sorted((ability(s,q) for q in roster(seller,s['year'],s)),reverse=True)[:11]
        if best and level>=sum(best)/len(best):
            fans(s,seller,-2)
            exit_concern=True
    if s['club'] in (buyer,seller) or costly:
        if exit_concern and s['club']==seller:
            brief(s,'transfer_exit',seller,p['name'],buyer)
        else:
            kind='transfer_reinforcement' if first_team else 'transfer_cost' if costly else 'transfer'
            brief(s,kind,buyer,p['name'],seller or '')
    if s['club'] in (buyer,seller):
        question(s,'transfer',s['club'],p['name'])


def update_support(s,team,opponent,goals,conceded):
    row=s['living_club']['fans'][team]
    sign=(goals>conceded)-(goals<conceded)
    run=row[1]
    row[1]=clamp(run+sign if sign and run*sign>0 else sign,-5,5)
    derby=team in ISTANBUL_RIVALS and opponent in ISTANBUL_RIVALS
    expectation=s['board_targets'][team]
    if sign:
        delta=sign*(2+int(derby)*3+int(abs(goals-conceded)>=3)+int(abs(row[1])>=3))
        if sign<0 and expectation<=4:delta-=1
        elif sign>0 and expectation>=12:delta+=1
    else:
        delta=-1 if expectation<=4 else 1 if s['club_reputation'][opponent]>=s['club_reputation'][team]+16 else 0
    # Keep ordinary results from pushing a long season permanently to either extreme.
    drift=round((row[0]-50)/16)
    if delta>0:delta=max(0,delta-drift)
    elif delta<0:delta=min(0,delta-drift)
    fans(s,team,delta)
    if s['employed'] and team==s['club']:
        kind=('derby' if derby else 'heavy' if conceded-goals>=3 else 'poor' if sign<0 else 'streak' if row[1]>=3
              else 'strong' if goals-conceded>=2 else None)
        if kind:
            brief(s,kind,team,opponent,f'{goals}–{conceded}',week=s['week']-1)
            if kind!='strong':
                question(s,'poor' if kind=='heavy' else kind,team,opponent,week=s['week']-1)
    return 3 if sign>0 else 1 if not sign else 0


def settle_promises(s,club,points):
    life=s['living_club']
    for key in ('promise','recovery'):
        pledge=life.get(key)
        if not pledge:
            continue
        pledge[0]-=1
        pledge[1]+=points
        if pledge[0]:
            continue
        success=pledge[1]>=5
        if key=='promise':
            fans(s,club,3 if success else -5)
            change=2 if success else -3
        else:
            change=4 if success else -5
        s['confidence']=clamp(s['confidence']+change,0,100)
        brief(s,key+('_met' if success else '_missed'),club,detail=str(pledge[1]),week=s['week']-1)
        del life[key]


def review(s,club,points,support=None):
    life=s['living_club']
    board=life['board']
    form=board['form']
    trust_before=s['confidence']
    previous=board['risk'] if form or board['risk'] else (100-trust_before)//3
    old_sport,old_fiscal=board['sport'],board['fiscal']
    form.append(points)
    del form[:-6]
    settle_promises(s,club,points)
    pledge_delta=s['confidence']-trust_before
    target=s['board_targets'][club]
    rank=standings(s).index(club)+1
    target_rate=1.75 if target<=4 else 1.4 if target<=9 else 1.1 if target<=13 else .9
    rate=sum(form)/len(form)
    under=len(form)>=4 and rank>target and rate<target_rate
    ledger=s['finance'][club]
    plan=projection(s,club)
    stress=ledger['cash']<0 or (plan['closing']<plan['reserve'] and plan['wages']>plan['wage_room'])
    board['sport']=min(8,board['sport']+1) if under else max(0,board['sport']-1)
    board['fiscal']=min(8,board['fiscal']+1) if stress else max(0,board['fiscal']-1)
    delta=2 if points==3 else -2 if under and points==0 else 0
    if under and board['sport']>=3:delta-=2
    if stress:delta-=2
    s['confidence']=clamp(s['confidence']+delta,0,100)
    board['risk']=clamp((100-s['confidence'])//3+board['sport']*7+board['fiscal']*8,0,100)
    if support is not None:
        opponent,goals,conceded,fan_before=support
        life['match_review']=dict(week=s['week']-1,opponent=opponent,goals=goals,conceded=conceded,
            trust=s['confidence']-trust_before,risk=board['risk']-previous,
            fans=life['fans'][club][0]-fan_before,sport=board['sport']-old_sport,
            fiscal=board['fiscal']-old_fiscal,under=under,stress=stress,
            pledge=pledge_delta)
    if previous<58<=board['risk']:
        brief(s,'board_warning',club,week=s['week']-1)
    played=s['week']-1
    if (played>=8 and played%4==0 and 'recovery' not in life
            and board['risk']>=72 and s['confidence']<=42):
        if board['fiscal']>=5 or board['sport']>=5:
            dismiss(s,'financial' if board['fiscal']>=5 else 'performance',s['week']-1)


def dismiss(s,reason,week):
    from is_piyasasi import leave
    brief(s,'dismissed',s['club'],detail=reason,week=week)
    leave(s,reason)


def record_week(s,results):
    for match in results:
        for home in (True,False):
            team,opponent=(match['home'],match['away']) if home else (match['away'],match['home'])
            goals,conceded=(match['x'],match['y']) if home else (match['y'],match['x'])
            fan_before=s['living_club']['fans'][team][0]
            points=update_support(s,team,opponent,goals,conceded)
            if s['employed'] and team==s['club']:
                review(s,team,points,(opponent,goals,conceded,fan_before))


def press_answer(s,choice):
    pending=pending_question(s)
    if choice not in ('responsibility','protect','promise') or pending is None:
        return False
    life=s['living_club']
    club=s['club']
    if choice=='promise':
        if 'promise' in life or s['week']>32:
            return False
        life['promise']=[3,0]
        fans(s,club,2)
    elif choice=='protect':
        for p in roster(club,s['year'],s):
            row=state(s,p)
            row['morale']=clamp(row['morale']+2,40,90)
        fans(s,club,-1)
    else:
        fans(s,club,1)
        s['confidence']=min(100,s['confidence']+1)
    brief(s,'response_'+choice,club,pending[4])
    del life['question']
    return True


def budget_shift(s):
    club=s['club']
    remaining=max(0,35-s['week'])
    if not remaining:
        return 0,0
    ledger=s['finance'][club]
    plan=projection(s,club)
    weekly=max(0,min(scaled(s,'wage',2000),ledger['transfer_budget']//remaining,
                     (plan['closing']-plan['reserve'])//remaining,plan['wage_room']-ledger['wage_budget']))
    return weekly,weekly*remaining


def meeting(s,choice):
    club=s['club']
    life=s['living_club']
    board=life['board']
    if not s['employed'] or (board['meeting'] and s['week']-board['meeting']<6):
        return False
    if choice=='budget':
        wage,cost=budget_shift(s)
        if not wage:
            return False
        ledger=s['finance'][club]
        ledger['wage_budget']+=wage
        ledger['transfer_budget']-=cost
        brief(s,'budget',club,detail=str(wage))
    elif choice=='recovery':
        if board['used_recovery'] or s['week']>32 or board['risk']<40:
            return False
        board['used_recovery']=True
        life['recovery']=[3,0]
    else:
        return False
    board['meeting']=s['week']
    return True


def season_review(s,rank,goal):
    board=s['living_club']['board']
    if board['fiscal']>=5 and board['risk']>=75:
        dismiss(s,'financial',34)
        return
    if rank>goal and s['board_misses']>=2 and board['risk']>=58:
        dismiss(s,'performance',34)


def new_season(s):
    life=s['living_club']
    for row in life['fans'].values():
        row[0]=round(50+(row[0]-50)*.75)
        row[1:]=[0,0]
    begin_spell(s)
