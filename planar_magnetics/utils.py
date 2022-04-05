import math


def weight_to_thickness(weight: float):
    """Converter a copper weight to a thickness

    Converters a copper weight (oz) to a thickess (meters)

    Args:
        weight: weight of copper layer in oz

    Returns:
        float: The copper thickness in meters
    """

    return 35e-6 * weight


def dcr_of_annulus(
    thickness: float, inner_radius: float, outer_radius: float, rho: float = 1.68e-8
):
    """Calculate the sheet resistance of an annulus
    """

    resistance = (2 * math.pi * rho) / (
        thickness * (math.log(outer_radius / inner_radius))
    )

    return resistance
