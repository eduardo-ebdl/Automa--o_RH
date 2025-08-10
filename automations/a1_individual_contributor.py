# automations/a1_individual_contributor.py
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
from core.business_rules import find_overtime_employees
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

# Em automations/a1_individual_contributor.py

def run():
    """Runs the overtime check, sends emails, and logs to Google Sheets."""
    logger.info("--- Starting Automation: a1 - Individual Contributor Overtime Alert ---")
    
    target_date = get_target_date()
    
    df = load_processed_data(config.CONTRIBUTORS_FILE)
    if df is None:
        return 0, 0

    overtime_list = find_overtime_employees(df, target_date)
    if overtime_list is None:
        return 0, 0
    
    spreadsheet_link = f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}"

    # 1. Prepara os dados para o Dashboard Diário
    dashboard_headers = ['Employee ID', 'Contributor Name', 'Hours Worked', 'Team', 'Manager Name']
    rows_for_dashboard = [dashboard_headers]
    
    # 2. Prepara os dados para o Log Histórico
    log_headers = ['Timestamp', 'Contributor Name', 'Hours Worked', 'Manager Email', 'Automation']
    rows_to_log = [] 

    # 3. Garante que os cabeçalhos existam na aba de Log (só adiciona se a aba estiver vazia)
    sheets_client.ensure_headers(config.GOOGLE_SHEET_ID, 'Log de Alertas', log_headers)

    email_jobs = []
    for _, row in overtime_list.iterrows():
        # Prepara a linha de dados para o log, sem o cabeçalho
        rows_to_log.append([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            row['CONTRIBUTOR_NAME'],
            row['HOURS_WORKED'],
            row['MANAGER_EMAIL'],
            'a1_individual_contributor'
        ])
        
        # Preenche os dados
        rows_for_dashboard.append([
            row['EMPLOYEE_ID'],
            row['CONTRIBUTOR_NAME'],
            row['HOURS_WORKED'],
            row['TEAM'],
            row['MANAGER_NAME']
        ])

        # Prepara o e-mail
        context = {
            'contributor_name': row['CONTRIBUTOR_NAME'],
            'target_date': target_date.strftime('%d/%m/%Y'),
            'hours_worked': row['HOURS_WORKED'],
            'hours_limit': config.HOURS_LIMIT,
            'manager_name': row['MANAGER_NAME'],
            'spreadsheet_link': spreadsheet_link
        }
        body = render_template('overtime_alert.html', context)
        
        if not body:
            logger.warning(f"Skipping email for {row['CONTRIBUTOR_NAME']} due to template rendering failure.")
            continue

        final_recipient = config.EMAIL_TEST_RECIPIENT if config.EMAIL_TEST_RECIPIENT else row['CONTRIBUTOR_EMAIL']
        email_jobs.append({'recipient': final_recipient, 'subject': "Alert | Daily Hour Limit Exceeded", 'body': body})
    
    # Executa as operações no Google Sheets
    if rows_to_log: # Se a lista não estiver vazia
        sheets_client.append_rows(config.GOOGLE_SHEET_ID, 'Log de Alertas', rows_to_log)
    
    if len(rows_for_dashboard) > 1:
        sheets_client.clear_and_write_rows(config.GOOGLE_SHEET_ID, 'Dashboard Horas Extras', rows_for_dashboard)
        
    # Envia os e-mails
    success, failed = send_emails_in_parallel(email_jobs, test_limit=config.EMAIL_TEST_LIMIT)
    
    logger.info("--- Automation Finished ---")
    return success, failed