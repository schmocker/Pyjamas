# Write distribution network-dependent and time-dependent properties to file

Write distribution network-dependent and time-dependent properties to txt file.

Each distribution network results in an own txt file.


## Inputs
The inputs to this model are:

1. Futures
1. Distribution networks
1. Market price
1. Power plant data
1. Tiers prices


## Outputs
no output


## Properties
The properties of this model are:

1. start date
1. time step size
1. end date


## Data writen to file

The following properties are writen to the file:

1. Time
1. Market_price
1. All tiers prices 
1. Sold power load of each power plant
1. Total sold power load (sum)


## Remarks

* write a new file, when no file existing with corresponding start, time step and end date.
* else it appends the data
* => to force a new file, delete old ones