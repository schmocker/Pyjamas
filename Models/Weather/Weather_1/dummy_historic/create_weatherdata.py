from datetime import datetime
from pytz import timezone
from Models._utils.time import datetime2utc_time, utc_time2datetime
import numpy as np
import csv

def create_weatherdate():

    # Year
    year_ref = 2000

    start_date = datetime(year_ref, 1, 1, 0, 15)
    end_date = datetime(year_ref+1, 1, 1, 0, 0)

    start_date_s = datetime2utc_time(start_date)
    end_date_s = datetime2utc_time(end_date)
    s_year = end_date_s-start_date_s

    actual_dates = np.arange(0,s_year,15*60)
    actual_year = year_ref

    # Temperature
    a = 0.5*18.2
    b = a-0.6
    c = np.pi
    T_vec = a*(np.cos((2*np.pi*actual_dates/s_year-c))) + b
    T_vec = T_vec.tolist()

    # Wind speed
    a = 1.4*0.5
    b = a+1.2
    c = -1/12*np.pi
    u_vec = a*(np.cos((2*np.pi*actual_dates/s_year-c))) + b
    u_vec = u_vec.tolist()

    # "Radiation"
    a = 0.5*5.6
    b = a+1.2
    c = np.pi
    P_vec = a*(np.cos((2*np.pi*actual_dates/s_year-c))) + b
    P_vec = P_vec.tolist()


    # Formatting
    date_vec = datetime2utc_time(datetime(actual_year, 1, 1, 0, 15))+actual_dates.astype(datetime)
    date_vec_date = [utc_time2datetime(x) for x in date_vec]
    date_vec_date = [x.replace(tzinfo=timezone('UTC')) for x in date_vec_date]
    date_vec_date = [x.astimezone(timezone('Europe/Brussels')) for x in date_vec_date]
    date_string = [x.strftime("%Y-%m-%d %H:%M") for x in date_vec_date]

    table = [date_string, T_vec, u_vec, P_vec]
    table = list(map(list, zip(*table)))

    # Write to file
    f = open('Weather_2000_woheader.csv', 'w', newline='')
    with f:
        writer = csv.writer(f)
        writer.writerows(table)

    # Write to file
    f = open('Weather_2000.csv', 'w', newline='')
    rows = zip(date_string, T_vec, u_vec, P_vec)
    with f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Temperature", "Wind_speed", "Radiation"])
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    create_weatherdate()
