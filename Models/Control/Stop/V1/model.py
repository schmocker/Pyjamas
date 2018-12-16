from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel

class Model(Supermodel):
    """
        stops the simulation after a set amount of runs
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)

        self.properties['stop_after'] = Property('Number of runs', default=1, data_type=int)

    async def func_in_sync(self):
        if self.model_run >= self.get_property('stop_after')-1:
            self.agent.end_all_model_loops()