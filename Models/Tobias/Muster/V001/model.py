from core import Supermodel

class Model(Supermodel):
    def __init__(self, id, name: str):
        super(Model, self).__init__(id, name, ["sum"])
        pass

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
    # - contains the main part, which will be triggered by the cronjob
    # - has to be as fast as possible
    async def func_peri(self, prep_to_peri=None):
        pass

    # POST
    # - runs once every iteration
    async def func_post(self, peri_to_post=None):
        pass

    # DEATH
    # - runs only once at the end
    async def func_death(self):
        pass
