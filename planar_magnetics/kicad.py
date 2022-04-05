from __future__ import annotations
from dataclasses import dataclass
import uuid


@dataclass
class ThroughHolePad:
    number: int
    at: Point
    size: float
    drill: float
    tstamp: uuid.UUID = uuid.uuid4()

    def __str__(self):
        expression = f'(pad "{self.number}" thru_hole circle (at {self.at}) (size {self.size*1e3} {self.size*1e3}) (drill {self.drill*1e3}) (layers *.Cu) (remove_unused_layers) (tstamp {self.tstamp}))'
        return expression


class Footprint:
    """Python representation of a KiCAD footprint
    """

    def __init__(
        self, name: str, version: str = "20211014", contents=[],
    ):
        self.name = name
        self.version = version
        self.contents = contents

    def __str__(self):
        header = f'footprint "{self.name}" (version {self.version}) (generator python_planar_magnetics)'
        contents = "\n".join([content.__str__() for content in self.contents])
        expression = f"({header} {contents})"

        return expression


if __name__ == "__main__":
    from planar_magnetics.geometry import Point

    pad1 = ThroughHolePad(1, Point(0, 0), 0.8e-3, 0.4e-3)
    pad2 = ThroughHolePad(2, Point(2e-3, 2e-3), 0.8e-3, 0.4e-3)
    footprint = Footprint("test", contents=[pad1, pad2])

    print(footprint)
