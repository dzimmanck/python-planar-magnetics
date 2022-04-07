# python-planar-magnetics
Programmaticaly create HF planar inductors and transformers.

# Background
The workflow for developing planar magnetics can be very inefficient and frustrating.  Power electronics engineers either struggle to draw planar windings directly in CAD or struggle with the inefficient design -> mechanical cad -> electrical cad -> dcr -> redesign flow.  `python-planar-magnetics` seeks to provide an much more efficient developer experience by generating optimized geometric structures for planar magnetics programmatically and then exporting these structures either to S-expressions (KiCAD) or DXF files (All other PCB CAD tools).  The library allows you to define planar structures that follow DRC guidlines programmatically and estimate DCR and preview shapes without ever opening a CAD tool.

# Basic Structure
The library allows both generation of planar magnetic 2-D elements (core cutouts, spirals, single turns) as well as complete components (inductors, transformers).  This offers two distinct types of user experiences.  If the user wants to create a complex design with several custom or unanticipated features such as a unique core geometry or a different layer interconnection strategy, then they can use this library to generate the base structures, import into their favorite CAD tool, and then manually modify or augment in any way they see fit.  If they simple want a complete planar inductor or transformer designed by this library, they can use the inductor and transformer modules to programatically create a complete part which can then be exported as a KiCAD footprint file or a collection of DXF files for each layer that can then be imported and stitched back together in CAD.

## Example: Creating a spiral

```python
from planar_magnetics.creepage import calculate_creepage
from planar_magnetics.utils import weight_to_thickness
from planar_magnetics.windings import Spiral
from planar_magnetics.geometry import Point

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

Preview (Matplotlib)       |  KiCAD                    |  DXF
:-------------------------:|:-------------------------:|:--------------------------:
![](https://github.com/dzimmanck/python-planar-magnetics/blob/main/images/3turn_spiral_matplotlib.png?raw=True)  |  ![](https://github.com/dzimmanck/python-planar-magnetics/blob/main/images/3turn_spiral_kicad.png?raw=True)  |  ![](https://github.com/dzimmanck/python-planar-magnetics/blob/main/images/3turn_spiral_dxf.png?raw=True)

## Example: Creating a complete inductor

Currently, the library only supports creation of a [Compensating Fringing Field Concept](https://www.psma.com/sites/default/files/uploads/files/Introduction%20of%20the%20CFFC-Compensating%20Fringing%20Field%20Concept%20Schaefer%2C%20ETH%20Zurich.pdf) inductor as a complete part.  Support for this part was added first as it has a relatively simple via structure and as it is an inductor, only requires functional isolation which simplifies meeting spacing requirements.  Support for more complex parts such as higher turn count inductors and transformers are planned for the future.

```python
from planar_magnetics.inductors import Cffc
from planar_magnetics.utils import weight_to_thickness

# create an inductor using the CFFC technique
inductor = Cffc(inner_radius=4.9e-3, outer_radius=9e-3, number_turns=5, voltage=500)

# estimate the dc resistance of this inductor
# using the CFFC structure, a 5 turn inductor requires 6 layers
# assume we are using 1.5 oz on top/botton and 2oz on interior layers
thicknesses = [
    weight_to_thickness(1.5),
    weight_to_thickness(2),
    weight_to_thickness(2),
    weight_to_thickness(2),
    weight_to_thickness(2),
    weight_to_thickness(1.5),
]
dcr = inductor.estimate_dcr(thicknesses)
print(f"Estimated DCR of this inductor is {dcr*1e3} mOhms")

# create a complete KiCAD footprint
inductor.to_kicad_footprint("cffc_inductor")
```

![KiCAD Footprint](https://github.com/dzimmanck/python-planar-magnetics/blob/main/images/cffc_kicad_footprint.png?raw=True)
