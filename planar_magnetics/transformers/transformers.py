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
        self.termination_width = 15e-3
        gap = 0.2e-3

        # create the layers
        self.layers = [
            Spiral(origin, inner_radius, outer_radius, n, gap, l) for l, n in stackup
        ]

        # create the core
        self.core = Core(
            at=origin,
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            termination_width=self.termination_width,
            edge_to_trace=0.635e-3,
            edge_to_core=0.5e-3,
        )

    def to_kicad_footprint(self, name: str):
        """Export the Cffc inductor design as a KiCAD footprint file (*.kicad_mods)
        """

        # add the reference and value silkscreens
        x_loc = self.core.width / 2 + 1e-3
        height_avail = (self.core.width - self.termination_width) / 2
        font_size = min(2e-3, height_avail / 4)
        val_loc = Point(x_loc, self.termination_width / 2 + height_avail / 3)
        ref_loc = Point(x_loc, self.termination_width / 2 + 2 * height_avail / 3)
        reference = Reference(ref_loc, font_size)
        value = Value(val_loc, font_size)

        # create a footprint from the various elements
        contents = [self.core] + self.layers + [reference, value]
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
        inner_radius=3e-3,
        outer_radius=6e-3,
        stackup=[("In1.Cu", 1), ("In1.Cu", 5), ("In2.Cu", 5), ("In1.Cu", 1)],
    )

    import matplotlib.pyplot as mp

    transformer.plot()
    mp.show()
