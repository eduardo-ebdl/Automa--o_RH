# automations/a3_consolidated_coordinator.py
import os
import sys
from datetime import date
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

import config
from core.data_loader import load_processed_data
from core.email_sender import send_emails_in_parallel
from core.logger_config import logger
from core.business_rules import find_overtime_employees

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
    """Runs the automation that sends a summary to coordinators and returns email stats."""
    logger.info("--- Starting Automation: a3 - Consolidated Coordinator Summary ---")
    
    target_date = get_target_date()
    
    df = load_processed_data(config.CONTRIBUTORS_FILE)
    if df is None:
        logger.error("Stopping automation: Data could not be loaded.")
        return 0, 0

    overtime_list = find_overtime_employees(df, target_date)

    if overtime_list is None:
        logger.info("No action required based on business rules.")
        return 0, 0

    email_jobs = []
    for coordinator_email, area_df in overtime_list.groupby('COORDINATOR_EMAIL'):
        coordinator_name = area_df['COORDINATOR_NAME'].iloc[0]
        area_name = area_df['AREA'].iloc[0]
        
        area_summary_html = ""
        for _, member in area_df.sort_values('CONTRIBUTOR_NAME').iterrows():
            area_summary_html += f"""
            <tr>
                <td style="padding-bottom: 15px;">
                    <table class="employee-card" width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td class="label">Name:</td>
                            <td class="value">{member['CONTRIBUTOR_NAME']}</td>
                        </tr>
                        <tr>
                            <td class="label">Hours Worked:</td>
                            <td class="value">{member['HOURS_WORKED']:.1f}</td>
                        </tr>
                    </table>
                </td>
            </tr>
            """
        context = {
            'coordinator_name': coordinator_name,
            'area_name': area_name,
            'target_date': target_date.strftime('%d/%m/%Y'),
            'area_summary_html': area_summary_html
        }
        
        body = render_template('coordinator_summary.html', context)
        if not body:
            logger.warning(f"Skipping email for coordinator {coordinator_name} due to template rendering failure.")
            continue

        final_recipient = config.EMAIL_TEST_RECIPIENT if config.EMAIL_TEST_RECIPIENT else coordinator_email
        
        email_jobs.append({
            'recipient': final_recipient,
            'subject': f"Daily Hours Summary for your Area ({area_name}) - {target_date.strftime('%d/%m/%Y')}",
            'body': body
        })

    success, failed = send_emails_in_parallel(email_jobs, test_limit=config.EMAIL_TEST_LIMIT)
    logger.info("--- Automation Finished ---")
    return success, failed