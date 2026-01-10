"""
Tests end-to-end du workflow complet.
Teste que le parser accepte différentes variations de noms de colonnes.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from coreview3d.api.main import app
from coreview3d.store.store import PersistenceManager

# Import des helpers
from tests.helpers import (
    create_test_collar_csv,
    create_test_survey_csv,
    create_test_assays_csv,
    create_test_excel_file,
    assert_session_data_valid,
    assert_cross_section_valid
)


@pytest.fixture
def client_with_temp_db():
    """Client FastAPI avec une DB temporaire."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_e2e.db"
    
    # Remplacer le persistence_manager global
    from coreview3d.store import store
    original_manager = store.persistence_manager
    store.persistence_manager = PersistenceManager(db_path=str(db_path))
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    store.persistence_manager = original_manager
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.parametrize("variation", [
    'standard',
    'uppercase',   # Le cas qui causait le bug !
    'lowercase',
    'mixed',
    'alternative'
])
def test_full_workflow_csv_variations(client_with_temp_db, variation):
    """
    Test du workflow complet CSV avec différentes variations de noms de colonnes.
    Vérifie que le parser accepte toutes les variations courantes.
    """
    client = client_with_temp_db
    
    # 1. Créer les CSV avec la variation spécifiée
    collar_csv = create_test_collar_csv(variation)
    survey_csv = create_test_survey_csv(variation)
    assays_csv = create_test_assays_csv(variation)
    
    # 2. Upload
    response = client.post(
        "/api/session/create",
        files={
            "collar_file": ("collar.csv", collar_csv, "text/csv"),
            "survey_file": ("survey.csv", survey_csv, "text/csv"),
            "assays_file": ("assays.csv", assays_csv, "text/csv")
        }
    )
    
    # Debug: Afficher la réponse en cas d'erreur
    if response.status_code != 200:
        print(f"\n❌ Test failed for variation: {variation}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
    
    assert response.status_code == 200, (
        f"Failed for variation '{variation}': {response.json()}"
    )
    
    data = response.json()
    assert data['success'] is True
    
    session_id = data['session_id']
    
    # 3. Calculer une cross-section
    response = client.post(
        "/api/cross-section/calculate",
        json={
            "session_id": session_id,
            "hole_ids": ["DH001", "DH002", "DH003"],
            "tolerance": 150.0
        }
    )
    
    if response.status_code != 200:
        print(f"\n❌ Cross-section failed for variation: {variation}")
        print(f"Response body: {response.json()}")
    
    assert response.status_code == 200
    section_data = response.json()['data']
    
    # 4. Valider la section
    assert_cross_section_valid(section_data)
    
    print(f"✅ Test passed for variation: {variation}")


@pytest.mark.integration
@pytest.mark.e2e
def test_uppercase_variation_regression():
    from coreview3d.parsers.csv_parser import DrillholeParser
    
    parser = DrillholeParser()
    
    # Créer un CSV avec les noms en majuscules
    collar_csv = create_test_collar_csv('uppercase')
    
    # Ce test doit passer maintenant
    df = parser.parse_collar(collar_csv)
    
    assert 'HOLEID' in df.columns
    assert 'EAST' in df.columns
    assert 'NORTH' in df.columns
    assert 'ELEV' in df.columns
    assert len(df) == 5


@pytest.mark.integration
@pytest.mark.e2e
def test_full_workflow_excel(client_with_temp_db):
    client = client_with_temp_db
    
    excel_file = create_test_excel_file('standard')
    
    response = client.post(
        "/api/session/create-excel",
        files={
            "file": ("drillholes.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
    )
    
    if response.status_code != 200:
        print(f"Excel upload response: {response.status_code}")
        print(f"Excel upload body: {response.json()}")
    
    assert response.status_code == 200
    session_id = response.json()['session_id']
    
    response = client.post(
        "/api/cross-section/calculate",
        json={
            "session_id": session_id,
            "hole_ids": ["DH001", "DH002"],
            "tolerance": 200.0
        }
    )
    
    assert response.status_code == 200
    section_data = response.json()['data']
    assert_cross_section_valid(section_data)


@pytest.mark.integration
@pytest.mark.e2e
def test_session_lifecycle(client_with_temp_db):
    client = client_with_temp_db
    
    # 1. Create
    collar_csv = create_test_collar_csv('uppercase')
    response = client.post(
        "/api/session/create",
        files={"collar_file": ("collar.csv", collar_csv, "text/csv")}
    )
    
    if response.status_code != 200:
        print(f"Create response: {response.status_code}")
        print(f"Create body: {response.json()}")
    
    assert response.status_code == 200
    session_id = response.json()['session_id']
    
    # 2. Load
    response = client.get(f"/api/session/load/{session_id}")
    assert response.status_code == 200
    assert response.json()['success'] is True
    
    # 3. List
    response = client.get("/api/session/list")
    assert response.status_code == 200
    sessions = response.json()['sessions']
    assert any(s['session_id'] == session_id for s in sessions)
    
    # 4. Delete
    response = client.delete(f"/api/session/delete/{session_id}")
    assert response.status_code == 200
    assert response.json()['success'] is True
    
    # 5. Vérifier que la session n'existe plus
    response = client.get(f"/api/session/load/{session_id}")
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.e2e
def test_cross_section_with_tolerance_variations(client_with_temp_db):
    """
    Test que différentes tolérances donnent différents résultats.
    """
    client = client_with_temp_db
    
    collar_csv = create_test_collar_csv('mixed')
    survey_csv = create_test_survey_csv('mixed')
    
    response = client.post(
        "/api/session/create",
        files={
            "collar_file": ("collar.csv", collar_csv, "text/csv"),
            "survey_file": ("survey.csv", survey_csv, "text/csv")
        }
    )
    
    assert response.status_code == 200
    session_id = response.json()['session_id']
    
    tolerances = [50, 150, 500]
    hole_counts = []
    
    for tolerance in tolerances:
        response = client.post(
            "/api/cross-section/calculate",
            json={
                "session_id": session_id,
                "hole_ids": ["DH001", "DH002", "DH003"],
                "tolerance": tolerance
            }
        )
        
        assert response.status_code == 200
        section_data = response.json()['data']
        hole_counts.append(len(section_data['drillholes']))
    
    assert hole_counts[0] <= hole_counts[1] <= hole_counts[2]


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.slow
def test_large_dataset_performance(client_with_temp_db):
    from coreview3d.parsers.csv_parser import DrillholeParser
    import pandas as pd
    import numpy as np
    from io import BytesIO
    import time
    
    client = client_with_temp_db
    
    large_collar_data = {
        'HOLEID': [f'DH{i:03d}' for i in range(1, 51)],
        'EAST': [500000 + i*10 for i in range(50)],
        'NORTH': [6000000 + i*10 for i in range(50)],
        'ELEV': [1200 + np.random.uniform(-10, 10) for _ in range(50)],
        'MAX_DEPTH': [150 + np.random.uniform(-20, 50) for _ in range(50)]
    }
    
    df = pd.DataFrame(large_collar_data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    parser = DrillholeParser()
    test_buffer = BytesIO(buffer.getvalue())
    try:
        parsed_df = parser.parse_collar(test_buffer)
        assert len(parsed_df) == 50, f"Parser should accept 50 holes, got {len(parsed_df)}"
    except Exception as e:
        pytest.fail(f"Parser failed on large dataset: {e}")
    
    buffer.seek(0)
    
    start = time.time()
    
    response = client.post(
        "/api/session/create",
        files={"collar_file": ("collar.csv", buffer, "text/csv")}
    )
    
    upload_time = time.time() - start
    
    assert response.status_code == 200
    session_id = response.json()['session_id']
    
    start = time.time()
    
    response = client.post(
        "/api/cross-section/calculate",
        json={
            "session_id": session_id,
            "hole_ids": [f'DH{i:03d}' for i in range(1, 21)],
            "tolerance": 200.0
        }
    )
    
    section_time = time.time() - start
    
    assert response.status_code == 200
    
    assert upload_time < 5.0
    assert section_time < 3.0
    
    print(f"\nPerformance: upload={upload_time:.2f}s, section={section_time:.2f}s")


@pytest.mark.integration
@pytest.mark.e2e
def test_all_variations_compatibility():
    from coreview3d.parsers.csv_parser import DrillholeParser
    
    parser = DrillholeParser()
    variations = ['standard', 'uppercase', 'lowercase', 'mixed', 'alternative']
    
    for variation in variations:
        # Test Collar
        collar_csv = create_test_collar_csv(variation)
        collar_df = parser.parse_collar(collar_csv)
        assert len(collar_df) > 0, f"Collar parsing failed for variation: {variation}"
        assert 'HOLEID' in collar_df.columns
        
        # Test Survey
        survey_csv = create_test_survey_csv(variation)
        survey_df = parser.parse_survey(survey_csv)
        assert len(survey_df) > 0, f"Survey parsing failed for variation: {variation}"
        assert 'HOLEID' in survey_df.columns
        
        # Test Assays
        assays_csv = create_test_assays_csv(variation)
        assays_df = parser.parse_assays(assays_csv)
        assert len(assays_df) > 0, f"Assays parsing failed for variation: {variation}"
        assert 'HOLEID' in assays_df.columns
        
        print(f"✅ All parsers work for variation: {variation}")