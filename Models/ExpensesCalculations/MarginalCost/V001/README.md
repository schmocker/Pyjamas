# Marginal cost
Determines the marginal cost of each power plant.

## Inputs
The input to this model is a dictionary holding the different parameters of power plants.

## Outputs
*dict* of form {"key": value,...}\
Each key/value pair consists of a string (key) and a list containing the corrsponding value for each power plant,
sorted after power plant id.

Key | Description | Unit
--- | --- | --- |
"power_plant_id" | power plant ID | [-]
"MarginalCost" | power plant name | [€/J]

## Properties
None

## Remarks
Output dictionary is sorted according to the incoming id's in PowerPlantData.

### Implementation

Marginal cost = Operational costs + Combustible (fuel) costs + CO2 costs + Disposal costs 
