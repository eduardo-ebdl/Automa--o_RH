import pandas as pd
from typing import Optional
from core.logger_config import logger

def load_processed_data(filepath: str) -> Optional[pd.DataFrame]:
    """
    Loads data directly from a CSV file into a pandas DataFrame,
    validates, and processes all date columns.
    """
    try:
        # lê o csv diretamente para um dataFrame do pandas
        df = pd.read_csv(filepath, sep=',')
        logger.info(f"Successfully loaded data from {filepath}.")
   
        df['LAST_UPDATE'] = pd.to_datetime(df['LAST_UPDATE'], dayfirst=True, errors='coerce')
        df['ADMISSION_DATE'] = pd.to_datetime(df['ADMISSION_DATE'], format='mixed', dayfirst=True, errors='coerce')

        # verificação de datas inválidas
        invalid_dates = df[df['ADMISSION_DATE'].isnull()]
        if not invalid_dates.empty:
            logger.warning(
                f"Found {len(invalid_dates)} rows with invalid dates in 'ADMISSION_DATE'. "
                "These rows will be ignored by anniversary checks."
            )
            for _, row in invalid_dates.iterrows():
                logger.warning(f" -> Invalid admission date for EMPLOYEE_ID: {row.get('EMPLOYEE_ID', 'N/A')}")
        
        return df

    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Failed to process CSV file: {filepath}. Error: {e}", exc_info=True)
        return None