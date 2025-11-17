"""
CSV parser for drillhole data with validation and column normalization
"""
import pandas as pd
import io
from typing import Union, BinaryIO, Optional

def normalize_column_names(df: pd.DataFrame, table_type: str) -> pd.DataFrame:
    """
    Normalise les noms de colonnes pour gérer les variations
    """
    # Strip whitespace
    df.columns = df.columns.str.strip()
    
    # Direct mapping (case-insensitive)
    mapping_table = {
        'collar': {
            'holeid': 'Hole_ID', 'hole_id': 'Hole_ID', 'dhid': 'Hole_ID', 'bh_id': 'Hole_ID',
            'easting': 'East', 'x': 'East', 'utmx': 'East',
            'northing': 'North', 'y': 'North', 'utmy': 'North',
            'elevation': 'Elevation', 'elev': 'Elevation', 'z': 'Elevation', 'rl': 'Elevation',
            'maxdepth': 'Max_Depth', 'depth': 'Max_Depth', 'length': 'Max_Depth', 'eoh': 'Max_Depth',
            'azi': 'Azimuth', 'azimut': 'Azimuth', 'bearing': 'Azimuth',
            'inclination': 'Dip', 'incl': 'Dip', 'plunge': 'Dip',
        },
        'survey': {
            'holeid': 'Hole_ID', 'hole_id': 'Hole_ID', 'dhid': 'Hole_ID', 'bh_id': 'Hole_ID',
            'length': 'Depth', 'depth_m': 'Depth', 'md': 'Depth', 'along_hole': 'Depth',
            'azi': 'Azimuth', 'azimut': 'Azimuth', 'bearing': 'Azimuth',
            'inclination': 'Dip', 'incl': 'Dip', 'plunge': 'Dip',
        },
        'assay': {
            'holeid': 'Hole_ID', 'hole_id': 'Hole_ID', 'dhid': 'Hole_ID', 'bh_id': 'Hole_ID',
            'from_m': 'From', 'from_depth': 'From', 'depth_from': 'From',
            'to_m': 'To', 'to_depth': 'To', 'depth_to': 'To',
            'lith': 'Lithology', 'litho': 'Lithology', 'rock_type': 'Lithology',
        }
    }
    
    if table_type not in mapping_table:
        return df
    
    # Create rename map (case-insensitive)
    rename_map = {}
    for col in df.columns:
        col_lower = col.lower().replace('_', '').replace('-', '').replace(' ', '')
        for key, value in mapping_table[table_type].items():
            key_lower = key.lower().replace('_', '').replace('-', '').replace(' ', '')
            if col_lower == key_lower:
                if col != value:  # Only rename if different
                    rename_map[col] = value
                break
    
    if rename_map:
        print(f"✓ Normalizing {table_type} columns: {rename_map}")
        df = df.rename(columns=rename_map)
    
    print(f"   Final columns: {list(df.columns)}")
    return df

class DrillholeParser:
    """Parser for mining drillhole CSV files with automatic column normalization"""
    
    COLLAR_REQUIRED = ["Hole_ID", "East", "North", "Elevation"]
    COLLAR_OPTIONAL = ["Max_Depth", "Azimuth", "Dip", "Date", "Project"]
    
    SURVEY_REQUIRED = ["Hole_ID", "Depth", "Azimuth", "Dip"]
    ASSAY_REQUIRED = ["Hole_ID", "From", "To"]
    
    def __init__(self):
        pass
    
    def _validate_columns(self, df: pd.DataFrame, required_cols: list, table_name: str, optional_cols: list = None) -> pd.DataFrame:
        """
        Validate that required columns exist in dataframe
        
        Args:
            df: DataFrame to validate
            required_cols: List of required column names
            table_name: Name of the table (for error messages)
            optional_cols: List of optional column names
            
        Returns:
            Validated DataFrame
            
        Raises:
            ValueError: If required columns are missing
        """
        missing_required = set(required_cols) - set(df.columns)
        if missing_required:
            raise ValueError(
                f"{table_name} CSV missing required columns: {missing_required}. "
                f"Found columns: {list(df.columns)}. "
                f"Please ensure your CSV has the correct column names or use standard variations."
            )
        
        # Log optional columns that are present/missing
        if optional_cols:
            present_optional = set(optional_cols) & set(df.columns)
            missing_optional = set(optional_cols) - set(df.columns)
            if present_optional:
                print(f"   Optional columns present: {list(present_optional)}")
            if missing_optional:
                print(f"   Optional columns missing: {list(missing_optional)}")
        
        return df
    
    def parse_collar(self, file: Union[str, BinaryIO]) -> pd.DataFrame:
        """
        Parse collar CSV file with automatic column normalization
        
        Required columns: Hole_ID, East, North, Elevation
        Optional columns: Max_Depth, Azimuth, Dip, Date, Project
        
        If Max_Depth is missing, it will be calculated from survey data later.
        If Azimuth/Dip are missing, default values will be used.
        
        Args:
            file: File path or file-like object
            
        Returns:
            DataFrame with normalized collar data
            
        Raises:
            ValueError: If file cannot be parsed or required columns are missing
        """
        try:
            df = pd.read_csv(file)
            print(f"📊 Loaded collar file with {len(df)} rows")
            print(f"   Original columns: {list(df.columns)}")
            
            # Normalize column names
            df = normalize_column_names(df, 'collar')
            
            # Validate required columns only
            df = self._validate_columns(df, self.COLLAR_REQUIRED, "Collar", self.COLLAR_OPTIONAL)
            
            # Validate numeric columns that are present
            numeric_cols = ["East", "North", "Elevation"]
            optional_numeric = ["Max_Depth", "Azimuth", "Dip"]
            
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            for col in optional_numeric:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Check for NaN values in required columns
            if df[numeric_cols].isna().any().any():
                nan_counts = df[numeric_cols].isna().sum()
                raise ValueError(
                    f"Collar file contains non-numeric values in required numeric columns. "
                    f"NaN counts: {nan_counts[nan_counts > 0].to_dict()}"
                )
            
            # Add default values for missing optional columns
            if "Max_Depth" not in df.columns:
                print("   ⚠️ Max_Depth not provided - will be calculated from survey data")
                df["Max_Depth"] = 0.0  # Placeholder, will be updated later
            
            if "Azimuth" not in df.columns:
                print("   ⚠️ Azimuth not provided - using default value 0° (North)")
                df["Azimuth"] = 0.0
            
            if "Dip" not in df.columns:
                print("   ⚠️ Dip not provided - using default value -90° (Vertical)")
                df["Dip"] = -90.0                
            elif "Dip" in df.columns:
                if (df["Dip"] > 0).all():
                    print("   ⚠️ Dips are positive - Flipping")
                    df["Dip"] = -df["Dip"]
            
            
            # Validate value ranges for columns that exist
            if "Dip" in df.columns and not df["Dip"].isna().all():
                if (df["Dip"] > 0).any() or (df["Dip"] < -90).any():
                    raise ValueError(
                        "Dip must be between -90 and 0 degrees (negative down). "
                        f"Found values: min={df['Dip'].min()}, max={df['Dip'].max()}"
                    )
            
            if "Azimuth" in df.columns and not df["Azimuth"].isna().all():
                if (df["Azimuth"] < 0).any() or (df["Azimuth"] >= 360).any():
                    raise ValueError(
                        "Azimuth must be between 0 and 360 degrees. "
                        f"Found values: min={df['Azimuth'].min()}, max={df['Azimuth'].max()}"
                    )
            
            print(f"✓ Collar file parsed successfully: {len(df)} drillholes")
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("Collar CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing collar CSV file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing collar CSV: {str(e)}")
    
    def parse_survey(self, file: Union[str, BinaryIO]) -> pd.DataFrame:
        """
        Parse survey (deviation) CSV file with automatic column normalization
        
        Args:
            file: File path or file-like object
            
        Returns:
            DataFrame with normalized survey data
        """
        try:
            df = pd.read_csv(file)
            print(f"📊 Loaded survey file with {len(df)} rows")
            print(f"   Original columns: {list(df.columns)}")
            
            # Normalize column names
            df = normalize_column_names(df, 'survey')
            
            # Validate required columns
            df = self._validate_columns(df, self.SURVEY_REQUIRED, "Survey")
            
            # Validate numeric columns
            numeric_cols = ["Depth", "Azimuth", "Dip"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            if df[numeric_cols].isna().any().any():
                nan_counts = df[numeric_cols].isna().sum()
                raise ValueError(
                    f"Survey file contains non-numeric values in numeric columns. "
                    f"NaN counts: {nan_counts[nan_counts > 0].to_dict()}"
                )
            
            # Validate value ranges
            if (df["Depth"] < 0).any():
                raise ValueError(
                    "Depth must be positive. "
                    f"Found negative values: {df[df['Depth'] < 0]['Depth'].values}"
                )
             
            if "Dip" in df.columns:
                if (df["Dip"] > 0).all():
                    print("   ⚠️ Dips are positive - Flipping")
                    df["Dip"] = -df["Dip"]
            
            if (df["Dip"] > 0).any() or (df["Dip"] < -90).any():
                raise ValueError(
                    "Dip must be between -90 and 0 degrees (negative down). "
                    f"Found values: min={df['Dip'].min()}, max={df['Dip'].max()}"
                )
            
            if (df["Azimuth"] < 0).any() or (df["Azimuth"] >= 360).any():
                raise ValueError(
                    "Azimuth must be between 0 and 360 degrees. "
                    f"Found values: min={df['Azimuth'].min()}, max={df['Azimuth'].max()}"
                )
            
            # Sort by Hole_ID and Depth
            df = df.sort_values(["Hole_ID", "Depth"])
            
            print(f"✓ Survey file parsed successfully: {len(df)} survey points")
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("Survey CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing survey CSV file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing survey CSV: {str(e)}")
    
    def parse_assays(self, file: Union[str, BinaryIO]) -> pd.DataFrame:
        """
        Parse assays/interval CSV file with automatic column normalization
        
        Args:
            file: File path or file-like object
            
        Returns:
            DataFrame with normalized assay/interval data
        """
        try:
            df = pd.read_csv(file)
            print(f"📊 Loaded assay file with {len(df)} rows")
            print(f"   Original columns: {list(df.columns)}")
            
            # Normalize column names
            df = normalize_column_names(df, 'assay')
            
            # Validate required columns
            df = self._validate_columns(df, self.ASSAY_REQUIRED, "Assay")
            
            # Validate numeric columns
            df["From"] = pd.to_numeric(df["From"], errors='coerce')
            df["To"] = pd.to_numeric(df["To"], errors='coerce')
            
            if df[["From", "To"]].isna().any().any():
                nan_counts = df[["From", "To"]].isna().sum()
                raise ValueError(
                    f"Assay file contains non-numeric From/To values. "
                    f"NaN counts: {nan_counts[nan_counts > 0].to_dict()}"
                )
            
            # Validate intervals
            invalid_intervals = df[df["From"] >= df["To"]]
            if len(invalid_intervals) > 0:
                raise ValueError(
                    f"From depth must be less than To depth. "
                    f"Found {len(invalid_intervals)} invalid intervals. "
                    f"Example: {invalid_intervals.head(1)[['Hole_ID', 'From', 'To']].to_dict('records')}"
                )
            
            if (df["From"] < 0).any() or (df["To"] < 0).any():
                raise ValueError("Depths must be positive (From >= 0, To >= 0)")
            
            # Convert numeric assay columns
            text_columns = ["Hole_ID", "Lithology"]
            for col in df.columns:
                if col not in ["From", "To"] and col not in text_columns:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
            
            # Sort by Hole_ID and From
            df = df.sort_values(["Hole_ID", "From"])
            
            print(f"✓ Assay file parsed successfully: {len(df)} intervals")
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("Assay CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing assay CSV file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing assays CSV: {str(e)}")