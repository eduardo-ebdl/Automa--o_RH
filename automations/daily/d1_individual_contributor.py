import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.data_loader import load_processed_data
from core.logger_config import logger
from core.business_rules import find_overtime_employees

from core.utils import get_target_date
from core.gsheets_service import log_dataframe_to_sheet
from core.email_service import send_bulk_notifications

def run():
    """
    Runs the overtime check, sends emails, and logs to Google Sheets
    using the core service layer.
    """
    logger.info("--- Starting Automation: a1 - Individual Contributor Overtime Alert ---")
    
    target_date = get_target_date()
    
    df = load_processed_data(config.CONTRIBUTORS_FILE)
    if df is None:
        return 0, 0

    overtime_list_df = find_overtime_employees(df, target_date)
    if overtime_list_df is None or overtime_list_df.empty:
        return 0, 0
    

    # 1. logar os resultados no Google Sheets
    # log para o Dashboard Diário (sobrescreve)
    dashboard_cols = ['EMPLOYEE_ID', 'CONTRIBUTOR_NAME', 'HOURS_WORKED', 'TEAM', 'MANAGER_NAME']
    log_dataframe_to_sheet(
        df=overtime_list_df[dashboard_cols],
        spreadsheet_id=config.GOOGLE_SHEET_ID,
        worksheet_name='Dashboard Horas Extras',
        mode='overwrite'
    )

    # log para o Histórico (adiciona)
    log_cols = ['CONTRIBUTOR_NAME', 'HOURS_WORKED', 'MANAGER_EMAIL']
    log_df = overtime_list_df[log_cols].copy()
    log_df['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_df['Automation'] = 'a1_individual_contributor'
    log_dataframe_to_sheet(
        df=log_df,
        spreadsheet_id=config.GOOGLE_SHEET_ID,
        worksheet_name='Log de Alertas',
        mode='append'
    )
    
    # 2. preparar e enviar os e-mails
    logger.info("Preparing emails for individual contributors...")
    
    # cria a lista de "jobs" para o serviço de e-mail
    jobs_data = []
    for _, row in overtime_list_df.iterrows():
        recipient = config.EMAIL_TEST_RECIPIENT if config.EMAIL_TEST_RECIPIENT else row['CONTRIBUTOR_EMAIL']
        context = {
            'nome': row['CONTRIBUTOR_NAME'], # Os nomes devem bater com o template
            'data': target_date.strftime('%d/%m/%Y'),
            'horas_trabalhadas': row['HOURS_WORKED'],
            'limite_horas': config.HOURS_LIMIT,
            'dashboard_url': f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}"
        }
        jobs_data.append({'recipient': recipient, 'context': context})

    # chama o serviço de envio de e-mail em lote
    success, failed = send_bulk_notifications(
        jobs_data=jobs_data,
        template_name='email/alerts/overtime_alert.html',
        subject_template="⚠️ Alerta de Horas Extras",
        test_limit=config.EMAIL_TEST_LIMIT
    )
    
    logger.info("--- Automation Finished ---")
    return success, failed

if __name__ == "__main__":
    load_dotenv()
    run()