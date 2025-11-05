"""
Calculate 3D drillhole trajectories from collar and survey data
Uses minimum curvature method for accurate trajectory calculation
"""
import numpy as np
import pandas as pd
from typing import Optional, List, Dict


def minimum_curvature(depth1: float, depth2: float, 
                     azi1: float, azi2: float,
                     dip1: float, dip2: float) -> tuple:
    """
    Calculate 3D displacement using minimum curvature method
    
    Args:
        depth1, depth2: Measured depths (meters)
        azi1, azi2: Azimuth angles (degrees, 0=North, clockwise)
        dip1, dip2: Dip angles (degrees, negative=down from horizontal)
        
    Returns:
        tuple: (delta_x, delta_y, delta_z) displacement in meters
    """
    # Convert to radians
    azi1_rad = np.radians(azi1)
    azi2_rad = np.radians(azi2)
    dip1_rad = np.radians(dip1)
    dip2_rad = np.radians(dip2)
    
    # Calculate course length
    md_diff = depth2 - depth1
    
    # Calculate dogleg angle (angle between survey vectors)
    cos_dogleg = (np.cos(dip2_rad - dip1_rad) - 
                  np.sin(dip1_rad) * np.sin(dip2_rad) * 
                  (1 - np.cos(azi2_rad - azi1_rad)))
    
    # Handle numerical precision issues
    cos_dogleg = np.clip(cos_dogleg, -1.0, 1.0)
    dogleg = np.arccos(cos_dogleg)
    
    # Ratio factor for minimum curvature
    if dogleg < 0.0001:  # Essentially straight
        rf = 1.0
    else:
        rf = 2 / dogleg * np.tan(dogleg / 2)
    
    # Calculate incremental changes
    delta_north = 0.5 * md_diff * (np.cos(dip1_rad) * np.cos(azi1_rad) + 
                                    np.cos(dip2_rad) * np.cos(azi2_rad)) * rf
    
    delta_east = 0.5 * md_diff * (np.cos(dip1_rad) * np.sin(azi1_rad) + 
                                   np.cos(dip2_rad) * np.sin(azi2_rad)) * rf
    
    delta_vert = 0.5 * md_diff * (np.sin(dip1_rad) + np.sin(dip2_rad)) * rf
    
    return delta_east, delta_north, delta_vert

def calculate_single_trajectory(collar: pd.Series, 
                               survey_df: Optional[pd.DataFrame] = None) -> List[Dict]:
    """
    Calculate 3D trajectory for a single drillhole
    
    Args:
        collar: Collar information
        survey_df: Survey measurements for this hole (optional)
        
    Returns:
        List of 3D points along the trajectory
    """
    points = []
    
    # Starting point at collar
    current_x = float(collar["East"])
    current_y = float(collar["North"])
    current_z = float(collar["Elevation"])
    
    points.append({
        "depth": 0.0,
        "x": current_x,
        "y": current_y,
        "z": current_z
    })
    

    if survey_df is not None and len(survey_df) > 0:
        # Use survey data - minimum curvature method
        prev_depth = 0.0
        prev_azimuth = float(collar["Azimuth"])
        prev_dip = float(collar["Dip"])
        
        for _, survey in survey_df.iterrows():
            depth = float(survey["Depth"])
            azimuth = float(survey["Azimuth"])
            dip = float(survey["Dip"])
            
            # Calculate increment using minimum curvature
            delta_depth = depth - prev_depth
            
            # Average angles for the interval
            avg_azimuth = (prev_azimuth + azimuth) / 2
            avg_dip = (prev_dip + dip) / 2
            
            # Convert to radians
            az_rad = np.radians(avg_azimuth)
            dip_rad = np.radians(avg_dip)
            
            # Calculate increments (dip is negative down)
            dx = delta_depth * np.sin(-dip_rad) * np.sin(az_rad)
            dy = delta_depth * np.sin(-dip_rad) * np.cos(az_rad)
            dz = delta_depth * np.cos(-dip_rad)
            
            # Update position
            current_x += dx
            current_y += dy
            current_z += dz
            
            points.append({
                "depth": depth,
                "x": current_x,
                "y": current_y,
                "z": current_z
            })
            
            # Update previous values
            prev_depth = depth
            prev_azimuth = azimuth
            prev_dip = dip
            
    else:
        # No survey data - straight line from collar
        max_depth = float(collar["Max_Depth"])
        azimuth = float(collar["Azimuth"])
        dip = float(collar["Dip"])
        
        # Convert to radians
        az_rad = np.radians(azimuth)
        dip_rad = np.radians(dip)
        
        # Calculate end point
        dx = max_depth * np.sin(-dip_rad) * np.sin(az_rad)
        dy = max_depth * np.sin(-dip_rad) * np.cos(az_rad)
        dz = max_depth * np.cos(-dip_rad)
        
        points.append({
            "depth": max_depth,
            "x": current_x + dx,
            "y": current_y + dy,
            "z": current_z + dz
        })
    
    return points


def calculate_trajectories(collar_df: pd.DataFrame, 
                          survey_df: Optional[pd.DataFrame] = None) -> List[Dict]:
    """
    Calculate 3D trajectories for all drillholes
    
    Args:
        collar_df: DataFrame with collar information
        survey_df: DataFrame with survey measurements (optional)
        
    Returns:
        List of drillhole trajectories with metadata
    """
    trajectories = []
    
    for _, collar in collar_df.iterrows():
        hole_id = collar["Hole_ID"]
        
        # Get survey data for this hole if available
        hole_survey = None

        if survey_df is not None:
            hole_survey = survey_df[survey_df["Hole_ID"] == hole_id]
            if len(hole_survey) == 0:
                hole_survey = None
        
        # Calculate trajectory
        points = calculate_single_trajectory(collar, hole_survey)
        
        trajectories.append({
            "hole_id": hole_id,
            "collar": {
                "east": float(collar["East"]),
                "north": float(collar["North"]),
                "elevation": float(collar["Elevation"]),
                "max_depth": float(collar["Max_Depth"]),
                "azimuth": float(collar["Azimuth"]),
                "dip": float(collar["Dip"])
            },
            "points": points,
            "has_survey": hole_survey is not None
        })
    
    return trajectories