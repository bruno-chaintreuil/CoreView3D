import pytest
import numpy as np
from src.coreview3d.geometry.cross_section import (
    project_drillhole_to_section,
    calculate_simple_cross_section
)


@pytest.fixture
def sample_trajectories():
    return [
        {
            'hole_id': 'DH001',
            'collar': {'east': 500000, 'north': 6000000, 'elev': 100},
            'points': [
                {'x': 500000, 'y': 6000000, 'z': 100},
                {'x': 500000, 'y': 6000000, 'z': 0}
            ]
        },
        {
            'hole_id': 'DH002',
            'collar': {'east': 500100, 'north': 6000000, 'elev': 100},
            'points': [
                {'x': 500100, 'y': 6000000, 'z': 100},
                {'x': 500100, 'y': 6000000, 'z': -50}
            ]
        },
        {
            'hole_id': 'DH003',
            'collar': {'east': 500200, 'north': 6001000, 'elev': 100}, # Éloigné en Nord
            'points': [
                {'x': 500200, 'y': 6001000, 'z': 100},
                {'x': 500200, 'y': 6001000, 'z': 0}
            ]
        }
    ]

def test_project_drillhole_to_section_basic():
    xy_start = np.array([500000, 6000000])
    xy_stop = np.array([500200, 6000000]) # Section Est-Ouest pure
    
    trajectory_points = [
        {'x': 500100, 'y': 6000000, 'z': 50}, # Pile sur la ligne à mi-chemin
    ]
    
    projected = project_drillhole_to_section(trajectory_points, xy_start, xy_stop)
    
    assert len(projected) == 1
    assert projected[0]['x'] == 100.0  # Distance depuis le départ
    assert projected[0]['z'] == 50.0   # Élévation conservée

def test_calculate_simple_cross_section_filtering(sample_trajectories):
    xy_start = (500000, 6000000)
    xy_stop = (500500, 6000000)
    hole_ids = ['DH001', 'DH002', 'DH003']
    
    result = calculate_simple_cross_section(
        sample_trajectories, hole_ids, xy_start, xy_stop, tolerance=50.0
    )
    
    found_ids = [h['hole_id'] for h in result['drillholes']]
    assert 'DH001' in found_ids
    assert 'DH002' in found_ids
    assert 'DH003' not in found_ids
    assert len(result['drillholes']) == 2

def test_calculate_simple_cross_section_large_tolerance(sample_trajectories):
    xy_start = (500000, 6000000)
    xy_stop = (500500, 6000000)
    hole_ids = ['DH001', 'DH002', 'DH003']
    
    result = calculate_simple_cross_section(
        sample_trajectories, hole_ids, xy_start, xy_stop, tolerance=1500.0
    )
    
    assert len(result['drillholes']) == 3

def test_calculate_simple_cross_section_id_selection(sample_trajectories):
    xy_start = (500000, 6000000)
    xy_stop = (500500, 6000000)
    
    result = calculate_simple_cross_section(
        sample_trajectories, ['DH001'], xy_start, xy_stop, tolerance=100.0
    )
    
    assert len(result['drillholes']) == 1
    assert result['drillholes'][0]['hole_id'] == 'DH001'


def test_cross_section_request_validation():
    from src.coreview3d.models.cross_section import CrossSectionRequest
    
    data = {
        "session_id": "test-session",
        "xy_start": (0.0, 0.0),
        "xy_stop": (100.0, 100.0),
        "hole_ids": ["DH01"],
        "tolerance": 50.0
    }
    
    req = CrossSectionRequest(**data)
    assert req.session_id == "test-session"
    assert req.xy_start == (0.0, 0.0)

def test_cross_section_response_structure():
    from src.coreview3d.models.cross_section import CrossSectionResponse
    
    sample_response = {
        "success": True,
        "xy_start": (0.0, 0.0),
        "xy_stop": (100.0, 0.0),
        "drillholes": [
            {
                "hole_id": "DH01",
                "trace": [{"x": 10.0, "z": 100.0}, {"x": 10.0, "z": 0.0}]
            }
        ]
    }
    
    resp = CrossSectionResponse(**sample_response)
    assert len(resp.drillholes) == 1
    assert resp.drillholes[0].trace[0].x == 10.0