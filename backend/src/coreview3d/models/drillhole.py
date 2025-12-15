from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class CollarModel(BaseModel):
    hole_id: str = Field(..., alias="Hole_ID")
    east: float = Field(..., alias="East")
    north: float = Field(..., alias="North")
    elevation: float = Field(..., alias="Elevation")
    max_depth: float = Field(..., alias="Max_Depth")
    azimuth: float = Field(..., alias="Azimuth")
    dip: float = Field(..., alias="Dip")
    date: Optional[str] = Field(None, alias="Date")
    project: Optional[str] = Field(None, alias="Project")

    class Config:
        populate_by_name = True


class SurveyModel(BaseModel):
    hole_id: str = Field(..., alias="Hole_ID")
    depth: float = Field(..., alias="Depth")
    azimuth: float = Field(..., alias="Azimuth")
    dip: float = Field(..., alias="Dip")

    class Config:
        populate_by_name = True


class AssayModel(BaseModel):
    hole_id: str = Field(..., alias="Hole_ID")
    from_depth: float = Field(..., alias="From")
    to_depth: float = Field(..., alias="To")
    lithology: Optional[str] = Field(None, alias="Lithology")
    
    class Config:
        populate_by_name = True
        extra = "allow"  # Allow additional columns like Au_ppm, Cu_pct, etc.


class TrajectoryPoint(BaseModel):
    depth: float
    x: float
    y: float
    z: float


class DrillholeTrajectory(BaseModel):
    hole_id: str
    collar: CollarModel
    points: List[TrajectoryPoint]


class DrillholeData(BaseModel):
    collars: List[CollarModel]
    surveys: Optional[List[SurveyModel]] = None
    assays: Optional[List[AssayModel]] = None
    trajectories: Optional[List[DrillholeTrajectory]] = None