from planar_magnetics.utils import dcr_of_annulus
from planar_magnetics.windings import Spiral
from planar_magnetics.geometry import Point
import math

# test for issue-10
def test_single_turn_resistance_estimation():
    inner_radius = 100
    outer_radius = 101
    thickness = 0.1

    # create large thin single turn
    spiral = Spiral(
        at=Point(0, 0),
        inner_radius=inner_radius,
        outer_radius=outer_radius,
        num_turns=1,
        spacing=0.1,
    )

    # estimate the resistance using the estimate_dcr method
    dcr = spiral.estimate_dcr(thickness=thickness)

    # estimate the resistance using the resistance of annulus helper function
    expected = dcr_of_annulus(thickness, inner_radius, outer_radius)
    assert math.isclose(dcr, expected)


if __name__ == "__main__":
    test_single_turn_resistance_estimation()
