"""Seasonal admissions for clubs whose real pool cannot cover positional needs."""
from datetime import date,timedelta
from oyuncu import GROUPS,state
from veritabani import TEAMS, register, roster
from yerellestirme import COUNTRIES

MINIMUM={'GK':2,'D':6,'M':7,'F':4}
FIRST=('Deniz','Ege','Aras','Baran','Ali','Ömer','Tuna','Kerem','Doruk','Umut','Eren','Emir','Kaan','Bora','Yiğit','Mert')
LAST=('Akyel','Günay','Yıldız','Koşar','Çakır','Sönmez','Keskin','Karaca','Gökmen','Ünal','Özer','Tekin','Aydın','Alkan','Ergin','Orhan')
ROLES={'GK':('GK',),'D':('CB','LB','RB'),'M':('CM','DM','AM','RM','LM'),'F':('CF','ST','SS')}

def replenish(s,rng):
    for team in TEAMS:
        squad=roster(team,s['year'],s)
        quality=.55+s['club_reputation'][team]/200+s['finance'][team]['academy_level']/220
        for role,minimum in MINIMUM.items():
            missing=minimum-sum(p['pos'] in GROUPS[role] for p in squad)
            for _ in range(max(0,missing)):
                index=len(s['generated'])+1
                pid=f'y{s["year"]}-{index}'
                country=rng.choices(('TR','DE','BG','AZ'),(94,2,2,2))[0]
                age=rng.randint(16,19)
                birth=date(s['year']-age,8,1)-timedelta(days=rng.randrange(365))
                rating=round(max(5,min(12,rng.gauss(7.8+quality*.55,1.25))),1)
                base=round(max(rating*10+12,min(185,rng.gauss(115+quality*13,15))))
                if country=='TR':
                    name=f'{rng.choice(FIRST)} {rng.choice(LAST)}'
                else:
                    names={'DE':('Lukas','Jonas','Felix'),'BG':('Ivan','Petar','Nikolay'),'AZ':('Elvin','Tural','Rauf')}
                    last={'DE':('Keller','Falk','Brandt'),'BG':('Petrov','Ivanov','Iliev'),'AZ':('Aliyev','Ismayilov','Huseynov')}
                    name=f'{rng.choice(names[country])} {rng.choice(last[country])}'
                name=f'{name} ({index})'
                numbers={s.get('numbers',{}).get(q['id'],q['number']) for q in roster(team,s['year'],s)}
                p=dict(id=pid,name=name,full_name=name,dob=birth.isoformat(),kind='fictional',
                       pos=rng.choice(ROLES[role]),rating=rating,pa_base=base,club=team,
                       number=next(n for n in range(1,100) if n not in numbers),nation=COUNTRIES[country][1],
                       citizenships=[dict(country_id=country,valid_from=None,raw=COUNTRIES[country][1])],
                       professionalism=round(rng.uniform(.82,1.18),2),
                       personality_drive=round(rng.uniform(.87,1.13),2))
                s['generated'][pid]=p
                register(s,pid,team)
                state(s,p).update(wage=rng.randint(350,700),contract=s['year']+rng.randint(3,5),role='Rotation')
