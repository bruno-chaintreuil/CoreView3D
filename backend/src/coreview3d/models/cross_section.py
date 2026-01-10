from pydantic import BaseModel
from typing import List, Tuple

class CrossSectionRequest(BaseModel):
    session_id: str
    xy_start: Tuple[float, float]
    xy_stop: Tuple[float, float]
    hole_ids: List[str]
    tolerance: float = 100.0

class DrillholePoint(BaseModel):
    z: float
    x: float

class ProjectedDrillhole(BaseModel):
    hole_id: str
    trace: List[DrillholePoint]

class CrossSectionResponse(BaseModel):
    success: bool
    xy_start: Tuple[float, float]
    xy_stop: Tuple[float, float]
    drillholes: List[ProjectedDrillhole]