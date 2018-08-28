# Distance cost
Determine the distance cost of each power plant

## Inputs
The inputs to this model are:

1. SPGLocations - Dictionary containing latitude and longitude coordinates of Signal Price Generator(SPG) locations
e.g. Baden, Brugg, Olten, etc..
1. PowerPlantsData - Dictionary holding the different required parameters of all power plants

## Outputs
*dict* of form {"key": value,...} sorted after power plant id, containing:

Key | Description | Unit
--- | --- | --- |
"power_plants" | power plant ID | [-]
"distribution_networks" | locations | ['str']
"costs" | distance costs | [€/m*J]

## Properties
DistanceFactor [€/MWh*km]

## Remarks
Distance cost calculations are based upon the distance between SPG and power plant locations

### Implementation
Distance Cost = Distance Factor * Distance