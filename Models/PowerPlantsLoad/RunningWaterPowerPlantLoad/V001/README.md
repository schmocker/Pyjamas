# Run-of-river power plant model

Determines the load of multiple run-of-river power stations for the given interval of time


## Inputs
The inputs to this model are:

1. Futures - Timestamps
1. PowerPlantsData - Dictionary holding the different required parameters of power plants


## Outputs
The output of this model is:

1. Load of all run-of-river power stations, load values are between 0 and 1


## Properties


## Remarks


### Implementation

A one year load-profile of run-of-river power station at Rhein, Rheinfelden is used to define the seasonal changes in
the load. The measured data [1] of most recent leap year 2016 is used to determine the load-profile. 

#### References
[1] Federal Office for the Environment FOEN - Hydrological data and forecasts, {Web} https://www.hydrodaten.admin.ch/en/messstationen_zustand.html