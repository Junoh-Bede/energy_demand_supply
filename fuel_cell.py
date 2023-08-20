
class FC:
    def __init__(self, c_e, c_h, operation, capacity):
        self.c_e = c_e
        self.c_h = c_h
        self.operation = operation
        self.capacity = capacity

    def calculate_heat(self, fuel):
        return self.c_h * fuel

    def calculate_electricity(self, fuel):
        return self.c_e * fuel

    def heat_based_fuel(self, energy):
        heat = energy[1]
        return min([heat / self.c_h, self.capacity / self.c_e])

    def ele_based_fuel(self, energy):
        ele = energy[0]
        return min([ele / self.c_e, self.capacity / self.c_e])

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
