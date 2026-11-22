import unicodedata

# Historical identities have their own keys, separate from present-day states.
COUNTRIES = {
    'TR': ('Türkiye', 'Turkey'), 'DE': ('Almanya', 'Germany'),
    'YU': ('Yugoslavya', 'Yugoslavia'), 'RS-YU': ('Sırbistan (Yugoslavya)', 'Serbia (Yugoslavia)'),
    'RS': ('Sırbistan', 'Serbia'), 'BR': ('Brezilya', 'Brazil'),
    'GH': ('Gana', 'Ghana'), 'BG': ('Bulgaristan', 'Bulgaria'),
    'EG': ('Mısır', 'Egypt'), 'CM': ('Kamerun', 'Cameroon'),
    'RO': ('Romanya', 'Romania'), 'BY': ('Belarus', 'Belarus'),
    'PL': ('Polonya', 'Poland'), 'SE': ('İsveç', 'Sweden'),
    'HR': ('Hırvatistan', 'Croatia'), 'SK': ('Slovakya', 'Slovakia'),
    'FR': ('Fransa', 'France'), 'CD': ('Kongo DC', 'Democratic Republic of Congo'),
    'ZA': ('Güney Afrika', 'South Africa'), 'MK-FYR': ('Makedonya (EYMC)', 'FYR of Macedonia'),
    'MK': ('Kuzey Makedonya', 'North Macedonia'), 'MA': ('Fas', 'Morocco'),
    'UA': ('Ukrayna', 'Ukraine'), 'IL': ('İsrail', 'Israel'),
    'BA': ('Bosna-Hersek', 'Bosnia-Herzegovina'), 'NG': ('Nijerya', 'Nigeria'),
    'RU': ('Rusya', 'Russia'), 'BE': ('Belçika', 'Belgium'),
    'AR': ('Arjantin', 'Argentina'), 'IR': ('İran', 'Iran'),
    'AZ': ('Azerbaycan', 'Azerbaijan'), 'AT': ('Avusturya', 'Austria'),
    'NO': ('Norveç', 'Norway'), 'AL': ('Arnavutluk', 'Albania'),
    'GB-ENG': ('İngiltere', 'England'), 'ML': ('Mali', 'Mali'),
    'TN': ('Tunus', 'Tunisia'), 'GN': ('Gine', 'Guinea'),
    'QA': ('Katar', 'Qatar'), 'CI': ('Fildişi Sahili', 'Ivory Coast'),
    'MD': ('Moldova', 'Moldova'), 'BF': ('Burkina Faso', 'Burkina Faso'),
    'SI': ('Slovenya', 'Slovenia'), 'AU': ('Avustralya', 'Australia'),
    'ZZ': ('Bilinmiyor', 'Unknown'),
}
POSITIONS = {
    'GK': ('Kaleci', 'Goalkeeper'), 'D': ('Defans', 'Defender'),
    'CB': ('Stoper', 'Centre-back'), 'RB': ('Sağ bek', 'Right-back'),
    'LB': ('Sol bek', 'Left-back'), 'M': ('Orta saha', 'Midfielder'),
    'CM': ('Merkez orta saha', 'Central midfield'), 'DM': ('Ön libero', 'Defensive midfield'),
    'AM': ('Ofansif orta saha', 'Attacking midfield'), 'RM': ('Sağ orta saha', 'Right midfield'),
    'LM': ('Sol orta saha', 'Left midfield'), 'RW': ('Sağ kanat', 'Right winger'),
    'LW': ('Sol kanat', 'Left winger'), 'F': ('Forvet', 'Forward'),
    'CF': ('Santrfor', 'Centre-forward'), 'ST': ('Golcü', 'Striker'),
    'SS': ('İkinci forvet', 'Second striker'),
}

def normal(text):
    return ' '.join(unicodedata.normalize('NFC', text).casefold().replace('i\u0307', 'i').split())

ALIASES = {normal(label): code for code, labels in COUNTRIES.items() for label in labels}

def parse_citizenships(raw):
    return [
        {'country_id': ALIASES.get(normal(label), 'ZZ'), 'valid_from': None, 'raw': label.strip()}
        for label in (raw or '').split('/') if label.strip()
    ]

def citizenship_ids(p):
    return {entry['country_id'] for entry in p['citizenships']} or {'ZZ'}

def country_label(code, lang):
    return COUNTRIES[code][lang == 'EN']

def player_countries(p, lang):
    return ' / '.join(country_label(entry['country_id'], lang) for entry in p['citizenships']) or country_label('ZZ', lang)

def position_label(code, lang):
    return POSITIONS.get(code, ('—', '—'))[lang == 'EN']

def is_domestic(p):
    return 'TR' in citizenship_ids(p)


POSITION_CODES_TR={'GK':'KL','D':'DF','CB':'STP','RB':'SB','LB':'SLB','M':'OS','CM':'MOS',
                   'DM':'ÖL','AM':'OOS','RM':'SaOS','LM':'SoOS','RW':'SaK','LW':'SoK',
                   'F':'FV','CF':'SF','ST':'GL','SS':'İF'}

def position_code(code,lang):
    return POSITION_CODES_TR.get(code,code) if lang=='TR' else code
