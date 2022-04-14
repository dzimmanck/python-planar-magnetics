from dataclasses import dataclass


@dataclass
class Conductor:
    resistivity: float
    temperature_coeff: float

    def get_resistivity(self, temperature: float):

        return self.resistivity * (1 + self.temperature_coeff * (temperature - 25))


# define some common materials as constants
COPPER = Conductor(1.68e-8, 0.0038)
