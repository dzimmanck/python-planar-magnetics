import math
import uuid
from planar_magnetics.materials import Ferrite, N96
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
    x = radius * (math.cos(start_angle) - math.cos(end_angle))

    # solve for the extension using the quadratic equasion
    extension = (-2 * x + math.sqrt(4 * x ** 2 + 4 * extension_area)) / 2

    return extension


class Core:
    """A magnetic core object

    Args:
        centerpost_radius: The centerpost radius in mm
        window_width: The winding window width in mm
        window_height: The winding window height in mm
        opening_width: The core termination opening widths in mm
        gap: The core cap in mm

    Attributes:
        centerpost_area: The area of the centerpost in square mm
        volume: The core volume in cubic mm
    """

    def __init__(
        self,
        centerpost_radius: float,
        window_width: float,
        window_height: float,
        opening_width: float = None,
        gap: float = 0,
    ):

        self.centerpost_radius = centerpost_radius
        self.window_width = window_width
        self.window_height = window_height

        # if the user does not specify a opening width for terminations, just use the window width
        if opening_width is None:
            self.opening_width = window_width
        else:
            self.opening_width = opening_width

        self.gap = gap

        # calculate core dimensions
        self.outerpost_radius = centerpost_radius + window_width

        # calculate the centerpost area
        self.centerpost_area = math.pi * self.centerpost_radius ** 2

        # calculate the start angle first outer post cutout leg
        start_angle = math.asin((self.opening_width / 2) / self.outerpost_radius)

        # calculate the end angle of the first outer post cutout leg
        end_angle = math.pi / 2 - start_angle

        # create polygons for the outer post cutouts
        extension = calculate_core_extension(
            area=self.centerpost_area,
            radius=self.outerpost_radius,
            opening_width=self.opening_width,
        )

        # Calculate the plate thickness so that the plate mating surface has the same area as the
        # centerpost area
        self.plate_thickness = self.centerpost_area / (
            2 * self.centerpost_radius * math.pi
        )

        self.width = 2 * (self.outerpost_radius * math.cos(start_angle) + extension)
        self.height = self.window_height + 2 * self.plate_thickness

    def get_coreloss(
        self, B: float, f: float, ferrite: Ferrite = N96, temperature: float = 25
    ):
        """Calculate the coreloss using steinmetz parameters
        """

        # This is not tested, so raise error
        raise NotImplementedError

        k, alpha, beta = ferrite.get_steinmetz_parameters(temperature)

        Pv = k * f ** alpha * B ** beta

        return Pv * self.volume

    def to_parts(
        self,
        freecad_path: str = "C:/Program Files/FreeCAD 0.19/bin",
        tol: float = 0.1,
        spacer_thickness: float = 0.0,
    ):

        # try and import the FreeCAD python extension
        try:
            import sys

            sys.path.append(freecad_path)
            import FreeCAD as cad
        except Exception:
            raise ImportError("You must have FeeCAD installed")
        import Part

        # create the center piece
        circle = Part.makeCircle(self.centerpost_radius)
        wire = Part.Wire(circle)
        disk = Part.Face(wire)
        centerpost = disk.extrude(cad.Vector(0, 0, self.window_height / 2))
        to_gap = self.centerpost_radius + self.window_width / 2 - self.gap / 2
        circle = Part.makeCircle(to_gap, cad.Vector(0, 0, self.window_height / 2))
        wire = Part.Wire(circle)
        disk = Part.Face(wire)
        topplate = disk.extrude(cad.Vector(0, 0, self.plate_thickness))
        centerpiece = centerpost.fuse(topplate)

        # create the top plate
        square = Part.makePlane(
            self.width,
            self.width,
            cad.Vector(-self.width / 2, -self.width / 2, self.window_height / 2,),
        )
        circle = Part.makeCircle(
            to_gap + self.gap, cad.Vector(0, 0, self.window_height / 2)
        )
        wire = Part.Wire(circle)
        disk = Part.Face(wire)
        topplate_face = square.cut(disk)
        topplate = topplate_face.extrude(cad.Vector(0, 0, self.plate_thickness))

        # create the legs
        opening_left_to_right = Part.makePlane(
            self.width,
            self.opening_width,
            cad.Vector(
                -self.width / 2, -self.opening_width / 2, self.window_height / 2,
            ),
        )
        opening_front_to_back = Part.makePlane(
            self.opening_width,
            self.width,
            cad.Vector(
                -self.opening_width / 2, -self.width / 2, self.window_height / 2,
            ),
        )
        circle = Part.makeCircle(
            self.outerpost_radius, cad.Vector(0, 0, self.window_height / 2),
        )
        wire = Part.Wire(circle)
        disk = Part.Face(wire)
        leg_face = square.cut(disk)
        legs_face = leg_face.cut(opening_left_to_right)
        legs_face = legs_face.cut(opening_front_to_back)
        legs = legs_face.extrude(cad.Vector(0, 0, -self.window_height / 2))

        # fuse the legs to the top plate
        topplate = topplate.fuse(legs)

        # create the spacer
        circle = Part.makeCircle(
            self.outerpost_radius - tol, cad.Vector(0, 0, self.window_height / 2),
        )
        wire = Part.Wire(circle)
        disk = Part.Face(wire)
        circle = Part.makeCircle(
            self.centerpost_radius + tol, cad.Vector(0, 0, self.window_height / 2),
        )
        wire = Part.Wire(circle)
        cutout = Part.Face(wire)
        washer = disk.cut(cutout)
        spacer = washer.extrude(cad.Vector(0, 0, -spacer_thickness))
        circle = Part.makeCircle(
            to_gap + self.gap - tol, cad.Vector(0, 0, self.window_height / 2),
        )
        wire = Part.Wire(circle)
        disk = Part.Face(wire)
        circle = Part.makeCircle(to_gap + tol, cad.Vector(0, 0, self.window_height / 2))
        wire = Part.Wire(circle)
        cutout = Part.Face(wire)
        washer = disk.cut(cutout)
        gap_spacer = washer.extrude(cad.Vector(0, 0, self.plate_thickness))
        spacer = spacer.fuse(gap_spacer)

        if not self.gap:
            top_half = centerpiece.fuse(topplate)
            top_half = top_half.removeSplitter()

            return {"core": top_half, "spacer": spacer}
        else:
            topplate = topplate.removeSplitter()
            centerpiece = centerpiece.removeSplitter()

            return {
                "core center": centerpiece,
                "core outer": topplate,
                "spacer": spacer,
            }

        # # bottom_half = top_half.mirror(cad.Vector(0, 0, 0), cad.Vector(0, 0, -1))

        # core = Part.makeCompound([top_half, bottom_half])

        # # scale part
        # core = core.scale(scale)

        # return core

    def to_step(
        self, filename: str, freecad_path: str = "C:/Program Files/FreeCAD 0.19/bin",
    ):
        """Export the core geometry to a step file
        """

        # try and import the FreeCAD python extension
        try:
            import sys

            sys.path.append(freecad_path)
            import FreeCAD as cad
        except Exception:
            raise ImportError("You must have FeeCAD installed")
        import Part

        parts = [part for part in self.to_parts().values() if part is not None]
        part = Part.makeCompound(parts)

        # top_half = parts[0]
        # for part in parts[1:]:
        #     top_half = top_half.fuse(part)

        # # bottom_half = top_half.mirror(cad.Vector(0, 0, 0), cad.Vector(0, 0, -1))
        part.exportStep(filename)

    def create_pcb_cutouts(self, center: Point = Point(0, 0), clearance: float = 0.5):
        """Generate cutout polygons"""

        # calculate the radius of the outer post cutouts
        outer_cutout_radius = self.outerpost_radius - clearance

        # calculate the start angle first outer post cutout leg
        start_angle = math.asin(
            (self.opening_width / 2 - clearance) / outer_cutout_radius
        )

        # calculate the end angle of the first outer post cutout leg
        end_angle = math.pi / 2 - start_angle

        # TODO: This could be a circle if it was supported
        centerpost = Polygon(
            [Arc(center, self.centerpost_radius + clearance, -math.pi, math.pi)],
            "Edge.Cuts",
            0.1,
            "none",
        )

        cutout_extension = (
            self.width / 2 + clearance - outer_cutout_radius * math.cos(start_angle)
        )

        # calculate the arcs
        arc = Arc(center, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, cutout_extension)
        corner3 = arc.start + Point(cutout_extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg1 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none")

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = Arc(center, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(-cutout_extension, 0)
        corner3 = arc.start + Point(0, cutout_extension)
        corner2 = Point(corner1.x, corner3.y)
        leg2 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none")

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = Arc(center, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, -cutout_extension)
        corner3 = arc.start + Point(-cutout_extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg3 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none")

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = Arc(center, outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(cutout_extension, 0)
        corner3 = arc.start + Point(0, -cutout_extension)
        corner2 = Point(corner1.x, corner2.y)
        leg4 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none")

        cutouts = [centerpost, leg1, leg2, leg3, leg4]

        return cutouts


if __name__ == "__main__":

    core = Core(8.6, 6, 6, 3, 0.5)
    core.to_step("core.step")
