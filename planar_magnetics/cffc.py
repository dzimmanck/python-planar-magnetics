import math
import uuid
from planar_magnetics.geometry import Arc, Point, Polygon, Via
from planar_magnetics.cores import Core
from planar_magnetics.creepage import Classification, calculate_creepage
from planar_magnetics.kicad import Footprint, ThroughHolePad


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
        size: float = 0.8e-3,
        drill: float = 0.4e-3,
    ):

        min_spacing = 0.5e-3

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
        gap: float = 0.5e-3,
        termination_width: float = None,
        viastrip_width: float = 1e-3,
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
            viastrip_width,
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
                viastrip_width,
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
            viastrip_width,
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
                0.8e-3,
                0.4e-3,
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


class Cffc:
    def __init__(
        self,
        inner_radius: float,
        outer_radius: float,
        number_turns: int,
        voltage: float,
        classification: Classification = Classification.B4,
    ):
        origin = Point(0, 0)

        # calculate the required creepage distance
        creapage = calculate_creepage(voltage, classification)

        termination_width = outer_radius - inner_radius

        # create the windings
        self.winding = Winding(
            at=origin,
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            number_turns=number_turns,
            gap=creapage,
            termination_width=termination_width,
        )

        # create the core
        self.core = Core(
            at=origin,
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            termination_width=termination_width,
            edge_to_trace=0.635e-3,
            edge_to_core=0.5e-3,
        )

    def __str__(self):
        expression = self.winding.__str__() + self.core.__str__()
        return expression

    def to_kicad_footprint(self, name: str):
        """Export the Cffc inductor design as a KiCAD footprint file (*.kicad_mods)
        """

        # vias are not allowed in KiCAD footprints, so convert the via strips to through-hole pads
        pads = [
            via.to_pad() for viastrip in self.winding.viastrips for via in viastrip.vias
        ]

        # create a footprint from the various elements
        contents = [self.core] + self.winding.turns + pads
        footprint = Footprint(name, contents=contents)

        # write the footprint to a file
        fh = open(f"{name}.kicad_mods", "w")
        fh.write(footprint.__str__())
        fh.close()


if __name__ == "__main__":

    inductor = Cffc(inner_radius=4.9e-3, outer_radius=9e-3, number_turns=6, voltage=500)

    inductor.to_kicad_footprint("Cffc_Inductor_01")
