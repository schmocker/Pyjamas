import datetime as datetime
from .special_days import *

def prep_date(self, date_i='01.01.2006 01:00', country_i=1):

    #date_i = '01.01.2006 01:00'

    date_i = datetime.strptime(date_i, '%d.%m.%Y %H:%M')
    weekend = date_i.isoweekday() == 6 | date_i.isoweekday() == 7
    if weekend == True:
        weekend = 1
    else:
        weekend = 0
    seconds = date_i.hour * 3600 + date_i.minute * 60
    holiday = func_holiday(date_i)
    country = country_i
    NN_input = np.array([[date_i.year], [weekend], [seconds], [holiday], [country]])

    return NN_input