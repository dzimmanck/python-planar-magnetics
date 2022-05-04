import math


def weight_to_thickness(weight: float):
    """Converter a copper weight to a thickness

    Converters a copper weight (oz) to a thickess (meters)

    Args:
        weight: weight of copper layer in oz

    Returns:
        float: The copper thickness in mm
    """

    return 35e-3 * weight


def dcr_of_sheet(thickness: float, width: float, length: float, rho: float = 1.68e-8):
    """Calculate the resistance of a rectangular sheet
    """
    resistance = 1e3 * (length * rho) / (width * thickness)
    return resistance


def dcr_of_annulus(
    thickness: float, inner_radius: float, outer_radius: float, rho: float = 1.68e-8
):
    """Calculate the sheet resistance of an annulus
    """

    assert (
        outer_radius > inner_radius
    ), f"Outer radius must be greater than inner radius"

    resistance = (2e3 * math.pi * rho) / (
        thickness * (math.log(outer_radius / inner_radius))
    )

    return resistance
