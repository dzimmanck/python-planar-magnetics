def weight_to_thickness(weight: float):
    """Converter a copper weight to a thickness

    Converters a copper weight (oz) to a thickess (meters)

    Args:
        weight: weight of copper layer in oz

    Returns:
        float: The copper thickness in meters
    """

    return 35e-6 * weight
