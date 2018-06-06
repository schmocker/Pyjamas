from core import Supermodel


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

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



