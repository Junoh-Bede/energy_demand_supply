from optimize import optimize_model
import pandas as pd


def main():
    df = pd.read_csv("sample.csv")
    capacity_range = range(1, 5000)
    optimize_model(df, capacity_range, 3).to_csv("/Users/junoh/Documents/04_gradschool/result.csv")


if __name__ == "__main__":
    main()
