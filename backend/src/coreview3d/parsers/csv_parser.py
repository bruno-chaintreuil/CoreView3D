import pandas as pd
import io
from typing import BinaryIO, Dict, List
import logging

logger = logging.getLogger("csv_parser")


class DrillholeParser:
  
    COLLAR_COLUMN_MAPPING = {
        # Hole ID 
        'holeid': 'HOLEID',
        'hole_id': 'HOLEID',
        'holeid': 'HOLEID',
        'hole id': 'HOLEID',
        'hole-id': 'HOLEID',
        'dhid': 'HOLEID',
        'id': 'HOLEID',
        
        # East
        'east': 'EAST',
        'x': 'EAST',
        'easting': 'EAST',
        'eastings': 'EAST',
        'xcoord': 'EAST',
        'x_coord': 'EAST',
        'xcoord': 'EAST',
        
        # North
        'north': 'NORTH',
        'y': 'NORTH',
        'northing': 'NORTH',
        'northings': 'NORTH',
        'ycoord': 'NORTH',
        'y_coord': 'NORTH',
        'ycoord': 'NORTH',
        
        # Elevation
        'elev': 'ELEV',
        'elevation': 'ELEV',
        'z': 'ELEV',
        'rl': 'ELEV',
        'alt': 'ELEV',
        'altitude': 'ELEV',
        'zcoord': 'ELEV',
        'z_coord': 'ELEV',
        
        # Max Depth
        'max_depth': 'MAX_DEPTH',
        'maxdepth': 'MAX_DEPTH',
        'max depth': 'MAX_DEPTH',
        'depth': 'MAX_DEPTH',
        'end_depth': 'MAX_DEPTH',
        'enddepth': 'MAX_DEPTH',
        'final_depth': 'MAX_DEPTH',
        'finaldepth': 'MAX_DEPTH',
        'total_depth': 'MAX_DEPTH',
        'totaldepth': 'MAX_DEPTH',
    }
    
    SURVEY_COLUMN_MAPPING = {
        # Hole ID
        'holeid': 'HOLEID',
        'hole_id': 'HOLEID',
        'hole id': 'HOLEID',
        'dhid': 'HOLEID',
        'id': 'HOLEID',
        
        # Depth
        'depth': 'DEPTH',
        'at': 'DEPTH',
        'at_depth': 'DEPTH',
        'survey_depth': 'DEPTH',
        'surveydepth': 'DEPTH',
        
        # Azimuth
        'azimuth': 'AZIMUTH',
        'az': 'AZIMUTH',
        'bearing': 'AZIMUTH',
        'azim': 'AZIMUTH',
        
        # Dip
        'dip': 'DIP',
        'inclination': 'DIP',
        'incl': 'DIP',
        'plunge': 'DIP',
    }
    
    ASSAYS_COLUMN_MAPPING = {
        # Hole ID
        'holeid': 'HOLEID',
        'hole_id': 'HOLEID',
        'hole id': 'HOLEID',
        'dhid': 'HOLEID',
        'id': 'HOLEID',
        
        # From
        'from': 'FROM',
        'from_depth': 'FROM',
        'fromdepth': 'FROM',
        'from depth': 'FROM',
        'start': 'FROM',
        'start_depth': 'FROM',
        
        # To
        'to': 'TO',
        'to_depth': 'TO',
        'todepth': 'TO',
        'to depth': 'TO',
        'end': 'TO',
        'end_depth': 'TO',
        
        # Lithology
        'lithology': 'LITHOLOGY',
        'lith': 'LITHOLOGY',
        'rock': 'LITHOLOGY',
        'rocktype': 'LITHOLOGY',
        'rock_type': 'LITHOLOGY',
        'litho': 'LITHOLOGY',
        
        # Au
        'au': 'AU_PPM',
        'au_ppm': 'AU_PPM',
        'auppm': 'AU_PPM',
        'gold': 'AU_PPM',
        'gold_ppm': 'AU_PPM',
        'au_g/t': 'AU_PPM',
        'au_gt': 'AU_PPM',
        'au_gpt': 'AU_PPM',
        
        # Cu
        'cu': 'CU_PCT',
        'cu_pct': 'CU_PCT',
        'cupct': 'CU_PCT',
        'cu_%': 'CU_PCT',
        'copper': 'CU_PCT',
        'copper_pct': 'CU_PCT',
        'cu_percent': 'CU_PCT',
    }
    
    def _normalize_column_name(self, col: str) -> str:
        normalized = col.lower().strip()
        normalized = normalized.replace(' ', '').replace('_', '').replace('-', '')
        return normalized
    
    def _apply_column_mapping(
        self, 
        df: pd.DataFrame, 
        mapping: Dict[str, str],
        required_columns: List[str],
        data_type: str
    ) -> pd.DataFrame:
        logger.debug(f"📊 Loaded {data_type} file with {len(df)} rows")
        logger.debug(f"   Original columns: {df.columns.tolist()}")
        
        rename_dict = {}
        for original_col in df.columns:
            normalized = self._normalize_column_name(original_col)
            
            if normalized in mapping:
                standard_name = mapping[normalized]
                if original_col != standard_name:  # Seulement si différent
                    rename_dict[original_col] = standard_name
        
        if rename_dict:
            logger.debug(f"✓ Normalizing {data_type} columns: {rename_dict}")
            df = df.rename(columns=rename_dict)
        else:
            logger.debug(f"✓ No normalization needed for {data_type}")
        
        logger.debug(f"   Final columns: {df.columns.tolist()}")
        
        missing = set(required_columns) - set(df.columns)
        if missing:
            available_cols = df.columns.tolist()
            
            error_msg = (
                f"{data_type} CSV missing required columns: {missing}.\n"
                f"Found columns: {available_cols}\n"
                f"Supported variations:\n"
            )
            
            for missing_col in missing:
                variations = [k for k, v in mapping.items() if v == missing_col]
                error_msg += f"  - {missing_col}: {', '.join(variations[:5])}...\n"
            
            raise ValueError(error_msg)
        
        return df
    
    def parse_collar(self, file: BinaryIO) -> pd.DataFrame:
        try:
            df = pd.read_csv(file)
            
            if df.empty:
                raise ValueError("Collar CSV is empty")
            
            required = ['HOLEID', 'EAST', 'NORTH', 'ELEV']
            
            df = self._apply_column_mapping(
                df, 
                self.COLLAR_COLUMN_MAPPING,
                required,
                "Collar"
            )
            
            df['HOLEID'] = df['HOLEID'].astype(str).str.strip()
            df['EAST'] = pd.to_numeric(df['EAST'], errors='coerce')
            df['NORTH'] = pd.to_numeric(df['NORTH'], errors='coerce')
            df['ELEV'] = pd.to_numeric(df['ELEV'], errors='coerce')
            
            if 'MAX_DEPTH' in df.columns:
                df['MAX_DEPTH'] = pd.to_numeric(df['MAX_DEPTH'], errors='coerce')
            
            initial_len = len(df)
            df = df.dropna(subset=['HOLEID', 'EAST', 'NORTH', 'ELEV'])
            
            if len(df) < initial_len:
                logger.warning(f"⚠️ Removed {initial_len - len(df)} rows with missing values")
            
            if df.empty:
                raise ValueError("No valid collar records after cleaning")
            
            logger.info(f"✅ Parsed {len(df)} collar records")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing collar CSV: {e}")
            raise ValueError(f"Error parsing collar CSV: {e}")
    
    def parse_survey(self, file: BinaryIO) -> pd.DataFrame:
        try:
            df = pd.read_csv(file)
            
            if df.empty:
                raise ValueError("Survey CSV is empty")
            
            required = ['HOLEID', 'DEPTH', 'AZIMUTH', 'DIP']
            
            df = self._apply_column_mapping(
                df,
                self.SURVEY_COLUMN_MAPPING,
                required,
                "Survey"
            )
            
            df['HOLEID'] = df['HOLEID'].astype(str).str.strip()
            df['DEPTH'] = pd.to_numeric(df['DEPTH'], errors='coerce')
            df['AZIMUTH'] = pd.to_numeric(df['AZIMUTH'], errors='coerce')
            df['DIP'] = pd.to_numeric(df['DIP'], errors='coerce')
            
            # Supprimer les lignes avec des valeurs manquantes
            initial_len = len(df)
            df = df.dropna(subset=['HOLEID', 'DEPTH', 'AZIMUTH', 'DIP'])
            
            if len(df) < initial_len:
                logger.warning(f"⚠️ Removed {initial_len - len(df)} rows with missing values")
            
            if df.empty:
                raise ValueError("No valid survey records after cleaning")
            
            logger.info(f"✅ Parsed {len(df)} survey records")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing survey CSV: {e}")
            raise ValueError(f"Error parsing survey CSV: {e}")
    
    def parse_assays(self, file: BinaryIO) -> pd.DataFrame:
        try:
            df = pd.read_csv(file)
            
            if df.empty:
                raise ValueError("Assays CSV is empty")
            
            required = ['HOLEID', 'FROM', 'TO']
            
            df = self._apply_column_mapping(
                df,
                self.ASSAYS_COLUMN_MAPPING,
                required,
                "Assays"
            )
            
            df['HOLEID'] = df['HOLEID'].astype(str).str.strip()
            df['FROM'] = pd.to_numeric(df['FROM'], errors='coerce')
            df['TO'] = pd.to_numeric(df['TO'], errors='coerce')
            
            if 'LITHOLOGY' in df.columns:
                df['LITHOLOGY'] = df['LITHOLOGY'].astype(str).str.strip().str.upper()
            
            if 'AU_PPM' in df.columns:
                df['AU_PPM'] = pd.to_numeric(df['AU_PPM'], errors='coerce')
            
            if 'CU_PCT' in df.columns:
                df['CU_PCT'] = pd.to_numeric(df['CU_PCT'], errors='coerce')
            
            initial_len = len(df)
            df = df.dropna(subset=['HOLEID', 'FROM', 'TO'])
            
            if len(df) < initial_len:
                logger.warning(f"⚠️ Removed {initial_len - len(df)} rows with missing values")
            
            if df.empty:
                raise ValueError("No valid assay records after cleaning")
            
            logger.info(f"✅ Parsed {len(df)} assay intervals")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing assays CSV: {e}")
            raise ValueError(f"Error parsing assays CSV: {e}")
    
    def get_supported_variations(self, data_type: str) -> List[str]:
        mapping = {
            'collar': self.COLLAR_COLUMN_MAPPING,
            'survey': self.SURVEY_COLUMN_MAPPING,
            'assays': self.ASSAYS_COLUMN_MAPPING
        }
        
        if data_type not in mapping:
            raise ValueError(f"Unknown data type: {data_type}. Must be one of: {list(mapping.keys())}")
        
        return list(mapping[data_type].keys())