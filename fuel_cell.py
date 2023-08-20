
class FC:
    def __init__(self, c_e, c_h):
        self.c_e = c_e
        self.c_h = c_h

    def calculate_heat(self, fuel):
        return self.c_h * fuel

    def calculate_electricity(self, fuel):
        return self.c_e * fuel

    def heat_based_fuel(self, heat):
        return heat / self.c_h

    def ele_based_fuel(self, ele):
        return ele / self.c_e

    def min_based_fuel(self, heat, ele):
        return min([self.heat_based_fuel(heat), self.ele_based_fuel(ele)])

    def max_based_fuel(self, heat, ele):
        return max([self.heat_based_fuel(heat), self.ele_based_fuel(ele)])


