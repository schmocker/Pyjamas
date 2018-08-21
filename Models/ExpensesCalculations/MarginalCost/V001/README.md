# Marginal cost

Determine the marginal cost of each power plant

## Inputs
The inputs to this model are:

1. OPEX - Dictionary containing power plant ids and operating expenses of all power plants
1. PowerPlantsData - Dictionary holding the different required parameters of power plants


## Outputs
The output of this model is:

1. MarginalCost - Dictionary containing power plant ids in one list and corresponding calculated marginal cost of all
power plants in other list


## Properties


## Remarks
Output dictionary is sorted according to the incoming id's in PowerPlantData.

### Implementation

Marginal cost = Operational costs + Combustible (fuel) costs + CO2 costs + Disposal costs 
