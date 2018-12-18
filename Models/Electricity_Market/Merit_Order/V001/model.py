from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import pandas as pd


class Model(Supermodel):

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['fut'] = Input(name='Futures', unit='s', info='utc time array in seconds since epoch', example='[1530792535, 1530792540, 1530792545]')
        self.inputs['demand'] = Input(name='European demand', unit='W', info='European power demand for each time step')
        self.inputs['power'] = Input(name='Power', unit='W', info='Power for each power plant and time step')
        self.inputs['power_plants'] = Input(name='Power Plants', unit='-', info='Power Plants')
        self.inputs['distance_costs'] = Input(name='Distance costs', unit='€/J', info='Distance costs for each power plant and distribution network')

        self.outputs['market_prices'] = Output(name='Market prices', unit='€/J', info='Market prices for each distribution network and time step')
        self.outputs['power_plants2'] = Output(name='Power Plants', unit='-', info='Power Plants with additional information')
        self.outputs['sorted_pp_id'] = Output(name='Sorted power plant ids', unit='-', info='sorted power plant ids for each distribution network')
        self.outputs['fut2'] = Output(name='Futurs', unit='s', info='utc time array in seconds since epoch')
        self.outputs['demands2'] = Output(name='Demands', unit='W', info='European power demand for each time step')


    async def func_peri(self, prep_to_peri=None):
        demands = await self.get_input("demand")  # f(time)
        powers = await self.get_input("power")  # f(time, pp)
        power_plants = await self.get_input("power_plants")  # f(pp)
        distance_costs = await self.get_input("distance_costs")  # f(pp, distNet)
        times = await self.get_input("fut")

        # add load to power plant
        power_plants['load'] = [None] * len(power_plants['id'])
        power_plants['distance_costs'] = [None] * len(power_plants['id'])
        power_plants['total_costs'] = [None] * len(power_plants['id'])

        for i, pp_id in enumerate(power_plants['id']):
            power_plants['load'][i]=powers['scaled_power'][np.where(np.array(powers['power_plant_id']) == pp_id)[0][0]]

            dc = distance_costs['costs'][np.where(np.array(distance_costs['power_plants']) == pp_id)[0][0]]
            power_plants['distance_costs'][i] = dc

            mc = power_plants['grenzkosten'][i]
            power_plants['total_costs'][i] = [d_c+mc for d_c in dc]


        NPA = pd.DataFrame.from_dict(power_plants)

        def build_price2(demand, powers, costs):
            try:
                price = costs[np.where(np.cumsum(powers) >= demand)[0][0]]
            except Exception as E:
                print(E)
                price = np.max(costs)
            return price

        def build_price(i_dn):
            costs = np.array(power_plants['total_costs'])[:, i_dn]

            sort_order = np.argsort(costs)

            costs = costs[sort_order]

            pp_ids = np.array(power_plants['id'])[sort_order]
            power = np.array(power_plants['load'])[sort_order]

            price = [build_price2(demand, power[:, i_ts], costs) for i_ts, demand in enumerate(demands)]

            return {'pp_ids': pp_ids.tolist(),
                    'prices': price}

        data = {v:build_price(i) for i, v in enumerate(distance_costs['distribution_networks'])}

        prices = [value['prices'] for key, value in data.items()]
        pp_ids = [value['pp_ids'] for key, value in data.items()]
        dn = [key for key, value in data.items()]
        prices = {'distribution_networks': dn, 'prices': prices}
        pp_ids = {'distribution_networks': dn, 'pp_ids': pp_ids}



        def final_load(i_pp, i_dn, i_t):
            if power_plants['total_costs'][i_pp][i_dn] <= prices['prices'][i_dn][i_t]:
                return power_plants['load'][i_pp][i_t]
            else:
                return 0

        power_plants['sold_load'] = [[[final_load(i_pp, i_dn, i_t)
                                        for i_t in range(len(prices['prices'][0]))]
                                       for i_dn in range(len(prices['distribution_networks']))]
                                      for i_pp in range(len(power_plants['id']))]

        self.set_output("market_prices", prices)
        self.set_output("sorted_pp_id", pp_ids)
        self.set_output("power_plants2", power_plants)
        self.set_output("fut2", times)
        self.set_output("demands2", demands)

