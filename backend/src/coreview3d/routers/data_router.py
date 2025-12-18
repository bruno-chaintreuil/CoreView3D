from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import io

from coreview3d.parsers.csv_parser import DrillholeParser
from coreview3d.geometry.trajectory import calculate_trajectories

data_router = APIRouter(prefix="/api", tags=["data"])

@data_router.post("/upload/collar")
async def upload_collar_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        parser = DrillholeParser()
        collar_df = parser.parse_collar(io.BytesIO(contents))
        
        return {
            "success": True,
            "message": f"Parsed {len(collar_df)} collars",
            "data": collar_df.to_dict(orient="records"),
            "columns": list(collar_df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing collar file: {str(e)}")

@data_router.post("/upload/survey")
async def upload_survey_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        parser = DrillholeParser()
        survey_df = parser.parse_survey(io.BytesIO(contents))
        
        return {
            "success": True,
            "message": f"Parsed {len(survey_df)} survey measurements",
            "data": survey_df.to_dict(orient="records"),
            "columns": list(survey_df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing survey file: {str(e)}")

@data_router.post("/upload/assays")
async def upload_assays_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        parser = DrillholeParser()
        assays_df = parser.parse_assays(io.BytesIO(contents))
        
        return {
            "success": True,
            "message": f"Parsed {len(assays_df)} assay intervals",
            "data": assays_df.to_dict(orient="records"),
            "columns": list(assays_df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing assays file: {str(e)}")

@data_router.post("/process/trajectories")
async def process_trajectories_endpoint(
    collar_file: UploadFile = File(...),
    survey_file: Optional[UploadFile] = File(None)
):
    try:
        parser = DrillholeParser()
        
        collar_contents = await collar_file.read()
        collar_df = parser.parse_collar(io.BytesIO(collar_contents))
        
        survey_df = None
        if survey_file:
            survey_contents = await survey_file.read()
            survey_df = parser.parse_survey(io.BytesIO(survey_contents))
        
        trajectories = calculate_trajectories(collar_df, survey_df)
        
        return {
            "success": True,
            "message": f"Calculated trajectories for {len(trajectories)} drillholes",
            "data": trajectories
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error processing trajectories: {str(e)}"
        )