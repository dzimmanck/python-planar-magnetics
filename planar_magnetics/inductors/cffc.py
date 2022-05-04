import math
from planar_magnetics.geometry import Point
from planar_magnetics.cores import Core
from planar_magnetics.creepage import Classification, calculate_creepage
from planar_magnetics.kicad import Footprint, Pad, PadType, Reference, Value
from planar_magnetics.windings.single import TopTurn, InnerTurn, BottomTurn, ViaStrip


class Winding:
    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        number_layers: int,
        gap: float = 0.5,
        termination_width: float = None,
        viastrip_width: float = 1,
    ):

        self.number_layers = number_layers

        if termination_width is None:
            termination_width = outer_radius - inner_radius

        # calculate other useful angles
        inner_gap_angle = math.asin(gap / inner_radius)
        term_angle = math.asin(termination_width / outer_radius)

        # calculate the angle we can allocate to the via transitions
        circumfrance_for_transitions = (
            2 * math.pi - term_angle
        ) * inner_radius - number_layers * gap
        angle_for_transitions = circumfrance_for_transitions / inner_radius
        viastrip_angle = angle_for_transitions / (number_layers - 1)

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
            for n in range(1, number_layers - 1)
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
                0.8,
                0.4,
            )
            for n in range(number_layers - 1)
        ]

    def estimate_dcr(self, thicknesses: [float], rho: float = 1.68e-8):
        """Estimate the DC resistance of the winding

        This function will estimate the DC resistance of the winding by calculating the estimated
        dc resistance of each turn and adding the estimated inter-turn via resistance 
        
        Args:
            thicknesses: The thickness of each layer in the winding
            rho (float): The conductivity of the material used in the layer

        Returns:
            float: An estimation of the DC resistance in ohms
        """

        assert (
            len(thicknesses) == self.number_layers
        ), f"You need to specify 1 thickness for each layer, so len(thicknesses) should be {self.number_layers}, not{len(thicknesses)}"

        resistance = 0
        for thickness, turn in zip(thicknesses, self.turns):
            resistance += turn.estimate_dcr(thickness, rho)

        return resistance

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
        termination_width: float = None,
    ):
        origin = Point(0, 0)

        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

        # calculate the required creepage distance
        creapage = calculate_creepage(voltage, classification)

        if termination_width is None:
            self.termination_width = outer_radius - inner_radius
        else:
            self.termination_width = termination_width

        self.number_turns = number_turns
        self.number_layers = number_turns + 1

        # create the windings
        self.winding = Winding(
            at=origin,
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            number_layers=self.number_layers,
            gap=creapage,
            termination_width=self.termination_width,
        )

        # create the core
        edge_to_trace = 0.635
        edge_to_core = 0.5
        self.core = Core(
            centerpost_radius=inner_radius - edge_to_trace - edge_to_core,
            window_width=(outer_radius - inner_radius)
            + 2 * (edge_to_core + edge_to_trace),
            window_height=6,
            opening_width=self.termination_width + 2 * (edge_to_core + edge_to_trace),
            gap=1,
        )

    def __str__(self):
        cutouts = self.core.create_pcb_cutouts(Point(0, 0), 0.5)
        windings_expr = self.winding.__str__()
        cutouts_expr = "\n".join([cutout.__str__() for cutout in cutouts])
        expression = self.winding.__str__() + self.core.__str__()
        return expression

    def estimate_dcr(self, thicknesses: [float], rho: float = 1.68e-8):
        """Estimate the DC resistance of the winding

        This function will estimate the DC resistance of the winding by calculating the estimated
        dc resistance of each turn and adding the estimated inter-turn via resistance 
        
        Args:
            thicknesses: The thickness of each layer in the winding
            rho (float): The conductivity of the material used in the layer

        Returns:
            float: An estimation of the DC resistance in ohms
        """

        return self.winding.estimate_dcr(thicknesses, rho)

    def to_kicad_footprint(self, name: str):
        """Export the Cffc inductor design as a KiCAD footprint file (*.kicad_mods)
        """

        # vias are not allowed in KiCAD footprints, so convert the via strips to through-hole pads
        pads = [
            via.to_pad() for viastrip in self.winding.viastrips for via in viastrip.vias
        ]

        # add the termination pads
        location = Point(self.outer_radius + self.termination_width / 2, 0)
        size = self.termination_width / 2
        pads.extend(
            [
                Pad(PadType.SMD, 1, location, size, ("F.Cu",)),
                Pad(PadType.SMD, 2, location, size, ("B.Cu",)),
            ]
        )

        # add the reference and value silkscreens
        x_loc = self.core.width / 2 + 1
        height_avail = (self.core.width - self.termination_width) / 2
        font_size = min(2, height_avail / 4)
        val_loc = Point(x_loc, self.termination_width / 2 + height_avail / 3)
        ref_loc = Point(x_loc, self.termination_width / 2 + 2 * height_avail / 3)
        reference = Reference(ref_loc, font_size)
        value = Value(val_loc, font_size)

        # create a footprint from the various elements
        contents = (
            self.core.create_pcb_cutouts()
            + self.winding.turns
            + pads
            + [reference, value]
        )

        footprint = Footprint(name, contents=contents)

        # write the footprint to a file
        fh = open(f"{name}.kicad_mod", "w")
        fh.write(footprint.__str__())
        fh.close()


if __name__ == "__main__":

    from planar_magnetics.utils import weight_to_thickness

    inductor = Cffc(inner_radius=4.9, outer_radius=9, number_turns=3, voltage=500)

    # estimate the dc resistance of this inductor
    # using the CFFC structure, a 5 turn inductor requires 6 layers
    # assume we are using 1.5 oz on top/botton and 2oz on interior layers
    thicknesses = [
        weight_to_thickness(1.5),
        weight_to_thickness(2),
        weight_to_thickness(2),
        weight_to_thickness(1.5),
    ]
    dcr = inductor.estimate_dcr(thicknesses)
    print(f"Estimated DCR of this inductor is {dcr*1e3} mOhms")

    # create a complete KiCAD footprint
    inductor.to_kicad_footprint("cffc_inductor")

    inductor.core.to_step("core.step")
