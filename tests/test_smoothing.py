import math
from planar_magnetics.geometry import Point, Arc, get_distance, Polygon, PI_OVER_TWO
from planar_magnetics.smoothing import smooth_point_to_arc_dbg as smooth_point_to_arc


def create_circle(arc):
    circle = Arc(arc.center, arc.radius, -math.pi, math.pi - 0.001)
    return circle


def check_tangential(point: Point, arc: Arc, corner: Arc):
    distance = get_distance(corner.center, point, arc.start)

    assert math.isclose(distance, corner.radius)

    center_to_center = abs(arc.center - corner.center)

    if arc.rotates_clockwise():
        arc_angle = arc.start_angle - PI_OVER_TWO
    else:
        arc_angle = arc.start_angle + PI_OVER_TWO

    # calculate the angle of the vector p1 to p2
    delta = arc.start - point
    segment_angle = math.atan2(delta.y, delta.x)

    # calculate the distance from the center of the arc to the center of the corner
    # if the segment intersects from the inside of the circle, it will be arc.radius - radius
    # if the segment intersects from the outside of the circle, it will be arc.radius + radius
    if segment_angle > arc_angle:
        assert math.isclose(center_to_center, arc.radius - corner.radius)
    else:
        assert math.isclose(center_to_center, arc.radius + corner.radius)


# -0.008262556694703485 -0.004212454071362315
# 0.0 0.0 0.00823528137423857 3.141592653589793 -1.41347928619736


def test_point_to_arc_smoothing():
    point = Point(-0.009, -0.004212454071362315)
    arc = Arc(Point(0, 0), 0.00823528137423857, 3.141592653589793, -1.41347928619736)

    corner = smooth_point_to_arc(point, arc, 2e-3)

    print(corner.start_angle, corner.end_angle)
    import matplotlib.pyplot as mp

    path = Polygon([point, arc]).to_pwl_path(math.pi / 200)
    x, y = zip(*path)
    mp.plot(x, y, "r--")

    path = Polygon([corner]).to_pwl_path(math.pi / 200)
    x, y = zip(*path)
    mp.plot(x, y, "b--")

    mp.axis("equal")
    mp.show()

    check_tangential(point, arc, corner)


if __name__ == "__main__":
    test_point_to_arc_smoothing()
