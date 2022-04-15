import math
from typing import Union
from pathlib import Path
from planar_magnetics.geometry import Arc, Polygon, Point, TWO_PI, PI_OVER_TWO
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

        # create the inner arcs
        r0 = inner_radius - gap
        a0 = -math.pi
        arcs = []
        overlap = False
        for i in range(integer_turns):
            # wide section
            r1 = wide_radii[i]
            angle = math.acos(r0 / r1)
            arc = Arc(at, r1, a0 + angle, math.pi)
            arcs.append(arc)

            # narrow section
            r0 = r1
            r1 = narrow_radii[i + 1]
            angle = math.acos(r0 / r1) - math.pi
            arc = Arc(at, r1, angle, rotation_angle)
            if angle > rotation_angle:  # the linear sections of the spiral overlap
                x = -r0
                y = x * math.tan(rotation_angle + math.pi)
                point = Point(x, y) + at
                arcs.append(point)
                overlap = True
            else:
                arcs.append(arc)
                overlap = False

            # update r0 and a0 for next turn
            r0 = r1
            a0 = rotation_angle

        # create the outer arcs
        r1 = outer_radius
        a0 = rotation_angle + math.acos(narrow_radii[-1] / outer_radius) + TWO_PI
        for i in range(integer_turns, 0, -1):
            # wide section
            r0 = narrow_radii[i] - gap
            angle = math.acos(r0 / r1)
            arc = Arc(at, r1, a0, rotation_angle + angle)
            arcs.append(arc)

            # narrow section
            r0 = wide_radii[i - 1] - gap
            r1 = narrow_radii[i] - gap
            angle = math.acos(r0 / r1) - math.pi
            arc = Arc(at, r1, rotation_angle, angle)
            if angle > rotation_angle:
                x = -r0
                y = x * math.tan(rotation_angle + math.pi)
                point = Point(x, y) + at
                arcs.append(point)
            else:
                arcs.append(arc)

            # update for the next turn
            r1 = r0
            a0 = math.pi

        polygon = Polygon(arcs, layer)

        # plot code for debugging
        # DELETE ME!
        import matplotlib.pyplot as mp

        path = polygon.to_pwl_path()
        x, y = zip(*path)
        mp.plot(x, y)
        mp.show()

        # Add smoothing if a positive radius is provided
        if radius > 0:
            polygon = smooth_polygon(polygon, radius)

        self.polygon = polygon

        # store the dimensions for DCR calculations
        self.wide_inner_radii = wide_radii
        self.wide_outer_radii = [r - gap for r in wide_radii[1:]] + [outer_radius]
        self.narrow_inner_radii = narrow_radii
        self.narrow_outer_radii = [r - gap for r in narrow_radii[1:]] + [outer_radius]
        self.fractional_turns = fractional_turns

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

        # calculate the resistance of the side section
        wide = 0
        for r0, r1 in zip(self.wide_inner_radii, self.wide_outer_radii):
            wide += dcr_of_annulus(thickness, r0, r1, rho)

        # calculate the resistance of the narrow section
        narrow = 0
        for r0, r1 in zip(self.narrow_inner_radii, self.narrow_outer_radii):
            narrow += dcr_of_annulus(thickness, r0, r1, rho)

        # resistance is a weighted average
        resistance = self.fractional_turns * narrow * (1 - self.fractional_turns) * wide

        return resistance

    def plot(self, ax=None, max_angle: float = math.pi / 36):
        self.polygon.plot(ax, max_angle)

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
        at=Point(0, 0),
        inner_radius=6e-3,
        outer_radius=12e-3,
        num_turns=2.06,
        gap=calculate_creepage(500, 1),
        layer="F.Cu",
        radius=0,
    )

    # # estimate the dc resistance of this spiral assuming 2 oz copper
    # dcr = spiral.estimate_dcr(thickness=weight_to_thickness(2))
    # print(f"Estimated DCR of this spiral is {dcr*1e3} mOhms")

    # dispay a preview of the spiral from Python using matplotlib
    import matplotlib.pyplot as mp

    spiral.plot()
    mp.show()

    # # # export this to a DXF file
    # # spiral.export_to_dxf("spiral.dxf")

    # # get the KiCad S expression, which can be then be copy-pasted into a KiCAD footprint file and edited from the footprint editer
    # print(spiral)
