# European Power Plant Database

This Model reads adatabase containing Data for the European Power Plants in different future scenarios.
It interpolates and combines data and outputs the combined data for all following models to use.

## Inputs
The input to this model is the **simulation time** from the scheduler.

## Outputs
The model outputs a combined table (as a *dict*) containing all **properties of all power plants.**

### Contents of Output
*dict* of form {"key": value,...}\
Each key/value pair consists of a string (key) and a list containing the corrsponding value for each power plant,
sorted after power plant id.

Key | Description | Unit
--- | --- | --- |
"id" | power plant ID | [-]
"kw_bezeichnung" | power plant name | [-]
"lat" | Latitude | [deg]
"long" | Longitude | [deg]
"p_inst" | Installed Power | [W]
"fk_kraftwerkstyp" | Foreign Key power plant type| [-]
"kwt_id" | power plant type ID | [-]
"bez_kraftwerkstyp" | power plant type name | [-]
"bez_subtyp" | power plant subtype name | [-]
"wirkungsgrad" | power plant efficiency | [-]
"var_opex" | variable OPEX | [€/J]
"capex" | CAPEX | [€/W_el]
"p_typisch" | typical power of power plant type | [W]
"spez_info" | special info of power plant type| for wind turbines: dict containing hub height: "NH" [m] and ground roughness: "Z0" [m]
"entsorgungspreis" | disposal price | [€/J_bs]
"fk_brennstofftyp" | Foreign Key fuel type | [-]
"brennstofftyp_id" | fuel type ID | [-]
"bez_brennstofftyp" | fuel type name | [-]
"co2emissfakt" | CO2 emission factor | [kg_CO2/J_bs]
"bs_preis" | fuel price | [€/J_bs]
"co2_preis" | CO2 price | [€/kg_CO2]
"co2_kosten" | CO2 costs | [€/J_el]
"entsorgungskosten" | disposal costs | [€/J_el]
"brennstoffkosten" | fuel costs | [€/J_el]
"grenzkosten" | marginal costs | [€/J_el]

## Properties
*None*

## Program structure
### birth
Connect to existing database. (Create session)

### peri
- Get input time array, use first time value for interpolation only
- Read all necessary tables and columns from database
- Interpolate values where necessary
- Calculate costs
- Build output dict

### interpolation functions
An interpolation function for each 1D, 2D and 3D exists.\
They are well documented within the function.\
Those functions mostly arrange the inputs and outputs and check for cases where not enough data points are provided
in which case no linear interpolation takes place but only interpolation to nearest.
The interpolation itself is handled through *scipy.interpolate.griddata*.