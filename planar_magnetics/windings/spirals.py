import math
from typing import Union
from pathlib import Path
from planar_magnetics.geometry import Arc, Polygon, Point, TWO_PI
from planar_magnetics.smoothing import smooth_polygon
from planar_magnetics.utils import dcr_of_annulus

# calculate optimal turn radii using equation 10 from Conceptualization and Analysis of a
# Next-Generation Ultra-Compact 1.5-kW PCB-Integrated Wide-Input-Voltage-Range 12V-Output
# Industrial DC/DC Converter Module
# https://www.pes-publications.ee.ethz.ch/uploads/tx_ethpublications/7_electronics-10-02158_FINAL_Knabben.pdf
def calc_trace_widths(inner_radius, outer_radius, num_turns):
    inverse_num_turns = 1 / num_turns
    radii = [
        (inner_radius ** (num_turns - i) * outer_radius ** i) ** inverse_num_turns
        for i in range(num_turns)
    ]

    return radii


class Spiral:
    """Create an optimized spiral multi-turn winding on a single layer
    """

    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        num_turns: float,
        gap: float,
        layer: str = "F.Cu",
        radius: float = 0.1e-3,
    ):
        assert num_turns >= 1, "A spiral must have at least 1 turn"

        # unpack the turns into the integer part and fractional part
        integer_turns, fractional_turns = divmod(num_turns, 1)
        integer_turns = int(integer_turns)

        # calculate the radii widths of each section
        wide_radii = calc_trace_widths(inner_radius, outer_radius, integer_turns)
        narrow_radii = calc_trace_widths(inner_radius, outer_radius, integer_turns + 1)

        # verify that the minimum trace width is greater than 2 x min radius
        min_trace_width = (
            narrow_radii[1] - narrow_radii[0] - gap
            if num_turns > 1
            else outer_radius - inner_radius
        )
        assert (
            min_trace_width > 2 * radius
        ), f"This spiral requires a min trace width of {1e3*min_trace_width}mm, which is less than 2 x radius"

        # calculate the over-rotation angle
        rotation_angle = -math.pi + TWO_PI * fractional_turns

        # create the arcs for the inner turns
        r0 = inner_radius - gap
        a0 = -math.pi
        arcs = []
        for i in range(integer_turns):
            # wide section
            r1 = wide_radii[i]
            angle = math.acos(r0 / r1)
            arc = Arc(at, r1, a0 + angle, math.pi)
            arcs.append(arc)

            # narrow section
            r0 = wide_radii[i]
            r1 = narrow_radii[i + 1]
            angle = math.acos(r0 / r1)
            arc = Arc(at, r1, -math.pi + angle, rotation_angle)
            arcs.append(arc)

            # update r0 and a0 for next turn
            r0 = r1
            a0 = rotation_angle

        # i = 0
        # while True:
        #     # narrow section
        #     r0 = wide_radii[i]
        #     r1 = narrow_radii[i + 1]
        #     angle = math.acos(r0 / r1)
        #     arc = Arc(at, r1, -math.pi + angle, rotation_angle)
        #     arcs.append(arc)

        #     # wide section
        #     try:
        #         r0 = r1
        #         r1 = wide_radii[i + 1]
        #         angle = math.acos(r0 / r1)
        #         arc = Arc(at, r1, rotation_angle + angle, math.pi)
        #         arcs.append(arc)
        #     except IndexError:
        #         break

        #     i += 1

        # create the outermost arc
        a0 = math.acos(narrow_radii[-1] / outer_radius)
        a1 = math.acos((narrow_radii[-1] - gap) / outer_radius)
        arc = Arc(at, outer_radius, rotation_angle + a0, rotation_angle + a1 - TWO_PI)
        arcs.append(arc)

        i = -1
        while True:
            # narrow section
            r0 = wide_radii[i] - gap
            r1 = narrow_radii[i] - gap
            angle = math.acos(r0 / r1)
            arc = Arc(at, r1, rotation_angle, -math.pi + angle)
            arcs.append(arc)

            # wide section
            try:
                r1 = r0
                r0 = narrow_radii[i - 1] - gap
                angle = math.acos(r0 / r1)
                arc = Arc(at, r1, math.pi, rotation_angle + angle)
                arcs.append(arc)
            except ValueError:
                break

            i -= 1

        polygon = Polygon(arcs, layer)

        # Add smoothing if a positive radius is provided
        if radius > 0:
            polygon = smooth_polygon(polygon, radius)

        self.polygon = polygon

        # self.wide_radii = wide_radii
        # self.wide_radii = wide_radii
        # self.outer_radii = [r - gap for r in radii[1:]] + [outer_radius]

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

        # sum the resistance of each turn
        resistance = 0
        for r0, r1 in zip(self.inner_radii, self.outer_radii):
            resistance += dcr_of_annulus(thickness, r0, r1, rho)

        return resistance

    def plot(self, max_angle: float = math.pi / 36):
        self.polygon.plot(max_angle)

    def export_to_dxf(
        self,
        filename: Union[str, Path],
        version: str = "R2000",
        encoding: str = None,
        fmt: str = "asc",
    ) -> None:
        """Export the polygon to a dxf file

        Args:
            filename: file name as string
            version: DXF version
            encoding: override default encoding as Python encoding string like ``'utf-8'``
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for Binary DXF
        """

        self.polygon.export_to_dxf(filename, version, encoding, fmt)

    def __str__(self):
        """Print KiCAD S-Expression of the spiral.  Assumes units are mm."""
        return self.polygon.__str__()


if __name__ == "__main__":

    from planar_magnetics.creepage import calculate_creepage
    from planar_magnetics.utils import weight_to_thickness

    # create a spiral inductor
    spiral = Spiral(
        at=Point(110e-3, 110e-3),
        inner_radius=6e-3,
        outer_radius=12e-3,
        num_turns=2.4,
        gap=calculate_creepage(500, 1),
        layer="F.Cu",
        radius=0,
    )

    # # estimate the dc resistance of this spiral assuming 2 oz copper
    # dcr = spiral.estimate_dcr(thickness=weight_to_thickness(2))
    # print(f"Estimated DCR of this spiral is {dcr*1e3} mOhms")

    # dispay a preview of the spiral from Python using matplotlib
    spiral.plot()

    # # # export this to a DXF file
    # # spiral.export_to_dxf("spiral.dxf")

    # # get the KiCad S expression, which can be then be copy-pasted into a KiCAD footprint file and edited from the footprint editer
    # print(spiral)
