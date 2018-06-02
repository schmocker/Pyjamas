# Pyjamas ![alt text](https://raw.githubusercontent.com/schmocker/Pyjamas/master/FlaskApp/static/images/favicon48.png "Logo Title Text 1")
Pyjamas is a web-based simulation environment. The word Pyjamas stands for:

* **Py**thon: Pyjamas is running mainly on python.
* **J**oint: Pyjamas grew out of a collaboration within the FHNW.
* **A**gent based: Pyjamas grew out of a collaboration within the FHNW.
* **M**gulti model: Pyjamas is all about model and modular construction of simulations.
* **A**synchronous: Pyjamas is based on asynchronous functions.
* **S**imulation program: That's actually what Pyjamas is all about

## Content
1. Pyjamas core
1. websimgui
1. Models

## 1. Pyjamas core
... more documentation will follow ...

## 2. websimgui
... more documentation will follow ...

## 3. Models
... more documentation will follow ...

### 3.1 Defining a model
Each model is defined in a file named *model.py*. The file lies within a hierarchical folder structure.
```
Project folder
|   Models
|   |   Topic_A
|   |   |   Model_X
|   |   |   |   Version_simple
|   |   |   |   |   model.py
|   |   |   |   Version_complex
|   |   |   |   |   model.py
|   |   |   |   |   db
|   |   |   |   |   |   db_declarative.py
|   |   |   |   |   |   db_dummy_data.py
|   |   |   |   |   view
|   |   |   |   |   |   d3.js
|   |   |   |   |   sketch
|   |   |   |   |   |   idea.py
|   |   |   |   |   |   draft.py
|   |   |   Mdoel_Y
|   |   |   |   V001
|   |   |   |   |   model.py
|   |   Topic_B
|   |   |   ....
```

Even though each model has to be defined as a class no knowledge about *object oriented programming* is required. At the
beginning it might seem very confusing but building a model really is only about defining a few functions.

By copying the model template folder from Models/Template_Topic/Template_Model one could get the whole folder structure
including a complete sample of the model file and other helpful files.

#### 3.1.1 The model class

```python
from core import Supermodel

class Model(Supermodel):
    def __init__(self, id, name: str):
        super(Model, self).__init__(id, name, ["sum"])
        pass
```

#### 3.1.2 The 5 methods
There are 5 methods (functions within a class) predefined within the model class:

* func_birth 🠞 start
* func_prep  &emsp;&emsp; 🠜  🠜  🠜  🠜
* func_peri  &emsp;&emsp;🠟 iteration  🠝
* func_post  &emsp;&emsp; 🠞  🠞  🠞  🠞
* func_death 🠞 end

These methods are already defined within the supermodel where thy are empty. One can overwrite a method by
redefining it here. Like this the defining of each method is optional. Of course it is also allowed to define
additional methods to use them within this model.

##### 3.1.2.1 birth method (start)
runs only once at the beginning
```python
async def func_birth(self):
    pass
```

##### 3.1.2.2 prep method (iteration step 1)
* runs once every iteration
* contains all the calculations, which can be done before cronjob is triggered
```python
async def func_prep(self):
    pass
```

##### 3.1.2.3 peri method (iteration step 2)
* runs once every iteration
* contains the main part of each iteration
* will be triggered by the cronjob
* has to be as fast as possible
```python
async def func_peri(self, prep_to_peri=None):
    pass
```

##### 3.1.2.4 post method (iteration step 3)
* runs once every iteration
* contains the end part of each iteration
```python
async def func_post(self, peri_to_post=None):
    pass
```

##### 3.1.2.5 death method (end)
* runs only once at the end
```python
async def func_death(self):
    pass
```

## 4. Sample Model
```python
from core import Supermodel


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name, ["sum"])

        # define inputs
        self.input = dict()
        self.input['v'] = {'name': 'wind speed'}
        self.input['dir'] = {'name': 'wind direction'}

        # define outputs
        self.output = dict()
        self.output['p_el'] = {'name': 'electrical power'}
        self.output['f_rot'] = {'name': 'rotor frequency'}

        # define parameters
        self.parameter = dict()
        self.parameter['h_hub'] = {'name': 'hub height'}


        # define persistent variables
        self.pers_variable_0 = 5

    async def func_birth(self):
        pass

    async def func_prep(self):
        # calculate something
        prep_result = 3 * 5
        # pass values to peri function
        return prep_result

    async def func_peri(self, prep_to_peri=None):
        prep_result = prep_to_peri
        # get inputs
        in1 = await self.get_input('input_1')
        in2 = await self.get_input('input_2')

        # calculate something
        # One can declare custom functions (eg: see end of file)
        # If you declare them "async" you will have to "await" them (like "extremely_complex_calculation")
        # Else one could declare "normal" (blocking) functions as well (like "complex_calculation")
        out1 = prep_result * self.complex_calculation(in1)
        out2 = await self.extremely_complex_calculation(in1, in2)

        # set output
        self.set_output("output_1", out1)
        self.set_output("output_2", out2)

        # pass values to post function
        outputs = {'out1': out1, 'out2': out2}
        return outputs

    async def func_post(self, peri_to_post=None):
        outputs = peri_to_post
        # do something with the values (eg: overwrite persistent variable)
        self.pers_variable_0 = outputs['out1']

    async def func_death(self):
        print("I am dying! Bye bye!")

    # define additional methods (normal)
    def complex_calculation(self, speed):
        speed_cut = speed / self.pers_variable_0
        return speed_cut

    # define additional methods (async)
    async def extremely_complex_calculation(self, speed, time):
        distance = speed * time / self.pers_variable_0
        return distance

```