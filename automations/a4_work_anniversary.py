# automations/a4_work_anniversary.py
import os
import sys
from datetime import date, datetime
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.data_loader import load_processed_data
from core.email_sender import send_emails_in_parallel
from core.logger_config import logger
from core.business_rules import find_work_anniversaries
from core.google_sheets_client import sheets_client

def get_target_date():
    """Determines the target date based on the config file."""
    if config.DATE_MODE == 'today':
        return date.today()
    return config.SPECIFIC_DATE

def render_template(template_name, context):
    """Renders an HTML template using Jinja2."""
    try:
        env = Environment(loader=FileSystemLoader(config.TEMPLATES_DIR))
        template = env.get_template(template_name)
        return template.render(context)
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {e}")
        return None

def run():
    """Runs the work anniversary automation and returns email stats."""
    logger.info("--- Starting Automation: a4 - Work Anniversary ---")
    
    target_date = get_target_date()
    
    df = load_processed_data(config.CONTRIBUTORS_FILE)
    if df is None: return 0, 0

    anniversary_list = find_work_anniversaries(df, target_date)

    if anniversary_list is None:
        return 0, 0
    
    worksheet_name = 'Log de Aniversários'
    log_headers = ['Timestamp', 'Contributor Name', 'Years Completed', 'Area', 'Automation']
    
    rows_to_log = []
    sheets_client.ensure_headers(config.GOOGLE_SHEET_ID, worksheet_name, log_headers)
    
    email_jobs = []
    for _, row in anniversary_list.iterrows():
        context = {
            'contributor_name': row['CONTRIBUTOR_NAME'],
            'years_completed': row['YEARS_COMPLETED']
        }
        body = render_template('anniversary_alert.html', context)
        
        if not body:
            logger.warning(f"Skipping email for {row['CONTRIBUTOR_NAME']} due to template rendering failure.")
            continue

        rows_to_log.append([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            row['CONTRIBUTOR_NAME'],
            row['YEARS_COMPLETED'],
            row['AREA'],
            'a4_work_anniversary'
        ])

        final_recipient = config.EMAIL_TEST_RECIPIENT if config.EMAIL_TEST_RECIPIENT else row['CONTRIBUTOR_EMAIL']
        
        email_jobs.append({
            'recipient': final_recipient,
            'subject': f"🎉 Feliz Aniversário de {row['YEARS_COMPLETED']} Anos de Empresa!",
            'body': body
        })
        
    if rows_to_log:
        sheets_client.append_rows(config.GOOGLE_SHEET_ID, worksheet_name, rows_to_log)
        
    success, failed = send_emails_in_parallel(email_jobs, test_limit=config.EMAIL_TEST_LIMIT)
    logger.info("--- Automation Finished ---")
    return success, failed

if __name__ == "__main__":
    load_dotenv()
    run()