"""Three completed weeks of player strain and a graduated return to play."""
from antrenman import INTENSITIES

WINDOW = 3


def history(z):
    return z.get('workload', ())


def fatigue(z):
    weighted = sum((minutes / 90 * 8 + training) * weight
                   for (minutes, training), weight in zip(reversed(history(z)), (1, .7, .4)))
    return min(28, round(weighted))


def recovery_staff(s, team):
    from personel import best
    fitness = best(s, team, 'fitness', 'fitness')
    medical = best(s, team, 'medical', 'fitness')
    return fitness // 5 + medical // 6, medical >= 15


def coaching_relief(s, team):
    from personel import best
    return best(s, team, 'coach', 'coaching') // 8


def recovery_ceiling(z, staff):
    rehab, _ = staff
    if z.get('return_weeks'):
        return min(96, (81 if z['return_weeks'] == 2 else 89) + rehab)
    return max(75, 100 - max(0, fatigue(z) - 8 - rehab))


def record(z, minutes, observation, relief, programme='Normal'):
    if observation:
        focus, intensity, status, _, _ = observation
        strain = (3 + 2 * INTENSITIES.index(intensity) + (focus == 'physical')
                  if status == 'trained' else 0)
    else:
        strain = 0 if z['injury'] or programme == 'Rest' else 5 if programme == 'Development' else 3
    z['workload'] = [*history(z), [minutes, max(0, strain - relief)]][-WINDOW:]


def progress_injury(z, staff):
    if z['injury']:
        z['injury'] -= 1
        if not z['injury']:
            z['return_weeks'] = 1 if staff[1] else 2
            z['condition'] = min(z['condition'], recovery_ceiling(z, staff))
    elif z.get('return_weeks'):
        z['return_weeks'] -= 1
        if not z['return_weeks']:
            z.pop('return_weeks')


def injury_multiplier(z, return_weeks):
    return 1 + max(0, fatigue(z) - 12) * .045 + bool(return_weeks) * .35
