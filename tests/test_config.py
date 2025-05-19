import os
from planar_magnetics.config import get_freecad_path, DEFAULT_FREECAD_PATH


def test_get_freecad_path_default():
    """Test that get_freecad_path returns the default path when no env var is set."""
    # Temporarily clear the environment variable if it exists
    original_value = os.environ.pop("FREECAD_PATH", None)
    try:
        # Test that the default path is returned
        assert get_freecad_path() == DEFAULT_FREECAD_PATH
    finally:
        # Restore the environment variable if it existed
        if original_value is not None:
            os.environ["FREECAD_PATH"] = original_value


def test_get_freecad_path_from_env(monkeypatch):
    """Test that get_freecad_path returns the value from environment variable when set."""
    # Test path value
    test_path = "/custom/path/to/freecad"

    # Set the environment variable to our test value
    monkeypatch.setenv("FREECAD_PATH", test_path)

    # Test that the function returns our custom path
    assert get_freecad_path() == test_path


def test_default_freecad_path_format():
    """Test that the default path follows expected format."""
    # Ensure the path is a string
    assert isinstance(DEFAULT_FREECAD_PATH, str)

    # Check that it contains expected FreeCAD path elements
    assert "FreeCAD" in DEFAULT_FREECAD_PATH
    assert "bin" in DEFAULT_FREECAD_PATH
