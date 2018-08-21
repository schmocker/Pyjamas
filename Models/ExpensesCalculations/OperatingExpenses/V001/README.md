# OPEX - Operating Expenses

Determine the operating expenses of each power plant

## Inputs
The inputs to this model are:

1. CombinedLoad - Dictionary containing ids and load of all power plants
1. PowerPlantData - Dictionary holding the different required parameters of power plants


## Outputs
The output of this model is:

1. OPEX - Dictionary containing power plant ids in one list and corresponding calculated operating expenses of all
power plant in other list


## Properties


## Remarks
Output dictionary is sorted according to the incoming id's in PowerPlantData.

### Implementation

Operational expenses/costs = Capex * (spez) Opex / Load
