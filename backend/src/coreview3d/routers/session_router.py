from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import uuid
import io
import logging
import pandas as pd

from coreview3d.store.store import SessionData, persistence_manager
from coreview3d.parsers.csv_parser import DrillholeParser
from coreview3d.parsers.excel_parser import ExcelDrillholeParser
from coreview3d.geometry.trajectory import calculate_trajectories

session_router = APIRouter(prefix="/api/session", tags=["session"])
logger = logging.getLogger("session")
logger.setLevel(logging.DEBUG)


@session_router.post("/create")
async def create_session(
    collar_file: UploadFile = File(...),
    survey_file: Optional[UploadFile] = File(None),
    assays_file: Optional[UploadFile] = File(None)
):
    try:
        logger.info("create_session: start")

        parser = DrillholeParser()
        
        c_content = await collar_file.read()
        collar_df = parser.parse_collar(io.BytesIO(c_content))
        
        survey_df = None
        if survey_file:
            s_content = await survey_file.read()
            survey_df = parser.parse_survey(io.BytesIO(s_content))
            
        assays_df = None
        if assays_file:
            a_content = await assays_file.read()
            assays_df = parser.parse_assays(io.BytesIO(a_content))
            
        trajectories = calculate_trajectories(collar_df, survey_df)
        
        session_id = str(uuid.uuid4())
        
        session_data = SessionData(
            collar_df=collar_df,
            survey_df=survey_df,
            assays_df=assays_df,
            trajectories=trajectories
        )

        await persistence_manager.save_session_data(session_id, session_data)
        
        logger.info(f"Session created with id={session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "metadata": {
                "total_holes": len(collar_df),
                "has_survey": survey_df is not None,
                "has_assays": assays_df is not None
            },
            "data": { 
                "trajectories": trajectories,
                "assays": assays_df.to_dict(orient="records") if assays_df is not None else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"create_session error: {e}")
        raise HTTPException(status_code=400, detail=f"Error opening file: {str(e)}")


@session_router.post("/create-excel")
async def create_session_excel(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Le fichier doit être au format .xlsx")
        
        contents = await file.read()
        parser = ExcelDrillholeParser() 
        result = parser.parse_excel_file(io.BytesIO(contents))
        
        if result['collar'] is None:
            raise HTTPException(status_code=400, detail="L'Excel doit contenir la feuille 'Collar'")
        
        trajectories = calculate_trajectories(result['collar'], result['survey'])
        
        session_id = str(uuid.uuid4())
        
        session_data = SessionData(
            collar_df=result['collar'],
            survey_df=result['survey'],
            assays_df=result['assays'],
            trajectories=trajectories
        )
        
        await persistence_manager.save_session_data(session_id, session_data)
        
        logger.info(f"Session Excel créée et persistée avec id={session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "metadata": {
                "total_holes": len(result['collar']),
                "has_survey": result['survey'] is not None,
                "has_assays": result['assays'] is not None,
            },
            "data": {
                "trajectories": trajectories,
                "assays": result['assays'].to_dict(orient="records") if result['assays'] is not None else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"create_session_excel error: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement de l'Excel: {str(e)}")


@session_router.get("/load/{session_id}")
async def load_session(session_id: str):
    try:
        session_data = await persistence_manager.get_session_data(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session ID {session_id} non trouvée.")

        logger.info(f"Session {session_id} chargée avec succès.")

        return {
            "success": True,
            "session_id": session_id,
            "metadata": {
                "total_holes": len(session_data.collar_df),
                "has_survey": session_data.survey_df is not None,
                "has_assays": session_data.assays_df is not None,
            },
            "data": {
                "trajectories": session_data.trajectories,
                "assays": session_data.assays_df.to_dict(orient="records") if session_data.assays_df is not None else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"load_session error: {e}")
        raise HTTPException(status_code=500, detail=f"Error opening session: {str(e)}")


@session_router.get("/list")
async def list_sessions():
    try:
        sessions = await persistence_manager.list_sessions()
        
        return {
            "success": True,
            "total": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"list_sessions error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des sessions: {str(e)}")


@session_router.get("/metadata/{session_id}")
async def get_session_metadata(session_id: str):
    try:
        metadata = await persistence_manager.get_session_metadata(session_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Session ID {session_id} non trouvée.")
        
        return {
            "success": True,
            "metadata": metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_session_metadata error: {e}")
        raise HTTPException(status_code=500, detail=f"Error when retrieving metadata: {str(e)}")


@session_router.delete("/delete/{session_id}")
async def delete_session(session_id: str):
    try:
        deleted = await persistence_manager.delete_session_data(session_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Session ID {session_id} not found.")
        
        logger.info(f"Session {session_id} supprimée avec succès.")
        
        return {
            "success": True,
            "message": f"Session {session_id} supprimée"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_session error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur when deleting session {session_id}: {str(e)}")