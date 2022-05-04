import math
from planar_magnetics.geometry import Arc, Point, Polygon
from planar_magnetics.kicad import Via
from planar_magnetics.utils import dcr_of_annulus
from planar_magnetics.windings.windings import Winding


class TopTurn(Winding):
    """Defines a top layer turn of a CFFC inductor
    """

    def __init__(
        self,
        at,
        inner_radius: float,
        outer_radius: float,
        gap: float,
        termination_width: float,
        viastrip_angle: float,
        viastrip_width: float,
        layer: str,
    ):

        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.layer = layer

        # calculate the gap angles
        inner_gap_angle = math.asin(gap / inner_radius)
        outer_gap_angle = math.asin(gap / outer_radius)

        # angle from "at" to the corner of the termination
        term_angle = math.asin(termination_width / outer_radius / 2)

        termination_arc = Arc(at, inner_radius, -term_angle, term_angle)

        # create the inner arc
        inner_arc = Arc(
            at,
            inner_radius + viastrip_width,
            term_angle,
            2 * math.pi - term_angle - inner_gap_angle - viastrip_angle,
        )

        via_arc = Arc(
            at,
            inner_radius,
            2 * math.pi - term_angle - inner_gap_angle - viastrip_angle,
            2 * math.pi - term_angle - inner_gap_angle,
        )

        # create outer arc
        outer_arc = Arc(
            at, outer_radius, 2 * math.pi - term_angle - outer_gap_angle, term_angle,
        )

        # create termination
        termination = [
            at + Point(outer_radius + termination_width, termination_width / 2),
            at + Point(outer_radius + termination_width, -termination_width / 2),
            at + Point(outer_radius * math.cos(term_angle), -termination_width / 2),
        ]

        # create the polygon
        points = [termination_arc, inner_arc, via_arc, outer_arc] + termination
        self.polygon = Polygon(points, layer)

    def __str__(self):

        return self.polygon.__str__()


class BottomTurn:
    """Defines a bottom layer turn of a CFFC inductor
    """

    def __init__(
        self,
        at,
        inner_radius: float,
        outer_radius: float,
        gap: float,
        termination_width: float,
        viastrip_angle: float,
        viastrip_width: float,
        layer: str,
    ):

        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.layer = layer

        # calculate the gap angles
        inner_gap_angle = math.asin(gap / inner_radius)
        outer_gap_angle = math.asin(gap / outer_radius)

        # angle from "at" to the corner of the termination
        term_angle = math.asin(termination_width / outer_radius / 2)

        termination_arc = Arc(at, inner_radius, term_angle, -term_angle)

        # create the inner arc
        inner_arc = Arc(
            at,
            inner_radius + viastrip_width,
            2 * math.pi - term_angle,
            term_angle + inner_gap_angle + viastrip_angle,
        )

        via_arc = Arc(
            at,
            inner_radius,
            term_angle + inner_gap_angle + viastrip_angle,
            term_angle + inner_gap_angle,
        )

        # create outer arc
        outer_arc = Arc(
            at, outer_radius, term_angle + outer_gap_angle, 2 * math.pi - term_angle,
        )

        # create termination
        termination = [
            at + Point(outer_radius + termination_width, -termination_width / 2),
            at + Point(outer_radius + termination_width, termination_width / 2),
            at + Point(outer_radius * math.cos(term_angle), termination_width / 2),
        ]

        # create the polygon
        points = [termination_arc, inner_arc, via_arc, outer_arc] + termination
        self.polygon = Polygon(points, layer)


class InnerTurn:
    """Defines a middle layer turn of a CFFC inductor
    """

    def __init__(
        self,
        at,
        inner_radius: float,
        outer_radius: float,
        gap: float,
        rotation: float,
        viastrip_angle: float,
        viastrip_width: float,
        layer: str,
    ):
        assert (
            outer_radius > inner_radius
        ), "outer radius must be greater than inner radius"

        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.layer = layer

        # calculate the gap angles
        inner_gap_angle = math.asin(gap / inner_radius)
        outer_gap_angle = math.asin(gap / outer_radius)

        # create the arcs
        start_via_arc = Arc(
            at,
            inner_radius,
            inner_gap_angle / 2 + rotation,
            inner_gap_angle / 2 + viastrip_angle + rotation,
        )
        inner_arc = Arc(
            at,
            inner_radius + viastrip_width,
            inner_gap_angle / 2 + viastrip_angle + rotation,
            2 * math.pi - inner_gap_angle / 2 - viastrip_angle + rotation,
        )
        end_via_arc = Arc(
            at,
            inner_radius,
            2 * math.pi - inner_gap_angle / 2 - viastrip_angle + rotation,
            2 * math.pi - inner_gap_angle / 2 + rotation,
        )
        outer_arc = Arc(
            at,
            outer_radius,
            2 * math.pi - outer_gap_angle / 2 + rotation,
            outer_gap_angle / 2 + rotation,
        )

        # create the polygon
        points = [start_via_arc, inner_arc, end_via_arc, outer_arc]
        self.polygon = Polygon(points, layer)


class ViaStrip:
    def __init__(
        self,
        at: Point,
        layers: (str),
        inner_radius: float,
        start_angle: float,
        end_angle: float,
        size: float = 0.8,
        drill: float = 0.4,
    ):

        min_spacing = 0.5

        # calculate how may vias we can fit in the strip
        angle = end_angle - start_angle
        width = inner_radius * abs(angle)
        number_vias = int(width / (drill + min_spacing))

        # calculate via locations
        via_radius = inner_radius + size / 2
        delta_angle = angle / number_vias
        initial_angle = start_angle + delta_angle / 2
        angles = [initial_angle + n * delta_angle for n in range(number_vias)]
        locations = [
            Point(via_radius * math.cos(angle), via_radius * math.sin(angle))
            for angle in angles
        ]

        # create via strip
        self.vias = [Via(location + at, size, drill, layers) for location in locations]

    def __str__(self):
        expression = "\n".join([via.__str__() for via in self.vias])
        return expression


if __name__ == "__main__":
    turn = InnerTurn(Point(0, 0), 6, 12, 0.5, 0, math.pi / 8, 0, "F.Cu")
    print(turn)
