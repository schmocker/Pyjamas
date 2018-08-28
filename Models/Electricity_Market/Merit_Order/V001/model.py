from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

class Model(Supermodel):

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['fut'] = Input(name='Futures', unit='s', info='utc time array in seconds since epoch',
                                   example='[1530792535, 1530792540, 1530792545]')

        self.inputs['demand'] = Input(name='European demand', unit='W',
                                      info='European power demand for each time step')
        self.inputs['power'] = Input(name='Power', unit='W',
                                     info='Power for each power plant and time step')
        self.inputs['marginal_costs'] = Input(name='Marginal costs', unit='€/J',
                                              info='Marginal costs for each power plant')
        self.inputs['distance_costs'] = Input(name='Distance costs', unit='€/J',
                                              info='Distance costs for each power plant and distribution network')

        self.properties["filter_ts"] = Property(default=0, data_type=int, name='Filter time step for view', info='Filter info', example='exampl')
        self.properties["filter_dn"] = Property(default=0, data_type=int, name='Filter distribution network for view')
        self.properties["filter_dn"] = Property(default=0, data_type=int, name='Filter distribution network for view')

        self.outputs['market_prices'] = Output(name='Market prices', unit='€/J',
                                               info='Market prices for each distribution network and time step')
        self.outputs['all_data'] = Output(name='All Data', unit='-',
                                               info='All data sorted by merit order for each distribution network and time step')



    async def func_peri(self, prep_to_peri=None):
        demands = await self.get_input("demand")  # f(time)
        powers = await self.get_input("power")  # f(time, pp)
        marginal_costs = await self.get_input("marginal_costs")  # f(pp)
        distance_costs = await self.get_input("distance_costs")  # f(pp, distNet)
        times = await self.get_input("fut")

        data = {'distribution_networks': distance_costs['distribution_networks'],
                'times': times,
                'market_price': [],
                'demand': demands,
                'power_plants': []}



        p_sort_order = np.argsort(powers['power_plant_id'])
        mc_sort_order = np.argsort(marginal_costs['power_plant_id'])
        dc_sort_order = np.argsort(distance_costs['power_plants'])


        fil_ts = self.get_property("filter_ts")
        fil_dn = self.get_property("filter_dn")

        for i_dn in range(len(distance_costs['distribution_networks'])):
            dn_id = distance_costs['distribution_networks'][0]
            data['market_price'].append([])
            data['power_plants'].append([])
            m_c = np.array(marginal_costs['MarginalCost'])[mc_sort_order]  # for each pp
            for i_ts in range(len(demands)):
                d = demands[i_ts]
                pp_ids = np.array(powers['power_plant_id'])[p_sort_order]
                p = np.array(powers['scaled_power'])[p_sort_order, i_ts]  # for each pp
                #m_c = np.array(marginal_costs['MarginalCost'])[mc_sort_order, i_ts]  # for each pp
                d_c = np.array(distance_costs['costs'])[dc_sort_order, i_dn]  # for each pp

                # sort all by arrays by the ascending costs
                sort_order = np.argsort(m_c + d_c)
                pp_ids = pp_ids[sort_order]
                m_c = m_c[sort_order]
                d_c = d_c[sort_order]
                c = m_c + d_c  # for each pp
                p = p[sort_order]
                try:
                    price = c[np.where(np.cumsum(p) >= d)[0][0]]
                except Exception as E:
                    price = np.max(c)
                # plot_merit_order(m_c, d_c, p, d, price)


                pp = {'ids': pp_ids.tolist(),
                      'm_c': m_c.tolist(),
                      'd_c': d_c.tolist(),
                      'c': c.tolist(),
                      'p': p.tolist()}
                data['power_plants'][i_dn].append(pp)
                data['market_price'][i_dn].append(price)

        prices = {'distribution_networks': distance_costs['distribution_networks'],
                  'prices': data['market_price']}

        self.set_output("market_prices", prices)
        self.set_output("all_data", data)





def plot_merit_order(m_c, d_c, powers, demand, price):

    cum_powers = np.cumsum(np.insert(powers, 0, 0))
    cp = cum_powers
    c = m_c + d_c

    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]

    mc_verts = [[(cp[i], 0.),(cp[i],m_c[i]),(cp[i+1],m_c[i]),(cp[i+1], 0.),(cp[i], 0.)] for i in range(len(c))]
    mc_paths = [Path(vert, codes) for vert in mc_verts]
    mc_patches = [patches.PathPatch(path, facecolor='orange', lw=1) for path in mc_paths]

    dc_verts = [[(cp[i], m_c[i]),(cp[i],m_c[i]+d_c[i]),(cp[i+1],m_c[i]+d_c[i]),(cp[i+1], m_c[i]),(cp[i], m_c[i])] for i in range(len(c))]
    dc_paths = [Path(vert, codes) for vert in dc_verts]
    dc_patches = [patches.PathPatch(path, facecolor='green', lw=1) for path in dc_paths]

    x_lim = np.max(cum_powers)
    y_lim = np.max(c)


    fig = plt.figure()
    ax = fig.add_subplot(111)
    [ax.add_patch(patch) for patch in mc_patches]
    [ax.add_patch(patch) for patch in dc_patches]

    a_x = x_lim/50
    a_y = y_lim/50
    ax.arrow(demand, 0, 0, price-a_y, head_width=a_x, head_length=a_y, fc='b', ec='b',)
    ax.arrow(demand, price, -demand+a_x, 0, head_width=a_y, head_length=a_x, fc='b', ec='b')

    ax.set_xlim(0, x_lim)
    ax.set_ylim(0, y_lim)
    plt.show()


if __name__ == "__main__":
    n_ts = 96
    n_kw = 200
    n_dist = 3

    # ids
    pp_ids_p = [i for i in range(n_kw)]
    np.random.shuffle(pp_ids_p)
    pp_ids_mc = [i for i in range(n_kw)]
    np.random.shuffle(pp_ids_mc)
    pp_ids_dc = [i for i in range(n_kw)]
    np.random.shuffle(pp_ids_dc)

    dist_ids = [i for i in range(n_dist)]
    np.random.shuffle(dist_ids)

    # data
    demands = (np.random.rand(n_ts)*1000+1000).tolist()
    powers = [(np.random.rand(n_ts)*50+3).tolist() for i in pp_ids_p]
    marginal_costs = [(np.random.rand(n_ts)*50+5).tolist() for i in pp_ids_mc]
    distance_costs = [(np.random.rand(n_dist)*20).tolist() for i in pp_ids_dc]

    inputs = {
        'demand': demands,
        'power': {'power_plants': pp_ids_p,
                  'powers': powers},
        'marginal_costs': {'power_plants': pp_ids_mc,
                           'costs': marginal_costs},
        'distance_costs': {'power_plants': pp_ids_dc,
                           'distribution_networks': dist_ids,
                           'costs': distance_costs}
    }

    # res = calc_merit_orders(inputs['demand'], inputs['power'], inputs['marginal_costs'], inputs['distance_costs'])

    properties = {}

    outputs = Model.test(inputs, properties)

    print(outputs)


