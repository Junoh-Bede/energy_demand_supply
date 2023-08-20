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
    interim_df['doy'] = data['doy']
    daily_min_energy = interim_df.groupby('doy').min()
    interim_df = interim_df.merge(daily_min_energy, how='left', left_on=['doy'], right_index=True, suffixes=("", "_mn"))
    interim_df['energy'] = interim_df.apply(
        lambda x: [x['ele_mn'],
                   x['heating_mn'] / ef_h + x['hotwater_mn'] / ef_w + x['cooling_mn'] / ef_c], axis=1)
    return interim_df


def optimize(data, fc_module):
    data['fc_fuel'] = data['energy'].apply(fc_module.fuel_function)
    data['fc_heat'] = data['fc_fuel'].apply(fc_module.calculate_heat)
    print(data)
    return data


def main(data_path, c_e=0.49, c_h=0.36):
    basic_data = pd.read_csv(data_path)
    interim_data = calculate_demand_side(basic_data)
    optimize(interim_data, FC(c_e, c_h, 0))


if __name__ == "__main__":
    main("sample.csv")


