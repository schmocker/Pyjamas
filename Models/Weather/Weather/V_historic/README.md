# Weather model

* works always in simulation mode (not live) using only historical weather data
* forecast weather by API not implemented


## Inputs
The inputs to this model are:

1. Modus (islive or not)
1. Information of KW's
1. Time series (Futures)


## Outputs
The outputs of this model are:

1. Weather data to KW's (ID, Temperature, Wind speed, Radiation)
2. Future weather: weather data base

## Properties
The properties of this model is:

1. Offset of temperature
1. Offset of wind speed
1. Offset of radiation
1. Reference year when using historical data for weather forecast


## Remarks

### Implementation

....