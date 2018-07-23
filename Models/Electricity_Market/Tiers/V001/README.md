# Tiers

Calculation of the electricity rate based on the stock price, the distribution network costs, service costs and taxes

## Inputs
The inputs to this model are:

1. stock price (for each location and futures)
1. distribution network costs (for each network and futures)
1. service costs (constant)
1. taxes (constant)

## Outputs
The output of this model is:

1. dict of 
    * location ID
    * electricity rate (values; for each location and futures)
    * borders of tiers (energy and network)

## Properties
The properties of this model are:

1. energy tiers
1. distribution network tiers


## Remarks

### Implementation

* when distribution network is not in tiers location, the values of the default are taken 

....