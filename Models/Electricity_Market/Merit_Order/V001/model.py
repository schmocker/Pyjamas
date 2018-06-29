from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

class Model(Supermodel):

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['demand'] = Input(name='European demand', unit='W',
                                      info='European power demand for each time step')
        self.inputs['power'] = Input(name='Power', unit='W',
                                     info='Power for each power plant and time step')
        self.inputs['marginal_costs'] = Input(name='Marginal costs', unit='$/J',
                                              info='Marginal costs for each power plant and time step')
        self.inputs['distance_costs'] = Input(name='Distance costs', unit='$/J',
                                              info='Distance costs for each power plant and distribution network')

        self.outputs['market_prices'] = Output(name='Market prices', unit='$',
                                               info='Market prices for each distribution network and time step')

    async def func_peri(self, prep_to_peri=None):
        demand = await self.get_input("demand")
        power = await self.get_input("power")
        marginal_costs = await self.get_input("marginal_costs")
        distance_costs = await self.get_input("distance_costs")

        market_prices = [1,2,3,4]
        self.set_output("market_prices", market_prices)

def plot_merit_order(costs, powers, demand, price):

    cum_powers = np.cumsum(np.insert(powers, 0, 0))
    cp = cum_powers
    co = costs
    verts = [[(cp[i], 0.),(cp[i],co[i]),(cp[i+1],co[i]),(cp[i+1], 0.),(cp[i], 0.)] for i in range(len(costs))]

    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]

    paths = [Path(vert, codes) for vert in verts]

    x_lim = np.max(cum_powers)
    y_lim = np.max(costs)


    fig = plt.figure()
    ax = fig.add_subplot(111)
    patchees = [patches.PathPatch(path, facecolor='orange', lw=1) for path in paths]
    [ax.add_patch(patch) for patch in patchees]

    a_x = x_lim/50
    a_y = y_lim/50
    ax.arrow(demand, 0, 0, price-a_y, head_width=a_x, head_length=a_y, fc='b', ec='b',)
    ax.arrow(demand, price, -demand+a_x, 0, head_width=a_y, head_length=a_x, fc='b', ec='b')

    ax.set_xlim(0, x_lim)
    ax.set_ylim(0, y_lim)
    plt.show()

    r=5;




def calc_merit_order(demands, power, marginal_costs, distance_costs):
    pp_ids = power['power_plants']

    i =0;

    for dist_id in distance_costs['distribution_networks']:
        for i_ts in range(len(demands)):
            demand = demands[i_ts]
            powers = np.array(power['powers'])[:,i_ts] # for each pp
            m_c = np.array(marginal_costs['costs'])[:,i_ts] # for each pp
            d_c = np.array(distance_costs['costs'])[:,dist_id] # for each pp
            costs = m_c + d_c # for each pp
            sort_order = np.argsort(costs)

            m_c = m_c[sort_order]
            d_c = d_c[sort_order]
            costs = costs[sort_order]
            powers = powers[sort_order]

            cp = np.cumsum(powers)

            price = costs[np.where(cp > demand)[0][0]]
            plot_merit_order(costs, powers, demand, price)



            i = i + 1;


    print(i)
    return [1,2,3]


if __name__ == "__main__":
    n_ts = 30
    n_kw = 80
    n_dist = 3

    demands = (np.random.rand(n_ts)*1000+1000).tolist()
    pp_ids = [i for i in range(n_kw)]
    powers = [(np.random.rand(n_ts)*50+3).tolist() for i in pp_ids]
    marginal_costs = [(np.random.rand(n_ts)*50+5).tolist() for i in pp_ids]
    dist_ids = [i for i in range(n_dist)]
    distance_costs = [(np.random.rand(n_dist)*20).tolist() for i in pp_ids]

    inputs = {
        'demand': demands,
        'power': {'power_plants': pp_ids,
                  'powers': powers},
        'marginal_costs': {'power_plants': pp_ids,
                           'costs': marginal_costs},
        'distance_costs': {'power_plants': pp_ids,
                           'distribution_networks': dist_ids,
                           'costs': distance_costs}
    }
    res = calc_merit_order(inputs['demand'],
                           inputs['power'],
                           inputs['marginal_costs'],
                           inputs['distance_costs'])

    properties = {}

    outputs = Model.test(inputs, properties)

    print(outputs)


