# Future Generator
### Input
- Time: takes a UTC time, for example from a scheduler

### Properties
-  Interval time [s]: defines the interval between each time step in seconds 
-  Number of intervals [-]: defines how many time seps of 'interval'

### Output
- Futures: passes a UTC time array. The first value of the array equals exactly the input time.
The following values increase with 'Interval time' seconds for 'Number of intervals' times.

### Calculation
The calculation of the future generator is quite simple. Attached is an example
```Python
# input: time
time = 1529620280

# property: Interval time [s]
interval = 5

# property: Number of intervals [-]
n_of_intevals = 3

# calculation
futures = [i * 5 + 1529620280 for i in range(3)]

#ouput: Futures
print(futures)
[1529620280, 1529620285, 1529620290]
```

### Model
The model can be found on <a target="_blank" href="https://github.com/schmocker/Pyjamas/tree/master/Models/Scheduler/Future_Geneartor/V1">GitHub Pyjamas</a>.
