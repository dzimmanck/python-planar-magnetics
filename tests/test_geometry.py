import numpy as np
import math
from planar_magnetics.geometry import find_center, arc_from_polar, Point


def test_find_center():
    centers = []
    for x in np.linspace(-5, 5, 5):
        for y in np.linspace(-5, 5, 5):
            centers.append(Point(x, y))

    radii = np.linspace(0.1, 2, 5)
    angles = np.linspace(-2 * np.pi, 2 * np.pi, 10)
    for radius in radii:
        for start_angle in angles:
            for end_angle in angles:
                for expected in centers:
                    arc = arc_from_polar(radius, start_angle, end_angle) + expected

                    try:
                        center = find_center(arc.start, arc.mid, arc.end)
                    except AssertionError:
                        continue

                    assert math.isclose(center.x, expected.x, abs_tol=1e-6)
                    assert math.isclose(center.y, expected.y, abs_tol=1e-6)


if __name__ == "__main__":
    test_find_center()
