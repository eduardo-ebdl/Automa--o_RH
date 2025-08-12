import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"
CREDENTIALS_FILE = BASE_DIR / "google_credentials.json" 
# business rules
HOURS_LIMIT = int(os.getenv("HOURS_LIMIT", 10))

# execution
DATE_MODE = os.getenv("DATE_MODE", "today")
SPECIFIC_DATE = (
    datetime.strptime(os.getenv("SPECIFIC_DATE"), "%Y-%m-%d").date()
    if os.getenv("SPECIFIC_DATE")
    else None
)

# testing
EMAIL_TEST_LIMIT = int(os.getenv("EMAIL_TEST_LIMIT", 10))
EMAIL_TEST_RECIPIENT = os.getenv("EMAIL_TEST_RECIPIENT")

# performance
MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", 8))

# integrations
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")