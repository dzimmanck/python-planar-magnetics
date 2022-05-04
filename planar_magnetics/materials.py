from dataclasses import dataclass


@dataclass
class Conductor:
    resistivity: float
    temperature_coeff: float

    def get_resistivity(self, temperature: float):

        return self.resistivity * (1 + self.temperature_coeff * (temperature - 25))


@dataclass
class Ferrite:
    permeability: float
    max_flux_density: float
    losses: dict

    def get_loss_density(f: float, B: float, temperature: float = 25):
        raise NotImplementedError


# define some common materials as constants
COPPER = Conductor(1.68e-8, 0.0038)

N96 = Ferrite(
    permeability=2900,
    max_flux_density=500,
    losses={
        25: {
            13: {1: 2, 3: 4, 5: 6},
            25: {1: 2, 3: 4, 5: 6},
            50: {1: 2, 3: 4, 5: 6},
            100: {1: 2, 3: 4, 5: 6},
            200: {1: 2, 3: 4, 5: 6},
            300: {1: 2, 3: 4, 5: 6},
        },
        100: {
            13: {1: 2, 3: 4, 5: 6},
            25: {1: 2, 3: 4, 5: 6},
            50: {1: 2, 3: 4, 5: 6},
            100: {1: 2, 3: 4, 5: 6},
            200: {1: 2, 3: 4, 5: 6},
            300: {1: 2, 3: 4, 5: 6},
        },
    },
)
