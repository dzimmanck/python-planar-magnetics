from enum import Enum


class PollutionDegree(Enum):
    One = 1
    Two = 2


# Creepage table from DIN EN 60664-1 (VDE-0110-1)
CREEPAGE_TABLE = {
    25: {PollutionDegree.One: 0.025e-3, PollutionDegree.Two: 0.040e-3},
    32: {PollutionDegree.One: 0.025e-3, PollutionDegree.Two: 0.040e-3},
    40: {PollutionDegree.One: 0.025e-3, PollutionDegree.Two: 0.040e-3},
    50: {PollutionDegree.One: 0.025e-3, PollutionDegree.Two: 0.040e-3},
    63: {PollutionDegree.One: 0.040e-3, PollutionDegree.Two: 0.063e-3},
    80: {PollutionDegree.One: 0.063e-3, PollutionDegree.Two: 0.100e-3},
    100: {PollutionDegree.One: 0.100e-3, PollutionDegree.Two: 0.160e-3},
    125: {PollutionDegree.One: 0.160e-3, PollutionDegree.Two: 0.250e-3},
    160: {PollutionDegree.One: 0.250e-3, PollutionDegree.Two: 0.400e-3},
    200: {PollutionDegree.One: 0.400e-3, PollutionDegree.Two: 0.630e-3},
    250: {PollutionDegree.One: 0.560e-3, PollutionDegree.Two: 1.000e-3},
    320: {PollutionDegree.One: 0.750e-3, PollutionDegree.Two: 1.600e-3},
    400: {PollutionDegree.One: 1.000e-3, PollutionDegree.Two: 2.000e-3},
    500: {PollutionDegree.One: 1.300e-3, PollutionDegree.Two: 2.500e-3},
    630: {PollutionDegree.One: 1.800e-3, PollutionDegree.Two: 3.200e-3},
    800: {PollutionDegree.One: 2.400e-3, PollutionDegree.Two: 4.000e-3},
    1000: {PollutionDegree.One: 3.200e-3, PollutionDegree.Two: 5.000e-3},
}


def weight_to_thickness(weight: float):
    """Converter a copper weight to a thickness

    Converters a copper weight (oz) to a thickess (meters)

    Args:
        weight: weight of copper layer in oz

    Returns:
        float: The copper thickness in meters
    """

    return 35e-6 * weight


def calculate_creepage(voltage: float, pollution_degree: PollutionDegree):
    """Calculates the minimum creepage distance

    Args:
        voltage: RMS voltage

    Returns:
        float: The recommended creepage distance as per DIN EN 60664-1 (VDE-0110-1)

    """

    for key, value in CREEPAGE_TABLE.items():
        if key >= voltage:
            return value[pollution_degree]

    raise Exception(f"{voltage}V is too high for standard PCB technology")
