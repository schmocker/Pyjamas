from datetime import datetime
from pytz import timezone
from .special_days import *
from ..date_functions import *
import numpy as np

def prep_date(self, date_i='01.01.2006 01:00', country_i=1):

    date_i = datetime.strptime(date_i, '%d.%m.%Y %H:%M')
    date_local = date_UTC_to_local(date_i)
    weekend = date_local.isoweekday() == 6 | date_local.isoweekday() == 7
    if weekend == True:
        weekend = 1
    else:
        weekend = 0
    seconds = date_local.hour * 3600 + date_local.minute * 60
    holiday = func_holiday(date_local)
    country = country_i
    nn_input = np.array([[date_local.year], [weekend], [seconds], [holiday], [country]])

    return nn_input
