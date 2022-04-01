from __future__ import annotations
from dataclasses import dataclass
import math
import uuid

from planar_magnetics.geometry import Point, Arc

# useful geometric constants
TWO_PI = 2 * math.pi
PI_OVER_TWO = math.pi / 2
THREE_PI_OVER_TWO = 3 * math.pi / 2


def get_distance(p0: Point, p1: Point, p2: Point):
    """Calculate the distance between a point and a line

    Calculate the distance between a point p0 and a line formed between p1 and p2
    """

    p21 = p2 - p1
    p10 = p1 - p0

    return abs(p21.x * p10.y - p21.y * p10.x) / abs(p21)


def get_quadrant(angle: float):
    """Calculate the quadrant of an angle"""

    angle %= TWO_PI

    if angle < 0:
        angle += TWO_PI

    if angle < PI_OVER_TWO:
        return 1
    if angle < math.pi:
        return 2
    if angle < THREE_PI_OVER_TWO:
        return 3
    return 4

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

    # normalized to the arc center, which simplifies the math.  We will add the arc center back to
    # the result at the end
    p1 = point - arc.center
    p2 = arc.start - arc.center

    # find the starting quadrant of the start of the arc
    starting_quadrant = get_quadrant(arc.start_angle)
    delta = p1 - p2

    # calculate the amplitude of the line segment
    R = abs(delta)

    # calculate the distance from the center of the arc to the center of the corner
    # if the segment intersects from the inside of the circle, it will be arc.radius - radius
    # if the segment intersects from the outside of the circle, it will be arc.radius + radius
    if abs(point - arc.center) < arc.radius:
        center_to_center = arc.radius - radius
        corner_inside_arc = True
    else:
        center_to_center = arc.radius + radius
        corner_inside_arc = False

    # calculate the angle of the vector from center to center
    alpha = math.atan2(delta.y, -delta.x)

    # angle = (
    #     math.asin((radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R)
    #     - alpha
    # )

    angle = (
        math.pi
        - math.asin(
            (radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R
        )
        - alpha
    )

    # if starting_quadrant > 2:
    #     angle = (
    #         math.asin(
    #             (radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R
    #         )
    #         - alpha
    #     )
    # else:
    #     angle = (
    #         math.pi
    #         - math.asin(
    #             (radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R
    #         )
    #         - alpha
    #     )

    # derive center of the corner
    x = center_to_center * math.cos(angle)
    y = center_to_center * math.sin(angle)
    center = Point(x, y) + arc.center

    # derive the start and end angles
    start_angle = PI_OVER_TWO + math.atan2(delta.y, delta.x)

    if corner_inside_arc:
        end_angle = angle
        print("inside")
    else:
        print("outside")
        end_angle = angle + math.pi

    # # make sure the corner arc rotates in the same direction as the main arc
    # if arc.rotates_clockwise():
    #     while start_angle < end_angle:
    #         start_angle += TWO_PI
    # else:
    #     while start_angle > end_angle:
    #         start_angle -= TWO_PI

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
    arc0 = Arc(
        Point(110.0e-3, 110.0e-3),
        0.011997448713915889,
        3.141592653589793,
        -2.519520609753873,
    )
    arc1 = Arc(Point(110.0e-3, 110.0e-3), 0.01, -2.9175173682879736, 3.141592653589793)

    corner = smooth_point_to_arc(arc0.end, arc1, radius=0.5e-3)
    print(corner)
