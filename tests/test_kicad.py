from planar_magnetics.kicad import PadType, Pad, Via, Reference, Value, Footprint
from planar_magnetics.geometry import Point
import uuid
import pytest
import re

def test_padtype_str_representation():
    assert str(PadType.TH) == "thru_hole"
    assert str(PadType.SMD) == "smd"


def test_pad_initialization():
    # Test with minimal required parameters
    pad = Pad(PadType.TH, 1, Point(10, 20), 1.5)
    assert pad.pad_type == PadType.TH
    assert pad.number == 1
    assert pad.at == Point(10, 20)
    assert pad.size == 1.5
    assert pad.layers == ("*.Cu",)
    assert pad.drill is None
    assert isinstance(pad.tstamp, uuid.UUID)
    
    # Test with all parameters specified
    test_uuid = uuid.uuid4()
    pad = Pad(
        PadType.SMD, 
        2, 
        Point(15, 25), 
        2.0, 
        ("F.Cu", "B.Cu"), 
        0.8,
        test_uuid
    )
    assert pad.pad_type == PadType.SMD
    assert pad.number == 2
    assert pad.at == Point(15, 25)
    assert pad.size == 2.0
    assert pad.layers == ("F.Cu", "B.Cu")
    assert pad.drill == 0.8
    assert pad.tstamp == test_uuid


def test_pad_str_representation():
    # Fix the UUID for consistent string comparison
    test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
    
    # Test through-hole pad with drill
    pad_th = Pad(PadType.TH, 1, Point(10, 20), 1.5, drill=0.8, tstamp=test_uuid)
    pad_th_str = str(pad_th)
    assert '(pad "1" thru_hole circle (at 10 20)' in pad_th_str
    assert '(size 1.5 1.5)' in pad_th_str
    assert '(drill 0.8)' in pad_th_str
    assert '(layers *.Cu)' in pad_th_str
    assert '(tstamp 12345678-1234-5678-1234-567812345678)' in pad_th_str
    
    # Test SMD pad without drill
    pad_smd = Pad(PadType.SMD, 2, Point(15, 25), 2.0, ("F.Cu",), tstamp=test_uuid)
    pad_smd_str = str(pad_smd)
    assert '(pad "2" smd rect (at 15 25)' in pad_smd_str
    assert '(size 2.0 2.0)' in pad_smd_str
    assert '(drill' not in pad_smd_str
    assert '(layers F.Cu)' in pad_smd_str


def test_via_initialization():
    # Test default initialization
    via = Via()
    assert via.at == Point(0, 0)
    assert via.size == 0.8
    assert via.drill == 0.4
    assert via.layers == ("F.Cu",)
    assert via.remove_unused_layers is True
    assert isinstance(via.tstamp, uuid.UUID)
    
    # Test with custom parameters
    test_uuid = uuid.uuid4()
    via = Via(
        Point(10, 20),
        1.0,
        0.5,
        ("F.Cu", "B.Cu"),
        False,
        test_uuid
    )
    assert via.at == Point(10, 20)
    assert via.size == 1.0
    assert via.drill == 0.5
    assert via.layers == ("F.Cu", "B.Cu")
    assert via.remove_unused_layers is False
    assert via.tstamp == test_uuid


def test_via_to_pad_conversion():
    via = Via(Point(10, 20), 1.0, 0.5, ("F.Cu", "B.Cu"))
    pad = via.to_pad(3)
    
    assert pad.pad_type == PadType.TH
    assert pad.number == 3
    assert pad.at == Point(10, 20)
    assert pad.size == 1.0
    assert pad.layers == ("*.Cu",)
    assert pad.drill == 0.5


def test_via_str_representation():
    test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
    
    # Test with remove_unused_layers=True
    via = Via(Point(10, 20), 1.0, 0.5, ("F.Cu",), True, test_uuid)
    via_str = str(via)
    assert '(via (at 10 20)' in via_str
    assert '(size 1.0)' in via_str
    assert '(drill 0.5)' in via_str
    assert '(layers F.Cu)' in via_str
    assert '(remove_unused_layers)' in via_str
    assert '(tstamp 12345678-1234-5678-1234-567812345678)' in via_str
    
    # Test with remove_unused_layers=False
    via = Via(Point(10, 20), 1.0, 0.5, ("F.Cu",), False, test_uuid)
    via_str = str(via)
    assert '(remove_unused_layers)' not in via_str


def test_reference_initialization_and_str():
    test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
    ref = Reference(Point(10, 20), 1.5e-3, 0.2e-3, "center", test_uuid)
    
    assert ref.at == Point(10, 20)
    assert ref.font_size == 1.5e-3
    assert ref.thickness == 0.2e-3
    assert ref.justification == "center"
    assert ref.tstamp == test_uuid
    
    ref_str = str(ref)
    assert '(fp_text reference "Ref**" (at 10 20)' in ref_str
    assert '(font (size 0.0015 0.0015) (thickness 0.0002))' in ref_str
    assert '(justify center)' in ref_str
    assert '(tstamp 12345678-1234-5678-1234-567812345678)' in ref_str


def test_value_initialization_and_str():
    test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
    val = Value(Point(10, 20), 1.5e-3, 0.2e-3, "center", test_uuid)
    
    assert val.at == Point(10, 20)
    assert val.font_size == 1.5e-3
    assert val.thickness == 0.2e-3
    assert val.justification == "center"
    assert val.tstamp == test_uuid
    
    val_str = str(val)
    assert '(fp_text value "Val**" (at 10 20)' in val_str
    assert '(font (size 0.0015 0.0015) (thickness 0.0002))' in val_str
    assert '(justify center)' in val_str
    assert '(tstamp 12345678-1234-5678-1234-567812345678)' in val_str


def test_footprint_initialization():
    # Test with default parameters
    fp = Footprint("Test_Footprint")
    assert fp.name == "Test_Footprint"
    assert fp.version == "20211014"
    assert fp.contents == []
    
    # Test with custom parameters
    fp = Footprint("Custom_Footprint", "20220101", [1, 2, 3])
    assert fp.name == "Custom_Footprint"
    assert fp.version == "20220101"
    assert fp.contents == [1, 2, 3]


def test_footprint_str_representation():
    # Create a footprint with various components
    ref = Reference(Point(0, 5))
    val = Value(Point(0, -5))
    pad1 = Pad(PadType.TH, 1, Point(-10, 0), 1.5, drill=0.8)
    pad2 = Pad(PadType.SMD, 2, Point(10, 0), 2.0)
    via = Via(Point(5, 5))
    
    fp = Footprint("Test_Footprint", contents=[ref, val, pad1, pad2, via])
    fp_str = str(fp)
    
    # Check the header and components
    assert '(footprint "Test_Footprint" (version 20211014) (generator python_planar_magnetics)' in fp_str
    assert 'fp_text reference "Ref**"' in fp_str
    assert 'fp_text value "Val**"' in fp_str
    assert 'pad "1" thru_hole circle' in fp_str
    assert 'pad "2" smd rect' in fp_str
    assert 'via (at 5 5)' in fp_str
    
    # Make sure the string is properly formatted with parentheses
    assert fp_str.count('(') == fp_str.count(')')
    assert fp_str.startswith('(')
    assert fp_str.endswith(')')
