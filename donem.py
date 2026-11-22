"""Bounded nominal indices for the fictional football economy."""
from functools import lru_cache

LIMITS = {
    'wage': 2.45, 'transfer': 2.90, 'signing': 2.35, 'staff': 2.12,
    'broadcast': 2.85, 'sponsors': 2.36, 'gate': 1.85, 'commercial': 2.58,
    'operations': 2.24, 'facilities': 2.09, 'prize': 2.30,
}


@lru_cache(maxsize=512)
def index(year, category):
    years=max(0,year-2000)
    return 1+(LIMITS[category]-1)*years/(years+28)


def multiplier(s, category):
    return index(s['year'],category) if s.get('economy_model')==2 else 1


def scaled(s, category, amount):
    return int(amount*multiplier(s,category))
