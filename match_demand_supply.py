import pandas as pd
import datetime


def calculate_demand_side(data, heat_storage=False, ef_h=1, ef_w=1, ef_c=1.3):
    """
    calculates demand side of energy mix
    :param data: dataframe contains datetime value, electricity demand, heating demand, hot water demand,
                cooling demand, and PV electricity generation.
    :param heat_storage: Boolean data indicates whether there is heat storage system
    :param ef_h: efficiency of heat recovery of fuel cell modules for heating
    :param ef_w: efficiency of heat recovery of fuel cell modules for hot water
    :param ef_c: efficiency of heat recovery of fuel cell modules for cooling
    :return: dataframe contains the energy mix result on demand side
    """
    data['doy'] = data['Date'].apply(lambda x: datetime.datetime.fromisoformat(x).date())
    if heat_storage:
        grouped = data[['Qhs_sys_kWh', 'Qww_sys_kWh', 'Qcs_sys_kWh', 'doy']].groupby('doy').mean()
        data = data.merge(grouped, how='left', left_on=['doy'], right_index=True, suffixes=("_x", ""))
        data.drop(['Qhs_sys_kWh_x', 'Qww_sys_kWh_x', 'Qcs_sys_kWh_x'], inplace=True, axis=1)
    interim_df = pd.DataFrame()
    interim_df['Date'] = data['Date']
    interim_df['ele'] = data['Eal_kWh'] + data['Ev_kWh'] + data['Eve_kWh'] + data['Edata_kWh'] + data['Epro_kWh']
    interim_df['pv_ele'] = data['E_PV_gen_kWh']
    interim_df['heating'] = data['Qhs_sys_kWh']
    interim_df['hotwater'] = data['Qww_sys_kWh']
    interim_df['cooling'] = data['Qcs_sys_kWh']
    interim_df['heat_tot'] = interim_df['heating'] / ef_h + interim_df['hotwater'] / ef_w + interim_df['cooling'] / ef_c
    interim_df['doy'] = data['doy']
    interim_df['net_ele'] = interim_df['ele'] - interim_df['pv_ele']
    daily_min_energy = interim_df.groupby('doy').min()[['net_ele', 'heat_tot']]
    interim_df = interim_df.merge(daily_min_energy, how='left', left_on=['doy'], right_index=True, suffixes=("", "_mn"))
    interim_df['energy'] = interim_df.apply(lambda x: [max([0, x['net_ele_mn']]), x['heat_tot_mn']], axis=1)
    return interim_df


def calculate_supply_side(data, fc_module, ef_h=1, ef_w=1, ef_c=1.3, ehp_h=2.7, ehp_w=2.7, ehp_c=3):
    """
    calculates supply side of energy mix
    :param data: dataframe contains demand side of energy mix
    :param fc_module: FC object with specification of fuel
    :param ef_h: efficiency of heat recovery of fuel cell modules for heating
    :param ef_w: efficiency of heat recovery of fuel cell modules for hot water
    :param ef_c: efficiency of heat recovery of fuel cell modules for cooling
    :param ehp_h: efficiency of electric heat pump for heating
    :param ehp_w: efficiency of electric heat pump for hot water
    :param ehp_c: efficiency of electric heat pump for cooling
    :return: dataframe contains supply side of energy mix
    """
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
    ele_summary = data['ele'] + data['ehp_ele'] - data['fc_ele'] - data['pv_ele']
    data['grid_ele'] = ele_summary.apply(lambda x: max([0, x]))
    data['surplus_ele'] = ele_summary.apply(lambda x: -min([0, x]))
    heat_summary = heat_raw - data['fc_heat']
    data['surplus_heat'] = heat_summary.apply(lambda x: -min([0, x]))
    return data[['Date', 'ele', 'ehp_ele', 'heating', 'hotwater', 'cooling', 'fc_fuel', 'fc_ele', 'fc_heat',
                 'grid_ele', 'pv_ele', 'surplus_ele', 'surplus_heat']]




