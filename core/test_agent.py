import asyncio
import logging

class TestAgent():

    def __init__(self):
        self.model = None

        # name
        self.name = "Model_Tester"

        # sync gates
        self.sync_gate_first = asyncio.Event()
        self.sync_gate_second = asyncio.Event()

        # func gates
        self.prep_gate = asyncio.Event()
        self.peri_gate = asyncio.Event()
        self.post_gate = asyncio.Event()

        # open func gates
        self.prep_gate.set()
        self.peri_gate.set()
        self.post_gate.set()

        # outputs that will be set as input for the model
        self.outputs = {}

        # outputs of the model
        self.model_outputs = {}

        # event loop
        self.loop = asyncio.get_event_loop()

        # logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        con = logging.StreamHandler()
        con.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s][%(processName)s] : %(message)s')
        con.setFormatter(formatter)
        self.logger.addHandler(con)
        self.log_debug("initialized logger")

    def log_debug(self, msg):
        self.logger.debug(f"[AGENT][{__name__}][{self.name}] : {msg}")

    def prepare_model(self):
        # execute func_birth for all models
        self.log_debug("starting internal birth")
        birth = asyncio.ensure_future(self.model._internal_birth())
        self.loop.run_until_complete(asyncio.gather(birth))

    def start(self):

        self.model.alive = True

        # func_birth is executed and finished for the model before anything else
        self.prepare_model()

        # link inputs
        self.log_debug("linking inputs")
        for input_name in self.outputs:
            self.model.link_input(self, input_name, input_name)
        
        # start the internal loop of the model
        self.log_debug("starting internal loop")
        prep = asyncio.ensure_future(self.model.internal_loop())
        self.loop.run_until_complete(asyncio.gather(prep))

    def set_model(self, model_to_add):
        self.model = model_to_add

    def set_input(self, input_name, input_value):
        self.outputs[input_name] = asyncio.Future()
        self.outputs[input_name].set_result(input_value)

    def remove_input(self, input_name):
        self.outputs.pop(input_name, None)
        self.model.inputs.pop(input_name, None)

    def link_models(self, output_model, output_name, input_model, input_name):
        input_model.link_input(output_model,output_name,input_name)

    async def syncFirst(self):
        # first sync gate ensures that the model is finished

        # read outputs of model
        self.log_debug("reading outputs")
        for name, future in self.model.outputs.items():
            self.model_outputs[name] = await future

        self.sync_gate_second.clear()
        self.sync_gate_first.set()
        self.log_debug("first sync gate opened")

    async def syncSecond(self):
        # second sync gate ensures that the model has finished func_in_sync and cleared its outputs
        
        self.log_debug("model.alive set to false")
        self.model.alive = False

        self.sync_gate_first.clear()
        self.sync_gate_second.set()
        self.log_debug("second sync gate opened")
