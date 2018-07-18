# Weather model

=> V_historic

* works always in simulation mode (not live) using only historical weather data
* forecast weather by API not implemented


## Inputs
The input to this model:

1. Modus (islife or not)
1. Information of KW's
1. Time series (Futures)


## Outputs
The output of this model is:

1. Weather data to KW's (ID, Temperature, Wind speed, Radiation
2. Future weather: weather data base

## Properties
The property of this model is:

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
