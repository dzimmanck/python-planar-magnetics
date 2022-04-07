import math
import uuid
from planar_magnetics.geometry import (
    Arc,
    Point,
    Polygon,
    TWO_PI,
    PI_OVER_TWO,
)


def calculate_core_extension(area: float, radius: float, opening_width: float) -> float:
    """Calculate the required core extension to have the same area as the center-post

    Args:
        area (float): The total required area of the outer legs
        radius (float): The radius of the edge of the outer legs

    Returns:
        float: The required extension
    """

    # first, calculate the area of a single leg with no extension
    start_angle = math.asin((opening_width / 2) / radius)
    end_angle = PI_OVER_TWO - start_angle

    x = math.sqrt(radius ** 2 - (opening_width / 2) ** 2)

    # start with the area of the square from the center to the corner
    min_leg_area = x ** 2

    # subtract the opening triangles
    min_leg_area -= x * opening_width / 2

    # subtract the arc
    min_leg_area -= ((end_angle - start_angle) / TWO_PI) * (math.pi * radius ** 2)

    # calculated the required extension area
    extension_area = area / 4 - min_leg_area

    # if the minimum leg area is already sufficient, then just return 0
    if extension_area <= 0:
        return 0

    # calculate the minimum width of the leg
    x = math.cos(start_angle) - math.cos(end_angle)

    # calculate the retuired extension to equalize the area
    extension = (extension_area - x ** 2) / (2 * x)

    return extension


class Core:
    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        termination_width: float = None,
        edge_to_trace: float = 0.635e-3,
        edge_to_core: float = 0.5e-3,
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

        # calculate the radius of the outer post cutouts
        outer_cutout_radius = self.outerpost_radius - edge_to_core

        # calculate the start angle first outer post cutout leg
        start_angle = math.asin(
            (termination_width / 2 + edge_to_trace) / outer_cutout_radius
        )

        # calculate the end angle of the first outer post cutout leg
        end_angle = math.pi / 2 - start_angle

        # create polygons for the outer post cutouts
        extension = calculate_core_extension(
            area=self.centerpost_area,
            radius=self.outerpost_radius,
            opening_width=termination_width + 2 * edge_to_trace + 2 * edge_to_core,
        )
        cutout_extension = extension + edge_to_core

        # calculate the arcs
        arc = Arc(at, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, cutout_extension)
        corner3 = arc.start + Point(cutout_extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg1 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1e-3, "none")

        # calculate the core cutout dimensions, which can be used for silkscreen placement
        self.width = 2 * (arc.start.x + cutout_extension)
        self.length = self.width

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = Arc(at, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(-cutout_extension, 0)
        corner3 = arc.start + Point(0, cutout_extension)
        corner2 = Point(corner1.x, corner3.y)
        leg2 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1e-3, "none")

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = Arc(at, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, -cutout_extension)
        corner3 = arc.start + Point(-cutout_extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg3 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1e-3, "none")

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = Arc(at, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(cutout_extension, 0)
        corner3 = arc.start + Point(0, -cutout_extension)
        corner2 = Point(corner1.x, corner2.y)
        leg4 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1e-3, "none")

        self.outerposts = [leg1, leg2, leg3, leg4]

    def __str__(self):

        # create the centerpost milling
        end = self.at + Point(self.centerpost_radius + self.edge_to_core, 0)
        layer = "Edge.Cuts"
        centerpost = f"(fp_circle (center {self.at}) (end {end}) (layer {layer}) (width 0.1) (fill none) (tstamp {self.tstamp}))"

        # create the milling for each corner
        outerposts = "\n".join(outerpost.__str__() for outerpost in self.outerposts)

        expression = "\n".join([centerpost, outerposts])

        return expression
