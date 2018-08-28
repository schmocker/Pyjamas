# Marginal cost
Determines the marginal cost of each power plant.

## Inputs
The input to this model is a *dict* holding the different parameters of all power plants.

## Outputs
*dict* of form {"key": value,...}\
Each key/value pair consists of a string (key) and a list containing the corrsponding value for each power plant,
sorted after power plant id.

Key | Description | Unit
--- | --- | --- |
"power_plant_id" | power plant ID | [-]
"MarginalCost" | marginal cost of power plant | [€/J]

## Properties
None

### Implementation
Marginal cost = Variable Opex + Combustible (fuel) costs + CO2 costs + Disposal costs 
