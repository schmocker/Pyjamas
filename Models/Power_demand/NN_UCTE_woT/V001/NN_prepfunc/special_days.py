import math
from datetime import date, timedelta

def func_holiday(self, date_x):
    # eastern
    hday_1 = func_easterday(date_x)

    # christmas
    hday_2 = func_xmasday(date_x)

    # holidays
    holidays = hday_1 | hday_2
    if holidays == True:
        holidays = 1
    else:
        holidays = 0

    return holidays


def func_easterday(self, date_x):
    ret_eastersun = func_eastersunday(date_x.year)
    d_eastersun = date(date_x.year, ret_eastersun[1], ret_eastersun[0])

    easter_start = d_eastersun - timedelta(days=2)
    easter_end = d_eastersun + timedelta(days=1)

    easterday = easter_start <= date_x.date() & date_x.date() <= easter_end
    if easterday == True:
        easterday = 1
    else:
        easterday = 0

    return easterday


def func_eastersunday(self, year_x):
    # easter formula based on Heiner Lichtenberg
    k = math.floor(year_x / 100)
    m = 15 + math.floor((3 * k + 3) / 4) - math.floor((8 * k + 13) / 25)
    s = 2 - math.floor((3 * k + 3) / 4)
    a = math.fmod(year_x, 19)
    d = math.fmod(19 * a + m, 30)
    r = math.floor(d / 29) + (math.floor(d / 28) - math.floor(d / 29)) * math.floor(a / 11)
    og = 21 + d - r
    sz = 7 - math.fmod(year_x + math.floor(year_x / 4) + s, 7)
    oe = 7 - math.fmod(og - sz, 7)
    march_day = og + oe

    # conversion to day and month
    if march_day > 31:
        day = march_day - 31
        month = 4
    else:
        day = march_day
        month = 4
    d_eastersun = np.array([[day], [month]])

    return d_eastersun


def func_xmasday(self, date_x):
    test_month = date_x.month == 12
    test_days = date_x.day == 24 | date_x.day == 25 | date_x.day == 26
    xmasday = test_month & test_days
    if xmasday == True:
        xmasday = 1
    else:
        xmasday = 0

    return xmasday
