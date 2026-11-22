import random

def age_at(p, year, week):
    from datetime import date, timedelta
    try:
        birth = date.fromisoformat(p.get('dob', ''))
        today = date(year, 8, 1) + timedelta(weeks=max(0, min(33, week - 1)))
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except (ValueError, TypeError):
        return '?'

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))

def ability(s, p):
    return s.get('fitness', {}).get(p['id'], {}).get('ability', p['rating'])

def state(s, p):
    z = s.setdefault('fitness', {}).setdefault(
        p['id'], dict(condition=100, morale=70, form=6.5, injury=0, apps=0),
    )
    z.setdefault('ability', float(p['rating']))
    if 'pa_version' not in z:
        from yerellestirme import is_domestic
        rng=random.Random('pa:'+p['id'])
        base=z.get('potential',p.get('pa_base',0)/10) or min(20,p['rating']+random.Random(p['id']).uniform(1,4))
        bonus=rng.randint(1,5) if p.get('kind')=='fictional' else rng.randint(5,10)
        z['potential']=min(200,round(base*10)+(bonus if is_domestic(p) else 0))/10
        z['pa_version']=1
    z.setdefault('professionalism',p.get('professionalism',1.0))
    z.setdefault('personality_drive',p.get('personality_drive',1.0))
    z.setdefault('injury_matches',0)
    z.setdefault('wage', int(400 + p['rating'] ** 2 * 14))
    if 'contract' not in z:
        z['contract']=2002+int(p['id'])%3 if p['id'].isdecimal() else s['year']+3
    z.setdefault('cards', 0)
    z.setdefault('ban', 0)
    return z

def power(s, p):
    z = state(s, p)
    return (z['ability'] * (.8 + .2 * z['condition'] / 100) +
            (z['morale'] - 70) * .009 + (z['form'] - 6.5) * .15)

GROUPS = {
    'GK': {'GK'}, 'D': {'D', 'CB', 'RB', 'LB'},
    'M': {'M', 'CM', 'DM', 'AM', 'RM', 'LM', 'RW', 'LW'},
    'F': {'F', 'CF', 'ST', 'SS'},
}

# The versioned profile adjusts estimated attributes; supplied historical ratings stay separate.
GOALKEEPING = {'Handling','Reflexes','One on ones','Kicking','Aerial reach'}
OFFENSIVE = {'Finishing','Dribbling','Crossing','Long shots','Set pieces'}
DEFENSIVE = {'Tackling','Marking','Positioning'}


def calibrated_attribute(name,position,ability,offset):
    if position=='GK':
        if name in GOALKEEPING or name=='Positioning':
            return offset
        if name in OFFENSIVE or name in {'Passing','Vision','Marking','Tackling'}:
            return 1.20*offset-.26*max(0,ability-11)
    if position!='GK' and name in GOALKEEPING:
        return 1.10*offset-.30*max(0,ability-10)
    if ((position in GROUPS['F'] and name in DEFENSIVE) or
            (position in GROUPS['D'] and name in {'Finishing','Long shots'})):
        return 1.25*offset-.25*max(0,ability-11)
    return 1.15*offset


def attributes(s,p):
 z=state(s,p);rng=random.Random(p['id']);pos=p['pos'];a=z['ability'];out={}
 for name in ('Finishing','Passing','Technique','Dribbling','Tackling','Marking','Heading','Crossing','First touch','Long shots','Set pieces','Handling','Decisions','Vision','Positioning','Work rate','Determination','Composure','Anticipation','Teamwork','Concentration','Flair','Leadership','Bravery','Pace','Acceleration','Stamina','Strength','Agility','Balance','Jumping','Reflexes','One on ones','Kicking','Aerial reach','Natural fitness'):
  bonus=3 if (pos=='GK' and name in ('Handling','Reflexes','One on ones','Kicking','Aerial reach')) or (pos in GROUPS['D'] and name in ('Tackling','Marking','Positioning')) or (pos in GROUPS['F'] and name in ('Finishing','Composure')) else -5 if name in ('Handling','Reflexes','One on ones','Kicking','Aerial reach') and pos!='GK' else 0
  if s.get('attribute_profile',1)>=2:
   if pos=='GK' and name in ('Finishing','Tackling','Marking','Vision','Passing','Crossing','Long shots','Dribbling'):
    bonus-=5
   elif pos in GROUPS['F'] and name in ('Tackling','Marking'):
    bonus-=5
   elif pos in GROUPS['D'] and name in ('Finishing','Long shots'):
    bonus-=4
  offset=rng.uniform(-3,3)
  if s.get('attribute_profile')==3:
   offset=calibrated_attribute(name,pos,a,offset)
  out[name]=round(clamp(a+offset+bonus,1,20))
 return out

def develop(s, p, rng, active=True, minutes=0, facility=1.):
    z = state(s,p)
    age = age_at(p,s['year']+1,1)
    old = z['ability']
    room = max(0,z['potential']-old)
    exposure = min(1,minutes/2200)
    training = min(.16,z.get('training_weeks',0)*.005)
    peak = 31 if p['pos']=='GK' else 28
    if isinstance(age,int) and age<=peak:
        youth = .58 if age<=22 else .32 if age<=26 else .11
        delta = youth*(.18+.82*exposure)*min(1,room/2)+training*min(1,room/3)
        if s.get('match_model') and 16<=age<=23:
            training_share=.65 if age<=17 else .50 if age<=20 else .35
            # Cap effective exposure for players physically struggling at senior level.
            readiness=min(1,.73+old/35)*max(.65,z['condition']/100)
            practice=min(1,.30+z.get('training_weeks',0)/35) if active else .12
            input_quality=training_share*practice+(1-training_share)*exposure*readiness
            delta=youth*(.12+.88*input_quality)*min(1,room/2)
        delta -= .14 if not active else 0
    elif isinstance(age,int):
        delta = -.27 - min(.82,.105*(age-peak)) - (.10 if not active else 0)
    else:
        delta = 0
    if delta>0:
        resilience=max(.62,1-z.get('injury_matches',0)*.025)
        delta*=z['professionalism']*z['personality_drive']*resilience*facility
    delta += rng.uniform(-.095,.095)
    ceiling = max(4,z['potential'] - .08)
    z['ability']=round(clamp(old+delta,4,ceiling),2)
    z.update(condition=100, injury=0, form=6.5, apps=0, minutes=0, training_weeks=0, injury_matches=0,
             morale=round(70+(z['morale']-70)*.45),cards=0,ban=0)

def prepare_player(s,p,team,fitness_bonus=None,programme=None):
    z = state(s, p)
    user_club = team == s['club'] and s['employed']
    if fitness_bonus is None or programme is None:
        from personel import effects, team_training
        if fitness_bonus is None:fitness_bonus=effects(s,team)[0]
        if programme is None:programme=team_training(s,team)
    z['condition'] = min(100,z['condition'] + fitness_bonus + (28 if user_club and programme=='Rest' else 23))
    z['morale'] += (70 - z['morale']) * .10
    age = age_at(p, s['year'], s['week'])
    if user_club:
        from antrenman import apply_plan, plan_for
        plan = plan_for(s,p,z,age)
        if plan:
            return apply_plan(z,*plan,age)
    if user_club and programme=='Development' and isinstance(age, int) and age < 25:
        z['training_weeks'] = z.get('training_weeks',0) + 1
        z['condition'] = max(40, z['condition'] - 4)
