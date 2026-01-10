import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("trajectory")

def calculate_trajectories(
    collar_df: pd.DataFrame,
    survey_df: Optional[pd.DataFrame] = None
) -> List[Dict]:
    """
    Calculate 3D trajectories for all drillholes.
    
    Expects normalized column names:
    - collar_df: HOLEID, EAST, NORTH, ELEV, MAX_DEPTH, AZIMUTH, DIP
    - survey_df: HOLEID, DEPTH, AZIMUTH, DIP
    """
    results = []

    for _, collar in collar_df.iterrows():
        hole_id = collar["HOLEID"]

        # Extract surveys for this hole
        sub = None
        if survey_df is not None and not survey_df.empty:
            subset = survey_df[survey_df["HOLEID"] == hole_id]
            if len(subset) > 0:
                sub = subset

        # Compute 3D points
        pts = calculate_single_trajectory(collar, sub)
        
        # Calculate Measured Depth (MD) along the path
        depths = [0.0]
        for i in range(1, len(pts)):
            segment_length = np.linalg.norm(np.array(pts[i]) - np.array(pts[i-1]))
            depths.append(depths[-1] + segment_length)

        results.append({
            "hole_id": hole_id,
            "collar": {
                "east": float(collar["EAST"]),
                "north": float(collar["NORTH"]),
                "elevation": float(collar["ELEV"]),
                "max_depth": float(collar.get("MAX_DEPTH", 0.0)),
                "azimuth": float(collar.get("AZIMUTH", 0.0)),
                "dip": float(collar.get("DIP", -90.0))
            },
            "points": [
                {"depth": depths[i], "x": pt[0], "y": pt[1], "z": pt[2]} 
                for i, pt in enumerate(pts)
            ],
            "has_survey": sub is not None
        })

    return results

def calculate_single_trajectory(
    collar: pd.Series,
    survey_df: Optional[pd.DataFrame] = None
) -> List[List[float]]:
    """
    Calculate 3D points for a single hole using standard mining conventions:
    - Azimuth: 0=North, 90=East
    - Dip: 0=Horizontal, -90=Vertical Down
    """
    x0 = float(collar["EAST"])
    y0 = float(collar["NORTH"])
    z0 = float(collar["ELEV"])
    max_depth = float(collar.get("MAX_DEPTH", 100.0))
    
    def get_displacement(depth_step, az_deg, dip_deg):
        # Convert Geographic Azimuth (0 North) to Math Angle (0 East, CCW)
        # Math_Angle = 90 - Geo_Azimuth
        az_rad = np.radians(90 - az_deg)
        dip_rad = np.radians(dip_deg)
        
        # Horizontal projection: cos(-90) = 0 (vertical), cos(0) = 1 (horizontal)
        horiz_dist = depth_step * np.cos(dip_rad)
        
        dx = horiz_dist * np.cos(az_rad)
        dy = horiz_dist * np.sin(az_rad)
        dz = depth_step * np.sin(dip_rad) # sin(-90) = -1 (down)
        return dx, dy, dz

    # Case 1: No Survey data - straight line from collar to max depth
    if survey_df is None or len(survey_df) == 0:
        az = float(collar.get("AZIMUTH", 0.0))
        dip = float(collar.get("DIP", -90.0))
        dx, dy, dz = get_displacement(max_depth, az, dip)
        return [[x0, y0, z0], [x0 + dx, y0 + dy, z0 + dz]]

    # Case 2: Process Survey intervals
    trajectory = [[x0, y0, z0]]
    survey_sorted = survey_df.sort_values("DEPTH").reset_index(drop=True)
    
    curr_x, curr_y, curr_z = x0, y0, z0
    prev_d = 0.0
    
    for _, row in survey_sorted.iterrows():
        d = float(row["DEPTH"])
        if d <= prev_d:
            continue
        
        step = d - prev_d
        dx, dy, dz = get_displacement(step, float(row["AZIMUTH"]), float(row["DIP"]))
        
        curr_x += dx
        curr_y += dy
        curr_z += dz
        trajectory.append([curr_x, curr_y, curr_z])
        prev_d = d
        
    # Optional: Extend to MAX_DEPTH if surveys end early
    if prev_d < max_depth:
        last_az = float(survey_sorted.iloc[-1]["AZIMUTH"])
        last_dip = float(survey_sorted.iloc[-1]["DIP"])
        step = max_depth - prev_d
        dx, dy, dz = get_displacement(step, last_az, last_dip)
        trajectory.append([curr_x + dx, curr_y + dy, curr_z + dz])

    return trajectory


def validate_trajectory(trajectory: List[List[float]]) -> bool:
    if not trajectory or len(trajectory) < 2:
        return False
    
    for point in trajectory:
        if len(point) != 3:
            return False
        if any(not isinstance(coord, (int, float)) or np.isnan(coord) for coord in point):
            return False
    
    return True


def get_trajectory_length(trajectory: List[List[float]]) -> float:
    if len(trajectory) < 2:
        return 0.0
    
    total_length = 0.0
    for i in range(1, len(trajectory)):
        p1 = np.array(trajectory[i-1])
        p2 = np.array(trajectory[i])
        total_length += np.linalg.norm(p2 - p1)
    
    return total_length