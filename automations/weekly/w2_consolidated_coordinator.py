import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from core.data_loader import load_processed_data
from core.logger_config import logger
from core.business_rules import find_overtime_employees
from core.utils import get_target_date
from core.email_service import send_bulk_notifications

def run():
    """Runs the automation that sends a summary to coordinators and returns email stats."""
    logger.info("--- Starting Automation: w2 - Consolidated Coordinator Summary ---")
    
    target_date = get_target_date()
    
    df = load_processed_data(config.CONTRIBUTORS_FILE)
    if df is None: return 0, 0

    overtime_list_df = find_overtime_employees(df, target_date)
    if overtime_list_df is None or overtime_list_df.empty:
        return 0, 0

    logger.info(f"Preparing consolidated summary emails for {overtime_list_df['COORDINATOR_EMAIL'].nunique()} coordinators.")

    jobs_data = []
    # agrupa a lista de horas extras por coordenador
    for coordinator_email, area_df in overtime_list_df.groupby('COORDINATOR_EMAIL'):
        coordinator_name = area_df['COORDINATOR_NAME'].iloc[0]
        area_name = area_df['AREA'].iloc[0]

        # gera o HTML dos cards para a área deste coordenador
        area_summary_html = ""
        for _, member in area_df.sort_values('CONTRIBUTOR_NAME').iterrows():
            area_summary_html += f"""
            <tr><td style="padding-bottom: 15px;">
                <table class="employee-card" width="100%" cellspacing="0" cellpadding="0">
                    <tr><td class="label">Name:</td><td class="value">{member['CONTRIBUTOR_NAME']}</td></tr>
                    <tr><td class="label">Hours Worked:</td><td class="value">{member['HOURS_WORKED']:.1f}</td></tr>
                </table>
            </td></tr>
            """
            
        recipient = config.EMAIL_TEST_RECIPIENT if config.EMAIL_TEST_RECIPIENT else coordinator_email
        context = {
            'nome_coordenador': coordinator_name,
            'nome_area': area_name,
            'data_resumo': target_date.strftime('%d/%m/%Y'),
            'resumo_area': area_summary_html,
            'dashboard_url': f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}"
        }
        jobs_data.append({'recipient': recipient, 'context': context})

    # chama o serviço de envio de e-mail em lote
    subject_template = "📋 Resumo da Área - {nome_area}"
    success, failed = send_bulk_notifications(
        jobs_data=jobs_data,
        template_name='email/reports/coordinator_summary.html',
        subject_template=subject_template,
        test_limit=config.EMAIL_TEST_LIMIT
    )
    
    logger.info("--- Automation Finished ---")
    return success, failed

if __name__ == "__main__":
    load_dotenv()
    run()