"""
CSV parser for drillhole data with validation
"""
import pandas as pd
from typing import Union, BinaryIO


class DrillholeParser:
    """Parser for mining drillhole CSV files"""
    
    # Required columns for each table type
    COLLAR_REQUIRED = ["Hole_ID", "East", "North", "Elevation", "Max_Depth", "Azimuth", "Dip"]
    SURVEY_REQUIRED = ["Hole_ID", "Depth", "Azimuth", "Dip"]
    ASSAY_REQUIRED = ["Hole_ID", "From", "To"]
    
    def __init__(self):
        pass
    
    def _validate_columns(self, df: pd.DataFrame, required_cols: list, table_name: str):
        """Validate that required columns exist in dataframe"""
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(
                f"{table_name} CSV missing required columns: {missing}. "
                f"Found columns: {list(df.columns)}"
            )
        return df
    
    def parse_collar(self, file: Union[str, BinaryIO]) -> pd.DataFrame:
        """
        Parse collar CSV file
        
        Args:
            file: File path or file-like object
            
        Returns:
            DataFrame with collar data
        """
        try:
            df = pd.read_csv(file)
            df = self._validate_columns(df, self.COLLAR_REQUIRED, "Collar")
            
            # Validate numeric columns
            numeric_cols = ["East", "North", "Elevation", "Max_Depth", "Azimuth", "Dip"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Check for NaN values after conversion
            if df[numeric_cols].isna().any().any():
                raise ValueError("Collar file contains non-numeric values in numeric columns")
            
            # Validate value ranges
            if (df["Dip"] > 0).any() or (df["Dip"] < -90).any():
                raise ValueError("Dip must be between -90 and 0 degrees (negative down)")
            
            if (df["Azimuth"] < 0).any() or (df["Azimuth"] >= 360).any():
                raise ValueError("Azimuth must be between 0 and 360 degrees")
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error parsing collar CSV: {str(e)}")
    
    def parse_survey(self, file: Union[str, BinaryIO]) -> pd.DataFrame:
        """
        Parse survey (deviation) CSV file
        
        Args:
            file: File path or file-like object
            
        Returns:
            DataFrame with survey data
        """
        try:
            df = pd.read_csv(file)
            df = self._validate_columns(df, self.SURVEY_REQUIRED, "Survey")
            
            # Validate numeric columns
            numeric_cols = ["Depth", "Azimuth", "Dip"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            if df[numeric_cols].isna().any().any():
                raise ValueError("Survey file contains non-numeric values in numeric columns")
            
            # Validate value ranges
            if (df["Depth"] < 0).any():
                raise ValueError("Depth must be positive")
            
            if (df["Dip"] > 0).any() or (df["Dip"] < -90).any():
                raise ValueError("Dip must be between -90 and 0 degrees (negative down)")
            
            if (df["Azimuth"] < 0).any() or (df["Azimuth"] >= 360).any():
                raise ValueError("Azimuth must be between 0 and 360 degrees")
            
            # Sort by Hole_ID and Depth
            df = df.sort_values(["Hole_ID", "Depth"])
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error parsing survey CSV: {str(e)}")
    
    def parse_assays(self, file: Union[str, BinaryIO]) -> pd.DataFrame:
        """
        Parse assays/interval CSV file
        
        Args:
            file: File path or file-like object
            
        Returns:
            DataFrame with assay/interval data
        """
        try:
            df = pd.read_csv(file)
            df = self._validate_columns(df, self.ASSAY_REQUIRED, "Assay")
            
            # Validate numeric columns
            df["From"] = pd.to_numeric(df["From"], errors='coerce')
            df["To"] = pd.to_numeric(df["To"], errors='coerce')
            
            if df[["From", "To"]].isna().any().any():
                raise ValueError("Assay file contains non-numeric From/To values")
            
            # Validate intervals
            if (df["From"] >= df["To"]).any():
                raise ValueError("From depth must be less than To depth")
            
            if (df["From"] < 0).any() or (df["To"] < 0).any():
                raise ValueError("Depths must be positive")
            
            # Convert numeric assay columns
            for col in df.columns:
                if col not in ["Hole_ID", "From", "To", "Lithology"]:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
            
            # Sort by Hole_ID and From
            df = df.sort_values(["Hole_ID", "From"])
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error parsing assays CSV: {str(e)}")

