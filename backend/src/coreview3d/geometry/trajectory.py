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

    # Starting collar coordinates
    x = float(collar["East"])
    y = float(collar["North"])
    z = float(collar["Elevation"])

    points.append({"depth": 0.0, "x": x, "y": y, "z": z})

    if survey_df is not None and len(survey_df) > 0:

        prev_depth = 0.0
        prev_az = float(collar["Azimuth"])
        prev_dip = float(collar["Dip"])

        for _, row in survey_df.iterrows():
            depth = float(row["Depth"])
            az = float(row["Azimuth"])
            dip = float(row["Dip"])

            # Length of segment
            d = depth - prev_depth

            # Averaged orientation for the interval
            avg_az = np.radians((prev_az + az) / 2)
            avg_dip = (prev_dip + dip) / 2

            # Convert dip to inclination (angle from vertical)
            incl = np.radians(90 + avg_dip)

            # Orientation: Y+ = North, X+ = East, Z vertical
            dx = d * np.sin(incl) * np.sin(avg_az)
            dy = d * np.sin(incl) * np.cos(avg_az)
            dz = d * np.cos(incl)

            # Update coordinates
            x += dx
            y += dy
            z += dz

            points.append({"depth": depth, "x": x, "y": y, "z": z})

            prev_depth = depth
            prev_az = az
            prev_dip = dip

    else:
      
        max_depth = float(collar["Max_Depth"])
        az = float(collar["Azimuth"])
        dip = float(collar["Dip"])

        az_rad = np.radians(az)
        incl = np.radians(90 + dip)

        dx = max_depth * np.sin(incl) * np.sin(az_rad)
        dy = max_depth * np.sin(incl) * np.cos(az_rad)
        dz = max_depth * np.cos(incl)

        points.append({
            "depth": max_depth,
            "x": x + dx,
            "y": y + dy,
            "z": z + dz
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

    results = []

    for _, collar in collar_df.iterrows():
        hole_id = collar["Hole_ID"]

        # Extract surveys for this hole, if any
        sub = None
        if survey_df is not None:
            subset = survey_df[survey_df["Hole_ID"] == hole_id]
            if len(subset) > 0:
                sub = subset

        # Compute the trajectory
        pts = calculate_single_trajectory(collar, sub)

        results.append({
            "hole_id": hole_id,
            "collar": {
                "east": float(collar["East"]),
                "north": float(collar["North"]),
                "elevation": float(collar["Elevation"]),
                "max_depth": float(collar["Max_Depth"]),
                "azimuth": float(collar["Azimuth"]),
                "dip": float(collar["Dip"])
            },
            "points": pts,
            "has_survey": sub is not None
        })

    return results
