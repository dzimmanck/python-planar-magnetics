# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [v0.1.7]

### Fixed
-Fix [issue-16](https://github.com/dzimmanck/python-planar-magnetics/issues/16).  The estimate_dcr method is now defined in the Winding class and inherited by all winding classes.
-Fix [issue-18](https://github.com/dzimmanck/python-planar-magnetics/issues/18).  Mutable default values in kicad.py dataclasses.
-Feature [issue-21](https://github.com/dzimmanck/python-planar-magnetics/issues/21). Updated FreeCAD paths throughout package to reference a configurable environment variable.

### Added

## [v0.1.6]

### Fixed
-Fix spelling error in the spiral `estimate_dcr` method ("temperature", not "termperature")

### Added
-Update README with information about the `Core` class
-Minor changes to CAD API

## [v0.1.5]

### Fixed

### Added
-Added ability to rotate point, arcs, polygons and windings
-Added ability to mirror point, arcs, polygons and windings about the x or y axis

## [v0.1.4]

### Fixed

### Added
-Change convention to assume dimensions are specified in mm rather than m
-Add support for coreloss calculations
-Add support for more complex CAD part generation for cores
-Minor code cleanups and API changes
-Some documentation cleanup
-Change the estimate_est method to be inherited from a base Winding class and to use materials
-Update version in setup.py file

## [v0.1.3]

### Fixed

### Added

- Code of conduct
- Add a "Conductor" class for calculating conductivity as a function of temperature.
- Add a "Transformer" class for multi-layer spiral based transformer designs
- Add support for .step file generation of cores for 3D rendering

## [v0.1.2]

### Fixed

- Fix error in spiral DC resistance calculation that was omitting the last turn ([issue-10](https://github.com/dzimmanck/python-planar-magnetics/issues/10))
- Fix bug in the code which tries to equalize the area of outer post legs with the centerpost

### Added

## [v0.1.1]

- Fix classifiers for PyPi release

## [v0.1.0]

- Initial release
