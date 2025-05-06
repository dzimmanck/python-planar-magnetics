import math
import pytest
import sys
from planar_magnetics.geometry import Point, Polygon, get_distance
from planar_magnetics.config import get_freecad_path


# Skip test if FreeCAD is not available
def is_freecad_available():
    try:
        freecad_path = get_freecad_path()
        sys.path.append(freecad_path)
        import FreeCAD  # noqa: F401
        return True
    except (ImportError, ModuleNotFoundError):
        return False


def test_get_distance():
    p0 = Point(1, 1)
    p1 = Point(0, 0)
    p2 = Point(2, 0)
    distance = get_distance(p0, p1, p2)
    assert math.isclose(distance, 1)


@pytest.mark.skipif(not is_freecad_available(), reason="FreeCAD not available")
def test_polygon_to_wire():
    """Test the Polygon.to_wire method that converts to a FreeCAD wire."""
    # Create a simple square polygon
    p0 = Point(0, 0)
    p1 = Point(10, 0)
    p2 = Point(10, 10)
    p3 = Point(0, 10)
    polygon = Polygon([p0, p1, p2, p3])

    # Get the Wire
    wire = polygon.to_wire()

    # Import FreeCAD again (for assertions)
    freecad_path = get_freecad_path()
    sys.path.append(freecad_path)
    import FreeCAD  # noqa: F401
    import Part

    # Verify it's a valid Wire object
    assert isinstance(wire, Part.Wire)

    # Verify the number of edges (should be 4 for a closed square)
    assert len(wire.Edges) == 4

    # Verify it's closed
    assert wire.isClosed()

    # Verify its length (perimeter should be 40 units)
    assert math.isclose(wire.Length, 40.0, rel_tol=1e-9)

    # Test with closed=False
    open_wire = polygon.to_wire(closed=False)
    assert len(open_wire.Edges) == 3  # Should have 3 edges if not closed
    assert not open_wire.isClosed()

    # Test with z-height
    z_wire = polygon.to_wire(z=5)
    for vertex in z_wire.Vertexes:
        assert math.isclose(vertex.Z, 5.0, rel_tol=1e-9)


if __name__ == "__main__":
    test_get_distance()
