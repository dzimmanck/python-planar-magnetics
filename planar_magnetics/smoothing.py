from __future__ import annotations
import math

from planar_magnetics.geometry import (
    Point,
    Arc,
    Polygon,
    get_distance,
    TWO_PI,
    PI_OVER_TWO,
    THREE_PI_OVER_TWO,
)


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

    # calculate the angle of the vector p1 to p2
    segment_angle = math.atan2(p2.y - p1.y, p2.x - p1.x)

    # calculate the initial angle that the arc is pointing
    if arc.rotates_clockwise():
        arc_angle = arc.start_angle - PI_OVER_TWO
    else:
        arc_angle = arc.start_angle + PI_OVER_TWO

    # calculate the orientation of the corner relative to the line segment
    # and use to determine how to calculate the delta for the distance arithmetic bellow
    if get_quadrant(arc_angle - segment_angle + PI_OVER_TWO) > 2:
        delta = p2 - p1  # positive orientation
        positive_orientation = True
    else:
        delta = p1 - p2  # negative orientation
        positive_orientation = False

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

    if arc.rotates_clockwise():
        angle = (
            math.pi
            - math.asin(
                (radius * R - delta.x * p1.y + delta.y * p1.x) / center_to_center / R
            )
            - alpha
        )
    else:
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
    start_angle = PI_OVER_TWO + math.atan2(delta.y, delta.x)

    if corner_inside_arc:
        end_angle = angle
    else:
        end_angle = angle + math.pi

    # make sure arc rotates in correct direction
    # positive orientations need to rotate clockwise
    if positive_orientation:
        while start_angle < end_angle:
            start_angle += TWO_PI
    else:
        while start_angle > end_angle:
            start_angle -= TWO_PI

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

    if abs(corner.center - arc2.center) < arc2.radius:
        start_angle = corner.end_angle
    else:
        start_angle = corner.end_angle - math.pi

    arcs += [
        corner,
        Arc(arc2.center, arc2.radius, start_angle, arc2.end_angle),
    ]
    return arcs


def smooth_polygon(polygon: Polygon, radius: float) -> Polygon:
    """Smooth the corners of a polygon

    Adds smooth transitions with tangential arcs in between the points of a polygon

    Args:
        polygon (Polygon): The original polygon to smooth
        radius (float): The radius of the smoothing arcs

    Returns:
        Polygon: A new polygon with smoothed corners
    """

    assert radius > 0, "The radius must be a positive number"

    # smooth the corners
    arcs = [polygon.points[0]]
    for arc in polygon.points[1:]:
        arcs.extend(round_corner(arcs.pop(), arc, radius))

    # don't forget to smooth the start-to-finish transition
    arcs.extend(round_corner(arcs.pop(), arcs.pop(0), radius))

    return Polygon(arcs, polygon.layer, polygon.width, polygon.fill)
