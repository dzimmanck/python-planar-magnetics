import math
from planar_magnetics.geometry import Point
from planar_magnetics.windings import Spiral
from planar_magnetics.cores import Core
from planar_magnetics.kicad import Footprint, Reference, Value


class Transformer:
    def __init__(
        self, inner_radius: float, outer_radius: float, stackup: dict,
    ):
        origin = Point(0, 0)
        self.termination_width = 15

        # create the layers
        self.layers = [
            Spiral(origin, inner_radius, outer_radius, n, 0.1, l) for l, n in stackup
        ]

        # create the core
        self.core = Core(
            centerpost_radius=inner_radius - 1.6,
            window_width=(outer_radius - inner_radius) + 2 * 1.6,
            window_height=4,
            opening_width=10,
        )

    def to_kicad_footprint(self, name: str):
        """Export the Cffc inductor design as a KiCAD footprint file (*.kicad_mods)
        """

        # add the reference and value silkscreens
        x_loc = self.core.width / 2 + 1
        height_avail = (self.core.width - self.termination_width) / 2
        font_size = min(2, height_avail / 4)
        val_loc = Point(x_loc, self.termination_width / 2 + height_avail / 3)
        ref_loc = Point(x_loc, self.termination_width / 2 + 2 * height_avail / 3)
        reference = Reference(ref_loc, font_size)
        value = Value(val_loc, font_size)

        cutouts = self.core.create_pcb_cutouts(Point(0, 0))

        # create a footprint from the various elements
        contents = cutouts + self.layers + [reference, value]
        footprint = Footprint(name, contents=contents)

        # write the footprint to a file
        fh = open(f"{name}.kicad_mod", "w")
        fh.write(footprint.__str__())
        fh.close()

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
        stackup=[("In1.Cu", 1), ("In1.Cu", 5), ("In2.Cu", 5), ("In1.Cu", 1)],
    )

    import matplotlib.pyplot as mp

    transformer.plot()
    mp.show()
