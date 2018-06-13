import numpy as np


def prep_prop_array(date):

    # Length of date array
    l_date = len(date)

    # Create array with country indexes and its length
    country_index = np.linspace(1, 24, 24)
    l_country = len(country_index)

    # Create array combining time and country array
    country_pred = np.tile(country_index, (1, l_date))
    date_pred = np.tile(date, (l_country, 1))
    date_pred = np.sort(date_pred, axis=None)
    date_pred = date_pred[np.newaxis]

    prop_array = np.column_stack((date_pred, country_pred))

    return prop_array
