# python-planar-magnetics
Programmaticaly create HF planar inductors and transformers.

# Background
The workflow for developing planar magnetics can be very inefficient and frustrating.  Power electronics engineers either struggle to draw planar windings directly in CAD or struggle with the inefficient design -> mechanical cad -> electrical cad -> dcr -> redesign flow.  `python-planar-magnetics` seeks to provide an much more efficient developer experience by generating optimized geometric structures for planar magnetics programmatically and then exporting these structures either to S-expressions (KiCAD) or DXF files (All other PCB CAD tools).  The library allows you to define planar structures the follow DRC guidlines programmatically and estimate DCR and preview shapes without ever optning a CAD tool.

# Basic Structure
The library allows both generation of planar magnetic 2-D elements (core cutouts, spirals, single turns) as well as complete components (inductors, transformers).  This offers two distinct types of user experiences.  If the user wants to create a complex design with several custom or unanticipated features such as a unique core geometry or a different layer interconnection strategy, then they can use this library to generate the base structures, import into their favorite CAD tool, and then manually modify or augment in any way they see fit.  If they simple want a complete planar inductor or transformer designed by this library, they can use the inductor and transformer modules to programatically create a complete part which can then be exported as a KiCAD footprint file or a collection of DXF files for each layer that can then be imported and stiched back together in CAD.

## Example: Creating a spiral

```python
from planar_magnetics.creepage import calculate_creepage
from planar_magnetics.utils import weight_to_thickness

# create a spiral inductor
    spiral = Spiral(
        at=Point(110e-3, 110e-3),
        inner_radius=6e-3,
        outer_radius=12e-3,
        num_turns=3,
        gap=calculate_creepage(500, 1),
        layer="F.Cu",
        radius=0.3e-3,
    )

    # estimate the dc resistance of this spiral assuming 2 oz copper
    dcr = spiral.estimate_dcr(thickness=weight_to_thickness(2))
    print(f"Estimated DCR of this spiral is {dcr*1e3} mOhms")

    # dispay a preview of the spiral from Python using matplotlib
    spiral.plot()

    # export this to a DXF file
    spiral.export_to_dxf("spiral.dxf")

    # get the KiCad S expression, which can be then be copy-pasted into a KiCAD footprint file and edited from the footprint editer
    print(spiral)
```

<img src="images/4turn_spiral.png" alt="4 turn spiral" style="width:400px;"/>

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
