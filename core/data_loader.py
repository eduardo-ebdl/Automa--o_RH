# core/data_loader.py
import pandas as pd
import os
from core.logger_config import logger

def load_processed_data(filepath):
    """
    Loads data from the CSV, validates, and processes all date columns.
    """
    try:
        df = pd.read_csv(filepath, sep=',')
        
        # 1. Processa a coluna LAST_UPDATE (já estava correto)
        df['LAST_UPDATE'] = pd.to_datetime(df['LAST_UPDATE'], dayfirst=True)
        
        # 2. Processa a coluna ADMISSION_DATE
        df['ADMISSION_DATE'] = pd.to_datetime(df['ADMISSION_DATE'], format='mixed', dayfirst=True, errors='coerce')

        # 3. Diagnóstico: Verifica se alguma data de admissão falhou na conversão
        invalid_dates = df[df['ADMISSION_DATE'].isnull()]
        if not invalid_dates.empty:
            logger.warning(f"Found {len(invalid_dates)} rows with invalid dates in 'ADMISSION_DATE' column. These rows will be ignored by anniversary checks.")
            for index, row in invalid_dates.iterrows():
                logger.warning(f" -> Invalid admission date for EMPLOYEE_ID: {row.get('EMPLOYEE_ID', 'N/A')}")
        
        return df
        
    except FileNotFoundError:
        logger.error(f"File not found at {filepath}")
        return None
    except Exception as e:
        logger.error(f"Failed to read or process the CSV file. Details: {e}", exc_info=True)
        return None