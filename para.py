"""Display-only currency conversion. The ledger always uses integer game USD."""
from datetime import date,timedelta
from decimal import Decimal, ROUND_HALF_UP

CURRENCIES=('TRY','GBP','EUR','USD')
# Representative simulation rates, not a quoted FX time series.
RATE_TABLE={2000:('.625','.66','1.08'),2001:('1.19','.70','1.12'),2002:('1.50','.67','1.05'),
            2003:('1.49','.62','.89'),2004:('1.43','.55','.81'),2005:('1.35','.55','.80'),
            2006:('1.43','.54','.80'),2009:('1.55','.64','.72'),2015:('2.72','.65','.90'),
            2020:('7.0','.78','.88'),2025:('39','.77','.91')}

def rate(s):
    currency=s.get('currency','USD')
    if currency=='USD':
        return Decimal(1),'USD'
    day=date(s['year'],8,1)+timedelta(weeks=s['week']-1)
    year=day.year
    key=max(k for k in RATE_TABLE if k<=year)
    coefficient=Decimal(RATE_TABLE[key][CURRENCIES.index(currency)])
    if currency=='TRY':
        if year<2005:
            return coefficient*1000000,'TRL'
        return coefficient,'YTL' if year<2009 else 'TRY'
    return coefficient,currency

def amount(s,value):
    return Decimal(value)*rate(s)[0]

def text(s,value):
    shown=amount(s,value)
    digits=0 if shown==shown.to_integral_value() else 2
    return f'{shown:,.{digits}f} {rate(s)[1]}'

def edit_value(s,value):
    return format(amount(s,value).normalize(),'f')

def from_display(s,raw):
    try:
        number=Decimal(raw.strip().replace(',',''))
        if not number.is_finite() or abs(number)>Decimal('1e21'):
            raise ValueError('Invalid monetary amount')
        return int((number/rate(s)[0]).to_integral_value(rounding=ROUND_HALF_UP))
    except ArithmeticError as exc:
        raise ValueError('Invalid monetary amount') from exc
