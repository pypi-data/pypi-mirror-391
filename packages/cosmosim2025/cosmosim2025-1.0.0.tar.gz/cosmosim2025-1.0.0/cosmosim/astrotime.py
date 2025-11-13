import datetime

def utc_to_jd(dt: datetime.datetime) -> float:
    a = (14 - dt.month)//12
    y = dt.year + 4800 - a
    m = dt.month + 12*a - 3
    jd = dt.day + ((153*m+2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
    jd += (dt.hour - 12)/24 + dt.minute/1440 + dt.second/86400
    return jd

def jd_to_utc(jd):
    jd += 0.5
    Z = int(jd)
    F = jd - Z
    A = Z
    B = A + 1524
    C = int((B - 122.1)/365.25)
    D = int(365.25 * C)
    E = int((B - D)/30.6001)
    day = B - D - int(30.6001 * E) + F
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715
    return datetime.datetime(int(year), int(month), int(day))
