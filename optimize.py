from match_demand_supply import calculate_demand_side, calculate_supply_side
from fuel_cell import FC
import pandas as pd
from tqdm import tqdm


def optimize_model(data, capacities, operation):
    demand_calculated = calculate_demand_side(data)
    results = []
    for capacity in tqdm(capacities):
        result = calculate_supply_side(demand_calculated, FC(0.45, 0.38, operation, capacity))
        operational_rate = result['fc_ele'].mean() / capacity
        self_sufficiency = ((result['fc_ele'] + result['pv_ele'] - result['surplus_ele']
                             ) / (result['ele'] + result['ehp_ele'])).mean()
        self_consumption = ((result['ele'] + result['ehp_ele'] - result['grid_ele']) / (
                result['fc_ele'] + result['pv_ele'])).mean()
        average_index = (self_sufficiency + self_consumption) / 2
        results.append([result, operational_rate, average_index, capacity])
    results = [i for i in results if i[1] >= 0.7]
    if len(results) != 0:
        print(max(results, key=lambda x: x[2])[1], max(results, key=lambda x: x[2])[2],
              max(results, key=lambda x: x[2])[3])
        return max(results, key=lambda x: x[2])[0]
    else:
        return pd.DataFrame()


