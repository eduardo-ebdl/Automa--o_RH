from datetime import timedelta

# app settings
BATCH_SIZE = 500
REQUEST_TIMEOUT = 10
REPROCESS_INTERVAL = timedelta(days=1)
ENABLE_DEBUG_LOGS = True

# constants
COL_HOURS = "Horas"
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