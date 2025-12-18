import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("trajectory")

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
    
    IMPORTANT: Expects DataFrames with NORMALIZED column names from DrillholeParser:
    - collar_df: HOLEID, EAST, NORTH, ELEV, MAX_DEPTH (optional), AZIMUTH (optional), DIP (optional)
    - survey_df: HOLEID, DEPTH, AZIMUTH, DIP
    
    Args:
        collar_df: DataFrame with collar information (normalized columns)
        survey_df: DataFrame with survey measurements (normalized columns) - optional
        
    Returns:
        List of drillhole trajectories with metadata
    """
    results = []

    for _, collar in collar_df.iterrows():
        hole_id = collar["HOLEID"]

        # Extract surveys for this hole, if any
        sub = None
        if survey_df is not None:
            subset = survey_df[survey_df["HOLEID"] == hole_id]
            if len(subset) > 0:
                sub = subset

        # Compute the trajectory
        pts = calculate_single_trajectory(collar, sub)
        
        # Ensure we always have at least 2 points
        if len(pts) < 2:
            logger.warning(f"Trajectory for {hole_id} has only {len(pts)} points, adding toe point")
            max_depth = float(collar.get("MAX_DEPTH", 100.0))
            pts.append([float(collar["EAST"]), float(collar["NORTH"]), float(collar["ELEV"]) - max_depth])

        # Calculate depth along hole for each point
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
                "max_depth": float(collar.get("MAX_DEPTH", 100.0)),
                "azimuth": float(collar.get("AZIMUTH", 0.0)),
                "dip": float(collar.get("DIP", -90.0))
            },
            "points": [{"depth": depths[i], 
                        "x": pt[0], "y": pt[1], "z": pt[2]} for i, pt in enumerate(pts)],
            "has_survey": sub is not None
        })

    return results


def calculate_single_trajectory(
    collar: pd.Series,
    survey_df: Optional[pd.DataFrame] = None
) -> List[List[float]]:
    """
    Calculate 3D trajectory for a single drillhole.
    
    Args:
        collar: Series with normalized columns (HOLEID, EAST, NORTH, ELEV, ...)
        survey_df: DataFrame with survey data (normalized columns: HOLEID, DEPTH, AZIMUTH, DIP)
    
    Returns:
        List of 3D points [[x, y, z], ...]
    """
    east = float(collar["EAST"])
    north = float(collar["NORTH"])
    elev = float(collar["ELEV"])
    
    # Get collar orientation - default to vertical down
    collar_azimuth = float(collar.get("AZIMUTH", 0.0))
    collar_dip = float(collar.get("DIP", -90.0))
    
    # Si pas de survey, trou avec orientation du collar
    if survey_df is None or len(survey_df) == 0:
        max_depth = float(collar.get("MAX_DEPTH", 100.0))
        
        # Calculate toe position based on collar orientation
        azimuth_rad = np.radians(collar_azimuth)
        
        # Dip: negative = down (mining convention)
        # Convert to inclination from vertical
        if collar_dip >= 0:
            incl_rad = np.radians(collar_dip)
        else:
            incl_rad = np.radians(180 + collar_dip)
        
        # Calculate displacement
        horiz_component = max_depth * np.sin(incl_rad)
        delta_x = horiz_component * np.sin(azimuth_rad)
        delta_y = horiz_component * np.cos(azimuth_rad)
        delta_z = -max_depth * np.cos(incl_rad)
        
        return [
            [east, north, elev],                           # Collar
            [east + delta_x, north + delta_y, elev + delta_z]  # Toe
        ]
    
    trajectory = [[east, north, elev]]  # Commence au collar
    
    survey_sorted = survey_df.sort_values("DEPTH").reset_index(drop=True)
    
    current_x = east
    current_y = north
    current_z = elev
    prev_depth = 0.0
    
    for _, survey_row in survey_sorted.iterrows():
        depth = float(survey_row["DEPTH"])
        azimuth_deg = float(survey_row["AZIMUTH"])
        dip_deg = float(survey_row["DIP"])
        
        interval_length = depth - prev_depth
        
        if interval_length <= 0:
            continue
        
        azimuth_rad = np.radians(azimuth_deg)
      
        if dip_deg >= 0:
            incl_rad = np.radians(dip_deg)
        else:
            incl_rad = np.radians(180 + dip_deg)
        
        horiz_component = interval_length * np.sin(incl_rad)
        delta_x = horiz_component * np.sin(azimuth_rad)
        delta_y = horiz_component * np.cos(azimuth_rad)
        delta_z = -interval_length * np.cos(incl_rad)
        
        current_x += delta_x
        current_y += delta_y
        current_z += delta_z
        
        trajectory.append([current_x, current_y, current_z])
        prev_depth = depth
    
    if len(trajectory) < 2:
        max_depth = float(collar.get("MAX_DEPTH", 100.0))
        trajectory.append([east, north, elev - max_depth])
    
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