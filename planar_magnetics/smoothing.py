from __future__ import annotations
from dataclasses import dataclass
import math
import uuid


def find_center(a: Point, b: Point, c: Point):
    """Find the center of a circle through three points

    Args:
        a (Point): A first point
        b (Point): A second point
        c (Point): A third point

        Returns:
            Point: The center of the circle that intersects the three points
    """
    temp = b.x ** 2 + b.y ** 2
    ab = (a.x ** 2 + a.y ** 2 - temp) / 2
    bc = (temp - c.x ** 2 - c.y ** 2) / 2
    det = (a.x - b.x) * (b.y - c.y) - (b.x - c.x) * (a.y - b.y)

    assert abs(det) > 1e-10, "Determinant must be non-zero to find circle center"

    # Center of circle
    x = (ab * (b.y - c.y) - bc * (a.y - b.y)) / det
    y = ((a.x - b.x) * bc - (b.x - c.x) * ab) / det

    return Point(x, y)


def find_smoothing_arc(point: Point, arc: Arc, radius: float):
    """Find smoothing arc between point and arc

    Assuming you have a section of polygon formed from a line segment to an arc, this finds the arc
    that can be inserted between the line segment and the arc which is tangential to each

    Args:
        p (Point): The point
        arc (Arc): The Arc

    Returns:
        (Arc): The smoothing corner arc
    """

    # find the radius and center of the arc
    c = find_center(arc.start, arc.mid, arc.end)
    r = abs(arc.start - c)

    p1 = point - c
    p2 = arc.start - c
    delta = p1 - p2

    R = abs(delta)
    alpha = math.atan2(delta.y, -delta.x)
    angle = (
        math.asin(
            (radius * abs(delta) - delta.x * p1.y + delta.y * p1.x) / (r - radius) / R
        )
        - alpha
    )

    # derive center
    x = (r - radius) * math.cos(angle)
    y = (r - radius) * math.sin(angle)
    center = Point(x, y) + c

    end_angle = angle + 2 * math.pi
    start_angle = math.pi / 2 + math.atan2(delta.y, delta.x)

    return arc_from_polar(radius, start_angle, end_angle) + center


def round_corner(arc1: Arc, arc2: Arc, radius: float):
    corner = find_smoothing_arc(arc1.end, arc2, radius)
    arcs = [
        arc1,
        corner,
        Arc(corner.end, arc2.mid, arc2.end),
    ]
    return arcs


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


# def smooth(polygon: Polygon, radius: float):
#     points = polygon.points
#     N = len(points)


#     arcs = round_corner(points[-N], points[-N+1], radius)


#     for a, b in pairwise(polygon.points):
#         if a.end == b.start:
#             points.extend([a, b])
#             continue

#         points.extend(round_corner(a, b, radius))

#     return Polygon(points, polygon.layer, polygon.width, polygon.fill)


if __name__ == "__main__":
    point = Point(-10e-3, 0)
    start = Point(-10e-3, -4.740726435806956e-3)
    mid = Point(10.79682080774686e-3, 2.429639393935523e-3)
    end = Point(-11.066819197003216e-3, 0)
    arc = Arc(start, mid, end)

    # point = Point(0, -1e-3)
    corner = find_smoothing_arc(point, arc, 0.5e-3)

    print(corner)
