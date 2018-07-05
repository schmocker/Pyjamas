from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        stops the simulation after a set amount of runs
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)

        self.properties['stop_after'] = Property(1, int, name='Number of runs')

    async def func_in_sync(self):
        if self.model_run >= self.get_property('stop_after')-1:
            self.agent.end_all_model_loops()