from fastapi import APIRouter, HTTPException
from coreview3d.store.store import persistence_manager
from coreview3d.models.cross_section import CrossSectionRequest, CrossSectionResponse
from coreview3d.geometry.cross_section import calculate_simple_cross_section

cross_section_router = APIRouter(prefix="/api/cross-section", tags=["cross-section"])

@cross_section_router.post("/calculate", response_model=CrossSectionResponse)
async def calculate_cross_section(request: CrossSectionRequest):    
    session_data = await persistence_manager.get_session_data(request.session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        result = calculate_simple_cross_section(
            trajectories=session_data.trajectories,
            hole_ids=request.hole_ids,
            xy_start=request.xy_start,
            xy_stop=request.xy_stop,
            tolerance=request.tolerance
        )
        
        return CrossSectionResponse(
            success=True,
            **result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))