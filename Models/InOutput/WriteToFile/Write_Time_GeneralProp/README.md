# Write general time-dependent properties to file

Write general (distribution network independent) time-dependent properties to txt file.


## Inputs
The inputs to this model are:

1. Futures
1. Demand
1. Power loads of power plants


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
1. Demand
1. For each power plant the power load
1. Sum of power loads over all power plants for each time step


## Remarks

* write a new file, when no file existing with corresponding start, time step and end date.
* else it appends the data
* => to force a new file, delete old ones
