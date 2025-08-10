# config.py
import os
from datetime import date

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CONTRIBUTORS_FILE = os.path.join(DATA_DIR, 'contributors.csv')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'google_credentials.json')

# --- Business Rules ---
HOURS_LIMIT = 10

# --- Execution Settings ---
# Set to 'today' for production or a specific date string for testing
DATE_MODE = 'specific' # 'today' or 'specific'
SPECIFIC_DATE = date(2025, 3, 12) # -  para testar o aniversario
# - 2025, 6, 8

# --- Testing ---
EMAIL_TEST_LIMIT = 1
EMAIL_TEST_RECIPIENT = os.getenv('EMAIL_SENDER')

# --- Performance ---
# Adicione esta linha:
MAX_PARALLEL_WORKERS = 8

# --- Integrations ---
GOOGLE_SHEET_ID = '1HBPfzn-_WaSnLr5rVBPTFerdC_DDpdh8QuzqhU_4sNs'