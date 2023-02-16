import math
from typing import Union
from pathlib import Path
from planar_magnetics.utils import dcr_of_annulus
from planar_magnetics.materials import Conductor, COPPER


class Winding:
    def estimate_dcr(
        self, thickness: float, temperature: float = 25, material: Conductor = COPPER
    ):
        """Estimate the DC resistance of the winding

        This function will estimate the DC resistance of the winding by calculating the estimated
        dc resistance of each turn and adding the estimated inter-turn via resistance

        Args:
            thickness: The copper thickness of the layer
            temperature: The temperature of the winding in degrees Celcius
            material: The material used for the winding

        Returns:
            float: An estimation of the DC resistance in ohms
        """
        # calculate the material resistivity
        rho = material.get_resistivity(temperature)

        # sum the resistance of each turn
        resistance = 0
        for r0, r1 in zip(self.inner_radii, self.outer_radii):
            resistance += dcr_of_annulus(thickness, r0, r1, rho)

        return resistance

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
