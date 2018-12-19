# Write power plant properties to file

Write power plant informations to txt file.


## Inputs
The inputs to this model are:

1. KW data


## Outputs
no output


## Properties
The properties of this model are:

1. start date
1. time step size
1. end date


## Data writen to file

The following properties are writen to the file:

1. KW id
1. KW description (KW Bezeichnung)
1. Installed power
1. Description of power plant type (Bez Kraftwerkstyp)


## Remarks

* write a new file, when no file existing with corresponding start, time step and end date.
* else it appends the data
* => to force a new file, delete old ones
