import smtplib
import ssl
from email.message import EmailMessage
import os
import concurrent.futures
from typing import List, Dict, Tuple

import config
from core.logger_config import logger

SMTP_SERVER = config.os.getenv('SMTP_SERVER')
SMTP_PORT = int(config.os.getenv('SMTP_PORT', '587'))
EMAIL_SENDER = config.os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = config.os.getenv('EMAIL_PASSWORD')

def _send_single_email(email_job: Dict[str, str]) -> Tuple[str, str]:
    """Internal function to send one email. Meant to be run in a thread."""
    recipient = email_job.get('recipient', 'unknown_recipient')
    try:
        subject = email_job['subject']
        body = email_job['body']

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient
        msg.set_content(body, subtype='html')

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.debug(f"Email sent successfully to {recipient}")
        return (recipient, "Success")
        
    except Exception as e:
        error_message = str(e).strip()
        # add 'exc_info=True' para logar o traceback completo do erro, para identificar problemas de conexão
        logger.error(f"Failed to send email to {recipient}. Error: {error_message}", exc_info=True)
        return (recipient, f"Failed: {error_message}")

def send_emails_in_parallel(email_jobs: List[Dict[str, str]], test_limit: int = None) -> Tuple[int, int]:
    """
    Receives a list of email jobs and sends them in parallel.
    Returns: (success_count, failed_count)
    """
    if not email_jobs:
        return 0, 0

    if test_limit is not None and len(email_jobs) > test_limit:
        logger.info(f"Test limit active. Processing only the first {test_limit} of {len(email_jobs)} jobs.")
        email_jobs = email_jobs[:test_limit]

    logger.info(f"Preparing to send {len(email_jobs)} emails in parallel...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_PARALLEL_WORKERS) as executor:
        results = list(executor.map(_send_single_email, email_jobs))

    success_count = sum(1 for _, status in results if status == "Success")
    failed_count = len(results) - success_count

    logger.info(f"Email sending task finished: {success_count} succeeded, {failed_count} failed.")
    return success_count, failed_count