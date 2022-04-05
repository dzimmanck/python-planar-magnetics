import math
import uuid
from planar_magnetics.geometry import Arc, Point, Polygon, Via
from planar_magnetics.cores import Core
from planar_magnetics.creepage import Classification, calculate_creepage
from planar_magnetics.kicad import Footprint, Pad, PadType, Reference, Value
from planar_magnetics.utils import dcr_of_annulus


class ViaStrip:
    """Defines a via-strip used to connect different layers
    """

    def __init__(
        viastrip_angle: float, viastrip_width: float,
    ):
        return None


class Turn:
    """Defines a single turn trace
    """

    def __init__(
        self,
        at,
        inner_radius: float,
        outer_radius: float,
        gap: float,
        layer: str = "F.Cu",
        angle: float = 0,
        start_termination=None,
        end_termination=None,
    ):
        assert (
            outer_radius > inner_radius
        ), "outer radius must be greater than inner radius"

        # store attributes
        self.at = at
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.gap = gap
        self.layer = layer
        self.start_termination = start_termination
        self.end_termination = end_termination

        # calculate the gap angles
        inner_gap_angle = math.asin(gap / inner_radius)
        outer_gap_angle = math.asin(gap / outer_radius)

        # create the arcs
        inner_arc = Arc(
            at,
            inner_radius,
            inner_gap_angle / 2 + angle,
            2 * math.pi - inner_gap_angle / 2 + angle,
        )
        outer_arc = Arc(
            at,
            outer_radius,
            2 * math.pi - outer_gap_angle / 2 + angle,
            outer_gap_angle / 2 + angle,
        )

        # if isinstance(start_termination, ViaStrip):

        # create the polygon
        points = [inner_arc, outer_arc]
        self.polygon = Polygon(points, layer)

    def estimate_dcr(self, thickness: float, rho: float = 1.68e-8):
        """Estimate the DC resistance of the winding

        This function will estimate the DC resistance of the winding by calculating the estimated
        dc resistance of each turn and adding the estimated inter-turn via resistance 
        
        Args:
            thickness (float): The copper thickness of the layer
            rho (float): The conductivity of the material used in the layer

        Returns:
            float: An estimation of the DC resistance in ohms
        """

        # calculate the termination resistance
        start_termination_resistance = (
            self.start_termination.estimate_dcr(temperature)
            if self.start_termination
            else 0
        )
        end_termination_resistance = (
            self.end_termination.estimate_dcr(temperature)
            if self.end_termination
            else 0
        )

        # estimate the resistance of the turn
        turn_resistance = dcr_of_annulus(
            thickness, self.inner_radius, self.outer_radius, rho
        )

        total_resistance = (
            start_termination_resistance + end_termination_resistance + turn_resistance
        )
        return total_resistance

    def __str__(self):
        return self.polygon.__str__()


# # calculate the gap angles
# inner_gap_angle = math.asin(gap / inner_radius)
# outer_gap_angle = math.asin(gap / outer_radius)

# # create the arcs
# start_via_arc = Arc(
#     at, inner_radius, inner_gap_angle / 2, inner_gap_angle / 2 + viastrip_angle,
# )
# inner_arc = Arc(
#     at,
#     inner_radius + viastrip_width,
#     inner_gap_angle / 2 + viastrip_angle,
#     2 * math.pi - inner_gap_angle / 2 - viastrip_angle,
# )
# end_via_arc = Arc(
#     at,
#     inner_radius,
#     2 * math.pi - inner_gap_angle / 2 - viastrip_angle,
#     2 * math.pi - inner_gap_angle / 2,
# )
# outer_arc = Arc(
#     at, outer_radius, 2 * math.pi - outer_gap_angle / 2, outer_gap_angle / 2,
# )

# # create the polygon
# points = [start_via_arc, inner_arc, end_via_arc, outer_arc]
# self.polygon = Polygon(points, layer)


if __name__ == "__main__":
    turn = Turn(
        at=Point(110e-3, 110e-3), inner_radius=6e-3, outer_radius=12e-3, gap=0.5e-3
    )

    from planar_magnetics.utils import weight_to_thickness

    print(turn.estimate_dcr(weight_to_thickness(4)) * 1e3)
