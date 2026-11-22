"""Small, deduplicated inbox derived from committed career state."""
from oyuncu import age_at
from veritabani import player,roster


def record(s,before):
    club=s['club']
    year,week=s['year'],s['week']-1
    selected=[]
    for pid,now in s['weekly_feedback']['players'].items():
        old=before.get(pid,{})
        if now['injury'] and not old.get('injury',0):selected.append((9,'injury',pid,now['injury']))
        if old.get('injury') and not now['injury']:selected.append((7,'recovery',pid,0))
        if now['condition']<70:selected.append((5,'tired',pid,now['condition']))
        if now['form_change'] is not None and abs(now['form_change'])>=.7:
            selected.append((4,'form',pid,now['form']))
        if isinstance(now['age'],int) and now['age']<21 and now['minutes']>=75:
            selected.append((3,'youth',pid,now['minutes']))
        if s['fitness'][pid]['contract']<=year+1 and week in (17,30):
            selected.append((8,'contract',pid,s['fitness'][pid]['contract']))
    for offer in s['offers']:
        if offer['seller']==club and offer['status']=='open' and (offer['year'],offer['week'])==(year,week):
            selected.append((8,'transfer',offer['pid'],offer['buyer']))
    for row in s['manager_state']['applications']:
        if row['status']=='offered' and row['expires']-2==year*34+s['week']:
            selected.append((8,'job',row['team'],row['expires']))
    next_fixture=next((row for row in s['schedule'] if row['week']==s['week']
                      and club in (row['home'],row['away'])),None)
    if next_fixture:
        rival=next_fixture['away'] if next_fixture['home']==club else next_fixture['home']
        selected.append((1,'fixture',rival,s['board_targets'][club]))
    history=s.setdefault('inbox',[])
    recent={(kind,subject) for entry in history[-2:] if entry['year']==year and entry['club']==club
            for _,kind,subject,_ in entry['items'] if kind not in ('fixture','job')}
    seen=set(recent)
    items=[]
    for priority,kind,subject,value in sorted(selected,key=lambda row:(-row[0],row[1],row[2])):
        if (kind,subject) not in seen:
            seen.add((kind,subject))
            items.append([priority,kind,subject,value])
        if len(items)>=7:break
    if history and (history[-1]['year'],history[-1]['week'])==(year,week):return
    history.append(dict(year=year,week=week,club=club,items=items))
    del history[:-12]


def cohorts(s):
    result={'U18':[],'U20':[],'Senior':[]}
    for p in roster(s['club'],s['year'],s):
        age=age_at(p,s['year'],s['week'])
        category='U18' if isinstance(age,int) and age<18 else 'U20' if isinstance(age,int) and age<20 else 'Senior'
        result[category].append(p)
    return result
