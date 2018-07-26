# Combined load of all power plants

Determine the load of each power plant according to incoming power plant key separately and then combine them together
to form the combined load


## Inputs
The inputs to this model are:

1. LoadWindTurbine - Load of all wind turbines
1. LoadPhotovoltaic - Load of all photovoltaic power plants
1. LoadRunningWaterPowerPlant - Load of all run-of-river power stations
1. LoadStoragePowerPlant - Load of all storage power plants
1. PowerPlantsData - Dictionary holding the different required parameters of power plants
1. Futures - Timestamps 


## Outputs
The output of this model is:

1. CombinedLoad - Dictionary containing ids of all power plants in the first list and corresponding calculated load of
all power plants in the second list, output values of load are between 0 and 1


## Properties


## Remarks
Output dictionary is not sorted and contains the load of wind turbines at first place on the top, then comes the load 
of PV, running-water, and storage power plants respectively, in the last comes the load of remaining power plants 
(assigned 100% load).

### Implementation


#### References
