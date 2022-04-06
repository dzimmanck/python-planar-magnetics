import math
from typing import Union
from pathlib import Path
from planar_magnetics.geometry import Arc, Polygon, Point
from planar_magnetics.smoothing import round_corner, smooth_polygon
from planar_magnetics.utils import dcr_of_annulus


class Spiral:
    """Create an optimized spiral multi-turn winding on a single layer
    """

    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        num_turns: int,
        gap: float,
        layer: str = "F.Cu",
        radius: float = 0.1e-3,
    ):

        # calculate optimal turn radii using equation 10 from Conceptualization and Analysis of a
        # Next-Generation Ultra-Compact 1.5-kW PCB-Integrated Wide-Input-Voltage-Range 12V-Output
        # Industrial DC/DC Converter Module
        # https://www.pes-publications.ee.ethz.ch/uploads/tx_ethpublications/7_electronics-10-02158_FINAL_Knabben.pdf
        inverse_num_turns = 1 / num_turns
        radii = [
            (inner_radius ** (num_turns - i) * outer_radius ** i) ** inverse_num_turns
            for i in range(num_turns)
        ]

        # verify that the minimum trace width is greater than 2 x min radius
        min_trace_width = (
            radii[1] - radii[0] - gap if num_turns > 1 else outer_radius - inner_radius
        )
        assert (
            min_trace_width > 2 * radius
        ), f"This spiral requires a min trace width of {1e3*min_trace_width}mm, which is less than 2 x radius"

        # create the arcs for the inner turns
        angle = math.acos(1 - gap / radii[0])
        arcs = [Arc(at, radii[0], -math.pi + angle, math.pi)]
        for r0, r1 in zip(radii[0:-1], radii[1:]):
            angle = math.acos(gap / r1 + r0 * (1 - gap / r0) / r1)
            arc = Arc(at, r1, -math.pi + angle, math.pi)
            arcs.append(arc)

        # create the outermost arc
        a0 = math.acos(
            gap / outer_radius + radii[-1] * (1 - gap / radii[-1]) / outer_radius
        )
        a1 = math.acos(radii[-1] * (1 - gap / radii[-1]) / outer_radius)
        arc = Arc(at, outer_radius, math.pi + a0, -math.pi + a1)
        arcs.append(arc)

        # create the outer arcs of the other turns
        for r0, r1 in zip(radii[-2::-1], radii[-1:0:-1]):
            angle = math.acos((r0 - gap) / (r1 - gap))
            arc = Arc(at, r1 - gap, math.pi, -math.pi + angle)
            arcs.append(arc)

        polygon = Polygon(arcs, layer)

        # Add smoothing if a positive radius is provided
        if radius > 0:
            polygon = smooth_polygon(polygon, radius)

        self.polygon = polygon

        self.radii = radii

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
        for r0, r1 in zip(self.radii[0:-1], self.radii[1:]):
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
        return self.polygon.__str__()


if __name__ == "__main__":

    from planar_magnetics.creepage import calculate_creepage
    from planar_magnetics.utils import weight_to_thickness

    # create a spiral inductor
    spiral = Spiral(
        at=Point(110e-3, 110e-3),
        inner_radius=6e-3,
        outer_radius=12e-3,
        num_turns=5,
        gap=calculate_creepage(500, 1),
        layer="F.Cu",
        radius=0.3e-3,
    )

    # estimate the resistance of the spiral
    thickness = weight_to_thickness(4)
    resistance = spiral.estimate_dcr(thickness)
    print(f"Estimated DCR of this spiral is {resistance*1e3} mOhms")

    # export to dxf
    spiral.export_to_dxf("test.dxf")
