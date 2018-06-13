import numpy as np

from .NN_functions import func_NeuralNetwork

def calc_demand(nn_input):

    # calculation of demand per date and country
    demand_GW_i = func_NeuralNetwork(nn_input)

    # summarize per date over countries
    num_country = np.unique(nn_input[:,4])
    demand_GW = np.add.reduceat(demand_GW_i, np.arange(0, len(demand_GW_i), num_country))

    # convert GW to W
    demand = np.multiply(demand_GW, 10e9)

    return demand