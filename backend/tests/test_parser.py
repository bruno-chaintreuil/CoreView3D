import pytest
import pandas as pd
from io import BytesIO
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from coreview3d.parsers.csv_parser import DrillholeParser

def create_collar_csv(column_names: dict) -> BytesIO:
    data = {
        column_names.get('holeid', 'HOLEID'): ['DH001', 'DH002', 'DH003'],
        column_names.get('east', 'EAST'): [500100, 500200, 500300],
        column_names.get('north', 'NORTH'): [6000100, 6000200, 6000300],
        column_names.get('elev', 'ELEV'): [1250.0, 1245.0, 1240.0],
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def create_survey_csv(column_names: dict) -> BytesIO:
    data = {
        column_names.get('holeid', 'HOLEID'): ['DH001', 'DH001', 'DH002'],
        column_names.get('depth', 'DEPTH'): [0.0, 50.0, 0.0],
        column_names.get('azimuth', 'AZIMUTH'): [45.0, 48.0, 45.0],
        column_names.get('dip', 'DIP'): [-60.0, -62.0, -60.0],
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def create_assays_csv(column_names: dict) -> BytesIO:
    data = {
        column_names.get('holeid', 'HOLEID'): ['DH001', 'DH001', 'DH002'],
        column_names.get('from', 'FROM'): [0.0, 25.0, 0.0],
        column_names.get('to', 'TO'): [25.0, 50.0, 25.0],
        column_names.get('lithology', 'LITHOLOGY'): ['GRANITE', 'ORE', 'GRANITE'],
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer



@pytest.mark.parametrize("holeid_variation", [
    'HOLEID', 'holeid', 'Hole_ID', 'hole_id', 'Hole ID', 'DHID', 'dhid', 'ID', 'id'
])
def test_collar_holeid_variations(holeid_variation):
    parser = DrillholeParser()
    
    csv = create_collar_csv({
        'holeid': holeid_variation,
        'east': 'EAST',
        'north': 'NORTH',
        'elev': 'ELEV'
    })
    
    df = parser.parse_collar(csv)
    
    assert 'HOLEID' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("east_variation", [
    'EAST', 'east', 'East', 'X', 'x', 'Easting', 'easting', 'XCOORD', 'x_coord'
])
def test_collar_east_variations(east_variation):
    parser = DrillholeParser()
    
    csv = create_collar_csv({
        'holeid': 'HOLEID',
        'east': east_variation,
        'north': 'NORTH',
        'elev': 'ELEV'
    })
    
    df = parser.parse_collar(csv)
    
    assert 'EAST' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("north_variation", [
    'NORTH', 'north', 'North', 'Y', 'y', 'Northing', 'northing', 'YCOORD', 'y_coord'
])
def test_collar_north_variations(north_variation):
    parser = DrillholeParser()
    
    csv = create_collar_csv({
        'holeid': 'HOLEID',
        'east': 'EAST',
        'north': north_variation,
        'elev': 'ELEV'
    })
    
    df = parser.parse_collar(csv)
    
    assert 'NORTH' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("elev_variation", [
    'ELEV', 'elev', 'Elevation', 'elevation', 'Z', 'z', 'RL', 'rl', 'ALT', 'alt'
])
def test_collar_elevation_variations(elev_variation):
    parser = DrillholeParser()
    
    csv = create_collar_csv({
        'holeid': 'HOLEID',
        'east': 'EAST',
        'north': 'NORTH',
        'elev': elev_variation
    })
    
    df = parser.parse_collar(csv)
    
    assert 'ELEV' in df.columns
    assert len(df) == 3


def test_collar_mixed_case():
    parser = DrillholeParser()
    
    csv = create_collar_csv({
        'holeid': 'Hole_ID',
        'east': 'easting',
        'north': 'Northing',
        'elev': 'ELEVATION'
    })
    
    df = parser.parse_collar(csv)
    
    assert 'HOLEID' in df.columns
    assert 'EAST' in df.columns
    assert 'NORTH' in df.columns
    assert 'ELEV' in df.columns
    assert len(df) == 3


def test_collar_all_lowercase():
    parser = DrillholeParser()
    
    csv = create_collar_csv({
        'holeid': 'holeid',
        'east': 'east',
        'north': 'north',
        'elev': 'elevation'
    })
    
    df = parser.parse_collar(csv)
    
    assert all(col in df.columns for col in ['HOLEID', 'EAST', 'NORTH', 'ELEV'])
    assert len(df) == 3


def test_collar_all_uppercase():
    parser = DrillholeParser()
    
    csv = create_collar_csv({
        'holeid': 'HOLEID',
        'east': 'EAST',
        'north': 'NORTH',
        'elev': 'ELEV'
    })
    
    df = parser.parse_collar(csv)
    
    assert all(col in df.columns for col in ['HOLEID', 'EAST', 'NORTH', 'ELEV'])
    assert len(df) == 3


@pytest.mark.parametrize("depth_variation", [
    'DEPTH', 'depth', 'Depth', 'AT', 'at', 'Survey_Depth', 'survey_depth'
])
def test_survey_depth_variations(depth_variation):
    parser = DrillholeParser()
    
    csv = create_survey_csv({
        'holeid': 'HOLEID',
        'depth': depth_variation,
        'azimuth': 'AZIMUTH',
        'dip': 'DIP'
    })
    
    df = parser.parse_survey(csv)
    
    assert 'DEPTH' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("azimuth_variation", [
    'AZIMUTH', 'azimuth', 'Azimuth', 'AZ', 'az', 'Bearing', 'bearing'
])
def test_survey_azimuth_variations(azimuth_variation):
    parser = DrillholeParser()
    
    csv = create_survey_csv({
        'holeid': 'HOLEID',
        'depth': 'DEPTH',
        'azimuth': azimuth_variation,
        'dip': 'DIP'
    })
    
    df = parser.parse_survey(csv)
    
    assert 'AZIMUTH' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("dip_variation", [
    'DIP', 'dip', 'Dip', 'INCLINATION', 'inclination', 'Incl', 'incl', 'Plunge'
])
def test_survey_dip_variations(dip_variation):
    parser = DrillholeParser()
    
    csv = create_survey_csv({
        'holeid': 'HOLEID',
        'depth': 'DEPTH',
        'azimuth': 'AZIMUTH',
        'dip': dip_variation
    })
    
    df = parser.parse_survey(csv)
    
    assert 'DIP' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("from_variation", [
    'FROM', 'from', 'From', 'From_Depth', 'from_depth', 'START', 'start'
])
def test_assays_from_variations(from_variation):
    parser = DrillholeParser()
    
    csv = create_assays_csv({
        'holeid': 'HOLEID',
        'from': from_variation,
        'to': 'TO',
        'lithology': 'LITHOLOGY'
    })
    
    df = parser.parse_assays(csv)
    
    assert 'FROM' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("to_variation", [
    'TO', 'to', 'To', 'To_Depth', 'to_depth', 'END', 'end'
])
def test_assays_to_variations(to_variation):
    parser = DrillholeParser()
    
    csv = create_assays_csv({
        'holeid': 'HOLEID',
        'from': 'FROM',
        'to': to_variation,
        'lithology': 'LITHOLOGY'
    })
    
    df = parser.parse_assays(csv)
    
    assert 'TO' in df.columns
    assert len(df) == 3


@pytest.mark.parametrize("lithology_variation", [
    'LITHOLOGY', 'lithology', 'Lithology', 'LITH', 'lith', 'Rock', 'rock', 'Rock_Type'
])
def test_assays_lithology_variations(lithology_variation):
    parser = DrillholeParser()
    
    csv = create_assays_csv({
        'holeid': 'HOLEID',
        'from': 'FROM',
        'to': 'TO',
        'lithology': lithology_variation
    })
    
    df = parser.parse_assays(csv)
    
    assert 'LITHOLOGY' in df.columns
    assert len(df) == 3



def test_collar_missing_required_column():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': [500100, 500200],
        # 'NORTH' manquant
        'ELEV': [1250.0, 1245.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    with pytest.raises(ValueError, match="missing required columns"):
        parser.parse_collar(buffer)


def test_get_supported_variations():
    parser = DrillholeParser()
    
    collar_variations = parser.get_supported_variations('collar')
    assert 'holeid' in collar_variations
    assert 'east' in collar_variations
    assert 'north' in collar_variations
    
    survey_variations = parser.get_supported_variations('survey')
    assert 'depth' in survey_variations
    assert 'azimuth' in survey_variations
    
    assays_variations = parser.get_supported_variations('assays')
    assert 'from' in assays_variations
    assert 'to' in assays_variations



def test_original_bug_case():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['DH001', 'DH002', 'DH003'],
        'EAST': [500100, 500200, 500300],
        'NORTH': [6000100, 6000200, 6000300],
        'ELEV': [1250.0, 1245.0, 1240.0],
        'MAX_DEPTH': [150.0, 200.0, 180.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result_df = parser.parse_collar(buffer)
    
    assert 'HOLEID' in result_df.columns
    assert 'EAST' in result_df.columns
    assert 'NORTH' in result_df.columns
    assert 'ELEV' in result_df.columns
    assert len(result_df) == 3


def test_helpers_compatibility():
    from tests.helpers import (
        create_test_collar_csv,
        create_test_survey_csv,
        create_test_assays_csv
    )
    
    parser = DrillholeParser()
    
    # Collar
    collar_csv = create_test_collar_csv()
    collar_df = parser.parse_collar(collar_csv)
    assert len(collar_df) > 0
    
    # Survey
    survey_csv = create_test_survey_csv()
    survey_df = parser.parse_survey(survey_csv)
    assert len(survey_df) > 0
    
    # Assays
    assays_csv = create_test_assays_csv()
    assays_df = parser.parse_assays(assays_csv)
    assert len(assays_df) > 0


def test_parser_uppercase_columns():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['DH001', 'DH002', 'DH003'],
        'EAST': [500100, 500200, 500300],
        'NORTH': [6000100, 6000200, 6000300],
        'ELEV': [1250.0, 1245.0, 1240.0],
        'MAX_DEPTH': [150.0, 200.0, 180.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    assert 'HOLEID' in result.columns
    assert 'EAST' in result.columns
    assert 'NORTH' in result.columns
    assert 'ELEV' in result.columns
    assert 'MAX_DEPTH' in result.columns
    
    assert len(result) == 3
    assert result['HOLEID'].tolist() == ['DH001', 'DH002', 'DH003']


def test_parser_lowercase_columns():
    parser = DrillholeParser()
    
    data = {
        'holeid': ['DH001', 'DH002'],
        'east': [500100, 500200],
        'north': [6000100, 6000200],
        'elevation': [1250.0, 1245.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    # Colonnes doivent être normalisées en majuscules
    assert 'HOLEID' in result.columns
    assert 'EAST' in result.columns
    assert 'NORTH' in result.columns
    assert 'ELEV' in result.columns
    assert len(result) == 2


def test_parser_mixed_case_columns():
    parser = DrillholeParser()
    
    data = {
        'Hole_ID': ['DH001', 'DH002'],
        'easting': [500100, 500200],
        'Northing': [6000100, 6000200],
        'ELEVATION': [1250.0, 1245.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    assert 'HOLEID' in result.columns
    assert 'EAST' in result.columns
    assert 'NORTH' in result.columns
    assert 'ELEV' in result.columns
    assert len(result) == 2


def test_parser_alternative_names():
    parser = DrillholeParser()
    
    data = {
        'DHID': ['DH001', 'DH002'],
        'X': [500100, 500200],
        'Y': [6000100, 6000200],
        'RL': [1250.0, 1245.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    assert 'HOLEID' in result.columns
    assert 'EAST' in result.columns
    assert 'NORTH' in result.columns
    assert 'ELEV' in result.columns
    assert len(result) == 2


def test_parser_with_underscores():
    parser = DrillholeParser()
    
    data = {
        'hole_id': ['DH001', 'DH002'],
        'x_coord': [500100, 500200],
        'y_coord': [6000100, 6000200],
        'z_coord': [1250.0, 1245.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    assert 'HOLEID' in result.columns
    assert 'EAST' in result.columns
    assert 'NORTH' in result.columns
    assert 'ELEV' in result.columns


def test_parser_missing_column_error():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': [500100, 500200],
        # NORTH manquant
        'ELEV': [1250.0, 1245.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    with pytest.raises(ValueError) as exc_info:
        parser.parse_collar(buffer)
    
    assert 'missing required columns' in str(exc_info.value)
    assert 'NORTH' in str(exc_info.value)


def test_parser_empty_csv():
    parser = DrillholeParser()
    
    # CSV vide
    buffer = BytesIO(b"HOLEID,EAST,NORTH,ELEV\n")
    
    with pytest.raises(ValueError) as exc_info:
        parser.parse_collar(buffer)
    
    assert 'empty' in str(exc_info.value).lower()


def test_parser_strips_whitespace():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['  DH001  ', ' DH002', 'DH003 '],
        'EAST': [500100, 500200, 500300],
        'NORTH': [6000100, 6000200, 6000300],
        'ELEV': [1250.0, 1245.0, 1240.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    assert result['HOLEID'].tolist() == ['DH001', 'DH002', 'DH003']


def test_parser_handles_nan():
    parser = DrillholeParser()
    
    import numpy as np
    
    data = {
        'HOLEID': ['DH001', 'DH002', 'DH003'],
        'EAST': [500100, np.nan, 500300],  # NaN dans une ligne
        'NORTH': [6000100, 6000200, 6000300],
        'ELEV': [1250.0, 1245.0, 1240.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    assert len(result) == 2
    assert 'DH001' in result['HOLEID'].values
    assert 'DH002' not in result['HOLEID'].values  # Ligne avec NaN supprimée
    assert 'DH003' in result['HOLEID'].values


def test_parser_type_conversion():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': ['500100', '500200'],  # Strings
        'NORTH': ['6000100', '6000200'],  # Strings
        'ELEV': ['1250.0', '1245.0']  # Strings
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_collar(buffer)
    
    assert result['HOLEID'].dtype == object  # String
    assert pd.api.types.is_numeric_dtype(result['EAST'])
    assert pd.api.types.is_numeric_dtype(result['NORTH'])
    assert pd.api.types.is_numeric_dtype(result['ELEV'])


def test_parser_survey():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['DH001', 'DH001', 'DH002'],
        'DEPTH': [0.0, 50.0, 0.0],
        'AZIMUTH': [45.0, 48.0, 45.0],
        'DIP': [-60.0, -62.0, -60.0]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_survey(buffer)
    
    assert 'HOLEID' in result.columns
    assert 'DEPTH' in result.columns
    assert 'AZIMUTH' in result.columns
    assert 'DIP' in result.columns
    assert len(result) == 3


def test_parser_assays():
    parser = DrillholeParser()
    
    data = {
        'HOLEID': ['DH001', 'DH001', 'DH002'],
        'FROM': [0.0, 25.0, 0.0],
        'TO': [25.0, 50.0, 25.0],
        'LITHOLOGY': ['GRANITE', 'ORE', 'DIORITE'],
        'AU_PPM': [0.1, 2.5, 0.3],
        'CU_PCT': [0.05, 0.8, 0.1]
    }
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    result = parser.parse_assays(buffer)
    
    assert 'HOLEID' in result.columns
    assert 'FROM' in result.columns
    assert 'TO' in result.columns
    assert 'LITHOLOGY' in result.columns
    assert len(result) == 3


def test_get_supported_variations():
    parser = DrillholeParser()
    
    collar_vars = parser.get_supported_variations('collar')
    assert 'holeid' in collar_vars
    assert 'east' in collar_vars
    assert 'north' in collar_vars
    assert 'x' in collar_vars
    assert 'y' in collar_vars
    
    survey_vars = parser.get_supported_variations('survey')
    assert 'depth' in survey_vars
    assert 'azimuth' in survey_vars
    assert 'dip' in survey_vars
    
    assays_vars = parser.get_supported_variations('assays')
    assert 'from' in assays_vars
    assert 'to' in assays_vars


def test_parser_real_world_case():
    parser = DrillholeParser()
    
    # Simuler un export de logiciel minier (tout en majuscules)
    csv_content = """HOLEID,EAST,NORTH,ELEV,MAX_DEPTH
DH001,500000,6000000,1200,150.5
DH002,500100,6000100,1205,200.0
DH003,500200,6000200,1210,180.5
"""
    
    buffer = BytesIO(csv_content.encode())
    result = parser.parse_collar(buffer)
    
    assert len(result) == 3
    assert all(col in result.columns for col in ['HOLEID', 'EAST', 'NORTH', 'ELEV', 'MAX_DEPTH'])
    assert result['HOLEID'].tolist() == ['DH001', 'DH002', 'DH003']