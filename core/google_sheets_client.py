# core/google_sheets_client.py
import gspread
from google.oauth2.service_account import Credentials
from core.logger_config import logger
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

class GoogleSheetsClient:
    def __init__(self, credentials_path=config.CREDENTIALS_FILE):
        try:
            creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
            self.client = gspread.authorize(creds)
            logger.info("Successfully authenticated with Google Sheets API.")
        except FileNotFoundError:
            logger.error(f"Google credentials file not found at '{credentials_path}'. Please ensure it is in the project root.")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            self.client = None

    def _get_worksheet(self, spreadsheet_id, worksheet_name):
        """Helper function to get a worksheet object with better logging."""
        if not self.client: return None
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            logger.info(f"Successfully accessed worksheet '{worksheet_name}'.")
            return worksheet
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet with ID '{spreadsheet_id}' not found.")
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet named '{worksheet_name}' not found. Please check for typos, extra spaces, or case sensitivity in your Google Sheet tab name.")
        except Exception as e:
            logger.error(f"An error occurred while accessing worksheet '{worksheet_name}': {e}")
        return None

    def ensure_headers(self, spreadsheet_id, worksheet_name, headers):
        """Checks if the A1 cell is empty and adds headers if it is."""
        worksheet = self._get_worksheet(spreadsheet_id, worksheet_name)
        if not worksheet: return

        try:
            cell_a1 = worksheet.acell('A1').value
            if not cell_a1:
                worksheet.append_row(headers, value_input_option='USER_ENTERED')
                logger.info(f"Headers added to worksheet '{worksheet_name}'.")
        except Exception as e:
            logger.error(f"Failed to ensure headers on worksheet '{worksheet_name}': {e}")

    def append_rows(self, spreadsheet_id, worksheet_name, data_rows):
        """Appends multiple rows to a worksheet."""
        worksheet = self._get_worksheet(spreadsheet_id, worksheet_name)
        if not worksheet: return False
        
        try:
            worksheet.append_rows(data_rows, value_input_option='USER_ENTERED')
            logger.info(f"Successfully appended {len(data_rows)} rows to worksheet '{worksheet_name}'.")
            return True
        except Exception as e:
            logger.error(f"An error occurred while appending rows to Google Sheets: {e}")
            return False

    def clear_and_write_rows(self, spreadsheet_id, worksheet_name, data_rows):
        """Clears a worksheet and writes new data, starting from cell A1."""
        worksheet = self._get_worksheet(spreadsheet_id, worksheet_name)
        if not worksheet: return False

        try:
            worksheet.clear()
            worksheet.update('A1', data_rows, value_input_option='USER_ENTERED')
            logger.info(f"Worksheet '{worksheet_name}' cleared and {len(data_rows)} new rows written.")
            return True
        except Exception as e:
            logger.error(f"An error occurred while clearing and writing to Google Sheets: {e}")
            return False

sheets_client = GoogleSheetsClient()