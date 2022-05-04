# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Fixed

### Added
-Change convention to assume dimensions are specified in mm rather than m
-Add support for coreloss calculations
-Add support for more complex CAD part generation for cores
-Minor code cleanups and API changes
-Some documentation cleanup
-Change the estimate_est method to be inherited from a base Winding class and to use materials

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
