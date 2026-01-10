from typing import Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd
import logging
import sqlite3
import json
import pickle
from pathlib import Path

logger = logging.getLogger("store")

@dataclass
class SessionData:
    collar_df: pd.DataFrame
    survey_df: pd.DataFrame = None
    assays_df: pd.DataFrame = None
    trajectories: list = None


class PersistenceManager:

    def __init__(self, db_path: str = "./data/sessions.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        collar_data BLOB,
                        survey_data BLOB,
                        assays_data BLOB,
                        trajectories TEXT
                    )
                """)
                conn.commit()
                logger.info(f"✅ Base de données initialisée: {self.db_path}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la DB: {e}")
            raise
    
    def _serialize_dataframe(self, df: Optional[pd.DataFrame]) -> Optional[bytes]:
        if df is None or df.empty:
            return None
        return pickle.dumps(df)
    
    def _deserialize_dataframe(self, data: Optional[bytes]) -> Optional[pd.DataFrame]:
        if data is None:
            return None
        return pickle.loads(data)

    async def save_session_data(self, session_id: str, data: SessionData) -> bool:
        try:
            metadata = {
                "total_holes": len(data.collar_df),
                "has_survey": data.survey_df is not None,
                "has_assays": data.assays_df is not None,
            }
            
            collar_blob = self._serialize_dataframe(data.collar_df)
            survey_blob = self._serialize_dataframe(data.survey_df)
            assays_blob = self._serialize_dataframe(data.assays_df)
            trajectories_json = json.dumps(data.trajectories) if data.trajectories else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT session_id FROM sessions WHERE session_id = ?", (session_id,))
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE sessions 
                        SET updated_at = CURRENT_TIMESTAMP,
                            metadata = ?,
                            collar_data = ?,
                            survey_data = ?,
                            assays_data = ?,
                            trajectories = ?
                        WHERE session_id = ?
                    """, (
                        json.dumps(metadata),
                        collar_blob,
                        survey_blob,
                        assays_blob,
                        trajectories_json,
                        session_id
                    ))
                    logger.info(f"✅ Session {session_id} mise à jour")
                else:
                    cursor.execute("""
                        INSERT INTO sessions (session_id, metadata, collar_data, survey_data, assays_data, trajectories)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        session_id,
                        json.dumps(metadata),
                        collar_blob,
                        survey_blob,
                        assays_blob,
                        trajectories_json
                    ))
                    logger.info(f"✅ Session {session_id} créée")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Erreur save_session_data: {e}")
            raise

    async def get_session_data(self, session_id: str) -> Optional[SessionData]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT collar_data, survey_data, assays_data, trajectories
                    FROM sessions
                    WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"⚠️ Session {session_id} non trouvée")
                    return None
                
                collar_blob, survey_blob, assays_blob, trajectories_json = row
                
                collar_df = self._deserialize_dataframe(collar_blob)
                survey_df = self._deserialize_dataframe(survey_blob)
                assays_df = self._deserialize_dataframe(assays_blob)
                trajectories = json.loads(trajectories_json) if trajectories_json else None
                
                logger.info(f"✅ Session {session_id} récupérée")
                
                return SessionData(
                    collar_df=collar_df,
                    survey_df=survey_df,
                    assays_df=assays_df,
                    trajectories=trajectories
                )
                
        except Exception as e:
            logger.error(f"Erreur get_session_data: {e}")
            raise

    async def delete_session_data(self, session_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                deleted = cursor.rowcount > 0
                conn.commit()
                
                if deleted:
                    logger.info(f"✅ Session {session_id} supprimée")
                else:
                    logger.warning(f"⚠️ Session {session_id} non trouvée pour suppression")
                    
                return deleted
                
        except Exception as e:
            logger.error(f"Erreur delete_session_data: {e}")
            raise

    async def list_sessions(self) -> list[dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, created_at, updated_at, metadata
                    FROM sessions
                    ORDER BY updated_at DESC
                """)
                
                sessions = []
                for row in cursor.fetchall():
                    session_id, created_at, updated_at, metadata_json = row
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    sessions.append({
                        "session_id": session_id,
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "metadata": metadata
                    })
                
                logger.info(f"✅ {len(sessions)} sessions listées")
                return sessions
                
        except Exception as e:
            logger.error(f"Erreur list_sessions: {e}")
            raise

    async def get_session_metadata(self, session_id: str) -> Optional[dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT metadata, created_at, updated_at
                    FROM sessions
                    WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                metadata_json, created_at, updated_at = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                return {
                    "session_id": session_id,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    **metadata
                }
                
        except Exception as e:
            logger.error(f"Erreur get_session_metadata: {e}")
            raise

persistence_manager = PersistenceManager()