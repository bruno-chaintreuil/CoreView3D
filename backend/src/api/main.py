"""
CoreView3D Backend API
Main FastAPI application for drillhole data processing
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import io

from coreview3d.parsers.csv_parser import DrillholeParser
from coreview3d.models.drillhole import DrillholeData
from coreview3d.geometry.trajectory import calculate_trajectories

app = FastAPI(
    title="CoreView3D API",
    description="Backend API for mining drillhole 3D visualization",
    version="0.1.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "CoreView3D API",
        "version": "0.1.0",
        "status": "operational"
    }


@app.post("/api/upload/collar")
async def upload_collar(file: UploadFile = File(...)):
    """
    Upload and parse collar CSV file
    
    Expected columns: Hole_ID, East, North, Elevation, Max_Depth, Azimuth, Dip
    """
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


@app.post("/api/upload/survey")
async def upload_survey(file: UploadFile = File(...)):
    """
    Upload and parse survey CSV file
    
    Expected columns: Hole_ID, Depth, Azimuth, Dip
    """
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


@app.post("/api/upload/assays")
async def upload_assays(file: UploadFile = File(...)):
    """
    Upload and parse assays/interval CSV file
    
    Expected columns: Hole_ID, From, To, and any property columns
    """
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


@app.post("/api/process/trajectories")
async def process_trajectories(
    collar_file: UploadFile = File(...),
    survey_file: Optional[UploadFile] = File(None)
):
    """
    Process drillhole trajectories from collar and optional survey data
    Returns 3D coordinates for visualization
    """
    try:
        parser = DrillholeParser()
        
        # Parse collar
        collar_contents = await collar_file.read()
        collar_df = parser.parse_collar(io.BytesIO(collar_contents))
        
        # Parse survey if provided
        survey_df = None
        if survey_file:
            survey_contents = await survey_file.read()
            survey_df = parser.parse_survey(io.BytesIO(survey_contents))
        
        # Calculate 3D trajectories
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


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "endpoints": {
            "collar": "/api/upload/collar",
            "survey": "/api/upload/survey",
            "assays": "/api/upload/assays",
            "trajectories": "/api/process/trajectories"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)