from core import Supermodel

class Model(Supermodel):
    def __init__(self, id, name: str):
        super(Model, self).__init__(id, name, ["sum"])
        pass

    ### THE 5 MODEL METHODS ###
    # There are 5 methods / functions:
    #
    # - func_birth  - start
    # - func_prep        🠜  🠜  🠜  🠜
    # - func_peri       🠟 iteration  🠝
    # - func_post        🠞  🠞  🠞  🠞
    # - func_death⃒  - end
    #
    # These methods are already defined within the supermodel where thy are empty. One can overwrite a method by
    # redefining it here. Like this the defining of each method is optional. Of course it is also allowed to define
    # additional methods to use them within this model.

    # BIRTH
    # - runs only once at the beginning
    async def func_birth(self):
        pass

    # PREP
    # - runs once every iteration
    # - contains all the calculations, which can be done before cronjob is triggered
    async def func_prep(self):
        pass

    # PERI
    # - runs once every iteration
    # - contains the main part of each iteration
    # - will be triggered by the cronjob
    # - has to be as fast as possible
    async def func_peri(self, prep_to_peri=None):
        pass

    # POST
    # - runs once every iteration
    # - contains the end part of each iteration
    async def func_post(self, peri_to_post=None):
        pass

    # DEATH
    # - runs only once at the end
    async def func_death(self):
        pass
