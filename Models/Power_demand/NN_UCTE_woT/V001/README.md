# Power demand model

Determination of the european (UCTE) power demand dependent on date and time


## Inputs
The input to this model:

1. futures


## Outputs
The output of this model is:

1. european (UCTE) power demand in [W]


## Properties
The property of this model is:

1. offset of the demand in % 


## Remarks

### Implementation

* by a neural network fitting
* power load reference data from ENTSO-e


### ENTSO-e reference data

* 2006-2015 
  * download from website as xlsx-file
  * remark in glossary, time: local time of Brussels
  * hourly values
  * https://www.entsoe.eu/data/data-portal/
 
* 2016-2017 
  * manually from transparency ENTSO-e site
  * time: CET/CEST
  * every quarter of an hour values
  * https://transparency.entsoe.eu/
  
* UCTE countries (24)
  * Austria
  * Bosnia-Herzegovina
  * Belgium
  * Bulgaria
  * Switzerland
  * Czech Republic
  * Germany
  * Denmark
  * Spain
  * France
  * Greece
  * Croatia
  * Hungray
  * Italy
  * Luxembourg
  * Montenegro
  * Makedonija
  * Netherland
  * Poland
  * Portugal
  * Romania
  * Serbia
  * Slovenia
  * Slovak Republic  

  
### Neural network

* determined by Matlab Neural Network Fitting App
* inputs
  * day of year
  * weekend yes/no
  * time in seconds
  * holiday yes/no
    * including easter and christmas
  * index of country
* output
  * power demand in [GW]


#### Remarks

Time handling

  * at the moment the difference in time zone's and daylight saving time/summertime of the different UCTE countries is not considered
  * e.g. Portugal, Romania, Bulgaria, ...
  * less correlation of neural network when datetime in UTC is used, therefore the need to convert the timestamp from UTC to CET/CEST
