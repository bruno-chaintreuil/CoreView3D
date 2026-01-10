import pytest
from pydantic import ValidationError
from coreview3d.models.cross_section import (
    CrossSectionRequest,
    SectionLineRequest,
    TracePoint,
    Interval,
    Drillhole
)


def test_cross_section_request_valid():
    request = CrossSectionRequest(
        session_id="test-123",
        hole_ids=["DH001", "DH002"],
        point_A=[500000, 6000000],
        point_B=[500500, 6000500],
        tolerance=100.0
    )
    
    assert request.session_id == "test-123"
    assert len(request.hole_ids) == 2


def test_cross_section_request_defaults():
    request = CrossSectionRequest(
        session_id="test-123",
        hole_ids=[]
    )
    
    assert request.tolerance == 100.0
    assert request.point_A is None
    assert request.point_B is None


def test_cross_section_request_tolerance_validation():
    with pytest.raises(ValidationError):
        CrossSectionRequest(
            session_id="test-123",
            hole_ids=["DH001"],
            tolerance=0.5  # Too small
        )
    
    with pytest.raises(ValidationError):
        CrossSectionRequest(
            session_id="test-123",
            hole_ids=["DH001"],
            tolerance=2000  # Too big
        )


def test_trace_point_creation():
    point = TracePoint(
        depth_along_hole=50.0,
        x_along_section=125.5,
        y_elevation=1200.0
    )
    
    assert point.depth_along_hole == 50.0


def test_interval_creation():
    interval = Interval(
        **{
            "from": 10.0,
            "to": 25.0,
            "lithology": "GRANITE",
            "au_ppm": 0.5
        }
    )
    
    assert interval.from_depth == 10.0
    assert interval.to_depth == 25.0
    assert interval.lithology == "GRANITE"


def test_drillhole_creation():
    drillhole = Drillhole(
        hole_id="DH001",
        distance_from_line=15.5,
        distance_along_line=125.0,
        collar_elevation=1250.0,
        trace=[
            TracePoint(depth_along_hole=0, x_along_section=125, y_elevation=1250),
            TracePoint(depth_along_hole=50, x_along_section=130, y_elevation=1200)
        ],
        intervals=[
            Interval(**{"from": 0, "to": 50, "lithology": "GRANITE"})
        ]
    )
    
    assert drillhole.hole_id == "DH001"
    assert len(drillhole.trace) == 2
    assert len(drillhole.intervals) == 1