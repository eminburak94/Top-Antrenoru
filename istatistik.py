"""Season statistics grouped by stable player and representing club."""
FIELDS=('apps','starts','minutes','goals','assists','rating_sum','rated','motm','yellow','red','saves','clean')
SHOT_EVENTS=frozenset(('wide','saved','on_target','goal','blocked'))

def accumulate(stats,result):
    by_player={}
    for side,team in enumerate((result['home'],result['away'])):
        for pid in result.get('participants', [[],[]])[side]:
            row=stats.setdefault(pid,{}).setdefault(team,dict.fromkeys(FIELDS,0))
            by_player[pid]=row
            row['apps']+=1
            row['minutes']+=result['minutes'][pid]
            row['starts']+=pid in result.get('starters',[[],[]])[side]
            mark=result.get('ratings',{}).get(pid)
            if mark is not None:
                row['rating_sum']+=round(mark*10)
                row['rated']+=1
        conceded=(result['y'],result['x'])[side]
        if not conceded:
            for pid in result.get('keepers',[[],[]])[side]:
                if result['minutes'].get(pid)==90 and pid in by_player:
                    by_player[pid]['clean']+=1
    for _,_,pid in result['events']:
        if pid in by_player:
            by_player[pid]['goals']+=1
    for _,_,pid,kind,other in result.get('play',[]):
        if kind=='saved' and other in by_player:
            by_player[other]['saves']+=1
        elif kind in ('yellow','red') and pid in by_player:
            by_player[pid][kind]+=1
    for _,_,pid,_ in result.get('assists',[]):
        if pid in by_player:
            by_player[pid]['assists']+=1
    ratings=result.get('ratings',{})
    if ratings and by_player:
        best=max(by_player,key=lambda pid:(ratings.get(pid,0),result['minutes'][pid],pid))
        by_player[best]['motm']+=1

def combine(records):
    return {field:sum(row.get(field,0) for row in records) for field in FIELDS}
