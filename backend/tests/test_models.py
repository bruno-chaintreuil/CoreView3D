import pytest
from pydantic import ValidationError
from coreview3d.models.cross_section import (
    CrossSectionRequest,
)


def test_cross_section_request_valid():
    request = CrossSectionRequest(
        session_id="test-123",
        hole_ids=["DH001", "DH002"],
        xy_start=[500000, 6000000],
        xy_stop=[500500, 6000500],
        tolerance=100.0
    )
    
    assert request.session_id == "test-123"
    assert len(request.hole_ids) == 2


def test_cross_section_request_tolerance_validation():
    with pytest.raises(ValidationError):
        CrossSectionRequest(
            session_id="test-123",
            hole_ids=["DH001"],
            x_start=0, y_start=0, x_stop=100, y_stop=100,
            tolerance=0.5  # Too small
        )
    
    with pytest.raises(ValidationError):
        CrossSectionRequest(
            session_id="test-123",
            hole_ids=["DH001"],
            x_start=0, y_start=0, x_stop=100, y_stop=100,
            tolerance=2000  # Too big
        )