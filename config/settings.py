from datetime import timedelta
from pathlib import Path

# app settings
BATCH_SIZE = 500
REQUEST_TIMEOUT = 10
REPROCESS_INTERVAL = timedelta(days=1)
ENABLE_DEBUG_LOGS = True

# constants
COL_HOURS = "Horas"
PROJECT_ROOT = Path(__file__).parent.parent
CONTRIBUTORS_FILE = PROJECT_ROOT / "data" / "sample_data.csv"
COL_PROJECT = "Projeto"
COL_EMPLOYEE = "Colaborador"
MSG_NO_DATA = "Nenhum dado encontrado para o período."
MSG_ERROR_GENERIC = "Ocorreu um erro inesperado."
ALLOWED_FILE_EXTENSIONS = [".csv", ".xlsx"]
DATE_FORMAT = "%Y-%m-%d"

# google sheets
GSHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]