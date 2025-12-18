import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger("cross_section_geometry")


def calculate_line_from_holes(collar_df: pd.DataFrame, hole_ids: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcule une ligne de section optimale à partir des collars sélectionnés.
    Utilise une régression linéaire (PCA) pour trouver la meilleure ligne.
    
    Args:
        collar_df: DataFrame avec colonnes ['HOLEID', 'EAST', 'NORTH', 'ELEV']
        hole_ids: Liste des IDs de trous à inclure
    
    Returns:
        (point_A, point_B): Tuple de deux arrays numpy [East, North]
    """
    # Filtrer les collars
    selected = collar_df[collar_df['HOLEID'].isin(hole_ids)]
    
    if len(selected) < 2:
        raise ValueError(f"Need at least 2 holes, got {len(selected)}")
    
    # Extraire les coordonnées 2D
    coords = selected[['EAST', 'NORTH']].values
    
    # Centroïde
    centroid = coords.mean(axis=0)
    
    # PCA manuelle (pour trouver la direction principale)
    centered = coords - centroid
    cov_matrix = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    # Premier vecteur propre = direction principale
    principal_direction = eigenvectors[:, np.argmax(eigenvalues)]
    
    # Projeter tous les points sur cette ligne
    projections = centered @ principal_direction
    
    # Trouver les extrémités
    min_proj = projections.min()
    max_proj = projections.max()
    
    # Étendre un peu pour inclure tous les trous
    margin = (max_proj - min_proj) * 0.1
    min_proj -= margin
    max_proj += margin
    
    # Calculer les points A et B
    point_A = centroid + min_proj * principal_direction
    point_B = centroid + max_proj * principal_direction
    
    logger.info(f"Calculated section line from {len(hole_ids)} holes: {point_A} to {point_B}")
    
    return point_A, point_B


def calculate_cross_section(
    collar_df: pd.DataFrame,
    survey_df: Optional[pd.DataFrame],
    assays_df: Optional[pd.DataFrame],
    hole_ids: Optional[List[str]],
    point_A: np.ndarray,
    point_B: np.ndarray,
    tolerance: float = 100.0
) -> Dict[str, Any]:
    # Direction et longueur de la ligne
    direction = point_B - point_A
    length = np.linalg.norm(direction)
    
    if length < 1.0:
        raise ValueError("Section line too short (< 1m)")
    
    direction_norm = direction / length
    
    # Azimuth de la section
    azimuth = np.degrees(np.arctan2(direction[0], direction[1])) % 360
    
    # Filtrer les trous
    if hole_ids:
        working_df = collar_df[collar_df['HOLEID'].isin(hole_ids)].copy()
    else:
        working_df = collar_df.copy()
    
    drillholes_data = []
    
    for _, collar in working_df.iterrows():
        hole_id = collar['HOLEID']
        collar_pos = np.array([collar['EAST'], collar['NORTH']])
        collar_elev = collar['ELEV']
        
        # Calculer la distance perpendiculaire à la ligne
        vec_to_collar = collar_pos - point_A
        distance_along = np.dot(vec_to_collar, direction_norm)
        closest_point = point_A + distance_along * direction_norm
        distance_from = np.linalg.norm(collar_pos - closest_point)
        
        # Vérifier la tolérance
        if distance_from > tolerance:
            continue
        
        # Construire la trace du trou
        trace = _calculate_hole_trace(
            hole_id=hole_id,
            collar=collar,
            survey_df=survey_df,
            point_A=point_A,
            direction_norm=direction_norm
        )
        
        if not trace:
            continue
        
        # Récupérer les intervalles (assays)
        intervals = _get_hole_intervals(hole_id, assays_df) if assays_df is not None else None
        
        drillholes_data.append({
            "hole_id": hole_id,
            "distance_from_line": float(distance_from),
            "distance_along_line": float(distance_along),
            "collar_elevation": float(collar_elev),
            "trace": trace,
            "intervals": intervals
        })
    
    if not drillholes_data:
        raise ValueError(f"No drillholes found within {tolerance}m tolerance")
    
    # Calculer les bounds pour le viewport
    all_distances = [h["distance_along_line"] for h in drillholes_data]
    all_elevations = [p["y_elevation"] for h in drillholes_data for p in h["trace"]]
    
    bounds = {
        "min_distance": float(min(all_distances)),
        "max_distance": float(max(all_distances)),
        "min_elevation": float(min(all_elevations)),
        "max_elevation": float(max(all_elevations))
    }
    
    logger.info(f"Cross-section calculated: {len(drillholes_data)} holes, bounds={bounds}")
    
    return {
        "section_line": {
            "point_A": [float(point_A[0]), float(point_A[1]), 0.0],
            "point_B": [float(point_B[0]), float(point_B[1]), 0.0],
            "direction": [float(direction_norm[0]), float(direction_norm[1]), 0.0],
            "length": float(length),
            "azimuth": float(azimuth)
        },
        "drillholes": drillholes_data,
        "bounds": bounds
    }


def _calculate_hole_trace(
    hole_id: str,
    collar: pd.Series,
    survey_df: Optional[pd.DataFrame],
    point_A: np.ndarray,
    direction_norm: np.ndarray
) -> List[Dict[str, float]]:
    """
    Calcule la trace 2D projetée d'un trou de forage.
    
    Returns:
        Liste de points [{depth_along_hole, x_along_section, y_elevation}]
    """
    collar_pos = np.array([collar['EAST'], collar['NORTH']], dtype=float)
    collar_elev = collar['ELEV']
    
    # Si pas de survey, trou vertical simple
    if survey_df is None or hole_id not in survey_df['HOLEID'].values:
        max_depth = collar.get('MAX_DEPTH', 100.0)
        
        # Projection du collar sur la ligne de section
        vec_to_collar = collar_pos - point_A
        distance_along = np.dot(vec_to_collar, direction_norm)
        
        return [
            {
                "depth_along_hole": 0.0,
                "x_along_section": float(distance_along),
                "y_elevation": float(collar_elev)
            },
            {
                "depth_along_hole": float(max_depth),
                "x_along_section": float(distance_along),
                "y_elevation": float(collar_elev - max_depth)
            }
        ]
    
    hole_survey = survey_df[survey_df['HOLEID'] == hole_id].sort_values('DEPTH')
    
    trace_points = []
    current_pos = collar_pos.copy()
    current_elev = float(collar_elev)
    prev_depth = 0.0
    
    for _, survey in hole_survey.iterrows():
        depth = survey['DEPTH']
        azimuth = np.radians(survey['AZIMUTH'])
        dip = survey['DIP']  # Dip positif = vers le bas
        
        # Longueur de l'intervalle
        interval_length = depth - prev_depth
        
        if interval_length <= 0:
            continue
        
        # Déplacement 3D (simplified: assume straight segments)
        dip_rad = np.radians(90 - dip)  # Convertir dip en angle depuis l'horizontale
        
        delta_east = interval_length * np.sin(dip_rad) * np.sin(azimuth)
        delta_north = interval_length * np.sin(dip_rad) * np.cos(azimuth)
        delta_elev = -interval_length * np.cos(dip_rad)
        
        current_pos += np.array([delta_east, delta_north])
        current_elev += delta_elev
        
        # Projection sur la ligne de section
        vec_to_point = current_pos - point_A
        distance_along = np.dot(vec_to_point, direction_norm)
        
        trace_points.append({
            "depth_along_hole": float(depth),
            "x_along_section": float(distance_along),
            "y_elevation": float(current_elev)
        })
        
        prev_depth = depth
    
    # Ajouter le collar au début
    vec_to_collar = collar_pos - point_A
    collar_distance = np.dot(vec_to_collar, direction_norm)
    
    trace_points.insert(0, {
        "depth_along_hole": 0.0,
        "x_along_section": float(collar_distance),
        "y_elevation": float(collar_elev)
    })
    
    return trace_points


def _get_hole_intervals(hole_id: str, assays_df: pd.DataFrame) -> Optional[List[Dict[str, Any]]]:
    """
    Récupère les intervalles d'assays pour un trou.
    
    Returns:
        Liste de dicts [{from, to, lithology, au_ppm, cu_pct, ...}]
    """
    hole_assays = assays_df[assays_df['HOLEID'] == hole_id]
    
    if hole_assays.empty:
        return None
    
    intervals = []
    for _, row in hole_assays.iterrows():
        interval = {
            "from": float(row['FROM']),
            "to": float(row['TO'])
        }
        
        # Ajouter les colonnes optionnelles si présentes
        if 'LITHOLOGY' in row and pd.notna(row['LITHOLOGY']):
            interval['lithology'] = str(row['LITHOLOGY'])
        
        if 'AU_PPM' in row and pd.notna(row['AU_PPM']):
            interval['au_ppm'] = float(row['AU_PPM'])
        
        if 'CU_PCT' in row and pd.notna(row['CU_PCT']):
            interval['cu_pct'] = float(row['CU_PCT'])
        
        intervals.append(interval)
    
    return intervals if intervals else None