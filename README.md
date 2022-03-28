# python-planar-magnetics
Programmaticaly create HF planar inductors and transformers.

# Background
The workflow for developing planar magnetics can be very inefficient and frustrating.  Power electronics engineers either struggle to draw planar windings directly in CAD, or if they are lucky enough to have a mechanical engineer to work with give hand drawings that get converted into DXF files and they imported into CAD, where they then fail DRC requireing changes.  `python-planar-magnetics` seeks to provide an much more efficient developer experience by generating optimized geometric structures for planar magnetics programmatically and then exporting these structures either to S-expressions (KiCAD) or DXF files (All other PCB CAD tools).

# Example Usage

Create a spiral winding

```python
from planars import Spiral

# create a spiral winding
spiral = Spiral(inner_radius=10e-3,
                outer_radius=15e-3,
                gap = 0.1e-3,
                num_turns = 4)

# print a KiCAD S-expression
print(spiral)
```

Create a [Compensating Fringing Field Concept](https://www.psma.com/sites/default/files/uploads/files/Introduction%20of%20the%20CFFC-Compensating%20Fringing%20Field%20Concept%20Schaefer%2C%20ETH%20Zurich.pdf) inductor.

```python
from planars import Cffc

# create a spiral winding
cffc = Cffc(inner_radius=10e-3,
            outer_radius=15e-3,
                gap = 0.1e-3)

# print a KiCAD S-expression
print(cffc)
```

# TODO:

1.  Add methods to estimate DC resistance
2.  Add helper functions for calculating required geometric gaps for creepage and clearance requirements
3.  Add DXF export
4.  Add Transformer class which optimally places vias that interconnect winding layers.  This should support optimal shield layers as well.
6.  Better support for core cutouts
7.  Output KiCAD component files rather the just the S-expression of the geometry
