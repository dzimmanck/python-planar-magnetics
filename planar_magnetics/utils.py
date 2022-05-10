import math
from planar_magnetics.materials import Conductor, COPPER


def weight_to_thickness(weight: float):
    """Converter a copper weight to a thickness

    Converters a copper weight (oz) to a thickness (meters)

    Args:
        weight: weight of copper layer in oz

    Returns:
        float: The copper thickness in mm
    """

    return 35e-3 * weight


def thickness_to_weight(thickness: float):
    """Converter a copper thickness to a weight

    Converters a copper thickness (m) to a weight (oz)

    Args:
        thickness: thickness of the layer in m

    Returns:
        float: The weight of the layer in oz
    """

    return 28571.428571428572 * thickness


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


def frequency_to_skin_depth(
    frequency: float, temperature: float = 25, material: Conductor = COPPER
):
    """Calculate the skin depth at a specific frequency
    """

    rho = material.get_resistivity(temperature)
    mu = material.permeability
    skin_depth = math.sqrt(2 * rho / (2 * math.pi * frequency * mu))

    return skin_depth


def skin_depth_to_frequency(
    skin_depth: float, temperature: float = 25, material: Conductor = COPPER
):
    """Calculate the frequency at a specific skin depth
    """

    rho = material.get_resistivity(temperature)
    mu = material.permeability
    frequency = 2 * rho / (2 * math.pi * skin_depth ** 2 * mu)

    return frequency


if __name__ == "__main__":
    frequency = skin_depth_to_frequency(weight_to_thickness(4))
    print(frequency)
