"""Individual plans and bounded calendar-month management reports."""
from datetime import date, timedelta

FOCUSES = ('general', 'technical', 'physical', 'tactical', 'recovery')
INTENSITIES = ('light', 'normal', 'intense')
MONTH_LIMIT = 12


def plan_for(s, p, z, age):
    explicit = s.get('individual_training', {}).get(p['id'])
    if explicit:
        return tuple(explicit)
    if not s.get('auto_training'):
        return None
    if z['injury'] or z['condition'] < 70:
        return 'recovery', 'normal'
    if isinstance(age,int) and age < 25 and recent_minutes(s,p['id']) == 0:
        return 'technical', 'normal'
    return ('general', 'normal') if isinstance(age,int) and age < 25 else None


def recent_minutes(s, pid):
    report = s.get('weekly_feedback', {})
    if (report.get('year'), report.get('week'), report.get('club')) != (
            s['year'], s['week'] - 1, s['club']):
        return None
    return report.get('players', {}).get(pid, {}).get('minutes')


def apply_plan(z, focus, intensity, age, match_minutes=None):
    level = INTENSITIES.index(intensity)
    before = z['condition']
    credit = 0
    if z['injury']:
        status = 'injured'
    elif focus == 'recovery':
        z['condition'] = min(100,before+(2,5,7)[level])
        status = 'recovered'
    else:
        load, weight = {'general': (3,.85), 'technical': (2,.9),
                        'physical': (5,1.), 'tactical': (2,.8)}[focus]
        # A full match makes an intensive session more costly. Training credit is unchanged.
        extra = 2 if level == 2 and match_minutes is not None and match_minutes >= 60 else 0
        z['condition'] = max(35,before-max(1,load+(-2,0,3)[level]+extra))
        if isinstance(age,int) and age < 25:
            credit = round(weight*(.65,.9,1.)[level],3)
            z['training_weeks'] = round(z.get('training_weeks',0)+credit,3)
        status = 'trained'
    return [focus,intensity,status,credit,z['condition']-before]


def record_month(s, report, observations):
    year, week, club = (report[k] for k in ('year','week','club'))
    day = date(year,8,1)+timedelta(weeks=week-1)
    month = day.strftime('%Y-%m')
    history = s.setdefault('monthly_training',[])
    if any((r['month'],r['club']) == (month,club) for r in history):
        return
    current = s.get('training_month')
    if current is None or (current['month'],current['club']) != (month,club):
        current = dict(month=month,club=club,last_week=0,weeks=0,players={})
        s['training_month'] = current
    if current['last_week'] >= week:
        return
    current['last_week'] = week
    current['weeks'] += 1
    for pid,weekly in report['players'].items():
        row = current['players'].setdefault(pid,dict(minutes=0,training=0,participation=0,
                    recovery=0,injured_weeks=0,plans={},weeks=0,team_weeks=0,
                    youth=isinstance(weekly['age'],int) and weekly['age']<25))
        row['weeks'] += 1
        row['minutes'] += weekly['minutes']
        obs = observations.get(pid)
        row['training'] = round(row['training']+(obs[3] if obs else weekly['training'] or 0),3)
        if obs:
            focus, intensity, status, _, condition = obs
            key = f'{focus}/{intensity}'
            row['plans'][key] = row['plans'].get(key,0)+1
            row['participation'] += status in ('trained','recovered')
            row['recovery'] += max(0,condition)
        else:
            row['team_weeks'] += 1
        row['injured_weeks'] += bool(weekly['injury'] or (obs and obs[2]=='injured'))
        row.update({key: weekly[key] for key in ('condition','form','morale','injury')})
    if week==34 or (day+timedelta(days=7)).month != day.month:
        history.append(s.pop('training_month'))
        del history[:-MONTH_LIMIT]


def ability_snapshot(s):
    from veritabani import roster
    return {p['id']: s.get('fitness',{}).get(p['id'],{}).get('ability',p['rating'])
            for p in roster(s['club'],s['year'],s)}
