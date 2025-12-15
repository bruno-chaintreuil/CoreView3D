import pandas as pd
import io
from typing import BinaryIO, Dict, Optional
import logging

from coreview3d.parsers.csv_parser import DrillholeParser

logger = logging.getLogger("excel_parser")


class ExcelDrillholeParser(DrillholeParser):
    COLLAR_SHEET_NAMES = ['collar', 'collars', 'holes', 'drillholes', 'dh']
    SURVEY_SHEET_NAMES = ['survey', 'surveys', 'deviation', 'deviations']
    ASSAYS_SHEET_NAMES = ['assays', 'assay', 'samples', 'results', 'intervals']
    
    def parse_excel_file(self, file: BinaryIO) -> Dict[str, Optional[pd.DataFrame]]:
        try:
            # Lire toutes les feuilles de l'Excel
            excel_file = pd.ExcelFile(file)
            sheet_names = excel_file.sheet_names
            
            logger.info(f"📊 Excel file contains {len(sheet_names)} sheets: {sheet_names}")
            
            # Créer un mapping case-insensitive des noms de feuilles
            sheet_mapping = {name.lower(): name for name in sheet_names}
            
            # Trouver et parser chaque type de feuille
            result = {
                'collar': self._find_and_parse_collar(excel_file, sheet_mapping),
                'survey': self._find_and_parse_survey(excel_file, sheet_mapping),
                'assays': self._find_and_parse_assays(excel_file, sheet_mapping)
            }
            
            # Log des résultats
            if result['collar'] is not None:
                logger.info(f"✅ Found Collar sheet with {len(result['collar'])} records")
            else:
                logger.warning("⚠️ No Collar sheet found")
            
            if result['survey'] is not None:
                logger.info(f"✅ Found Survey sheet with {len(result['survey'])} records")
            
            if result['assays'] is not None:
                logger.info(f"✅ Found Assays sheet with {len(result['assays'])} records")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise ValueError(f"Error parsing Excel file: {e}")
    
    def _find_and_parse_collar(
        self, 
        excel_file: pd.ExcelFile, 
        sheet_mapping: Dict[str, str]
    ) -> Optional[pd.DataFrame]:
        sheet_name = self._find_sheet(sheet_mapping, self.COLLAR_SHEET_NAMES)
        
        if sheet_name is None:
            return None
        
        logger.debug(f"Found collar sheet: '{sheet_name}'")
        
        df = excel_file.parse(sheet_name)
        
        if df.empty:
            logger.warning(f"Collar sheet '{sheet_name}' is empty")
            return None
        
        try:
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
            
            # Nettoyer
            df = df.dropna(subset=['HOLEID', 'EAST', 'NORTH', 'ELEV'])
            
            if df.empty:
                raise ValueError("No valid collar records after cleaning")
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing collar sheet: {e}")
            raise
    
    def _find_and_parse_survey(
        self,
        excel_file: pd.ExcelFile,
        sheet_mapping: Dict[str, str]
    ) -> Optional[pd.DataFrame]:
        sheet_name = self._find_sheet(sheet_mapping, self.SURVEY_SHEET_NAMES)
        
        if sheet_name is None:
            return None
        
        logger.debug(f"Found survey sheet: '{sheet_name}'")
        
        df = excel_file.parse(sheet_name)
        
        if df.empty:
            logger.warning(f"Survey sheet '{sheet_name}' is empty")
            return None
        
        try:
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
            
            df = df.dropna(subset=['HOLEID', 'DEPTH', 'AZIMUTH', 'DIP'])
            
            if df.empty:
                raise ValueError("No valid survey records after cleaning")
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing survey sheet: {e}")
            raise
    
    def _find_and_parse_assays(
        self,
        excel_file: pd.ExcelFile,
        sheet_mapping: Dict[str, str]
    ) -> Optional[pd.DataFrame]:
        sheet_name = self._find_sheet(sheet_mapping, self.ASSAYS_SHEET_NAMES)
        
        if sheet_name is None:
            return None
        
        logger.debug(f"Found assays sheet: '{sheet_name}'")
        
        df = excel_file.parse(sheet_name)
        
        if df.empty:
            logger.warning(f"Assays sheet '{sheet_name}' is empty")
            return None
        
        try:
            required = ['HOLEID', 'FROM', 'TO']
            df = self._apply_column_mapping(
                df,
                self.ASSAYS_COLUMN_MAPPING,
                required,
                "Assays"
            )
            
            # Convertir les types
            df['HOLEID'] = df['HOLEID'].astype(str).str.strip()
            df['FROM'] = pd.to_numeric(df['FROM'], errors='coerce')
            df['TO'] = pd.to_numeric(df['TO'], errors='coerce')
            
            # Colonnes optionnelles
            if 'LITHOLOGY' in df.columns:
                df['LITHOLOGY'] = df['LITHOLOGY'].astype(str).str.strip().str.upper()
            
            if 'AU_PPM' in df.columns:
                df['AU_PPM'] = pd.to_numeric(df['AU_PPM'], errors='coerce')
            
            if 'CU_PCT' in df.columns:
                df['CU_PCT'] = pd.to_numeric(df['CU_PCT'], errors='coerce')
            
            # Nettoyer
            df = df.dropna(subset=['HOLEID', 'FROM', 'TO'])
            
            if df.empty:
                raise ValueError("No valid assay records after cleaning")
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing assays sheet: {e}")
            raise
    
    def _find_sheet(
        self,
        sheet_mapping: Dict[str, str],
        possible_names: list
    ) -> Optional[str]:
        for name in possible_names:
            if name in sheet_mapping:
                return sheet_mapping[name]
        return None
    
    def parse_collar_sheet(self, file: BinaryIO, sheet_name: str = 'Collar') -> pd.DataFrame:
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            
            if df.empty:
                raise ValueError(f"Sheet '{sheet_name}' is empty")
            
            required = ['HOLEID', 'EAST', 'NORTH', 'ELEV']
            df = self._apply_column_mapping(
                df,
                self.COLLAR_COLUMN_MAPPING,
                required,
                "Collar"
            )
            
            # Convertir types (même code que CSV)
            df['HOLEID'] = df['HOLEID'].astype(str).str.strip()
            df['EAST'] = pd.to_numeric(df['EAST'], errors='coerce')
            df['NORTH'] = pd.to_numeric(df['NORTH'], errors='coerce')
            df['ELEV'] = pd.to_numeric(df['ELEV'], errors='coerce')
            
            if 'MAX_DEPTH' in df.columns:
                df['MAX_DEPTH'] = pd.to_numeric(df['MAX_DEPTH'], errors='coerce')
            
            df = df.dropna(subset=['HOLEID', 'EAST', 'NORTH', 'ELEV'])
            
            if df.empty:
                raise ValueError("No valid collar records after cleaning")
            
            logger.info(f"✅ Parsed {len(df)} collar records from sheet '{sheet_name}'")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing Excel collar sheet '{sheet_name}': {e}")
            raise ValueError(f"Error parsing Excel collar sheet: {e}")
    
    def parse_survey_sheet(self, file: BinaryIO, sheet_name: str = 'Survey') -> pd.DataFrame:
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            
            if df.empty:
                raise ValueError(f"Sheet '{sheet_name}' is empty")
            
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
            
            df = df.dropna(subset=['HOLEID', 'DEPTH', 'AZIMUTH', 'DIP'])
            
            if df.empty:
                raise ValueError("No valid survey records after cleaning")
            
            logger.info(f"✅ Parsed {len(df)} survey records from sheet '{sheet_name}'")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing Excel survey sheet '{sheet_name}': {e}")
            raise ValueError(f"Error parsing Excel survey sheet: {e}")
    
    def parse_assays_sheet(self, file: BinaryIO, sheet_name: str = 'Assays') -> pd.DataFrame:
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            
            if df.empty:
                raise ValueError(f"Sheet '{sheet_name}' is empty")
            
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
            
            df = df.dropna(subset=['HOLEID', 'FROM', 'TO'])
            
            if df.empty:
                raise ValueError("No valid assay records after cleaning")
            
            logger.info(f"✅ Parsed {len(df)} assay records from sheet '{sheet_name}'")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing Excel assays sheet '{sheet_name}': {e}")
            raise ValueError(f"Error parsing Excel assays sheet: {e}")