import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from core.data_loader import load_processed_data
from core.logger_config import logger
from core.business_rules import find_overtime_employees
from core.utils import get_target_date
from core.gsheets_service import log_dataframe_to_sheet
from core.email_service import send_bulk_notifications

def run():
    """Runs the automation that sends a consolidated summary to managers and returns email stats."""
    logger.info("--- Starting Automation: w1 - Consolidated Manager Summary ---")
    
    target_date = get_target_date()
    
    df = load_processed_data(config.CONTRIBUTORS_FILE)
    if df is None: return 0, 0

    overtime_list_df = find_overtime_employees(df, target_date)
    if overtime_list_df is None or overtime_list_df.empty:
        return 0, 0
    
    logger.info(f"Preparing consolidated summary emails for {overtime_list_df['MANAGER_EMAIL'].nunique()} managers.")
    
    jobs_data = []
    # agrupa a lista de horas extras por gestor
    for manager_email, team_df in overtime_list_df.groupby('MANAGER_EMAIL'):
        manager_name = team_df['MANAGER_NAME'].iloc[0]
        
        # gera o HTML dos cards para a equipe deste gestor
        team_summary_html = ""
        for _, member in team_df.sort_values('CONTRIBUTOR_NAME').iterrows():
            team_summary_html += f"""
            <tr><td style="padding-bottom: 15px;">
                <table class="employee-card" width="100%" cellspacing="0" cellpadding="0">
                    <tr><td class="label">Name:</td><td class="value">{member['CONTRIBUTOR_NAME']}</td></tr>
                    <tr><td class="label">Hours Worked:</td><td class="value">{member['HOURS_WORKED']:.1f}</td></tr>
                </table>
            </td></tr>
            """
        
        recipient = config.EMAIL_TEST_RECIPIENT if config.EMAIL_TEST_RECIPIENT else manager_email
        context = {
            'nome_gestor': manager_name,
            'data_resumo': target_date.strftime('%d/%m/%Y'),
            'tabela_horas': team_summary_html,
            'dashboard_url': f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}"
        }
        jobs_data.append({'recipient': recipient, 'context': context})

    # chama o serviço de envio de e-mail em lote
    success, failed = send_bulk_notifications(
        jobs_data=jobs_data,
        template_name='email/reports/manager_summary.html',
        subject_template="📈 Resumo Diário - Gerência",
        test_limit=config.EMAIL_TEST_LIMIT
    )
    
    logger.info("--- Automation Finished ---")
    return success, failed

if __name__ == "__main__":
    load_dotenv()
    run()