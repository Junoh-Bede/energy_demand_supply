import pandas as pd
from fuel_cell import FC
import datetime


def calculate_demand_side(data, heat_storage=False, ef_h=1, ef_w=1, ef_c=1.3):
    """
    prepare demand data for optimization
    """
    data['doy'] = data['Date'].apply(lambda x: datetime.datetime.fromisoformat(x).date())
    if heat_storage:
        grouped = data[['Qhs_sys_kWh', 'Qww_sys_kWh', 'Qcs_sys_kWh', 'doy']].groupby('doy').mean()
        data = data.merge(grouped, how='left', left_on=['doy'], right_index=True, suffixes=("_x", ""))
        data.drop(['Qhs_sys_kWh_x', 'Qww_sys_kWh_x', 'Qcs_sys_kWh_x'], inplace=True, axis=1)
    interim_df = pd.DataFrame()
    interim_df['ele'] = data['Eal_kWh'] + data['Ev_kWh'] + data['Eve_kWh'] + data['Edata_kWh'] + data['Epro_kWh']
    interim_df['heating'] = data['Qhs_sys_kWh']
    interim_df['hotwater'] = data['Qww_sys_kWh']
    interim_df['cooling'] = data['Qcs_sys_kWh']
    interim_df['heat_tot'] = interim_df['heating'] / ef_h + interim_df['hotwater'] / ef_w + interim_df['cooling'] / ef_c
    interim_df['doy'] = data['doy']
    daily_min_energy = interim_df.groupby('doy').min()[['ele', 'heat_tot']]
    interim_df = interim_df.merge(daily_min_energy, how='left', left_on=['doy'], right_index=True, suffixes=("", "_mn"))
    interim_df['energy'] = interim_df.apply(
        lambda x: [x['ele_mn'], x['heat_tot_mn']], axis=1)
    return interim_df


def optimize(data, fc_module, ef_h=1, ef_w=1, ef_c=1.3, ehp_h=2.7, ehp_w=2.7, ehp_c=3):
    data['fc_fuel'] = data['energy'].apply(fc_module.fuel_function)
    data['fc_heat'] = data['fc_fuel'].apply(fc_module.calculate_heat)
    data['fc_ele'] = data['fc_fuel'].apply(fc_module.calculate_electricity)
    heat_raw = data['heating'] / ef_h + data['hotwater'] / ef_w + data['cooling'] / ef_c
    fc_heat_proportion_raw = data['fc_heat'] / heat_raw
    fc_heat_proportion = fc_heat_proportion_raw.apply(lambda x: min([x, 1]))
    ehp_heat_proportion = 1 - fc_heat_proportion
    ehp_heating = ehp_heat_proportion * data['heating']
    ehp_hotwater = ehp_heat_proportion * data['hotwater']
    ehp_cooling = ehp_heat_proportion * data['cooling']
    data['ehp_ele'] = ehp_heating / ehp_h + ehp_hotwater / ehp_w + ehp_cooling / ehp_c
    ele_summary = data['ele'] + data['ehp_ele'] - data['fc_ele']
    data['grid_ele'] = ele_summary.apply(lambda x: max([0, x]))
    data['surplus_ele'] = ele_summary.apply(lambda x: -min([0, x]))
    heat_summary = heat_raw - data['fc_heat']
    data['surplus_heat'] = heat_summary.apply(lambda x: -min([0, x]))
    print(data)
    return data[['ele', 'ehp_ele', 'heating', 'hotwater', 'cooling', 'fc_fuel', 'fc_ele', 'fc_heat',
                 'grid_ele', 'surplus_ele', 'surplus_heat']]


def main(data_path, c_e=0.49, c_h=0.36):
    basic_data = pd.read_csv(data_path)
    interim_data = calculate_demand_side(basic_data)
    result = optimize(interim_data, FC(c_e, c_h, 2))
    result.to_csv("result_sample.csv")


if __name__ == "__main__":
    main("sample.csv")


