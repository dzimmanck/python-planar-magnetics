import math
from planar_magnetics.geometry import Point
from planar_magnetics.windings import Spiral
from planar_magnetics.cores import Core
from planar_magnetics.kicad import Footprint, Reference, Value


class Transformer:
    """A multi-winding planar transformer

    Args:
        inner_radius: The inner radius of the windings in mm
        outer_radius: The outer radius of the windings in mm
        stackup: A dictionary of tuples specifying the layer and number of turns for each winding
        core_to_edge: The clearance required between the core surface and the pcb cutouts in 
        core_to_pcb: The distance between the core and the pcb surface in the z direction in mm
        board_thickness: The thickness of the PCB in mm
        trace_to_edge: The distance between winding edges and the edge cuts in mm
    """

    def __init__(
        self,
        inner_radius: float,
        outer_radius: float,
        stackup: dict,
        core_to_edge: float = 0.5,
        trace_to_edge: float = 1,
        core_to_pcb: float = 1,
        board_thickness: float = 1.6,
        opening_width: float = None,
        gap: float = 0,
    ):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.stackup = stackup
        self.core_to_edge = core_to_edge
        self.trace_to_edge = trace_to_edge
        self.core_to_pcb = core_to_pcb
        self.board_thickness = board_thickness
        if opening_width is None:
            self.opening_width = outer_radius - inner_radius
        else:
            self.opening_width = opening_width

        # create the layers
        self.layers = [
            Spiral(inner_radius, outer_radius, n, s, l) for l, n, s in stackup
        ]

        # create the core
        core_to_trace = core_to_edge + trace_to_edge
        self.core = Core(
            centerpost_radius=inner_radius - core_to_trace,
            window_width=(outer_radius - inner_radius) + 2 * core_to_trace,
            window_height=board_thickness + 2 * core_to_pcb,
            opening_width=self.opening_width + 2 * core_to_trace,
            gap=gap,
        )

    def to_kicad_footprint(
        self,
        name: str,
        create_core_step: bool = False,
        freecad_path: str = "C:/Program Files/FreeCAD 0.19/bin",
    ):
        """Export the Cffc inductor design as a KiCAD footprint file (*.kicad_mods)
        """

        # add the reference and value silkscreens
        x_loc = self.core.width / 2 + 1
        height_avail = (self.core.width - self.opening_width) / 2
        font_size = min(2, height_avail / 4)
        val_loc = Point(x_loc, self.opening_width / 2 + height_avail / 3)
        ref_loc = Point(x_loc, self.opening_width / 2 + 2 * height_avail / 3)
        reference = Reference(ref_loc, font_size)
        value = Value(val_loc, font_size)

        cutouts = self.core.create_pcb_cutouts(Point(0, 0), self.core_to_edge)

        # create a footprint from the various elements
        contents = cutouts + self.layers + [reference, value]
        footprint = Footprint(name, contents=contents)

        # write the footprint to a file
        fh = open(f"{name}.kicad_mod", "w")
        fh.write(footprint.__str__())
        fh.close()

        if create_core_step:
            self.core.to_step(f"{name}.step", self.core_to_pcb - 0.1, 0.1, freecad_path)

    def plot(self):
        import matplotlib.pyplot as mp

        n_rows = min(2, len(self.layers))
        n_columns = math.ceil(len(self.layers) / 2)
        fig, axes = mp.subplots(n_rows, n_columns)

        for layer, ax in zip(self.layers, axes.ravel()):
            layer.plot(ax=ax)


if __name__ == "__main__":

    transformer = Transformer(
        inner_radius=3,
        outer_radius=6,
        stackup=[
            ("In1.Cu", 1, 0.1),
            ("In1.Cu", 5, 0.1),
            ("In2.Cu", 5, 0.1),
            ("In1.Cu", 1, 0.1),
        ],
    )

    import matplotlib.pyplot as mp

    transformer.plot()
    mp.show()
