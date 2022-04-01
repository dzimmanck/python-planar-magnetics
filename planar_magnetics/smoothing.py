from __future__ import annotations
from dataclasses import dataclass
import math
import uuid

from planar_magnetics.geometry import Point, Arc

TWO_PI = 2 * math.pi
PI_OVER_2 = math.pi / 2


def get_distance(p0: Point, p1: Point, p2: Point):
    """Calculate the distance between a point and a line

    Calculate the distance between a point p0 and a line formed between p1 and p2
    """

    p21 = p2 - p1
    p10 = p1 - p0

    return abs(p21.x * p10.y - p21.y * p10.x) / abs(p21)


def smooth_point_to_arc(point: Point, arc: Arc, radius: float):
    """Find smoothing arc that joins section of polygon formed from a point and an arc

    Assuming you have a section of polygon formed from a line segment to an arc, this finds the arc
    that can be inserted between the line segment and the arc which is tangential to each

    Args:
        p (Point): The point
        arc (Arc): The Arc

    Returns:
        (Arc): The smoothing corner arc
    """

    r = arc.radius

    p1 = point - arc.center
    p2 = arc.start - arc.center

    if arc.rotates_clockwise():
        delta = p2 - p1
    else:
        delta = p1 - p2

    # calculate the amplitude of the line segment
    R = abs(delta)

    # # -------------------------------------------------------
    # # equation for the distance between a point and a line
    # radius * R = abs(delta.x * (p1.y - y) - delta.y * (p1.x - x))

    # radius * R = delta.x * (p1.y - y) - delta.y * (p1.x - x)
    # radius * R = delta.y * (p1.x - x) - delta.x * (p1.y - y)

    # # sub in trig expressions for x and y
    # x = center_to_center * math.cos(angle)
    # y = center_to_center * math.sin(angle)

    # (radius * R + delta.y *p1.x - delta.x * p1.y) / center_to_center = delta.y * math.cos(angle) - delta.x * math.sin(angle)
    # (radius * R - delta.y *p1.x + delta.x * p1.y) / center_to_center = delta.x * math.sin(angle) - delta.y * math.cos(angle)

    # alpha = math.atan2(delta.y, -delta.x)
    # (radius * R + delta.y *p1.x - delta.x * p1.y) / center_to_center = R * math.sin(angle + alpha)

    # alpha = math.atan2(-delta.y, delta.x)
    # (radius * R - delta.y *p1.x + delta.x * p1.y) / center_to_center = R * math.sin(angle + alpha)

    # # -------------------------------------------------------

    # calculate the distance from the center of the arc to the center of the corner
    # if the segment intersects from the inside of the circle, it will be arc.radius - radius
    # if the segment intersects from the outside of the circle, it will be arc.radius + radius
    if abs(point - arc.center) < arc.radius:
        center_to_center = r - radius
    else:
        center_to_center = r + radius

    # calculate the angle of the vector from center to center
    alpha = math.atan2(delta.y, -delta.x)
    angle = (
        math.asin((radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R)
        - alpha
    )

    # # the arcsin function generates an angle that is between -pi and pi
    # # pi - angle is also a valid solution we need to check
    if arc.rotates_clockwise():
        angle = (
            math.pi
            - math.asin(
                (radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R
            )
            - alpha
        )
    else:

        # calculate the angle of the vector from center to center
        alpha = math.atan2(delta.y, -delta.x)
        angle = (
            math.asin(
                (radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R
            )
            - alpha
        )

    # derive center of the corner
    x = center_to_center * math.cos(angle)
    y = center_to_center * math.sin(angle)
    center = Point(x, y) + arc.center

    # derive the start and end angles
    start_angle = PI_OVER_2 + math.atan2(delta.y, delta.x)
    end_angle = angle

    # make sure the corner arc rotates in the same direction as the main arc
    if arc.rotates_clockwise():
        while start_angle < end_angle:
            start_angle += TWO_PI
    else:
        while start_angle > end_angle:
            start_angle -= TWO_PI

    print("s", start_angle)
    print("e", end_angle)

    return Arc(center, radius, start_angle, end_angle)


def round_corner(arc1: Arc, arc2: Arc, radius: float):

    # check if the transition from the end of arc1 is continuous
    if math.isclose(arc1.radius, get_distance(arc1.center, arc1.end, arc2.start)):
        # if so, we just add the original arc
        arcs = [arc1]
    else:
        # otherwise we add a smoothing corner
        corner = smooth_point_to_arc(arc2.start, arc1.reverse(), radius).reverse()
        arcs = [
            Arc(arc1.center, arc1.radius, arc1.start_angle, corner.start_angle),
            corner,
        ]
    # check if the transition to the start of arc2 is continuous
    if math.isclose(arc2.radius, get_distance(arc2.center, arc1.end, arc2.start)):
        # if so, we just add the original arc
        return arcs + [arc2]

    # otherwise we add a smoothing corner
    corner = smooth_point_to_arc(arc1.end, arc2, radius)

    arcs += [
        corner,
        Arc(arc2.center, arc2.radius, corner.end_angle, arc2.end_angle),
    ]
    return arcs


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


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
