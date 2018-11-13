# Weather model

* create weather data based on the futures
    1. current weather forecast by API
    1. historic weather data from 2006-2017


## Inputs
The inputs to this model are:

1. Modus (islive or not)
1. Information of KW's
1. Time series (Futures)


## Outputs
The outputs of this model are:

1. Weather data to KW's (KW id, windspeed, radiation, windmesshoehe)
2. Future weather: weather data base (time, temperature, wind speed, radiation)

### Weather data to KW

dict of
* KW id
* Windspeed
* Radiation
* Windmesshoehe

### Demand weather for demand calculation

dict of
* Location id
* Latitude
* Longitude
* Temperature

### Future weather

dict of
* Point ids
* Latitude
* Longitude
* Weather (time, temperature, wind speed, radiation)

### Map weather for demand calculation

dict of
* Futures
* Coordinates of map grid points
* Temperature
* Wind speed
* Radiation


## Properties
The properties of this model are:

1. Offset of temperature
1. Offset of wind speed
1. Offset of radiation
1. Reference year when using historical data for weather forecast

## Remarks

### Implementation

* when futures are now or later and futures within 7 days, then API weather data is used
* else historic data of reference year is provided

### Reference year

* provided are the years 2006-2017, selecting 1.1.2006 or late dates in 2017 can lead to problems, not catched so far
* when year of futures is a leap year and reference not, then reference year is adjusted to the nearest reference leap year (2008, 2012, 2016)

### data

* API_Key, historical data (dict_hist), as well as the previous loaded API data are stored (and i.a. required) in the folder confidential
