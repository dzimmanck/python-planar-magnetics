import os


# Default path to FreeCAD binaries
DEFAULT_FREECAD_PATH = "C:/Program Files/FreeCAD 0.19/bin"


# Function to get FreeCAD path with environment variable override
def get_freecad_path():
    """
    Get the FreeCAD path from environment variable FREECAD_PATH if available,
    otherwise use the default path.
    """
    return os.getenv("FREECAD_PATH", DEFAULT_FREECAD_PATH)
