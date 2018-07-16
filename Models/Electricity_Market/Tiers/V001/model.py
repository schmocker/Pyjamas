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
        self.inputs['stock_ex_price'] = Input(name='', unit='', info="")
        self.inputs['distnet_costs'] = Input(name='', unit='', info="")
        self.inputs['DLK'] = Input(name='', unit='', info="")
        self.inputs['Abgaben'] = Input(name='', unit='', info="")

        # define outputs
        self.outputs['tiers_prices'] = Output(name='???', unit='???', info='???')

        # define properties
        ET_def = {"border": [-1., -0.8, -0.3, 0., 0.3, 0.8, 1.],
              "weight": [-2., -1.25, -0.75, 0.75, 1.25, 2.]}
        NT_def = {"border": [-1., -0.7, -0.4, 0., 0.4, 0.7, 1.],
              "weight": [-1.75, -1., -0.5, 0.5, 1., 1.75]}
        self.properties['weight_ET'] = Property(default=ET_def, data_type=dict, name='energy tiers', unit='-', info='borders and weights of energy tiers')
        self.properties['weight_NT'] = Property(default=NT_def, data_type=dict, name='net tiers', unit='-', info='borders and weights of net tiers')


        # define persistent variables
        #self.data_hist = None

    async def func_birth(self):
        pass

    async def func_amend(self, keys=[]):
        pass

    async def func_peri(self, prep_to_peri=None):

        # read and determine borders and tiers
        border_tiers = self.det_border_tiers()


        print(border_tiers)

    def det_border_tiers(self):

        # read borders
        ET_border = self.get_property('weight_ET')["border"]
        NT_border = self.get_property('weight_NT')["border"]

        ET_border = np.array(ET_border)
        NT_border = np.array(NT_border)

        # merge
        borders = np.append(ET_border, NT_border)
        borders = np.unique(borders)

        # read tiers
        ET_tiers_orig = self.get_property('weight_ET')["weight"]
        NT_tiers_orig = self.get_property('weight_NT')["weight"]

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

            print(it)

        # return dict
        border_tiers = {'borders': borders,
                        'ET_tiers': ET_tiers,
                        'NT_tiers': NT_tiers}

        return border_tiers








if __name__ == "__main__":

    # input
    stock_ex_price = {'distribution_netowrks': ['Baden', 'Brugg'],
                      'prices': [[1, 2, 3], [1.1, 2.2, 3.3]]}
    distnet_costs = {'distribution_networks': stock_ex_price['distribution_netowrks'],
                    'costs': [100, 111]}
    DLK = [0.5]
    abgaben = [0.25]

    # properties
    ET = {"border": [-1., -0.8, -0.3, 0., 0.3, 0.8, 1.],
          "weight": [-2., -1.25, -0.75, 0.75, 1.25, 2.]}
    NT = {"border": [-1., -0.7, -0.4, 0., 0.4, 0.7, 1.],
          "weight": [-1.75, -1., -0.5, 0.5, 1., 1.75]}

    inputs = {'stock_ex_price': stock_ex_price,
              'distnet_costs': distnet_costs,
              'DLK': DLK,
              'Abgaben': abgaben}
    props = {'weight_ET': ET,
             'weight_NT': NT}

    outputs = Model.test(inputs, props)
