import gspread
from google.oauth2.service_account import Credentials
from core.logger_config import logger
import config

class GSheetsClient:
    def __init__(self, credentials_path=config.CREDENTIALS_FILE):
        try:
            creds = Credentials.from_service_account_file(credentials_path, scopes=config.GSHEETS_SCOPES)
            self.client = gspread.authorize(creds)
            logger.info("✅ Successfully authenticated with Google Sheets API.")
        except FileNotFoundError:
            logger.error(f"❌ Google credentials file not found at '{credentials_path}'.")
            self.client = None
        except Exception as e:
            logger.error(f"❌ Failed to authenticate with Google Sheets: {e}", exc_info=True)
            self.client = None

    def get_worksheet(self, spreadsheet_id, worksheet_name):
        """Gets a worksheet object with validation and detailed logging."""
        if not self.client:
            logger.error("Google Sheets client is not initialized.")
            return None

        if not spreadsheet_id or not worksheet_name:
            logger.error("Spreadsheet ID and Worksheet name are required.")
            return None

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            logger.info(f"📄 Successfully accessed worksheet '{worksheet_name}'.")
            return worksheet
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"❌ Spreadsheet with ID '{spreadsheet_id}' not found.")
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"❌ Worksheet named '{worksheet_name}' not found. Check for typos or case sensitivity.")
        except Exception as e:
            logger.error(f"❌ Error accessing worksheet '{worksheet_name}': {e}", exc_info=True)
        return None

    def ensure_headers(self, spreadsheet_id, worksheet_name, headers):
        """Checks if the A1 cell is empty and adds headers if needed."""
        worksheet = self.get_worksheet(spreadsheet_id, worksheet_name)
        if not worksheet:
            return

        try:
            cell_a1 = worksheet.acell('A1').value
            if not cell_a1:
                worksheet.append_row(headers, value_input_option='USER_ENTERED')
                logger.info(f"✅ Headers added to worksheet '{worksheet_name}'.")
            else:
                logger.debug(f"Headers already present in worksheet '{worksheet_name}'.")
        except Exception as e:
            logger.error(f"❌ Failed to ensure headers on worksheet '{worksheet_name}': {e}", exc_info=True)

    def append_rows(self, spreadsheet_id, worksheet_name, data_rows):
        """Appends multiple rows to a worksheet."""
        worksheet = self.get_worksheet(spreadsheet_id, worksheet_name)
        if not worksheet:
            return False
        
        try:
            worksheet.append_rows(data_rows, value_input_option='USER_ENTERED')
            logger.info(f"✅ Appended {len(data_rows)} rows to worksheet '{worksheet_name}'.")
            return True
        except Exception as e:
            logger.error(f"❌ Error appending rows to Google Sheets: {e}", exc_info=True)
            return False

    def clear_and_write_rows(self, spreadsheet_id, worksheet_name, data_rows):
        """Clears a worksheet and writes new data."""
        worksheet = self.get_worksheet(spreadsheet_id, worksheet_name)
        if not worksheet:
            return False

        try:
            worksheet.clear()
            worksheet.update('A1', data_rows, value_input_option='USER_ENTERED')
            logger.info(f"✅ Worksheet '{worksheet_name}' cleared and {len(data_rows)} new rows written.")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing and writing to Google Sheets: {e}", exc_info=True)
            return False


# exporta uma instância padrão
gsheets_client = GSheetsClient()