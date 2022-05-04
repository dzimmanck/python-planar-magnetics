import math
from typing import Union
from pathlib import Path
from planar_magnetics.geometry import Arc, Polygon, Point
from planar_magnetics.smoothing import smooth_polygon
from planar_magnetics.utils import dcr_of_annulus
from planar_magnetics.materials import Conductor, COPPER
from planar_magnetics.windings.windings import Winding


class Spiral(Winding):
    """An optimized spiral multi-turn winding on a single layer

    Args:
        inner_radius: The inner radius of the spiral specified in mm
        outer_radius: The outer radius of the spiral specified in mm
        num_turns: The number of turns in the spiral
        spacing: The inter-turn spacing specified in mm
        layer: A string representing what layer the spiral is on
        radius: The radius used to smooth out the corners of the shape
        at: The center of the spiral
        rotation: The relative rotation of the spiral in radians

    Attributes:
        polygon: The final shape of the spiral
    """

    def __init__(
        self,
        inner_radius: float,
        outer_radius: float,
        num_turns: int,
        spacing: float,
        layer: str = "F.Cu",
        radius: float = 0,
        at: Point = Point(0, 0),
        rotation: float = 0,
    ):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.num_turns = num_turns
        self.at = at

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
            radii[1] - radii[0] - spacing
            if num_turns > 1
            else outer_radius - inner_radius
        )
        assert (
            min_trace_width > 2 * radius
        ), f"This spiral requires a min trace width of {1e3*min_trace_width}mm, which is less than 2 x radius"

        # create the arcs for the inner turns
        angle = math.acos(1 - spacing / radii[0])
        arcs = [Arc(at, radii[0], -math.pi + angle, math.pi)]
        for r0, r1 in zip(radii[0:-1], radii[1:]):
            angle = math.acos(spacing / r1 + r0 * (1 - spacing / r0) / r1)
            arc = Arc(at, r1, -math.pi + angle, math.pi)
            arcs.append(arc)

        # create the outermost arc
        a0 = math.acos(
            spacing / outer_radius
            + radii[-1] * (1 - spacing / radii[-1]) / outer_radius
        )
        a1 = math.acos(radii[-1] * (1 - spacing / radii[-1]) / outer_radius)
        arc = Arc(at, outer_radius, math.pi + a0, -math.pi + a1)
        arcs.append(arc)

        # create the outer arcs of the other turns
        for r0, r1 in zip(radii[-2::-1], radii[-1:0:-1]):
            angle = math.acos((r0 - spacing) / (r1 - spacing))
            arc = Arc(at, r1 - spacing, math.pi, -math.pi + angle)
            arcs.append(arc)

        polygon = Polygon(arcs, layer)

        # Add smoothing if a positive radius is provided
        if radius > 0:
            polygon = smooth_polygon(polygon, radius)

        self.polygon = polygon.rotate_about(at, rotation)

        self.inner_radii = radii
        self.outer_radii = [r - spacing for r in radii[1:]] + [outer_radius]

    def estimate_dcr(
        self, thickness: float, termperature: float = 25, material: Conductor = COPPER
    ):
        """Estimate the DC resistance of the winding

        This function will estimate the DC resistance of the winding by calculating the estimated
        dc resistance of each turn and adding the estimated inter-turn via resistance 
        
        Args:
            thickness: The copper thickness of the layer
            temperature: The temperature of the winding in degrees Celcius
            material: The material used for the winding

        Returns:
            float: An estimation of the DC resistance in ohms
        """
        # calculate the material resistivity
        rho = material.get_resistivity(termperature)

        # sum the resistance of each turn
        resistance = 0
        for r0, r1 in zip(self.inner_radii, self.outer_radii):
            resistance += dcr_of_annulus(thickness, r0, r1, rho)

        return resistance


if __name__ == "__main__":

    from planar_magnetics.creepage import calculate_creepage
    from planar_magnetics.utils import weight_to_thickness

    # create a spiral inductor
    spiral = Spiral(
        at=Point(110e-3, 110e-3),
        inner_radius=6e-3,
        outer_radius=12e-3,
        num_turns=1,
        spacing=calculate_creepage(500, 1),
        layer="F.Cu",
        radius=0.3e-3,
    )

    # estimate the dc resistance of this spiral assuming 2 oz copper
    dcr = spiral.estimate_dcr(thickness=weight_to_thickness(2))
    print(f"Estimated DCR of this spiral is {dcr*1e3} mOhms")

    # dispay a preview of the spiral from Python using matplotlib
    spiral.plot()

    # # export this to a DXF file
    # spiral.export_to_dxf("spiral.dxf")

    # get the KiCad S expression, which can be then be copy-pasted into a KiCAD footprint file and edited from the footprint editer
    print(spiral)
