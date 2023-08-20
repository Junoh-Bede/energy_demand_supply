from match_demand_supply import calculate_demand_side, calculate_supply_side
from fuel_cell import FC
import pandas as pd


def main():
    df = pd.read_csv("sample.csv")
    demand_calculated = calculate_demand_side(df)
    result = calculate_supply_side(demand_calculated, FC(0.45, 0.38, 2))
    result.to_csv("result_sample.csv")


if __name__ == "__main__":
    main()
