import pytest
import numpy as np
from coreview3d.geometry.cross_section import (
    calculate_line_from_holes,
    calculate_cross_section,
    _calculate_hole_trace,
    _get_hole_intervals
)

def test_calculate_line_from_holes_basic(sample_collar_df):
    hole_ids = ['DH001', 'DH002']
    
    pt_A, pt_B = calculate_line_from_holes(sample_collar_df, hole_ids)
    
    assert isinstance(pt_A, np.ndarray)
    assert isinstance(pt_B, np.ndarray)
    assert len(pt_A) == 2
    assert len(pt_B) == 2
    
    length = np.linalg.norm(pt_B - pt_A)
    assert length > 0


def test_calculate_line_from_holes_multiple(sample_collar_df):
    hole_ids = ['DH001', 'DH002', 'DH003']
    
    pt_A, pt_B = calculate_line_from_holes(sample_collar_df, hole_ids)
    
    length = np.linalg.norm(pt_B - pt_A)
    assert length > 100  # Au moins 100m


def test_calculate_line_from_holes_insufficient(sample_collar_df):
    hole_ids = ['DH001']
    
    with pytest.raises(ValueError, match="Need at least 2 holes"):
        calculate_line_from_holes(sample_collar_df, hole_ids)


def test_calculate_line_from_holes_invalid_ids(sample_collar_df):
    hole_ids = ['INVALID1', 'INVALID2']
    
    with pytest.raises(ValueError):
        calculate_line_from_holes(sample_collar_df, hole_ids)


def test_calculate_cross_section_basic(sample_collar_df, sample_survey_df, sample_assays_df):
    hole_ids = ['DH001', 'DH002']
    point_A = np.array([500050, 6000050])
    point_B = np.array([500350, 6000350])
    
    result = calculate_cross_section(
        collar_df=sample_collar_df,
        survey_df=sample_survey_df,
        assays_df=sample_assays_df,
        hole_ids=hole_ids,
        point_A=point_A,
        point_B=point_B,
        tolerance=100.0
    )
    
    assert 'section_line' in result
    assert 'drillholes' in result
    assert 'bounds' in result
    
    assert len(result['drillholes']) > 0
    assert result['section_line']['length'] > 0


def test_calculate_cross_section_with_tolerance(sample_collar_df, sample_survey_df, sample_assays_df):
    point_A = np.array([500050, 6000050])
    point_B = np.array([500350, 6000350])
    
    result_large = calculate_cross_section(
        collar_df=sample_collar_df,
        survey_df=sample_survey_df,
        assays_df=sample_assays_df,
        hole_ids=None,
        point_A=point_A,
        point_B=point_B,
        tolerance=500.0
    )
    
    result_small = calculate_cross_section(
        collar_df=sample_collar_df,
        survey_df=sample_survey_df,
        assays_df=sample_assays_df,
        hole_ids=None,
        point_A=point_A,
        point_B=point_B,
        tolerance=10.0
    )
    
    assert len(result_large['drillholes']) >= len(result_small['drillholes'])


def test_calculate_cross_section_no_tolerance_match(sample_collar_df):
    point_A = np.array([600000, 7000000])  # Très loin
    point_B = np.array([600100, 7000100])
    
    with pytest.raises(ValueError, match="No drillholes found"):
        calculate_cross_section(
            collar_df=sample_collar_df,
            survey_df=None,
            assays_df=None,
            hole_ids=None,
            point_A=point_A,
            point_B=point_B,
            tolerance=10.0
        )


def test_calculate_cross_section_line_too_short(sample_collar_df):
    point_A = np.array([500000, 6000000])
    point_B = np.array([500000.5, 6000000.5])  # < 1m
    
    with pytest.raises(ValueError, match="Section line too short"):
        calculate_cross_section(
            collar_df=sample_collar_df,
            survey_df=None,
            assays_df=None,
            hole_ids=['DH001'],
            point_A=point_A,
            point_B=point_B,
            tolerance=100.0
        )


def test_calculate_cross_section_without_survey(sample_collar_df, sample_assays_df):
    point_A = np.array([500050, 6000050])
    point_B = np.array([500350, 6000350])
    
    result = calculate_cross_section(
        collar_df=sample_collar_df,
        survey_df=None,
        assays_df=sample_assays_df,
        hole_ids=['DH001', 'DH002'],
        point_A=point_A,
        point_B=point_B,
        tolerance=100.0
    )
    
    assert len(result['drillholes']) > 0
    
    for hole in result['drillholes']:
        if len(hole['trace']) >= 2:
            x_values = [p['x_along_section'] for p in hole['trace']]
            assert max(x_values) - min(x_values) < 1.0  # Variation < 1m


def test_calculate_hole_trace_vertical(sample_collar_df):
    collar = sample_collar_df.iloc[0]
    point_A = np.array([500000, 6000000])
    direction_norm = np.array([1.0, 0.0])
    
    trace = _calculate_hole_trace(
        hole_id=collar['HOLEID'],
        collar=collar,
        survey_df=None,
        point_A=point_A,
        direction_norm=direction_norm
    )
    
    assert len(trace) == 2  # Collar + toe
    assert trace[0]['depth_along_hole'] == 0.0
    assert trace[1]['depth_along_hole'] == collar['MAX_DEPTH']


def test_get_hole_intervals(sample_assays_df):
    intervals = _get_hole_intervals('DH001', sample_assays_df)
    
    assert intervals is not None
    assert len(intervals) == 3
    assert intervals[0]['lithology'] == 'GRANITE'
    assert 'au_ppm' in intervals[0]
    assert 'cu_pct' in intervals[0]


def test_get_hole_intervals_no_data(sample_assays_df):
    intervals = _get_hole_intervals('INVALID_HOLE', sample_assays_df)
    
    assert intervals is None

