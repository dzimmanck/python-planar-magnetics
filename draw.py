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


@dataclass
class Via:
    at: float = 0.0
    size: float = 0.8
    drill: float = 0.4
    layers: (str) = ("F.Cu")
    tsamp: uuid.UUID = uuid.uuid4()

    def __str__(self):
        tsamp = uuid.uuid4()
        layers = " ".join(self.layers)
        return f"(via (at {self.at}) (size {self.size} (drill {self.drill}) (layer {layers} (free) (net 0) (tsamp {self.tsamp})"


@dataclass
class Arc:
    start: Point
    mid: Point
    end: Point

    def __str__(self):
        return f"(arc (start {self.start}) (mid {self.mid}) (end {self.end}))"


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

    def __str__(self):
        points = "".join([f"{point}" for point in self.points])
        width = 0
        layer = "F.Cu"
        expression = f"(gr_poly(pts{points})(layer {layer}) (width {width}) (fill solid) (tstamp 5c1d6842-15a5-4f73-b198-8836681840a1))"
        return expression


# (gr_poly
#     (pts
#       (arc (start 138.99987499921875 129.05) (mid 119 129) (end 138.99987499921875 128.95))
#       (arc (start 143.99991666643518 128.95) (mid 114 129) (end 143.99991666643518 129.05))
#     ) (layer "F.Cu") (width 0) (fill solid) (tstamp 5c1d6842-15a5-4f73-b198-8836681840a1))

# (via (at 133.043447 111.6019) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (free) (net 0) (tstamp 4f9fdeff-02
class Turn:
    """Defines a middle layer turn of a CFFC inductor
    """

    def __init__(self, inner_radius, outer_radius, gap):
        assert (
            outer_radius > inner_radius
        ), "outer radius must be greater than inner radius"

        center = 129

        x = center + inner_radius * math.sqrt(1 - (gap / 2 / inner_radius) ** 2)
        start = Point(x, center + gap / 2)
        mid = Point(center - inner_radius, center)
        end = Point(x, center - gap / 2)
        inner_arc = Arc(start, mid, end)

        x = center + outer_radius * math.sqrt(1 - (gap / 2 / outer_radius) ** 2)
        end = Point(x, center + gap / 2)
        mid = Point(center - outer_radius, center)
        start = Point(x, center - gap / 2)
        outer_arc = Arc(start, mid, end)

        # create the polygon
        points = [inner_arc, outer_arc]
        self.polygon = Polygon(points)

    def __str__(self):
        return self.polygon.__str__()


if __name__ == "__main__":

    turn = Turn(10, 15, 0.5)
    print(turn)
