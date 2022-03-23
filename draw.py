from __future__ import annotations
from dataclasses import dataclass
import math
import uuid

# (gr_poly (pts
#  (xy 181.8 127.499999)
#   (arc (start 112.800001 127.499999) (mid 110.678681 126.621319) (end 109.800001 124.499999))
#   (arc (start 109.800001 80.5) (mid 110.678681 78.37868) (end 112.800001 77.5))
#   (arc (start 181.8 77.5) (mid 183.92132 78.37868) (end 184.8 80.5))
#   (arc (start 184.8 124.499999) (mid 183.92132 126.621319) (end 181.8 127.499999))) (layer "F.SilkS") (width 0.2) (fill none) (tstamp 88377deb-24e1-427b-8fd0-88456d2f78dd))


@dataclass
class Point:
    x: float
    y: float

    def __str__(self):
        return f"{self.x} {self.y}"

    def __add__(self, other: Point):
        return Point(self.x + other.x, self.y + other.y)

    def __radd__(self, other: Point):
        return self.__add__(other)


@dataclass
class Via:
    at: float = 0.0
    size: float = 0.8
    drill: float = 0.4
    layers: (str) = ("F.Cu")
    tstamp: uuid.UUID = uuid.uuid4()

    def __str__(self):
        layers = " ".join(self.layers)
        return f"(via (at {self.at}) (size {self.size} (drill {self.drill}) (layer {layers} (free) (net 0) (tstamp {self.tstamp})"


@dataclass
class Arc:
    start: Point
    mid: Point
    end: Point

    def __str__(self):
        return f"(arc (start {self.start}) (mid {self.mid}) (end {self.end}))"

    def __add__(self, other: Point):
        return Arc(self.start + other, self.mid + other, self.end + other)


def create_arc_from_polar(radius, start_angle, end_angle):
    mid_angle = 0.5 * (start_angle + end_angle)
    start = Point(radius * math.cos(start_angle), radius * math.sin(start_angle))
    mid = Point(radius * math.cos(mid_angle), radius * math.sin(mid_angle))
    end = Point(radius * math.cos(end_angle), radius * math.sin(end_angle))
    return Arc(start, mid, end)


# (gr_poly
#     (pts
#       (xy 131.4 105.6)
#       (xy 134.3 109.1)
#       (xy 134.3 119)
#       (xy 129.15 126.65)
#       (xy 124 128.7)
#       (xy 123.55 118.6)
#       (xy 125.2 117.75)
#       (xy 126.45 115.5)
#       (xy 126.45 113.25)
#       (xy 125.85 108.9)
#       (xy 123.15 107.05)
#       (xy 121.1 106.25)
#       (xy 114.9 107.7)
#       (xy 113.5 110.15)
#       (xy 113.5 113.05)
#       (xy 114.9 116.75)
#       (xy 117.8 118.8)
#       (xy 120.9 118.6)
#       (xy 121.1 129.3)
#       (xy 116.35 129.3)
#       (xy 114.5 128.9)
#       (xy 111.85 128.25)
#       (xy 107.9 125.8)
#       (xy 104.4 116.95)
#       (xy 105.25 108.1)
#       (xy 108.1 103.75)
#       (xy 111.85 100.45)
#     ) (layer "F.Cu") (width 0.2) (fill solid) (tstamp f284b1e2-75a4-4a3f-a5f4-6f05f15fb4f5))
#   (gr_rect (start 43.225 31.2) (end 240.975 141.55) (layer "Edge.Cuts") (width 2) (fill none) (tstamp 054bbc1a-25db-482a-a3ba-a4a8c3d812e5))


@dataclass
class Polygon:
    points: [Point]
    layer: str = "F.Cu"
    tstamp: uuid.UUID = uuid.uuid4()

    def __add__(self, other: Point):
        return Polygon([point + other for point in self.points], self.layer)

    def __str__(self):
        points = "".join([f"{point}" for point in self.points])
        width = 0
        expression = f"(gr_poly(pts{points})(layer {self.layer}) (width {width}) (fill solid) (tstamp {self.tstamp}))"
        return expression


class Turn:
    """Defines a middle layer turn of a CFFC inductor
    """

    def __init__(
        self,
        at,
        inner_radius: float,
        outer_radius: float,
        gap: float,
        angle: float,
        viastrip_angle: float,
        viastrip_width: float,
        layer: str,
    ):
        assert (
            outer_radius > inner_radius
        ), "outer radius must be greater than inner radius"

        # create the vias arcs
        a = math.asin(gap / 2 / inner_radius)
        b = viastrip_angle / 2
        c = math.asin(gap / 2 / outer_radius)
        start_via_arc = create_arc_from_polar(inner_radius, a + angle, b + angle)
        inner_arc = create_arc_from_polar(
            inner_radius + viastrip_width, b + angle, 2 * math.pi - b + angle
        )
        end_via_arc = create_arc_from_polar(
            inner_radius, 2 * math.pi - b + angle, 2 * math.pi - a + angle
        )
        outer_arc = create_arc_from_polar(
            outer_radius, 2 * math.pi - c + angle, c + angle
        )

        # create the polygon
        points = [start_via_arc, inner_arc, end_via_arc, outer_arc]
        self.polygon = Polygon(points, layer) + at

    def __str__(self):
        return self.polygon.__str__()


class Cffc:
    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        number_turns: int,
        gap: float = 0.5,
    ):

        # calculate the angle we can allocate to the via transitions
        inner_circumfrance = 2 * math.pi * inner_radius

        viastrip_angle = (
            2 * math.pi * (inner_circumfrance - number_turns * gap) / inner_circumfrance
        ) / number_turns

        # create the top and bottom turns
        top = Turn(at, inner_radius, outer_radius, gap, 0, viastrip_angle, 1, "F.Cu")
        inners = [
            Turn(
                at,
                inner_radius,
                outer_radius,
                gap,
                n * 2 * math.pi / number_turns,
                viastrip_angle,
                1,
                f"In{n}.Cu",
            )
            for n in range(1, number_turns - 1)
        ]
        bottom = Turn(
            at,
            inner_radius,
            outer_radius,
            gap,
            (number_turns - 1) * 2 * math.pi / number_turns,
            viastrip_angle,
            1,
            "B.Cu",
        )
        self.turns = [top] + inners + [bottom]

    def __str__(self):
        return "\n".join(turn.__str__() for turn in self.turns)


if __name__ == "__main__":
    at = Point(110, 110)

    # # create 4 turns
    # turn1 = Turn(at, 10, 15, 0.5, 0 * math.pi / 3, math.pi / 4, 1, "F.Cu")
    # turn2 = Turn(at, 10, 15, 0.5, 1 * math.pi / 3, math.pi / 4, 1, "In1.Cu")
    # turn3 = Turn(at, 10, 15, 0.5, 2 * math.pi / 3, math.pi / 4, 1, "In2.Cu")
    # turn4 = Turn(at, 10, 15, 0.5, 3 * math.pi / 3, math.pi / 4, 1, "In3.Cu")
    # turn5 = Turn(at, 10, 15, 0.5, 4 * math.pi / 3, math.pi / 4, 1, "In4.Cu")
    # turn6 = Turn(at, 10, 15, 0.5, 5 * math.pi / 3, math.pi / 4, 1, "B.Cu")
    # print(turn1)
    # print(turn2)
    # print(turn3)
    # print(turn4)
    # print(turn5)
    # print(turn6)

    inductor = Cffc(at, 10, 15, 6, 0.5)
    print(inductor)
