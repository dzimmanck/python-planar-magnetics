from __future__ import annotations
from dataclasses import dataclass
import uuid
from enum import Enum


class PadType(Enum):
    TH = 1
    SMD = 2

    def __str__(self):
        if self.value == 1:
            return "thru_hole"
        else:
            return "smd"


@dataclass
class Pad:
    pad_type: PadType
    number: int
    at: Point
    size: float
    layers: (str) = ("*.Cu",)
    drill: float = None
    tstamp: uuid.UUID = uuid.uuid4()

    def __str__(self):

        layers = " ".join(self.layers)
        drill_expression = f"(drill {self.drill*1e3})" if self.drill else ""
        shape = "circle" if self.pad_type == PadType.TH else "rect"
        expression = f'(pad "{self.number}" {self.pad_type} circle (at {self.at}) (size {self.size*1e3} {self.size*1e3}) {drill_expression} (layers {layers}) (remove_unused_layers) (tstamp {self.tstamp}))'
        return expression


@dataclass
class Reference:
    at: Point
    font_size: float = 1.27e-3
    thickness: float = 0.15e-3
    justification: str = "left"
    tstamp: uuid.UUID = uuid.uuid4()

    def __str__(self):

        expression = f'(fp_text reference "Ref**" (at {self.at}) (layer "F.SilkS") (effects (font (size {self.font_size*1e3} {self.font_size*1e3}) (thickness {self.thickness*1e3})) (justify {self.justification})) (tstamp {self.tstamp}))'

        return expression


@dataclass
class Value:
    at: Point
    font_size: float = 1.27e-3
    thickness: float = 0.15e-3
    justification: str = "left"
    tstamp: uuid.UUID = uuid.uuid4()

    def __str__(self):

        expression = f'(fp_text value "Val**" (at {self.at}) (layer "F.SilkS") (effects (font (size {self.font_size*1e3} {self.font_size*1e3}) (thickness {self.thickness*1e3})) (justify {self.justification})) (tstamp {self.tstamp}))'

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
