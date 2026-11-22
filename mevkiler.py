"""Position templates and estimated fit. Catalog position evidence stays unchanged."""
LAYOUTS = {
    '4-4-2': ('GK','RB','CB','CB','LB','RM','CM','CM','LM','ST','ST'),
    '4-3-3': ('GK','RB','CB','CB','LB','DM','CM','CM','RW','ST','LW'),
    '4-2-3-1': ('GK','RB','CB','CB','LB','DM','DM','RW','AM','LW','ST'),
    '4-1-4-1': ('GK','RB','CB','CB','LB','DM','RM','CM','CM','LM','ST'),
    '3-5-2': ('GK','CB','CB','CB','RWB','DM','CM','CM','LWB','ST','ST'),
    '5-3-2': ('GK','RWB','CB','CB','CB','LWB','CM','DM','CM','ST','ST'),
}
GROUP = {**dict.fromkeys(('RB','LB','CB','SW','RWB','LWB'),'D'),
         **dict.fromkeys(('DM','RM','CM','LM','RW','AM','LW'),'M'),
         **dict.fromkeys(('CF','ST','SS'),'F'),'GK':'GK'}
NEAR = {
    'CB': ('SW','RB','LB','DM'), 'SW': ('CB',),
    'RB': ('RWB','CB','RM'), 'LB': ('LWB','CB','LM'),
    'RWB': ('RB','RM','RW'), 'LWB': ('LB','LM','LW'),
    'DM': ('CM','CB'), 'CM': ('DM','AM'), 'AM': ('CM','SS','CF'),
    'RM': ('RW','RWB'), 'LM': ('LW','LWB'),
    'RW': ('RM','RWB','CF'), 'LW': ('LM','LWB','CF'),
    'ST': ('CF','SS'), 'CF': ('ST','SS'), 'SS': ('CF','AM','ST'),
}
SKILLS_BY_POSITION = {
    'GK': ('Handling','Reflexes','One on ones','Aerial reach'),
    'CB': ('Marking','Heading','Positioning','Strength'),
    'SW': ('Positioning','Anticipation','Decisions','Passing'),
    'DM': ('Tackling','Positioning','Passing','Decisions'),
    'CM': ('Passing','Teamwork','Vision','Decisions'),
    'AM': ('Vision','Dribbling','Passing','First touch'),
    'ST': ('Finishing','Anticipation','Heading','Composure'),
}
for code in ('RB','LB','RWB','LWB'):
    SKILLS_BY_POSITION[code]=('Tackling','Pace','Crossing','Positioning')
for code in ('RM','LM','RW','LW'):
    SKILLS_BY_POSITION[code]=('Pace','Dribbling','Crossing','First touch')


def group_for(code):
    return GROUP.get(code, code)


def fit_level(player, position):
    primary = player['pos']
    secondary = player.get('alternate_positions', ())
    if position==primary:
        return 4
    if position in secondary:
        return 3
    if group_for(position)=='GK' or primary=='GK':
        return 0
    if primary==group_for(position):
        return 2
    if any(code in NEAR.get(position, ()) for code in (primary,*secondary)):
        return 2
    if group_for(primary)==group_for(position):
        return 1
    return 0


def fit_factor(player, position):
    level=fit_level(player,position)
    if level==0 and (position=='GK' or player['pos']=='GK'):
        return .64
    return (.78,.87,.94,.98,1.)[level]

POSITION_NAMES = {
    'GK': ('Kaleci','Goalkeeper'), 'SW': ('Libero','Sweeper'),
    'RB': ('Sağ bek','Right back'), 'LB': ('Sol bek','Left back'),
    'CB': ('Stoper','Centre back'), 'RWB': ('Sağ kanat bek','Right wing-back'),
    'LWB': ('Sol kanat bek','Left wing-back'), 'DM': ('Defansif orta saha','Defensive midfield'),
    'RM': ('Sağ orta saha','Right midfield'), 'LM': ('Sol orta saha','Left midfield'),
    'CM': ('Merkez orta saha','Central midfield'), 'RW': ('Sağ hücum kanadı','Right wing'),
    'LW': ('Sol hücum kanadı','Left wing'), 'AM': ('Ofansif orta saha','Attacking midfield'),
    'CF': ('Forvet','Centre forward'), 'ST': ('Santrfor','Striker'), 'SS': ('İkinci forvet','Second striker'),
}
FIT_NAMES = (('Mevki dışı','Out of position'),('Grup içi tahmin','Group estimate'),
             ('Yakın mevki / tahmin','Related position / estimated'),
             ('Katalog ikinci mevki','Catalog secondary position'),('Katalog ana mevki','Catalog primary position'))


def label(code,lang):
    return POSITION_NAMES[code][lang=='EN']


def coordinates(roles):
    bands={'GK':0,'CB':1,'SW':1,'RB':1,'LB':1,'RWB':1,'LWB':1,
           'DM':2,'CM':3,'RM':3,'LM':3,'AM':4,'RW':4,'LW':4,'ST':5}
    if roles[1]=='CB' and 'RWB' in roles:
        bands.update(RWB=2,LWB=2)
    for i,role in enumerate(roles):
        x=bands[role]
        peers=[j for j,r in enumerate(roles) if bands[r]==x]
        order=sorted(peers,key=lambda j:(roles[j].startswith('R')-roles[j].startswith('L'),j))
        index=order.index(i)
        yield (95+148*x,(index+1)*340/(len(order)+1))
