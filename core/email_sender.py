# core/email_sender.py
import smtplib
import ssl
from email.message import EmailMessage
import os
import concurrent.futures

import config
from core.logger_config import logger

# --- Email Settings from environment variables ---
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def _send_single_email(email_job):
    """Internal function to send one email. Meant to be run in a thread."""
    try:
        recipient = email_job['recipient']
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
        
        return (recipient, "Success")
    except Exception as e:
        error_message = str(e).strip()
        # Aqui usamos o logger em vez de print para consistência
        logger.error(f"Failed to send email to {email_job.get('recipient', 'unknown')}. Error: {error_message}")
        return (email_job.get('recipient', 'unknown'), f"Failed: {error_message}")

def send_emails_in_parallel(email_jobs, test_limit=None):
    """
    Receives a list of email jobs and sends them in parallel.
    Returns: A tuple (success_count, failed_count)
    """
    if not email_jobs:
        return 0, 0

    if test_limit is not None and len(email_jobs) > test_limit:
        logger.info(f"Test limit is active. Processing only the first {test_limit} of {len(email_jobs)} email jobs.")
        email_jobs = email_jobs[:test_limit]

    logger.info(f"Preparing to send {len(email_jobs)} emails in parallel...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_PARALLEL_WORKERS) as executor:
        results = list(executor.map(_send_single_email, email_jobs))

    success_count = sum(1 for r in results if r[1] == "Success")
    failed_count = len(results) - success_count
    
    logger.info(f"Email sending task finished: {success_count} succeeded, {failed_count} failed.")
    
    return success_count, failed_count