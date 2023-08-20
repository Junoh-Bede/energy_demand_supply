
class FC:
    def __init__(self, c_e, c_h, operation):
        self.c_e = c_e
        self.c_h = c_h
        self.operation = operation

    def calculate_heat(self, fuel):
        return self.c_h * fuel

    def calculate_electricity(self, fuel):
        return self.c_e * fuel

    def heat_based_fuel(self, energy):
        heat = energy[1]
        return heat / self.c_h

    def ele_based_fuel(self, energy):
        ele = energy[0]
        return ele / self.c_e

    def min_based_fuel(self, energy):
        return min([self.heat_based_fuel(energy), self.ele_based_fuel(energy)])

    def max_based_fuel(self, energy):
        return max([self.heat_based_fuel(energy), self.ele_based_fuel(energy)])

    def fuel_function(self, energy):
        if self.operation == 0:
            return self.min_based_fuel(energy)
        elif self.operation == 1:
            return self.ele_based_fuel(energy)
        elif self.operation == 2:
            return self.heat_based_fuel(energy)
        else:
            return self.max_based_fuel(energy)
