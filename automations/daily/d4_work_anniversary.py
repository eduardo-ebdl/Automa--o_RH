import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from core.data_loader import load_processed_data
from core.logger_config import logger
from core.business_rules import find_work_anniversaries
from core.utils import get_target_date
from core.gsheets_service import log_dataframe_to_sheet
from core.email_service import send_bulk_notifications

def run():
    """Runs the work anniversary automation and returns email stats."""
    logger.info("--- Starting Automation: d2 - Work Anniversary ---")
    
    target_date = get_target_date()
    
    df = load_processed_data(config.CONTRIBUTORS_FILE)
    if df is None: return 0, 0

    anniversary_df = find_work_anniversaries(df, target_date)
    if anniversary_df is None or anniversary_df.empty:
        return 0, 0

    # 1. logar os resultados no Google Sheets
    # prepara o DataFrame com as colunas certas para o log
    log_df = anniversary_df[['CONTRIBUTOR_NAME', 'YEARS_COMPLETED', 'AREA']].copy()
    log_df['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_df['Automation'] = 'd2_work_anniversary'
    
    log_dataframe_to_sheet(
        df=log_df,
        spreadsheet_id=config.GOOGLE_SHEET_ID,
        worksheet_name='Log de Aniversários',
        mode='append'
    )
    
    # 2. prepara e envia os e-mails
    logger.info("Preparing work anniversary emails...")
    
    jobs_data = []
    for _, row in anniversary_df.iterrows():
        recipient = config.EMAIL_TEST_RECIPIENT if config.EMAIL_TEST_RECIPIENT else row['CONTRIBUTOR_EMAIL']
        context = {
            'nome': row['CONTRIBUTOR_NAME'],
            'anos_empresa': row['YEARS_COMPLETED'],
            'dashboard_url': f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}"
        }
        jobs_data.append({'recipient': recipient, 'context': context})

    # chama o serviço de envio de e-mail em lote
    subject = "🎉 Parabéns pelo seu Aniversário de Empresa!"
    success, failed = send_bulk_notifications(
        jobs_data=jobs_data,
        template_name='email/alerts/anniversary_alert.html',
        subject_template=subject,
        test_limit=config.EMAIL_TEST_LIMIT
    )
    
    logger.info("--- Automation Finished ---")
    return success, failed

if __name__ == "__main__":
    load_dotenv()
    run()