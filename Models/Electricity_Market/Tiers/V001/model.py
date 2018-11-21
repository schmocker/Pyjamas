from core import Supermodel
from core.util import Input, Output, Property
from datetime import datetime, timedelta
from Models._utils.time import datetime2utc_time, utc_time2datetime
import numpy as np
from pytz import timezone
import json
from scipy.interpolate import griddata
import pandas as pd
import requests
import os

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['stock_ex_price'] = Input(name='Stock exchange price', unit='€/J', info="stock exchange price")
        self.inputs['distnet_costs'] = Input(name='Distribution network cost', unit='{-, €/J}', info="distribution network cost")
        self.inputs['service_cost'] = Input(name='Service cost', unit='€/J', info="service cost")
        self.inputs['taxes'] = Input(name='Taxes', unit='€/J', info="taxes")
        self.inputs['futures'] = Input(name='Futures', unit='s', info="Futures")

        # define outputs
        self.outputs['el_rate'] = Output(name='Electricity rate', unit='€/J', info='electricity rate')
        self.outputs['times'] = Output(name='Times', unit='s', info='Times')
        self.outputs['y_scaling'] = Output(name='Scaling of y axis', unit='', info='Scaling of y axis')
        self.outputs['y_label'] = Output(name='y label', unit='', info='Label of y axis')

        # define properties
        ET_def = {"location": ["Baden"],
                  "border": [[-1.0, -0.5, -0.2, 0.0, 0.2, 0.5, 1.0]],
                  "weight": [[-0.3, -0.6, -0.8, 1.1, 1.3, 1.5]]}
        NT_def = {"location": ["Baden"],
                  "border": [[-1.0, -0.8, -0.5, 0.0, 0.4, 0.8, 1.0]],
                  "weight": [[-0.5, -0.6, -0.8, 1.2, 1.5, 1.8]]}
        ET_def = json.dumps(ET_def)
        NT_def = json.dumps(NT_def)
        self.properties['weight_ET'] = Property(default=ET_def, data_type=str, name='energy tiers', unit='-', info='borders and weights of energy tiers', example=ET_def)
        self.properties['weight_NT'] = Property(default=NT_def, data_type=str, name='net tiers', unit='-', info='borders and weights of net tiers', example=NT_def)
        self.properties["scaling"] = Property(default=1, data_type=float, name='Scaling factor', unit='-',
                                              info='Scaling factor for y axis', example='3.6e9')
        self.properties["y_labeling"] = Property(default='Price', data_type=str, name='y label', unit='-',
                                                 info='Label for y axis', example='Price [€/MWh]')

        # define persistent variables
        self.weight_ET = None
        self.weight_NT = None
        self.y_scaling = None
        self.y_labeling = None

    async def func_birth(self):
        pass

    async def func_amend(self, keys=[]):

        if 'weight_ET' in keys:
            weight_ET_i = self.get_property('weight_ET')
            self.weight_ET = json.loads(weight_ET_i)

        if 'weight_NT' in keys:
            weight_NT_i = self.get_property('weight_NT')
            self.weight_NT = json.loads(weight_NT_i)

        if 'scaling' in keys:
            self.y_scaling = self.get_property("scaling")

        if 'y_labeling' in keys:
            self.y_labeling = self.get_property("y_labeling")

    async def func_peri(self, prep_to_peri=None):

        # locations information
        loc_tiers = self.weight_ET['location']

        # read prices
        stock_prices_input = await self.get_input('stock_ex_price')

        # read distribution costs
        dn_costs_input = await self.get_input('distnet_costs')
        loc_distnet = dn_costs_input['distribution_networks']
        len_loc_distnet = len(loc_distnet)

        # DLK
        DLK_val = await self.get_input('service_cost')

        # Abgaben
        abgaben_val = await self.get_input('taxes')

        # electricity rate
        el_rate = []
        border_tiers = []
        for nt in range(0, len_loc_distnet):

            # compare location of distribution network with tiers locations, in it?
            if loc_distnet[nt] in loc_tiers:
                idx = loc_tiers.index(loc_distnet[nt])
            else:           # if not in list, take default values
                idx = 0

            # distribution cost
            dist_costs = dn_costs_input['costs'][nt]

            # read and determine borders and tiers
            border_tiers_i = self.det_border_tiers(idx)

            # stock prices
            stock_prices = stock_prices_input['prices'][nt]

            el_rate_i = []
            for i_mt in range(0, len(stock_prices)):
                # stock price
                mt = stock_prices[i_mt]
                # electricity rate
                el_rate_ii = np.multiply(mt, border_tiers_i['ET_tiers']) + np.multiply(dist_costs, border_tiers_i['NT_tiers']) + DLK_val + abgaben_val
                el_rate_ii = el_rate_ii.tolist()
                el_rate_i.append(el_rate_ii)

            el_rate.append(el_rate_i)
            border_tiers.append(border_tiers_i)

        output = {'Stao_ID': loc_distnet,
                  'values': el_rate,
                  'borders': border_tiers
                  }

        # set output
        self.set_output("el_rate", output)
        self.set_output("times", await self.get_input('futures'))
        self.set_output("y_scaling", self.y_scaling)
        self.set_output("y_label", self.y_labeling)

    def det_border_tiers(self, it):

        # read borders
        ET_border = self.weight_ET["border"][it]
        NT_border = self.weight_NT["border"][it]

        ET_border = np.array(ET_border)
        NT_border = np.array(NT_border)

        # merge
        borders = np.append(ET_border, NT_border)
        borders = np.unique(borders)

        # read tiers
        ET_tiers_orig = self.weight_ET["weight"][it]
        NT_tiers_orig = self.weight_NT["weight"][it]

        # create tiers corresponding to border
        ind_ET = 0
        ind_NT = 0
        ET_tiers = np.array(ET_tiers_orig[ind_ET])
        NT_tiers = np.array(NT_tiers_orig[ind_NT])
        for it in range(1, len(borders) - 1):

            # ET
            if ET_border[ind_ET+1] <= borders[it]:
                ind_ET = ind_ET + 1
                ET_tiers = np.append(ET_tiers, ET_tiers_orig[ind_ET])
            else:
                ET_tiers = np.append(ET_tiers, ET_tiers_orig[ind_ET])

            # NT
            if NT_border[ind_NT+1] <= borders[it]:
                ind_NT = ind_NT + 1
                NT_tiers = np.append(NT_tiers, NT_tiers_orig[ind_NT])
            else:
                NT_tiers = np.append(NT_tiers, NT_tiers_orig[ind_NT])

            #print(it)

        # return dict
        border_tiers = {'borders': borders.tolist(),
                        'ET_tiers': ET_tiers.tolist(),
                        'NT_tiers': NT_tiers.tolist()}

        return border_tiers

if __name__ == "__main__":

    # input
    stock_ex_price = {'distribution_networks': ['Baden', 'Brugg'],
                      'prices': [[1, 2, 3], [1.1, 2.2, 3.3]]}
    distnet_costs = {'distribution_networks': stock_ex_price['distribution_networks'],
                     'costs': [100, 111]}
    DLK = [0.5]
    abgaben = [0.25]

    # properties
    ET = {"location": ['Baden', 'Brugg'],
          "border": [[-1., -0.8, -0.3, 0., 0.3, 0.8, 1.], [-1., -0.85, -0.35, 0., 0.35, 0.85, 1.]],
          "weight": [[-2., -1.25, -0.75, 0.75, 1.25, 2.], [-2., -1.3, -0.8, 0.8, 1.3, 2.]]}
    NT = {"location": ['Baden', 'Brugg'],
          "border": [[-1., -0.7, -0.4, 0., 0.4, 0.7, 1.], [-1., -0.75, -0.45, 0., 0.45, 0.75, 1.]],
          "weight": [[-1.75, -1., -0.5, 0.5, 1., 1.75], [-1.8, -1.05, -0.55, 0.55, 1.05, 1.8]]}
    ET = json.dumps(ET)
    NT = json.dumps(NT)

    inputs = {'stock_ex_price': stock_ex_price,
              'distnet_costs': distnet_costs,
              'service_cost': DLK,
              'taxes': abgaben}
    props = {'weight_ET': ET,
             'weight_NT': NT}

    outputs = Model.test(inputs, props)
