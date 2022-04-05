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

    def rotate(self, angle: float):
        """Rotate an arc about its center"""
        return Arc(
            self.center, self.radius, self.start_angle + angle, self.end_angle + angle
        )

    def rotate_about(self, about: Point, angle: float):
        """ Rotate an arc around a reference point"""

        # calculate the new center for the arc
        offset = self.center - about
        sin_angle = math.sin(angle)
        cos_angle = math.cos(angle)
        x = offset.x * cos_angle - offset.y * sin_angle
        y = offset.y * cos_angle + offset.x * sin_angle
        center = about + Point(x, y)

        return Arc(
            center, self.radius, self.start_angle + angle, self.end_angle + angle
        )

    def interpolate(self, max_angle: float = math.pi / 36):
        """Create a PWL approximation of the arc with a list of points
        """
        points = []
        angle = self.start_angle
        if self.rotates_counterclockwise():
            while angle < self.end_angle:
                point = Point(
                    self.radius * math.cos(angle), self.radius * math.sin(angle)
                )
                points.append(self.center + point)
                angle += max_angle
        else:
            while angle > self.end_angle:
                point = Point(
                    self.radius * math.cos(angle), self.radius * math.sin(angle)
                )
                points.append(self.center + point)
                angle -= max_angle

        point = Point(
            self.radius * math.cos(self.end_angle),
            self.radius * math.sin(self.end_angle),
        )
        points.append(self.center + point)
        return points

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

    def to_poly_path(self, max_angle: float = math.pi / 36):
        """Create a list of tuples representing the polypath
        """
        points = []
        for point in self.points:

            if isinstance(point, Arc):
                points.extend([(p.x, p.y) for p in point.interpolate(max_angle)])
                continue
            points.append((point.x, point.y))
        return points

    def add_to_dxf_model(self, modelspace):

        for point in self.points:
            point.add_to_dxf_model(modelspace)

    def plot(self, max_angle: float = math.pi / 36):
        """Create a plot preview of the polygon
        """
        import matplotlib.pyplot as mp

        path = self.to_poly_path(max_angle)
        mp.figure(figsize=(8, 8))
        mp.axis("equal")
        x, y = zip(*path)
        mp.fill(x, y)
        mp.show()


if __name__ == "__main__":

    arc = Arc(Point(0, 0), 10, 0, math.pi / 2)
