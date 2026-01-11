import numpy as np
from typing import List, Tuple
import pandas as pd

def project_drillhole_to_section(
    trajectory_points: List[dict],
    xy_start: np.ndarray,
    xy_stop: np.ndarray,
) -> List[dict]:
    section_vec = xy_stop - xy_start
    section_length = np.linalg.norm(section_vec)
    section_dir = section_vec / section_length
    
    projected_points = []
    
    for point in trajectory_points:
        point_xy = np.array([point['x'], point['y']])
        
        vec_to_point = point_xy - xy_start
        distance_along = np.dot(vec_to_point, section_dir)
        
        projected_points.append({
            'x': distance_along,
            'z': point['z']
        })
    
    return projected_points


def calculate_simple_cross_section(
    trajectories: List[dict],
    hole_ids: List[str],
    xy_start: Tuple[float, float],
    xy_stop: Tuple[float, float],
    tolerance: float = 100.0
) -> dict:
    start = np.array(xy_start)
    stop = np.array(xy_stop)
    
    section_vec = stop - start
    section_length = np.linalg.norm(section_vec)
    section_dir = section_vec / section_length
    
    perpendicular = np.array([-section_dir[1], section_dir[0]])
    
    result_drillholes = []
    
    for traj in trajectories:
        if traj['hole_id'] not in hole_ids:
            continue
        
        collar_xy = np.array([traj['collar']['east'], traj['collar']['north']])
        vec_to_collar = collar_xy - start
        distance_perp = abs(np.dot(vec_to_collar, perpendicular))
        
        if distance_perp > tolerance:
            continue
        
        projected = project_drillhole_to_section(
            traj['points'],
            start,
            stop
        )
        
        result_drillholes.append({
            'hole_id': traj['hole_id'],
            'trace': projected
        })
    
    return {
        'xy_start': xy_start,
        'xy_stop': xy_stop,
        'drillholes': result_drillholes
    }