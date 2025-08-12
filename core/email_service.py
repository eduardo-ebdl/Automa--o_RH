import os
from typing import List, Dict, Optional, Tuple
from jinja2 import Environment, FileSystemLoader

import config
from core.logger_config import logger
from core import email_sender

# configurar o ambiente "Jinja2" uma única vez
try:
    jinja_env = Environment(loader=FileSystemLoader(config.TEMPLATES_DIR))
    logger.info("Jinja2 environment configured successfully.")
except Exception as e:
    logger.error(f"Failed to configure Jinja2 environment: {e}")
    jinja_env = None

def render_template_with_jinja(template_name: str, context: Dict) -> Optional[str]:
    """Lê e renderiza um template HTML usando Jinja2."""
    if not jinja_env:
        logger.error("Jinja2 environment not available. Cannot render template.")
        return None
    try:
        template = jinja_env.get_template(template_name)
        return template.render(context)
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {e}", exc_info=True)
        return None

def send_email_notification(
    template_name: str,
    context: Dict,
    subject: str,
    recipient: str
) -> Tuple[int, int]:
    """
    Prepara e envia um único email de notificação.
    Esta é uma função de conveniência para automações que enviam um e-mail por vez.
    """
    body = render_template_with_jinja(template_name, context)
    if not body:
        logger.error(f"Aborting email send to {recipient} because template rendering failed.")
        return 0, 1 # 0 sucessos, 1 falha

    email_job = [{'recipient': recipient, 'subject': subject, 'body': body}]
    
    # chama diretamente o sender para enviar o único e-mail
    success, failed = email_sender.send_emails_in_parallel(email_job, test_limit=1)
    return success, failed

def send_bulk_notifications(
    jobs_data: List[Dict],
    template_name: str,
    subject_template: str,
    test_limit: Optional[int] = None
) -> Tuple[int, int]:
    """
    Prepara e envia múltiplos e-mails, cada um com seu próprio contexto.
    
    Args:
        jobs_data: Uma lista de dicionários. Cada dicionário deve conter 'recipient' e 'context'.
                   Ex: [{'recipient': 'a@a.com', 'context': {'name': 'John'}}, ...]
        template_name: O nome do arquivo de template HTML.
        subject_template: O template para o assunto do e-mail.
    """
    logger.info(f"Preparing bulk email sending task for {len(jobs_data)} jobs.")
    
    email_jobs = []
    for job_info in jobs_data:
        recipient = job_info.get('recipient')
        context = job_info.get('context', {})
        
        if not recipient:
            logger.warning("Skipping a job due to missing recipient.")
            continue
            
        # renderiza o corpo do e-mail para este job específico
        body = render_template_with_jinja(template_name, context)
        if not body:
            logger.warning(f"Skipping email for {recipient} because template rendering failed.")
            continue
        
        # renderiza o assunto do e-mail para este job
        subject = subject_template.format(**context)
        
        email_jobs.append({
            'recipient': recipient,
            'subject': subject,
            'body': body
        })

    # chama o sender com a lista de jobs e retorna o resultado
    success, failed = email_sender.send_emails_in_parallel(email_jobs, test_limit=test_limit)
    return success, failed