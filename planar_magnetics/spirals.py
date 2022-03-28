import math

from planar_magnetics.primitives import Arc, Polygon, Point, arc_from_polar


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

        # create the arcs for the inner turns
        angle = math.acos(1 - gap / radii[0])
        arcs = [arc_from_polar(radii[0], -math.pi + angle, math.pi)]
        for r0, r1 in zip(radii[0:-1], radii[1:]):
            angle = math.acos(gap / r1 + r0 * (1 - gap / r0) / r1)
            arc = arc_from_polar(r1, -math.pi + angle, math.pi)
            arcs.append(arc)

        # create the outermost arc
        a0 = math.acos(
            gap / outer_radius + radii[-1] * (1 - gap / radii[-1]) / outer_radius
        )
        a1 = math.acos(radii[-1] * (1 - gap / radii[-1]) / outer_radius)
        arc = arc_from_polar(outer_radius, math.pi + a0, -math.pi + a1)
        arcs.append(arc)

        # create the outer arcs of the other turns
        for r0, r1 in zip(radii[-2::-1], radii[-1:0:-1]):
            angle = math.acos((r0 - gap) / (r1 - gap))
            arc = arc_from_polar(r1 - gap, math.pi, -math.pi + angle)
            arcs.append(arc)

        self.polygon = Polygon(arcs, layer) + at

    def estimate_dcr(self, thickness: float, temperature: float = 25):
        """Estimate the DC resistance of the winding

        This function will estimate the DC resistance of the winding by calculating the estimated
        dc resistance of each turn and adding the estimated inter-turn via resistance 
        
        Args:
            thickness: thickness of the layer
            temperature: winding temperature in decrees C

        Returns:
            float:s An estimation of the DC resistance in ohms
        """

        # TODO
        raise NotImplementedError

    def __str__(self):
        return self.polygon.__str__()


if __name__ == "__main__":

    from planar_magnetics.utils import calculate_creepage, PollutionDegree

    # create a spiral inductor
    spiral = Spiral(
        at=Point(110e-3, 110e-3),
        inner_radius=10e-3,
        outer_radius=15e-3,
        num_turns=4,
        gap=calculate_creepage(
            500 / 4, PollutionDegree.Two
        ),  # creepage per turn for spiral that needs to withstand 500V
        layer="F.Cu",
    )

    # get the KiCad S expression to PCB footprint
    print(spiral)