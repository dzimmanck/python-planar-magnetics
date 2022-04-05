from __future__ import annotations
from dataclasses import dataclass, field
import math
import uuid
import ezdxf
from planar_magnetics.kicad import Pad, PadType

# useful geometric constants
TWO_PI = 2 * math.pi
PI_OVER_TWO = math.pi / 2
THREE_PI_OVER_TWO = 3 * math.pi / 2


@dataclass
class Point:
    x: float
    y: float

    def __str__(self):
        return f"{self.x*1e3} {self.y*1e3}"

    def __add__(self, other: Point):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point):
        return Point(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)


@dataclass
class Via:
    at: float = 0.0
    size: float = 0.8
    drill: float = 0.4
    layers: (str) = ("F.Cu",)
    remove_unused_layers = True
    tstamp: uuid.UUID = uuid.uuid4()

    def to_pad(self, number: int = 1):
        """Convert to an equivalent through-hole pad"""

        return Pad(PadType.TH, number, self.at, self.size, ("*.Cu",), self.drill)

    def __str__(self):
        layers = " ".join(self.layers)
        annular_option = "(remove_unused_layers)" if self.remove_unused_layers else ""
        return f"(via (at {self.at}) (size {self.size*1e3}) (drill {self.drill*1e3}) (layers {layers}) {annular_option} (free) (net 0) (tstamp {self.tstamp}))"


def point_from_polar(radius, angle):
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return Point(x, y)


@dataclass
class Arc:
    center: Point
    radius: float
    start_angle: float
    end_angle: float
    start: Point = field(init=False)
    mid: Point = field(init=False)
    end: Point = field(init=False)

    def __post_init__(self):
        """Derivce the three point representation of the Arc"""
        mid_angle = (self.start_angle + self.end_angle) / 2
        self.start = self.center + point_from_polar(self.radius, self.start_angle)
        self.mid = self.center + point_from_polar(self.radius, mid_angle)
        self.end = self.center + point_from_polar(self.radius, self.end_angle)

    def __str__(self):
        return f"(arc (start {self.start}) (mid {self.mid}) (end {self.end}))"

    def __add__(self, other: Point):
        return Arc(selt.at + other, self.radius, self.start_angle, self.end_angle)

    def rotates_clockwise(self):
        return self.end_angle < self.start_angle

    def rotates_counterclockwise(self):
        return self.end_angle > self.start_angle

    def reverse(self):
        return Arc(self.center, self.radius, self.end_angle, self.start_angle)

    def add_to_dxf_model(self, modelspace):
        """Add Arc to DXF model"""

        modelspace.add_arc(
            center=(self.center.x, self.center.y),
            radius=self.radius,
            start_angle=self.start_angle,
            end_angle=self.end_angle,
        )


@dataclass
class Polygon:
    points: [Point]
    layer: str = "F.Cu"
    width: float = 0
    fill: str = "solid"
    tstamp: uuid.UUID = uuid.uuid4()

    def __add__(self, other: Point):
        return Polygon(
            [point + other for point in self.points], self.layer, self.width, self.fill
        )

    def __str__(self):
        points = "".join(
            [
                f"{point}" if isinstance(point, Arc) else f"(xy {point})"
                for point in self.points
            ]
        )
        expression = f"(fp_poly(pts{points})(layer {self.layer}) (width {self.width}) (fill {self.fill}) (tstamp {self.tstamp}))"
        return expression


if __name__ == "__main__":

    arc = Arc(Point(0, 0), 10, 0, math.pi / 2)
