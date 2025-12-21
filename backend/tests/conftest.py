import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from coreview3d.store.store import PersistenceManager, SessionData


@pytest.fixture
def temp_db_path():
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_sessions.db"
    yield str(db_path)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def persistence_manager(temp_db_path):
    return PersistenceManager(db_path=temp_db_path)


@pytest.fixture
def sample_collar_df():
    return pd.DataFrame({
        'HOLEID': ['DH001', 'DH002', 'DH003', 'DH004'],
        'EAST': [500100, 500200, 500300, 500150],
        'NORTH': [6000100, 6000200, 6000300, 6000400],
        'ELEV': [1250.0, 1245.0, 1240.0, 1255.0],
        'MAX_DEPTH': [150.0, 200.0, 180.0, 120.0]
    })


@pytest.fixture
def sample_survey_df():
    data = []
    for hole_id in ['DH001', 'DH002', 'DH003']:
        data.extend([
            {'HOLEID': hole_id, 'DEPTH': 0.0, 'AZIMUTH': 45.0, 'DIP': -60.0},
            {'HOLEID': hole_id, 'DEPTH': 50.0, 'AZIMUTH': 48.0, 'DIP': -62.0},
            {'HOLEID': hole_id, 'DEPTH': 100.0, 'AZIMUTH': 50.0, 'DIP': -65.0},
            {'HOLEID': hole_id, 'DEPTH': 150.0, 'AZIMUTH': 52.0, 'DIP': -68.0}
        ])
    return pd.DataFrame(data)


@pytest.fixture
def sample_assays_df():
    data = []
    for hole_id in ['DH001', 'DH002', 'DH003']:
        data.extend([
            {'HOLEID': hole_id, 'FROM': 0.0, 'TO': 25.0, 'LITHOLOGY': 'GRANITE', 'AU_PPM': 0.1, 'CU_PCT': 0.05},
            {'HOLEID': hole_id, 'FROM': 25.0, 'TO': 75.0, 'LITHOLOGY': 'DIORITE', 'AU_PPM': 0.5, 'CU_PCT': 0.12},
            {'HOLEID': hole_id, 'FROM': 75.0, 'TO': 150.0, 'LITHOLOGY': 'ORE', 'AU_PPM': 2.5, 'CU_PCT': 0.85}
        ])
    return pd.DataFrame(data)


@pytest.fixture
def sample_trajectories():
    return {
        'DH001': [[500100, 6000100, 1250], [500110, 6000110, 1200], [500120, 6000120, 1150]],
        'DH002': [[500200, 6000200, 1245], [500210, 6000210, 1195], [500220, 6000220, 1145]],
        'DH003': [[500300, 6000300, 1240], [500310, 6000310, 1190], [500320, 6000320, 1140]]
    }


@pytest.fixture
def sample_session_data(sample_collar_df, sample_survey_df, sample_assays_df, sample_trajectories):
    return SessionData(
        collar_df=sample_collar_df,
        survey_df=sample_survey_df,
        assays_df=sample_assays_df,
        trajectories=sample_trajectories
    )

