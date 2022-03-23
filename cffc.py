import math
import uuid
from primitives import Point, Polygon, Via, arc_from_polar


class TopTurn:
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

        self.layer = layer

        # calculate the gap angles
        inner_gap_angle = math.asin(gap / inner_radius)
        outer_gap_angle = math.asin(gap / outer_radius)

        # angle from "at" to the corner of the termination
        term_angle = math.asin(termination_width / outer_radius)

        termination_arc = arc_from_polar(inner_radius, -term_angle / 2, term_angle / 2)

        # create the inner arc
        inner_arc = arc_from_polar(
            inner_radius + viastrip_width,
            term_angle / 2,
            2 * math.pi - term_angle / 2 - inner_gap_angle - viastrip_angle,
        )

        via_arc = arc_from_polar(
            inner_radius,
            2 * math.pi - term_angle / 2 - inner_gap_angle - viastrip_angle,
            2 * math.pi - term_angle / 2 - inner_gap_angle,
        )

        # create outer arc
        outer_arc = arc_from_polar(
            outer_radius,
            2 * math.pi - term_angle / 2 - outer_gap_angle,
            term_angle / 2,
        )

        # create termination
        termination = [
            Point(outer_radius + 5, termination_width / 2),
            Point(outer_radius + 5, -termination_width / 2),
            Point(outer_radius * math.cos(term_angle / 2), -termination_width / 2),
        ]

        # create the polygon
        points = [termination_arc, inner_arc, via_arc, outer_arc] + termination
        self.polygon = Polygon(points, layer) + at

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

        self.layer = layer

        # calculate the gap angles
        inner_gap_angle = math.asin(gap / inner_radius)
        outer_gap_angle = math.asin(gap / outer_radius)

        # angle from "at" to the corner of the termination
        term_angle = math.asin(termination_width / outer_radius)

        termination_arc = arc_from_polar(inner_radius, term_angle / 2, -term_angle / 2)

        # create the inner arc
        inner_arc = arc_from_polar(
            inner_radius + viastrip_width,
            2 * math.pi - term_angle / 2,
            term_angle / 2 + inner_gap_angle + viastrip_angle,
        )

        via_arc = arc_from_polar(
            inner_radius,
            term_angle / 2 + inner_gap_angle + viastrip_angle,
            term_angle / 2 + inner_gap_angle,
        )

        # create outer arc
        outer_arc = arc_from_polar(
            outer_radius,
            term_angle / 2 + outer_gap_angle,
            2 * math.pi - term_angle / 2,
        )

        # create termination
        termination = [
            Point(outer_radius + 5, -termination_width / 2),
            Point(outer_radius + 5, termination_width / 2),
            Point(outer_radius * math.cos(term_angle / 2), termination_width / 2),
        ]

        # create the polygon
        points = [termination_arc, inner_arc, via_arc, outer_arc] + termination
        self.polygon = Polygon(points, layer) + at

    def __str__(self):

        return self.polygon.__str__()


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

        self.layer = layer

        # calculate the gap angles
        inner_gap_angle = math.asin(gap / inner_radius)
        outer_gap_angle = math.asin(gap / outer_radius)

        # create the arcs
        start_via_arc = arc_from_polar(
            inner_radius,
            inner_gap_angle / 2 + rotation,
            inner_gap_angle / 2 + viastrip_angle + rotation,
        )
        inner_arc = arc_from_polar(
            inner_radius + viastrip_width,
            inner_gap_angle / 2 + viastrip_angle + rotation,
            2 * math.pi - inner_gap_angle / 2 - viastrip_angle + rotation,
        )
        end_via_arc = arc_from_polar(
            inner_radius,
            2 * math.pi - inner_gap_angle / 2 - viastrip_angle + rotation,
            2 * math.pi - inner_gap_angle / 2 + rotation,
        )
        outer_arc = arc_from_polar(
            outer_radius,
            2 * math.pi - outer_gap_angle / 2 + rotation,
            outer_gap_angle / 2 + rotation,
        )

        # create the polygon
        points = [start_via_arc, inner_arc, end_via_arc, outer_arc]
        self.polygon = Polygon(points, layer) + at

    def __str__(self):
        return self.polygon.__str__()


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


class Winding:
    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        number_turns: int,
        gap: float = 0.5,
        termination_width: float = None,
    ):

        if termination_width is None:
            termination_width = outer_radius - inner_radius

        # calculate other useful angles
        inner_gap_angle = math.asin(gap / inner_radius)
        term_angle = math.asin(termination_width / outer_radius)

        # calculate the angle we can allocate to the via transitions
        circumfrance_for_transitions = (
            2 * math.pi - term_angle
        ) * inner_radius - number_turns * gap
        angle_for_transitions = circumfrance_for_transitions / inner_radius
        viastrip_angle = angle_for_transitions / (number_turns - 1)

        # calculate other useful angles
        inner_gap_angle = math.asin(gap / inner_radius)
        term_angle = math.asin(termination_width / outer_radius)

        # calculate the required rotation per turn
        initial_rotation = (term_angle + inner_gap_angle) / 2
        rotation_per_turn = viastrip_angle + inner_gap_angle

        # create the top and bottom turns
        top = TopTurn(
            at,
            inner_radius,
            outer_radius,
            gap,
            termination_width,
            viastrip_angle,
            1,
            "F.Cu",
        )
        inners = [
            InnerTurn(
                at,
                inner_radius,
                outer_radius,
                gap,
                -n * rotation_per_turn - initial_rotation,
                viastrip_angle,
                1,
                f"In{n}.Cu",
            )
            for n in range(1, number_turns - 1)
        ]
        bottom = BottomTurn(
            at,
            inner_radius,
            outer_radius,
            gap,
            termination_width,
            viastrip_angle,
            1,
            "B.Cu",
        )
        self.turns = [top] + inners + [bottom]

        # create the via strips
        initial_angle = initial_rotation + inner_gap_angle / 2

        layers = [(t.layer, b.layer) for t, b in zip(self.turns[0:-1], self.turns[1:])]

        self.viastrips = [
            ViaStrip(
                at,
                layers[n],
                inner_radius,
                -initial_angle - n * rotation_per_turn,
                -initial_angle - n * rotation_per_turn - viastrip_angle,
                0.8,
                0.4,
            )
            for n in range(number_turns - 1)
        ]

    def estimate_dcr(self, stackup: [float], temperature: float = 25):
        """Estimate the DC resistance of the winding

        This function will estimate the DC resistance of the winding by calculating the estimated
        dc resistance of each turn and adding the estimated inter-turn via resistance 
        
        Args:
            stackup: list of copper weights for each layer in ounces
            temperature: winding temperature in decrees C

        Returns:
            float: An estimation of the DC resistance in ohms
        """

        # TODO
        raise NotImplementedError

    def __str__(self):
        turns = "\n".join(turn.__str__() for turn in self.turns)
        vias = "\n".join(viastrip.__str__() for viastrip in self.viastrips)
        expression = turns + vias
        return expression


class Core:
    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        termination_width: float = None,
        edge_to_trace: float = 0.635,
        edge_to_core: float = 0.5,
    ):

        if termination_width is None:
            termination_width = outer_radius - inner_radius

        self.at = at
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.edge_to_trace = edge_to_trace
        self.edge_to_core = edge_to_core
        self.tstamp = uuid.uuid4()

        # calculate core dimensions
        self.centerpost_radius = inner_radius - edge_to_trace - edge_to_core
        self.outerpost_radius = outer_radius + edge_to_trace + edge_to_core

        # calculate the centerpost area
        self.centerpost_area = math.pi * self.centerpost_radius ** 2

        # create polygons for the outer post cutouts
        extension = 3
        outer_cutout_radius = self.outerpost_radius - edge_to_core
        start_angle = math.asin(
            (termination_width / 2 + edge_to_trace) / outer_cutout_radius
        )
        end_angle = math.pi / 2 - start_angle
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, extension)
        corner3 = arc.start + Point(extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg1 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(-extension, 0)
        corner3 = arc.start + Point(0, extension)
        corner2 = Point(corner1.x, corner3.y)
        leg2 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, -extension)
        corner3 = arc.start + Point(-extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg3 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(extension, 0)
        corner3 = arc.start + Point(0, -extension)
        corner2 = Point(corner1.x, corner2.y)
        leg4 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        self.outerposts = [leg1, leg2, leg3, leg4]

    def __str__(self):

        # create the centerpost milling
        end = self.at + Point(self.centerpost_radius + self.edge_to_core, 0)
        layer = "Edge.Cuts"
        centerpost = f"(gr_circle (center {self.at}) (end {end}) (layer {layer}) (width 0.1) (fill none) (tstamp {self.tstamp}))"

        # create the milling for each corner
        outerposts = "\n".join(outerpost.__str__() for outerpost in self.outerposts)

        expression = "\n".join([centerpost, outerposts])

        return expression


if __name__ == "__main__":
    at = Point(110, 110)

    winding = Winding(at, 10, 15, 6, 0.5)
    core = Core(at, 10, 15)
    print(winding)
    print(core)

    # turn = TopTurn(at, 10, 15, 0.5, 5, math.pi / 8, 1, "F.Cu")
    # turn = InnerTurn(at, 10, 15, 0.5, 0, math.pi / 8, 1, "F.Cu")
    # print(turn)
