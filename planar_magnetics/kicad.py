from __future__ import annotations
from planar_magnetics.geometry import Point
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
        expression = f'(pad "{self.number}" {self.pad_type} {shape} (at {self.at}) (size {self.size*1e3} {self.size*1e3}) {drill_expression} (layers {layers}) (remove_unused_layers) (tstamp {self.tstamp}))'
        return expression


@dataclass
class Via:
    at: Point = Point(0, 0)
    size: float = 0.8
    drill: float = 0.4
    layers: (str) = ("F.Cu",)
    remove_unused_layers = True
    tstamp: uuid.UUID = uuid.uuid4()

    def to_pad(self, number: int = 1):
        """Convert to an equivalent through-hole pad"""

        return Pad(PadType.TH, number, self.at, self.size, ("*.Cu",), self.drill)

    def __str__(self):
        layers = " ".join(self.layers)
        annular_option = "(remove_unused_layers)" if self.remove_unused_layers else ""
        return f"(via (at {self.at}) (size {self.size*1e3}) (drill {self.drill*1e3}) (layers {layers}) {annular_option} (free) (net 0) (tstamp {self.tstamp}))"


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
