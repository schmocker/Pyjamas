# Pyjamas
Pyjamas is a web-based simulation environment. The word Pyjamas stands for:
* **Py**thon: Pyjamas is running mainly on python.<
* **J**oint: Pyjamas grew out of a collaboration within the FHNW.
* **A**gent based: Pyjamas grew out of a collaboration within the FHNW.
* **M**gulti model: Pyjamas is all about model and modular construction of simulations.
* **A**synchronous: Pyjamas is based on asynchronous functions.
* **S**imulation program: That's actually what Pyjamas is all about

## Content
* 1. Pyjamas core
* 2. websimgui
* 3. Models
## 1. Pyjamas core</h3>
... more documentation will follow ...
## 2. websimgui
... more documentation will follow ...
## 3. Models
... more documentation will follow ...

### 3.1 Defining a model</h4>


#### 3.1.1 The 5 methods</h5>
There are 5 methods (functions within a class):

* func_birth 🠞 start
* func_prep  &emsp;&emsp; 🠜  🠜  🠜  🠜
* func_peri  &emsp;&emsp;🠟 iteration  🠝
* func_post  &emsp;&emsp; 🠞  🠞  🠞  🠞
* func_death 🠞 end

These methods are already defined within the supermodel where thy are empty. One can overwrite a method by
redefining it here. Like this the defining of each method is optional. Of course it is also allowed to define
additional methods to use them within this model.

```python
async def func_birth(self):
    pass
```