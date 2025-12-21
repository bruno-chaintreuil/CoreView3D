from pathlib import Path
import pytest
from coreview3d.store.store import SessionData


@pytest.mark.asyncio
async def test_save_session_creates_db(persistence_manager, sample_session_data):
    session_id = "test-session-001"
    
    result = await persistence_manager.save_session_data(session_id, sample_session_data)
    
    assert result is True
    assert Path(persistence_manager.db_path).exists()


@pytest.mark.asyncio
async def test_save_and_retrieve_session(persistence_manager, sample_session_data):
    session_id = "test-session-002"
    
    # Save
    await persistence_manager.save_session_data(session_id, sample_session_data)
    
    # Retrieve
    retrieved = await persistence_manager.get_session_data(session_id)
    
    assert retrieved is not None
    assert len(retrieved.collar_df) == len(sample_session_data.collar_df)
    assert retrieved.collar_df['HOLEID'].tolist() == sample_session_data.collar_df['HOLEID'].tolist()
    assert retrieved.trajectories == sample_session_data.trajectories


@pytest.mark.asyncio
async def test_retrieve_nonexistent_session(persistence_manager):
    result = await persistence_manager.get_session_data("does-not-exist")
    assert result is None


@pytest.mark.asyncio
async def test_update_existing_session(persistence_manager, sample_session_data):
    session_id = "test-session-003"
    
    # Save initial
    await persistence_manager.save_session_data(session_id, sample_session_data)
    
    # Modify
    modified_data = sample_session_data
    modified_data.collar_df.loc[0, 'ELEV'] = 9999.0
    
    # Update
    await persistence_manager.save_session_data(session_id, modified_data)
    
    # Retrieve
    retrieved = await persistence_manager.get_session_data(session_id)
    
    assert retrieved.collar_df.loc[0, 'ELEV'] == 9999.0


@pytest.mark.asyncio
async def test_delete_session(persistence_manager, sample_session_data):
    session_id = "test-session-004"
    
    # Save
    await persistence_manager.save_session_data(session_id, sample_session_data)
    
    # Delete
    deleted = await persistence_manager.delete_session_data(session_id)
    
    assert deleted is True
    
    # Verify it's gone
    retrieved = await persistence_manager.get_session_data(session_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_nonexistent_session(persistence_manager):
    result = await persistence_manager.delete_session_data("does-not-exist")
    assert result is False


@pytest.mark.asyncio
async def test_list_sessions(persistence_manager, sample_session_data):
    session_ids = ["test-session-005", "test-session-006", "test-session-007"]
    
    # Save multiple sessions
    for sid in session_ids:
        await persistence_manager.save_session_data(sid, sample_session_data)
    
    # List
    sessions = await persistence_manager.list_sessions()
    
    assert len(sessions) >= 3
    session_id_list = [s['session_id'] for s in sessions]
    
    for sid in session_ids:
        assert sid in session_id_list


@pytest.mark.asyncio
async def test_session_metadata(persistence_manager, sample_session_data):
    session_id = "test-session-008"
    
    await persistence_manager.save_session_data(session_id, sample_session_data)
    
    metadata = await persistence_manager.get_session_metadata(session_id)
    
    assert metadata is not None
    assert metadata['session_id'] == session_id
    assert metadata['total_holes'] == 4
    assert metadata['has_survey'] is True
    assert metadata['has_assays'] is True


@pytest.mark.asyncio
async def test_save_session_without_optional_data(persistence_manager, sample_collar_df):
    session_id = "test-session-009"
    
    session_data = SessionData(
        collar_df=sample_collar_df,
        survey_df=None,
        assays_df=None,
        trajectories=None
    )
    
    await persistence_manager.save_session_data(session_id, session_data)
    
    retrieved = await persistence_manager.get_session_data(session_id)
    
    assert retrieved is not None
    assert retrieved.survey_df is None
    assert retrieved.assays_df is None
    assert retrieved.trajectories is None

