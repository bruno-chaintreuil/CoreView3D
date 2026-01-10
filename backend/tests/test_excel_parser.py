import pytest
import pandas as pd
from io import BytesIO
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from coreview3d.parsers.excel_parser import ExcelDrillholeParser


def create_excel_file(
    collar_data: dict,
    survey_data: dict = None,
    assays_data: dict = None,
    collar_sheet_name: str = 'Collar',
    survey_sheet_name: str = 'Survey',
    assays_sheet_name: str = 'Assays'
) -> BytesIO:
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Collar
        collar_df = pd.DataFrame(collar_data)
        collar_df.to_excel(writer, sheet_name=collar_sheet_name, index=False)
        
        # Survey
        if survey_data:
            survey_df = pd.DataFrame(survey_data)
            survey_df.to_excel(writer, sheet_name=survey_sheet_name, index=False)
        
        # Assays
        if assays_data:
            assays_df = pd.DataFrame(assays_data)
            assays_df.to_excel(writer, sheet_name=assays_sheet_name, index=False)
    
    buffer.seek(0)
    return buffer


def test_parse_excel_file_complete():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001', 'DH002', 'DH003'],
        'EAST': [500100, 500200, 500300],
        'NORTH': [6000100, 6000200, 6000300],
        'ELEV': [1250.0, 1245.0, 1240.0],
        'MAX_DEPTH': [150.0, 200.0, 180.0]
    }
    
    survey_data = {
        'HOLEID': ['DH001', 'DH001', 'DH002'],
        'DEPTH': [0.0, 50.0, 0.0],
        'AZIMUTH': [45.0, 48.0, 45.0],
        'DIP': [-60.0, -62.0, -60.0]
    }
    
    assays_data = {
        'HOLEID': ['DH001', 'DH001', 'DH002'],
        'FROM': [0.0, 25.0, 0.0],
        'TO': [25.0, 50.0, 25.0],
        'LITHOLOGY': ['GRANITE', 'ORE', 'DIORITE'],
        'AU_PPM': [0.1, 2.5, 0.3]
    }
    
    excel_file = create_excel_file(collar_data, survey_data, assays_data)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['collar'] is not None
    assert result['survey'] is not None
    assert result['assays'] is not None
    
    assert len(result['collar']) == 3
    assert len(result['survey']) == 3
    assert len(result['assays']) == 3
    
    assert 'HOLEID' in result['collar'].columns
    assert 'EAST' in result['collar'].columns
    assert 'NORTH' in result['collar'].columns


def test_parse_excel_file_collar_only():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': [500100, 500200],
        'NORTH': [6000100, 6000200],
        'ELEV': [1250.0, 1245.0]
    }
    
    excel_file = create_excel_file(collar_data)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['collar'] is not None
    assert result['survey'] is None
    assert result['assays'] is None
    
    assert len(result['collar']) == 2


@pytest.mark.parametrize("sheet_name", [
    'Collar', 'collar', 'COLLAR', 'Collars', 'collars', 'Holes', 'holes'
])
def test_parse_excel_collar_sheet_name_variations(sheet_name):
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': [500100, 500200],
        'NORTH': [6000100, 6000200],
        'ELEV': [1250.0, 1245.0]
    }
    
    excel_file = create_excel_file(collar_data, collar_sheet_name=sheet_name)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['collar'] is not None
    assert len(result['collar']) == 2


@pytest.mark.parametrize("sheet_name", [
    'Survey', 'survey', 'SURVEY', 'Surveys', 'Deviation', 'deviation'
])
def test_parse_excel_survey_sheet_name_variations(sheet_name):
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001'],
        'EAST': [500100],
        'NORTH': [6000100],
        'ELEV': [1250.0]
    }
    
    survey_data = {
        'HOLEID': ['DH001'],
        'DEPTH': [0.0],
        'AZIMUTH': [45.0],
        'DIP': [-60.0]
    }
    
    excel_file = create_excel_file(collar_data, survey_data, survey_sheet_name=sheet_name)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['survey'] is not None
    assert len(result['survey']) == 1


def test_parse_excel_column_variations():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'Hole_ID': ['DH001', 'DH002'],
        'X': [500100, 500200],
        'Y': [6000100, 6000200],
        'RL': [1250.0, 1245.0]         
    }
    
    excel_file = create_excel_file(collar_data)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['collar'] is not None
    
    assert 'HOLEID' in result['collar'].columns
    assert 'EAST' in result['collar'].columns
    assert 'NORTH' in result['collar'].columns
    assert 'ELEV' in result['collar'].columns


def test_parse_excel_mixed_case_columns():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'Hole_ID': ['DH001', 'DH002'],
        'easting': [500100, 500200],
        'Northing': [6000100, 6000200],
        'ELEVATION': [1250.0, 1245.0]
    }
    
    excel_file = create_excel_file(collar_data)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['collar'] is not None
    assert all(col in result['collar'].columns for col in ['HOLEID', 'EAST', 'NORTH', 'ELEV'])


def test_parse_collar_sheet_specific():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': [500100, 500200],
        'NORTH': [6000100, 6000200],
        'ELEV': [1250.0, 1245.0]
    }
    
    excel_file = create_excel_file(collar_data)
    
    df = parser.parse_collar_sheet(excel_file, sheet_name='Collar')
    
    assert len(df) == 2
    assert 'HOLEID' in df.columns
    assert df['HOLEID'].tolist() == ['DH001', 'DH002']


def test_parse_survey_sheet_specific():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001'],
        'EAST': [500100],
        'NORTH': [6000100],
        'ELEV': [1250.0]
    }
    
    survey_data = {
        'HOLEID': ['DH001', 'DH001'],
        'DEPTH': [0.0, 50.0],
        'AZIMUTH': [45.0, 48.0],
        'DIP': [-60.0, -62.0]
    }
    
    excel_file = create_excel_file(collar_data, survey_data)
    
    df = parser.parse_survey_sheet(excel_file, sheet_name='Survey')
    
    assert len(df) == 2
    assert 'HOLEID' in df.columns
    assert 'DEPTH' in df.columns


def test_parse_assays_sheet_specific():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001'],
        'EAST': [500100],
        'NORTH': [6000100],
        'ELEV': [1250.0]
    }
    
    assays_data = {
        'HOLEID': ['DH001', 'DH001'],
        'FROM': [0.0, 25.0],
        'TO': [25.0, 50.0],
        'LITHOLOGY': ['GRANITE', 'ORE'],
        'AU_PPM': [0.1, 2.5]
    }
    
    excel_file = create_excel_file(collar_data, assays_data=assays_data)
    
    df = parser.parse_assays_sheet(excel_file, sheet_name='Assays')
    
    assert len(df) == 2
    assert 'HOLEID' in df.columns
    assert 'FROM' in df.columns
    assert 'TO' in df.columns
    assert 'LITHOLOGY' in df.columns


# def test_parse_excel_empty_sheet():
#     parser = ExcelDrillholeParser()
    
#     # Créer un Excel avec une feuille vide
#     buffer = BytesIO()
#     with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
#         empty_df = pd.DataFrame()
#         empty_df.to_excel(writer, sheet_name='Collar', index=False)
    
#     buffer.seek(0)
    
#     with pytest.raises(ValueError, match="empty"):
#         parser.parse_excel_file(buffer)


def test_parse_excel_missing_required_column():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': [500100, 500200],
        # NORTH missing
        'ELEV': [1250.0, 1245.0]
    }
    
    excel_file = create_excel_file(collar_data)
    
    with pytest.raises(ValueError, match="missing required columns"):
        parser.parse_excel_file(excel_file)


def test_parse_excel_with_nan_values():
    import numpy as np
    
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001', 'DH002', 'DH003'],
        'EAST': [500100, np.nan, 500300],  # NaN
        'NORTH': [6000100, 6000200, 6000300],
        'ELEV': [1250.0, 1245.0, 1240.0]
    }
    
    excel_file = create_excel_file(collar_data)
    
    result = parser.parse_excel_file(excel_file)
    
    assert len(result['collar']) == 2
    assert 'DH001' in result['collar']['HOLEID'].values
    assert 'DH002' not in result['collar']['HOLEID'].values
    assert 'DH003' in result['collar']['HOLEID'].values


def test_parse_excel_strips_whitespace():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['  DH001  ', ' DH002', 'DH003 '],
        'EAST': [500100, 500200, 500300],
        'NORTH': [6000100, 6000200, 6000300],
        'ELEV': [1250.0, 1245.0, 1240.0]
    }
    
    excel_file = create_excel_file(collar_data)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['collar']['HOLEID'].tolist() == ['DH001', 'DH002', 'DH003']


def test_parse_excel_type_conversion():
    parser = ExcelDrillholeParser()
    
    collar_data = {
        'HOLEID': ['DH001', 'DH002'],
        'EAST': ['500100', '500200'],  # Strings
        'NORTH': ['6000100', '6000200'],  # Strings
        'ELEV': ['1250.0', '1245.0']  # Strings
    }
    
    excel_file = create_excel_file(collar_data)
    
    result = parser.parse_excel_file(excel_file)
    
    assert result['collar']['HOLEID'].dtype == object  # String
    assert pd.api.types.is_numeric_dtype(result['collar']['EAST'])
    assert pd.api.types.is_numeric_dtype(result['collar']['NORTH'])
    assert pd.api.types.is_numeric_dtype(result['collar']['ELEV'])