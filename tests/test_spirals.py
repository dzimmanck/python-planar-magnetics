from planar_magnetics.utils import dcr_of_annulus
from planar_magnetics.windings import Spiral
from planar_magnetics.geometry import Point
import math


def test_single_turn_resistance_estimation():
    # create large thin single turn
    spiral = Spiral(
        Point(0, 0), inner_radius=100, outer_radius=101, num_turns=1, gap=0.1
    )

    # estimate the resistance using the estimate_dcr method
    dcr = spiral.estimate_dcr(thickness=0.1)

    # estimate the resistance using the resistane of annulus helper function
    expected = dcr_of_annulus(0.1, 100, 101)
    print(dcr, expected)
    assert math.isclose(dcr, expected)


if __name__ == "__main__":
    test_single_turn_resistance_estimation()
