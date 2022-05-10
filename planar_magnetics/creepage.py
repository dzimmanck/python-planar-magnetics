from enum import Enum


class Classification(Enum):
    B1 = 1, "Internal Conductors"
    B2 = 2, "External Conductors, uncoated, sea level to 3050 m"
    B3 = 3, "External Conductors, uncoated, over 3050 m"
    B4 = 4, "External Conductors, with permanent polymer coating (any elevation)"
    A5 = 5, "External Conductors, with conformal coating over assembly (any elevation)"
    A6 = 6, "External Component lead/termination, uncoated"
    A7 = (
        7,
        "External Component lead termination, with conformal coating (any elevation)",
    )

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, description: str = None):
        self._description_ = description

    def __str__(self):
        return self.description

    # this makes sure that the description is read-only
    @property
    def description(self):
        return self._description_


# Creepage table
CREEPAGE_TABLE = {
    15: [0.05, 0.1, 0.1, 0.05, 0.13, 0.13, 0.13],
    30: [0.05, 0.1, 0.1, 0.05, 0.13, 0.25, 0.13],
    50: [0.1, 0.6, 0.6, 0.13, 0.13, 0.4, 0.13],
    100: [0.1, 0.6, 1.5, 0.13, 0.13, 0.5, 0.13],
    150: [0.2, 0.6, 3.2, 0.4, 0.4, 0.8, 0.4],
    170: [0.2, 1.25, 3.2, 0.4, 0.4, 0.8, 0.4],
    250: [0.2, 1.25, 6.4, 0.4, 0.4, 0.8, 0.4],
    300: [0.2, 1.25, 12.5, 0.4, 0.4, 0.8, 0.4],
    500: [0.25, 2.5, 12.5, 0.8, 0.8, 1.5, 0.8],
}

PER_VOLT_TABLE = [
    0.0025,
    0.005,
    0.025,
    0.00305,
    0.00305,
    0.00305,
    0.00305,
]


def calculate_creepage(voltage: float, classification: Classification):
    """Calculates the minimum creepage distance

    Args:
        voltage: RMS voltage

    Returns:
        float: The recommended creepage distance

    """

    # re-cast to classification to allow users to pass an integer as the classification
    classification = Classification(classification)

    for key, value in CREEPAGE_TABLE.items():
        if key >= voltage:
            return value[classification.value - 1]

    # if the voltage is >500V, the per/volt table must be added
    base_volt = CREEPAGE_TABLE[500][classification.value - 1]
    per_volt = PER_VOLT_TABLE[classification.value - 1]
    creepage = base_volt + (voltage - 500) * per_volt
    return creepage


if __name__ == "__main__":

    classification = Classification(3)
    print(classification)
    creepage = calculate_creepage(1000, 3)
    print(creepage)
