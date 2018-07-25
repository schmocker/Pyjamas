# Photovoltaic power system model

Determines the load of multiple PV power systems for the given values of their corresponding global radiation


## Inputs
The inputs to this model are:

1. WeatherData - Dictionary holding Power plant ids and corresponding required weather data for all power plants
1. PowerPlantsData - Dictionary holding the different required parameters of power plants


## Outputs
The output of this model is:

1. Load of all PV systems, load values are between 0 and 1


## Properties


## Remarks


### Implementation

The basic PV system having nominal power of 1kW is implemented using the following equations under the standard test 
conditions(STC) for module's temperature
```
    Pout = (Pn - Ptemp)*(Rtilt/1000)
    Ptmep = (Tmod - 25) * 0.0034 * Pn
    Rtilt = (1- Gloss)*Gr
    where,
    Pout = Output power[W]
    Pn = Module's nominal power[W]
    Ptemp = Loss[W] due to modules temperature
    Tmod = PV module's temperature[°C] (STC = 25°C)
    Rtilt = Radiation on tilted surface[W/m^2]
    Gloss = Global radiation loss[%] due to module's physical orientation
    Gr = Measured global radiations[W/m^2]
```
The final load of each PV system is calculated as follow
```
    load = Pout / Pn  
    load values between 0 and 1
```
