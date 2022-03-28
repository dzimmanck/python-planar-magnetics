class Core:
    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        termination_width: float = None,
        edge_to_trace: float = 0.635,
        edge_to_core: float = 0.5,
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

        # create polygons for the outer post cutouts
        extension = 3
        outer_cutout_radius = self.outerpost_radius - edge_to_core
        start_angle = math.asin(
            (termination_width / 2 + edge_to_trace) / outer_cutout_radius
        )
        end_angle = math.pi / 2 - start_angle
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, extension)
        corner3 = arc.start + Point(extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg1 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(-extension, 0)
        corner3 = arc.start + Point(0, extension)
        corner2 = Point(corner1.x, corner3.y)
        leg2 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(0, -extension)
        corner3 = arc.start + Point(-extension, 0)
        corner2 = Point(corner3.x, corner1.y)
        leg3 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        start_angle += math.pi / 2
        end_angle += math.pi / 2
        arc = arc_from_polar(outer_cutout_radius, start_angle, end_angle)
        corner1 = arc.end + Point(extension, 0)
        corner3 = arc.start + Point(0, -extension)
        corner2 = Point(corner1.x, corner2.y)
        leg4 = Polygon([arc, corner1, corner2, corner3], "Edge.Cuts", 0.1, "none") + at

        self.outerposts = [leg1, leg2, leg3, leg4]

    def __str__(self):

        # create the centerpost milling
        end = self.at + Point(self.centerpost_radius + self.edge_to_core, 0)
        layer = "Edge.Cuts"
        centerpost = f"(gr_circle (center {self.at}) (end {end}) (layer {layer}) (width 0.1) (fill none) (tstamp {self.tstamp}))"

        # create the milling for each corner
        outerposts = "\n".join(outerpost.__str__() for outerpost in self.outerposts)

        expression = "\n".join([centerpost, outerposts])

        return expression
