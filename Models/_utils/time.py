import time
import datetime
from pytz import timezone
import calendar
import pytz


# always use utc time form time.time between models
def utc_time2datetime(utc_time, tz=None):
    utc_datetime = datetime.datetime.fromtimestamp(utc_time)
    if tz is None:
        tz_datetime = utc_datetime.astimezone(timezone('utc'))
    else:
        tz_datetime = utc_datetime.astimezone(tz)
    return tz_datetime


def datetime2utc_time(datetime):
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=timezone('utc'))
    utc_datetime = datetime.astimezone(timezone('utc')).replace(tzinfo=None)
    utc_timetuple = utc_datetime.timetuple()
    utc_time = calendar.timegm(utc_timetuple) + datetime.microsecond / 1E6
    return utc_time


# Example
def example():

    print(f"All time zones: {pytz.all_timezones}")

    print("\nExample time")
    t = time.time()
    print(f"utc_timetime: {t} -> " + time.strftime("%Y-%m-%d %H:%M:%S+00:00", time.gmtime(t)))

    print("\nFrom time to upc datetime and back to time")
    utc_datetime = utc_time2datetime(t)
    print(f"utc_datetime:                       {utc_datetime}")
    utc_time = datetime2utc_time(utc_datetime)
    print(f"utc_timetime: {utc_time}  -> " + time.strftime("%Y-%m-%d %H:%M:%S+00:00", time.gmtime(utc_time)))

    print("\nFrom time to Europe/Brussels datetime and back to time")
    local_datetime = utc_time2datetime(t, timezone('Europe/Brussels'))
    print(f"loc_datetime:                       {local_datetime}")
    utc_time2 = datetime2utc_time(local_datetime)
    print(f"utc_timetime: {utc_time2}  -> " + time.strftime("%Y-%m-%d %H:%M:%S+00:00", time.gmtime(utc_time2)))

    print("\nFrom timestring > 2038 to datetime (only 64 bit)")
    t_string = 'Fri Jun 22 10:55:01 2060'
    t_tuple = time.strptime(t_string)
    t = calendar.timegm(t_tuple)
    dt = utc_time2datetime(t)
    print(dt)

if __name__ == "__main__":
    example()
