from __future__ import annotations
from typing import Optional
import pandas as pd
from datetime import date

import config
from core.logger_config import logger


def find_overtime_employees(df: pd.DataFrame, target_date: date) -> Optional[pd.DataFrame]:
    """
    Applies the core business logic to find employees who worked overtime.
    Encapsulates filtering and logging for key business scenarios.

    Args:
        df (pd.DataFrame): The DataFrame with all employee data.
        target_date (date): The specific date to check for records.

    Returns:
        Optional[pd.DataFrame]: DataFrame containing only the employees who
        worked overtime, or None if no action is needed.
    """
    logger.info(f"Applying business rules for target date: {target_date.strftime('%d/%m/%Y')}")

    date_filter = df['LAST_UPDATE'].dt.date == target_date
    active_filter = df['STATUS'] == 'Active'
    today_records = df[date_filter & active_filter]

    if today_records.empty:
        logger.warning(
            f"No records found for the target date {target_date.strftime('%d/%m/%Y')}. "
            "Data might be outdated."
        )
        return None

    logger.info(f"Found {len(today_records)} total active records for today. Now checking for overtime...")

    overtime_df = today_records[today_records['HOURS_WORKED'] > config.HOURS_LIMIT]

    if overtime_df.empty:
        logger.info("Data is up-to-date. No employees met the overtime criteria today.")
        return None

    logger.info(f"Found {len(overtime_df)} contributors who exceeded the hour limit.")
    return overtime_df


def find_work_anniversaries(df: pd.DataFrame, target_date: date) -> Optional[pd.DataFrame]:
    """
    Finds employees whose work anniversary is on the target date.
    Assumes the DataFrame has already been cleaned by the data_loader.
    """
    logger.info(f"Applying business rules to find work anniversaries for {target_date.strftime('%d/%m/%Y')}")

    try:
        valid_df = df.dropna(subset=['ADMISSION_DATE'])

        anniversary_filter = (
            (valid_df['ADMISSION_DATE'].dt.month == target_date.month) &
            (valid_df['ADMISSION_DATE'].dt.day == target_date.day) &
            (valid_df['ADMISSION_DATE'].dt.year < target_date.year)
        )
        active_filter = valid_df['STATUS'] == 'Active'

        anniversary_df = valid_df[anniversary_filter & active_filter].copy()

        if anniversary_df.empty:
            logger.info("No work anniversaries found for the target date.")
            return None

        anniversary_df['YEARS_COMPLETED'] = target_date.year - anniversary_df['ADMISSION_DATE'].dt.year

        logger.info(f"Found {len(anniversary_df)} employees celebrating their work anniversary.")
        return anniversary_df

    except Exception as e:
        logger.error(f"An unexpected error occurred while finding work anniversaries: {e}", exc_info=True)
        return None