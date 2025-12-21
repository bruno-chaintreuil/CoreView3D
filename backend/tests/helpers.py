import pandas as pd
import numpy as np
from io import BytesIO
from typing import Tuple


def create_test_collar_csv(variation: str = 'standard') -> BytesIO:
    base_data = {
        'holes': ['DH001', 'DH002', 'DH003', 'DH004', 'DH005'],
        'east': [500100, 500200, 500300, 500150, 500250],
        'north': [6000100, 6000200, 6000300, 6000400, 6000250],
        'elev': [1250.0, 1245.0, 1240.0, 1255.0, 1248.0],
        'depth': [150.0, 200.0, 180.0, 120.0, 175.0]
    }
    
    # Définir les noms de colonnes selon la variation
    if variation == 'standard':
        columns = {
            'holes': 'Hole_ID',
            'east': 'East',
            'north': 'North',
            'elev': 'Elevation',
            'depth': 'Max_Depth'
        }
    elif variation == 'uppercase':
        columns = {
            'holes': 'HOLEID',
            'east': 'EAST',
            'north': 'NORTH',
            'elev': 'ELEV',
            'depth': 'MAX_DEPTH'
        }
    elif variation == 'lowercase':
        columns = {
            'holes': 'holeid',
            'east': 'east',
            'north': 'north',
            'elev': 'elevation',
            'depth': 'max_depth'
        }
    elif variation == 'mixed':
        columns = {
            'holes': 'Hole_ID',
            'east': 'easting',
            'north': 'Northing',
            'elev': 'ELEVATION',
            'depth': 'max_depth'
        }
    elif variation == 'alternative':
        columns = {
            'holes': 'DHID',
            'east': 'X',
            'north': 'Y',
            'elev': 'RL',
            'depth': 'Depth'
        }
    else:
        raise ValueError(f"Unknown variation: {variation}")
    
    data = {
        columns['holes']: base_data['holes'],
        columns['east']: base_data['east'],
        columns['north']: base_data['north'],
        columns['elev']: base_data['elev'],
        columns['depth']: base_data['depth']
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def create_test_survey_csv(variation: str = 'standard') -> BytesIO:
    holes = ['DH001', 'DH002', 'DH003', 'DH004', 'DH005']
    data_list = []
    
    for hole_id in holes:
        for depth in [0, 25, 50, 75, 100, 125, 150]:
            azimuth = 45 + np.random.uniform(-5, 5)
            dip = -60 + np.random.uniform(-10, 10)
            data_list.append({
                'holes': hole_id,
                'depth': depth,
                'azimuth': azimuth,
                'dip': dip
            })
    
    if variation == 'standard':
        columns = {'holes': 'Hole_ID', 'depth': 'Depth', 'azimuth': 'Azimuth', 'dip': 'Dip'}
    elif variation == 'uppercase':
        columns = {'holes': 'HOLEID', 'depth': 'DEPTH', 'azimuth': 'AZIMUTH', 'dip': 'DIP'}
    elif variation == 'lowercase':
        columns = {'holes': 'holeid', 'depth': 'depth', 'azimuth': 'azimuth', 'dip': 'dip'}
    elif variation == 'mixed':
        columns = {'holes': 'Hole_ID', 'depth': 'DEPTH', 'azimuth': 'az', 'dip': 'Inclination'}
    elif variation == 'alternative':
        columns = {'holes': 'DHID', 'depth': 'At', 'azimuth': 'Bearing', 'dip': 'Incl'}
    else:
        raise ValueError(f"Unknown variation: {variation}")
    
    df = pd.DataFrame(data_list)
    df = df.rename(columns={
        'holes': columns['holes'],
        'depth': columns['depth'],
        'azimuth': columns['azimuth'],
        'dip': columns['dip']
    })
    
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def create_test_assays_csv(variation: str = 'standard') -> BytesIO:
    data_list = []
    lithologies = ['GRANITE', 'DIORITE', 'ORE', 'ALTERED', 'SCHIST']
    
    for hole_id in ['DH001', 'DH002', 'DH003', 'DH004', 'DH005']:
        depth = 0
        max_depth = 150
        
        while depth < max_depth:
            interval_length = np.random.uniform(10, 30)
            to_depth = min(depth + interval_length, max_depth)
            
            lithology = np.random.choice(lithologies)
            au_ppm = np.random.lognormal(0, 1) if lithology in ['ORE', 'ALTERED'] else np.random.uniform(0.01, 0.5)
            cu_pct = np.random.lognormal(-2, 0.5) if lithology in ['ORE', 'ALTERED'] else np.random.uniform(0.01, 0.1)
            
            data_list.append({
                'holes': hole_id,
                'from': depth,
                'to': to_depth,
                'lithology': lithology,
                'au': round(au_ppm, 3),
                'cu': round(cu_pct, 3)
            })
            
            depth = to_depth
    
    if variation == 'standard':
        columns = {'holes': 'Hole_ID', 'from': 'From', 'to': 'To', 'lithology': 'Lithology', 'au': 'Au_ppm', 'cu': 'Cu_pct'}
    elif variation == 'uppercase':
        columns = {'holes': 'HOLEID', 'from': 'FROM', 'to': 'TO', 'lithology': 'LITHOLOGY', 'au': 'AU_PPM', 'cu': 'CU_PCT'}
    elif variation == 'lowercase':
        columns = {'holes': 'holeid', 'from': 'from', 'to': 'to', 'lithology': 'lithology', 'au': 'au_ppm', 'cu': 'cu_pct'}
    elif variation == 'mixed':
        columns = {'holes': 'Hole_ID', 'from': 'from_depth', 'to': 'to_depth', 'lithology': 'LITH', 'au': 'Au', 'cu': 'Copper'}
    elif variation == 'alternative':
        columns = {'holes': 'DHID', 'from': 'Start', 'to': 'End', 'lithology': 'Rock', 'au': 'Gold', 'cu': 'Cu'}
    else:
        raise ValueError(f"Unknown variation: {variation}")
    
    df = pd.DataFrame(data_list)
    df = df.rename(columns={
        'holes': columns['holes'],
        'from': columns['from'],
        'to': columns['to'],
        'lithology': columns['lithology'],
        'au': columns['au'],
        'cu': columns['cu']
    })
    
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def create_test_excel_file(variation: str = 'standard') -> BytesIO:
    collar_csv = create_test_collar_csv(variation)
    collar_df = pd.read_csv(collar_csv)
    
    survey_csv = create_test_survey_csv(variation)
    survey_df = pd.read_csv(survey_csv)
    
    assays_csv = create_test_assays_csv(variation)
    assays_df = pd.read_csv(assays_csv)
    
    holeid_col = collar_df.columns[0]
    first_3_holes = collar_df[holeid_col].head(3).tolist()
    
    collar_df = collar_df.head(3)
    survey_df = survey_df[survey_df.iloc[:, 0].isin(first_3_holes)]
    assays_df = assays_df[assays_df.iloc[:, 0].isin(first_3_holes)]
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        collar_df.to_excel(writer, sheet_name='Collar', index=False)
        survey_df.to_excel(writer, sheet_name='Survey', index=False)
        assays_df.to_excel(writer, sheet_name='Assays', index=False)
    
    buffer.seek(0)
    return buffer


def assert_session_data_valid(session_data):
    assert session_data is not None
    assert session_data.collar_df is not None
    assert len(session_data.collar_df) > 0
    
    required_columns = ['HOLEID', 'EAST', 'NORTH', 'ELEV']
    for col in required_columns:
        assert col in session_data.collar_df.columns, f"Column {col} missing from collar_df"
    
    if session_data.survey_df is not None:
        assert 'HOLEID' in session_data.survey_df.columns
        assert 'DEPTH' in session_data.survey_df.columns
    
    if session_data.assays_df is not None:
        assert 'HOLEID' in session_data.assays_df.columns
        assert 'FROM' in session_data.assays_df.columns
        assert 'TO' in session_data.assays_df.columns


def assert_cross_section_valid(section_data: dict):
    assert 'section_line' in section_data, "Missing 'section_line' in response"
    assert 'drillholes' in section_data, "Missing 'drillholes' in response"
    assert 'bounds' in section_data, "Missing 'bounds' in response"
    
    line = section_data['section_line']
    assert 'point_A' in line
    assert 'point_B' in line
    assert 'length' in line
    assert line['length'] > 0, "Section line length must be > 0"
    
    assert len(section_data['drillholes']) > 0, "No drillholes in section"
    
    for hole in section_data['drillholes']:
        assert 'hole_id' in hole
        assert 'trace' in hole
        assert len(hole['trace']) >= 2, f"Hole {hole['hole_id']} has less than 2 trace points"
        
        for point in hole['trace']:
            assert 'x_along_section' in point
            assert 'y_elevation' in point
    
    bounds = section_data['bounds']
    assert 'min_distance' in bounds
    assert 'max_distance' in bounds
    assert 'min_elevation' in bounds
    assert 'max_elevation' in bounds
    assert bounds['max_distance'] > bounds['min_distance'], "Invalid distance bounds"
    assert bounds['max_elevation'] > bounds['min_elevation'], "Invalid elevation bounds"


def create_minimal_collar_csv(variation: str = 'standard') -> BytesIO:
    return create_test_collar_csv(variation)