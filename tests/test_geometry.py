import numpy as np
import math
from planar_magnetics.geometry import Point, get_distance


def test_get_distance():
    p0 = Point(1, 1)
    p1 = Point(0, 0)
    p2 = Point(2, 0)
    distance = get_distance(p0, p1, p2)
    assert math.isclose(distance, 1)


if __name__ == "__main__":
    test_get_distance()
