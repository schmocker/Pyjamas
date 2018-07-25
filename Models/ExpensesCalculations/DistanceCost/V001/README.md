# Marginal cost

Determine the distance cost of each power plant

## Inputs
The inputs to this model are:

1. SPGLocations - Dictionary containing latitude and longitude coordinates of Signal Price Generator(SPG) locations
e.g. Baden, Brugg, olten, etc..
1. PowerPlantsData - Dictionary holding the different required parameters of power plants


## Outputs
The output of this model is:

1. DistanceCost: Dictionary containing the locations of all Signal Price Generators (SPGs), power plant ids and 
distance costs for all SPG locations


## Properties
The property of this model is:

1. DistanceFactor 

## Remarks
Distance cost calculations are based upon the distance between SPG and power plant locations

### Implementation