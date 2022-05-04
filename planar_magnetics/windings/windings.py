import math
from typing import Union
from pathlib import Path


class Winding:
    def mirror_x(self):
        """Mirror the winding about the x-axis"""
        mirrored = self
        mirrored.polygon = self.polygon.mirror_x()
        return mirrored

    def mirror_y(self):
        """Mirror the winding about the y-axis"""
        mirrored = self
        mirrored.polygon = self.polygon.mirror_y()
        return mirrored

    def rotate(self, angle: float):
        """Rotate a winding about its center"""
        rotated = self
        rotated.polygon = self.polygon.rotate_about(self.at, angle)
        return rotated

    def plot(self, ax=None, max_angle: float = math.pi / 36):
        self.polygon.plot(ax, max_angle)

    def to_dxf(
        self,
        filename: Union[str, Path],
        version: str = "R2000",
        encoding: str = None,
        fmt: str = "asc",
    ) -> None:
        """Export the polygon to a dxf file

        Args:
            filename: file name as string
            version: DXF version
            encoding: override default encoding as Python encoding string like ``'utf-8'``
            fmt: ``'asc'`` for ASCII DXF (default) or ``'bin'`` for Binary DXF
        """

        self.polygon.to_dxf(filename, version, encoding, fmt)

    def __str__(self):
        """Print KiCAD S-Expression of the spiral.  Assumes units are mm."""
        return self.polygon.__str__()
