# Calculation of distance factor
Calculation of the distance factor based on the European Power Plant and a location given by the geographical coordinates 

## Inputs
The inputs to this model are:

1. European Power Plant
2. Geographical coordinates of location

## Outputs

The output is:

1. Distance cost factor for each location

## Properties

The property is:

1. Network cost for medium voltage customers per MWh times traded energy amount within a year

Rabiosa Churwalden: Netzkosten Mittelspannung 2017: Tag 4.40 Rp./kWh, Nacht 3.50 Rp./kWh => Mittel (Annahme) = 4 Rp./kWh
=> annual network cost = 148E9 € for demand of 3700 TWh (Entso-e TYNDP2018_MAF)

## Remarks

### Implementation

NK = DK = int_year sum(distance_KW_i * P_KW_i) * DKF dt = 8760 h * DKF * sum(distance_KW_i * P_KW_i)

=> DKF = ... 