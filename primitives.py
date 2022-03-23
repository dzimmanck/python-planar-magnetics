from __future__ import annotations
from dataclasses import dataclass
import math
import uuid


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
        return f"(via (at {self.at}) (size {self.size}) (drill {self.drill}) (layers {layers}) (free) (net 0) (tstamp {self.tstamp}))"


@dataclass
class Arc:
    start: Point
    mid: Point
    end: Point

    def __str__(self):
        return f"(arc (start {self.start}) (mid {self.mid}) (end {self.end}))"

    def __add__(self, other: Point):
        return Arc(self.start + other, self.mid + other, self.end + other)


def arc_from_polar(radius, start_angle, end_angle):
    mid_angle = 0.5 * (start_angle + end_angle)
    start = Point(radius * math.cos(start_angle), radius * math.sin(start_angle))
    mid = Point(radius * math.cos(mid_angle), radius * math.sin(mid_angle))
    end = Point(radius * math.cos(end_angle), radius * math.sin(end_angle))
    return Arc(start, mid, end)


@dataclass
class Polygon:
    points: [Point]
    layer: str = "F.Cu"
    tstamp: uuid.UUID = uuid.uuid4()

    def __add__(self, other: Point):
        return Polygon([point + other for point in self.points], self.layer)

    def __str__(self):
        points = "".join(
            [
                f"{point}" if isinstance(point, Arc) else f"(xy {point})"
                for point in self.points
            ]
        )
        width = 0
        expression = f"(gr_poly(pts{points})(layer {self.layer}) (width {width}) (fill solid) (tstamp {self.tstamp}))"
        return expression
